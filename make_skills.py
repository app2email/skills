#!/usr/bin/env python3
"""Generates the app2email Agent Skills (https://agentskills.io) from the API spec.

    python3 make_skills.py [path/to/openapi_v1.json]      default: ../../apidoer/openapi/openapi_v1.json

Guidance (how an agent should behave) is written here, in GUIDANCE_*. Every fact about the API (paths, parameters,
request bodies, examples, error codes, webhook events, scopes) is rendered from the OpenAPI spec, so the skills stay
in step with apidoer/ApiV1*.cs and make_openapi.py. Do not edit the generated SKILL.md and references/*.md by hand.

Outputs (all under this folder):
  app2email-whatsapp/SKILL.md + references/endpoints.md, errors.md, webhooks.md     the main skill
  app2email-setup/SKILL.md                                                           keys, scopes, sandbox, connecting clients, agent sign-up
  app2email-broadcasts/SKILL.md + references/send-template.md                        templates, lists, segments, scheduling
  app2email-agent-handoff/SKILL.md                                                   the 24 hour window, owners, handoff
  well-known-skills-index.json                                                       legacy index (v0.1.0: name, description, files), /.well-known/skills/index.json
  well-known-agent-skills-index.json + agent-skills/<name>.zip                       the current index (https://schemas.agentskills.io/discovery/0.2.0/schema.json:
                                                                                     name, type skill-md | archive, description, url, digest sha256:<hex>),
                                                                                     /.well-known/agent-skills/index.json
  claude-code-marketplace/plugins/app2email/skills/<name>/...                        copies for the Claude Code plugin

The website copies (2026-11-06, A5): with A2E_FRONT_STATIC=<front>/static (or --front <front>/static):
  static/skills/<name>/...                   https://www.app2email.com/skills/<name>/SKILL.md (site_url; existing static files)
  static/.well-known/skills/index.json       the legacy index (existing static file)
  <front>/src/lib/server/agent_skills/files.json  (or A2E_FRONT_AGENT_SKILLS_DIR / --front-server <dir>) everything else, served by the routes
                                             /.well-known/agent-skills/[...path] and /.well-known/skills/[...path] through serve.ts in that folder:
      /.well-known/agent-skills/index.json, <name>.zip, <name>/SKILL.md      the discovery index and what it lists
      /.well-known/skills/<name>/<file>                                       the files the legacy index lists
  Routes, not static/: adapter-node's static server answers any *.gz with Content-Encoding: gzip (clients unzip it on the way and hash the tar,
  not the digest's bytes), sets no CORS header (the discovery spec asks for Access-Control-Allow-Origin: *), and serves static/ on reseller
  hosts before hooks.server.ts can refuse it. The archives are .zip anyway, so a static copy would also verify.
Discovery: https://specification.website/spec/agent-readiness/agent-skills-discovery/ ; https://github.com/cloudflare/agent-skills-discovery-rfc
(archives .tar.gz or .zip, application/zip, digest = sha256 of the archive file's bytes); legacy fallback: https://mysticmind.github.io/agentskills-cli/sources/well-known
"""
import base64, hashlib, io, json, os, re, shutil, sys, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
_args = [a for a in sys.argv[1:]]
FRONT_STATIC = os.environ.get("A2E_FRONT_STATIC") or ""
if "--front" in _args:
    FRONT_STATIC = _args[_args.index("--front") + 1]
    del _args[_args.index("--front"):_args.index("--front") + 2]
FRONT_SERVER = os.environ.get("A2E_FRONT_AGENT_SKILLS_DIR") or ""
if "--front-server" in _args:
    FRONT_SERVER = _args[_args.index("--front-server") + 1]
    del _args[_args.index("--front-server"):_args.index("--front-server") + 2]
if FRONT_STATIC and not FRONT_SERVER:
    FRONT_SERVER = os.path.join(os.path.dirname(os.path.normpath(os.path.abspath(FRONT_STATIC))), "src", "lib", "server", "agent_skills")
SPEC_PATH = _args[0] if _args else os.path.join(HERE, "..", "..", "apidoer", "openapi", "openapi_v1.json")
RAW_BASE = "https://raw.githubusercontent.com/app2email/skills/main"   # where the skills repo will be published
SITE = "https://www.app2email.com"
SITE_BASE = SITE + "/skills"                                            # the same files served by the website
AGENT_SKILLS_SCHEMA = "https://schemas.agentskills.io/discovery/0.2.0/schema.json"
DOCS = SITE + "/docs/api"
VERSION = "1.1.0"

with open(SPEC_PATH, encoding="utf-8") as f:
    SPEC = json.load(f)
PATHS = SPEC["paths"]
SCHEMAS = SPEC["components"]["schemas"]
API_VERSION = SPEC["info"]["version"]
SERVER = SPEC["servers"][0]["url"].rstrip("/")
METHODS = ("get", "post", "put", "patch", "delete")


# ----------------------------------------------------------------------------------------------------------------- spec helpers
def deref(node):
    """Follows $ref into components/schemas or components/parameters."""
    if isinstance(node, dict) and "$ref" in node:
        parts = node["$ref"].split("/")
        section = SPEC["components"].get(parts[-2], {})
        return deref(section[parts[-1]])
    return node


# the skills are for a number's agent, and their copies in the web app's static/skills are served on reseller hosts too: the account management and
# partner groups, the partner-only events and the codes only those groups answer are left out (they stay in the route-served /docs/api/*.md; review rules-3)
LEFT_OUT_TAGS = ("Account management", "Partner")
PARTNER_ONLY_EVENTS = {e.get("type") for e in SPEC.get("x-a2e-webhook-events", []) if e.get("group") == "Partner"}


def all_operations():
    for path, item in PATHS.items():
        for m in METHODS:
            if m in item:
                yield m.upper(), path, item[m]


