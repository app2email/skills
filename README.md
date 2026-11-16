# app2email Agent Skills

[Agent Skills](https://agentskills.io) that teach an AI agent how to use app2email's WhatsApp API safely: when a template is needed, how to fill it, what it cannot do, how to hand a conversation to a person. They work in Claude Code, Claude.ai, OpenClaw, Cursor and any client that reads `SKILL.md` folders.

**Generated.** `make_skills.py` renders every API fact (endpoints, parameters, examples, errors, events, scopes) from `apidoer/openapi/openapi_v1.json`; only the guidance text lives in the script. Regenerate after any API change:

```sh
python3 sdk/skills/make_skills.py [--front <front>/static]          # or: python3 make_skills.py path/to/openapi_v1.json
```

Never edit the `SKILL.md` or `references/*.md` files by hand.

| Skill | For |
| --- | --- |
| `app2email-whatsapp` | the main skill: setup, which message to send, guardrails, errors, endpoint table; `references/` hold the full endpoint, error and webhook reference |
| `app2email-setup` | getting a key with the right scopes, sandbox keys, connecting MCP / n8n / Zapier / Make / Power Automate / SDKs |
| `app2email-broadcasts` | templates, personalisation, lists and segments, scheduling, consent and the Do Not Call list |
| `app2email-agent-handoff` | the 24 hour window, conversation owners, handing over to a person, approvals |

## Three ways to install

1. **From the website**: `npx skills add https://www.app2email.com`. The site serves `/.well-known/agent-skills/index.json` (schema 0.2.0: `well-known-agent-skills-index.json`, `agent-skills/*.zip` here, one-file skills as `/.well-known/agent-skills/<name>/SKILL.md`), the legacy `/.well-known/skills/index.json` with the files it lists under `/.well-known/skills/<name>/`, and `/skills/<name>/`. Also `npx skills add app2email/skills` from the GitHub repository.
2. **Claude Code plugin marketplace:** `claude plugin marketplace add app2email/skills` then `claude plugin install app2email@app2email` (the marketplace lives in `claude-code-marketplace/`; the plugin bundles the skills and the hosted MCP server `https://api.app2email.com/mcp`, and asks for the key through `userConfig`). Validate before publishing: `claude plugin validate sdk/skills/claude-code-marketplace`.
3. **ClawHub (OpenClaw):** one skill at a time, see below.

## Publishing

- **GitHub repo `app2email/skills`:** push this folder as the repository root. `well-known-skills-index.json` and the marketplace point at `https://raw.githubusercontent.com/app2email/skills/main/...`; change `RAW_BASE` in `make_skills.py` if the repository name differs.
- **Website:** `python3 sdk/skills/make_skills.py --front <front>/static` (or `A2E_FRONT_STATIC`) writes `static/skills/`, `static/.well-known/skills/index.json` and `<front>/src/lib/server/agent_skills/files.json`, which the routes `/.well-known/agent-skills/[...path]` and `/.well-known/skills/[...path]` serve (CORS, no `Content-Encoding`, 404 on reseller sites). Archives are `.zip`: a static `*.gz` is sent with `Content-Encoding: gzip`, so clients would hash the inner tar.
- **ClawHub:** `npm i -g clawhub && clawhub login`, then for each skill `clawhub skill publish ./app2email-whatsapp --slug app2email-whatsapp --name "app2email WhatsApp" --owner app2email --categories sales-marketing --topics "whatsapp,messaging,app2email"` (categories must be exact ClawHub slugs; `--dry-run` first; the owner `app2email` must exist on ClawHub). Repeat for `app2email-setup`, `app2email-broadcasts`, `app2email-agent-handoff`.
- **Anthropic's plugin directory:** submit the marketplace plugin through the form linked from https://code.claude.com/docs/en/plugins/publish.

## Validation

`make_skills.py` checks the frontmatter rules of the Agent Skills spec (name = folder name, lowercase with hyphens, description under 1024 characters, SKILL.md under 500 lines). The reference validator can be run too: `npx skills-ref validate ./app2email-whatsapp` (see https://github.com/agentskills/agentskills).