def operations():
    for m, path, op in all_operations():
        if not set(op.get("tags", [])) & set(LEFT_OUT_TAGS):
            yield m, path, op


def left_out_codes():
    kept = {c for _m, _p, o in operations() for c in o.get("x-a2e-error-codes", [])}
    return {c for _m, _p, o in all_operations() for c in o.get("x-a2e-error-codes", [])} - kept


def short(path):
    return path.replace("/v1/{number}", "")


def scope_of(op, method=None):
    # x-a2e-scope: the handler's own scope (make_openapi.py reads it from the C#); "" = any valid key, "*" = full access
    # "a|b" (2026-11-06, Bookings): any one of them is enough
    if isinstance(op.get("x-a2e-scope"), str):
        return op["x-a2e-scope"].replace("|", " or ") or "any"
    # older specs: the scope stated in the description ("Scope: messages:send"), else by convention
    d = op.get("description", "") + " " + op.get("summary", "")
    m = re.search(r"[Ss]cope:?\s*`?([a-z]+:[a-z]+|\*)`?", d)
    if m:
        return m.group(1)
    tags = op.get("tags", [""])
    if method is None:
        for mm, p, o in operations():
            if o is op:
                method = mm
    table = {
        "Messages": "messages:send" if method in ("POST", "DELETE") else "messages:read",
        "Templates": "templates:manage" if method in ("POST", "DELETE") else "messages:read",
        "Broadcasts": "messages:send" if method == "POST" else "messages:read",
        "Account": "messages:read",
        "Do Not Call": "dnc:manage",
        "Opt-ins": "settings:manage" if method in ("POST", "PUT", "DELETE") else "messages:read",
        "Settings": "settings:manage" if method in ("PUT", "POST") else "messages:read",
        "Webhooks": "webhooks:manage",
        "Contacts": "contacts:manage" if method in ("POST", "PUT", "PATCH", "DELETE") else "messages:read",
        "Conversations": "messages:send" if method in ("PUT", "POST") else "messages:read",
        "Approvals": "messages:send" if method == "POST" else "messages:read",
    }
    return table.get(tags[0], "")


def param_rows(op):
    rows = []
    for p in op.get("parameters", []):
        p = deref(p) if "$ref" in p else p
        if p.get("name") == "number" and p.get("in") == "path":
            continue
        sch = p.get("schema", {})
        typ = sch.get("type", "")
        if "enum" in sch:
            typ += " (" + " | ".join(str(e) for e in sch["enum"]) + ")"
        rows.append((p["name"], p.get("in", ""), typ, "yes" if p.get("required") else "", (p.get("description") or "").replace("\n", " ")))
    return rows


def body_schema(op):
    rb = op.get("requestBody")
    if not rb:
        return None
    content = rb.get("content", {}).get("application/json", {})
    return deref(content.get("schema", {})), content.get("examples", {})


def without_partner_events(text):
    """the static copies are served on reseller hosts too: leave out the "<partner event>: {...}." parts of a text (WebhookEvent.data lists every event's data)"""
    for t in PARTNER_ONLY_EVENTS:
        text = re.sub(re.escape(t) + r": \{[^{}]*\}\.? ?", "", text)
    return text


def schema_fields(schema, depth=0, seen=None):
    """Flat list of (name, type, required, description) for an object schema, one level of nesting."""
    seen = seen or set()
    schema = deref(schema)
    out = []
    req = set(schema.get("required", []))
    for name, prop in (schema.get("properties") or {}).items():
        prop = deref(prop)
        typ = prop.get("type", "object" if "properties" in prop else "")
        if "enum" in prop:
            typ += " (" + " | ".join(str(e) for e in prop["enum"] if e not in PARTNER_ONLY_EVENTS) + ")"		# partner events: account and partner webhooks only (left out of the static copies)
        if typ == "array":
            items = deref(prop.get("items", {}))
            typ = "array of " + (items.get("type", "object") if "properties" not in items else "object")
        out.append(("  " * depth + name, typ, "yes" if name in req else "", without_partner_events((prop.get("description") or "").replace("\n", " "))))
        if depth == 0 and "properties" in prop and id(prop) not in seen:
            seen.add(id(prop))
            out.extend(schema_fields(prop, depth + 1, seen))
    return out


def md_table(headers, rows):
    def esc(v):
        return str(v).replace("|", "\\|")
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for r in rows:
        lines.append("| " + " | ".join(esc(c) for c in r) + " |")
    return "\n".join(lines)


def example_json(obj):
    return "```json\n" + json.dumps(obj, indent=2, ensure_ascii=False) + "\n```"


def first_example(op):
    bs = body_schema(op)
    if not bs:
        return None
    _, examples = bs
    for ex in examples.values():
        if "value" in ex:
            return ex["value"]
    return None


def kebab(s):
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", s)
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1-\2", s)
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def docs_url(op):
    """the call's page: /docs/api/<tag slug>/<operationId slug> (add .md for Markdown)"""
    return DOCS + "/" + (kebab((op.get("tags") or ["Other"])[0]) or "other") + "/" + kebab(op.get("operationId", ""))


def group_table():
    """the main skill's table: one row per group (tag), its calls and its docs page; references/endpoints.md has every call in full"""
    rows, by_tag = [], {}
    for m, p, o in operations():
        by_tag.setdefault((o.get("tags") or ["Other"])[0], []).append(f"`{m} {short(p)}`")
    for tag, calls in by_tag.items():
        rows.append((tag, ", ".join(calls), f"{DOCS}/{kebab(tag) or 'other'}"))
    return md_table(["Group", "Calls", "Docs"], rows)


def mcp_tool_count():
    for s in SPEC.get("x-a2e-mcp-servers", []) or []:
        if isinstance(s, dict) and s.get("name") == "messaging":
            return len(s.get("tools", []))
    return len({o.get("x-a2e-mcp-tool") for _m, _p, o in operations() if o.get("x-a2e-mcp-tool")})


def endpoint_table(filter_fn=lambda m, p, o: True):
    rows = []
    for m, p, o in operations():
        if not filter_fn(m, p, o):
            continue
        rows.append((f"`{m} {short(p)}`", o.get("summary", ""), scope_of(o, m)))
    return md_table(["Call", "Does", "Scope"], rows)


def has_path(path):
    return path in PATHS


# ------------------------------------------------------------------------------------------------------------- generated parts
def gen_overview():
    desc = SPEC["info"].get("description", "")
    # the first paragraph of the spec description, and the "Rate limit"/"Plans" paragraphs
    paras = [p.strip() for p in desc.split("\n\n") if p.strip()]
    keep = [p for p in paras if p.startswith(("**Authentication", "**Rate limit", "**Plans", "**Free-form", "**Scheduled", "**Request ID", "**Test without"))]
    return "\n\n".join(keep)


def gen_endpoints_reference():
    parts = [f"# app2email API v1 endpoint reference\n\nGenerated from the OpenAPI spec (API version {API_VERSION}). Base: `{SERVER}/v1/{{number}}`. Every path below is relative to that base.\n"]
    by_tag = {}
    for m, p, o in operations():
        by_tag.setdefault(o.get("tags", ["Other"])[0], []).append((m, p, o))
    for tag, ops in by_tag.items():
        parts.append(f"\n## {tag}\n")
        for m, p, o in ops:
            parts.append(f"\n### `{m} {short(p)}`\n\n{o.get('summary', '')}. Scope: `{scope_of(o, m) or 'any'}`. Docs: {docs_url(o)}\n")
            if o.get("description"):
                parts.append(o["description"].strip() + "\n")
            rows = param_rows(o)
            if rows:
                parts.append("\nParameters:\n\n" + md_table(["Name", "In", "Type", "Required", "Meaning"], rows) + "\n")
            bs = body_schema(o)
            if bs:
                schema, _ = bs
                fields = schema_fields(schema)
                if fields:
                    parts.append("\nRequest body:\n\n" + md_table(["Field", "Type", "Required", "Meaning"], fields) + "\n")
                ex = first_example(o)
                if ex is not None:
                    parts.append("\nExample request:\n\n" + example_json(ex) + "\n")
            ok = o.get("responses", {}).get("200") or o.get("responses", {}).get("202")
            if ok:
                content = ok.get("content", {}).get("application/json", {})
                exs = content.get("examples", {})
                ex = content.get("example")
                if ex is None:
                    for e in exs.values():
                        if "value" in e:
                            ex = e["value"]
                            break
                if ex is not None:
                    parts.append("\nExample answer:\n\n" + example_json(ex) + "\n")
    return "\n".join(parts)


def gen_errors_reference():
    err = deref(SCHEMAS["Error"])
    codes = [c for c in err["properties"]["code"].get("enum", []) if c not in left_out_codes()]
    resp = deref(SCHEMAS["ErrorResponse"])
    fields = schema_fields(err)
    out = ["# app2email API errors\n", "Every failed call answers `success: false` with `request_id` and an `error` object:\n", md_table(["Field", "Type", "Required", "Meaning"], fields), ""]
    # status texts from the spec's responses (collected from any operation)
    statuses = {}
    for m, p, o in operations():
        for code, r in o.get("responses", {}).items():
            if code.isdigit() and int(code) >= 400 and code not in statuses:
                statuses[code] = r.get("description", "")
    out.append("\n## HTTP status meanings\n")
    out.append(md_table(["Status", "Meaning"], sorted(statuses.items())))
    out.append("\n## Error codes\n")
    out.append(", ".join(f"`{c}`" for c in codes))
    out.append(f"\n\nEach code with its fix: {DOCS}/errors#<code>.")
    out.append("\n\nWhat to do: read `how_to_fix`. A template value mistake comes with `example_request`: copy its shape. `429 rate_limited` carries `Retry-After` (seconds): wait, then retry. `422 outside_24h_window`: send an approved template instead of free-form. `403 plan_not_allowed` / `service_not_live` and `401` codes need the account owner, not a retry. `is_retriable` (when present) says whether the same request can be sent again later.")
    _ = resp
    return "\n".join(out)


def gen_webhooks_reference():
    wev = deref(SCHEMAS.get("WebhookEvent", {}))
    # the event types: WebhookEvent.type without the test-only "ping". every webhook gets every event (2026-11-05)
    events = [e for e in (wev.get("properties", {}).get("type", {}).get("enum", []) if wev else []) if e != "ping" and e not in PARTNER_ONLY_EVENTS]
    out = ["# app2email webhooks\n", f"Create one with `POST /webhooks` (scope `webhooks:manage`). Every webhook gets every event: check the event's `type` and answer 2xx to the ones you do not handle. Events: " + ", ".join(f"`{e}`" for e in events) + ".\n"]
    if wev:
        out.append("Each delivery is a JSON body:\n\n" + md_table(["Field", "Type", "Required", "Meaning"], schema_fields(wev)))
    out.append("\nSignature: header `X-App2email-Signature: t=<unix seconds>,v1=<hex HMAC-SHA256 of \"<t>.<raw body>\">` with the webhook's secret (shown once at creation or after `rotate-secret`). While an old secret still signs (`rotate-secret` with `keep_old_for_hours`) the header has two `v1=` values: accept the event when any one matches. Reject deliveries older than 5 minutes. Deliveries are retried with backoff; `GET /webhooks/{id}/deliveries` shows attempts and `POST .../redeliver` sends one again.")
    out.append(f"\nEvery event with its payload, verify code (Node.js, Python, PHP) and a tester: {DOCS}/webhooks")
    return "\n".join(out)


def gen_send_template_reference():
    op = PATHS["/v1/{number}/messages"]["post"]
    schema, examples = body_schema(op)
    out = [f"# POST /messages: the request body\n\n{op.get('description', '')}\n", "## Fields\n", md_table(["Field", "Type", "Required", "Meaning"], schema_fields(schema)), ""]
    for key in ("Template", "Component", "Parameter", "Media", "FreeFormText", "FreeFormMedia", "Recipient"):
        if key in SCHEMAS:
            s = deref(SCHEMAS[key])
            out.append(f"\n### {key}\n\n{s.get('description', '')}\n\n" + md_table(["Field", "Type", "Required", "Meaning"], schema_fields(s)))
    out.append("\n## Examples (from the spec)\n")
    for name, ex in examples.items():
        if "value" in ex:
            out.append(f"\n**{ex.get('summary', name)}**\n\n" + example_json(ex["value"]))
    return "\n".join(out)


def gen_scopes():
    desc = SPEC["info"].get("description", "")
    m = re.search(r"A key has \*\*scopes\*\*:(.+?)(?:\n\n|$)", desc, re.S)
    return ("A key has scopes:" + m.group(1)).strip() if m else "Scopes are listed by `GET /me` (`scopes_available`)."


def conversation_section():
    """Conversation and handoff calls: from the spec when it has them, otherwise the agreed contract (marked)."""
    if has_path("/v1/{number}/conversations/{contact}/owner") or has_path("/v1/{number}/conversations/{phone}/owner"):
        return endpoint_table(lambda m, p, o: "/conversations" in p or "/approvals" in p)
    return (
        endpoint_table(lambda m, p, o: "/conversations" in p)
        + "\n\nAdded in the next API release (not yet in the published spec; the MCP tools `get_conversation` and `set_conversation_owner` use them):\n\n"
        + md_table(
            ["Call", "Does", "Scope"],
            [
                ("`GET /conversations/{contact}`", "window_open, window_closes_at, owner, name, last messages", "messages:read"),
                ("`PUT /conversations/{contact}/owner`", 'body {"owner": "human"|"agent"|"paused"|"", "reason", "summary", "until_minutes"}', "messages:send"),
                ("`GET /approvals`, `POST /approvals/{id}/approve|reject`", "sends held for a human OK (keys with an approval threshold)", "messages:read / messages:send"),
            ],
        )
    )


def contacts_section():
    if any("/contacts" in p for p in PATHS):
        return endpoint_table(lambda m, p, o: "/contacts" in p or "/segments" in p)
    return (
        "Added in the next API release (not yet in the published spec):\n\n"
        + md_table(
            ["Call", "Does", "Scope"],
            [
                ("`GET /contacts`", "search: q, tag, consent_marketing, limit, cursor", "messages:read"),
                ("`POST /contacts`", "upsert one or many: identity, name, tags[], custom_fields{}, source, consent_* fields", "contacts:manage"),
                ("`GET/PATCH/DELETE /contacts/{identity}`", "one contact", "contacts:manage"),
                ("`POST /contacts/import`", "CSV or JSON array", "contacts:manage"),
                ("`POST /contacts/{identity}/consent`", "record marketing consent with evidence", "contacts:manage"),
                ("`GET /contacts/export.csv`", "everything, for audits", "messages:read"),
                ("`GET/POST /segments`, `GET/PUT/DELETE /segments/{id}`", "saved filters; `POST /messages` takes `segment`", "contacts:manage"),
            ],
        )
    )


# ---------------------------------------------------------------------------------------------------------------- the guidance
GUARDRAILS = """## Guardrails (read before any send)

- CANNOT send a free-form message (text, image, video, document, buttons) to a contact whose 24 hour window is closed. `window_open: false` or `422 outside_24h_window` means: send an APPROVED template instead, or stop.
- CANNOT send marketing to a number on the Do Not Call list (the API refuses with `403 recipient_opted_out`) or to a person who has not consented to marketing. Utility messages (order updates, reminders the person asked for) do not need marketing consent.
- CANNOT connect a WhatsApp number or pay for a plan: a person does that. An agent can start an account for a person with the Management MCP server (`create_account`, see app2email-setup); otherwise ask the user for the number and a key.
- CANNOT read messages of other numbers: a key belongs to one number.
- Every send reaches a real person's phone and counts against the customer's monthly plan (outgoing WhatsApp messages and outgoing emails together). Confirm the recipients and the content with the user unless they already told you to send; use `dry_run: true` first for template sends; use an `Idempotency-Key` so a retry never sends twice.
- Never put the API key in a message, a log, a web page or a reply to the user.
- When the person asks for a human, stop automating that contact: hand the conversation over (see the agent handoff skill) and say so."""

GUIDANCE_MAIN = """---
name: app2email-whatsapp
description: Send and receive WhatsApp Business messages through the app2email API (templates, free-form replies inside the 24 hour window, conversations, contacts, Do Not Call list, broadcasts, webhooks). Use when the user mentions WhatsApp messaging, WhatsApp templates, app2email, or wants an agent to message customers on WhatsApp.
license: MIT
compatibility: Needs network access to api.app2email.com and an app2email API key (APP2EMAIL_API_KEY) plus the WhatsApp number (APP2EMAIL_NUMBER).
metadata:
  author: app2email
  version: "__VERSION__"
  source: generated by sdk/skills/make_skills.py from the app2email OpenAPI spec __API_VERSION__
---

# app2email WhatsApp

app2email connects a business's own WhatsApp number (official WhatsApp Business Cloud API, the customer owns the number and pays Meta directly) to email, to automations and to agents. This skill is for an agent that sends or reads WhatsApp messages through the REST API `__SERVER__/v1/{number}/...`, through the MCP server `https://api.app2email.com/mcp` (__TOOLS__ tools: __DOCS__/mcp), or through the SDKs (`app2email-api` on npm and PyPI).

## Setup

- Base URL: `__SERVER__/v1/YOUR_NUMBER` where `YOUR_NUMBER` is the WhatsApp number you send from, country code first, digits only.
- Auth: `Authorization: Bearer YOUR_API_KEY`. Keys come from https://www.app2email.com/dashboard/apikey and are shown once. Keep them in the environment (`APP2EMAIL_API_KEY`, `APP2EMAIL_NUMBER`).
- First call: `GET /me` (is the key valid, which scopes, which plan, the limits). If it fails, stop and tell the user.
- Reference: __DOCS__ (one page per call, add `.md` for Markdown), errors __DOCS__/errors#<code>, webhooks __DOCS__/webhooks. For agents: https://www.app2email.com/llms.txt, https://www.app2email.com/docs-api.md (everything in one file), OpenAPI `__SERVER__/v1/openapi.json`.

__SCOPES__

## Start here

1. `GET /me` checks the key.
2. `GET /templates` lists the approved templates, each with the values it needs and a complete `example_request`.
3. `GET /conversations/{contact}/messages` (or `GET /conversations`) tells you whether the contact's reply window is open (`window_open`).
4. `POST /messages` with `"dry_run": true` checks everything and sends nothing.
5. `POST /messages` for real, with an `Idempotency-Key` header. Then `GET /messages/{message_id}` or a webhook reports delivery.

## Which message to send

| Situation | Send |
| --- | --- |
| Starting a conversation, or `window_open` is false | an approved template: `"type": "template"` |
| The reply window is open (the contact wrote within 24 hours) | a free-form message, one contact per call: `"type": "text"` / `image` / `video` / `document` / `audio` (`"voice": true`: a voice note) / `sticker` / `location` / `contacts` / `reaction` (each counts as one message), or a template |
| Buttons, a menu, cards, a form, a location or the contact's number | `"type": "interactive"`: `button`, `list`, `cta_url`, `carousel`, `flow`, `location_request_message`, `request_contact_info` |
| Show that you read it, or that you are typing | `POST /messages/read` with the `message_id` (`"typing": true` for the typing indicator). Free: not counted, no window |
| The same or a personalised message to many numbers | a template with `to` as a list, or `recipients` with per-number values, or `segment` |
| A big list, or the client stops waiting after about 30 seconds | add `"background": true`, then follow `GET /broadcasts/{code}` |
| Later | a template with `"send_at"` (ISO 8601 with a time zone, 1 minute to 29 days ahead) |
| The person asks for a human | `PUT /conversations/{contact}/owner` with `"owner": "human"`, a reason and a summary (see app2email-agent-handoff) |

__GUARDRAILS__

## Errors

Every failed call returns `{ "success": false, "request_id": "...", "error": { "code", "message", "how_to_fix", ... } }`. Read `how_to_fix`; copy `example_request` when it is given; wait `Retry-After` seconds on 429; quote `request_id` to the user when you cannot fix it. The full list is in [references/errors.md](references/errors.md).

## Endpoints

__GROUPS__

Full parameters, bodies and examples: [references/endpoints.md](references/endpoints.md). Webhook events and signature check: [references/webhooks.md](references/webhooks.md).

## Facts worth remembering

__FACTS__
"""

GUIDANCE_SETUP = """---
name: app2email-setup
description: Set up an agent or automation to use app2email's WhatsApp API: start an app2email account for a person (Management MCP create_account), get the number connected, create an API key with the right scopes (or a sandbox key), connect the MCP server, n8n, Zapier, Make, Power Automate or the SDKs, and check that the key works. Use when the user is configuring app2email access, asks for an app2email API key or account, or wants to connect a tool to app2email.
license: MIT
metadata:
  author: app2email
  version: "__VERSION__"
  source: generated by sdk/skills/make_skills.py from the app2email OpenAPI spec __API_VERSION__
---

# app2email setup

## No account yet: an agent starts it, the person finishes it

Management MCP server `https://api.app2email.com/mcp/manage` (__DOCS__/agents). No previous human sign-up is required.

1. Call `create_account` with `contact_email` (no key). It returns `signup_id`, `management_key`, `onboarding_link` and `message`.
2. Give the person `onboarding_link`: they confirm the e-mail, connect their WhatsApp number and choose a plan. Nothing can be sent before that. `get_account_status` says what is still needed.
3. Pass the `management_key` as `Authorization: Bearer <management_key>` on every later call.
4. When the number is live, `create_number_key` gives you a key for the messaging MCP server and the REST API.

## What the person does (an agent cannot)

1. Connect the WhatsApp Business number on https://www.app2email.com (Embedded Signup with Meta; an existing WhatsApp Business app number keeps working on the phone, this is called coexistence).
2. Pick a paid plan: the API needs one (`403 plan_not_allowed` otherwise).
3. Create an API key on https://www.app2email.com/dashboard/apikey. Choose scopes for the job, an expiry, optionally an IP allow-list. A **sandbox** key simulates sends (nothing reaches a phone, nothing is counted): use one while building. A key can carry a **daily cap** and an **approval threshold** (sends to more numbers than the threshold wait for a human OK on the dashboard).
4. Give the agent the key and the number through the environment: `APP2EMAIL_API_KEY`, `APP2EMAIL_NUMBER`.

## Scopes

__SCOPES__

Ask for the smallest set: a support agent needs `messages:read` and `messages:send`; a CRM sync needs `contacts:manage`; opt-out handling needs `dnc:manage`; nothing needs `*`.

## Connect a client

- **MCP (Claude Code, Claude, Cursor, VS Code, Codex, OpenClaw):** `https://api.app2email.com/mcp` (Streamable HTTP) with `Authorization: Bearer YOUR_API_KEY`; reads are marked read-only, every send or change destructive. Claude Code: `claude mcp add --transport http app2email https://api.app2email.com/mcp --header "Authorization: Bearer YOUR_API_KEY"`. Every client: __DOCS__/mcp
- **OpenClaw channel (the agent answers WhatsApp messages as they arrive):** `openclaw plugins install clawhub:@app2email/openclaw-whatsapp`, then `channels.app2email-whatsapp.apiKey` and `.number`.
- **n8n:** community node `n8n-nodes-app2email` (credential: API key + number). **Zapier:** the app2email app (custom auth: key + number). **Make:** import `__SERVER__/v1/openapi.json`. **Power Automate:** custom connector from `__SERVER__/v1/swagger2.json`.
- **Code:** `npm install app2email-api` / `pip install app2email-api`, or plain HTTP with the Bearer header.

## Check it works

```
curl -H "Authorization: Bearer $APP2EMAIL_API_KEY" __SERVER__/v1/$APP2EMAIL_NUMBER/me
```

`key_valid: true`, `service_status: "LIVE"` and the scopes you expect. Then `GET /templates` and a `POST /messages` with `"dry_run": true`.

## Limits to tell the user about

__FACTS__
"""

GUIDANCE_BROADCASTS = """---
name: app2email-broadcasts
description: Send WhatsApp template messages to one contact, a list or a segment through app2email: pick an approved template, fill its values (body text, header media, buttons, named placeholders), personalise per recipient, schedule, dry run, run big lists in the background, follow delivery, and respect consent and the Do Not Call list. Use when the user wants to notify, remind or market to customers on WhatsApp, or asks about WhatsApp templates and broadcasts.
license: MIT
metadata:
  author: app2email
  version: "__VERSION__"
  source: generated by sdk/skills/make_skills.py from the app2email OpenAPI spec __API_VERSION__
---

# app2email broadcasts and templates

A template is a message Meta approved in advance (name, language, placeholders). Templates are the only way to message a contact who did not write in the last 24 hours. Three categories: UTILITY (transactional, cheaper), MARKETING (needs consent, refused for Do Not Call numbers), AUTHENTICATION (one-time codes).

## Procedure

1. `GET /templates`: choose an APPROVED template; the answer carries `example_request` per template, copy its shape. `GET /templates/{name}` shows rejection reasons and quality.
2. Build the body (see [references/send-template.md](references/send-template.md)): `to` (one number, a comma list, or an array), or `recipients` with per-number `components`, or `segment` (a saved contact filter). Shared `template.components` apply to everyone; a recipient's component of the same type (same button index) replaces it.
3. `POST /messages` with `"dry_run": true`. Fix anything the error reports (`example_request`).
4. Confirm with the user: how many numbers, which template, when. Then send with an `Idempotency-Key` and a `campaign_name`.
5. More than a few hundred numbers or a slow client: `"background": true` → `202` with `broadcast.status_url`; follow `GET /broadcasts/{code}` or the `broadcast.completed` webhook. `GET /broadcasts/{code}/results.csv` gives the result per number.
6. Later: `"send_at"`; cancel with `POST /broadcasts/{code}/cancel`.

## Personalisation

Numbered placeholders take `{"type": "text", "text": "John"}` in order; named placeholders add `"parameter_name"`. Header media: `link` (public URL, app2email downloads it), base64 `data`, or a media `id` from `POST /media` (upload once, reuse for 30 days). Leave the header out to use the template's sample media. Buttons: `{"type": "button", "sub_type": "url", "index": "0", "parameters": [{"type": "text", "text": "abc"}]}`.

Contacts' `custom_fields` (from `POST /contacts`) can be used as values when sending to a `segment`.

## Consent and compliance

- MARKETING templates: only to contacts with consent (record it with `POST /contacts/{identity}/consent` or `POST /optins`); the opt-in rule can be enforced per number (`PUT /settings/optin`).
- The Do Not Call list (`GET /donotcall`) is applied automatically to marketing sends; `contact.opted_out` webhook events tell you when someone taps "Stop promotions". Add numbers with `POST /donotcall` when a person asks not to be contacted.
- The monthly plan limit counts outgoing WhatsApp messages and outgoing emails together (`GET /usage`); Meta charges per message beyond the free service allowance (`GET /usage/meta` when available).

__GUARDRAILS__

## Endpoints used

__ENDPOINTS__
"""

GUIDANCE_HANDOFF = """---
name: app2email-agent-handoff
description: Run an AI agent that answers WhatsApp conversations through app2email and hands them to a person when needed: check the 24 hour reply window, read the conversation, reply free-form or with a template, claim or release conversation ownership (agent, human, paused), write a handoff summary, and react to webhook events. Use when building or operating a WhatsApp support or sales agent on app2email, or when a WhatsApp conversation must go to a human.
license: MIT
metadata:
  author: app2email
  version: "__VERSION__"
  source: generated by sdk/skills/make_skills.py from the app2email OpenAPI spec __API_VERSION__
---

# app2email agent handoff

app2email routes every inbound WhatsApp message to the number's email bridge, webhooks, A2A agent, OpenClaw channel or auto reply, as the owner set up. A conversation has an **owner**: `""` (default routing), `agent` (an automation owns it), `human` (a person owns it: auto reply and agent forwarding stop; the email bridge and dashboard take over), `paused` (nothing automatic is sent). Owners can carry a reason, a summary and a timeout.

## Loop for an answering agent

1. Inbound arrives (webhook `message.received`, the OpenClaw channel, or polling `GET /messages?direction=in`).
2. `GET /conversations/{contact}` (or `/conversations/{contact}/messages`): `window_open`, `window_closes_at`, `owner`, recent history. If `owner` is `human` or `paused`, do not answer.
3. Decide. Inside the window: `POST /messages` with `type` text / image / document / interactive (buttons or a list to ask a structured question). Outside: an approved template, or wait.
4. When the person asks for a human, is angry, asks about money, legal, health, or anything outside your remit: hand over (below) and tell the person someone will take over.
5. Report status through `GET /messages/{id}` or the `message.status` / `message.failed` webhooks.

## Handing over

`PUT /conversations/{contact}/owner` with:

```json
{"owner": "human", "reason": "customer asked for a person", "summary": "Order #1234 arrived damaged; wants a replacement; photo received at 10:12; promised a reply today.", "until_minutes": 480}
```

The summary is what the person reads first: facts, what was promised, what is open, in a few lines. `until_minutes` returns the conversation to default routing later (leave it out to hand over for good). app2email sends the `conversation.owner_changed` webhook event and, when email forwarding is on, the handoff reaches the owner's mailbox so they can reply from there (their reply stays inside the window rules; late replies are held and the contact gets a "Show reply" notice).

To take a conversation back: `"owner": "agent"`; to stop everything automatic for a contact: `"owner": "paused"`; to restore defaults: `"owner": ""`.

## Approvals and caps

A key can have a daily message cap and an approval threshold. A send above the threshold answers `202` with `status: "pending_approval"` and an `approval_url`; the owner approves on the dashboard (or an agent with the right key through `POST /approvals/{id}/approve`). Do not retry a pending send.

__GUARDRAILS__

## Calls

__CONVERSATIONS__

Contacts (names, tags, custom fields, consent evidence):

__CONTACTS__

Webhook events: [app2email-whatsapp/references/webhooks.md](../app2email-whatsapp/references/webhooks.md).
"""


def cut(text, limit):
    """text up to limit characters, ended at the last full sentence"""
    if len(text) <= limit:
        return text
    head = text[:limit]
    end = head.rfind(". ")
    return head[:end + 1] if end > 0 else head.rstrip() + "..."


def facts():
    desc = SPEC["info"].get("description", "")
    items = []
    m = re.search(r"\*\*Free-form replies:\*\*(.+?)\n\n", desc, re.S)
    if m:
        items.append("Free-form replies: " + cut(" ".join(m.group(1).split()), 600))
    m = re.search(r"\*\*Rate limit:\*\*(.+?)\n\n", desc, re.S)
    if m:
        items.append("Rate limit: " + " ".join(m.group(1).split()))
    m = re.search(r"\*\*Several recipients:\*\*(.+?)\n\n", desc, re.S)
    if m:
        items.append("Several recipients: " + cut(" ".join(m.group(1).split()), 500))
    m = re.search(r"\*\*Media headers:\*\*(.+?)\n\n", desc, re.S)
    if m:
        items.append("Media: " + " ".join(m.group(1).split()))
    m = re.search(r"\*\*Plans:\*\*(.+?)\n\n", desc, re.S)
    if m:
        items.append("Plans: " + " ".join(m.group(1).split()))
    return "\n".join(f"- {i}" for i in items)


def render(template, **extra):
    out = template.replace("__VERSION__", VERSION).replace("__API_VERSION__", API_VERSION).replace("__SERVER__", SERVER).replace("__DOCS__", DOCS)
    out = out.replace("__TOOLS__", str(mcp_tool_count()))
    out = out.replace("__GUARDRAILS__", GUARDRAILS).replace("__SCOPES__", gen_scopes()).replace("__FACTS__", facts())
    for k, v in extra.items():
        out = out.replace("__" + k + "__", v)
    return out


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text.rstrip() + "\n")


def check_frontmatter(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    assert m, path + ": no frontmatter"
    name = re.search(r"^name: (.+)$", m.group(1), re.M).group(1).strip()
    desc = re.search(r"^description: (.+)$", m.group(1), re.M).group(1).strip()
    folder = os.path.basename(os.path.dirname(path))
    assert name == folder, f"{path}: name {name} must match folder {folder}"
    assert re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name) and len(name) <= 64, path + ": bad name"
    assert 0 < len(desc) <= 1024, path + ": description length"
    assert len(text.splitlines()) < 500, f"{path}: SKILL.md over 500 lines ({len(text.splitlines())}); move detail to references/"
    return name, desc


# ------------------------------------------------------------------------------------------------------------------------ main
MAIN = os.path.join(HERE, "app2email-whatsapp")
write(os.path.join(MAIN, "SKILL.md"), render(GUIDANCE_MAIN, GROUPS=group_table()))
write(os.path.join(MAIN, "references", "endpoints.md"), gen_endpoints_reference())
write(os.path.join(MAIN, "references", "errors.md"), gen_errors_reference())
write(os.path.join(MAIN, "references", "webhooks.md"), gen_webhooks_reference())

write(os.path.join(HERE, "app2email-setup", "SKILL.md"), render(GUIDANCE_SETUP))

BC = os.path.join(HERE, "app2email-broadcasts")
write(os.path.join(BC, "SKILL.md"), render(GUIDANCE_BROADCASTS, ENDPOINTS=endpoint_table(lambda m, p, o: o.get("tags", [""])[0] in ("Messages", "Templates", "Broadcasts", "Do Not Call", "Opt-ins") and "/conversations" not in p)))
write(os.path.join(BC, "references", "send-template.md"), gen_send_template_reference())

write(os.path.join(HERE, "app2email-agent-handoff", "SKILL.md"), render(GUIDANCE_HANDOFF, CONVERSATIONS=conversation_section(), CONTACTS=contacts_section()))

skills = []
for folder in ("app2email-whatsapp", "app2email-setup", "app2email-broadcasts", "app2email-agent-handoff"):
    skill_md = os.path.join(HERE, folder, "SKILL.md")
    name, desc = check_frontmatter(skill_md)
    files = []
    for root, _dirs, fnames in os.walk(os.path.join(HERE, folder)):
        for fn in sorted(fnames):
            files.append(os.path.relpath(os.path.join(root, fn), os.path.join(HERE, folder)).replace(os.sep, "/"))
    files.sort(key=lambda f: (f != "SKILL.md", f))
    skills.append({"name": name, "description": desc, "files": files, "url": f"{RAW_BASE}/{folder}/SKILL.md", "site_url": f"{SITE_BASE}/{folder}/SKILL.md"})

write(os.path.join(HERE, "well-known-skills-index.json"), json.dumps({"skills": skills}, indent=2))


ZIP_DATE = (1980, 1, 1, 0, 0, 0)


def skill_archive(folder):
    """<name>.zip with SKILL.md at the root, byte for byte the same on every run: sorted entries, a fixed date, mode 0644, deflate level 9, no extra
    fields or comment. Not a .tar.gz: a static server that reads *.gz as an encoding (sirv in adapter-node) makes clients hash the inner tar."""
    root = os.path.join(HERE, folder)
    raw = io.BytesIO()
    files = sorted((os.path.relpath(os.path.join(d, f), root).replace(os.sep, "/") for d, _s, fs in os.walk(root) for f in fs), key=lambda f: (f != "SKILL.md", f))
    with zipfile.ZipFile(raw, "w") as z:
        for rel in files:
            info = zipfile.ZipInfo(rel, date_time=ZIP_DATE)
            info.compress_type, info.create_system, info.external_attr = zipfile.ZIP_DEFLATED, 3, 0o100644 << 16
            z.writestr(info, open(os.path.join(root, rel), "rb").read(), compresslevel=9)
    return raw.getvalue()


# the current discovery index (v0.2.0): a one-file skill is its SKILL.md, a skill with references/ is a .zip; digest = sha256 of the exact bytes at url.
# Every url is under /.well-known/agent-skills/ (one route: CORS, no Content-Encoding, refused on reseller hosts)
AGENT_SKILLS_DIR = os.path.join(HERE, "agent-skills")
shutil.rmtree(AGENT_SKILLS_DIR, ignore_errors=True)
os.makedirs(AGENT_SKILLS_DIR)
entries = []
served = {}          # served path -> bytes: the /.well-known/agent-skills/ files
for s_ in skills:
    if s_["files"] == ["SKILL.md"]:
        data = open(os.path.join(HERE, s_["name"], "SKILL.md"), "rb").read()
        rel = s_["name"] + "/SKILL.md"
        entries.append({"name": s_["name"], "type": "skill-md", "description": s_["description"], "url": f"{SITE}/.well-known/agent-skills/{rel}",
                        "digest": "sha256:" + hashlib.sha256(data).hexdigest()})
    else:
        data = skill_archive(s_["name"])
        rel = s_["name"] + ".zip"
        open(os.path.join(AGENT_SKILLS_DIR, rel), "wb").write(data)
        entries.append({"name": s_["name"], "type": "archive", "description": s_["description"], "url": f"{SITE}/.well-known/agent-skills/{rel}",
                        "digest": "sha256:" + hashlib.sha256(data).hexdigest()})
    served["/.well-known/agent-skills/" + rel] = data
agent_index = json.dumps({"$schema": AGENT_SKILLS_SCHEMA, "skills": entries}, indent=2)
write(os.path.join(HERE, "well-known-agent-skills-index.json"), agent_index)
served["/.well-known/agent-skills/index.json"] = (agent_index.rstrip() + "\n").encode("utf-8")
for s_ in skills:
    for f in s_["files"]:
        served[f"/.well-known/skills/{s_['name']}/{f}"] = open(os.path.join(HERE, s_["name"], f), "rb").read()

# copies for the Claude Code plugin (no symlinks: marketplaces are cloned)
plugin_skills = os.path.join(HERE, "claude-code-marketplace", "plugins", "app2email", "skills")
shutil.rmtree(plugin_skills, ignore_errors=True)
for s in skills:
    shutil.copytree(os.path.join(HERE, s["name"]), os.path.join(plugin_skills, s["name"]))



def content_type(path):
    return {".json": "application/json", ".zip": "application/zip", ".md": "text/markdown; charset=utf-8"}[os.path.splitext(path)[1]]


# the website (A2E_FRONT_STATIC or --front): static/skills/<name>/ and the legacy static/.well-known/skills/index.json (both existing static files);
# the rest goes to the routes' data file (FRONT_SERVER/files.json), never to static/ (see the top of this file)
if FRONT_STATIC:
    if not os.path.isdir(FRONT_STATIC):
        raise SystemExit("make_skills: no such folder: " + FRONT_STATIC)
    for sub_dir in ("skills", os.path.join(".well-known", "skills"), os.path.join(".well-known", "agent-skills")):
        shutil.rmtree(os.path.join(FRONT_STATIC, sub_dir), ignore_errors=True)
    for s in skills:
        shutil.copytree(os.path.join(HERE, s["name"]), os.path.join(FRONT_STATIC, "skills", s["name"]))
    write(os.path.join(FRONT_STATIC, ".well-known", "skills", "index.json"), json.dumps({"skills": skills}, indent=2))
    files_json = {"generated_by": "sdk/skills/make_skills.py --front (API repo); do not edit", "files": {}}
    for path in sorted(served):
        data = served[path]
        entry = {"type": content_type(path), "sha256": hashlib.sha256(data).hexdigest()}
        if path.endswith(".zip"):
            entry["base64"] = base64.b64encode(data).decode("ascii")
        else:
            entry["text"] = data.decode("utf-8")
        files_json["files"][path] = entry
    os.makedirs(FRONT_SERVER, exist_ok=True)
    write(os.path.join(FRONT_SERVER, "files.json"), json.dumps(files_json, indent=1, ensure_ascii=False))
    print("website copies written:", os.path.normpath(FRONT_STATIC), "+", os.path.join(os.path.normpath(FRONT_SERVER), "files.json"))

print("skills written:", ", ".join(s["name"] for s in skills))
