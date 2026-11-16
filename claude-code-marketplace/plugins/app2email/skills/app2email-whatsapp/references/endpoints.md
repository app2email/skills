# app2email API v1 endpoint reference

Generated from the OpenAPI spec (API version 1.4.0). Base: `https://api.app2email.com/v1/{number}`. Every path below is relative to that base.


## Messages


### `GET /messages`

Messages sent and received, newest first. Scope: `messages:read`. Docs: https://www.app2email.com/docs/api/messages/list-messages

Messages sent from the number (`direction` out, with their status and times) and received from contacts (`direction` in). Filters: a time window, the direction, the status of sent messages, one contact, or one broadcast. Page with `next_cursor`.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| since | query | string |  | Only messages at or after this time. ISO 8601, eg 2026-10-25T10:00:00Z. |
| until | query | string |  | Only messages before this time. ISO 8601. |
| direction | query | string (in \| out) |  | in: received. out: sent. Left out: both. |
| status | query | string (queued \| accepted \| sent \| delivered \| read \| failed) |  | Sent messages only: queued, accepted, sent, delivered, read or failed. Not with direction=in. |
| to | query | string |  | Only with this contact (full number, digits, with country code). |
| broadcast | query | string |  | Only the messages of this broadcast (its code). |
| limit | query | integer |  | How many (1 to 200, default 50). |
| cursor | query | string |  | The next_cursor of the previous answer, unchanged. Leave out for the first page. |


Example answer:

```json
{
  "success": true,
  "request_id": "h5vnq",
  "messages": [
    {
      "direction": "in",
      "message_id": "wamid.HBgLNjE0MTIzNDU2NzgVAgARGBJTQU1QTEVfVEVTVF9FVkVOVAA=",
      "from": "61412345678",
      "name": "John",
      "text": "Yes, Friday works",
      "media": null,
      "time": "2026-10-26T01:20:44Z",
      "conversation_url": "https://www.app2email.com/conversation/61412345678_4976659348270_..."
    },
    {
      "direction": "out",
      "message_id": "wamid.HBgLNjE0OTg3NjU0MzIVAgARGBJTQU1QTEVfT1VUQk9VTkQwMgA=",
      "to": "61498765432",
      "status": "read",
      "sent_by": "api",
      "text": "Hi Mary, your order #1235 has shipped.",
      "time": "2026-10-26T01:12:09Z",
      "times": {
        "submitted": "2026-10-26T01:12:08Z",
        "accepted": "2026-10-26T01:12:09Z",
        "sent": "2026-10-26T01:12:10Z",
        "delivered": "2026-10-26T01:12:11Z",
        "read": "2026-10-26T01:15:02Z"
      }
    }
  ],
  "next_cursor": "MjAyNi0xMC0yNlQwMToxMjowOVp8NDI",
  "count": 2
}
```


### `POST /messages`

Send a WhatsApp message: template, or free-form reply. Scope: `messages:send`. Docs: https://www.app2email.com/docs/api/messages/send-template-message

Sends one approved template to one recipient, or to several when `to` lists several numbers (or `recipients` gives each number its own values). The parameters are checked against the template before sending; on a mismatch the error includes a complete, correct `example_request` for that template. Nothing is sent when the request itself is invalid. `dry_run` checks without sending; `background` answers 202 and sends after; `send_at` schedules it (202, status scheduled). `type` text, image, video, document or interactive sends a free-form message to one contact within 24 hours of the contact's last message (422 outside_24h_window otherwise). `segment` sends a template to a saved segment's contacts. A business-scoped user id works wherever a number does. Also `audio`, `sticker`, `location`, `contacts`, `reaction` and the newer interactive kinds; template carousels, limited-time offers, catalog, MPM, SPM, flow and OTP buttons. `callback_data` comes back in message.status. MARKETING templates follow `marketing_api` / messages.marketing_route (`sent_via` in the answer).


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| Idempotency-Key | header | string |  | Optional. A unique value for this message or list (eg a UUID). The same request with the same key within 24 hours gets the first answer again, and nothing is sent twice. Ignored by dry runs. |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| messaging_product | string (whatsapp) |  | Optional. Always 'whatsapp'. |
| recipient_type | string (individual) |  | Optional. Always 'individual'. |
| to | string |  | Recipient's WhatsApp number with country code. Digits only is best (spaces, '+', '-' are removed). Several recipients: separate the numbers with commas, eg "61412345678,61498765432" (semicolons and new lines work too), or send a JSON array of numbers. Each number gets its own message, and the response lists the result per number in 'results'. A free-form message (not 'template') goes to one number. A business-scoped user id (eg 61.AbC123, from from_user_id) is accepted as it is. |
| recipient | string |  | Optional, instead of 'to': one contact, a phone number or a business-scoped user id (BSUID). Sent to WhatsApp as 'recipient'. |
| segment | string |  | Optional, app2email only, instead of 'to' / 'recipients': the id or name of a saved segment (GET /segments). Templates only. Each contact's named template parameters without a value are filled from its custom_fields ('name' from the contact's name). Recorded as a broadcast. |
| type | string (template \| text \| image \| video \| document \| interactive \| audio \| sticker \| location \| contacts \| reaction) |  | 'template' (default): an approved template. Otherwise a free-form message within the 24 hour window; the field of the same name holds it. Left out with status 'read': mark as read. |
| interactive | object |  | WhatsApp's interactive object. type button: action.buttons, up to 3 reply buttons (title up to 20 characters; the shortcut "buttons": ["Confirm", "Change"] works too). type list: action.button (the text that opens the list) and action.sections with rows (up to 10 rows in all; a row can be a plain title). type cta_url: action.parameters {display_text, url}. header: text (60 characters), or image / video / document (link, data or id) for button and cta_url. body.text up to 1024 characters, footer.text up to 60. Also (WhatsApp Cloud API's objects): carousel (action.cards: 2 to 10, image or video header, one URL button or quick replies each; or product cards {card_index, type: 'product', action: {product_retailer_id, catalog_id}}), location_request_message, request_contact_info, flow (action.parameters: flow_message_version '3', flow_id or flow_name, flow_cta), product and product_list (a connected catalog), catalog_message, call_permission_request and voice_call (Calling), address_message (India; optional text header), order_details and order_status (payments). The fixed action.name of a kind is filled in when left out. |
|   type | string (button \| list \| cta_url \| carousel \| location_request_message \| request_contact_info \| flow \| product \| product_list \| catalog_message \| call_permission_request \| voice_call \| address_message \| order_details \| order_status) | yes |  |
|   header | object |  |  |
|   body | object |  |  |
|   footer | object |  |  |
|   action | object | yes |  |
| template | object |  |  |
|   name | string | yes | Exact name of an APPROVED template. |
|   language | object |  | Required when the template exists in more than one language. |
|   components | array of object |  | Values for the template's placeholders and media. Leave out for templates without parameters. |
| text | object |  |  |
|   body | string | yes | The text. Up to 4096 characters. |
|   preview_url | boolean |  | true: show a preview of a link in the text. |
| image | object |  | Give exactly one of: link, data or id. 'filename' is shown to the recipient for documents. |
|   link | string |  | Public http(s) URL. app2email downloads the file and uploads it to WhatsApp. |
|   data | string |  | The file, base64 encoded. A 'data:<mime>;base64,' prefix is accepted. |
|   id | string |  | A media id from POST /media (or uploaded to WhatsApp for this number). |
|   filename | string |  | Needed with 'data' for documents. |
|   mime_type | string |  | Optional. The type is detected from the file where possible. |
|   caption | string |  | Optional text under the image, video or document. |
| video | object |  | Give exactly one of: link, data or id. 'filename' is shown to the recipient for documents. |
| document | object |  | Give exactly one of: link, data or id. 'filename' is shown to the recipient for documents. |
| reply_to | string |  | Optional, free-form only: the message_id of one of the contact's messages, quoted by this one. Meta's 'context': {"message_id": ...} works too. |
| send_at | string |  | Optional, templates only: send later. ISO 8601 with a time zone ('Z' or '+11:00'), 1 minute to 29 days ahead. The answer is HTTP 202 with status 'scheduled'. |
| campaign_name | string |  | Optional, app2email only. Several numbers in 'to' (or 'recipients'): the name of the broadcast this list is recorded as (Activity Log under Broadcasts). Default "API: <template name>". Not used for one number. |
| recipients | array of object |  | Optional, app2email only, instead of 'to': each number with its own values. Each entry's components replace the shared template.components of the same type (a button: the same index). Every number is checked before anything is sent. |
| dry_run | boolean |  | Optional, app2email only. true: check everything and answer with the exact WhatsApp message per number, without sending, logging or counting anything. |
| background | boolean |  | Optional, app2email only. true: answer HTTP 202 once everything is checked and the media uploaded, then send. Progress: broadcast.status_url (GET /v1/{number}/broadcasts/{code}) or the broadcast.completed webhook event. |
| audio | object |  | aac, amr, mp3, m4a or ogg (OPUS), up to 16 MB. No caption. |
|   link | string |  | Public http(s) URL. app2email downloads the file and uploads it to WhatsApp. |
|   data | string |  | The file, base64 encoded. |
|   id | string |  | A media id from POST /media. |
|   filename | string |  |  |
|   mime_type | string |  |  |
|   voice | boolean |  | true: a voice message (play button, transcript). Ogg with the OPUS codec only; app2email does not convert. |
| sticker | object |  | WebP only: up to 100 KB static, 500 KB animated. No caption. |
|   link | string |  | Public http(s) URL. app2email downloads the file and uploads it to WhatsApp. |
|   data | string |  | The file, base64 encoded. |
|   id | string |  | A media id from POST /media. |
|   filename | string |  |  |
|   mime_type | string |  |  |
| location | object |  |  |
|   latitude | number | yes |  |
|   longitude | number | yes |  |
|   name | string |  |  |
|   address | string |  |  |
| contacts | array of object |  | type 'contacts': 1 to 20 cards. |
| reaction | object |  |  |
|   message_id | string | yes | A message the contact sent, up to 30 days old. |
|   emoji | string | yes | One emoji. "" removes your reaction. |
| context | object |  | Meta's form of reply_to. |
|   message_id | string |  |  |
| callback_data | string |  | Optional. Sent to WhatsApp as biz_opaque_callback_data; back as data.callback_data in this message's message.status events. Meta's own field name works too. |
| recipient_identity_key_hash | string |  | Optional, one recipient (per number: in recipients[]): delivered only while the contact's identity key has this hash (message.received data.identity_key_hash); else message.failed, 137000 recipient_identity_changed. Needs PUT /settings/identity-check. |
| marketing_api | string (auto \| cloud_api \| mm_api) |  | Optional, MARKETING templates: the path for this send (true = mm_api, false = cloud_api). Default: the number's setting messages.marketing_route (auto). |
| product_policy | string (CLOUD_API_FALLBACK \| STRICT) |  | Optional, Marketing Messages API only: STRICT = no fallback to the Cloud API. Default CLOUD_API_FALLBACK. |
| message_activity_sharing | boolean |  | Optional, Marketing Messages API only: share read and click activity with Meta for this message. |
| status | string (read) |  | Meta's mark-read body: 'read' with message_id (no type). |
| message_id | string |  | Meta's mark-read body: the received message. |
| typing_indicator | object |  | Meta's mark-read body: also show the typing indicator. |
|   type | string (text) |  |  |


Example request:

```json
{
  "to": "61412345678",
  "type": "template",
  "template": {
    "name": "order_update",
    "language": {
      "code": "en"
    },
    "components": [
      {
        "type": "body",
        "parameters": [
          {
            "type": "text",
            "text": "John"
          },
          {
            "type": "text",
            "text": "#1234"
          }
        ]
      }
    ]
  }
}
```


Example answer:

```json
{
  "success": true,
  "request_id": "kxrkf",
  "message_id": "wamid.HBgLNjE0MTIzNDU2NzgVAgARGBJTQU1QTEVfVEVTVF9FVkVOVAA=",
  "status": "accepted",
  "from": "4976659348270",
  "to": "61412345678",
  "template": {
    "name": "order_update",
    "language": "en",
    "category": "UTILITY"
  },
  "text": "Hi John, your order #1234 has shipped.",
  "conversation_url": "https://www.app2email.com/conversation/61412345678_4976659348270_...",
  "note": "accepted by WhatsApp. delivery and read status appear in your app2email Activity Log (WhatsApp sent).",
  "contacts": [
    {
      "input": "61412345678",
      "wa_id": "61412345678"
    }
  ]
}
```


### `GET /messages/{message_id}`

Status of a sent message. Scope: `messages:read`. Docs: https://www.app2email.com/docs/api/messages/get-message-status

Any message sent from the number (API, Broadcast page, email replies): status, the time of each step, why it failed, and the contact's reply or button tap.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| message_id | path | string | yes | The message_id from the send answer (starts with 'wamid.'). URL-encode it. |


### `POST /messages/read`

Mark a received message as read, optionally typing. Scope: `messages:send`. Docs: https://www.app2email.com/docs/api/messages/mark-message-read

Blue ticks on a message the contact sent (and the earlier ones of the chat), up to 30 days old; `typing` also shows the typing indicator for up to 25 seconds. Free: not counted, no 24 hour window. Meta's own body on POST /messages works too.


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| message_id | string | yes | A message the contact sent, up to 30 days old. |
| typing | boolean |  | true: also the typing indicator (25 seconds or until your reply). |
| dry_run | boolean |  |  |


Example answer:

```json
{
  "success": true,
  "request_id": "k2rdq",
  "message_id": "wamid.HBgLNjE0MTIzNDU2NzgVAgASGBQzQUZCMTY0MDc2MUYwNzBDNTY5MAA=",
  "status": "read",
  "typing_indicator": true
}
```


### `GET /marketing`

Where marketing templates go: Cloud API or Marketing Messages API. Scope: `messages:read`. Docs: https://www.app2email.com/docs/api/messages/get-marketing-status

The route setting (messages.marketing_route), the route a marketing template takes now, WhatsApp's onboarding status and the account's Cloud API switch. `?refresh=true` asks WhatsApp now (otherwise up to 1 hour old).


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| refresh | query | boolean |  | true: ask WhatsApp now. |


Example answer:

```json
{
  "success": true,
  "request_id": "q8mkt",
  "marketing": {
    "route": "auto",
    "effective_route": "mm_api",
    "onboarding_status": "ONBOARDED",
    "cloud_api_marketing_disabled": false,
    "checked_at": "2026-11-06T01:00:00Z"
  }
}
```


## Templates


### `GET /templates`

List your templates, with an example request for each. Scope: `messages:read`. Docs: https://www.app2email.com/docs/api/templates/list-templates

All templates of the number's WhatsApp account: status, category, what values each needs, and for approved templates a complete example request.


### `POST /templates`

Create a template and submit it for approval. Scope: `templates:manage`. Docs: https://www.app2email.com/docs/api/templates/create-template

Needs the 'templates:manage' scope. The template goes to WhatsApp for review (minutes to a day). `template.status_changed` tells the result. Every Meta field is passed on (TTL, link tracking, max price, Template Library). WABA-wide: every number on this WhatsApp Business Account uses the same templates.


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| name | string | yes | Lowercase letters, digits and underscores. |
| language | string | yes |  |
| category | string (MARKETING \| UTILITY \| AUTHENTICATION) | yes |  |
| components | array of object |  | WhatsApp's components: BODY (text), HEADER, FOOTER, BUTTONS. Required unless library_template_name is given. |
| parameter_format | string (NAMED \| POSITIONAL) |  | NAMED ({{first_name}}) or POSITIONAL ({{1}}) placeholders. |
| allow_category_change | boolean |  | Passed on; Meta ignores it since 9 Apr 2025 (it sets the category itself). |
| message_send_ttl_seconds | integer |  | How long WhatsApp tries to deliver (Meta's ranges per category). |
| cta_url_link_tracking_opted_out | boolean |  | true: no click tracking on URL buttons. |
| is_primary_device_delivery_only | boolean |  |  |
| sub_category | string |  |  |
| display_format | string |  |  |
| degrees_of_freedom_spec | object |  | Marketing creative options, as Meta takes them. |
| send_type | string (campaign \| direct) |  | Marketing Messages API templates. |
| optimization_spec | object |  | Marketing max price (Meta: 'max price'). Needs the WhatsApp account enrolled in Meta's max price feature (Marketing Messages API). Both fields null: back to rate card pricing. Replaces bid_spec (not accepted since 31 Jul 2026). |
|   bid_amount | integer | yes | Most WhatsApp may charge per 1,000 deliveries, in the smallest unit of the account's currency (5000 = USD 0.05 a message). |
|   bid_strategy | string (LOWEST_COST_WITH_BID_CAP) | yes |  |
|   bid_country_multiplier_overrides | object |  | Country (ISO 3166-1 alpha-2) -> multiplier (above 0, at most 10), up to 240. Replaces the whole map; {} removes it. |
| library_template_name | string |  | Create from the Template Library (GET /template-library); then no components. |
| library_template_button_inputs | array of object |  | Library templates with buttons: the website and phone number. |
| library_template_body_inputs | object |  |  |


Example request:

```json
{
  "name": "order_update",
  "language": "en",
  "category": "UTILITY",
  "components": [
    {
      "type": "BODY",
      "text": "Hi {{1}}, your order {{2}} has shipped.",
      "example": {
        "body_text": [
          [
            "John",
            "#1234"
          ]
        ]
      }
    }
  ]
}
```


### `GET /templates/{name}`

One template: status, rejection reason, what it needs. Scope: `messages:read`. Docs: https://www.app2email.com/docs/api/templates/get-template

Every language of the template. Not from a cache: a status that just changed shows. With every field Meta keeps (sub_category, previous_category, TTL, link tracking, library name).


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| name | path | string | yes | The template's name. |


Example answer:

```json
{
  "success": true,
  "request_id": "k7qtm",
  "name": "order_update",
  "versions": [
    {
      "id": "1234567890",
      "name": "order_update",
      "language": "en",
      "category": "UTILITY",
      "status": "APPROVED",
      "can_send": true,
      "needs": {
        "body": "2 text values"
      },
      "example_request": {
        "to": "61412345678",
        "type": "template",
        "template": {
          "name": "order_update",
          "language": {
            "code": "en"
          },
          "components": [
            {
              "type": "body",
              "parameters": [
                {
                  "type": "text",
                  "text": "John"
                },
                {
                  "type": "text",
                  "text": "#1234"
                }
              ]
            }
          ]
        }
      }
    }
  ]
}
```


### `PATCH /templates/{name}`

Edit a template (components, category, TTL, max price). Scope: `templates:manage`. Docs: https://www.app2email.com/docs/api/templates/edit-template

Needs 'templates:manage'. Only APPROVED, REJECTED or PAUSED templates; an approved one at most once a day, 10 times in 30 days. WABA-wide: every number on this WhatsApp Business Account uses the same templates.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| name | path | string | yes | The template's name. |
| language | query | string |  | The template's language (eg en, en_US). Needed when the template has several. |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| components | array of object |  | All components, in WhatsApp's format. A media header may use example.header_sample_url (a public link). |
| category | string (MARKETING \| UTILITY \| AUTHENTICATION) |  | Not for APPROVED templates. |
| message_send_ttl_seconds | integer |  | How long WhatsApp tries to deliver (Meta's ranges per category). |
| cta_url_link_tracking_opted_out | boolean |  | true: no click tracking on URL buttons. |
| parameter_format | string (NAMED \| POSITIONAL) |  |  |
| sub_category | string |  |  |
| display_format | string |  |  |
| is_primary_device_delivery_only | boolean |  |  |
| optimization_spec | object |  | Marketing max price (Meta: 'max price'). Needs the WhatsApp account enrolled in Meta's max price feature (Marketing Messages API). Both fields null: back to rate card pricing. Replaces bid_spec (not accepted since 31 Jul 2026). |
|   bid_amount | integer | yes | Most WhatsApp may charge per 1,000 deliveries, in the smallest unit of the account's currency (5000 = USD 0.05 a message). |
|   bid_strategy | string (LOWEST_COST_WITH_BID_CAP) | yes |  |
|   bid_country_multiplier_overrides | object |  | Country (ISO 3166-1 alpha-2) -> multiplier (above 0, at most 10), up to 240. Replaces the whole map; {} removes it. |
| allow_category_change | boolean |  | Passed on; Meta ignores it since 9 Apr 2025. |


Example request:

```json
{
  "components": [
    {
      "type": "BODY",
      "text": "Hi {{1}}, your order {{2}} is on its way.",
      "example": {
        "body_text": [
          [
            "John",
            "#1234"
          ]
        ]
      }
    },
    {
      "type": "FOOTER",
      "text": "Reply STOP to opt out"
    }
  ]
}
```


Example answer:

```json
{
  "success": true,
  "request_id": "t2edt",
  "template": {
    "id": "1234567890",
    "name": "order_update",
    "language": "en",
    "previous_status": "APPROVED"
  },
  "changed": [
    "components"
  ],
  "note": "WhatsApp reviews the edited template again; the template.status_changed event tells the result. Every number on this WhatsApp Business Account uses the new version."
}
```


### `DELETE /templates/{name}`

Delete a template (every language, or one). Scope: `templates:manage`. Docs: https://www.app2email.com/docs/api/templates/delete-template

Needs the 'templates:manage' scope. The template app2email uses for its own alerts cannot be deleted here. WABA-wide: every number on this WhatsApp Business Account uses the same templates.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| name | path | string | yes | The template's name. |
| language | query | string |  | Only this language. Default: every language. |


Example answer:

```json
{
  "success": true,
  "request_id": "e2mxa",
  "deleted": "order_update",
  "languages": [
    "en"
  ],
  "note": "All languages of the template were deleted. The same name and language can be used again after WhatsApp has removed it."
}
```


### `POST /templates/delete`

Delete several templates at once (all or nothing). Scope: `templates:manage`. Docs: https://www.app2email.com/docs/api/templates/delete-templates

Needs 'templates:manage'. names (every language) or ids, at most 100 languages; one bad id deletes nothing. WABA-wide: every number on this WhatsApp Business Account uses the same templates.


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| names | array of string |  |  |
| ids | array of string |  |  |


Example answer:

```json
{
  "success": true,
  "request_id": "t3blk",
  "deleted": [
    {
      "name": "summer_sale",
      "language": "en",
      "id": "1234567891"
    },
    {
      "name": "old_promo",
      "language": "en",
      "id": "1234567892"
    },
    {
      "name": "old_promo",
      "language": "de",
      "id": "1234567893"
    }
  ],
  "note": "Deleted on the whole WhatsApp Business Account. An approved template's name and language can be used again after 30 days."
}
```


### `POST /templates/{name}/archive`

Archive a template (deleted by WhatsApp after 28 days). Scope: `templates:manage`. Docs: https://www.app2email.com/docs/api/templates/archive-template

Needs 'templates:manage'. Every language, or ?language=. Only APPROVED or REJECTED templates; unarchive within 28 days to keep it. WABA-wide: every number on this WhatsApp Business Account uses the same templates.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| name | path | string | yes | The template's name. |
| language | query | string |  | Only this language. Default: every language. |


Example answer:

```json
{
  "success": true,
  "request_id": "t4arc",
  "name": "summer_sale",
  "archived": [
    {
      "language": "en",
      "id": "1234567891"
    }
  ],
  "failed": [],
  "note": "Archived on the whole WhatsApp Business Account. WhatsApp deletes archived templates 28 days after archiving; unarchive before then to keep them."
}
```


### `POST /templates/{name}/unarchive`

Unarchive a template. Scope: `templates:manage`. Docs: https://www.app2email.com/docs/api/templates/unarchive-template

Needs 'templates:manage'. Back to its previous status. Within 28 days of archiving. WABA-wide: every number on this WhatsApp Business Account uses the same templates.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| name | path | string | yes | The template's name. |
| language | query | string |  | Only this language. Default: every language. |


Example answer:

```json
{
  "success": true,
  "request_id": "t4una",
  "name": "summer_sale",
  "unarchived": [
    {
      "language": "en",
      "id": "1234567891"
    }
  ],
  "failed": [],
  "note": "Unarchived: back to their previous status (or APPROVED) on the whole WhatsApp Business Account."
}
```


### `GET /templates/{name}/compare`

Compare two templates: block rate, sends, top block reason. Scope: `messages:read`. Docs: https://www.app2email.com/docs/api/templates/compare-templates

Both templates of this account, each sent at least 1,000 times in the period.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| name | path | string | yes | The template's name. |
| with | query | string | yes | The other template's name. |
| language | query | string |  | The template's language (eg en, en_US). Needed when the template has several. |
| with_language | query | string |  | The other template's language. |
| days | query | integer (7 \| 30 \| 60 \| 90) |  | How far back: 7, 30, 60 or 90 days. |


Example answer:

```json
{
  "success": true,
  "request_id": "t5cmp",
  "template": {
    "name": "summer_sale",
    "language": "en",
    "id": "5289179717853347"
  },
  "with": {
    "name": "summer_sale_v2",
    "language": "en",
    "id": "1533406637136032"
  },
  "days": 30,
  "since": "2026-10-07T01:00:00.000Z",
  "until": "2026-11-06T01:00:00.000Z",
  "metrics": [
    {
      "metric": "BLOCK_RATE",
      "type": "RELATIVE",
      "order_by_relative_metric": [
        "1533406637136032",
        "5289179717853347"
      ]
    },
    {
      "metric": "MESSAGE_SENDS",
      "type": "NUMBER_VALUES",
      "number_values": [
        {
          "key": "5289179717853347",
          "value": 1273
        },
        {
          "key": "1533406637136032",
          "value": 1042
        }
      ]
    },
    {
      "metric": "TOP_BLOCK_REASON",
      "type": "STRING_VALUES",
      "string_values": [
        {
          "key": "5289179717853347",
          "value": "UNKNOWN_BLOCK_REASON"
        },
        {
          "key": "1533406637136032",
          "value": "UNKNOWN_BLOCK_REASON"
        }
      ]
    }
  ]
}
```


### `PUT /templates/{name}/authentication`

Create or update an authentication template in many languages. Scope: `templates:manage`. Docs: https://www.app2email.com/docs/api/templates/upsert-auth-template

Needs 'templates:manage'. Missing languages are created, existing ones updated, in one call. Not for business-scoped user ids (131062). WABA-wide: every number on this WhatsApp Business Account uses the same templates.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| name | path | string | yes | The authentication template's name. |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| languages | array of string | yes |  |
| otp_type | string (COPY_CODE \| ONE_TAP \| ZERO_TAP) |  |  |
| add_security_recommendation | boolean |  | Adds 'For your security, do not share this code.' |
| code_expiration_minutes | integer |  | Adds the expiry footer. |
| supported_apps | array of object |  | ONE_TAP and ZERO_TAP: 1 to 5 Android apps. |
| zero_tap_terms_accepted | boolean |  | ZERO_TAP: must be true. |
| components | array of object |  | Instead of the fields above: BODY, FOOTER, BUTTONS in WhatsApp's format. |
| message_send_ttl_seconds | integer |  |  |


Example answer:

```json
{
  "success": true,
  "request_id": "t8ups",
  "name": "verify_code",
  "category": "AUTHENTICATION",
  "templates": [
    {
      "language": "en_US",
      "id": "954638012257287",
      "status": "APPROVED"
    },
    {
      "language": "es_ES",
      "id": "969725527415202",
      "status": "APPROVED"
    }
  ],
  "note": "Created or updated in every language listed, on the whole WhatsApp Business Account. Send it with the code as the body parameter and the copy-code button parameter."
}
```


### `GET /template-previews`

Authentication template texts, per language. Scope: `messages:read`. Docs: https://www.app2email.com/docs/api/templates/preview-auth-templates

The fixed texts WhatsApp puts into an authentication template (body, security line, expiry footer, buttons).


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| languages | query | string |  | Comma separated (eg en_US,es_ES). Default: every language. |
| add_security_recommendation | query | boolean |  | With the security line. |
| code_expiration_minutes | query | integer |  | With the expiry footer (1 to 90). |


Example answer:

```json
{
  "success": true,
  "request_id": "t9prv",
  "category": "AUTHENTICATION",
  "previews": [
    {
      "language": "en_US",
      "body": "*{{1}}* is your verification code. For your security, do not share this code.",
      "footer": "This code expires in 10 minutes.",
      "buttons": [
        {
          "autofill_text": "Autofill",
          "text": "Copy code"
        }
      ]
    }
  ]
}
```


### `GET /template-library`

Meta's Template Library (pre-approved templates). Scope: `messages:read`. Docs: https://www.app2email.com/docs/api/templates/list-template-library

Utility and authentication templates written by Meta. Create one with POST /templates and library_template_name.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| search | query | string |  | Words in the template. |
| topic | query | string |  | eg ORDER_MANAGEMENT, PAYMENTS, ACCOUNT_UPDATE, CUSTOMER_FEEDBACK. |
| usecase | query | string |  | eg SHIPMENT_CONFIRMATION, PAYMENT_DUE_REMINDER. |
| industry | query | string |  | E_COMMERCE or FINANCIAL_SERVICES. |
| language | query | string |  | eg en_US. |
| name | query | string |  | A library template's name. |
| limit | query | integer |  | 1 to 200. |
| cursor | query | string |  | next_cursor of the previous answer. |


Example answer:

```json
{
  "success": true,
  "request_id": "t6lib",
  "templates": [
    {
      "name": "delivery_update_1",
      "language": "en_US",
      "category": "UTILITY",
      "topic": "ORDER_MANAGEMENT",
      "usecase": "DELIVERY_UPDATE",
      "industry": [
        "E_COMMERCE"
      ],
      "body": "Good news! Your order {{1}} is on its way. Track it here.",
      "body_params": [
        "#12345"
      ],
      "body_param_types": [
        "TEXT"
      ],
      "buttons": [
        {
          "type": "URL",
          "text": "Track order",
          "url": "https://www.example.com/"
        }
      ],
      "id": "7147013345418927"
    }
  ],
  "next_cursor": null,
  "note": "Create one with POST /v1/4976659348270/templates {\"name\", \"language\", \"category\", \"library_template_name\", \"library_template_button_inputs\"}."
}
```


### `GET /template-insights`

Template insights: sent, delivered, read, clicked, cost. Scope: `messages:read`. Docs: https://www.app2email.com/docs/api/templates/get-template-insights

Per template and day (UTC), 90 days back, at most 10 template languages. Insights must be on (POST); not for EU or Japan accounts.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| templates | query | string | yes | Template names, comma separated. |
| language | query | string |  | Only this language. |
| since | query | string |  | First day, YYYY-MM-DD. Default: 6 days before until. |
| until | query | string |  | Last day, YYYY-MM-DD. Default: today. |
| metrics | query | string |  | Comma separated: sent, delivered, read, clicked, cost. Default: all. |
| product | query | string (cloud_api \| marketing_messages) |  | cloud_api (default) or marketing_messages. |


Example answer:

```json
{
  "success": true,
  "request_id": "t7get",
  "since": "2026-10-31",
  "until": "2026-11-06",
  "product": "cloud_api",
  "templates": [
    {
      "name": "summer_sale",
      "language": "en",
      "id": "1234567891"
    }
  ],
  "data_points": [
    {
      "template": "summer_sale",
      "language": "en",
      "template_id": "1234567891",
      "date": "2026-11-05",
      "sent": 1200,
      "delivered": 1150,
      "read": 870,
      "clicked": [
        {
          "type": "url_button",
          "button_content": "Shop now",
          "count": 96
        }
      ],
      "cost": [
        {
          "type": "amount_spent",
          "value": 30.12
        },
        {
          "type": "cost_per_delivered",
          "value": 0.03
        }
      ]
    }
  ],
  "note": "Daily, UTC. Read and click counts stop changing 7 days after a message is sent. cost is left out for accounts billed through a partner's credit line."
}
```


### `POST /template-insights`

Switch template insights on (cannot be undone). Scope: `templates:manage`. Docs: https://www.app2email.com/docs/api/templates/enable-template-insights

Needs 'templates:manage' and {"confirm": true}. Adds link tracking and lets Meta collect anonymised chat data. WABA-wide: every number on this WhatsApp Business Account uses the same templates.


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| confirm | boolean (True) | yes | Must be true: switching insights on cannot be undone. |


Example answer:

```json
{
  "success": true,
  "request_id": "t7ins",
  "enabled": true,
  "note": "Template insights are on for the whole WhatsApp Business Account, from now on (no data from before). This cannot be undone. Link tracking of a template's URL buttons can be turned off per template (cta_url_link_tracking_opted_out)."
}
```


## Media


### `POST /media`

Upload a file once, get a media id. Scope: `messages:send`. Docs: https://www.app2email.com/docs/api/media/upload-media

Uploads an image, video, document, audio file or sticker to WhatsApp and returns a `media_id` for `{"id": ...}` in later sends (templates or free-form). WhatsApp keeps it 30 days. JSON (a link or base64 data) or multipart/form-data (`file`, optional `type`). Limits: image JPEG/PNG 5 MB, video MP4/3GP 16 MB, audio 16 MB, sticker WebP 100 KB static / 500 KB animated, document 100 MB. A sandbox key checks the file and uploads nothing.


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| type | string (image \| video \| document \| audio \| sticker) | yes |  |
| file | object | yes | Give 'link' (a public URL) or base64 'data'. 'filename' for documents. |
|   link | string |  |  |
|   data | string |  |  |
|   filename | string |  |  |
|   mime_type | string |  | Optional. The type is detected from the file where possible. |
|   voice | boolean |  | Audio: check it is a voice message (Ogg with OPUS). |


Example request:

```json
{
  "type": "image",
  "file": {
    "link": "https://example.com/photo.jpg"
  }
}
```


### `GET /media/{id}`

Download a received file (stored copy, else from WhatsApp). Scope: `messages:read`. Docs: https://www.app2email.com/docs/api/media/get-media

app2email keeps its own copy of every received image, video, audio, document and sticker (WhatsApp's ids expire after 7 days): served first. Without one, the file comes from WhatsApp by the message's media id, or by a WhatsApp media id in the URL. Header X-Media-Source: stored | whatsapp. `?info=true`: type, size and sha256 instead of the file. WhatsApp pauses media lookups after many errors, so an id it did not know is remembered for 30 minutes.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The message_id of a received message (wamid..., URL-encoded), or a WhatsApp media id (digits). |
| info | query | boolean |  | true: the file's type, size and sha256 as JSON, not the file. |


### `DELETE /media/{id}`

Delete an uploaded file at WhatsApp. Scope: `messages:send`. Docs: https://www.app2email.com/docs/api/media/delete-media

The media_id of POST /media (WhatsApp keeps uploads 30 days otherwise). A scheduled send that still uses it then fails. app2email's stored copies of received files stay.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The WhatsApp media id (digits). |


Example answer:

```json
{
  "success": true,
  "request_id": "d7mdl",
  "media_id": "1037543291543636",
  "deleted": true
}
```


## Broadcasts


### `GET /broadcasts`

Your latest broadcasts. Scope: `messages:read`. Docs: https://www.app2email.com/docs/api/broadcasts/list-broadcasts

Broadcasts sent through the API (several numbers) and from the Broadcast page, newest first.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| limit | query | integer |  | How many (1 to 100, default 20). |


### `GET /broadcasts/{code}`

A broadcast's status and the result per number. Scope: `messages:read`. Docs: https://www.app2email.com/docs/api/broadcasts/get-broadcast

Counts and the result for each number, live while a background send runs.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| code | path | string | yes | broadcast.code from the send answer, or from GET /broadcasts. |


### `GET /broadcasts/{code}/results.csv`

A broadcast's result for each message, as CSV. Scope: `messages:read`. Docs: https://www.app2email.com/docs/api/broadcasts/get-broadcast-csv

One row per message: number, status, message_id, the time of each step, the reply and the error. Opens in a spreadsheet. Values that start with = + - or @ get a ' in front, so a spreadsheet does not run them as formulas.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| code | path | string | yes | broadcast.code from the send answer, or from GET /broadcasts. |


### `POST /broadcasts/{code}/cancel`

Cancel a scheduled or sending API broadcast. Scope: `messages:send`. Docs: https://www.app2email.com/docs/api/broadcasts/cancel-broadcast

Needs the 'messages:send' scope. A scheduled broadcast (send_at) is removed: nothing is sent (200). A broadcast that is sending now (API list, background or scheduled): the messages not yet handed to WhatsApp are not sent, those already sent stay sent (202, status cancelling). Broadcasts started from the dashboard, and finished ones, cannot be cancelled here (409 broadcast_not_cancellable). broadcast.completed is sent with data.status cancelled.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| code | path | string | yes | broadcast.code from the send answer. |


Example answer:

```json
{
  "success": true,
  "request_id": "u1nqc",
  "broadcast": {
    "code": "k3XbQ9rTzP2mWv7a1c9e",
    "status": "cancelled"
  },
  "sent_before_cancel": 0,
  "note": "It was scheduled and had not started: nothing was sent."
}
```


## Account


### `GET /me`

Check the key: its scopes, the number, the plan and the limits. Scope: `any`. Docs: https://www.app2email.com/docs/api/account/get-me

Works with any valid key, whatever its scopes. Use it for a 'test connection' step in Zapier, Make, n8n or Power Automate.


Example answer:

```json
{
  "success": true,
  "request_id": "a7k3p",
  "key_valid": true,
  "api_version": "v1",
  "number": "4976659348270",
  "plan": "standard_5000",
  "service_status": "LIVE",
  "key": {
    "name": "Zapier",
    "scopes": [
      "messages:read",
      "messages:send"
    ],
    "ip_allow": ""
  },
  "limits": {
    "max_numbers_per_request": 1000,
    "requests_per_second": 20,
    "burst": 50,
    "rate_limit_mode": "log_only",
    "webhooks_max": 5
  },
  "scopes_available": [
    "messages:send",
    "messages:read",
    "dnc:manage",
    "webhooks:manage",
    "templates:manage",
    "settings:manage",
    "contacts:manage",
    "calls:manage",
    "bookings:manage",
    "submissions:manage",
    "orders:manage",
    "tickets:manage"
  ]
}
```


### `GET /requests`

The latest logged API requests. Scope: `messages:read`. Docs: https://www.app2email.com/docs/api/account/list-requests

Only errors (status 400 and up) and requests that change something (sends, webhook and settings changes) are logged, for 30 days. Each one has its request_id, route, status, time, key and address. No bodies and no keys are stored.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| limit | query | integer |  | How many (1 to 200, default 50). |
| status | query | string |  | error (400 and up), ok (below 400), or an HTTP status such as 422. |


Example answer:

```json
{
  "success": true,
  "request_id": "x9d2m",
  "requests": [
    {
      "request_id": "kxrkf",
      "time": "2026-10-26T01:12:09Z",
      "method": "POST",
      "route": "/v1/4976659348270/messages",
      "status": 422,
      "ms": 412,
      "key": "Zapier",
      "ip": "203.0.113.7"
    }
  ],
  "note": "Only errors and requests that change something are logged. Rows are kept 30 days."
}
```


### `GET /requests/{id}`

One logged request, by its request_id. Scope: `messages:read`. Docs: https://www.app2email.com/docs/api/account/get-request

The request_id of any answer, for example from a failed send.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The request_id from an answer. |


Example answer:

```json
{
  "success": true,
  "request_id": "p3uvn",
  "request": {
    "request_id": "kxrkf",
    "time": "2026-10-26T01:12:09Z",
    "method": "POST",
    "route": "/v1/4976659348270/messages",
    "status": 422,
    "ms": 412,
    "key": "Zapier",
    "ip": "203.0.113.7"
  }
}
```


### `GET /usage/history`

Messages and broadcasts per month. Scope: `messages:read`. Docs: https://www.app2email.com/docs/api/account/get-usage-history

Per calendar month (UTC), newest first: messages sent, failed, received and broadcasts.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| months | query | integer |  | How many months (1 to 24, default 6). |


Example answer:

```json
{
  "success": true,
  "request_id": "m4ry7",
  "number": "4976659348270",
  "months": [
    {
      "month": "2026-10",
      "messages_sent": 412,
      "messages_failed": 3,
      "messages_received": 97,
      "broadcasts": 2
    },
    {
      "month": "2026-09",
      "messages_sent": 380,
      "messages_failed": 1,
      "messages_received": 88,
      "broadcasts": 1
    }
  ]
}
```


### `GET /stats`

Message counts, delivery and read rates for a period. Scope: `messages:read`. Docs: https://www.app2email.com/docs/api/account/get-stats

For a time range (default the last 30 days, at most 366 days). The same counts as a broadcast report.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| from | query | string |  | Start of the range. ISO 8601. |
| to | query | string |  | End of the range. ISO 8601. |


Example answer:

```json
{
  "success": true,
  "request_id": "t6bwe",
  "from": "2026-09-26T00:00:00Z",
  "to": "2026-10-26T00:00:00Z",
  "messages": {
    "submitted": 120,
    "accepted": 118,
    "sent": 117,
    "delivered": 110,
    "read": 84,
    "failed": 2,
    "replied": 19
  },
  "received": 40,
  "rates": {
    "delivery": 0.9402,
    "read": 0.7636,
    "reply": 0.1624
  }
}
```


### `GET /usage`

Plan, messages used and left, limits, what WhatsApp charges. Scope: `messages:read`. Docs: https://www.app2email.com/docs/api/account/get-usage

WhatsApp messages used and left this billing month, the billing period, the most numbers per send request, your own monthly cap, and `meta_pricing`: the month's messages by Meta's pricing category with an indicative cost.


### `GET /usage/meta`

What WhatsApp charges this billing month, per day. Scope: `messages:read`. Docs: https://www.app2email.com/docs/api/account/get-usage-meta

The billing month's messages by Meta's pricing category (the 1,000 free service messages, billable service, utility, marketing, authentication) with an indicative cost estimate, in all and per day. From the pricing object of WhatsApp's status webhooks; Meta bills you directly, so treat the amount as a guide.


Example answer:

```json
{
  "success": true,
  "request_id": "m7bqs",
  "number": "4976659348270",
  "meta_pricing": {
    "billing_period": {
      "start": "2026-10-15T00:00:00Z",
      "end": "2026-11-15T00:00:00Z"
    },
    "counts": {
      "service_free_used": 412,
      "service_billable": 0,
      "utility": 120,
      "marketing": 35,
      "authentication": 0,
      "free_entry_point": 2,
      "unknown": 3,
      "total": 572,
      "estimated_cost_usd": 4.3
    },
    "free_service_messages": {
      "allowance_per_month": 1000,
      "used": 412,
      "left": 588
    },
    "estimated_cost": {
      "currency": "USD",
      "amount": 4.3,
      "rate_region": "Rest of Asia Pacific (Australia, New Zealand, Japan, ...)",
      "rate_region_code": "apac",
      "rates_per_message": {
        "marketing": 0.0842,
        "utility": 0.0113,
        "authentication": 0.0113,
        "service": 0.0113
      },
      "rates_last_checked": "2026-11-02"
    },
    "days": [
      {
        "date": "2026-11-01",
        "counts": {
          "service_free_used": 20,
          "service_billable": 0,
          "utility": 5,
          "marketing": 0,
          "authentication": 0,
          "free_entry_point": 0,
          "unknown": 0,
          "total": 25,
          "estimated_cost_usd": 0.0565
        }
      }
    ]
  }
}
```


## Conversations


### `GET /conversations`

The contacts, most recent activity first. Scope: `messages:read`. Docs: https://www.app2email.com/docs/api/conversations/list-conversations

One entry per contact, with the last message in each direction and whether a free-form reply can be sent now (window_open).


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| since | query | string |  | Only contacts active at or after this time. ISO 8601. |
| limit | query | integer |  | How many (1 to 200, default 50). |
| cursor | query | string |  | The next_cursor of the previous answer, unchanged. Leave out for the first page. |


Example answer:

```json
{
  "success": true,
  "request_id": "q2lzd",
  "conversations": [
    {
      "contact": "61412345678",
      "name": "John",
      "last_inbound": "2026-10-26T01:20:44Z",
      "last_outbound": "2026-10-26T01:12:09Z",
      "window_open": true,
      "messages": 12,
      "conversation_url": "https://www.app2email.com/conversation/61412345678_4976659348270_..."
    }
  ],
  "next_cursor": null,
  "count": 1
}
```


### `GET /conversations/{phone}/messages`

One contact's messages, both directions. Scope: `messages:read`. Docs: https://www.app2email.com/docs/api/conversations/list-conversation-messages

The messages with one contact, newest first. window_open says whether a free-form reply can be sent now.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| phone | path | string | yes | The contact's number, with country code, or their business-scoped user id. |
| since | query | string |  | At or after this time. ISO 8601. |
| until | query | string |  | Before this time. ISO 8601. |
| limit | query | integer |  | How many (1 to 200, default 50). |
| cursor | query | string |  | The next_cursor of the previous answer, unchanged. Leave out for the first page. |


Example answer:

```json
{
  "success": true,
  "request_id": "d8ce1",
  "contact": "61412345678",
  "window_open": true,
  "messages": [
    {
      "direction": "in",
      "message_id": "wamid.HBgLNjE0MTIzNDU2NzgVAgARGBJTQU1QTEVfVEVTVF9FVkVOVAA=",
      "from": "61412345678",
      "name": "John",
      "text": "Yes, Friday works",
      "media": null,
      "time": "2026-10-26T01:20:44Z",
      "conversation_url": "https://www.app2email.com/conversation/61412345678_4976659348270_..."
    }
  ],
  "next_cursor": null,
  "count": 1
}
```


### `GET /conversations/{contact}`

One contact: window state, last messages, owner. Scope: `messages:read`. Docs: https://www.app2email.com/docs/api/conversations/get-conversation

The conversation with one contact: `window_state` open or closed and `window_closes_at`, the last message each way, held email replies, and who owns it (see PUT .../owner).


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| contact | path | string | yes | The contact's number (country code first), or their business-scoped user id. |


Example answer:

```json
{
  "success": true,
  "request_id": "c9slm",
  "contact": "61412345678",
  "identity_type": "phone",
  "phone": "61412345678",
  "name": "John",
  "window_state": "open",
  "window_open": true,
  "window_closes_at": "2026-10-27T01:05:44Z",
  "last_inbound_at": "2026-10-26T01:20:44Z",
  "last_outbound_at": "2026-10-26T01:12:09Z",
  "messages": 12,
  "owner": "human",
  "owner_set_at": "2026-10-26T01:21:00Z",
  "owner_set_by": "api:Support bot",
  "owner_reason": "customer asked for a person",
  "owner_summary": "Wants to move the delivery to Monday.",
  "held_replies": false,
  "conversation_url": "https://www.app2email.com/conversation/61412345678_4976659348270_..."
}
```


### `PUT /conversations/{contact}/owner`

Hand a contact over: human, agent, paused, or back to normal. Scope: `messages:send`. Docs: https://www.app2email.com/docs/api/conversations/set-conversation-owner

Needs the 'messages:send' scope. `human` or `paused`: app2email's auto reply and the A2A / OpenClaw agent leave the contact alone (while the number's setting a2a.respect_owner is on); email forwarding carries on. `agent`: an automation owns it (a marker for everyone else). `""`: the normal routing. `until_minutes` makes it temporary. Fires the conversation.owner_changed webhook event. A number that has never been in touch gets a conversation record so the owner can be set first.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| contact | path | string | yes | The contact's number (country code first), or their business-scoped user id. |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| owner | string ( \| agent \| human \| paused) | yes | '' = the normal routing. human / paused: the auto reply and the A2A / OpenClaw agent leave this contact alone. |
| reason | string |  |  |
| summary | string |  | What the conversation is about so far, for the person taking over. |
| until_minutes | integer |  | After this many minutes the owner goes back to ''. |


## Do Not Call


### `GET /donotcall`

The Do Not Call list, or check one number. Scope: `dnc:manage`. Docs: https://www.app2email.com/docs/api/do-not-call/list-do-not-call

The whole list, or with ?number= whether that number is on it.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| number | query | string |  | Check only this number (with country code). |


### `POST /donotcall`

Add numbers to the Do Not Call list. Scope: `dnc:manage`. Docs: https://www.app2email.com/docs/api/do-not-call/add-do-not-call

Up to 1000 numbers, with an optional name and note each. Numbers already on the list are left as they are. All or nothing: one invalid number, nothing is added.


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| numbers | array of object |  |  |
| number | string |  |  |
| name | string |  |  |
| note | string |  |  |


### `DELETE /donotcall/{phone}`

Remove a number from the Do Not Call list. Scope: `dnc:manage`. Docs: https://www.app2email.com/docs/api/do-not-call/remove-do-not-call


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| phone | path | string | yes | The number to remove, with country code. |


### `GET /compliance/export.csv`

Consent records, Do Not Call list and opt-ins as one CSV. Scope: `dnc:manage`. Docs: https://www.app2email.com/docs/api/do-not-call/export-compliance

Needs the 'dnc:manage' scope. One row per record with record_type (consent, do_not_call, opt_in), identity, name, status, time, source, text, note and evidence: the records the Spam Act 2003 expects you to be able to show.


## Settings


### `GET /settings/autoreply`

The auto reply to new contacts. Scope: `settings:manage`. Docs: https://www.app2email.com/docs/api/settings/get-autoreply

Needs the 'settings:manage' scope. The text of the first reply a new contact gets (the dashboard's Auto reply page).


Example answer:

```json
{
  "text": "Thanks for writing! We reply within a day."
}
```


### `PUT /settings/autoreply`

Change the auto reply text. Scope: `settings:manage`. Docs: https://www.app2email.com/docs/api/settings/set-autoreply

Text only: the image and attachment of the auto reply are set on the dashboard. 1 to 4000 characters.


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| text | string | yes | The first reply a new contact gets (the Default Auto Reply). 1 to 4000 characters. Auto Reply cards added on the dashboard (by date, day, time or keyword) are checked first; this text is used when none of them matches. |


Example answer:

```json
{
  "text": "Thanks for writing! We reply within a day."
}
```


### `GET /settings/forwarding`

Who gets the messages by email. Scope: `settings:manage`. Docs: https://www.app2email.com/docs/api/settings/get-forwarding

Needs the 'settings:manage' scope. The email addresses that get each WhatsApp message (the dashboard's Forward email page).


Example answer:

```json
{
  "success": true,
  "request_id": "f9hsi",
  "forwarding": {
    "to": [
      "a@x.com"
    ],
    "cc": [],
    "bcc": [],
    "text": "New WhatsApp message",
    "works_on_this_plan": true,
    "plan": "standard_5000"
  }
}
```


### `PUT /settings/forwarding`

Change who gets the messages by email. Scope: `settings:manage`. Docs: https://www.app2email.com/docs/api/settings/set-forwarding

Fields left out stay as they are. Up to 3 valid emails each for to, cc and bcc. WhatsApp-to-email forwarding works on the Professional and Trial plans (works_on_this_plan says whether it does for this number).


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| to | array of string |  | Up to 3 emails. Or a string: "a@x.com, b@y.com". |
| cc | array of string |  | Up to 3 emails. |
| bcc | array of string |  | Up to 3 emails. |
| text | string |  | The line put before each forwarded message. |


Example answer:

```json
{
  "success": true,
  "request_id": "f9hsi",
  "forwarding": {
    "to": [
      "a@x.com"
    ],
    "cc": [],
    "bcc": [],
    "text": "New WhatsApp message",
    "works_on_this_plan": true,
    "plan": "standard_5000"
  }
}
```


### `GET /settings/number`

The number's settings: email behaviour, caps, compliance. Scope: `messages:read`. Docs: https://www.app2email.com/docs/api/settings/get-number-settings

Every setting with its value (defaults filled in).


Example answer:

```json
{
  "success": true,
  "request_id": "s1xpa",
  "settings": {
    "email": {
      "delivery_receipts": "failed_only",
      "mark_read_on_open": false,
      "include_history": 20,
      "history_images": "link"
    },
    "caps": {
      "monthly_messages": 0
    },
    "compliance": {
      "adm_disclosure": "",
      "stop_keywords_extra": []
    },
    "a2a": {
      "respect_owner": true
    }
  }
}
```


### `PUT /settings/number`

Change some of the number's settings. Scope: `settings:manage`. Docs: https://www.app2email.com/docs/api/settings/update-number-settings

Needs the 'settings:manage' scope. Only the keys given change; nested objects (`{"email": {"mark_read_on_open": true}}`) or dotted keys (`{"email.mark_read_on_open": true}`) both work. Not with a sandbox key.


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| email | object |  |  |
|   delivery_receipts | string (failed_only \| none \| all) |  | An email to the sender when their email reply failed on WhatsApp (or for every status). |
|   mark_read_on_open | boolean |  | Send WhatsApp a read receipt when the forwarded email is opened. |
|   include_history | integer |  | Earlier messages of the conversation quoted under a forwarded message (the [HISTORY] block), at most 100. 0 = none and no Show All History button. 20 is what every number had before this setting existed. The dashboard offers 0, 10, 20, 50 and 100 (Chat History Summary). |
|   history_images | string (name \| link \| thumbnail) |  | What goes under a photo the contact sent in that history. The photo's own line ([IMAGE, file name, type, size]) is always shown. name: nothing more. link: a line with the link to the full-size photo. thumbnail: a small picture linked to the full-size photo; it is loaded from that link, not attached to the email. A photo app2email has no copy of gets nothing more. The dashboard calls it Images in Chat History Summary. |
| caps | object |  |  |
|   monthly_messages | integer |  | Your own monthly cap on outgoing messages (WhatsApp + email). 0 = the plan limit only. |
| compliance | object |  |  |
|   adm_disclosure | string |  | Appended once to automated replies (auto reply, agents), eg 'This reply was generated automatically.' |
|   stop_keywords_extra | array of string |  | Your own opt-out words besides the built-in ones (STOP and its translations). |
| a2a | object |  |  |
|   respect_owner | boolean |  | Skip the A2A / OpenClaw agent when a conversation's owner is human or paused. |
| messages | object |  |  |
|   marketing_route | string (auto \| cloud_api \| mm_api) |  | Where MARKETING templates go: auto = the Marketing Messages API once WhatsApp says the account is onboarded, else the Cloud API; cloud_api; mm_api. |


Example answer:

```json
{
  "success": true,
  "request_id": "s1xpa",
  "settings": {
    "email": {
      "delivery_receipts": "failed_only",
      "mark_read_on_open": false,
      "include_history": 20,
      "history_images": "link"
    },
    "caps": {
      "monthly_messages": 0
    },
    "compliance": {
      "adm_disclosure": "",
      "stop_keywords_extra": []
    },
    "a2a": {
      "respect_owner": true
    }
  }
}
```


## Opt-ins


### `GET /settings/optin`

Is the opt-in rule for marketing on?. Scope: `settings:manage`. Docs: https://www.app2email.com/docs/api/opt-ins/get-optin-setting

Needs the 'settings:manage' scope.


Example answer:

```json
{
  "require_optin_for_marketing": true
}
```


### `PUT /settings/optin`

Turn the opt-in rule for marketing on or off. Scope: `settings:manage`. Docs: https://www.app2email.com/docs/api/opt-ins/set-optin-setting

When on, MARKETING template messages are only sent to numbers with an opt-in record. Others are skipped (recipient_not_opted_in; a single recipient gets 403). Utility templates and replies are not affected. Off by default.


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| require_optin_for_marketing | boolean | yes | true: marketing templates are only sent to numbers with an opt-in record (others: recipient_not_opted_in). Utility templates are not affected. Off by default. |


Example answer:

```json
{
  "require_optin_for_marketing": true
}
```


### `GET /optins`

The opt-in records, or check one number. Scope: `settings:manage`. Docs: https://www.app2email.com/docs/api/opt-ins/list-optins

Your own proof that people agreed to your messages (kept by app2email; nothing else uses it unless the opt-in rule is on). Needs the 'settings:manage' scope.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| number | query | string |  | Check only this number: opted_in true or false. |
| limit | query | integer |  | How many (1 to 200, default 100). |
| after | query | string |  | The next_after of the previous page. |


Example answer:

```json
{
  "success": true,
  "request_id": "o1lkr",
  "total": 2,
  "optins": [
    {
      "number": "61412345678",
      "name": "John",
      "source": "api",
      "note": "",
      "at": "2026-10-26T01:00:00Z",
      "added_by": "api"
    },
    {
      "number": "61498765432",
      "name": "Mary",
      "source": "web form",
      "note": "ticked the box",
      "at": "2026-10-01T00:00:00Z",
      "added_by": "api"
    }
  ],
  "next_after": null,
  "opted_in": null
}
```


### `POST /optins`

Record that people opted in. Scope: `settings:manage`. Docs: https://www.app2email.com/docs/api/opt-ins/add-optins

Up to 1000 entries, all or nothing. A number already recorded is updated. Needs the 'settings:manage' scope.


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| numbers | array of object | yes | Numbers as strings, or objects with number, name, source, note and at (ISO 8601, when they opted in; default now). |


Example answer:

```json
{
  "success": true,
  "request_id": "o9ahv",
  "saved": 2
}
```


### `DELETE /optins/{phone}`

Remove an opt-in record. Scope: `settings:manage`. Docs: https://www.app2email.com/docs/api/opt-ins/remove-optin

Needs the 'settings:manage' scope.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| phone | path | string | yes | The number, with country code. |


Example answer:

```json
{
  "success": true,
  "request_id": "r6dyw",
  "removed": "61412345678"
}
```


## Contacts


### `GET /contacts`

Your contacts, newest first. Scope: `messages:read`. Docs: https://www.app2email.com/docs/api/contacts/list-contacts

Filter by a search text, a tag, or consent. Page with `next_cursor`.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| q | query | string |  | Part of the name or number. |
| tag | query | string |  | Only contacts with this tag. |
| consent | query | boolean |  | true: with marketing consent. false: without. |
| limit | query | integer |  | How many (1 to 200, default 50). |
| cursor | query | string |  | The next_cursor of the previous answer, unchanged. Leave out for the first page. |


Example answer:

```json
{
  "success": true,
  "request_id": "l4vne",
  "contacts": [
    {
      "identity": "61412345678",
      "identity_type": "phone",
      "phone": "61412345678",
      "name": "John Smith",
      "tags": [
        "vip"
      ],
      "custom_fields": {
        "first_name": "John",
        "order_id": "1234"
      },
      "source": "crm",
      "consent": {
        "marketing": true,
        "at": "2026-10-01T09:00:00Z",
        "source": "web form",
        "text": "Yes, send me offers on WhatsApp",
        "evidence": "https://example.com/forms/123",
        "recorded": true
      },
      "last_inbound_at": "2026-10-26T01:20:44Z",
      "created": "2026-10-01T09:00:10Z",
      "updated": "2026-10-26T01:20:44Z"
    }
  ],
  "next_cursor": null,
  "count": 1,
  "total": 1
}
```


### `POST /contacts`

Make or update contacts (one, or a list of up to 1000). Scope: `contacts:manage`. Docs: https://www.app2email.com/docs/api/contacts/upsert-contacts

Needs the 'contacts:manage' scope. Upsert by identity (phone or business-scoped user id): the fields given replace, the ones left out stay. Custom fields merge. `consent` records consent with its evidence. Fires contact.updated for requests of up to 50 contacts.


Example answer:

```json
{
  "success": true,
  "request_id": "u8wqb",
  "saved": 1,
  "created": 1,
  "updated": 0,
  "contacts": [
    {
      "identity": "61412345678",
      "identity_type": "phone",
      "phone": "61412345678",
      "name": "John Smith",
      "tags": [
        "vip"
      ],
      "custom_fields": {
        "first_name": "John",
        "order_id": "1234"
      },
      "source": "crm",
      "consent": {
        "marketing": true,
        "at": "2026-10-01T09:00:00Z",
        "source": "web form",
        "text": "Yes, send me offers on WhatsApp",
        "evidence": "https://example.com/forms/123",
        "recorded": true
      },
      "last_inbound_at": "2026-10-26T01:20:44Z",
      "created": "2026-10-01T09:00:10Z",
      "updated": "2026-10-26T01:20:44Z"
    }
  ]
}
```


### `POST /contacts/import`

Import contacts from CSV or JSON (up to 5000 rows). Scope: `contacts:manage`. Docs: https://www.app2email.com/docs/api/contacts/import-contacts

Needs the 'contacts:manage' scope. `text/csv` with a header row: phone (or identity / number / mobile), name (or first_name + last_name), tags (separated by |), consent_marketing (yes/no), consent_source, consent_text, consent_evidence, consent_at, source; every other column becomes a custom field. Or `application/json` with a list of contacts as for POST /contacts. Rows with a problem are skipped and listed; the rest are saved.


Example answer:

```json
{
  "success": true,
  "request_id": "i2gka",
  "rows": 120,
  "saved": 118,
  "created": 90,
  "updated": 28,
  "skipped": 2,
  "errors": [
    {
      "row": 7,
      "problem": "'0412' must be a WhatsApp number with country code, digits only (8 to 15 digits), or a business-scoped user id like 61.AbC123"
    }
  ],
  "note": "Rows with a problem were skipped (the first 50 are listed); the rest were saved."
}
```


### `GET /contacts/export.csv`

All contacts as CSV. Scope: `messages:read`. Docs: https://www.app2email.com/docs/api/contacts/export-contacts

One row per contact with tags (separated by |), consent and custom fields (as JSON). Up to 50,000 rows.


### `GET /contacts/{identity}`

One contact. Scope: `messages:read`. Docs: https://www.app2email.com/docs/api/contacts/get-contact


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| identity | path | string | yes | The contact's number (country code first), or their business-scoped user id. |


### `PATCH /contacts/{identity}`

Change a contact. Scope: `contacts:manage`. Docs: https://www.app2email.com/docs/api/contacts/update-contact

Needs the 'contacts:manage' scope. The same fields as POST /contacts; only the ones given change.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| identity | path | string | yes | The contact's number (country code first), or their business-scoped user id. |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| phone | string |  |  |
| identity | string |  | Instead of phone: a number or a business-scoped user id. |
| name | string |  |  |
| tags | array of string |  | Up to 50. A comma separated string works too. |
| custom_fields | object |  | Up to 50 text values (names: letters, digits, underscores). Used as named template values in segment sends. |
| source | string |  |  |
| consent | object |  | Consent to marketing messages, with the evidence the Spam Act 2003 expects you to keep. |
|   marketing | boolean |  | true: consented. false: withdrawn (add them to the Do Not Call list too). |
|   at | string |  | When. Now when left out. |
|   source | string |  |  |
|   text | string |  | The wording the contact agreed to. |
|   evidence | string |  | A link, file name, IP address or message id that proves it. |


### `DELETE /contacts/{identity}`

Delete a contact record. Scope: `contacts:manage`. Docs: https://www.app2email.com/docs/api/contacts/delete-contact

Needs the 'contacts:manage' scope. The Do Not Call list and the opt-ins are separate records and stay. The contact's appointments (and notes, payments, packages) are kept: add `booking_data=erase` to erase or anonymise them too (future confirmed appointments are cancelled without a message, every appointment loses the customer's name, number, e-mail and notes, and their notes, links, holds and poll votes are deleted; the answer then carries `booking_data_erased` with the counts, and `booking.customer.erased` is sent). That cannot be undone. With `booking_data=erase` the contact's ticket data is erased too (orders and tickets lose the name, number, email and answers; old ticket links stop working); the answer then carries `ticket_data_erased` with the counts and `ticket.buyer.erased` is sent. It is refused, with the reason in `note`, while the contact holds a valid ticket for a coming date.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| identity | path | string | yes | The contact's number (country code first), or their business-scoped user id. |
| booking_data | query | string (erase) |  | erase: also erase the contact's booking data (appointments, notes, links, holds, poll votes, package and payment details). Left out: the appointments are kept. |


### `POST /contacts/{identity}/consent`

Record consent (or its withdrawal) with evidence. Scope: `contacts:manage`. Docs: https://www.app2email.com/docs/api/contacts/record-consent

Needs the 'contacts:manage' scope. Makes the contact when it is new. `marketing: false` records a withdrawal: add the contact to the Do Not Call list too. Fires contact.updated.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| identity | path | string | yes | The contact's number (country code first), or their business-scoped user id. |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| marketing | boolean |  | true: consented. false: withdrawn (add them to the Do Not Call list too). |
| at | string |  | When. Now when left out. |
| source | string |  |  |
| text | string |  | The wording the contact agreed to. |
| evidence | string |  | A link, file name, IP address or message id that proves it. |


### `GET /segments`

Your segments (saved contact filters). Scope: `messages:read`. Docs: https://www.app2email.com/docs/api/contacts/list-segments


Example answer:

```json
{
  "success": true,
  "request_id": "g5tnr",
  "segments": [
    {
      "id": 12,
      "name": "VIP, consented",
      "filter": {
        "tags_any": [
          "vip"
        ],
        "consent_marketing": true,
        "last_inbound_days": 90
      },
      "contacts": null,
      "created": "2026-11-02T01:00:00Z",
      "updated": "2026-11-02T01:00:00Z"
    }
  ],
  "count": 1
}
```


### `POST /segments`

Save a contact filter as a segment. Scope: `contacts:manage`. Docs: https://www.app2email.com/docs/api/contacts/create-segment

Needs the 'contacts:manage' scope. Up to 100 segments. Send to it with POST /messages `segment`.


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| name | string |  |  |
| filter | object |  | Which contacts a segment holds. Every condition given must hold. |
|   tags_any | array of string |  | At least one of these tags. |
|   tags_all | array of string |  | All of these tags. |
|   consent_marketing | boolean |  | true: only contacts with marketing consent. false: only without. |
|   last_inbound_days | integer |  | Wrote to the number in the last N days. |
|   search | string |  | Part of the name or number. |


### `GET /segments/{id}`

One segment, with how many contacts match now. Scope: `messages:read`. Docs: https://www.app2email.com/docs/api/contacts/get-segment


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The segment's id, or its exact name. |


### `PUT /segments/{id}`

Rename a segment or replace its filter. Scope: `contacts:manage`. Docs: https://www.app2email.com/docs/api/contacts/update-segment

Needs the 'contacts:manage' scope. A `filter` given replaces the whole filter.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The segment's id, or its exact name. |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| name | string |  |  |
| filter | object |  | Which contacts a segment holds. Every condition given must hold. |
|   tags_any | array of string |  | At least one of these tags. |
|   tags_all | array of string |  | All of these tags. |
|   consent_marketing | boolean |  | true: only contacts with marketing consent. false: only without. |
|   last_inbound_days | integer |  | Wrote to the number in the last N days. |
|   search | string |  | Part of the name or number. |


### `DELETE /segments/{id}`

Delete a segment (its contacts stay). Scope: `contacts:manage`. Docs: https://www.app2email.com/docs/api/contacts/delete-segment

Needs the 'contacts:manage' scope.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The segment's id, or its exact name. |


### `GET /segments/{id}/contacts`

The contacts a segment matches now. Scope: `messages:read`. Docs: https://www.app2email.com/docs/api/contacts/list-segment-contacts


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The segment's id, or its exact name. |
| limit | query | integer |  | How many (1 to 200, default 50). |
| cursor | query | string |  | The next_cursor of the previous answer, unchanged. Leave out for the first page. |


### `GET /blocked`

WhatsApp users this number blocked. Scope: `messages:read`. Docs: https://www.app2email.com/docs/api/contacts/list-blocked-users

WhatsApp's own block list of the number (not the Do Not Call list). Page with `next_cursor`.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| limit | query | integer |  | How many (1 to 200, default 50). |
| cursor | query | string |  | The next_cursor of the previous answer, unchanged. Leave out for the first page. |


Example answer:

```json
{
  "success": true,
  "request_id": "l3blk",
  "blocked": [
    {
      "wa_id": "61412345678"
    },
    {
      "wa_id": "61498765432"
    }
  ],
  "count": 2,
  "next_cursor": "QVFIUkpVTXl4dE9Ed1"
}
```


### `POST /blocked`

Block WhatsApp users. Scope: `contacts:manage`. Docs: https://www.app2email.com/docs/api/contacts/block-users

They cannot message the number and it cannot message them. Up to 1000 per call; only users who wrote in the last 24 hours.


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| users | array of string | yes | Phone numbers (country code, digits) or business-scoped user ids. Meta's own block_users list works too. |


Example answer:

```json
{
  "success": true,
  "request_id": "b1lkp",
  "blocked": [
    {
      "input": "+61412345678",
      "wa_id": "61412345678"
    }
  ]
}
```


### `DELETE /blocked`

Unblock WhatsApp users. Scope: `contacts:manage`. Docs: https://www.app2email.com/docs/api/contacts/unblock-users

Same body as blocking.


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| users | array of string | yes | Phone numbers (country code, digits) or business-scoped user ids. Meta's own block_users list works too. |


Example answer:

```json
{
  "success": true,
  "request_id": "u2lkr",
  "unblocked": [
    {
      "input": "+61412345678",
      "wa_id": "61412345678"
    }
  ]
}
```


### `GET /contact-book/{bsuid}`

Is a phone number on file for a business-scoped user id. Scope: `messages:read`. Docs: https://www.app2email.com/docs/api/contacts/get-contact-book-entry

WhatsApp's contact book (per business portfolio) keeps the numbers of users the business talked to, so webhooks include them. Never returns the number.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| bsuid | path | string | yes | The business-scoped user id (from_user_id of a message.received event), eg US.13491208655302741918. Parent ids (.ENT.) are refused. |


Example answer:

```json
{
  "success": true,
  "request_id": "c4bok",
  "bsuid": "US.13491208655302741918",
  "present": true
}
```


### `DELETE /contact-book/{bsuid}`

Remove a business-scoped user id from the contact book. Scope: `contacts:manage`. Docs: https://www.app2email.com/docs/api/contacts/delete-contact-book-entry

Later webhooks may then leave the number out (unless the user writes again).


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| bsuid | path | string | yes | The business-scoped user id (from_user_id of a message.received event), eg US.13491208655302741918. Parent ids (.ENT.) are refused. |


Example answer:

```json
{
  "success": true,
  "request_id": "c5bod",
  "bsuid": "US.13491208655302741918",
  "deleted": true
}
```


## Approvals


### `GET /approvals`

Sends held for approval. Scope: `messages:read`. Docs: https://www.app2email.com/docs/api/approvals/list-approvals

Sends held by a key's approval gate (approval_above on the API key page): pending ones by default, `status=all` for the resolved and expired ones of the last 7 days too.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| status | query | string (pending \| all) |  | pending (default) or all. |


Example answer:

```json
{
  "success": true,
  "request_id": "a4lxc",
  "approvals": [
    {
      "id": "apr_a1b2c3d4e5f6g7h8",
      "status": "pending",
      "created": "2026-11-02T01:12:09Z",
      "expires": "2026-11-04T01:12:09Z",
      "key": "Agent",
      "request_id": "p3kdm",
      "recipients": 250,
      "summary": {
        "recipients": 250,
        "to_send": 248,
        "template": {
          "name": "november_offer",
          "language": "en",
          "category": "MARKETING"
        },
        "text": "Hi {{first_name}}, ..."
      },
      "url": "https://www.app2email.com/dashboard/approvals?id=apr_a1b2c3d4e5f6g7h8",
      "approve_url": "https://api.app2email.com/v1/4976659348270/approvals/apr_a1b2c3d4e5f6g7h8/approve"
    }
  ],
  "count": 1
}
```


### `POST /approvals/{id}/approve`

Approve a held send: it is sent now. Scope: `messages:send`. Docs: https://www.app2email.com/docs/api/approvals/approve-send

Needs the 'messages:send' scope, from a key that is not a sandbox key. The stored request is run as a normal send (the Do Not Call list, the limits and the daily cap are checked again); `send` in the answer is the answer the original request would have got. Fires approval.resolved. A held send expires 48 hours after it was held.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The approval's id. |


Example answer:

```json
{
  "success": true,
  "request_id": "a5mzd",
  "approval": {
    "id": "apr_a1b2c3d4e5f6g7h8",
    "status": "approved",
    "resolved_by": "api:Manager",
    "resolved_at": "2026-11-02T02:00:00Z",
    "result": {
      "http_status": 200,
      "status": "accepted",
      "accepted": 248,
      "failed": 0,
      "broadcast_code": "k3XbQ9rTzP2mWv7a1c9e"
    }
  },
  "send": {
    "success": true,
    "status": "accepted",
    "recipients": 250,
    "accepted": 248,
    "failed": 2
  },
  "note": "Approved and sent: 'send' is the answer the original request would have got."
}
```


### `POST /approvals/{id}/reject`

Reject a held send: nothing is sent. Scope: `messages:send`. Docs: https://www.app2email.com/docs/api/approvals/reject-send

Needs the 'messages:send' scope. Fires approval.resolved.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The approval's id. |


## Webhooks


### `GET /webhooks`

Your webhooks. Scope: `webhooks:manage`. Docs: https://www.app2email.com/docs/api/webhooks/list-webhooks

With the result of the last delivery to each.


Example answer:

```json
{
  "success": true,
  "request_id": "w3bls",
  "events_available": [
    "message.status",
    "message.received",
    "message.failed",
    "contact.opted_out",
    "broadcast.completed",
    "usage.threshold",
    "template.status_changed",
    "conversation.owner_changed",
    "message.held_for_approval",
    "approval.resolved",
    "contact.updated",
    "waitlist.joined",
    "waitlist.notified",
    "waitlist.removed",
    "booking.created",
    "booking.cancelled",
    "booking.rescheduled",
    "booking.rated",
    "flow.completed",
    "booking.updated",
    "booking.note.created",
    "calendar.block.created",
    "calendar.block.deleted",
    "call.incoming",
    "call.status",
    "message.edited",
    "message.deleted",
    "contact.changed_number",
    "number.updated",
    "number.error",
    "flow.status_changed",
    "booking.paid",
    "booking.refunded",
    "payment.paid",
    "package.purchased",
    "poll.voted",
    "poll.closed",
    "booking.customer.erased",
    "order.created",
    "order.paid",
    "order.accepted",
    "order.ready",
    "order.completed",
    "order.cancelled",
    "order.refunded",
    "order.no_show",
    "submission.created",
    "submission.files_ready",
    "submission.updated",
    "submission.status_changed",
    "submission.assigned",
    "submission.note_added",
    "submission.customer_replied",
    "submission.deleted",
    "submit.automation_failed",
    "ticket.order.confirmed",
    "ticket.order.refunded",
    "ticket.checked_in",
    "ticket.passed_on",
    "ticket.event.sold_out",
    "ticket.event.cancelled",
    "ticket.waitlist.joined",
    "ticket.buyer.erased"
  ],
  "webhooks": [
    {
      "id": "wh_a1b2c3d4e5f6g7h8",
      "url": "https://hooks.example.com/app2email",
      "events": [
        "message.status",
        "message.received",
        "message.failed",
        "contact.opted_out",
        "broadcast.completed",
        "usage.threshold",
        "template.status_changed",
        "conversation.owner_changed",
        "message.held_for_approval",
        "approval.resolved",
        "contact.updated",
        "waitlist.joined",
        "waitlist.notified",
        "waitlist.removed",
        "booking.created",
        "booking.cancelled",
        "booking.rescheduled",
        "booking.rated",
        "flow.completed",
        "booking.updated",
        "booking.note.created",
        "calendar.block.created",
        "calendar.block.deleted",
        "call.incoming",
        "call.status",
        "message.edited",
        "message.deleted",
        "contact.changed_number",
        "number.updated",
        "number.error",
        "flow.status_changed",
        "booking.paid",
        "booking.refunded",
        "payment.paid",
        "package.purchased",
        "poll.voted",
        "poll.closed",
        "booking.customer.erased",
        "order.created",
        "order.paid",
        "order.accepted",
        "order.ready",
        "order.completed",
        "order.cancelled",
        "order.refunded",
        "order.no_show",
        "submission.created",
        "submission.files_ready",
        "submission.updated",
        "submission.status_changed",
        "submission.assigned",
        "submission.note_added",
        "submission.customer_replied",
        "submission.deleted",
        "submit.automation_failed",
        "ticket.order.confirmed",
        "ticket.order.refunded",
        "ticket.checked_in",
        "ticket.passed_on",
        "ticket.event.sold_out",
        "ticket.event.cancelled",
        "ticket.waitlist.joined",
        "ticket.buyer.erased"
      ],
      "secret": "whsec_3Fq9LmZ2xT8pW1rK7vB4nD6sH0jC5yA9",
      "created": "2026-11-01T09:30:00.000Z",
      "active": true,
      "format": "app2email",
      "headers": {
        "Authorization": "****YXNz"
      },
      "last_delivery": {
        "at": "2026-11-06T01:00:03.300Z",
        "ok": true,
        "result": "HTTP 200 in 184 ms"
      }
    }
  ]
}
```


### `POST /webhooks`

Get events at your URL. Scope: `webhooks:manage`. Docs: https://www.app2email.com/docs/api/webhooks/create-webhook

Up to 5 per number. Every webhook gets every event: use the event's type to pick the ones you handle. The same URL again answers that webhook, turned on (200). The answer has the secret that signs every event. Optional: headers (custom headers) and format (app2email or meta).


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| url | string | yes | Public https address that accepts POST. No redirects. |
| events | array of string |  | Not used: every webhook gets every event. Accepted (and ignored) so older clients keep working. |
| headers | object |  | Up to 5 custom headers sent with every event, eg {"Authorization": "Basic dXNlcjpwYXNz"}. Values: printable ASCII, one line. Not allowed: Host, User-Agent, Content-*, X-App2email-*, X-Hub-*, Proxy-*, X-Forwarded-* and connection headers. Answers (also a test's sent_headers) show each value as its last 4 characters. |
| format | string (app2email \| meta) |  | The body format, not an event choice: every webhook still gets every event. meta: what comes from WhatsApp is sent as Meta's own webhook body ({object, entry[].changes[]}, as Meta sent it; X-App2email-Event: meta.<field>), one POST per change, instead of its events (message.*, contact.opted_out, contact.changed_number, number.*, template.status_changed, WhatsApp's handovers and marketing_resumed). app2email's own events (broadcast.completed, usage.threshold, approvals, contact changes made in app2email ...) keep the envelope. Signed the same way. |


### `GET /webhooks/samples`

A sample of every event. Scope: `webhooks:manage`. Docs: https://www.app2email.com/docs/api/webhooks/webhook-samples

Each event type (and ping) as a test of that type sends it: the real fields, with made-up values and "test": true. Needs the 'webhooks:manage' scope.


Example answer:

```json
{
  "success": true,
  "request_id": "w3bsm",
  "samples": {
    "ping": {
      "id": "evt_Xq3k9m2Lw8Rt5Yp1Zs01",
      "type": "ping",
      "created": "2026-11-06T01:00:00.000Z",
      "number": "4976659348270",
      "test": true,
      "data": {
        "webhook_id": "wh_a1b2c3d4e5f6g7h8",
        "message": "Test event. If you can see this, your webhook works."
      }
    },
    "message.received": {
      "id": "evt_Xq3k9m2Lw8Rt5Yp1Zs01",
      "type": "message.received",
      "created": "2026-11-06T01:00:00.000Z",
      "number": "4976659348270",
      "data": {
        "message_id": "wamid.HBgLNjE0MTIzNDU2NzgVAgARGBJTQU1QTEVfVEVTVF9FVkVOVAA=",
        "from": "61412345678",
        "name": "Sample Contact",
        "type": "text",
        "text": "Hi, is my order on its way?",
        "conversation_url": "https://www.app2email.com/conversation/61412345678_4976659348270_SAMPLEk3XbQ9rTzP2mW",
        "timestamp": "2026-11-06T01:00:00.000Z",
        "from_user_id": "AU.1234567890123456",
        "whatsapp": {
          "from": "61412345678",
          "from_user_id": "AU.1234567890123456",
          "id": "wamid.HBgLNjE0MTIzNDU2NzgVAgARGBJTQU1QTEVfVEVTVF9FVkVOVAA=",
          "timestamp": "1762390800",
          "type": "text",
          "text": {
            "body": "Hi, is my order on its way?"
          }
        }
      },
      "test": true
    },
    "message.status": {
      "id": "evt_Xq3k9m2Lw8Rt5Yp1Zs01",
      "type": "message.status",
      "created": "2026-11-06T01:00:00.000Z",
      "number": "4976659348270",
      "data": {
        "message_id": "wamid.HBgLNjE0MTIzNDU2NzgVAgARGBJTQU1QTEVfVEVTVF9FVkVOVAA=",
        "to": "61412345678",
        "status": "delivered",
        "timestamp": "2026-11-06T01:00:00.000Z",
        "sent_by": "api",
        "whatsapp_status": "delivered",
        "recipient_user_id": "AU.1234567890123456",
        "pricing": {
          "billable": true,
          "pricing_model": "PMP",
          "type": "regular",
          "category": "utility"
        },
        "callback_data": "order-1234"
      },
      "test": true
    }
  },
  "meta_samples": {
    "message.received": {
      "object": "whatsapp_business_account",
      "entry": [
        {
          "id": "102290129340398",
          "changes": [
            {
              "field": "messages",
              "value": {
                "messaging_product": "whatsapp",
                "metadata": {
                  "display_phone_number": "4976659348270",
                  "phone_number_id": "106540352242922"
                },
                "contacts": [
                  {
                    "profile": {
                      "name": "Sample Contact"
                    },
                    "wa_id": "61412345678",
                    "user_id": "AU.1234567890123456"
                  }
                ],
                "messages": [
                  {
                    "from": "61412345678",
                    "from_user_id": "AU.1234567890123456",
                    "id": "wamid.HBgLNjE0MTIzNDU2NzgVAgARGBJTQU1QTEVfVEVTVF9FVkVOVAA=",
                    "timestamp": "1762390800",
                    "type": "text",
                    "text": {
                      "body": "Hi, is my order on its way?"
                    }
                  }
                ]
              }
            }
          ]
        }
      ]
    }
  },
  "note": "What a test of each type sends (POST .../webhooks/{id}/test with {\"type\": \"...\"}). Real events have the same fields, with real values and without \"test\". meta_samples: what a webhook with \"format\": \"meta\" gets instead, for the events that come from WhatsApp."
}
```


### `PATCH /webhooks/{id}`

Change a webhook: url, active, headers, format. Scope: `webhooks:manage`. Docs: https://www.app2email.com/docs/api/webhooks/update-webhook

Only what is given changes: url, active, headers (a header set to null is removed), format. `active: true` turns a webhook back on after it was switched off for failures (and clears the failure count). The same url as another webhook of the number: 409 webhook_url_in_use. Needs the 'webhooks:manage' scope.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The webhook's id. |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| url | string |  | Public https address that accepts POST. No redirects. |
| events | array of string |  | Not used: every webhook gets every event. A PATCH with only events answers 200 with the webhook unchanged. |
| active | boolean |  | true: turn the webhook on again (after it was switched off for failures). false: turn it off. |
| headers | object |  | Up to 5 custom headers sent with every event, eg {"Authorization": "Basic dXNlcjpwYXNz"}. Values: printable ASCII, one line. Not allowed: Host, User-Agent, Content-*, X-App2email-*, X-Hub-*, Proxy-*, X-Forwarded-* and connection headers. Answers (also a test's sent_headers) show each value as its last 4 characters. A header set to null is removed; "headers": null removes them all. |
| format | string (app2email \| meta) |  | The body format, not an event choice: every webhook still gets every event. meta: what comes from WhatsApp is sent as Meta's own webhook body ({object, entry[].changes[]}, as Meta sent it; X-App2email-Event: meta.<field>), one POST per change, instead of its events (message.*, contact.opted_out, contact.changed_number, number.*, template.status_changed, WhatsApp's handovers and marketing_resumed). app2email's own events (broadcast.completed, usage.threshold, approvals, contact changes made in app2email ...) keep the envelope. Signed the same way. |


Example answer:

```json
{
  "success": true,
  "request_id": "v3gkx",
  "webhook": {
    "id": "wh_a1b2c3d4e5f6g7h8",
    "url": "https://hooks.example.com/app2email",
    "events": [
      "message.status",
      "message.received",
      "message.failed",
      "contact.opted_out",
      "broadcast.completed",
      "usage.threshold",
      "template.status_changed",
      "conversation.owner_changed",
      "message.held_for_approval",
      "approval.resolved",
      "contact.updated",
      "waitlist.joined",
      "waitlist.notified",
      "waitlist.removed",
      "booking.created",
      "booking.cancelled",
      "booking.rescheduled",
      "booking.rated",
      "flow.completed",
      "booking.updated",
      "booking.note.created",
      "calendar.block.created",
      "calendar.block.deleted",
      "call.incoming",
      "call.status",
      "message.edited",
      "message.deleted",
      "contact.changed_number",
      "number.updated",
      "number.error",
      "flow.status_changed",
      "booking.paid",
      "booking.refunded",
      "payment.paid",
      "package.purchased",
      "poll.voted",
      "poll.closed",
      "booking.customer.erased",
      "order.created",
      "order.paid",
      "order.accepted",
      "order.ready",
      "order.completed",
      "order.cancelled",
      "order.refunded",
      "order.no_show",
      "submission.created",
      "submission.files_ready",
      "submission.updated",
      "submission.status_changed",
      "submission.assigned",
      "submission.note_added",
      "submission.customer_replied",
      "submission.deleted",
      "submit.automation_failed",
      "ticket.order.confirmed",
      "ticket.order.refunded",
      "ticket.checked_in",
      "ticket.passed_on",
      "ticket.event.sold_out",
      "ticket.event.cancelled",
      "ticket.waitlist.joined",
      "ticket.buyer.erased"
    ],
    "secret": "whsec_...",
    "created": "2026-10-20T04:00:00Z",
    "active": true,
    "disabled_reason": null,
    "last_delivery": {
      "at": "2026-10-26T01:12:11Z",
      "ok": true,
      "result": "200"
    }
  }
}
```


### `DELETE /webhooks/{id}`

Delete a webhook. Scope: `webhooks:manage`. Docs: https://www.app2email.com/docs/api/webhooks/delete-webhook

Stops every delivery to it, planned retries included. Its delivery log is kept 7 days.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The webhook's id. |


Example answer:

```json
{
  "success": true,
  "request_id": "w3bdl",
  "deleted": "wh_a1b2c3d4e5f6g7h8"
}
```


### `POST /webhooks/{id}/test`

Send a test event now. Scope: `webhooks:manage`. Docs: https://www.app2email.com/docs/api/webhooks/test-webhook

Sends a test event to the webhook's URL straight away (once, no retries, not in the delivery log) and answers how the URL responded. No body: a 'ping'. {"type": "message.received"}: that event's sample. {"event": {...}}: your own event. Test events carry "test": true and the header X-App2email-Test: true, and are signed like every event. Up to 30 tests an hour per number (429 too_many_tests). A webhook with format meta gets the event as Meta's own body.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The webhook's id. |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| type | string (ping \| message.status \| message.received \| message.failed \| contact.opted_out \| broadcast.completed \| usage.threshold \| template.status_changed \| conversation.owner_changed \| message.held_for_approval \| approval.resolved \| contact.updated \| waitlist.joined \| waitlist.notified \| waitlist.removed \| booking.created \| booking.cancelled \| booking.rescheduled \| booking.rated \| flow.completed \| booking.updated \| booking.note.created \| calendar.block.created \| calendar.block.deleted \| call.incoming \| call.status \| message.edited \| message.deleted \| contact.changed_number \| number.updated \| number.error \| flow.status_changed \| booking.paid \| booking.refunded \| payment.paid \| package.purchased \| poll.voted \| poll.closed \| booking.customer.erased \| order.created \| order.paid \| order.accepted \| order.ready \| order.completed \| order.cancelled \| order.refunded \| order.no_show \| submission.created \| submission.files_ready \| submission.updated \| submission.status_changed \| submission.assigned \| submission.note_added \| submission.customer_replied \| submission.deleted \| submit.automation_failed \| ticket.order.confirmed \| ticket.order.refunded \| ticket.checked_in \| ticket.passed_on \| ticket.event.sold_out \| ticket.event.cancelled \| ticket.waitlist.joined \| ticket.buyer.erased) |  |  |
| event | object |  | What app2email POSTs to your webhook URL. Headers: X-App2email-Event (the type), X-App2email-Delivery (the id), X-App2email-Signature: t=<unix seconds>,v1=<hex HMAC-SHA256 of "<t>.<raw body>" with the webhook's secret> (a second v1= while an old secret is kept), X-Hub-Signature-256: sha256=<hex HMAC-SHA256 of the raw body with the webhook's secret> (as Meta signs WhatsApp webhooks), and on test events X-App2email-Test: true. |
|   id | string |  |  |
|   type | string (message.status \| message.received \| message.failed \| contact.opted_out \| broadcast.completed \| usage.threshold \| template.status_changed \| conversation.owner_changed \| message.held_for_approval \| approval.resolved \| contact.updated \| waitlist.joined \| waitlist.notified \| waitlist.removed \| booking.created \| booking.cancelled \| booking.rescheduled \| booking.rated \| flow.completed \| booking.updated \| booking.note.created \| calendar.block.created \| calendar.block.deleted \| call.incoming \| call.status \| message.edited \| message.deleted \| contact.changed_number \| number.updated \| number.error \| flow.status_changed \| booking.paid \| booking.refunded \| payment.paid \| package.purchased \| poll.voted \| poll.closed \| booking.customer.erased \| order.created \| order.paid \| order.accepted \| order.ready \| order.completed \| order.cancelled \| order.refunded \| order.no_show \| submission.created \| submission.files_ready \| submission.updated \| submission.status_changed \| submission.assigned \| submission.note_added \| submission.customer_replied \| submission.deleted \| submit.automation_failed \| ticket.order.confirmed \| ticket.order.refunded \| ticket.checked_in \| ticket.passed_on \| ticket.event.sold_out \| ticket.event.cancelled \| ticket.waitlist.joined \| ticket.buyer.erased \| ping) |  |  |
|   created | string |  |  |
|   number | string |  | Your WhatsApp number. |
|   test | boolean |  | Only on test events (POST .../test): true. |
|   data | object |  | message.status: {message_id, to, status (sent\|delivered\|read\|played\|clicked\|failed\|deleted), timestamp, error {code, message, title, details, error_code, how_to_fix, is_retriable, retry_after_seconds}, sent_by, broadcast_code, whatsapp_status, pricing, callback_data, recipient_user_id, recipient_identity_key_hash, whatsapp}. message.failed: the same data as message.status with status failed. message.received: {message_id, from, from_user_id, media_url, name, type, text, button {text, payload}, in_reply_to, conversation_url, timestamp, context, referral, location, contacts, reaction, interactive, flow, order, identity_key_hash, whatsapp (Meta's message object)}. contact.opted_out: {number, name, source (stop_promotions\|whatsapp_stop), detail, timestamp}. broadcast.completed: {code, name, status (completed\|cancelled\|missed), sent_by, numbers, posted, accepted, errors, skipped_do_not_call, skipped_monthly_limit, status_url, report_url}. usage.threshold: {threshold_percent (80\|100), whatsapp_messages {used, limit, left}, plan_messages {whatsapp_sent, emails_sent, total_sent, limit, left}, plan, billing_period {start, end}, timestamp}. template.status_changed: {template {name, language, id}, status (APPROVED\|PENDING\|REJECTED\|PAUSED\|DISABLED\|COMPONENTS_UPDATED ...), change (a Meta field, or components: the template was edited), previous_value, new_value, components, reason, can_send, timestamp}. conversation.owner_changed: {contact, owner, previous_owner, reason, summary, until, set_by, timestamp}. message.held_for_approval: {approval_id, url, approve_url, recipients, key, summary, expires, timestamp}. approval.resolved: {approval_id, status (approved\|rejected\|expired), resolved_by, result {status, accepted, failed, broadcast_code}, timestamp}. contact.updated: {contact (a Contact), change (upsert\|patch\|consent\|marketing_resumed), timestamp}. booking.created / booking.cancelled / booking.rescheduled / booking.rated: the Booking object (id, reference, status, contact, contact_name, service {id, name, duration_min}, start, end, timezone, source, calendar {provider, event_id, url, error}, answers, notes, provider {id, name}, rating, payment_status, credits_used, attendance_confirmed, cancelled {at, by, reason}, rescheduled_from_id, link_id, created) plus timestamp; booking.created also hold (true when made from a held time); booking.rescheduled also rescheduled_from {id, reference, start, end}; booking.rated also rated_at. flow.completed: {flow_key, flow_name, contact, contact_name, session_id, answers {field: text}, timestamp}. booking.updated: the Booking object plus changed [name \| email \| notes \| answers \| provider] and updated_by. booking.note.created: the Note {id, contact, appointment_id, booking_reference, body, author, author_kind, pinned, created, updated} plus booking {id, reference} (null when on the customer alone). calendar.block.created / calendar.block.deleted: the Block {id, provider_id, title, notes, start, end, start_local, end_local, source, created_by, created, updated} plus by. booking.paid / booking.refunded: the Booking object plus payment {the Payment}; booking.refunded also refund {amount, amount_label, full, by}. payment.paid: {payment, timestamp}. package.purchased: {purchase, payment, granted, timestamp}. poll.voted: {poll_id, title, name, contact, email, choices, comment}. poll.closed: {poll_id, title, status closed \| booked, chosen_option, appointment_id, by}. booking.customer.erased: {contact, counts}. submission.created / submission.files_ready / submission.updated / submission.status_changed / submission.assigned / submission.note_added / submission.customer_replied / submission.deleted: the Submission object (id, reference, form {key, name}, channel, status, status_name, status_kind, status_color, priority, tags, due, assignee {id, name}, contact {identity, name, phone, email, verified}, conversation_id, answers {field: value}, extra, location, parent, summary, files_count, files_pending, unread, link, created, updated, status_changed, closed, files, buttons); submission.updated, submission.status_changed and submission.assigned also change {status {from, to}, assignee {from, to}, answers, priority, tags, due, location, files {added}, verified, note, by}; submission.note_added also note and by; submission.customer_replied also reply {text, files, button, followup}; submission.deleted also erased (an erased submission keeps only id, reference, form, channel, status, status_kind, created). submit.automation_failed: the Submission object (without files and buttons) plus automation {id, name}, step, error. waitlist.joined: {id, reference, status, service_id, service_name, provider_id, provider_name, date, date_label, slot_id, time_label, contact, contact_name, contact_email, seats, source, notified_count, notified_at, appointment_id, note, created, updated, day, slot_local, contact_masked, created_at, by, timestamp}. waitlist.notified: {id, reference, status, service_id, service_name, provider_id, provider_name, date, date_label, slot_id, time_label, contact, contact_name, contact_email, seats, source, notified_count, notified_at, appointment_id, note, created, updated, day, slot_local, contact_masked, created_at, offer, timestamp}. waitlist.removed: {id, reference, status, service_id, service_name, provider_id, provider_name, date, date_label, slot_id, time_label, contact, contact_name, contact_email, seats, source, notified_count, notified_at, appointment_id, note, created, updated, day, slot_local, contact_masked, created_at, by, timestamp}. call.incoming: {call_id, status, direction, event, from, from_user_id, to, to_user_id, contact, session, start_time, end_time, duration_seconds, biz_opaque_callback_data, error, recording, transcription, timestamp, whatsapp}. call.status: {call_id, status, direction, event, from, from_user_id, to, to_user_id, contact, session, start_time, end_time, duration_seconds, biz_opaque_callback_data, error, recording, transcription, timestamp, whatsapp}. message.edited: {message_id, original_message_id, from, from_user_id, name, type, text, message, conversation_url, timestamp, whatsapp}. message.deleted: {message_id, original_message_id, from, from_user_id, name, conversation_url, timestamp, whatsapp}. contact.changed_number: {change, previous, new, name, body, message_id, conversation_url, timestamp, whatsapp}. number.updated: {change, previous_value, new_value, details, next_step, whatsapp_field, timestamp}. number.error: {code, title, message, details, href, error_code, how_to_fix, is_retriable, retry_after_seconds, timestamp}. flow.status_changed: {flow_id, change, event, old_status, new_status, message, warning, alert_state, threshold, error_rate, p50_latency, p90_latency, availability, requests_count, errors, timestamp}. order.created: {reference, status, source, fulfilment, asap, due, customer, items, items_count, currency, subtotal, discount, discount_code, delivery_fee, fees, tip, tax, total, total_label, refunded, payment, delivery, note, allergy_note, pickup_code, created, timestamp}. order.paid: {reference, status, source, fulfilment, asap, due, customer, items, items_count, currency, subtotal, discount, discount_code, delivery_fee, fees, tip, tax, total, total_label, refunded, payment, delivery, note, allergy_note, pickup_code, created, timestamp}. order.accepted: {reference, status, source, fulfilment, asap, due, customer, items, items_count, currency, subtotal, discount, discount_code, delivery_fee, fees, tip, tax, total, total_label, refunded, payment, delivery, note, allergy_note, pickup_code, created, timestamp}. order.ready: {reference, status, source, fulfilment, asap, due, customer, items, items_count, currency, subtotal, discount, discount_code, delivery_fee, fees, tip, tax, total, total_label, refunded, payment, delivery, note, allergy_note, pickup_code, created, timestamp}. order.completed: {reference, status, source, fulfilment, asap, due, customer, items, items_count, currency, subtotal, discount, discount_code, delivery_fee, fees, tip, tax, total, total_label, refunded, payment, delivery, note, allergy_note, pickup_code, created, timestamp, handover}. order.cancelled: {reference, status, source, fulfilment, asap, due, customer, items, items_count, currency, subtotal, discount, discount_code, delivery_fee, fees, tip, tax, total, total_label, refunded, payment, delivery, note, allergy_note, pickup_code, created, timestamp, cancelled}. order.refunded: {reference, status, source, fulfilment, asap, due, customer, items, items_count, currency, subtotal, discount, discount_code, delivery_fee, fees, tip, tax, total, total_label, refunded, payment, delivery, note, allergy_note, pickup_code, created, timestamp, refund}. order.no_show: {reference, status, source, fulfilment, asap, due, customer, items, items_count, currency, subtotal, discount, discount_code, delivery_fee, fees, tip, tax, total, total_label, refunded, payment, delivery, note, allergy_note, pickup_code, created, timestamp, no_show}. ticket.order.confirmed: {order, timestamp}. ticket.order.refunded: {order, refund, timestamp}. ticket.checked_in: {ticket, order, check_in, timestamp}. ticket.passed_on: {ticket, previous_ticket_id, order, timestamp}. ticket.event.sold_out: {event, date, sold, timestamp}. ticket.event.cancelled: {event, date, scope, refund, reason, orders, tickets, refunded, refunded_label, refunds_failed, timestamp}. ticket.waitlist.joined: {entry, event, timestamp}. ticket.buyer.erased: {contact, counts, timestamp}. ping: {webhook_id, message}. |


### `POST /webhooks/{id}/rotate-secret`

Make a new signing secret. Scope: `webhooks:manage`. Docs: https://www.app2email.com/docs/api/webhooks/rotate-webhook-secret

Events are signed with the new secret from then on; the old one stops working at once, unless keep_old_for_hours (1 to 24) is given: the old secret then also signs (a second v1= in X-App2email-Signature) until previous_secret_until. Needs the 'webhooks:manage' scope.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The webhook's id. |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| keep_old_for_hours | integer |  | The old secret keeps signing too (a second v1= in X-App2email-Signature) for this many hours. |


Example answer:

```json
{
  "success": true,
  "request_id": "v3gkx",
  "webhook": {
    "id": "wh_a1b2c3d4e5f6g7h8",
    "url": "https://hooks.example.com/app2email",
    "events": [
      "message.status",
      "message.received",
      "message.failed",
      "contact.opted_out",
      "broadcast.completed",
      "usage.threshold",
      "template.status_changed",
      "conversation.owner_changed",
      "message.held_for_approval",
      "approval.resolved",
      "contact.updated",
      "waitlist.joined",
      "waitlist.notified",
      "waitlist.removed",
      "booking.created",
      "booking.cancelled",
      "booking.rescheduled",
      "booking.rated",
      "flow.completed",
      "booking.updated",
      "booking.note.created",
      "calendar.block.created",
      "calendar.block.deleted",
      "call.incoming",
      "call.status",
      "message.edited",
      "message.deleted",
      "contact.changed_number",
      "number.updated",
      "number.error",
      "flow.status_changed",
      "booking.paid",
      "booking.refunded",
      "payment.paid",
      "package.purchased",
      "poll.voted",
      "poll.closed",
      "booking.customer.erased",
      "order.created",
      "order.paid",
      "order.accepted",
      "order.ready",
      "order.completed",
      "order.cancelled",
      "order.refunded",
      "order.no_show",
      "submission.created",
      "submission.files_ready",
      "submission.updated",
      "submission.status_changed",
      "submission.assigned",
      "submission.note_added",
      "submission.customer_replied",
      "submission.deleted",
      "submit.automation_failed",
      "ticket.order.confirmed",
      "ticket.order.refunded",
      "ticket.checked_in",
      "ticket.passed_on",
      "ticket.event.sold_out",
      "ticket.event.cancelled",
      "ticket.waitlist.joined",
      "ticket.buyer.erased"
    ],
    "secret": "whsec_...",
    "created": "2026-10-20T04:00:00Z",
    "active": true,
    "disabled_reason": null,
    "last_delivery": {
      "at": "2026-10-26T01:12:11Z",
      "ok": true,
      "result": "200"
    }
  }
}
```


### `GET /webhooks/{id}/deliveries`

The last deliveries, with every attempt. Scope: `webhooks:manage`. Docs: https://www.app2email.com/docs/api/webhooks/list-webhook-deliveries

The events sent to this webhook in the last 7 days (the latest 100), newest first, each with its attempts. Use it to find what failed.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The webhook's id. |
| limit | query | integer |  | How many (1 to 100, default 50). |
| status | query | string (failed \| delivered) |  | failed: never delivered. delivered: delivered. |


Example answer:

```json
{
  "success": true,
  "request_id": "p0fsa",
  "deliveries": [
    {
      "event_id": "evt_Xq3k9m2",
      "type": "message.status",
      "created": "2026-10-26T01:12:11Z",
      "delivered": false,
      "attempts": [
        {
          "at": "2026-10-26T01:12:11Z",
          "ok": false,
          "http_status": 503,
          "ms": 2001,
          "error": "timeout"
        },
        {
          "at": "2026-10-26T01:12:21Z",
          "ok": false,
          "http_status": 503,
          "ms": 1995,
          "error": "timeout"
        }
      ]
    }
  ],
  "note": "The last 100 deliveries of the last 7 days."
}
```


### `GET /webhooks/{id}/deliveries/{event_id}`

One delivery, with the event as it was sent. Scope: `webhooks:manage`. Docs: https://www.app2email.com/docs/api/webhooks/get-webhook-delivery

Every try, and next_attempt_at while a retry is planned. event_body only with a key that also has messages:read.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The webhook's id. |
| event_id | path | string | yes | The event's id (X-App2email-Delivery, or 'id' in the event). |


Example answer:

```json
{
  "success": true,
  "request_id": "y5wdn",
  "delivery": {
    "event_id": "evt_Xq3k9m2",
    "type": "message.status",
    "created": "2026-10-26T01:12:11Z",
    "delivered": false,
    "attempts": [
      {
        "at": "2026-10-26T01:12:11Z",
        "ok": false,
        "http_status": 503,
        "ms": 2001,
        "error": "timeout"
      }
    ],
    "event_body": {
      "id": "evt_Xq3k9m2",
      "type": "message.status",
      "created": "2026-10-26T01:12:11Z",
      "number": "4976659348270",
      "data": {
        "message_id": "wamid.HBgLNjE0MTIzNDU2NzgVAgARGBJTQU1QTEVfVEVTVF9FVkVOVAA=",
        "to": "61412345678",
        "status": "delivered",
        "timestamp": "2026-10-26T01:12:11Z"
      }
    }
  }
}
```


### `POST /webhooks/{id}/deliveries/{event_id}/redeliver`

Send a stored event again. Scope: `webhooks:manage`. Docs: https://www.app2email.com/docs/api/webhooks/redeliver-webhook-event

The same event (same id, same body) is sent to the webhook's URL once, now, and the answer says how the URL responded. Needs the 'webhooks:manage' scope. An event that is being sent right now (its first try or a planned retry): 409 delivery_in_progress. Delivered: no more planned retries.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The webhook's id. |
| event_id | path | string | yes | The event's id. |


Example answer:

```json
{
  "success": true,
  "request_id": "z8rjh",
  "delivered": true,
  "http_status": 200,
  "response_ms": 180,
  "error": null
}
```


### `GET /events`

Fetch events (no webhook address needed). Scope: `messages:read`. Docs: https://www.app2email.com/docs/api/webhooks/list-events

The number's events, fetched instead of pushed: for an agent or a script with no public address for a webhook. Every event is the JSON a webhook gets (https://www.app2email.com/docs/api/webhooks), with the same id, oldest first. Keep the `cursor` of each answer and pass it as `after` on the next call; after a lost answer the same event can come again, so skip ids you have handled. `wait` holds the answer until an event arrives (long polling; one waiting call at a time is enough). The first call switches the number's feed on: events are kept from then on, for 72 hours (the newest 2,000), and the feed switches itself off after 7 days without a call. Webhooks keep working beside it.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| after | query | string |  | The `cursor` of the previous answer, unchanged. Left out: from the oldest event still kept. `now`: only events from this moment on. |
| wait | query | integer |  | Seconds to wait for an event when there is none yet (0 to 25). 0, the default, answers at once. |
| types | query | string |  | Only these event types, comma separated. Left out: every event. |
| from | query | string |  | Only events of this contact (data.from, data.to, data.contact or data.number): full number, digits, with country code. |
| limit | query | integer |  | How many (1 to 100). |


Example answer:

```json
{
  "success": true,
  "request_id": "e7fd2",
  "events": [
    {
      "id": "evt_Xq3k9m2Lw8Rt5Yp1Zs01",
      "type": "message.status",
      "created": "2026-11-15T03:10:02.000Z",
      "number": "4976659348270",
      "data": {
        "message_id": "wamid.HBgLNjE0MTIzNDU2NzgVAgARGBI5QTNDQTVCM0Q0Q0Q2RTY3RTcA",
        "to": "61412345678",
        "status": "delivered",
        "timestamp": "2026-11-15T03:10:01.000Z",
        "sent_by": "api"
      }
    },
    {
      "id": "evt_Ab7c2d9Ef4Gh6Jk8Lm03",
      "type": "message.received",
      "created": "2026-11-15T03:10:09.000Z",
      "number": "4976659348270",
      "data": {
        "message_id": "wamid.HBgLNjE0MTIzNDU2NzgVAgASGBQzQUZCMTY0MDc2MUYwNzBDNTY5MAA=",
        "from": "61412345678",
        "name": "John",
        "type": "text",
        "text": "Thanks! When will it arrive?",
        "timestamp": "2026-11-15T03:10:08.000Z"
      }
    }
  ],
  "count": 2,
  "cursor": "ec_184467",
  "has_more": false,
  "feed": {
    "on": true,
    "started": false,
    "kept_hours": 72,
    "waited": true
  }
}
```


### `POST /webhooks/test-url`

Send a test event to any URL. Scope: `webhooks:manage`. Docs: https://www.app2email.com/docs/api/webhooks/test-webhook-url

One signed POST to any https URL, answered with the exact request sent and your URL's answer. No saved webhook needed. Shares the 30 tests an hour of the number (429 too_many_tests with Retry-After); 60 an hour per target host and per its IP address.


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| url | string | yes | https only. A private address answers result.stage blocked_address. |
| type | string |  | ping or a number event type (x-a2e-webhook-events, not the Partner group). |
| data | object |  | Your own event data, sent in the normal envelope (at most 16 KB in all). |
| raw | object |  | Sent as the whole body instead of an envelope. |
| secret | string |  | Signs the test. Leave out for a new random one (answered in sent.secret). |
| format | string (app2email \| meta) |  | meta: the events that come from WhatsApp as Meta's own webhook body. |
| headers | object |  | Up to 5 custom headers, the same rules as a webhook's. |


Example answer:

```json
{
  "success": true,
  "request_id": "t7kq2",
  "sent": {
    "method": "POST",
    "url": "https://hooks.example.com/app2email",
    "headers": {
      "Content-Type": "application/json; charset=utf-8",
      "User-Agent": "app2email-webhooks/1.0",
      "X-App2email-Event": "ping",
      "X-App2email-Delivery": "evt_Xq3k9m2Lw8Rt5Yp1Zs01",
      "X-App2email-Signature": "t=1762390800,v1=5257a869e7ecebeda32affa62cdca3fa51cad7e77a0e56ff536d0ce8e108d8bd",
      "X-Hub-Signature-256": "sha256=7d0e8a4a2a5c0b8b1a8f3f62c1d0e2b5c6f8a9e0d1c2b3a4f5e6d7c8b9a0f1e2",
      "X-App2email-Test": "true"
    },
    "body": "{\"id\":\"evt_Xq3k9m2Lw8Rt5Yp1Zs01\",\"type\":\"ping\",\"created\":\"2026-11-06T01:00:00.000Z\",\"number\":\"4976659348270\",\"test\":true,\"data\":{\"webhook_id\":\"wh_test_url\",\"message\":\"Test event. If you can see this, your webhook works.\"}}",
    "secret": "whsec_3Fq9LmZ2xT8pW1rK7vB4nD6sH0jC5yA9",
    "secret_generated": true
  },
  "result": {
    "ok": true,
    "stage": "response",
    "status": 200,
    "ms": 184,
    "headers": {
      "Content-Type": "application/json",
      "Date": "Fri, 06 Nov 2026 01:00:00 GMT",
      "Server": "nginx"
    },
    "body": "{\"received\":true}",
    "body_truncated": false
  }
}
```


### `GET /webhooks/catchers`

Your catchers. Scope: `webhooks:manage`. Docs: https://www.app2email.com/docs/api/webhooks/list-webhook-catchers

The number's catchers that have not expired.


Example answer:

```json
{
  "success": true,
  "request_id": "c4tcl",
  "catchers": [
    {
      "token": "Q7cT2mX9pLk3vB8nR1sWd4Fh6Jk0Zx2C",
      "url": "https://api.app2email.com/hooks/catch/Q7cT2mX9pLk3vB8nR1sWd4Fh6Jk0Zx2C",
      "created": "2026-11-06T01:00:00.000Z",
      "expires": "2026-11-06T02:00:00.000Z",
      "requests": 2,
      "full": false
    }
  ],
  "limits": {
    "catchers": 3,
    "requests": 50,
    "body_max_bytes": 65536
  }
}
```


### `POST /webhooks/catchers`

Get a temporary URL that keeps what it receives. Scope: `webhooks:manage`. Docs: https://www.app2email.com/docs/api/webhooks/create-webhook-catcher

A URL for 1 hour that keeps up to 50 requests of up to 64 KB: use it as a webhook URL or in test-url, then read them. POST https://api.app2email.com/hooks/catch/{token} needs no key and answers 200 {"ok":true}; 404 unknown, 410 expired, 413 over 64 KB, 429 full. At most 3 per number at a time.


### `GET /webhooks/catchers/{token}`

What a catcher received. Scope: `webhooks:manage`. Docs: https://www.app2email.com/docs/api/webhooks/get-webhook-catcher

The requests, oldest first, with their headers and body. Poll with after = the last seq you have.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| token | path | string | yes | The catcher's token. |
| after | query | integer |  | Only the requests after this seq. |


Example answer:

```json
{
  "success": true,
  "request_id": "c4tcg",
  "token": "Q7cT2mX9pLk3vB8nR1sWd4Fh6Jk0Zx2C",
  "url": "https://api.app2email.com/hooks/catch/Q7cT2mX9pLk3vB8nR1sWd4Fh6Jk0Zx2C",
  "created": "2026-11-06T01:00:00.000Z",
  "expires": "2026-11-06T02:00:00.000Z",
  "full": false,
  "count": 1,
  "requests": [
    {
      "seq": 1,
      "received": "2026-11-06T01:00:03.120Z",
      "method": "POST",
      "headers": {
        "Content-Type": "application/json; charset=utf-8",
        "User-Agent": "app2email-webhooks/1.0",
        "X-App2email-Event": "message.status",
        "X-App2email-Delivery": "evt_Xq3k9m2Lw8Rt5Yp1Zs01",
        "X-App2email-Signature": "t=1762390800,v1=5257a869e7ecebeda32affa62cdca3fa51cad7e77a0e56ff536d0ce8e108d8bd",
        "X-Hub-Signature-256": "sha256=7d0e8a4a2a5c0b8b1a8f3f62c1d0e2b5c6f8a9e0d1c2b3a4f5e6d7c8b9a0f1e2"
      },
      "body": "{\"id\":\"evt_Xq3k9m2Lw8Rt5Yp1Zs01\",\"type\":\"message.status\",\"created\":\"2026-11-06T01:00:03.100Z\",\"number\":\"4976659348270\",\"data\":{\"message_id\":\"wamid.SANDBOX.k3XbQ9rTzP2mWv7a1c9eQ7cT\",\"to\":\"61412345678\",\"status\":\"delivered\",\"timestamp\":\"2026-11-06T01:00:03.000Z\",\"sent_by\":\"api\"}}",
      "body_truncated": false
    }
  ]
}
```


### `DELETE /webhooks/catchers/{token}`

Delete a catcher. Scope: `webhooks:manage`. Docs: https://www.app2email.com/docs/api/webhooks/delete-webhook-catcher

Deletes it and what it received. Its URL answers 404 from then on.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| token | path | string | yes | The catcher's token. |


Example answer:

```json
{
  "success": true,
  "request_id": "c4tcd",
  "deleted": "Q7cT2mX9pLk3vB8nR1sWd4Fh6Jk0Zx2C"
}
```


## Analytics


### `GET /analytics/pricing`

WhatsApp cost and volume of this number. Scope: `messages:read`. Docs: https://www.app2email.com/docs/api/analytics/get-pricing-analytics

Meta's pricing_analytics for this number: delivered messages and their cost per period. Estimates, not the invoice.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| since | query | string |  | Start, ISO 8601. Default: 30 days before until. At most 1 year back. |
| until | query | string |  | End, ISO 8601. Default: now. |
| granularity | query | string (half_hour \| day \| month) |  | Default day. |
| countries | query | string |  | Only these countries: comma separated 2-letter codes. |
| dimensions | query | string |  | Break down by: comma separated category, type, country, tier, phone. Default category,type. |


Example answer:

```json
{
  "success": true,
  "request_id": "a2p4r",
  "since": "2026-10-01T00:00:00.000Z",
  "until": "2026-10-03T00:00:00.000Z",
  "granularity": "day",
  "currency": "EUR",
  "data_points": [
    {
      "start": "2026-10-01T00:00:00.000Z",
      "end": "2026-10-02T00:00:00.000Z",
      "pricing_category": "MARKETING",
      "pricing_type": "REGULAR",
      "volume": 120,
      "cost": 15.6
    },
    {
      "start": "2026-10-01T00:00:00.000Z",
      "end": "2026-10-02T00:00:00.000Z",
      "pricing_category": "SERVICE",
      "pricing_type": "FREE_CUSTOMER_SERVICE",
      "volume": 41,
      "cost": 0
    },
    {
      "start": "2026-10-02T00:00:00.000Z",
      "end": "2026-10-03T00:00:00.000Z",
      "pricing_category": "UTILITY",
      "pricing_type": "REGULAR",
      "volume": 300,
      "cost": 6.9
    }
  ],
  "totals": {
    "volume": 461,
    "cost": 22.5
  }
}
```


### `GET /analytics/messages`

Messages sent and delivered, as WhatsApp counts them. Scope: `messages:read`. Docs: https://www.app2email.com/docs/api/analytics/get-message-analytics

Meta's analytics for this number, per period.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| since | query | string |  | Start, ISO 8601. Default: 30 days before until. At most 1 year back. |
| until | query | string |  | End, ISO 8601. Default: now. |
| granularity | query | string (half_hour \| day \| month) |  | Default day. |
| countries | query | string |  | Only these countries: comma separated 2-letter codes. |


Example answer:

```json
{
  "success": true,
  "request_id": "a3m5s",
  "since": "2026-10-01T00:00:00.000Z",
  "until": "2026-10-03T00:00:00.000Z",
  "granularity": "day",
  "data_points": [
    {
      "start": "2026-10-01T00:00:00.000Z",
      "end": "2026-10-02T00:00:00.000Z",
      "sent": 161,
      "delivered": 155
    },
    {
      "start": "2026-10-02T00:00:00.000Z",
      "end": "2026-10-03T00:00:00.000Z",
      "sent": 300,
      "delivered": 291
    }
  ],
  "totals": {
    "sent": 461,
    "delivered": 446
  }
}
```


### `GET /activity`

The WhatsApp Business Account's activity log. Scope: `messages:read`. Docs: https://www.app2email.com/docs/api/analytics/get-account-activity

Newest first: registrations, PIN and partner changes, billing, templates. Covers every number on the WABA.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| limit | query | integer |  | How many (1 to 100, default 25). |
| cursor | query | string |  | The next_cursor of the previous answer. |


Example answer:

```json
{
  "success": true,
  "request_id": "a4c6t",
  "activities": [
    {
      "id": "1234567890123",
      "event_type": "PHONE_NUMBER_REGISTERED_ON_CLOUD_API",
      "category": "PHONE_NUMBER",
      "actor_id": "61550000000001",
      "time": "2026-11-05T22:14:03.000Z"
    },
    {
      "id": "1234567890122",
      "event_type": "TWO_STEP_VERIFICATION_PIN_CHANGED",
      "category": "PHONE_NUMBER",
      "actor_id": "61550000000001",
      "time": "2026-11-05T22:13:40.000Z"
    }
  ],
  "count": 2,
  "next_cursor": "QVFIUmFfVEhuS2xOZA"
}
```


### `GET /conversions/dataset`

The Conversions API dataset of the account. Scope: `messages:read`. Docs: https://www.app2email.com/docs/api/analytics/get-conversions-dataset

404 dataset_not_found: create it first.


Example answer:

```json
{
  "success": true,
  "request_id": "a5d7u",
  "dataset": {
    "id": "1265431020859743",
    "name": "WhatsApp conversions"
  }
}
```


### `POST /conversions/dataset`

Create the Conversions API dataset. Scope: `settings:manage`. Docs: https://www.app2email.com/docs/api/analytics/create-conversions-dataset

One per WhatsApp Business Account. Answer 201.


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| name | string |  |  |


### `GET /conversions/dataset/quality`

Quality of the Conversions API dataset. Scope: `messages:read`. Docs: https://www.app2email.com/docs/api/analytics/get-conversions-dataset-quality

Meta's dataset quality: event match quality, coverage, freshness. fields: Meta's field list (default: all of these).


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| fields | query | string |  | Meta's field list, eg web{event_match_quality,event_name}. |
| agent_name | query | string |  | Only the events a partner integration sent. |


Example answer:

```json
{
  "success": true,
  "request_id": "a8g0x",
  "dataset_id": "1265431020859743",
  "quality": {
    "web": [
      {
        "event_name": "Purchase",
        "event_match_quality": {
          "composite_score": 6.2,
          "match_key_feedback": [
            {
              "identifier": "ctwa_clid",
              "coverage": {
                "percentage": 92.5
              }
            }
          ]
        },
        "event_coverage": {
          "percentage": 71.3
        },
        "data_freshness": {
          "upload_frequency": "real_time"
        }
      }
    ]
  }
}
```


### `POST /conversions/events`

Send conversion events of WhatsApp chats. Scope: `messages:send`. Docs: https://www.app2email.com/docs/api/analytics/send-conversion-events

Up to 1,000 events to the account's dataset (eg a Purchase after a click-to-WhatsApp ad). Defaults: action_source, messaging_channel, the WABA id.


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| data | array of object | yes |  |
| test_event_code | string |  | From Events Manager: the events show under Test events and are not used for ads. |
| partner_agent | string |  |  |


Example answer:

```json
{
  "success": true,
  "request_id": "a7f9w",
  "dataset_id": "1265431020859743",
  "events_received": 1,
  "fbtrace_id": "AbCdEfGh1234"
}
```


## Book-and-Pay


### `GET /bookings/waitlist`

The waitlist of full days. Scope: `bookings:manage or messages:read`. Docs: https://www.app2email.com/docs/api/book-and-pay/list-booking-waitlist

Scope: `bookings:manage` (or `messages:read`). The customers waiting for a time, soonest day first, oldest entry first. Active entries (pending_confirm, waiting, notified) unless include_closed. When a time frees up (a cancellation, a move, a removed time block, and every 5 minutes) the waiting customers of that day get a WhatsApp message with a link to book it; the first booking wins. 409 `waitlist_not_set_up` while the waitlist is not available on the server.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| from | query | string |  | The first day, YYYY-MM-DD in the business time zone. Default today. |
| to | query | string |  | The last day (included). Default from + 60 days; at most 366 days. |
| service_id | query | string |  | Only this service. |
| contact | query | string |  | Only this customer (number with country code, digits only, or business-scoped user id). |
| include_closed | query | boolean |  | true: also booked, expired and removed entries. |
| limit | query | integer |  | At most this many entries (1 to 1000, default 500). |


Example answer:

```json
{
  "success": true,
  "request_id": "w1lst",
  "entries": [
    {
      "id": 12,
      "reference": "WL-4HT9XC",
      "status": "waiting",
      "service_id": "haircut",
      "service_name": "Haircut",
      "provider_id": "maria",
      "provider_name": "Maria",
      "date": "2026-11-20",
      "date_label": "Fri 20 Nov 2026",
      "slot_id": "",
      "time_label": "",
      "contact": "61412345678",
      "contact_name": "Jane",
      "contact_email": "",
      "seats": 1,
      "source": "api",
      "notified_count": 0,
      "notified_at": null,
      "appointment_id": null,
      "note": "",
      "created": "2026-11-13T01:00:00.000Z",
      "updated": "2026-11-13T01:00:00.000Z",
      "day": "2026-11-20",
      "slot_local": "",
      "contact_masked": "•••• 5678",
      "created_at": "2026-11-13T01:00:00.000Z"
    }
  ],
  "count": 1,
  "from": "2026-11-13",
  "to": "2027-01-12",
  "timezone": "Australia/Sydney"
}
```


### `POST /bookings/waitlist`

Put a customer on the waitlist of a full day. Scope: `bookings:manage`. Docs: https://www.app2email.com/docs/api/book-and-pay/add-to-booking-waitlist

Scope: `bookings:manage`. Not with a sandbox key. The service must have its waitlist on, the day must be bookable and have no free time left (or the group time in slot_id must be full) - force: true skips the free-time check. One active entry per customer, service and day: asking again answers 200 with that entry (existing: true). Sends `waitlist.joined`. The customer is offered a time when one opens.


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| contact | string | yes | The customer's WhatsApp number with country code, digits only, or their business-scoped user id. |
| name | string |  |  |
| email | string |  | Optional: the offer goes by e-mail when WhatsApp cannot be used. |
| service_id | string | yes | A service with its waitlist switched on (config.services[].waitlist). |
| provider_id | string |  | Optional: one staff member. Left out: anyone. |
| date | string | yes | The wanted day, YYYY-MM-DD in the business time zone. |
| slot_id | string |  | Optional: a full group time on that day, yyyy-MM-ddTHH:mm (slot_local is taken too). |
| seats | integer |  | Places wanted on a group service. |
| force | boolean |  | true: add even when the day still has free times. |


Example answer:

```json
{
  "success": true,
  "request_id": "w2add",
  "entry": {
    "id": 12,
    "reference": "WL-4HT9XC",
    "status": "waiting",
    "service_id": "haircut",
    "service_name": "Haircut",
    "provider_id": "maria",
    "provider_name": "Maria",
    "date": "2026-11-20",
    "date_label": "Fri 20 Nov 2026",
    "slot_id": "",
    "time_label": "",
    "contact": "61412345678",
    "contact_name": "Jane",
    "contact_email": "",
    "seats": 1,
    "source": "api",
    "notified_count": 0,
    "notified_at": null,
    "appointment_id": null,
    "note": "",
    "created": "2026-11-13T01:00:00.000Z",
    "updated": "2026-11-13T01:00:00.000Z",
    "day": "2026-11-20",
    "slot_local": "",
    "contact_masked": "•••• 5678",
    "created_at": "2026-11-13T01:00:00.000Z"
  },
  "existing": true
}
```


### `POST /bookings/waitlist/{reference}/remove`

Take a customer off the waitlist. Scope: `bookings:manage`. Docs: https://www.app2email.com/docs/api/book-and-pay/remove-from-booking-waitlist

Scope: `bookings:manage`. Not with a sandbox key. The customer is not messaged. Sends `waitlist.removed`. An entry that is already closed answers 200 as it is.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| reference | path | string | yes | The entry's reference (or its id). |


Example answer:

```json
{
  "success": true,
  "request_id": "w3rem",
  "entry": {
    "id": 12,
    "reference": "WL-4HT9XC",
    "status": "removed",
    "service_id": "haircut",
    "service_name": "Haircut",
    "provider_id": "maria",
    "provider_name": "Maria",
    "date": "2026-11-20",
    "date_label": "Fri 20 Nov 2026",
    "slot_id": "",
    "time_label": "",
    "contact": "61412345678",
    "contact_name": "Jane",
    "contact_email": "",
    "seats": 1,
    "source": "api",
    "notified_count": 0,
    "notified_at": null,
    "appointment_id": null,
    "note": "",
    "created": "2026-11-13T01:00:00.000Z",
    "updated": "2026-11-13T01:00:00.000Z",
    "day": "2026-11-20",
    "slot_local": "",
    "contact_masked": "•••• 5678",
    "created_at": "2026-11-13T01:00:00.000Z"
  }
}
```


### `GET /bookings`

The appointments, soonest start first. Scope: `bookings:manage or messages:read`. Docs: https://www.app2email.com/docs/api/book-and-pay/list-bookings

Scope: `bookings:manage` (or `messages:read`). Booked on WhatsApp, from the dashboard or through the API. Filter by a range of days (business time zone) or times, a status, or one contact; `order=desc` for the latest start first. Page with `next_cursor`.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| from | query | string |  | Only appointments starting at or after this day (YYYY-MM-DD, business time zone) or ISO 8601 time. |
| to | query | string |  | Only appointments starting on or before this day (YYYY-MM-DD, included) or before this ISO 8601 time. |
| status | query | string (confirmed \| cancelled \| completed \| no_show) |  | Only this status. |
| contact | query | string |  | Only this customer (number with country code, or business-scoped user id). |
| provider_id | query | string |  | Only this staff member's appointments (GET /bookings/staff). |
| upcoming | query | boolean |  | true: confirmed appointments starting now or later, soonest first (status, from, to and order are then ignored). |
| q | query | string |  | Appointments whose customer name, reference or number contains this text. |
| order | query | string (asc \| desc) |  | asc: soonest start first (default). desc: latest start first. |
| limit | query | integer |  | How many (1 to 200, default 50). |
| cursor | query | string |  | The next_cursor of the previous answer, unchanged. Leave out for the first page. |


Example answer:

```json
{
  "success": true,
  "request_id": "b1kq2",
  "bookings": [
    {
      "id": 42,
      "reference": "BK-7Q3M2A",
      "status": "confirmed",
      "contact": "61412345678",
      "contact_name": "John Smith",
      "contact_email": "john@example.com",
      "service": {
        "id": "haircut",
        "name": "Haircut",
        "duration_min": 30
      },
      "start": "2026-11-09T22:00:00.000Z",
      "end": "2026-11-09T22:30:00.000Z",
      "timezone": "Australia/Sydney",
      "source": "api",
      "calendar": {
        "provider": "google",
        "event_id": "evt_1a2b3c",
        "url": "https://calendar.google.com/calendar/event?eid=..."
      },
      "answers": {},
      "notes": "First visit",
      "provider": {
        "id": "maria",
        "name": "Maria"
      },
      "credits_used": 0,
      "created": "2026-11-06T01:12:09.000Z"
    }
  ],
  "next_cursor": null,
  "count": 1,
  "order": "asc",
  "enabled": true,
  "timezone": "Australia/Sydney"
}
```


### `POST /bookings`

Book an appointment for a customer at a free slot. Scope: `bookings:manage`. Docs: https://www.app2email.com/docs/api/book-and-pay/create-booking

Scope: `bookings:manage`. Not with a sandbox key. The slot must be one of GET /bookings/availability (on the grid, inside the hours, free; the business's own minimum notice does not apply). The customer gets the confirmation on WhatsApp (a text with a calendar file inside their 24 hour window, else the booking confirmation template) unless `notify` is false; the business gets an email, the calendar event is written, and `booking.created` is sent (with `hold: true` when made from a hold). 409 `booking_slot_taken` when the time went meanwhile. To book a time kept with POST /bookings/holds, send its `hold` reference. Send an `Idempotency-Key` header to retry safely: the same key and body within 24 hours gets the first answer again.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| Idempotency-Key | header | string |  | Optional. A unique value for this message or list (eg a UUID). The same request with the same key within 24 hours gets the first answer again, and nothing is sent twice. Ignored by dry runs. |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| contact | string | yes | The customer's WhatsApp number with country code, digits only, or their business-scoped user id. |
| service_id | string | yes | One of config.services[].id (GET /settings/booking). |
| start | string | yes | A free slot's id from GET /bookings/availability: local time in the business time zone, yyyy-MM-ddTHH:mm. |
| name | string | yes |  |
| email | string |  |  |
| notes | string |  | Notes for the business. |
| provider_id | string |  | The staff member (config.providers[].id). Left out: the first free one. |
| notify | boolean |  | Send the customer the confirmation on WhatsApp (a text inside their 24 hour window, else the booking confirmation template). |
| answers | object |  | Optional extra fields kept with the booking. |
| hold | string |  | The reference of a held time (POST /bookings/holds): the booking is made from that hold, takes its reference and frees it. `contact` and `name` from this body win over the hold's; service and time come from the hold. |
| answers_q | object |  | The answers to the service's questions (config.services[].questions), by question id: text, a list for a multi-choice question, true for a tick box. Required questions must be answered (400 `invalid_answers`). |
| location_index | integer |  | Which of the service's locations (config.services[].locations, 0-based). Left out: the first. |
| location_value | string |  | The customer's address, for an at-your-address location (5 to 300 characters). |
| addon_ids | array of string |  | The service's add-ons (config.services[].addons ids): each adds its price and minutes (400 `invalid_addons` for one the service does not offer). |
| guests | array of object |  | People who come along, up to config.services[].guests_max; on a group service each takes a place (400 `invalid_guests`). |
| utm | object |  | Kept with the booking (answers.utm). |
|   source | string |  |  |
|   medium | string |  |  |
|   campaign | string |  |  |
|   term | string |  |  |
|   content | string |  |  |
| series | object |  | Book a series: one appointment per occurrence (each its own reference and reminders; monthly = the same day of the month, a month without it is skipped). Every date is checked; the ones that are not free are skipped and listed in series.skipped of the answer. The customer gets one confirmation. Not with hold. |
|   freq | string (weekly \| biweekly \| every4weeks \| monthly) | yes |  |
|   count | integer | yes |  |


### `GET /bookings/availability`

The free slots per day for a service, as the customer would see them. Scope: `bookings:manage or messages:read`. Docs: https://www.app2email.com/docs/api/book-and-pay/get-booking-availability

Scope: `bookings:manage` (or `messages:read`). Every day of the range (at most 32 days, default today + 6) with its free start times: the opening hours, the closed days, the booked appointments and the calendar's busy time applied. Each slot's `id` is the local time `POST /bookings` takes as `start`. With staff members, `providers` names who is free; `provider_id` asks for one member's own availability.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| service_id | query | string |  | The service (config.services[].id). |
| from | query | string |  | The first day, YYYY-MM-DD in the business time zone. Default today. |
| to | query | string |  | The last day (included). Default from + 6 days; at most 32 days. |
| provider_id | query | string |  | One staff member's own availability (config.providers[].id). Left out: anyone available. |
| addons | query | string |  | A comma list of the service's add-on ids: the slots are long enough for them. |
| seats | query | integer |  | The places wanted on a group time (1 + guests): only times with that many places left. |


Example answer:

```json
{
  "success": true,
  "request_id": "a9xw1",
  "timezone": "Australia/Sydney",
  "enabled": true,
  "days": [
    {
      "date": "2026-11-10",
      "slots": [
        {
          "id": "2026-11-10T09:00",
          "title": "9:00 AM",
          "start": "2026-11-09T22:00:00.000Z",
          "end": "2026-11-09T22:30:00.000Z",
          "providers": [
            "maria",
            "tom"
          ]
        },
        {
          "id": "2026-11-10T09:30",
          "title": "9:30 AM",
          "start": "2026-11-09T22:30:00.000Z",
          "end": "2026-11-09T23:00:00.000Z",
          "providers": [
            "tom"
          ]
        }
      ]
    },
    {
      "date": "2026-11-11",
      "slots": []
    }
  ]
}
```


### `GET /bookings/reports`

The booking report of a range of days. Scope: `bookings:manage or messages:read`. Docs: https://www.app2email.com/docs/api/book-and-pay/get-booking-reports

Scope: `bookings:manage` (or `messages:read`). Over the appointments whose START is in the range (days in the business time zone): totals (bookings, upcoming, completed, cancelled and by the customer, no-shows, the no-show and cancel rates, new and returning customers, revenue and refunds in minor units, the average days booked ahead, the online share), per day, per weekday and hour, per service, staff member and source, and the waitlist numbers. Revenue = online payments of those appointments, less refunds. The range: from / to (at most 366 days), or days (the last N days up to today; default 30). With days=7, 30 or 90 (or nothing) the answer also has the keys of the older report (bookings, completed, cancelled, no_shows, csat, reminders_sent, sessions, top_services, per_provider, nudges). `format=csv`: one line per appointment (reference, date, time, service, staff, customer name, customer phone, status, source, price, paid, add-ons, guests, series, answers); `format=csv_summary`: the older metric,value lines.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| from | query | string |  | The first day, YYYY-MM-DD in the business time zone. |
| to | query | string |  | The last day (included). With from alone: from + 29 days. |
| days | query | integer |  | Instead of from / to: the last N days up to today (1 to 366; 7, 30 or 90 also give the older keys). Default 30. |
| service_id | query | string |  | Only this service (service is taken too). |
| provider_id | query | string |  | Only this staff member (provider is taken too). |
| format | query | string (json \| csv \| csv_summary) |  | csv: one line per appointment. csv_summary: the older metric,value lines. |


Example answer:

```json
{
  "success": true,
  "request_id": "r5mpk",
  "days": 30,
  "from": "2026-10-07T01:00:00.000Z",
  "to": "2026-11-06T01:00:00.000Z",
  "bookings": {
    "total": 48,
    "by_source": {
      "whatsapp_flow": 40,
      "dashboard": 5,
      "api": 3
    }
  },
  "completed": 39,
  "cancelled": {
    "total": 4,
    "by": {
      "customer": 3,
      "business": 1
    }
  },
  "no_shows": 2,
  "no_show_rate": 0.0488,
  "csat": {
    "average": 4.6,
    "responses": 21
  },
  "reminders_sent": 41,
  "sessions": {
    "started": 62,
    "completed": 40,
    "conversion": 0.6452
  },
  "top_services": [
    {
      "id": "haircut",
      "name": "Haircut",
      "count": 30
    },
    {
      "id": "colour",
      "name": "Colour",
      "count": 18
    }
  ],
  "per_provider": [
    {
      "id": "maria",
      "name": "Maria",
      "count": 28
    },
    {
      "id": "tom",
      "name": "Tom",
      "count": 20
    }
  ],
  "nudges": {
    "rebook": 9
  }
}
```


### `GET /bookings/{id}`

One appointment, by id or reference. Scope: `bookings:manage or messages:read`. Docs: https://www.app2email.com/docs/api/book-and-pay/get-booking

Scope: `bookings:manage` (or `messages:read`).


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The booking's id, or its reference (BK-XXXXXX). |


Example answer:

```json
{
  "success": true,
  "request_id": "b8sva",
  "booking": {
    "id": 42,
    "reference": "BK-7Q3M2A",
    "status": "confirmed",
    "contact": "61412345678",
    "contact_name": "John Smith",
    "contact_email": "john@example.com",
    "service": {
      "id": "haircut",
      "name": "Haircut",
      "duration_min": 30
    },
    "start": "2026-11-09T22:00:00.000Z",
    "end": "2026-11-09T22:30:00.000Z",
    "timezone": "Australia/Sydney",
    "source": "api",
    "calendar": {
      "provider": "google",
      "event_id": "evt_1a2b3c",
      "url": "https://calendar.google.com/calendar/event?eid=..."
    },
    "answers": {},
    "notes": "First visit",
    "provider": {
      "id": "maria",
      "name": "Maria"
    },
    "credits_used": 0,
    "created": "2026-11-06T01:12:09.000Z"
  }
}
```


### `POST /bookings/{id}/cancel`

Cancel an appointment. Scope: `bookings:manage`. Docs: https://www.app2email.com/docs/api/book-and-pay/cancel-booking

Scope: `bookings:manage`. Not with a sandbox key. The calendar event is removed, `booking.cancelled` is sent, and the customer is told on WhatsApp (a text inside their 24 hour window, else the cancellation template) unless `notify` is false. 409 `booking_cancelled` when it already was.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The booking's id, or its reference (BK-XXXXXX). |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| reason | string |  |  |
| notify | boolean |  | Tell the customer on WhatsApp (a text inside their 24 hour window, else the cancellation template). |
| scope | string (one \| following) |  | following: this appointment and the later ones of its series (the customer gets one message); the answer adds series { id, cancelled, skipped }. |


Example answer:

```json
{
  "success": true,
  "request_id": "b3nd4",
  "booking": {
    "id": 42,
    "reference": "BK-7Q3M2A",
    "status": "cancelled",
    "contact": "61412345678",
    "contact_name": "John Smith",
    "contact_email": "john@example.com",
    "service": {
      "id": "haircut",
      "name": "Haircut",
      "duration_min": 30
    },
    "start": "2026-11-09T22:00:00.000Z",
    "end": "2026-11-09T22:30:00.000Z",
    "timezone": "Australia/Sydney",
    "source": "api",
    "calendar": {
      "provider": "google",
      "event_id": "evt_1a2b3c",
      "url": "https://calendar.google.com/calendar/event?eid=..."
    },
    "answers": {},
    "notes": "First visit",
    "provider": {
      "id": "maria",
      "name": "Maria"
    },
    "credits_used": 0,
    "created": "2026-11-06T01:12:09.000Z",
    "cancelled": {
      "at": "2026-11-07T03:00:00.000Z",
      "by": "api",
      "reason": "customer asked by phone"
    }
  },
  "note": "Cancelled. The customer is told on WhatsApp (a text inside their 24 hour window, else the cancellation template)."
}
```


### `POST /bookings/{id}/status`

Mark an appointment completed, a no-show, or back to confirmed. Scope: `bookings:manage`. Docs: https://www.app2email.com/docs/api/book-and-pay/set-booking-status

Scope: `bookings:manage`. Not with a sandbox key. Completed appointments get the follow-up message (aftercare and the rating buttons) when the business turned it on; the reports count both. An appointment that is not marked is completed by itself 24 hours after its end. A cancelled appointment cannot be marked (409 `booking_cancelled`).


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The booking's id, or its reference (BK-XXXXXX). |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| status | string (completed \| no_show \| confirmed) | yes | completed: the customer came. no_show: they did not. confirmed: undo one of those (within 7 days of the end). |


Example answer:

```json
{
  "success": true,
  "request_id": "b9twc",
  "booking": {
    "id": 42,
    "reference": "BK-7Q3M2A",
    "status": "completed",
    "contact": "61412345678",
    "contact_name": "John Smith",
    "contact_email": "john@example.com",
    "service": {
      "id": "haircut",
      "name": "Haircut",
      "duration_min": 30
    },
    "start": "2026-11-09T22:00:00.000Z",
    "end": "2026-11-09T22:30:00.000Z",
    "timezone": "Australia/Sydney",
    "source": "api",
    "calendar": {
      "provider": "google",
      "event_id": "evt_1a2b3c",
      "url": "https://calendar.google.com/calendar/event?eid=..."
    },
    "answers": {},
    "notes": "First visit",
    "provider": {
      "id": "maria",
      "name": "Maria"
    },
    "credits_used": 0,
    "created": "2026-11-06T01:12:09.000Z"
  }
}
```


### `GET /settings/booking`

The booking settings, the default Flow's status and every Flow. Scope: `bookings:manage or messages:read`. Docs: https://www.app2email.com/docs/api/book-and-pay/get-booking-settings

Scope: `bookings:manage` (or `messages:read`). Every key of the configuration with its value (defaults filled in): the trigger words, the hours, the services, the messages, the calendar, the staff members; plus the number's Book-and-Pay Flows (as booking_flow in GET /flows).


Example answer:

```json
{
  "success": true,
  "request_id": "s4bkg",
  "enabled": true,
  "configured": true,
  "timezone": "Australia/Sydney",
  "key_status": "valid",
  "validation": [],
  "config": {
    "trigger": {
      "keywords": [
        "book",
        "booking",
        "appointment",
        "reserve",
        "reservation",
        "schedule"
      ],
      "new_contact": false,
      "cancel_keywords": [
        "cancel"
      ],
      "reschedule_keywords": [
        "reschedule",
        "change booking"
      ],
      "other_words_limit": 10,
      "intro_text": "Tap the button below to choose a time that suits you.",
      "cta": "Book now",
      "header": "",
      "footer": ""
    },
    "schedule": {
      "timezone": "Australia/Sydney",
      "hours": {
        "mon": [
          [
            "09:00",
            "17:00"
          ]
        ],
        "tue": [
          [
            "09:00",
            "17:00"
          ]
        ],
        "wed": [
          [
            "09:00",
            "17:00"
          ]
        ],
        "thu": [
          [
            "09:00",
            "17:00"
          ]
        ],
        "fri": [
          [
            "09:00",
            "17:00"
          ]
        ],
        "sat": [],
        "sun": []
      },
      "slot_interval_min": 30,
      "buffer_before_min": 0,
      "buffer_after_min": 0,
      "min_notice_min": 120,
      "max_advance_days": 30,
      "max_per_slot": 1,
      "overrides": []
    },
    "services": [
      {
        "id": "haircut",
        "name": "Haircut",
        "duration_min": 30,
        "description": "",
        "price": "$40",
        "enabled": true
      }
    ],
    "details": {
      "ask_email": true,
      "ask_notes": true
    },
    "messages": {
      "business_name": "",
      "location": "12 Example St, Sydney",
      "confirmation_text": "You're booked: {service} on {date} at {time} ({duration} min). Reference {reference}. Reply CANCEL if your plans change.",
      "send_ics": true,
      "notify_email": ""
    },
    "calendar": {
      "provider": "google",
      "write_calendar_id": "primary",
      "busy_calendar_ids": [],
      "event_title": "{service} - {name}",
      "event_description": "Booked on WhatsApp.\nPhone: +{phone}\nReference: {reference}\n{notes}"
    },
    "providers": []
  },
  "flow": {
    "key": "booking",
    "name": "Appointment booking",
    "kind": "booking",
    "enabled": true,
    "is_default": true,
    "trigger_keywords": [],
    "id": "1234567890123456",
    "status": "published",
    "can_send": true,
    "health": "AVAILABLE",
    "last_published_at": "2026-11-06T00:00:00Z",
    "updated_at": "2026-11-06T00:00:00.000Z"
  },
  "flows": [
    {
      "key": "booking",
      "name": "Appointment booking",
      "kind": "booking",
      "enabled": true,
      "is_default": true,
      "trigger_keywords": [],
      "id": "1234567890123456",
      "status": "published",
      "can_send": true,
      "health": "AVAILABLE",
      "last_published_at": "2026-11-06T00:00:00Z",
      "updated_at": "2026-11-06T00:00:00.000Z"
    }
  ]
}
```


### `PUT /settings/booking`

Switch Book-and-Pay on or off and change the settings. Scope: `bookings:manage`. Docs: https://www.app2email.com/docs/api/book-and-pay/update-booking-settings

Scope: `bookings:manage`. Not with a sandbox key. `config` is partial: a section object is merged key by key into the stored section, a list (services, providers, schedule.overrides) or a single value replaces what is stored. The whole result is checked against the rules of every section (400 `invalid_setting` with `details.problems`; nothing is saved then). Switching Book-and-Pay on also creates the utility templates bookings send outside the 24 hour window (Meta reviews them).


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| enabled | boolean |  |  |
| config | object |  | The booking configuration, by section. trigger: the words that send the Flow, its intro text and button; schedule: timezone, opening hours per weekday (hours.mon ... [["09:00", "17:00"]]), slot_interval_min, buffers, min_notice_min, max_advance_days, max_per_slot, max_per_day (the most appointments on one day, per staff member when there is staff; 0 = no limit), cancel_notice_min (a customer may cancel or move only until this many minutes before the start; 0 = any time), overrides (closed days); services: id, name, duration_min, description, price, enabled, prep_text, aftercare_text, retail_links, payment_link, deposit_text; details: ask_email, ask_notes; messages: the texts the customer gets (placeholders {service} {date} {time} {duration} {business} {location} {reference} {name} {phone} {notes} {end_time} {provider} {prep} {booking_link}), web: see the web property, reminders, followup, rebook, notify_email; calendar: provider (builtin \| google \| microsoft \| caldav \| ics \| calcom \| calendly \| acuity \| square \| msbookings \| simplybook \| setmore \| zohobookings), write_calendar_id, busy_calendar_ids, event_title, event_description; providers: the staff members. GET /settings/booking shows every key with its value. |
|   trigger | object |  | The words that start a booking, and the message with the button. `other_words_limit` (default 10, 0 to 100): a trigger word counts only when the message has fewer than this many other words, so a long message never starts a Flow; 0 = a message of any length. |
|   schedule | object |  |  |
|   services | array of object |  |  |
|   details | object |  |  |
|   messages | object |  |  |
|   calendar | object |  |  |
|   web | object |  | The online booking page: enabled, slug (the public address /book/<slug>; unique, 5 to 40 characters of a-z 0-9 and - for a new or changed address), headline, intro, trigger_mode (flow \| link \| both), link_button, link_text, link_valid_days (1..60), hold_minutes (5..30), confirm_text (must contain {reference}), allow_manage. |
|   providers | array of object |  |  |


Example answer:

```json
{
  "success": true,
  "request_id": "s4bkg",
  "enabled": true,
  "configured": true,
  "timezone": "Australia/Sydney",
  "key_status": "valid",
  "validation": [],
  "config": {
    "trigger": {
      "keywords": [
        "book",
        "booking",
        "appointment",
        "reserve",
        "reservation",
        "schedule"
      ],
      "new_contact": false,
      "cancel_keywords": [
        "cancel"
      ],
      "reschedule_keywords": [
        "reschedule",
        "change booking"
      ],
      "other_words_limit": 10,
      "intro_text": "Tap the button below to choose a time that suits you.",
      "cta": "Book now",
      "header": "",
      "footer": ""
    },
    "schedule": {
      "timezone": "Australia/Sydney",
      "hours": {
        "mon": [
          [
            "09:00",
            "17:00"
          ]
        ],
        "tue": [
          [
            "09:00",
            "17:00"
          ]
        ],
        "wed": [
          [
            "09:00",
            "17:00"
          ]
        ],
        "thu": [
          [
            "09:00",
            "17:00"
          ]
        ],
        "fri": [
          [
            "09:00",
            "17:00"
          ]
        ],
        "sat": [],
        "sun": []
      },
      "slot_interval_min": 30,
      "buffer_before_min": 0,
      "buffer_after_min": 0,
      "min_notice_min": 120,
      "max_advance_days": 30,
      "max_per_slot": 1,
      "overrides": []
    },
    "services": [
      {
        "id": "haircut",
        "name": "Haircut",
        "duration_min": 30,
        "description": "",
        "price": "$40",
        "enabled": true
      }
    ],
    "details": {
      "ask_email": true,
      "ask_notes": true
    },
    "messages": {
      "business_name": "",
      "location": "12 Example St, Sydney",
      "confirmation_text": "You're booked: {service} on {date} at {time} ({duration} min). Reference {reference}. Reply CANCEL if your plans change.",
      "send_ics": true,
      "notify_email": ""
    },
    "calendar": {
      "provider": "google",
      "write_calendar_id": "primary",
      "busy_calendar_ids": [],
      "event_title": "{service} - {name}",
      "event_description": "Booked on WhatsApp.\nPhone: +{phone}\nReference: {reference}\n{notes}"
    },
    "providers": []
  },
  "flow": {
    "key": "booking",
    "name": "Appointment booking",
    "kind": "booking",
    "enabled": true,
    "is_default": true,
    "trigger_keywords": [],
    "id": "1234567890123456",
    "status": "published",
    "can_send": true,
    "health": "AVAILABLE",
    "last_published_at": "2026-11-06T00:00:00Z",
    "updated_at": "2026-11-06T00:00:00.000Z"
  },
  "flows": [
    {
      "key": "booking",
      "name": "Appointment booking",
      "kind": "booking",
      "enabled": true,
      "is_default": true,
      "trigger_keywords": [],
      "id": "1234567890123456",
      "status": "published",
      "can_send": true,
      "health": "AVAILABLE",
      "last_published_at": "2026-11-06T00:00:00Z",
      "updated_at": "2026-11-06T00:00:00.000Z"
    }
  ]
}
```


### `POST /flows/{key}/send`

Send a Flow to a contact (the booking form or another form). Scope: `bookings:manage`. Docs: https://www.app2email.com/docs/api/book-and-pay/send-flow

Scope: `bookings:manage`. Not with a sandbox key. A Flow of the number's Book-and-Pay section, by its `key` (GET /flows). A Flow message is free-form: it can only go to a contact who wrote to the number in the last 24 hours (422 `outside_24h_window`; send an approved template first, then the Flow when they answer). The Flow must be enabled and published (409 `flow_not_published`). The contact's answers come back as `booking.created` (a booking Flow) or `flow.completed` (a form Flow). Counts as one message of the plan.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| key | path | string | yes | The Flow's key (GET /flows). |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| contact | string | yes | The contact's WhatsApp number with country code, digits only, or their business-scoped user id. They must have written to the number in the last 24 hours. |
| purpose | string (book \| reschedule) |  | reschedule: move the contact's next appointment (a booking Flow only). |


Example answer:

```json
{
  "success": true,
  "request_id": "f7rhb",
  "sent": true,
  "message_id": "wamid.HBgLNjE0MTIzNDU2NzgVAgARGBI...",
  "session_id": 518,
  "flow": {
    "key": "booking",
    "name": "Appointment booking",
    "kind": "booking"
  },
  "contact": "61412345678",
  "purpose": "book",
  "note": "Sent. The contact's answers come back as the booking.created event (a booking Flow) or the flow.completed event (a form Flow)."
}
```


## Calendar


### `PATCH /bookings/{id}`

Change an appointment's details. Scope: `bookings:manage`. Docs: https://www.app2email.com/docs/api/calendar/update-booking

Scope: `bookings:manage`. Not with a sandbox key. The customer's `name` or `email`, the `notes`, the `answers` and the staff member (`provider_id`: the time must be free for the new one, else 409 `booking_slot_taken`; the calendar event moves too). The time is changed with POST /bookings/{id}/reschedule. `booking.updated` is sent with `changed` naming the fields.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The booking's id, or its reference (BK-XXXXXX). |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| name | string |  |  |
| email | string |  |  |
| notes | string |  |  |
| provider_id | string |  | Another staff member; "any" = the first free one. The time must be free for them (409 booking_slot_taken). |
| answers | object |  | Replaces the extra fields kept with the booking. |


Example answer:

```json
{
  "success": true,
  "request_id": "c9bp1",
  "booking": {
    "id": 42,
    "reference": "BK-7Q3M2A",
    "status": "confirmed",
    "contact": "61412345678",
    "contact_name": "John Smith",
    "contact_email": "john@example.com",
    "service": {
      "id": "haircut",
      "name": "Haircut",
      "duration_min": 30
    },
    "start": "2026-11-11T23:00:00.000Z",
    "end": "2026-11-11T23:30:00.000Z",
    "timezone": "Australia/Sydney",
    "source": "api",
    "calendar": {
      "provider": "google",
      "event_id": "evt_1a2b3c",
      "url": null,
      "error": null
    },
    "answers": {},
    "notes": "First visit",
    "provider": {
      "id": "maria",
      "name": "Maria"
    },
    "credits_used": 0,
    "link_id": null,
    "notes_count": 1,
    "created": "2026-11-06T01:12:09.000Z"
  }
}
```


### `GET /calendar`

Everything on the calendar for a range of days. Scope: `bookings:manage or messages:read`. Docs: https://www.app2email.com/docs/api/calendar/get-calendar

Scope: `bookings:manage` (or `messages:read`). One feed for a range of days (business time zone; default 7 days from today, at most 62): the appointments, the blocked time, the busy time of the connected calendar (our own appointments left out) and the times held right now, each with `start`/`end` in UTC and `start_local`/`end_local`; plus the opening hours per day (overrides applied), the staff and the services. `include` picks any of `bookings,blocks,busy,holds`; cancelled appointments only with `cancelled=true`.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| from | query | string |  | The first day, YYYY-MM-DD in the business time zone. Default today. |
| to | query | string |  | The last day (included). Default from + 6 days; at most 62 days. |
| provider_id | query | string |  | Only this staff member's entries (and the business-wide ones). Left out: everyone. |
| include | query | string |  | Comma list of bookings, blocks, busy, holds. Default: all four. |
| cancelled | query | boolean |  | true: also the cancelled appointments. |


Example answer:

```json
{
  "success": true,
  "request_id": "c1fd2",
  "timezone": "Australia/Sydney",
  "from": "2026-11-10",
  "to": "2026-11-16",
  "now_local": "2026-11-11T10:42",
  "enabled": true,
  "web": {
    "enabled": true,
    "slug": "sample-salon",
    "url": "https://www.app2email.com/book/sample-salon"
  },
  "hours": {
    "2026-11-12": [
      [
        "09:00",
        "17:00"
      ]
    ],
    "2026-11-14": []
  },
  "providers": [
    {
      "id": "maria",
      "name": "Maria",
      "enabled": true,
      "services": [
        "haircut"
      ],
      "hours": {
        "2026-11-12": [
          [
            "09:00",
            "17:00"
          ]
        ]
      }
    }
  ],
  "services": [
    {
      "id": "haircut",
      "name": "Haircut",
      "duration_min": 30,
      "price": "$40",
      "description": "",
      "enabled": true
    }
  ],
  "events": [
    {
      "kind": "booking",
      "id": 42,
      "reference": "BK-7Q3M2A",
      "status": "confirmed",
      "start": "2026-11-11T23:00:00.000Z",
      "end": "2026-11-11T23:30:00.000Z",
      "start_local": "2026-11-12T10:00",
      "end_local": "2026-11-12T10:30",
      "service_id": "haircut",
      "service_name": "Haircut",
      "duration_min": 30,
      "provider_id": "maria",
      "provider_name": "Maria",
      "contact": "61412345678",
      "contact_name": "John Smith",
      "notes_count": 1
    },
    {
      "id": 3,
      "provider_id": "maria",
      "title": "Lunch",
      "notes": "",
      "start": "2026-11-14T01:00:00.000Z",
      "end": "2026-11-14T02:00:00.000Z",
      "start_local": "2026-11-14T12:00",
      "end_local": "2026-11-14T13:00",
      "source": "api",
      "created_by": "API key Planner",
      "created": "2026-11-11T01:12:09.000Z",
      "updated": "2026-11-11T01:12:09.000Z",
      "kind": "block"
    },
    {
      "kind": "busy",
      "provider_id": "maria",
      "title": "Busy (Google Calendar)",
      "start": "2026-11-12T03:00:00.000Z",
      "end": "2026-11-12T04:00:00.000Z",
      "start_local": "2026-11-12T14:00",
      "end_local": "2026-11-12T15:00"
    },
    {
      "kind": "hold",
      "reference": "BK-4HT9XC",
      "service_id": "haircut",
      "service_name": "Haircut",
      "provider_id": "maria",
      "name": "John",
      "start": "2026-11-12T22:00:00.000Z",
      "end": "2026-11-12T22:30:00.000Z",
      "start_local": "2026-11-13T09:00",
      "end_local": "2026-11-13T09:30",
      "expires": "2026-11-11T01:22:00.000Z"
    }
  ]
}
```


### `GET /calendar/blocks`

The blocked times. Scope: `bookings:manage or messages:read`. Docs: https://www.app2email.com/docs/api/calendar/list-calendar-blocks

Scope: `bookings:manage` (or `messages:read`). The time blocks touching a range of days (business time zone; default 31 days from today, at most 62), soonest first. With `provider_id`: that staff member's blocks and the business-wide ones.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| from | query | string |  | The first day, YYYY-MM-DD. Default today. |
| to | query | string |  | The last day (included). Default from + 30 days. |
| provider_id | query | string |  | One staff member's blocks and the business-wide ones. |


Example answer:

```json
{
  "success": true,
  "request_id": "c2bl3",
  "blocks": [
    {
      "id": 3,
      "provider_id": "maria",
      "title": "Lunch",
      "notes": "",
      "start": "2026-11-14T01:00:00.000Z",
      "end": "2026-11-14T02:00:00.000Z",
      "start_local": "2026-11-14T12:00",
      "end_local": "2026-11-14T13:00",
      "source": "api",
      "created_by": "API key Planner",
      "created": "2026-11-11T01:12:09.000Z",
      "updated": "2026-11-11T01:12:09.000Z"
    }
  ],
  "count": 1,
  "from": "2026-11-10",
  "to": "2026-12-10",
  "timezone": "Australia/Sydney"
}
```


### `POST /calendar/blocks`

Block time so that no one can book it. Scope: `bookings:manage`. Docs: https://www.app2email.com/docs/api/calendar/create-calendar-block

Scope: `bookings:manage`. Not with a sandbox key. Time off, a break, a closed afternoon: for one staff member (`provider_id`) or the whole business. Give `start` and `end`, or `date` for one whole day. Existing appointments are not touched. The block is made with `source` "api" and `created_by` "API key <name>"; `calendar.block.created` is sent. Send an `Idempotency-Key` header to retry safely: the same key and body within 24 hours gets the first answer again (an error does not use the key up).


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| Idempotency-Key | header | string |  | Optional. A unique value for this message or list (eg a UUID). The same request with the same key within 24 hours gets the first answer again, and nothing is sent twice. Ignored by dry runs. |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| start | string |  | Local time in the business time zone, yyyy-MM-ddTHH:mm. Or ISO 8601 with an offset (2026-11-14T12:00:00+11:00). |
| end | string |  | Same format as start. After start, at most 31 days later. |
| date | string |  | Instead of start and end: one whole day (YYYY-MM-DD, business time zone). |
| provider_id | string |  | A staff member (GET /bookings/staff). Left out: the whole business. |
| title | string |  |  |
| notes | string |  |  |


### `PATCH /calendar/blocks/{id}`

Change a blocked time. Scope: `bookings:manage`. Docs: https://www.app2email.com/docs/api/calendar/update-calendar-block

Scope: `bookings:manage`. Not with a sandbox key. Any of `start`, `end`, `date`, `provider_id`, `title`, `notes`; what is left out stays.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The block's id. |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| start | string |  |  |
| end | string |  |  |
| date | string |  | One whole day: sets start and end. |
| provider_id | string |  |  |
| title | string |  |  |
| notes | string |  |  |


Example answer:

```json
{
  "success": true,
  "request_id": "c4bu5",
  "block": {
    "id": 3,
    "provider_id": "maria",
    "title": "Long lunch",
    "notes": "",
    "start": "2026-11-14T01:00:00.000Z",
    "end": "2026-11-14T02:30:00.000Z",
    "start_local": "2026-11-14T12:00",
    "end_local": "2026-11-14T13:30",
    "source": "api",
    "created_by": "API key Planner",
    "created": "2026-11-11T01:12:09.000Z",
    "updated": "2026-11-11T01:12:09.000Z"
  }
}
```


### `DELETE /calendar/blocks/{id}`

Remove a blocked time. Scope: `bookings:manage`. Docs: https://www.app2email.com/docs/api/calendar/delete-calendar-block

Scope: `bookings:manage`. Not with a sandbox key. The time can be booked again. `calendar.block.deleted` is sent.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The block's id. |


Example answer:

```json
{
  "success": true,
  "request_id": "c5bd6",
  "deleted": true,
  "block": {
    "id": 3,
    "provider_id": "maria",
    "title": "Lunch",
    "notes": "",
    "start": "2026-11-14T01:00:00.000Z",
    "end": "2026-11-14T02:00:00.000Z",
    "start_local": "2026-11-14T12:00",
    "end_local": "2026-11-14T13:00",
    "source": "api",
    "created_by": "API key Planner",
    "created": "2026-11-11T01:12:09.000Z",
    "updated": "2026-11-11T01:12:09.000Z"
  }
}
```


### `GET /bookings/services`

The services a customer can book, and their staff. Scope: `bookings:manage or messages:read`. Docs: https://www.app2email.com/docs/api/calendar/list-bookable-services

Scope: `bookings:manage` (or `messages:read`). The enabled services with their length, price and description, and the staff members who do each one (`staff` is empty when the business has no staff). The ids go into GET /bookings/availability, GET /bookings/next, POST /bookings and POST /bookings/holds.


Example answer:

```json
{
  "success": true,
  "request_id": "c6sv7",
  "services": [
    {
      "id": "haircut",
      "name": "Haircut",
      "duration_min": 30,
      "price": "$40",
      "description": null,
      "staff": [
        "maria",
        "tom"
      ]
    }
  ],
  "timezone": "Australia/Sydney",
  "enabled": true
}
```


### `GET /bookings/staff`

The staff members and the services they do. Scope: `bookings:manage or messages:read`. Docs: https://www.app2email.com/docs/api/calendar/list-booking-staff

Scope: `bookings:manage` (or `messages:read`). The enabled staff members (`provider_id` in the other calls) with the ids of the enabled services each one does. Empty when the business has no staff.


Example answer:

```json
{
  "success": true,
  "request_id": "c7st8",
  "staff": [
    {
      "id": "maria",
      "name": "Maria",
      "services": [
        "haircut",
        "colour"
      ]
    }
  ],
  "timezone": "Australia/Sydney",
  "enabled": true
}
```


### `GET /bookings/next`

The next free start times for a service, across days. Scope: `bookings:manage or messages:read`. Docs: https://www.app2email.com/docs/api/calendar/get-next-booking-slots

Scope: `bookings:manage` (or `messages:read`). Like GET /bookings/availability but without choosing days: the next `count` free start times after `after` (default now), looking at most 60 days ahead. Each slot's `id` is what POST /bookings, /bookings/holds and /bookings/{id}/reschedule take as `start`.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| service_id | query | string |  | The service (GET /bookings/services). |
| provider_id | query | string |  | One staff member's own availability. Left out: anyone available. |
| after | query | string |  | Only times after this: a day (YYYY-MM-DD, its start in the business time zone) or an ISO 8601 time. Default now. |
| count | query | integer |  | How many slots (1 to 20). |


Example answer:

```json
{
  "success": true,
  "request_id": "c8nx9",
  "slots": [
    {
      "id": "2026-11-12T09:00",
      "date": "2026-11-12",
      "title": "9:00 AM",
      "start": "2026-11-11T22:00:00.000Z",
      "end": "2026-11-11T22:30:00.000Z",
      "providers": [
        "maria"
      ]
    }
  ],
  "count": 1,
  "timezone": "Australia/Sydney",
  "enabled": true
}
```


### `POST /bookings/{id}/reschedule`

Move an appointment to another time. Scope: `bookings:manage`. Docs: https://www.app2email.com/docs/api/calendar/reschedule-booking

Scope: `bookings:manage`. Not with a sandbox key. Moves a confirmed appointment in place: same `id` and `reference`, the calendar event moved, reminders start again. `start` must be a free slot (the booking's own time counts as free). The customer is told on WhatsApp unless `notify` is false. `booking.rescheduled` is sent with `rescheduled_from`. 409 `booking_slot_taken` when the time is not free. Send an `Idempotency-Key` header to retry safely: the same key and body within 24 hours gets the first answer again (an error does not use the key up).


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The booking's id, or its reference (BK-XXXXXX). |
| Idempotency-Key | header | string |  | Optional. A unique value for this message or list (eg a UUID). The same request with the same key within 24 hours gets the first answer again, and nothing is sent twice. Ignored by dry runs. |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| start | string | yes | A free slot (GET /bookings/availability or /bookings/next): Local time in the business time zone, yyyy-MM-ddTHH:mm. |
| provider_id | string |  | Left out: the booking's own staff member. "any": the first free one. |
| notify | boolean |  | Tell the customer on WhatsApp (a text inside their 24 hour window, else the confirmation template). |
| scope | string (one \| following) |  | following: this booking and the later ones of its series move by the same time difference (each checked; the customer gets one message); the answer adds series { id, moved, skipped }. |


Example answer:

```json
{
  "success": true,
  "request_id": "c0rs2",
  "booking": {
    "id": 42,
    "reference": "BK-7Q3M2A",
    "status": "confirmed",
    "contact": "61412345678",
    "contact_name": "John Smith",
    "contact_email": "john@example.com",
    "service": {
      "id": "haircut",
      "name": "Haircut",
      "duration_min": 30
    },
    "start": "2026-11-11T23:00:00.000Z",
    "end": "2026-11-11T23:30:00.000Z",
    "timezone": "Australia/Sydney",
    "source": "api",
    "calendar": {
      "provider": "google",
      "event_id": "evt_1a2b3c",
      "url": null,
      "error": null
    },
    "answers": {},
    "notes": "First visit",
    "provider": {
      "id": "maria",
      "name": "Maria"
    },
    "credits_used": 0,
    "link_id": null,
    "notes_count": 1,
    "created": "2026-11-06T01:12:09.000Z"
  },
  "note": "Moved. The booking keeps its id and reference. The customer is told on WhatsApp."
}
```


### `GET /bookings/{id}/notes`

The internal notes of an appointment and its customer. Scope: `bookings:manage or messages:read`. Docs: https://www.app2email.com/docs/api/calendar/list-booking-notes

Scope: `bookings:manage` (or `messages:read`). The notes written on this appointment and the customer's other notes, pinned first then newest; `on_this_booking` tells them apart. Notes are never shown to the customer.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The booking's id, or its reference (BK-XXXXXX). |


Example answer:

```json
{
  "success": true,
  "request_id": "d1nl3",
  "notes": [
    {
      "id": 7,
      "contact": "61412345678",
      "appointment_id": 42,
      "booking_reference": "BK-7Q3M2A",
      "body": "Prefers the window seat.",
      "author": "API key Planner",
      "author_kind": "api",
      "pinned": false,
      "created": "2026-11-11T01:12:09.000Z",
      "updated": "2026-11-11T01:12:09.000Z",
      "on_this_booking": true
    }
  ],
  "count": 1,
  "booking": {
    "id": 42,
    "reference": "BK-7Q3M2A"
  },
  "contact": "61412345678"
}
```


### `POST /bookings/{id}/notes`

Add an internal note to an appointment. Scope: `bookings:manage`. Docs: https://www.app2email.com/docs/api/calendar/add-booking-note

Scope: `bookings:manage`. Not with a sandbox key. The note is about the appointment's customer and written on this appointment. `author` is "API key <name>" and `author_kind` "api". `booking.note.created` is sent. Send an `Idempotency-Key` header to retry safely: the same key and body within 24 hours gets the first answer again (an error does not use the key up).


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The booking's id, or its reference (BK-XXXXXX). |
| Idempotency-Key | header | string |  | Optional. A unique value for this message or list (eg a UUID). The same request with the same key within 24 hours gets the first answer again, and nothing is sent twice. Ignored by dry runs. |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| body | string | yes |  |
| pinned | boolean |  |  |
| contact | string |  | POST /bookings/notes only: the customer (number with country code, or business-scoped user id). Left out when booking_id is given. |
| booking_id | string |  | POST /bookings/notes only: the appointment (id or reference) the note is written on; the customer is taken from it. |


### `GET /bookings/notes`

The internal notes of a customer. Scope: `bookings:manage or messages:read`. Docs: https://www.app2email.com/docs/api/calendar/list-customer-notes

Scope: `bookings:manage` (or `messages:read`). Every note about one customer (`contact` is required), pinned first then newest. Page with `next_cursor`.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| contact | query | string |  | The customer: number with country code, or business-scoped user id. Required. |
| limit | query | integer |  | How many (1 to 200, default 50). |
| cursor | query | string |  | The next_cursor of the previous answer, unchanged. Leave out for the first page. |


Example answer:

```json
{
  "success": true,
  "request_id": "d3nc5",
  "notes": [
    {
      "id": 7,
      "contact": "61412345678",
      "appointment_id": 42,
      "booking_reference": "BK-7Q3M2A",
      "body": "Prefers the window seat.",
      "author": "API key Planner",
      "author_kind": "api",
      "pinned": false,
      "created": "2026-11-11T01:12:09.000Z",
      "updated": "2026-11-11T01:12:09.000Z"
    }
  ],
  "next_cursor": null,
  "count": 1,
  "contact": "61412345678"
}
```


### `POST /bookings/notes`

Add an internal note to a customer. Scope: `bookings:manage`. Docs: https://www.app2email.com/docs/api/calendar/add-customer-note

Scope: `bookings:manage`. Not with a sandbox key. Give `contact`, or `booking_id` to write it on one appointment (the customer is taken from it). `author` is "API key <name>", `author_kind` "api". `booking.note.created` is sent. Send an `Idempotency-Key` header to retry safely: the same key and body within 24 hours gets the first answer again (an error does not use the key up).


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| Idempotency-Key | header | string |  | Optional. A unique value for this message or list (eg a UUID). The same request with the same key within 24 hours gets the first answer again, and nothing is sent twice. Ignored by dry runs. |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| body | string | yes |  |
| pinned | boolean |  |  |
| contact | string |  | POST /bookings/notes only: the customer (number with country code, or business-scoped user id). Left out when booking_id is given. |
| booking_id | string |  | POST /bookings/notes only: the appointment (id or reference) the note is written on; the customer is taken from it. |


### `DELETE /bookings/notes/{note_id}`

Delete an internal note. Scope: `bookings:manage`. Docs: https://www.app2email.com/docs/api/calendar/delete-booking-note

Scope: `bookings:manage`. Not with a sandbox key. The note is hidden from every list.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| note_id | path | string | yes | The note's id. |


Example answer:

```json
{
  "success": true,
  "request_id": "d5nd7",
  "deleted": true,
  "id": 7
}
```


### `GET /bookings/links`

The personal booking links. Scope: `bookings:manage or messages:read`. Docs: https://www.app2email.com/docs/api/calendar/list-booking-links

Scope: `bookings:manage` (or `messages:read`). The personal links of the number, newest first; `contact` shows one customer's. Each has its `state` (ok, expired, revoked, used_up, off) and how often it was opened. Page with `next_cursor`.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| contact | query | string |  | Only this customer's links. |
| limit | query | integer |  | How many (1 to 200, default 50). |
| cursor | query | string |  | The next_cursor of the previous answer, unchanged. Leave out for the first page. |


Example answer:

```json
{
  "success": true,
  "request_id": "e1ll8",
  "links": [
    {
      "id": 21,
      "code": "k3XbQ9rTzP2m",
      "url": "https://www.app2email.com/book/k3XbQ9rTzP2m",
      "kind": "personal",
      "contact": "61412345678",
      "contact_name": "John",
      "service_id": null,
      "provider_id": null,
      "purpose": "book",
      "booking_id": null,
      "single_use": false,
      "max_uses": 0,
      "uses": 0,
      "expires": "2026-11-18T01:12:09.000Z",
      "revoked": null,
      "source": "api",
      "created_by": "API key Planner",
      "open_count": 0,
      "last_opened": null,
      "created": "2026-11-11T01:12:09.000Z",
      "state": "ok"
    }
  ],
  "next_cursor": null,
  "count": 1
}
```


### `POST /bookings/links`

Make a link that opens the online booking page. Scope: `bookings:manage`. Docs: https://www.app2email.com/docs/api/calendar/create-booking-link

Scope: `bookings:manage`. Not with a sandbox key. A link for a customer to book, move an appointment (`purpose` reschedule + `booking_id`) or manage their appointments (`purpose` manage). Send the `url` to the customer yourself. With a `contact` the page knows the customer and confirms the booking right away; without one it is a one-off link and the customer confirms on WhatsApp. The online booking page must be switched on, else the answer says the link will not open yet. `created_by` is "API key <name>", `source` "api". Send an `Idempotency-Key` header to retry safely: the same key and body within 24 hours gets the first answer again (an error does not use the key up).


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| Idempotency-Key | header | string |  | Optional. A unique value for this message or list (eg a UUID). The same request with the same key within 24 hours gets the first answer again, and nothing is sent twice. Ignored by dry runs. |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| contact | string |  | The customer's WhatsApp number with country code, digits only, or their business-scoped user id. |
| name | string |  |  |
| service_id | string |  | Preselect a service. |
| provider_id | string |  | Preselect a staff member. |
| purpose | string (book \| reschedule \| manage) |  |  |
| booking_id | string |  | The appointment (id or reference) of a reschedule / manage link. |
| single_use | boolean |  | The link stops working after one booking. |
| expires_in_hours | integer |  | Default: the business's setting (7 days). |


### `DELETE /bookings/links/{code}`

Revoke a personal booking link. Scope: `bookings:manage`. Docs: https://www.app2email.com/docs/api/calendar/revoke-booking-link

Scope: `bookings:manage`. Not with a sandbox key. The link stops opening. The public address is not a personal link: change it on the dashboard.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| code | path | string | yes | The link's code (or its id). |


Example answer:

```json
{
  "success": true,
  "request_id": "e3lr1",
  "link": {
    "id": 21,
    "code": "k3XbQ9rTzP2m",
    "url": "https://www.app2email.com/book/k3XbQ9rTzP2m",
    "kind": "personal",
    "contact": "61412345678",
    "contact_name": "John",
    "service_id": null,
    "provider_id": null,
    "purpose": "book",
    "booking_id": null,
    "single_use": false,
    "max_uses": 0,
    "uses": 0,
    "expires": "2026-11-18T01:12:09.000Z",
    "revoked": "2026-11-11T02:00:00.000Z",
    "source": "api",
    "created_by": "API key Planner",
    "open_count": 0,
    "last_opened": null,
    "created": "2026-11-11T01:12:09.000Z",
    "state": "revoked"
  },
  "note": "Revoked. The link no longer opens."
}
```


### `POST /bookings/holds`

Keep a free time for a few minutes. Scope: `bookings:manage`. Docs: https://www.app2email.com/docs/api/calendar/create-booking-hold

Scope: `bookings:manage`. Not with a sandbox key. Keeps a free time for `minutes` (1 to 30, default 10) so no one else can book it while the customer decides: it counts as taken in the availability, the calendar and every booking check. The slot is checked like a booking is; 409 `booking_slot_taken` when it is not free. Book it with POST /bookings and `hold` (the `reference`), or release it with DELETE; it frees itself at `expires`. Send an `Idempotency-Key` header to retry safely: the same key and body within 24 hours gets the first answer again (an error does not use the key up).


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| Idempotency-Key | header | string |  | Optional. A unique value for this message or list (eg a UUID). The same request with the same key within 24 hours gets the first answer again, and nothing is sent twice. Ignored by dry runs. |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| service_id | string | yes |  |
| start | string | yes | A free slot of GET /bookings/availability or /bookings/next: Local time in the business time zone, yyyy-MM-ddTHH:mm. |
| provider_id | string |  | Left out (or "any"): the first free staff member who does the service. |
| contact | string |  | The customer, when known. |
| name | string |  |  |
| minutes | integer |  | How long to keep the time. |
| answers_q | object |  | The answers to the service's questions, by question id (see POST /bookings). |
| location_index | integer |  | Which of the service's locations (0-based). Left out: the first. |
| location_value | string |  | The customer's address, for an at-your-address location. |
| addon_ids | array of string |  | The service's add-ons: the time is held as long as they make it. |
| guests | array of object |  | People who come along; on a group service each takes a place. |
| utm | object |  | { source, medium, campaign, term, content }, kept with the booking. |


### `DELETE /bookings/holds/{reference}`

Release a held time. Scope: `bookings:manage`. Docs: https://www.app2email.com/docs/api/calendar/release-booking-hold

Scope: `bookings:manage`. Not with a sandbox key. Frees the time at once. Releasing a time that was already released answers 200 again; one that expired or was booked answers 409 `hold_expired`.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| reference | path | string | yes | The hold's reference, as POST /bookings/holds answered. |


Example answer:

```json
{
  "success": true,
  "request_id": "f2hr3",
  "released": true,
  "hold": {
    "reference": "BK-4HT9XC",
    "status": "released",
    "service_id": "haircut",
    "provider_id": "maria",
    "contact": "61412345678",
    "name": "John",
    "start": "2026-11-09T22:00:00.000Z",
    "end": "2026-11-09T22:30:00.000Z",
    "start_local": "2026-11-10T09:00",
    "end_local": "2026-11-10T09:30",
    "expires": "2026-11-09T04:10:00.000Z",
    "source": "api"
  }
}
```


## Calling


### `GET /calling/settings`

WhatsApp calling settings. Scope: `calls:manage`. Docs: https://www.app2email.com/docs/api/calling/get-call-settings

Meta's settings of the number: calling on or off, call icon, call hours, call-back permission, SIP.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| include_sip_credentials | query | boolean |  | true: the SIP password too (never for a sandbox key). |


Example answer:

```json
{
  "success": true,
  "request_id": "c1g2s",
  "settings": {
    "calling": {
      "status": "ENABLED",
      "call_icon_visibility": "DEFAULT",
      "callback_permission_status": "ENABLED",
      "call_hours": {
        "status": "ENABLED",
        "timezone_id": "Europe/Berlin",
        "weekly_operating_hours": [
          {
            "day_of_week": "MONDAY",
            "open_time": "0900",
            "close_time": "1700"
          }
        ]
      },
      "sip": {
        "status": "DISABLED"
      }
    }
  }
}
```


### `PATCH /calling/settings`

Change the calling settings. Scope: `calls:manage`. Docs: https://www.app2email.com/docs/api/calling/update-call-settings

Passed to Meta as {"calling": {...}}; status in upper case.


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| calling | object | yes | Meta's calling settings object, passed as it is. |
|   status | string |  | ENABLED or DISABLED. |
|   call_icon_visibility | string |  | DEFAULT or DISABLE_ALL. |
|   call_icons | object |  |  |
|   call_hours | object |  |  |
|   callback_permission_status | string |  | ENABLED: a user who calls grants call-back permission. |
|   srtp_key_exchange_protocol | string |  | DTLS or SDES. |
|   sip | object |  |  |
|   video | object |  |  |
|   audio | object |  |  |


Example answer:

```json
{
  "success": true,
  "request_id": "c2h3t",
  "updated": [
    "status",
    "call_icon_visibility"
  ],
  "calling": {
    "status": "ENABLED",
    "call_icon_visibility": "DEFAULT"
  }
}
```


### `POST /calls`

Start, answer, reject or end a WhatsApp call. Scope: `calls:manage`. Docs: https://www.app2email.com/docs/api/calling/manage-call

Meta's call actions with your SDP. Answer an incoming call within 30 to 60 s. Business-initiated calls need the contact's permission and are billed per minute.


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| action | string (connect \| pre_accept \| accept \| reject \| terminate \| media_update) | yes |  |
| to | string |  | connect: the contact's number or business-scoped user id (sent as recipient). |
| recipient | string |  | Instead of to: a business-scoped user id. |
| call_id | string |  | Every action but connect: the call's id (call.incoming / call.status). |
| session | object |  |  |
|   sdp_type | string (offer \| answer) | yes |  |
|   sdp | string | yes | RFC 8866 SDP. |
| biz_opaque_callback_data | string |  |  |
| recording | object |  |  |
|   status | string |  |  |
|   purpose | string |  |  |
|   announcement_language | string |  |  |
| transcription | object |  |  |
|   status | string |  |  |
|   purpose | string |  |  |
|   announcement_language | string |  |  |
| messaging_product | string |  | Meta's body: accepted and ignored. |


Example answer:

```json
{
  "success": true,
  "request_id": "c3i4u",
  "action": "accept",
  "call_id": "wacid.HBgLMTY1MDU1NTEyMzQVAgARGCBBQkNERUY"
}
```


### `GET /calls/permissions/{contact}`

May the number call this contact. Scope: `calls:manage`. Docs: https://www.app2email.com/docs/api/calling/get-call-permission

The contact's call permission and how many calls or permission requests are left.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| contact | path | string | yes | The contact's number with country code, digits only, or their business-scoped user id. |


Example answer:

```json
{
  "success": true,
  "request_id": "c4j5v",
  "contact": "61412345678",
  "permission": {
    "status": "temporary",
    "expires_at": "2026-11-13T01:00:00.000Z"
  },
  "actions": [
    {
      "action_name": "start_call",
      "can_perform_action": true,
      "limits": [
        {
          "time_period": "PT24H",
          "max_allowed": 100,
          "current_usage": 2
        }
      ]
    },
    {
      "action_name": "send_call_permission_request",
      "can_perform_action": false,
      "limits": [
        {
          "time_period": "P1D",
          "max_allowed": 1,
          "current_usage": 1,
          "limit_expiration_time": 1794013200
        }
      ]
    }
  ]
}
```


## Flows


### `GET /flows`

List WhatsApp Flows. Scope: `messages:read or bookings:manage`. Docs: https://www.app2email.com/docs/api/flows/list-flows

Every flow of the WhatsApp Business Account: id, name, status, categories, validation errors. This number's Book-and-Pay Flows also have `key`, `can_send` and `booking_flow` (POST /flows/{key}/send sends them); the first page adds the Book-and-Pay Flows not uploaded yet (no id). Needs 'messages:read' or 'bookings:manage'.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| limit | query | integer |  | 1 to 100. |
| cursor | query | string |  | next_cursor of the previous answer. |


Example answer:

```json
{
  "success": true,
  "request_id": "f1lst",
  "flows": [
    {
      "id": "1234567890123456",
      "name": "appointment_booking",
      "status": "DRAFT",
      "categories": [
        "APPOINTMENT_BOOKING"
      ],
      "validation_errors": []
    },
    {
      "id": "1234567890123457",
      "name": "feedback",
      "status": "PUBLISHED",
      "categories": [
        "SURVEY"
      ],
      "validation_errors": []
    },
    {
      "id": "1234567890123458",
      "name": "Appointment booking - +61 2 9876 5432",
      "status": "PUBLISHED",
      "categories": [
        "APPOINTMENT_BOOKING"
      ],
      "validation_errors": [],
      "key": "booking",
      "can_send": true,
      "booking_flow": {
        "key": "booking",
        "name": "Appointment booking",
        "kind": "booking",
        "enabled": true,
        "is_default": true,
        "trigger_keywords": [],
        "id": "1234567890123458",
        "status": "published",
        "can_send": true,
        "health": "AVAILABLE",
        "last_published_at": "2026-11-06T00:00:00Z",
        "updated_at": "2026-11-06T00:00:00.000Z"
      }
    }
  ],
  "next_cursor": null,
  "count": 3,
  "enabled": true,
  "note": "A Flow with a key is one of this number's Book-and-Pay Flows: POST /v1/{number}/flows/{key}/send sends it to a contact inside their 24 hour window (can_send), and its trigger words send it."
}
```


### `POST /flows`

Create a flow (draft, or published at once). Scope: `templates:manage`. Docs: https://www.app2email.com/docs/api/flows/create-flow

Needs 'templates:manage'. A draft; with flow_json and publish: true it is published at once (cannot be undone). WABA-wide: every number on this WhatsApp Business Account shares its flows.


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| name | string | yes | Internal name; customers do not see it. |
| categories | array of string | yes |  |
| flow_json | object |  | The Flow JSON (version, screens), as an object or a string. Max 10 MB. |
| publish | boolean |  | true (with flow_json): published at once. Cannot be undone. |
| clone_flow_id | string |  | Copy this flow (of the same account). |
| endpoint_uri | string |  | https URL of your data endpoint, for flows that use one. |


### `GET /flows/{id}`

One flow: status, validation errors, health. Scope: `messages:read`. Docs: https://www.app2email.com/docs/api/flows/get-flow

Status, categories, validation errors, Flow JSON version, endpoint, and whether it can be sent (health_status).


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The flow's id (digits). |


Example answer:

```json
{
  "success": true,
  "request_id": "f1get",
  "flow": {
    "id": "1234567890123456",
    "name": "appointment_booking",
    "status": "DRAFT",
    "categories": [
      "APPOINTMENT_BOOKING"
    ],
    "validation_errors": [],
    "json_version": "7.2",
    "health_status": {
      "can_send_message": "AVAILABLE",
      "entities": [
        {
          "entity_type": "FLOW",
          "id": "1234567890123456",
          "can_send_message": "AVAILABLE"
        }
      ]
    }
  }
}
```


### `PATCH /flows/{id}`

Change a flow's name, categories or endpoint. Scope: `templates:manage`. Docs: https://www.app2email.com/docs/api/flows/update-flow

Needs 'templates:manage'. The Flow JSON: PUT /flows/{id}/json. A published flow goes back to DRAFT until you publish it again; messages already sent keep the old version. WABA-wide: every number on this WhatsApp Business Account shares its flows.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The flow's id (digits). |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| name | string |  |  |
| categories | array of string |  |  |
| endpoint_uri | string |  |  |
| application_id | string |  | The Meta app connected to a flow with an endpoint. |


Example answer:

```json
{
  "success": true,
  "request_id": "f1upd",
  "flow_id": "1234567890123456",
  "changed": [
    "name"
  ],
  "note": "The flow was PUBLISHED: it is a DRAFT again until you publish it (POST /flows/1234567890123456/publish); messages already sent keep the old version."
}
```


### `DELETE /flows/{id}`

Delete a draft flow. Scope: `templates:manage`. Docs: https://www.app2email.com/docs/api/flows/delete-flow

Needs 'templates:manage'. Drafts only; deprecate a published flow instead. WABA-wide: every number on this WhatsApp Business Account shares its flows.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The flow's id (digits). |


Example answer:

```json
{
  "success": true,
  "request_id": "f1del",
  "deleted": "1234567890123456",
  "name": "appointment_booking"
}
```


### `GET /flows/{id}/json`

A flow's Flow JSON. Scope: `messages:read`. Docs: https://www.app2email.com/docs/api/flows/get-flow-json

The flow.json WhatsApp keeps for the flow.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The flow's id (digits). |


Example answer:

```json
{
  "success": true,
  "request_id": "f1jsn",
  "flow_id": "1234567890123456",
  "flow_json": {
    "version": "7.2",
    "screens": [
      {
        "id": "WELCOME",
        "title": "Welcome",
        "terminal": true,
        "success": true,
        "data": {},
        "layout": {
          "type": "SingleColumnLayout",
          "children": [
            {
              "type": "TextHeading",
              "text": "Book a visit"
            },
            {
              "type": "Footer",
              "label": "Done",
              "on-click-action": {
                "name": "complete",
                "payload": {}
              }
            }
          ]
        }
      }
    ]
  }
}
```


### `PUT /flows/{id}/json`

Replace a flow's Flow JSON. Scope: `templates:manage`. Docs: https://www.app2email.com/docs/api/flows/update-flow-json

Needs 'templates:manage'. The body is the Flow JSON (or {"flow_json": {...}}), max 10 MB; the answer lists WhatsApp's validation errors. A published flow goes back to DRAFT until you publish it again; messages already sent keep the old version. WABA-wide: every number on this WhatsApp Business Account shares its flows.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The flow's id (digits). |


Example answer:

```json
{
  "success": true,
  "request_id": "f1put",
  "flow_id": "1234567890123456",
  "validation_errors": [],
  "note": "WhatsApp found no errors. Publish with POST /flows/1234567890123456/publish (cannot be undone)."
}
```


### `POST /flows/{id}/publish`

Publish a flow (cannot be undone). Scope: `templates:manage`. Docs: https://www.app2email.com/docs/api/flows/publish-flow

Needs 'templates:manage'. A draft without validation errors. Afterwards it cannot be deleted (deprecate it instead); a change puts it back to DRAFT until published again. WABA-wide: every number on this WhatsApp Business Account shares its flows.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The flow's id (digits). |


Example answer:

```json
{
  "success": true,
  "request_id": "f1pub",
  "flow_id": "1234567890123456",
  "name": "appointment_booking",
  "previous_status": "DRAFT",
  "status": "PUBLISHED",
  "note": "Published for every number on this WhatsApp Business Account. It cannot be deleted (deprecate it instead). Changing its name, categories, endpoint or Flow JSON puts it back to DRAFT until you publish again; messages already sent keep the old version."
}
```


### `POST /flows/{id}/deprecate`

Deprecate a published flow (cannot be undone). Scope: `templates:manage`. Docs: https://www.app2email.com/docs/api/flows/deprecate-flow

Needs 'templates:manage'. It can no longer be sent or opened. WABA-wide: every number on this WhatsApp Business Account shares its flows.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The flow's id (digits). |


Example answer:

```json
{
  "success": true,
  "request_id": "f1dep",
  "flow_id": "1234567890123456",
  "name": "appointment_booking",
  "previous_status": "PUBLISHED",
  "status": "DEPRECATED",
  "note": "Deprecated: it can no longer be sent or opened, on every number of this WhatsApp Business Account. This cannot be undone."
}
```


### `GET /flows/{id}/preview`

A public preview link of a flow (30 days). Scope: `messages:read`. Docs: https://www.app2email.com/docs/api/flows/get-flow-preview

Anyone with the link can open it, also in an iframe. A new link: POST.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The flow's id (digits). |


Example answer:

```json
{
  "success": true,
  "request_id": "f1prv",
  "flow_id": "1234567890123456",
  "preview_url": "https://business.facebook.com/wa/manage/flows/1234567890123456/preview/?token=b9d6a1c2",
  "expires_at": "2026-12-06T01:00:00+0000",
  "note": "Anyone with the link can see the flow until it expires (30 days). Add &interactive=true to try it."
}
```


### `POST /flows/{id}/preview`

A new preview link of a flow (the old one stops working). Scope: `templates:manage`. Docs: https://www.app2email.com/docs/api/flows/renew-flow-preview

Needs 'templates:manage'. Meta's preview.invalidate(true): the old link stops working at once.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The flow's id (digits). |


Example answer:

```json
{
  "success": true,
  "request_id": "f1prn",
  "flow_id": "1234567890123456",
  "preview_url": "https://business.facebook.com/wa/manage/flows/1234567890123456/preview/?token=e4f7c3a9",
  "expires_at": "2026-12-06T01:00:00+0000",
  "note": "A new link; the old one no longer works. Anyone with the link can see the flow until it expires (30 days). Add &interactive=true to try it."
}
```


### `GET /flows/encryption-key`

The number's public key for flows with a data endpoint. Scope: `messages:read`. Docs: https://www.app2email.com/docs/api/flows/get-flow-encryption-key

This number only (each number has its own key). signature_status MISMATCH: set the key again. set_by: bookings when it is the key Book-and-Pay made for its Flows.


Example answer:

```json
{
  "success": true,
  "request_id": "f2key",
  "public_key": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAx...\n-----END PUBLIC KEY-----",
  "signature_status": "VALID",
  "set_by": "other",
  "note": "This number's key (each number has its own)."
}
```


### `PUT /flows/encryption-key`

Set the number's public key for flow endpoints. Scope: `templates:manage`. Docs: https://www.app2email.com/docs/api/flows/set-flow-encryption-key

Needs 'templates:manage'. A 2048-bit RSA public key, PEM; a private key is refused unsent. This number only. 409 `encryption_key_managed` while Book-and-Pay has its key for the number (one key per number at WhatsApp).


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| public_key | string | yes | A 2048-bit RSA public key, PEM. Never the private key. |


Example answer:

```json
{
  "success": true,
  "request_id": "f2set",
  "note": "Set for this number only (each number of the WhatsApp Business Account has its own). Your endpoint decrypts with the private key."
}
```


## Number


### `GET /health`

Number health: can it send, quality, limit, name status. Scope: `messages:read`. Docs: https://www.app2email.com/docs/api/number/get-number-health

WhatsApp's health_status and the number's fields (quality, messaging limit, throughput, display name review, account mode). Kept 60 s.


Example answer:

```json
{
  "success": true,
  "request_id": "h7q2m",
  "health": {
    "can_send_message": "AVAILABLE",
    "entities": [
      {
        "entity_type": "PHONE_NUMBER",
        "id": "106540352242922",
        "can_send_message": "AVAILABLE"
      },
      {
        "entity_type": "WABA",
        "id": "102290129340398",
        "can_send_message": "AVAILABLE"
      }
    ],
    "display_phone_number": "+49 76659 348270",
    "verified_name": "Lucky Shrub",
    "quality_rating": "GREEN",
    "messaging_limit": "TIER_2K",
    "throughput": "STANDARD",
    "status": "CONNECTED",
    "name_status": "APPROVED",
    "code_verification_status": "VERIFIED",
    "account_mode": "LIVE",
    "is_official_business_account": false,
    "coexistence": false
  },
  "fetched_at": "2026-11-06T01:00:00.000Z"
}
```


### `PUT /settings/identity-check`

Turn WhatsApp's identity change check on or off. Scope: `settings:manage`. Docs: https://www.app2email.com/docs/api/number/set-identity-check

On: webhooks carry identity_key_hash, and a send with recipient_identity_key_hash is only delivered while it matches (else failed, code 137000).


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| enabled | boolean | yes |  |


Example answer:

```json
{
  "success": true,
  "request_id": "i2k7d",
  "identity_check": {
    "enabled": true
  }
}
```


### `GET /profile`

The WhatsApp business profile. Scope: `messages:read`. Docs: https://www.app2email.com/docs/api/number/get-business-profile

About, address, description, email, websites, vertical and the photo link, as WhatsApp users see them.


Example answer:

```json
{
  "success": true,
  "request_id": "p4m1x",
  "profile": {
    "about": "Plants and flowers, delivered",
    "address": "1 Garden Lane, Berlin",
    "description": "Family florist since 1998.",
    "email": "hello@luckyshrub.example",
    "profile_picture_url": "https://pps.whatsapp.net/v/t61.24694-24/123_n.jpg",
    "websites": [
      "https://luckyshrub.example"
    ],
    "vertical": "RETAIL"
  }
}
```


### `PATCH /profile`

Change the WhatsApp business profile. Scope: `settings:manage`. Docs: https://www.app2email.com/docs/api/number/update-business-profile

Fields left out stay as they are. Meta's own body (with messaging_product, profile_picture_handle) works unchanged.


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| about | string |  |  |
| address | string |  |  |
| description | string |  |  |
| email | string |  |  |
| websites | array of string |  |  |
| vertical | string |  |  |
| profile_picture_handle | string |  | A Resumable Upload handle (Meta's body). PUT /profile/photo makes one from a link. |


Example answer:

```json
{
  "success": true,
  "request_id": "p5n2y",
  "updated": [
    "about",
    "websites"
  ],
  "profile": {
    "about": "Plants and flowers, delivered same day",
    "websites": [
      "https://luckyshrub.example",
      "https://luckyshrub.example/shop"
    ]
  }
}
```


### `PUT /profile/photo`

Change the profile photo from a public link. Scope: `settings:manage`. Docs: https://www.app2email.com/docs/api/number/set-profile-photo

app2email downloads the image (JPG or PNG, up to 5 MB; 640x640 px suggested) and uploads it to WhatsApp.


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| link | string | yes | Public http(s) link to a JPG or PNG image, up to 5 MB. |


Example answer:

```json
{
  "success": true,
  "request_id": "f8a3c",
  "updated": [
    "photo"
  ],
  "link": "https://luckyshrub.example/logo.png"
}
```


### `PUT /profile/display-name`

Submit a new display name for Meta's review. Scope: `settings:manage`. Docs: https://www.app2email.com/docs/api/number/set-display-name

Answer 202. GET /health shows new_name_status. After approval, number.updated (change display_name, next_step reconnect): press Reconnect on the dashboard within 14 days.


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| name | string | yes |  |


Example answer:

```json
{
  "success": true,
  "request_id": "d1s9w",
  "display_name": {
    "current": "Lucky Shrub",
    "requested": "Lucky Shrub Florist",
    "status": "PENDING_REVIEW"
  },
  "next_step": "wait_for_review",
  "note": "When Meta approves the name, the number.updated event (change display_name, next_step reconnect) is sent: then press Reconnect on the dashboard within 14 days."
}
```


### `GET /profile/official-business-account`

Official Business Account (blue tick) status. Scope: `messages:read`. Docs: https://www.app2email.com/docs/api/number/get-official-business-account

The state of the number's Official Business Account request.


Example answer:

```json
{
  "success": true,
  "request_id": "o2b5a",
  "official_business_account": {
    "status": "UNDER_REVIEW",
    "status_message": "Your request is being reviewed."
  }
}
```


### `POST /profile/official-business-account`

Request an Official Business Account (blue tick). Scope: `settings:manage`. Docs: https://www.app2email.com/docs/api/number/request-official-business-account

Answer 202. Meta decides on notability; supporting_links: 5 to 10 articles about the business.


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| business_website_url | string | yes |  |
| primary_country_of_operation | string | yes |  |
| primary_language | string |  |  |
| parent_business_or_brand | string |  |  |
| supporting_links | array of string |  | Articles about the business (not paid or own content). |
| additional_supporting_information | string |  |  |


Example answer:

```json
{
  "success": true,
  "request_id": "o3c6b",
  "official_business_account": {
    "status": "PENDING",
    "status_message": "Request submitted."
  },
  "tracking_id": "98765432101234"
}
```


### `GET /profile/india-compliance`

India business compliance information. Scope: `messages:read`. Docs: https://www.app2email.com/docs/api/number/get-india-compliance

The legal entity, grievance officer and customer care contacts (numbers in India).


Example answer:

```json
{
  "success": true,
  "request_id": "c7i1n",
  "india_compliance": {
    "entity_name": "Lucky Shrub Pvt Ltd",
    "entity_type": "PRIVATE_COMPANY",
    "grievance_officer_details": {
      "name": "A. Rao",
      "email": "grievance@luckyshrub.example",
      "mobile_number": "+919812345678"
    },
    "customer_care_details": {
      "email": "care@luckyshrub.example",
      "landline_number": "+912212345678"
    }
  }
}
```


### `PUT /profile/india-compliance`

Set the India business compliance information. Scope: `settings:manage`. Docs: https://www.app2email.com/docs/api/number/set-india-compliance

Replaces it. Needed for numbers that message users in India.


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| entity_name | string | yes |  |
| entity_type | string (LIMITED_LIABILITY_PARTNERSHIP \| SOLE_PROPRIETORSHIP \| PARTNERSHIP \| PUBLIC_COMPANY \| PRIVATE_COMPANY \| OTHER) | yes |  |
| entity_type_custom | string |  | Needed with entity_type OTHER, refused with any other. |
| is_registered | boolean |  | Only with entity_type OTHER or PARTNERSHIP. |
| grievance_officer_details | object | yes |  |
|   name | string | yes |  |
|   email | string | yes |  |
|   mobile_number | string |  |  |
|   landline_number | string |  |  |
| customer_care_details | object | yes |  |
|   email | string | yes |  |
|   mobile_number | string |  |  |
|   landline_number | string |  |  |


Example answer:

```json
{
  "success": true,
  "request_id": "c8j2o",
  "india_compliance": {
    "entity_name": "Lucky Shrub Pvt Ltd",
    "entity_type": "PRIVATE_COMPANY",
    "grievance_officer_details": {
      "name": "A. Rao",
      "email": "grievance@luckyshrub.example",
      "mobile_number": "+919812345678"
    },
    "customer_care_details": {
      "email": "care@luckyshrub.example",
      "landline_number": "+912212345678"
    }
  }
}
```


### `GET /username`

The business username. Scope: `messages:read`. Docs: https://www.app2email.com/docs/api/number/get-username

status none: the number has no username.


Example answer:

```json
{
  "success": true,
  "request_id": "u1n4m",
  "username": "luckyshrub",
  "status": "approved"
}
```


### `PUT /username`

Adopt or change the business username. Scope: `settings:manage`. Docs: https://www.app2email.com/docs/api/number/set-username

3 to 35 characters of a-z, 0-9, '.', '_', with a letter. At most 2 changes in 14 days (422 username_change_limit).


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| username | string | yes |  |
| transfer_action | string (none \| force_transfer) |  | force_transfer: move it here from another number of the same business. |


Example answer:

```json
{
  "success": true,
  "request_id": "u2o5n",
  "username": "luckyshrub",
  "status": "reserved"
}
```


### `DELETE /username`

Remove the business username. Scope: `settings:manage`. Docs: https://www.app2email.com/docs/api/number/delete-username

Removing does not reset the 14-day change limit.


Example answer:

```json
{
  "success": true,
  "request_id": "u3p6o",
  "deleted": true
}
```


### `GET /username/suggestions`

Usernames reserved for the business. Scope: `messages:read`. Docs: https://www.app2email.com/docs/api/number/get-username-suggestions

Reserved names have a higher chance of approval.


Example answer:

```json
{
  "success": true,
  "request_id": "u4q7p",
  "suggestions": [
    "luckyshrub",
    "lucky.shrub"
  ],
  "count": 2
}
```


### `GET /settings/conversation-starters`

Ice breakers, commands and welcome message. Scope: `messages:read`. Docs: https://www.app2email.com/docs/api/number/get-conversation-starters

What WhatsApp users see when they open a chat or type '/'.


Example answer:

```json
{
  "success": true,
  "request_id": "s1t8q",
  "conversation_starters": {
    "prompts": [
      "Track my order",
      "Opening hours"
    ],
    "commands": [
      {
        "name": "order",
        "description": "Where is my order?"
      }
    ]
  }
}
```


### `PUT /settings/conversation-starters`

Set ice breakers, commands or the welcome message. Scope: `settings:manage`. Docs: https://www.app2email.com/docs/api/number/set-conversation-starters

Replaces the parts given. A tap or a command arrives as a normal text message (forwarded by email as usual).


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| prompts | array of string |  | Ice breakers. No emoji. [] removes them. |
| commands | array of object |  | Slash commands. No emoji. [] removes them. Meta's command_name / command_description work too. |
| welcome_message | boolean |  | Meta's enable_welcome_message: a request_welcome message when a user opens a chat for the first time. |


Example answer:

```json
{
  "success": true,
  "request_id": "s2u9r",
  "conversation_starters": {
    "prompts": [
      "Track my order",
      "Opening hours"
    ],
    "commands": [
      {
        "name": "order",
        "description": "Where is my order?"
      }
    ]
  }
}
```


### `GET /qr-codes`

QR codes and short links. Scope: `messages:read`. Docs: https://www.app2email.com/docs/api/number/list-qr-codes

Up to 2,000 per number. Codes never expire; WhatsApp gives no scan counts.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| image | query | string (svg \| png) |  | Also give each code's image link (qr_image_url) in this format. |
| limit | query | integer |  | How many (1 to 200, default 50). |
| cursor | query | string |  | The next_cursor of the previous answer. |


Example answer:

```json
{
  "success": true,
  "request_id": "q1r2s",
  "qr_codes": [
    {
      "code": "4O4YGZEG3RIVE1",
      "prefilled_message": "Hi, I saw your poster",
      "deep_link_url": "https://wa.me/message/4O4YGZEG3RIVE1",
      "qr_image_url": "https://scontent.xx.fbcdn.net/m1/v/t6/qr_4O4YGZEG3RIVE1.png"
    }
  ],
  "count": 1
}
```


### `POST /qr-codes`

Create a QR code and wa.me short link. Scope: `settings:manage`. Docs: https://www.app2email.com/docs/api/number/create-qr-code

The chat opens with prefilled_message (up to 140 characters). Answer 201.


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| prefilled_message | string | yes |  |
| image | string (svg \| png) |  |  |


### `GET /qr-codes/{code}`

One QR code. Scope: `messages:read`. Docs: https://www.app2email.com/docs/api/number/get-qr-code

With ?image=svg or png, its image link too.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| code | path | string | yes | The QR code's code (14 characters), as in the list. |
| image | query | string (svg \| png) |  | Also give each code's image link (qr_image_url) in this format. |


Example answer:

```json
{
  "success": true,
  "request_id": "q3t4u",
  "qr_code": {
    "code": "4O4YGZEG3RIVE1",
    "prefilled_message": "Hi, I saw your poster",
    "deep_link_url": "https://wa.me/message/4O4YGZEG3RIVE1",
    "qr_image_url": "https://scontent.xx.fbcdn.net/m1/v/t6/qr_4O4YGZEG3RIVE1.png"
  }
}
```


### `PATCH /qr-codes/{code}`

Change a QR code's prefilled message. Scope: `settings:manage`. Docs: https://www.app2email.com/docs/api/number/update-qr-code

The code, link and image stay the same.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| code | path | string | yes | The QR code's code (14 characters), as in the list. |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| prefilled_message | string | yes |  |


Example answer:

```json
{
  "success": true,
  "request_id": "q4u5v",
  "qr_code": {
    "code": "4O4YGZEG3RIVE1",
    "prefilled_message": "Hi, I saw your new poster",
    "deep_link_url": "https://wa.me/message/4O4YGZEG3RIVE1"
  }
}
```


### `DELETE /qr-codes/{code}`

Delete a QR code and its short link. Scope: `settings:manage`. Docs: https://www.app2email.com/docs/api/number/delete-qr-code

Printed codes and shared links stop working.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| code | path | string | yes | The QR code's code (14 characters), as in the list. |


Example answer:

```json
{
  "success": true,
  "request_id": "q5v6w",
  "deleted": true,
  "code": "4O4YGZEG3RIVE1"
}
```


### `GET /settings/commerce`

Cart and catalog icon on or off. Scope: `messages:read`. Docs: https://www.app2email.com/docs/api/number/get-commerce-settings

WhatsApp's defaults: cart on, catalog icon hidden.


Example answer:

```json
{
  "success": true,
  "request_id": "m1c2a",
  "commerce": {
    "cart_enabled": true,
    "catalog_visible": false
  }
}
```


### `PUT /settings/commerce`

Turn the cart or the catalog icon on or off. Scope: `settings:manage`. Docs: https://www.app2email.com/docs/api/number/set-commerce-settings

One or both. Meta's is_cart_enabled / is_catalog_visible work too.


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| cart_enabled | boolean |  |  |
| catalog_visible | boolean |  |  |


Example answer:

```json
{
  "success": true,
  "request_id": "m2d3b",
  "commerce": {
    "catalog_visible": true
  }
}
```


### `GET /catalog`

The connected product catalog. Scope: `messages:read`. Docs: https://www.app2email.com/docs/api/number/get-catalog

Connected to the WhatsApp Business Account, so to every number on it. null: none.


Example answer:

```json
{
  "success": true,
  "request_id": "g1h2i",
  "catalog": {
    "id": "1043215907766185",
    "name": "Lucky Shrub plants"
  },
  "connected": true
}
```


### `PUT /catalog`

Connect a product catalog. Scope: `settings:manage`. Docs: https://www.app2email.com/docs/api/number/connect-catalog

A catalog from Commerce Manager; the WABA-wide link for product messages.


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| catalog_id | string | yes |  |


Example answer:

```json
{
  "success": true,
  "request_id": "g2i3j",
  "catalog": {
    "id": "1043215907766185"
  },
  "connected": true
}
```


## Payments


### `GET /payments`

The payments, newest first. Scope: `bookings:manage or messages:read`. Docs: https://www.app2email.com/docs/api/payments/list-payments

Scope: `bookings:manage` (or `messages:read`). The payments of appointments, package purchases and payment requests. Filter by `booking` (id or reference), `contact`, `status` and `kind`. Page with `next_cursor`.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| booking | query | string |  | Only this appointment's payments (id or BK- reference). |
| contact | query | string |  | Only this customer's payments. |
| status | query | string (pending \| paid \| partly_refunded \| refunded \| failed \| expired \| cancelled) |  | Only this status. |
| kind | query | string (booking \| request \| package \| ticket) |  | Only this kind. |
| limit | query | integer |  | How many (1 to 200, default 50). |
| cursor | query | string |  | The next_cursor of the previous answer, unchanged. Leave out for the first page. |


Example answer:

```json
{
  "success": true,
  "request_id": "p1ls2",
  "payments": [
    {
      "id": 15,
      "kind": "booking",
      "status": "paid",
      "provider": "stripe",
      "amount": 40.0,
      "amount_label": "$40.00",
      "full_label": "$40.00",
      "discount_label": "",
      "coupon_code": "",
      "currency": "USD",
      "refunded": 0.0,
      "refunded_label": "",
      "description": "Haircut",
      "contact": "61412345678",
      "payer_name": "John Smith",
      "appointment_id": 42,
      "booking_reference": "BK-7Q3M2A",
      "package_purchase_id": null,
      "checkout_url": "",
      "link_url": "",
      "last_error": "",
      "paid": "2026-11-11T01:15:00.000Z",
      "refunded_at": null,
      "created": "2026-11-11T01:10:00.000Z"
    }
  ],
  "next_cursor": null,
  "count": 1,
  "currency": "USD"
}
```


### `GET /payments/{id}`

One payment. Scope: `bookings:manage or messages:read`. Docs: https://www.app2email.com/docs/api/payments/get-payment

Scope: `bookings:manage` (or `messages:read`). No provider key or secret is ever in the answer.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The payment's id. |


Example answer:

```json
{
  "success": true,
  "request_id": "p2gt3",
  "payment": {
    "id": 15,
    "kind": "booking",
    "status": "paid",
    "provider": "stripe",
    "amount": 40.0,
    "amount_label": "$40.00",
    "full_label": "$40.00",
    "discount_label": "",
    "coupon_code": "",
    "currency": "USD",
    "refunded": 0.0,
    "refunded_label": "",
    "description": "Haircut",
    "contact": "61412345678",
    "payer_name": "John Smith",
    "appointment_id": 42,
    "booking_reference": "BK-7Q3M2A",
    "package_purchase_id": null,
    "checkout_url": "",
    "link_url": "",
    "last_error": "",
    "paid": "2026-11-11T01:15:00.000Z",
    "refunded_at": null,
    "created": "2026-11-11T01:10:00.000Z"
  }
}
```


### `POST /payments/links`

Ask a customer to pay an amount. Scope: `bookings:manage`. Docs: https://www.app2email.com/docs/api/payments/create-payment-link

Scope: `bookings:manage`. Not with a sandbox key. Makes a one-off payment request and the page where the customer pays (the business's own Stripe or PayPal). With `send` true and the customer inside their 24 hour window they also get it on WhatsApp with a Pay button; otherwise send the `url` yourself. 409 `payments_not_connected` when no provider is connected. `payment.paid` is sent when it is paid. Send an `Idempotency-Key` header to retry safely: the same key and body within 24 hours gets the first answer again (an error does not use the key up).


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| Idempotency-Key | header | string |  | Optional. A unique value for this message or list (eg a UUID). The same request with the same key within 24 hours gets the first answer again, and nothing is sent twice. Ignored by dry runs. |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| contact | string | yes | The customer's WhatsApp number with country code, digits only, or their business-scoped user id. |
| amount | number | yes | In the business's payment currency (config.payments.currency). |
| description | string | yes | Shown to the customer. |
| booking_id | string |  | The appointment it is for (id or reference). |
| name | string |  |  |
| send | boolean |  | Also send the link to the customer on WhatsApp (a message with a Pay button, only inside their 24 hour window). |


### `POST /payments/{id}/refund`

Refund a payment, in full or a part. Scope: `bookings:manage`. Docs: https://www.app2email.com/docs/api/payments/refund-payment

Scope: `bookings:manage`. Not with a sandbox key. Sends real money back through the business's own provider; it cannot be undone. `amount` is a part in the payment's currency; left out, everything that is left. A full refund of an appointment's payment sets its `payment.status` to refunded. `booking.refunded` is sent. 409 `refund_not_possible`, 502 `payment_provider_error`. Send an `Idempotency-Key` header to retry safely: the same key and body within 24 hours gets the first answer again (an error does not use the key up). For a payment of kind `ticket` use `POST /tickets/orders/{id}/refund` instead: it also ends the tickets.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The payment's id. |
| Idempotency-Key | header | string |  | Optional. A unique value for this message or list (eg a UUID). The same request with the same key within 24 hours gets the first answer again, and nothing is sent twice. Ignored by dry runs. |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| amount | number |  | A part of the money, in the payment's currency. Left out: everything that is left. |


Example answer:

```json
{
  "success": true,
  "request_id": "p4rf5",
  "payment": {
    "id": 15,
    "kind": "booking",
    "status": "partly_refunded",
    "provider": "stripe",
    "amount": 40.0,
    "amount_label": "$40.00",
    "full_label": "$40.00",
    "discount_label": "",
    "coupon_code": "",
    "currency": "USD",
    "refunded": 10.0,
    "refunded_label": "$10.00",
    "description": "Haircut",
    "contact": "61412345678",
    "payer_name": "John Smith",
    "appointment_id": 42,
    "booking_reference": "BK-7Q3M2A",
    "package_purchase_id": null,
    "checkout_url": "",
    "link_url": "",
    "last_error": "",
    "paid": "2026-11-11T01:15:00.000Z",
    "refunded_at": null,
    "created": "2026-11-11T01:10:00.000Z"
  },
  "note": "Refunded through the payment provider. booking.refunded is sent."
}
```


### `POST /bookings/{id}/payment`

Record a payment taken outside app2email. Scope: `bookings:manage`. Docs: https://www.app2email.com/docs/api/payments/set-booking-payment

Scope: `bookings:manage`. Not with a sandbox key. The business's own record: `paid` (cash, a terminal), `waived` (nothing to pay) or `due` (still expected). Nothing is charged or refunded; online payments are recorded by the provider. The booking's `payment` shows the result.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The booking's id, or its reference (BK-XXXXXX). |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| status | string (paid \| waived \| due) | yes | paid: taken outside app2email (cash, a terminal). waived: nothing to pay. due: still expected (the service's price is the amount when none is recorded). |


Example answer:

```json
{
  "success": true,
  "request_id": "p5bs6",
  "booking": {
    "id": 42,
    "reference": "BK-7Q3M2A",
    "status": "confirmed",
    "payment": {
      "status": "paid",
      "due": 0.0,
      "paid": 0.0,
      "currency": "USD"
    }
  }
}
```


### `GET /bookings/packages`

The prepaid packages on sale. Scope: `bookings:manage or messages:read`. Docs: https://www.app2email.com/docs/api/payments/list-packages

Scope: `bookings:manage` (or `messages:read`). The enabled packages of the business (config.payments.packages) with their price and the services they cover. Customers buy them on the online booking page; POST /bookings/packages/grant gives one without a payment.


Example answer:

```json
{
  "success": true,
  "request_id": "p6pk7",
  "packages": [
    {
      "id": "ten-pack",
      "name": "10 sessions",
      "description": "",
      "sessions": 10,
      "price_amount": 400.0,
      "price_label": "$400.00",
      "valid_days": 365,
      "services": []
    }
  ],
  "count": 1,
  "currency": "USD"
}
```


### `GET /bookings/packages/purchases`

The packages customers hold. Scope: `bookings:manage or messages:read`. Docs: https://www.app2email.com/docs/api/payments/list-package-purchases

Scope: `bookings:manage` (or `messages:read`). Purchases and grants, newest first. `status=live` = active with sessions left.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| contact | query | string |  | Only this customer's. |
| status | query | string (live \| pending \| active \| used_up \| expired \| refunded \| cancelled) |  | live, or one status. |
| limit | query | integer |  | How many (1 to 200, default 50). |


Example answer:

```json
{
  "success": true,
  "request_id": "p7pp8",
  "purchases": [
    {
      "id": 5,
      "contact": "61412345678",
      "contact_name": "John Smith",
      "package_id": "ten-pack",
      "package_name": "10 sessions",
      "services": [],
      "sessions_total": 10,
      "sessions_used": 2,
      "sessions_left": 8,
      "expires": "2027-11-11T01:15:00.000Z",
      "status": "active",
      "payment_id": 17,
      "created": "2026-11-11T01:15:00.000Z"
    }
  ],
  "count": 1
}
```


### `POST /bookings/packages/grant`

Give a customer a package without a payment. Scope: `bookings:manage`. Docs: https://www.app2email.com/docs/api/payments/grant-package

Scope: `bookings:manage`. Not with a sandbox key. Makes an active purchase of a package on sale (`sessions` overrides its session count). `package.purchased` is sent with `granted: true`. Send an `Idempotency-Key` header to retry safely: the same key and body within 24 hours gets the first answer again (an error does not use the key up).


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| Idempotency-Key | header | string |  | Optional. A unique value for this message or list (eg a UUID). The same request with the same key within 24 hours gets the first answer again, and nothing is sent twice. Ignored by dry runs. |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| contact | string | yes |  |
| package_id | string | yes | One of GET /bookings/packages. |
| sessions | integer |  | Default: the package's sessions. |
| name | string |  |  |


### `GET /bookings/customers`

The customers with appointments. Scope: `bookings:manage or messages:read`. Docs: https://www.app2email.com/docs/api/payments/list-booking-customers

Scope: `bookings:manage` (or `messages:read`). The people who have appointments, newest activity first, with visits, no-shows, upcoming count, packages left and the total paid. `q` searches name, e-mail and number; `tag` filters by a contact tag. Page with `next_cursor`.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| q | query | string |  | Name, e-mail or number contains this. |
| tag | query | string |  | Only contacts with this tag. |
| sort | query | string (recent \| name \| visits) |  | recent (default), name or visits. |
| limit | query | integer |  | How many (1 to 200, default 50). |
| cursor | query | string |  | The next_cursor of the previous answer, unchanged. Leave out for the first page. |


Example answer:

```json
{
  "success": true,
  "request_id": "c1cl0",
  "customers": [
    {
      "contact": "61412345678",
      "name": "John Smith",
      "email": "john@example.com",
      "tags": [
        "vip"
      ],
      "visits": 6,
      "no_shows": 0,
      "upcoming": 1,
      "last_visit": "2026-10-20T23:00:00.000Z",
      "next_start": "2026-11-12T23:00:00.000Z",
      "packages_left": 8,
      "total_paid_label": "$240.00"
    }
  ],
  "next_cursor": null,
  "count": 1
}
```


### `GET /bookings/customers/{contact}`

A customer's whole profile. Scope: `bookings:manage or messages:read`. Docs: https://www.app2email.com/docs/api/payments/get-customer-profile

Scope: `bookings:manage` (or `messages:read`). Contact details and tags, upcoming and past appointments, internal notes and reminders, packages, payments, stats and the last 20 messages: one call for an agent that is about to talk to the customer.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| contact | path | string | yes | The customer: number with country code, or business-scoped user id. |


Example answer:

```json
{
  "success": true,
  "request_id": "c2cg1",
  "customer": {
    "contact": "61412345678",
    "name": "John Smith",
    "email": "john@example.com",
    "tags": [
      "vip"
    ]
  },
  "stats": {
    "visits": 6,
    "no_shows": 0,
    "cancellations": 1,
    "total_paid_label": "$240.00"
  },
  "upcoming": [],
  "past": [],
  "notes": [
    {
      "id": 7,
      "contact": "61412345678",
      "appointment_id": 42,
      "booking_reference": "BK-7Q3M2A",
      "body": "Prefers the window seat.",
      "author": "API key Planner",
      "author_kind": "api",
      "pinned": false,
      "remind_at": null,
      "created": "2026-11-11T01:12:09.000Z",
      "updated": "2026-11-11T01:12:09.000Z"
    }
  ],
  "reminders": [],
  "packages": [
    {
      "id": 5,
      "contact": "61412345678",
      "contact_name": "John Smith",
      "package_id": "ten-pack",
      "package_name": "10 sessions",
      "services": [],
      "sessions_total": 10,
      "sessions_used": 2,
      "sessions_left": 8,
      "expires": "2027-11-11T01:15:00.000Z",
      "status": "active",
      "payment_id": 17,
      "created": "2026-11-11T01:15:00.000Z"
    }
  ],
  "payments": [
    {
      "id": 15,
      "kind": "booking",
      "status": "paid",
      "provider": "stripe",
      "amount": 40.0,
      "amount_label": "$40.00",
      "full_label": "$40.00",
      "discount_label": "",
      "coupon_code": "",
      "currency": "USD",
      "refunded": 0.0,
      "refunded_label": "",
      "description": "Haircut",
      "contact": "61412345678",
      "payer_name": "John Smith",
      "appointment_id": 42,
      "booking_reference": "BK-7Q3M2A",
      "package_purchase_id": null,
      "checkout_url": "",
      "link_url": "",
      "last_error": "",
      "paid": "2026-11-11T01:15:00.000Z",
      "refunded_at": null,
      "created": "2026-11-11T01:10:00.000Z"
    }
  ],
  "messages": [
    {
      "direction": "in",
      "text": "Can I move Friday?",
      "time": "2026-11-10T22:00:00.000Z"
    }
  ]
}
```


### `PATCH /bookings/customers/{contact}`

Change a customer's name, e-mail, tags or fields. Scope: `bookings:manage`. Docs: https://www.app2email.com/docs/api/payments/update-customer

Scope: `bookings:manage`. Not with a sandbox key. Updates the contact record (made when there is none). The e-mail also goes onto the customer's upcoming confirmed appointments so their e-mails reach the new address.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| contact | path | string | yes | The customer: number with country code, or business-scoped user id. |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| name | string |  |  |
| email | string |  |  |
| tags | array of string |  |  |
| custom_fields | object |  |  |


Example answer:

```json
{
  "success": true,
  "request_id": "c3cu2",
  "customer": {
    "contact": "61412345678",
    "name": "John Smith",
    "email": "john.new@example.com",
    "tags": [
      "vip",
      "colour"
    ]
  }
}
```


### `DELETE /bookings/customers/{contact}`

Erase a customer's booking data. Scope: `bookings:manage`. Docs: https://www.app2email.com/docs/api/payments/erase-customer-booking-data

Scope: `bookings:manage`. Not with a sandbox key. For a privacy request. Future confirmed appointments are cancelled without a message (reason "data erased"); every appointment of the customer loses their number, name, e-mail, notes and answers (the row stays, anonymised, so reports still count it); their notes, links, holds and poll votes are deleted; package purchases and payments keep amounts and dates but lose the customer. The contact record and the conversation are kept: `DELETE /contacts/{identity}?booking_data=erase` removes the contact too. `booking.customer.erased` is sent. It cannot be undone.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| contact | path | string | yes | The customer: number with country code, or business-scoped user id. |


Example answer:

```json
{
  "success": true,
  "request_id": "c4ce3",
  "erased": true,
  "counts": {
    "appointments": 4,
    "cancelled": 1,
    "notes": 2,
    "links": 1,
    "holds": 0,
    "votes": 0,
    "packages": 0,
    "payments": 1
  },
  "note": "The customer's appointments, notes, links, holds and poll votes were erased or anonymised."
}
```


### `GET /bookings/polls`

The meeting polls. Scope: `bookings:manage or messages:read`. Docs: https://www.app2email.com/docs/api/payments/list-polls

Scope: `bookings:manage` (or `messages:read`). Newest first, with options, votes and status.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| status | query | string (open \| closed \| booked) |  | Only this status. |
| limit | query | integer |  | How many (1 to 100, default 50). |


Example answer:

```json
{
  "success": true,
  "request_id": "q1pl4",
  "polls": [
    {
      "id": 12,
      "title": "Team planning",
      "description": "",
      "service_id": "consultation",
      "provider_id": "",
      "duration_min": 60,
      "options": [
        {
          "id": "a",
          "start": "2026-11-11T23:00:00.000Z",
          "end": "2026-11-12T00:00:00.000Z",
          "start_local": "2026-11-12T10:00",
          "end_local": "2026-11-12T11:00",
          "votes": 2,
          "voters": [
            "Sam",
            "Alex"
          ]
        },
        {
          "id": "b",
          "start": "2026-11-12T03:00:00.000Z",
          "end": "2026-11-12T04:00:00.000Z",
          "start_local": "2026-11-12T14:00",
          "end_local": "2026-11-12T15:00",
          "votes": 1,
          "voters": [
            "Sam"
          ]
        }
      ],
      "votes": [
        {
          "name": "Sam",
          "contact": "61412345678",
          "email": null,
          "choices": [
            "a",
            "b"
          ],
          "comment": "",
          "created": "2026-11-11T02:00:00.000Z"
        }
      ],
      "contact": "",
      "contact_name": "",
      "status": "open",
      "chosen_option": "",
      "appointment_id": null,
      "url": "https://www.app2email.com/book/pQ4rT7uV9wXy",
      "closes": "2026-11-12T00:00:00.000Z",
      "created": "2026-11-11T01:00:00.000Z"
    }
  ],
  "count": 1
}
```


### `POST /bookings/polls`

Offer several times and let people vote. Scope: `bookings:manage`. Docs: https://www.app2email.com/docs/api/payments/create-poll

Scope: `bookings:manage`. Not with a sandbox key. 2 to 10 possible start times (each free now; the business's rule: inside the opening hours), a title, a service or a length. The times are not held. Share the `url`: people open it and vote. Pick the winner with POST /bookings/polls/{id}/book. `poll.voted` is sent for each vote. Send an `Idempotency-Key` header to retry safely: the same key and body within 24 hours gets the first answer again (an error does not use the key up).


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| Idempotency-Key | header | string |  | Optional. A unique value for this message or list (eg a UUID). The same request with the same key within 24 hours gets the first answer again, and nothing is sent twice. Ignored by dry runs. |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| title | string | yes |  |
| description | string |  |  |
| options | array of string | yes | Start times: local time in the business time zone (yyyy-MM-ddTHH:mm) or ISO 8601 with an offset. Each must be free now. |
| service_id | string |  | Its length is used. Give this or duration_min. |
| duration_min | integer |  |  |
| provider_id | string |  |  |
| contact | string |  | The main customer: booking the poll then makes an appointment for them. Left out: the time is blocked. |
| name | string |  |  |
| closes_at | string |  | When voting ends. |


### `GET /bookings/polls/{id}`

One poll with its votes. Scope: `bookings:manage or messages:read`. Docs: https://www.app2email.com/docs/api/payments/get-poll

Scope: `bookings:manage` (or `messages:read`). The options with their vote counts and voters, and every vote with the voter's name, number and comment.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The poll's id. |


Example answer:

```json
{
  "success": true,
  "request_id": "q3pg6",
  "poll": {
    "id": 12,
    "title": "Team planning",
    "description": "",
    "service_id": "consultation",
    "provider_id": "",
    "duration_min": 60,
    "options": [
      {
        "id": "a",
        "start": "2026-11-11T23:00:00.000Z",
        "end": "2026-11-12T00:00:00.000Z",
        "start_local": "2026-11-12T10:00",
        "end_local": "2026-11-12T11:00",
        "votes": 2,
        "voters": [
          "Sam",
          "Alex"
        ]
      },
      {
        "id": "b",
        "start": "2026-11-12T03:00:00.000Z",
        "end": "2026-11-12T04:00:00.000Z",
        "start_local": "2026-11-12T14:00",
        "end_local": "2026-11-12T15:00",
        "votes": 1,
        "voters": [
          "Sam"
        ]
      }
    ],
    "votes": [
      {
        "name": "Sam",
        "contact": "61412345678",
        "email": null,
        "choices": [
          "a",
          "b"
        ],
        "comment": "",
        "created": "2026-11-11T02:00:00.000Z"
      }
    ],
    "contact": "",
    "contact_name": "",
    "status": "open",
    "chosen_option": "",
    "appointment_id": null,
    "url": "https://www.app2email.com/book/pQ4rT7uV9wXy",
    "closes": "2026-11-12T00:00:00.000Z",
    "created": "2026-11-11T01:00:00.000Z"
  }
}
```


### `POST /bookings/polls/{id}/close`

Close a poll to new votes. Scope: `bookings:manage`. Docs: https://www.app2email.com/docs/api/payments/close-poll

Scope: `bookings:manage`. Not with a sandbox key. No more votes. `poll.closed` is sent with status `closed`.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The poll's id. |


Example answer:

```json
{
  "success": true,
  "request_id": "q4pk7",
  "poll": {
    "id": 12,
    "title": "Team planning",
    "description": "",
    "service_id": "consultation",
    "provider_id": "",
    "duration_min": 60,
    "options": [
      {
        "id": "a",
        "start": "2026-11-11T23:00:00.000Z",
        "end": "2026-11-12T00:00:00.000Z",
        "start_local": "2026-11-12T10:00",
        "end_local": "2026-11-12T11:00",
        "votes": 2,
        "voters": [
          "Sam",
          "Alex"
        ]
      },
      {
        "id": "b",
        "start": "2026-11-12T03:00:00.000Z",
        "end": "2026-11-12T04:00:00.000Z",
        "start_local": "2026-11-12T14:00",
        "end_local": "2026-11-12T15:00",
        "votes": 1,
        "voters": [
          "Sam"
        ]
      }
    ],
    "votes": [
      {
        "name": "Sam",
        "contact": "61412345678",
        "email": null,
        "choices": [
          "a",
          "b"
        ],
        "comment": "",
        "created": "2026-11-11T02:00:00.000Z"
      }
    ],
    "contact": "",
    "contact_name": "",
    "status": "closed",
    "chosen_option": "",
    "appointment_id": null,
    "url": "https://www.app2email.com/book/pQ4rT7uV9wXy",
    "closes": "2026-11-12T00:00:00.000Z",
    "created": "2026-11-11T01:00:00.000Z"
  },
  "note": "Closed: no more votes. poll.closed is sent."
}
```


### `POST /bookings/polls/{id}/book`

Pick the winning time. Scope: `bookings:manage`. Docs: https://www.app2email.com/docs/api/payments/book-poll

Scope: `bookings:manage`. Not with a sandbox key. The option is checked like a business booking (409 `booking_slot_taken` when it is not free any more). With a main contact an appointment is made for them (source dashboard; the normal WhatsApp confirmation unless `notify` is false); without one the time is blocked in the calendar under the poll's title. The poll becomes `booked` and `poll.closed` is sent with the chosen option. Send an `Idempotency-Key` header to retry safely: the same key and body within 24 hours gets the first answer again (an error does not use the key up).


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The poll's id. |
| Idempotency-Key | header | string |  | Optional. A unique value for this message or list (eg a UUID). The same request with the same key within 24 hours gets the first answer again, and nothing is sent twice. Ignored by dry runs. |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| option_id | string | yes | One of the poll's options[].id. |
| notify | boolean |  | Tell the customer on WhatsApp (when the poll has a contact). |


Example answer:

```json
{
  "success": true,
  "request_id": "q5pb8",
  "poll": {
    "id": 12,
    "title": "Team planning",
    "description": "",
    "service_id": "consultation",
    "provider_id": "",
    "duration_min": 60,
    "options": [
      {
        "id": "a",
        "start": "2026-11-11T23:00:00.000Z",
        "end": "2026-11-12T00:00:00.000Z",
        "start_local": "2026-11-12T10:00",
        "end_local": "2026-11-12T11:00",
        "votes": 2,
        "voters": [
          "Sam",
          "Alex"
        ]
      },
      {
        "id": "b",
        "start": "2026-11-12T03:00:00.000Z",
        "end": "2026-11-12T04:00:00.000Z",
        "start_local": "2026-11-12T14:00",
        "end_local": "2026-11-12T15:00",
        "votes": 1,
        "voters": [
          "Sam"
        ]
      }
    ],
    "votes": [
      {
        "name": "Sam",
        "contact": "61412345678",
        "email": null,
        "choices": [
          "a",
          "b"
        ],
        "comment": "",
        "created": "2026-11-11T02:00:00.000Z"
      }
    ],
    "contact": "",
    "contact_name": "",
    "status": "booked",
    "chosen_option": "a",
    "appointment_id": null,
    "url": "https://www.app2email.com/book/pQ4rT7uV9wXy",
    "closes": "2026-11-12T00:00:00.000Z",
    "created": "2026-11-11T01:00:00.000Z"
  },
  "booking": null,
  "block": null,
  "note": "The time is blocked in the calendar (the poll has no contact)."
}
```


## Order-and-Pay


### `GET /shop`

The shop: on or off, open now, the order page, counts and limits. Scope: `orders:manage`. Docs: https://www.app2email.com/docs/api/order-and-pay/get-shop

Scope: `orders:manage`. Start here. `enabled` says whether the shop takes orders; `open_now` and `paused` what a customer would find right now; `page_url` is the public order page; `counts` and `limits` say how big the catalog is and may get (10,000 items, archived ones not counted). A number that never opened Order-and-Pay answers `set_up` false.


Example answer:

```json
{
  "success": true,
  "request_id": "h1shp",
  "shop": {
    "set_up": true,
    "enabled": true,
    "name": "Sample Pizza",
    "preset": "takeaway",
    "currency": "USD",
    "timezone": "Australia/Sydney",
    "page_url": "https://www.app2email.com/shop/sample-pizza",
    "open_now": true,
    "paused": false,
    "pickup": true,
    "delivery": false,
    "browse": "page",
    "counts": {
      "items": 42,
      "active": 40,
      "categories": 5
    },
    "limits": {
      "items": 10000,
      "categories": 500,
      "variants": 250,
      "search_limit": 100
    }
  }
}
```


### `GET /shop/settings`

Every setting of the shop, as the shop uses it. Scope: `orders:manage`. Docs: https://www.app2email.com/docs/api/order-and-pay/get-shop-settings

Scope: `orders:manage`. `config` holds the sections with every value in force: `fulfilment` (pickup, delivery, opening hours, special days, the pause), `pickup` (preparation time, time slots), `delivery` (the options with areas and costs), `checkout` (minimum order, fees, tips, notes), `payments`, `discounts` (codes), `orders` (automatic acceptance), `notify` (e-mail addresses), `whatsapp` (the words that open the shop, how customers order, the order messages), and `business`, `money`, `tax`, `stock`, `catalog`. A value the shop never changed shows the default of its type.


Example answer:

```json
{
  "success": true,
  "request_id": "h2set",
  "settings": {
    "enabled": true,
    "slug": "sample-pizza",
    "page_url": "https://www.app2email.com/shop/sample-pizza",
    "config": {
      "fulfilment": {
        "pickup": true,
        "delivery": false,
        "pause_until": "",
        "pause_reason": ""
      },
      "pickup": {
        "prep_minutes": 20,
        "asap": true,
        "slots": false
      }
    }
  }
}
```


### `PUT /shop/settings`

Change settings of the shop. Scope: `orders:manage`. Docs: https://www.app2email.com/docs/api/order-and-pay/update-shop-settings

Scope: `orders:manage`. Not with a sandbox key. Send `config` with the sections to change and, in each, only the keys to change: an object is merged key by key, a list replaces the stored list. Example: pause the shop for half an hour with `{"config": {"fulfilment": {"pause_until": "2026-11-14T12:30:00Z", "pause_reason": "Kitchen is full"}}}`. The whole result is checked before anything is saved: 400 `shop_invalid` names the first problem and `error.details.problems` all of them. The currency cannot change while the shop has items. The switch (`enabled`) and the order page's address are set in the dashboard, where they have their own checks. `not_ready` in the answer lists what still keeps the shop from taking orders.


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| config | object | yes | The sections to change, each with only the keys to change. An object inside a section is merged key by key; a list (hours of a day, delivery methods, discount codes) replaces the stored list. |


Example answer:

```json
{
  "success": true,
  "request_id": "h3put",
  "settings": {
    "enabled": true,
    "slug": "sample-pizza",
    "page_url": "https://www.app2email.com/shop/sample-pizza",
    "config": {
      "fulfilment": {
        "pickup": true,
        "delivery": false,
        "pause_until": "2026-11-14T12:30:00Z",
        "pause_reason": "Kitchen is full"
      }
    }
  },
  "not_ready": []
}
```


### `GET /shop/categories`

The categories of the catalog. Scope: `orders:manage`. Docs: https://www.app2email.com/docs/api/order-and-pay/list-shop-categories

Scope: `orders:manage`. Two levels at most (`parent_id`). `items` counts the items of each; `hidden` categories are not shown to customers.


Example answer:

```json
{
  "success": true,
  "request_id": "h4cat",
  "categories": [
    {
      "id": 3,
      "parent_id": null,
      "name": "Pizza",
      "slug": "pizza",
      "sort": 1,
      "hidden": false,
      "items": 12
    }
  ]
}
```


### `GET /shop/items`

Search and filter the products. Scope: `orders:manage`. Docs: https://www.app2email.com/docs/api/order-and-pay/list-shop-items

Scope: `orders:manage`. The same search customers use: `q` finds words in the name, description, SKU and tags and tolerates typing mistakes (`typo_match` true). Filter by `category`, `tags`, a price range, `in_stock`, and any attribute with `attr.<key>=<value>` (eg `attr.colour=red,blue`). Without `status` only items customers can buy are listed; `status=any` adds hidden ones, `status=archived` lists the archive. Page with `limit` and `offset`; `total` stops counting at a few thousand (`total_capped`). `facets=1` adds the counts per attribute value, tag and the price range of the result. Variants and option groups are in GET /shop/items/{id}.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| q | query | string |  | Words to search for. |
| category | query | integer |  | Only this category (its id). |
| tags | query | string |  | Only items with all of these tags, separated by commas. |
| price_min | query | integer |  | Lowest price, minor units. |
| price_max | query | integer |  | Highest price, minor units. |
| in_stock | query | string (1 \| 0) |  | 1 = leave out what is sold out. |
| status | query | string (active \| hidden \| archived \| any) |  | active (default), hidden, archived, or any (everything but archived). |
| stock | query | string (low \| out \| untracked) |  | Only items in this stock state. |
| sort | query | string (relevance \| manual \| price_asc \| price_desc \| newest \| best \| name) |  | relevance (default with q), manual (the shop's own order), price_asc, price_desc, newest, best, name. |
| facets | query | string (1 \| 0) |  | 1 = add the counts per attribute value and tag. |
| limit | query | integer |  | How many (1 to 100, default 24). |
| offset | query | integer |  | Skip this many. |


Example answer:

```json
{
  "success": true,
  "request_id": "h5lst",
  "items": [
    {
      "id": 12,
      "sku": "PZ-MARG",
      "name": "Margherita",
      "description": "Tomato, mozzarella, basil.",
      "category_id": 3,
      "price": 1000,
      "price_label": "$10.00",
      "compare_at": null,
      "tax_class": "standard",
      "status": "active",
      "has_variants": false,
      "tags": [
        "vegetarian"
      ],
      "attrs": {},
      "allergens": [
        "gluten",
        "milk"
      ],
      "dietary": [
        "vegetarian"
      ],
      "track_stock": false,
      "stock_qty": 0,
      "low_stock_at": null,
      "stock_state": "untracked",
      "daily_limit": null,
      "sold_out_until": null,
      "sold_out_now": false,
      "no_whatsapp": false,
      "min_qty": 1,
      "max_qty": 0,
      "prep_minutes": null,
      "sort": 0,
      "sold_count": 41,
      "image": null,
      "created_at": "2026-11-13T01:00:00Z",
      "updated_at": "2026-11-13T01:00:00Z"
    }
  ],
  "total": 1,
  "total_capped": false,
  "typo_match": false,
  "limit": 24,
  "offset": 0,
  "facets": null,
  "currency": "USD"
}
```


### `POST /shop/items`

Add a product. Scope: `orders:manage`. Docs: https://www.app2email.com/docs/api/order-and-pay/create-shop-item

Scope: `orders:manage`. Not with a sandbox key. The body is the item: `name` and `price` (minor units) are needed, everything else is optional. `variants` gives the versions of the item (size, colour), each with its `attrs`, optional `price` and own stock; `option_group_ids` links existing option groups (extras, choices). Customers see an `active` item at once. 409 `shop_sku_taken` when the SKU is in use, 409 `shop_limit` at 10,000 items. Pictures are added in the dashboard (or by an import with picture addresses).


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| name | string |  |  |
| price | integer |  | Whole minor units (cents): 1250 = 12.50. |
| description | string |  |  |
| sku | string |  |  |
| category_id | integer |  |  |
| compare_at | integer |  |  |
| status | string (active \| hidden \| archived) |  |  |
| tags | array of string |  |  |
| attrs | object |  |  |
| allergens | array of string |  |  |
| dietary | array of string |  |  |
| track_stock | boolean |  |  |
| stock_qty | integer |  |  |
| low_stock_at | integer |  |  |
| no_whatsapp | boolean |  |  |
| min_qty | integer |  |  |
| max_qty | integer |  |  |
| prep_minutes | integer |  |  |
| sort | integer |  |  |
| option_group_ids | array of integer |  |  |
| variants | array of object |  | The whole list: a stored variant that is left out is removed. Send id to keep a variant. |


### `GET /shop/items/{id}`

One product with variants, option groups and pictures. Scope: `orders:manage`. Docs: https://www.app2email.com/docs/api/order-and-pay/get-shop-item

Scope: `orders:manage`. Everything needed to put the item in a cart: `variants` (an item with `has_variants` needs a `variant_id` in the cart line), `option_groups` with their choices, price changes and how many must and may be chosen, the stock of the item or of each variant, and `images`.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The item's id (GET /shop/items). |


Example answer:

```json
{
  "success": true,
  "request_id": "h7get",
  "item": {
    "id": 12,
    "sku": "PZ-MARG",
    "name": "Margherita",
    "description": "Tomato, mozzarella, basil.",
    "category_id": 3,
    "price": 1000,
    "price_label": "$10.00",
    "compare_at": null,
    "tax_class": "standard",
    "status": "active",
    "has_variants": false,
    "tags": [
      "vegetarian"
    ],
    "attrs": {},
    "allergens": [
      "gluten",
      "milk"
    ],
    "dietary": [
      "vegetarian"
    ],
    "track_stock": false,
    "stock_qty": 0,
    "low_stock_at": null,
    "stock_state": "untracked",
    "daily_limit": null,
    "sold_out_until": null,
    "sold_out_now": false,
    "no_whatsapp": false,
    "min_qty": 1,
    "max_qty": 0,
    "prep_minutes": null,
    "sort": 0,
    "sold_count": 41,
    "image": null,
    "created_at": "2026-11-13T01:00:00Z",
    "updated_at": "2026-11-13T01:00:00Z",
    "variants": [],
    "option_group_ids": [
      10
    ],
    "images": [],
    "option_groups": [
      {
        "id": 10,
        "name": "Size",
        "min_choices": 1,
        "max_choices": 1,
        "options": [
          {
            "id": 101,
            "name": "Small",
            "price_delta": 0,
            "price_delta_label": "",
            "sold_out_now": false,
            "default_on": true
          },
          {
            "id": 102,
            "name": "Large",
            "price_delta": 300,
            "price_delta_label": "+$3.00",
            "sold_out_now": false,
            "default_on": false
          }
        ]
      }
    ]
  },
  "currency": "USD"
}
```


### `PUT /shop/items/{id}`

Change a product: only the keys sent change. Scope: `orders:manage`. Docs: https://www.app2email.com/docs/api/order-and-pay/update-shop-item

Scope: `orders:manage`. Not with a sandbox key. Send the keys to change. `variants`, when sent, is the whole list: include the `id` of each variant to keep, leave one out to remove it. Stock figures are only written when the request names them (`stock_qty` of the item or of a variant); to change stock safely while orders come in use POST /shop/items/{id}/stock. `status` archived takes the item out of the catalog.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The item's id (GET /shop/items). |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| name | string |  |  |
| price | integer |  | Whole minor units (cents): 1250 = 12.50. |
| description | string |  |  |
| sku | string |  |  |
| category_id | integer |  |  |
| compare_at | integer |  |  |
| status | string (active \| hidden \| archived) |  |  |
| tags | array of string |  |  |
| attrs | object |  |  |
| allergens | array of string |  |  |
| dietary | array of string |  |  |
| track_stock | boolean |  |  |
| stock_qty | integer |  |  |
| low_stock_at | integer |  |  |
| no_whatsapp | boolean |  |  |
| min_qty | integer |  |  |
| max_qty | integer |  |  |
| prep_minutes | integer |  |  |
| sort | integer |  |  |
| option_group_ids | array of integer |  |  |
| variants | array of object |  | The whole list: a stored variant that is left out is removed. Send id to keep a variant. |


Example answer:

```json
{
  "success": true,
  "request_id": "h8put",
  "item": {
    "id": 12,
    "sku": "PZ-MARG",
    "name": "Margherita",
    "description": "Tomato, mozzarella, basil.",
    "category_id": 3,
    "price": 1100,
    "price_label": "$11.00",
    "compare_at": null,
    "tax_class": "standard",
    "status": "active",
    "has_variants": false,
    "tags": [
      "vegetarian"
    ],
    "attrs": {},
    "allergens": [
      "gluten",
      "milk"
    ],
    "dietary": [
      "vegetarian"
    ],
    "track_stock": false,
    "stock_qty": 0,
    "low_stock_at": null,
    "stock_state": "untracked",
    "daily_limit": null,
    "sold_out_until": null,
    "sold_out_now": false,
    "no_whatsapp": false,
    "min_qty": 1,
    "max_qty": 0,
    "prep_minutes": null,
    "sort": 0,
    "sold_count": 41,
    "image": null,
    "created_at": "2026-11-13T01:00:00Z",
    "updated_at": "2026-11-13T01:00:00Z",
    "variants": [],
    "option_group_ids": [
      10
    ],
    "images": [],
    "option_groups": [
      {
        "id": 10,
        "name": "Size",
        "min_choices": 1,
        "max_choices": 1,
        "options": [
          {
            "id": 101,
            "name": "Small",
            "price_delta": 0,
            "price_delta_label": "",
            "sold_out_now": false,
            "default_on": true
          },
          {
            "id": 102,
            "name": "Large",
            "price_delta": 300,
            "price_delta_label": "+$3.00",
            "sold_out_now": false,
            "default_on": false
          }
        ]
      }
    ]
  },
  "currency": "USD"
}
```


### `DELETE /shop/items/{id}`

Archive a product. Scope: `orders:manage`. Docs: https://www.app2email.com/docs/api/order-and-pay/archive-shop-item

Scope: `orders:manage`. Not with a sandbox key. The item is archived, not erased: orders keep their lines and the reports their figures. Archived items are not counted against the 10,000 item limit. PUT with `status` active brings it back.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The item's id (GET /shop/items). |


Example answer:

```json
{
  "success": true,
  "request_id": "h9del",
  "item": {
    "id": 12,
    "sku": "PZ-MARG",
    "name": "Margherita",
    "description": "Tomato, mozzarella, basil.",
    "category_id": 3,
    "price": 1000,
    "price_label": "$10.00",
    "compare_at": null,
    "tax_class": "standard",
    "status": "archived",
    "has_variants": false,
    "tags": [
      "vegetarian"
    ],
    "attrs": {},
    "allergens": [
      "gluten",
      "milk"
    ],
    "dietary": [
      "vegetarian"
    ],
    "track_stock": false,
    "stock_qty": 0,
    "low_stock_at": null,
    "stock_state": "untracked",
    "daily_limit": null,
    "sold_out_until": null,
    "sold_out_now": false,
    "no_whatsapp": false,
    "min_qty": 1,
    "max_qty": 0,
    "prep_minutes": null,
    "sort": 0,
    "sold_count": 41,
    "image": null,
    "created_at": "2026-11-13T01:00:00Z",
    "updated_at": "2026-11-13T01:00:00Z",
    "variants": [],
    "option_group_ids": [
      10
    ],
    "images": [],
    "option_groups": [
      {
        "id": 10,
        "name": "Size",
        "min_choices": 1,
        "max_choices": 1,
        "options": [
          {
            "id": 101,
            "name": "Small",
            "price_delta": 0,
            "price_delta_label": "",
            "sold_out_now": false,
            "default_on": true
          },
          {
            "id": 102,
            "name": "Large",
            "price_delta": 300,
            "price_delta_label": "+$3.00",
            "sold_out_now": false,
            "default_on": false
          }
        ]
      }
    ]
  },
  "currency": "USD"
}
```


### `POST /shop/items/{id}/stock`

Set or change the stock of a product. Scope: `orders:manage`. Docs: https://www.app2email.com/docs/api/order-and-pay/set-shop-stock

Scope: `orders:manage`. Not with a sandbox key. `mode` set writes the figure, `mode` add changes it by `value` (negative takes away) in one step that cannot lose a sale happening at the same moment. For an item with variants send `variant_id`. Every change is written to the stock history with the key's name and the `note`. 409 `shop_not_tracked` when the item does not count stock: send `start_tracking` true to switch it on with this figure.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The item's id (GET /shop/items). |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| mode | string (set \| add) |  |  |
| value | integer | yes | The new figure (set) or the change (add; negative takes away). |
| variant_id | integer |  |  |
| note | string |  |  |
| start_tracking | boolean |  | Switch stock counting on for an item that does not count yet. |


Example answer:

```json
{
  "success": true,
  "request_id": "h10st",
  "item_id": 14,
  "variant_id": null,
  "stock_qty": 24
}
```


### `POST /shop/items/{id}/sold_out`

Mark a product sold out for a while, or back. Scope: `orders:manage`. Docs: https://www.app2email.com/docs/api/order-and-pay/set-shop-sold-out

Scope: `orders:manage`. Not with a sandbox key. For items that do not count stock (a dish that ran out). `until`: `on` until switched back, `1h`, `2h`, `4h`, `today` (until the end of the shop's day), `off` to make it available again, or a later time. Customers see it greyed out or not at all, as the shop has chosen.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The item's id (GET /shop/items). |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| until | string | yes | on (until switched back), 1h, 2h, 4h, today, off (available again), or a later ISO 8601 time. |


Example answer:

```json
{
  "success": true,
  "request_id": "h11so",
  "item_id": 12,
  "sold_out_until": "2026-11-14T13:00:00Z",
  "sold_out_now": true
}
```


### `GET /shop/orders`

The orders, newest first. Scope: `orders:manage`. Docs: https://www.app2email.com/docs/api/order-and-pay/list-shop-orders

Scope: `orders:manage`. `group` narrows the list: `open` (accepted, being prepared, ready, on the way, and new ones), `new` (waiting for the shop to accept), `waiting` (not paid or not confirmed yet), `done`, `cancelled`. `q` finds a reference, a name or a number. Lists leave out the lines: `items_text` says what was ordered in one line, GET /shop/orders/{id} has the rest. Page with `before` set to `next_before`. To follow orders without polling use the `order.*` webhook events.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| group | query | string (open \| new \| waiting \| done \| cancelled) |  | open, new, waiting, done or cancelled. Left out: all. |
| q | query | string |  | A reference, a customer's name or number. |
| before | query | integer |  | For the next page: next_before of the previous answer. |
| limit | query | integer |  | How many (1 to 100, default 50). |


Example answer:

```json
{
  "success": true,
  "request_id": "h12ol",
  "orders": [
    {
      "id": 318,
      "reference": "SO-K7M2QX",
      "status": "accepted",
      "status_text": "Accepted",
      "source": "api",
      "fulfilment": "pickup",
      "asap": true,
      "due_at": "2026-11-13T01:20:00Z",
      "due_label": "today 12:20",
      "slot_label": "",
      "customer_name": "Sample Contact",
      "customer_phone": "61412345678",
      "customer_email": "",
      "contact_identity": "61412345678",
      "contact_verified": true,
      "address": {},
      "delivery_method": "",
      "delivery_zone": "",
      "note": "",
      "allergy_note": "",
      "items_count": 3,
      "items_text": "2 x Margherita, 1 x Cola",
      "currency": "USD",
      "subtotal": 3050,
      "discount": 0,
      "discount_code": "",
      "delivery_fee": 0,
      "fees": 0,
      "tip": 0,
      "tax": 0,
      "total": 3050,
      "total_label": "$30.50",
      "refunded": 0,
      "refundable": 3050,
      "payment_state": "on_pickup",
      "payment_method": "",
      "payment_id": null,
      "pickup_code": "7KQ2",
      "order_url": "https://www.app2email.com/o/Xk3mP9qR2sT7",
      "actions": [
        "preparing",
        "ready",
        "complete",
        "cancel",
        "time"
      ],
      "can_refund": false,
      "late": false,
      "created_at": "2026-11-13T01:00:00Z",
      "accepted_at": "2026-11-13T01:00:00Z",
      "ready_at": null,
      "completed_at": null,
      "cancelled_at": null,
      "cancelled_by": "",
      "cancel_reason": "",
      "handed_by": "",
      "handed_method": ""
    }
  ],
  "more": false,
  "next_before": null
}
```


### `POST /shop/orders`

Place an order for a customer. Scope: `orders:manage`. Docs: https://www.app2email.com/docs/api/order-and-pay/create-shop-order

Scope: `orders:manage`. Not with a sandbox key. For a system or an agent that takes the order itself. The cart is priced from the shop's data as it is now, stock is taken in the same step, and the order appears in the dashboard and the counter app like any other (`source` api). You vouch for `contact`: the order counts as that customer's own, and they get the shop's order messages on WhatsApp (confirmation with the pickup QR code, ready, and so on) where those are switched on. `pay` later = at pickup or on delivery; `pay` online answers `checkout_url`: send it to the customer, the order is confirmed (and `order.created` sent) when it is paid. Send `expected_total` with the total the customer agreed to: a different total answers 409 `shop_changed` with the new quote in `error.details.quote`. 409 `shop_order_problems` lists what is in the way the same way. The `Idempotency-Key` header (or `client_key`) makes a retry safe: the same key answers the same order with `repeated` true and status 200.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| Idempotency-Key | header | string |  | Optional. A unique value for this message or list (eg a UUID). The same request with the same key within 24 hours gets the first answer again, and nothing is sent twice. Ignored by dry runs. |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| lines | array of object | yes |  |
| fulfilment | string (pickup \| delivery) |  |  |
| address | object |  | Needed for delivery: line1 and at least one of suburb, city or postcode. |
|   line1 | string |  | Street and number. |
|   line2 | string |  |  |
|   suburb | string |  |  |
|   city | string |  |  |
|   region | string |  |  |
|   postcode | string |  |  |
|   country | string |  |  |
|   notes | string |  | For the driver. |
|   lat | number |  | Where the customer is (latitude), with lng. Only the delivery options that charge by distance read it; without it they answer code `location`. |
|   lng | number |  | Longitude, with lat. |
| delivery_method | string |  | When the shop has several delivery options: the id of one (GET /shop/settings, config.delivery.methods). |
| discount_code | string |  |  |
| tip_percent | integer |  |  |
| tip_minor | integer |  | A tip as an amount; wins over tip_percent. |
| contact | string | yes | The customer's WhatsApp number with the country code, digits only. |
| name | string | yes |  |
| email | string |  |  |
| asap | boolean |  |  |
| slot | string |  | With asap false: the start of a time the quote offered, YYYY-MM-DDTHH:mm in the shop's time. |
| note | string |  |  |
| allergy_note | string |  |  |
| pay | string (later \| online) |  |  |
| method | string |  | With pay online: stripe or paypal; empty = the first connected. |
| expected_total | integer |  | The total the customer agreed to: a different total answers 409 shop_changed with the new quote. |
| client_key | string |  | Your own unique key of this order (the Idempotency-Key header does the same): the same key again answers the same order. |


Example answer:

```json
{
  "success": true,
  "request_id": "h13od",
  "order": {
    "id": 318,
    "reference": "SO-K7M2QX",
    "status": "accepted",
    "status_text": "Accepted",
    "source": "api",
    "fulfilment": "pickup",
    "asap": true,
    "due_at": "2026-11-13T01:20:00Z",
    "due_label": "today 12:20",
    "slot_label": "",
    "customer_name": "Sample Contact",
    "customer_phone": "61412345678",
    "customer_email": "",
    "contact_identity": "61412345678",
    "contact_verified": true,
    "address": {},
    "delivery_method": "",
    "delivery_zone": "",
    "note": "",
    "allergy_note": "",
    "items_count": 3,
    "items_text": "2 x Margherita, 1 x Cola",
    "currency": "USD",
    "subtotal": 3050,
    "discount": 0,
    "discount_code": "",
    "delivery_fee": 0,
    "fees": 0,
    "tip": 0,
    "tax": 0,
    "total": 3050,
    "total_label": "$30.50",
    "refunded": 0,
    "refundable": 3050,
    "payment_state": "on_pickup",
    "payment_method": "",
    "payment_id": null,
    "pickup_code": "7KQ2",
    "order_url": "https://www.app2email.com/o/Xk3mP9qR2sT7",
    "actions": [
      "preparing",
      "ready",
      "complete",
      "cancel",
      "time"
    ],
    "can_refund": false,
    "late": false,
    "created_at": "2026-11-13T01:00:00Z",
    "accepted_at": "2026-11-13T01:00:00Z",
    "ready_at": null,
    "completed_at": null,
    "cancelled_at": null,
    "cancelled_by": "",
    "cancel_reason": "",
    "handed_by": "",
    "handed_method": "",
    "lines": [
      {
        "id": 901,
        "item_id": 12,
        "variant_id": null,
        "sku": "PZ-MARG",
        "name": "Margherita",
        "variant_label": "",
        "options": [
          {
            "id": 102,
            "group": "Size",
            "name": "Large",
            "price_delta": 300
          }
        ],
        "qty": 2,
        "unit_price": 1300,
        "unit_price_label": "$13.00",
        "line_total": 2600,
        "line_total_label": "$26.00",
        "note": ""
      }
    ]
  },
  "repeated": true,
  "checkout_url": "",
  "payment_id": null
}
```


### `GET /shop/orders/{id}`

One order with lines, payment, next steps and history. Scope: `orders:manage`. Docs: https://www.app2email.com/docs/api/order-and-pay/get-shop-order

Scope: `orders:manage`. By id or by reference. `lines` with the chosen variant and options, the money, the pickup or delivery details, `actions` (what POST /shop/orders/{id}/action accepts now), `can_refund` with `refundable`, and `events`: who did what and when, on which device, including the hand-over at the counter.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The order's id, or its reference (SO-K7M2QX). |


Example answer:

```json
{
  "success": true,
  "request_id": "h14og",
  "order": {
    "id": 318,
    "reference": "SO-K7M2QX",
    "status": "accepted",
    "status_text": "Accepted",
    "source": "api",
    "fulfilment": "pickup",
    "asap": true,
    "due_at": "2026-11-13T01:20:00Z",
    "due_label": "today 12:20",
    "slot_label": "",
    "customer_name": "Sample Contact",
    "customer_phone": "61412345678",
    "customer_email": "",
    "contact_identity": "61412345678",
    "contact_verified": true,
    "address": {},
    "delivery_method": "",
    "delivery_zone": "",
    "note": "",
    "allergy_note": "",
    "items_count": 3,
    "items_text": "2 x Margherita, 1 x Cola",
    "currency": "USD",
    "subtotal": 3050,
    "discount": 0,
    "discount_code": "",
    "delivery_fee": 0,
    "fees": 0,
    "tip": 0,
    "tax": 0,
    "total": 3050,
    "total_label": "$30.50",
    "refunded": 0,
    "refundable": 3050,
    "payment_state": "on_pickup",
    "payment_method": "",
    "payment_id": null,
    "pickup_code": "7KQ2",
    "order_url": "https://www.app2email.com/o/Xk3mP9qR2sT7",
    "actions": [
      "preparing",
      "ready",
      "complete",
      "cancel",
      "time"
    ],
    "can_refund": false,
    "late": false,
    "created_at": "2026-11-13T01:00:00Z",
    "accepted_at": "2026-11-13T01:00:00Z",
    "ready_at": null,
    "completed_at": null,
    "cancelled_at": null,
    "cancelled_by": "",
    "cancel_reason": "",
    "handed_by": "",
    "handed_method": "",
    "lines": [
      {
        "id": 901,
        "item_id": 12,
        "variant_id": null,
        "sku": "PZ-MARG",
        "name": "Margherita",
        "variant_label": "",
        "options": [
          {
            "id": 102,
            "group": "Size",
            "name": "Large",
            "price_delta": 300
          }
        ],
        "qty": 2,
        "unit_price": 1300,
        "unit_price_label": "$13.00",
        "line_total": 2600,
        "line_total_label": "$26.00",
        "note": ""
      }
    ]
  },
  "events": [
    {
      "type": "placed",
      "to_status": "new",
      "by_name": "API key Till",
      "at": "2026-11-13T01:00:00Z"
    }
  ]
}
```


### `POST /shop/orders/{id}/action`

Move an order on, change its time, cancel or decline it. Scope: `orders:manage`. Docs: https://www.app2email.com/docs/api/order-and-pay/update-shop-order

Scope: `orders:manage`. Not with a sandbox key. `action`: `accept`, `preparing`, `ready`, `out_for_delivery`, `complete` (handed over or delivered), `time` with `minutes` (later, or negative for earlier), `cancel` or `reject` with a `reason`, `no_show` for a ready pickup that was never collected (it ends as not collected and counts as a no-show of that customer), and `hand_lines` with `lines` [{ `id`, `qty` }] to give some lines now and the rest later (only when the shop has switched on partial hand-over; the order stays open until `complete`). Only the steps in the order's `actions` are accepted; anything else answers 400 `shop_invalid`, and 409 `shop_changed` when someone else moved the order meanwhile. `cancel` and `reject` give the stock back (`restock` false keeps it) and, with `refund` true, refund a paid order; `notice` in the answer says when a refund did not go through. The customer is told on WhatsApp where the shop has that message switched on. The step is written to the order's history with the key's name.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The order's id, or its reference (SO-K7M2QX). |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| action | string (accept \| preparing \| ready \| out_for_delivery \| complete \| cancel \| reject \| time \| no_show \| hand_lines) | yes |  |
| reason | string |  | cancel, reject: what the customer is told. |
| minutes | integer |  | time: minutes later (negative: earlier). |
| refund | boolean |  | cancel, reject of a paid order: refund it. no_show: refund what was paid online (default false: the payment is kept). |
| restock | boolean |  | cancel, reject: give the stock back (default true). no_show: default false. |
| collected | string (cash \| card) |  | complete of an order paid at the counter. |
| lines | array of object |  | hand_lines: the lines given now (the shop setting orders.partial_handover must be on). The order stays open; complete hands over what is left. |


Example answer:

```json
{
  "success": true,
  "request_id": "h15oa",
  "order": {
    "id": 318,
    "reference": "SO-K7M2QX",
    "status": "ready",
    "status_text": "Ready",
    "source": "api",
    "fulfilment": "pickup",
    "asap": true,
    "due_at": "2026-11-13T01:20:00Z",
    "due_label": "today 12:20",
    "slot_label": "",
    "customer_name": "Sample Contact",
    "customer_phone": "61412345678",
    "customer_email": "",
    "contact_identity": "61412345678",
    "contact_verified": true,
    "address": {},
    "delivery_method": "",
    "delivery_zone": "",
    "note": "",
    "allergy_note": "",
    "items_count": 3,
    "items_text": "2 x Margherita, 1 x Cola",
    "currency": "USD",
    "subtotal": 3050,
    "discount": 0,
    "discount_code": "",
    "delivery_fee": 0,
    "fees": 0,
    "tip": 0,
    "tax": 0,
    "total": 3050,
    "total_label": "$30.50",
    "refunded": 0,
    "refundable": 3050,
    "payment_state": "on_pickup",
    "payment_method": "",
    "payment_id": null,
    "pickup_code": "7KQ2",
    "order_url": "https://www.app2email.com/o/Xk3mP9qR2sT7",
    "actions": [
      "preparing",
      "ready",
      "complete",
      "cancel",
      "time"
    ],
    "can_refund": false,
    "late": false,
    "created_at": "2026-11-13T01:00:00Z",
    "accepted_at": "2026-11-13T01:00:00Z",
    "ready_at": null,
    "completed_at": null,
    "cancelled_at": null,
    "cancelled_by": "",
    "cancel_reason": "",
    "handed_by": "",
    "handed_method": "",
    "lines": [
      {
        "id": 901,
        "item_id": 12,
        "variant_id": null,
        "sku": "PZ-MARG",
        "name": "Margherita",
        "variant_label": "",
        "options": [
          {
            "id": 102,
            "group": "Size",
            "name": "Large",
            "price_delta": 300
          }
        ],
        "qty": 2,
        "unit_price": 1300,
        "unit_price_label": "$13.00",
        "line_total": 2600,
        "line_total_label": "$26.00",
        "note": ""
      }
    ]
  },
  "notice": ""
}
```


### `POST /shop/orders/{id}/refund`

Refund an order that was paid online. Scope: `orders:manage`. Docs: https://www.app2email.com/docs/api/order-and-pay/refund-shop-order

Scope: `orders:manage`. Not with a sandbox key. In full when `amount` is left out, else that many minor units (at most `refundable`). The money goes back through the payment provider the way it was paid; an order paid at the counter cannot be refunded here. The order itself stays as it is: cancel it with POST /shop/orders/{id}/action when it should also end.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The order's id, or its reference (SO-K7M2QX). |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| amount | integer |  | Minor units. Left out: all that is left. |


Example answer:

```json
{
  "success": true,
  "request_id": "h16rf",
  "order": {
    "id": 318,
    "reference": "SO-K7M2QX",
    "status": "accepted",
    "status_text": "Accepted",
    "source": "api",
    "fulfilment": "pickup",
    "asap": true,
    "due_at": "2026-11-13T01:20:00Z",
    "due_label": "today 12:20",
    "slot_label": "",
    "customer_name": "Sample Contact",
    "customer_phone": "61412345678",
    "customer_email": "",
    "contact_identity": "61412345678",
    "contact_verified": true,
    "address": {},
    "delivery_method": "",
    "delivery_zone": "",
    "note": "",
    "allergy_note": "",
    "items_count": 3,
    "items_text": "2 x Margherita, 1 x Cola",
    "currency": "USD",
    "subtotal": 3050,
    "discount": 0,
    "discount_code": "",
    "delivery_fee": 0,
    "fees": 0,
    "tip": 0,
    "tax": 0,
    "total": 3050,
    "total_label": "$30.50",
    "refunded": 3050,
    "refundable": 0,
    "payment_state": "refunded",
    "payment_method": "stripe",
    "payment_id": null,
    "pickup_code": "7KQ2",
    "order_url": "https://www.app2email.com/o/Xk3mP9qR2sT7",
    "actions": [
      "preparing",
      "ready",
      "complete",
      "cancel",
      "time"
    ],
    "can_refund": false,
    "late": false,
    "created_at": "2026-11-13T01:00:00Z",
    "accepted_at": "2026-11-13T01:00:00Z",
    "ready_at": null,
    "completed_at": null,
    "cancelled_at": null,
    "cancelled_by": "",
    "cancel_reason": "",
    "handed_by": "",
    "handed_method": "",
    "lines": [
      {
        "id": 901,
        "item_id": 12,
        "variant_id": null,
        "sku": "PZ-MARG",
        "name": "Margherita",
        "variant_label": "",
        "options": [
          {
            "id": 102,
            "group": "Size",
            "name": "Large",
            "price_delta": 300
          }
        ],
        "qty": 2,
        "unit_price": 1300,
        "unit_price_label": "$13.00",
        "line_total": 2600,
        "line_total_label": "$26.00",
        "note": ""
      }
    ]
  }
}
```


### `POST /shop/quote`

Price a cart: total, problems, times and ways to pay. Scope: `orders:manage`. Docs: https://www.app2email.com/docs/api/order-and-pay/quote-shop-order

Scope: `orders:manage`. Nothing is saved and no stock is taken. `quote` has the lines with their prices, the discount (or why a code gives none), the delivery fee for the address, fees, tip, tax and `total`; `problems` lists what is in the way (empty = the order can be placed). `times` says whether as-soon-as-possible is offered and when it would be ready, and the time slots when the shop uses them; `pay` which ways to pay this order has. Quote first, show the total, then POST /shop/orders with `expected_total`.


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| lines | array of object | yes |  |
| fulfilment | string (pickup \| delivery) |  |  |
| address | object |  | Needed for delivery: line1 and at least one of suburb, city or postcode. |
|   line1 | string |  | Street and number. |
|   line2 | string |  |  |
|   suburb | string |  |  |
|   city | string |  |  |
|   region | string |  |  |
|   postcode | string |  |  |
|   country | string |  |  |
|   notes | string |  | For the driver. |
|   lat | number |  | Where the customer is (latitude), with lng. Only the delivery options that charge by distance read it; without it they answer code `location`. |
|   lng | number |  | Longitude, with lat. |
| delivery_method | string |  | When the shop has several delivery options: the id of one (GET /shop/settings, config.delivery.methods). |
| discount_code | string |  |  |
| tip_percent | integer |  |  |
| tip_minor | integer |  | A tip as an amount; wins over tip_percent. |
| contact | string |  | Optional: the customer's WhatsApp number, for discount codes that depend on the customer. |


Example answer:

```json
{
  "success": true,
  "request_id": "h17qt",
  "quote": {
    "currency": "USD",
    "lines": [],
    "items_count": 3,
    "subtotal": 3050,
    "discount": 0,
    "discount_code": "",
    "discount_message": "",
    "fulfilment": "pickup",
    "delivery_fee": 0,
    "delivery_method": "",
    "delivery_zone": "",
    "fees_total": 0,
    "tip": 0,
    "tax": 0,
    "tax_included": true,
    "total": 3050,
    "total_label": "$30.50",
    "prep_minutes": 20,
    "ok": true,
    "problems": []
  },
  "times": {
    "asap": {
      "offered": true,
      "ok": true,
      "ready_label": "about 12:20",
      "message": ""
    },
    "slots_on": false,
    "days": [],
    "open_now": true,
    "paused": false
  },
  "pay": {
    "online": [
      "stripe"
    ],
    "later": true,
    "must_prepay": false,
    "free": false
  }
}
```


### `GET /shop/report`

The shop's figures for a range of days. Scope: `orders:manage`. Docs: https://www.app2email.com/docs/api/order-and-pay/get-shop-report

Scope: `orders:manage`. Both days are included, in the shop's time zone; the default is the last 7 days and a range covers 366 days at most. Orders by state, sales, what was paid online and at the counter by cash and card, delivery fees, tips, discounts, tax and refunds, the best sellers, orders per hour and per day, the customers who spent most, the discount codes used, where the orders came from, and the hand-over log.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| from | query | string |  | First day, YYYY-MM-DD. Default: six days before to. |
| to | query | string |  | Last day, YYYY-MM-DD. Default: today. |


Example answer:

```json
{
  "success": true,
  "request_id": "h18rp",
  "report": {
    "from": "2026-11-07",
    "to": "2026-11-13",
    "timezone": "Australia/Sydney",
    "orders": {
      "placed": 61,
      "completed": 55,
      "cancelled": 4
    },
    "money": {
      "sales_label": "$1,840.50"
    }
  }
}
```


### `POST /shop/link`

A customer's personal link to the order page. Scope: `orders:manage`. Docs: https://www.app2email.com/docs/api/order-and-pay/get-shop-order-link

Scope: `orders:manage`. The order page opened through this link knows the customer: their name, their last five delivery addresses and their orders are there, and an order placed needs no confirmation step. Valid for 7 days. It identifies the customer, so send it only to that customer (for example in a template message). `page_url` is the public page without the personal part.


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| contact | string | yes | The customer's WhatsApp number with the country code, digits only. |


Example answer:

```json
{
  "success": true,
  "request_id": "h19lk",
  "url": "https://www.app2email.com/shop/sample-pizza?t=eyJ...",
  "page_url": "https://www.app2email.com/shop/sample-pizza",
  "days": 7,
  "enabled": true
}
```


## Submit-Info


### `GET /submit/guide`

The Submit-Info guide for agents: every key, rule and example. Scope: `submissions:manage`. Docs: https://www.app2email.com/docs/api/submit-info/get-submit-guide

Scope: `submissions:manage`. Start here. One JSON document with everything needed to set Submit-Info up without reading anything else: every key of a form definition with its default and limit, the field types and how WhatsApp shows each, stage rules, rule operators, the automation triggers and actions with their keys and an example each, placeholders, formula functions, connection kinds, roles and abilities, limits, the presets, and three complete worked setups. `this_number` names the forms, lists and connections the number already has, so nothing is replaced by accident. Next: write a setup document and send it to POST /submit/setup with `dry_run` true.


Example answer:

```json
{
  "success": true,
  "request_id": "g1gde",
  "guide": {
    "product": "Submit-Info",
    "summary": "A form is a plain list of questions in steps. app2email turns it into a WhatsApp Flow and a web page with the same steps. Each filled-in form is a submission: answers, files, a reference and a public status page. A submission moves through the form's stages, can be assigned, noted, answered and exported. Automations (when - if - do) react to what happens: they reply, e-mail, change the stage, calculate, and call outside systems. Outside systems are reached through connections: a plain HTTP request, an operation of an OpenAPI document, or a tool of an MCP server.",
    "how_to": [
      "1. GET /guide (this document). Pick a preset from `presets` (GET /presets?key=<key> returns its complete setup document) or write your own.",
      "2. POST /setup with \"dry_run\": true: nothing is saved; `problems` lists every problem with its path and a fix.",
      "3. POST /setup without dry_run when `problems` is empty. Existing forms, lists and connections with the same key are replaced.",
      "4. POST /forms/{key}/publish uploads the generated Flow to WhatsApp and publishes it (or list the keys under \"publish\" in the setup document).",
      "5. Share links.wa_me or links.web of the form (GET /forms/{key}), or send it to a contact with POST /forms/{key}/send."
    ],
    "form": {
      "keys": {
        "title": "required. 1-60 characters. the form's public name",
        "stages": "2-12 stages; the first is where a new submission starts. left out = New, In progress, Done"
      },
      "key_rule": "keys of steps, fields, stages and calculated values: a lower-case letter, then up to 39 of a-z, 0-9 and _. fields and calculated values share one set of keys",
      "field_keys": {
        "key": "required. a lower-case letter, then up to 39 of a-z, 0-9 and _; unique in the form; not a reserved word",
        "required": "true = must be answered. default false"
      },
      "field_types": [
        {
          "type": "number",
          "value": "number",
          "keys": {
            "min": "a number or null",
            "max": "a number or null",
            "decimals": "0-6; 0 = whole numbers",
            "unit": "shown after the value, max 20 characters"
          },
          "whatsapp": "TextInput (number)",
          "notes": "A number. With decimals the phone shows a text keyboard and the server checks the number."
        }
      ],
      "internal_types": [
        "text",
        "textarea",
        "number",
        "email",
        "phone",
        "date",
        "select",
        "multiselect",
        "yesno",
        "rating"
      ],
      "reserved_keys": [
        "reference",
        "status",
        "status_name",
        "form",
        "form_key",
        "channel",
        "contact",
        "link",
        "id",
        "created",
        "updated",
        "assignee",
        "priority",
        "tags",
        "due",
        "files",
        "flow_token",
        "screen",
        "error_message",
        "error",
        "answers",
        "extra",
        "submission",
        "note",
        "button",
        "business",
        "desk_link",
        "status_kind",
        "verified",
        "files_count",
        "prefill",
        "confirm",
        "true",
        "false",
        "null",
        "and",
        "or",
        "not"
      ],
      "whatsapp": "the Flow is generated: one screen per step (a step with several photo / document fields is split, one picker per screen).",
      "stage": {
        "keys": {
          "key": "required. a lower-case letter, then up to 39 of a-z, 0-9 and _",
          "kind": "open | done | cancelled. at least one open and one done stage"
        },
        "example": {
          "key": "approved",
          "name": "Approved",
          "kind": "done",
          "color": "green",
          "set_by": [
            "manager"
          ],
          "require_note": true,
          "message": "Your application {reference} is approved. {note}"
        }
      },
      "rule": {
        "shape": "{ \"field\": \"<key>\", <operator>: <value> } with one or more operators (every one must hold), or { \"all\": [rules] }, or { \"any\": [rules] }.",
        "operators": [
          "equals",
          "not_equals",
          "in",
          "not_in",
          "contains",
          "empty",
          "not_empty",
          "gt",
          "gte",
          "lt",
          "lte"
        ],
        "groups": "all | any",
        "in_show_if": "`field` is a field of an EARLIER step that is asked or hidden",
        "in_automations": "`field` is any field key or extra key, or status, status_kind, channel, form, priority, tags, assignee, verified, files_count, contact.name, contact.phone",
        "example": {
          "all": [
            {
              "field": "category",
              "in": [
                "outage",
                "safety"
              ]
            },
            {
              "field": "amount",
              "gt": 5000
            }
          ]
        }
      }
    },
    "automation": {
      "keys": {
        "name": "required. within one form a name is unique: setup replaces the automation with the same name",
        "actions": "1-20 actions, run in order"
      },
      "triggers": [
        {
          "trigger": "status_changed",
          "when": "the stage changed",
          "options": {
            "to": [],
            "from": []
          }
        }
      ],
      "trigger_options": {
        "status_changed.to": "stage keys the submission moved to; [] = any",
        "overdue.minutes": "5 to 43200"
      },
      "actions": [
        {
          "type": "set_status",
          "does": "moves the submission to a stage",
          "keys": {
            "status": "a stage key",
            "note": "kept with the change; placeholders"
          },
          "example": {
            "type": "set_status",
            "status": "approved",
            "note": ""
          }
        }
      ],
      "placeholders": [
        {
          "name": "{reference}",
          "is": "the submission's reference, for example MR-7Q3M2A"
        }
      ],
      "placeholder_notes": "a name that is not known stays as typed. in JSON bodies and arguments a string that is exactly one placeholder keeps the value's type (a number stays a number). in addresses each inserted value is percent-encoded",
      "formula": {
        "language": "numbers, 'texts', field keys, + - * / %, comparisons == != > >= < <=, and / or / not, brackets and the functions below.",
        "functions": [
          {
            "name": "round",
            "usage": "round(x, decimals)",
            "does": "x rounded (half away from zero); decimals 0-10, default 0"
          }
        ],
        "examples": [
          "reading - previous('reading')",
          "round(quantity * lookup('prices', product, 'price'), 2)"
        ]
      },
      "json_path": "in `save`: $ = the whole answer, $.a.b[0].c = a value inside it, $text = the answer as text (MCP: the first text content)",
      "limits": "a failed outside call is tried again after 1 minute, 10 minutes and 1 hour, then the webhook event submit.automation_failed is sent."
    },
    "connection": {
      "keys": {
        "kind": "http | openapi | mcp",
        "base_url": "https only. for mcp: the server's address"
      },
      "kinds": [
        {
          "kind": "http",
          "use": "a plain HTTP API: the action names method, path, query, headers and a JSON body"
        }
      ],
      "auth_types": [
        {
          "type": "bearer",
          "use": "Authorization: Bearer <secret>"
        }
      ],
      "limits": {
        "timeout_seconds": 15,
        "answer_kb": 256,
        "request_kb": 256,
        "extra_headers": 5,
        "functions": 300,
        "params_per_function": 40,
        "calls_per_minute": 60,
        "calls_per_day": 2000,
        "addresses": "https only; private, loopback, link-local and metadata addresses are refused; redirects are not followed"
      },
      "example": {
        "key": "billing",
        "name": "Billing",
        "kind": "http",
        "base_url": "https://billing.example.com/api",
        "auth": {
          "type": "bearer",
          "secret": "<your token>"
        },
        "headers": {},
        "enabled": true
      }
    },
    "member": {
      "keys": {
        "email": "required: the invitation goes there",
        "role": "admin | manager | agent | viewer: a starting set of abilities"
      },
      "roles": {
        "owner": [
          "note",
          "reply",
          "edit",
          "stage",
          "assign",
          "files",
          "export",
          "delete",
          "run",
          "forms",
          "automations",
          "team"
        ],
        "admin": [
          "note",
          "reply",
          "edit",
          "stage",
          "assign",
          "files",
          "export",
          "delete",
          "run",
          "forms",
          "automations",
          "team"
        ],
        "manager": [
          "note",
          "reply",
          "edit",
          "stage",
          "assign",
          "files",
          "export",
          "delete",
          "run"
        ],
        "agent": [
          "note",
          "reply",
          "edit",
          "stage",
          "files",
          "run"
        ],
        "viewer": []
      },
      "abilities": [
        "note",
        "reply",
        "edit",
        "stage",
        "assign",
        "files",
        "export",
        "delete",
        "run",
        "forms",
        "automations",
        "team"
      ],
      "notes": "seeing submissions is implied. an agent may assign to themselves only"
    },
    "settings": {
      "enabled": "true switches Submit-Info on for the number",
      "config": {
        "default_prefix": "2-4 letters, default SI",
        "retention_days": "0 = keep; else 30-3650"
      }
    },
    "limits": {
      "forms": 100,
      "steps_per_form": 12,
      "fields_per_step": 12,
      "fields_per_form": 60,
      "definition_kb": 64,
      "stages_per_form": 12,
      "lists": 50,
      "items_per_list": 1000,
      "list_kb": 200,
      "list_items_shown_in_a_select": 200,
      "automations": 200,
      "actions_per_automation": 20,
      "connections": 30,
      "members": 200,
      "files_per_submission": 60,
      "file_mb_whatsapp": 25,
      "file_mb_web_and_api": 10,
      "answers_kb": 64,
      "note_or_reply_characters": 4000,
      "tags_per_submission": 20,
      "tag_characters": 40,
      "page": 50,
      "page_max": 200,
      "run_log_days": 30
    },
    "setup": {
      "shape": "{ dry_run, settings: { enabled, config }, lists: [...], connections: [...], forms: [{ key, name, definition }], automations: [...], publish: [form keys] }. every part is optional",
      "order": "lists and connections are applied first, then forms, then automations. with any problem nothing is written",
      "replaces": "forms, lists and connections by key; automations by name within the same form"
    },
    "presets": [
      {
        "key": "quote",
        "name": "Quote request",
        "description": "What is needed, quantity, photos and address. Staff enter the amount; the customer accepts or declines with a button.",
        "category": "Customers"
      },
      {
        "key": "meter_reading",
        "name": "Meter reading",
        "description": "Meter number, reading and a photo. The usage since the last reading is calculated; odd readings are queried.",
        "category": "Customers"
      },
      {
        "key": "job_completed",
        "name": "Job completed",
        "description": "Field staff log a finished job: the job from a list, work done, parts, hours, photos and the location.",
        "category": "Field staff"
      }
    ],
    "examples": [
      {
        "title": "A quote request the customer accepts or declines with a button",
        "setup": {
          "dry_run": true,
          "settings": {
            "enabled": true
          },
          "lists": [
            {
              "key": "products",
              "name": "Products",
              "items": [
                {
                  "id": "pump-s",
                  "title": "Pump, small",
                  "description": "Up to 40 l/min",
                  "price": 240
                },
                {
                  "id": "pump-l",
                  "title": "Pump, large",
                  "description": "Up to 120 l/min",
                  "price": 610
                }
              ]
            }
          ],
          "connections": [
            {
              "name": "ERP",
              "kind": "http",
              "base_url": "https://erp.example.com/api",
              "auth": {
                "type": "bearer",
                "secret": "YOUR_ERP_TOKEN"
              },
              "headers": {
                "X-Tenant": "acme"
              },
              "enabled": true,
              "key": "erp"
            }
          ],
          "forms": [
            {
              "key": "quote",
              "name": "Quote request",
              "definition": {
                "title": "Quote request",
                "description": "Tell us what you need and we will send a price.",
                "prefix": "QR",
                "steps": [
                  {
                    "key": "need",
                    "title": "What you need",
                    "text": "",
                    "show_if": null,
                    "fields": [
                      {
                        "key": "product",
                        "type": "select",
                        "label": "Product",
                        "required": true,
                        "list": "products"
                      },
                      {
                        "key": "quantity",
                        "type": "number",
                        "label": "How many?",
                        "required": true,
                        "min": 1,
                        "max": 10000,
                        "decimals": 0
                      },
                      {
                        "key": "notes",
                        "type": "textarea",
                        "label": "Anything we should know?",
                        "required": false,
                        "max_length": 1000
                      },
                      {
                        "key": "photos",
                        "type": "photo",
                        "label": "Photos of the site (optional)",
                        "required": false,
                        "max_files": 3,
                        "source": "any"
                      },
                      {
                        "key": "quote_amount",
                        "type": "number",
                        "label": "Quote amount",
                        "internal": true,
                        "decimals": 2,
                        "unit": "USD"
                      }
                    ]
                  },
                  {
                    "key": "delivery",
                    "title": "Delivery",
                    "text": "",
                    "show_if": null,
                    "fields": [
                      {
                        "key": "deliver",
                        "type": "yesno",
                        "label": "Do you need delivery?",
                        "required": true
                      }
                    ]
                  },
                  {
                    "key": "delivery_address",
                    "title": "Delivery address",
                    "text": "",
                    "show_if": {
                      "field": "deliver",
                      "equals": true
                    },
                    "fields": [
                      {
                        "key": "address",
                        "type": "textarea",
                        "label": "Where should we deliver?",
                        "required": true,
                        "max_length": 300
                      }
                    ]
                  }
                ],
                "stages": [
                  {
                    "key": "new",
                    "name": "New",
                    "kind": "open",
                    "color": "blue",
                    "set_by": [],
                    "require_note": false,
                    "message": ""
                  },
                  {
                    "key": "quoted",
                    "name": "Quoted",
                    "kind": "open",
                    "color": "amber",
                    "set_by": [],
                    "require_note": false,
                    "message": ""
                  },
                  {
                    "key": "accepted",
                    "name": "Accepted",
                    "kind": "done",
                    "color": "green",
                    "set_by": [],
                    "require_note": false,
                    "message": "Thank you. We will be in touch about {reference} shortly."
                  },
                  {
                    "key": "declined",
                    "name": "Declined",
                    "kind": "cancelled",
                    "color": "grey",
                    "set_by": [],
                    "require_note": false,
                    "message": ""
                  }
                ],
                "trigger": {
                  "words": [
                    "quote"
                  ],
                  "header": "",
                  "body": "Tap the button to ask for a quote.",
                  "button": "Get a quote",
                  "footer": ""
                },
                "after": {
                  "review_step": true,
                  "reply": "Thanks {contact.name}. Your request {reference} is with us; the price follows shortly.",
                  "allow_additions": true,
                  "status_page": true
                },
                "calculated": [
                  {
                    "key": "estimate",
                    "label": "Estimate",
                    "formula": "quantity * lookup('products', product, 'price')",
                    "unit": "USD",
                    "decimals": 2
                  }
                ]
              }
            }
          ],
          "automations": [
            {
              "name": "Price a quote request in the ERP",
              "form": "quote",
              "enabled": true,
              "trigger": "submitted",
              "options": {},
              "conditions": {
                "all": [
                  {
                    "field": "quantity",
                    "gt": 0
                  }
                ]
              },
              "actions": [
                {
                  "type": "http",
                  "connection": "erp",
                  "method": "POST",
                  "path": "/quotes",
                  "query": {},
                  "headers": {
                    "X-Source": "whatsapp"
                  },
                  "body": {
                    "reference": "{reference}",
                    "customer": {
                      "name": "{contact.name}",
                      "phone": "{contact.phone}"
                    },
                    "product": "{product}",
                    "quantity": "{quantity}",
                    "photos": "{files.photos}"
                  },
                  "save": {
                    "erp_id": "$.id",
                    "quote_amount": "$.total"
                  },
                  "on_fail": "retry"
                },
                {
                  "type": "set_status",
                  "status": "quoted",
                  "note": "Priced by the ERP"
                },
                {
                  "type": "reply",
                  "text": "Your quote {reference}: {quote_amount} USD for {quantity} x {product}. Shall we go ahead?",
                  "buttons": [
                    {
                      "id": "accept",
                      "title": "Accept",
                      "set_status": "accepted"
                    },
                    {
                      "id": "decline",
                      "title": "Decline",
                      "set_status": "declined"
                    }
                  ],
                  "file": "",
                  "link": true
                }
              ]
            },
            {
              "name": "Tell the owner when a quote is accepted",
              "form": "quote",
              "enabled": true,
              "trigger": "status_changed",
              "options": {
                "to": [
                  "accepted"
                ],
                "from": []
              },
              "conditions": null,
              "actions": [
                {
                  "type": "email",
                  "to": [
                    "owner"
                  ],
                  "subject": "Quote {reference} accepted: {quote_amount} USD",
                  "body": "{contact.name} ({contact.phone}) accepted.\n\n{answers}\n\n{desk_link}",
                  "attach_files": false
                }
              ]
            }
          ],
          "publish": [
            "quote"
          ]
        }
      }
    ],
    "this_number": {
      "enabled": true,
      "forms": [
        "meter_reading"
      ],
      "lists": [
        "products"
      ],
      "connections": [
        "erp"
      ]
    }
  }
}
```


### `GET /submit/settings`

Submit-Info settings: the switch, the config and the public code. Scope: `submissions:manage`. Docs: https://www.app2email.com/docs/api/submit-info/get-submit-settings

Scope: `submissions:manage`. `enabled` says whether Submit-Info is switched on for the number (words, links and automations work only then; everything can be set up while it is off). `config` holds every setting with its value: the default reference prefix, the menu and status words, where e-mails go, the time zone, the look of the web pages, shared inbox views and the retention time. `code` is the number's public code in every form and inbox address.


Example answer:

```json
{
  "success": true,
  "request_id": "s1set",
  "enabled": true,
  "config": {
    "business_name": "",
    "default_prefix": "SI",
    "menu_words": [
      "form",
      "forms",
      "report",
      "submit"
    ],
    "menu_text": "What would you like to send us?",
    "status_words": [
      "status"
    ],
    "other_words_limit": 10,
    "notify_email": "",
    "timezone": "",
    "brand": {
      "color": "#2DAE5C",
      "background": "#FFFFFF",
      "hide_branding": false
    },
    "views": [
      {
        "key": "urgent",
        "name": "Urgent",
        "filter": {
          "priority": [
            "urgent"
          ],
          "status_kind": [
            "open"
          ]
        }
      }
    ],
    "retention_days": 0
  },
  "code": "k3xbq9rtzp2mwv7",
  "links": {
    "forms": "https://www.app2email.com/form/k3xbq9rtzp2mwv7",
    "desk": "https://www.app2email.com/desk/k3xbq9rtzp2mwv7",
    "wa_me": "https://wa.me/4976659348270"
  }
}
```


### `PUT /submit/settings`

Switch Submit-Info on or off and change its settings. Scope: `submissions:manage`. Docs: https://www.app2email.com/docs/api/submit-info/update-submit-settings

Scope: `submissions:manage`. Not with a sandbox key. Send `enabled`, `config`, or both (400 `nothing_to_change` with neither). `config` is partial: only the keys you send change. A section such as `brand` is merged key by key; a list such as `menu_words` or `views` replaces what is stored. The result is checked as a whole (400 `invalid_settings` with the problems in `error.details`; nothing is saved then). Switching on makes the forms' words and links answer; a form still needs POST /submit/forms/{key}/publish to open inside WhatsApp.


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| enabled | boolean |  | Switches Submit-Info on or off for the number: words, links and automations. |
| config | object |  | The number's Submit-Info settings. |
|   business_name | string |  | The {business} placeholder and the name on the web pages. "" = the number's verified name. |
|   default_prefix | string |  | 2 to 4 letters A-Z: the reference prefix of forms that have none. |
|   menu_words | array of string |  | A contact who sends one of these gets the form (one form) or a menu of the forms (several). [] = no menu. |
|   menu_text | string |  | The text above the menu. |
|   status_words | array of string |  | A contact with a submission of the last 90 days who sends one of these gets its stage. |
|   other_words_limit | integer |  | A form's word starts the form only when the message has fewer than this many other words, so a long message never starts a form. 0 = a message of any length. Menu and status words also need a message of at most 5 words. |
|   notify_email | string |  | Where the business's e-mails go. "" = the number's Default To address. "off" = none. |
|   timezone | string |  | "" = the number's time zone. |
|   brand | object |  | The look of the web form and the status page. |
|   views | array of object |  | Saved inbox views the whole team shares. |
|   retention_days | integer |  | For forms that set none: 0 = keep, else closed submissions are erased after this many days (30 to 3650). |


Example answer:

```json
{
  "success": true,
  "request_id": "s1set",
  "enabled": true,
  "config": {
    "business_name": "",
    "default_prefix": "SI",
    "menu_words": [
      "form",
      "forms",
      "report",
      "submit"
    ],
    "menu_text": "What would you like to send us?",
    "status_words": [
      "status"
    ],
    "other_words_limit": 10,
    "notify_email": "",
    "timezone": "",
    "brand": {
      "color": "#2DAE5C",
      "background": "#FFFFFF",
      "hide_branding": false
    },
    "views": [
      {
        "key": "urgent",
        "name": "Urgent",
        "filter": {
          "priority": [
            "urgent"
          ],
          "status_kind": [
            "open"
          ]
        }
      }
    ],
    "retention_days": 0
  },
  "code": "k3xbq9rtzp2mwv7",
  "links": {
    "forms": "https://www.app2email.com/form/k3xbq9rtzp2mwv7",
    "desk": "https://www.app2email.com/desk/k3xbq9rtzp2mwv7",
    "wa_me": "https://wa.me/4976659348270"
  }
}
```


### `POST /submit/setup`

Apply or dry-run a whole setup: forms, lists, automations. Scope: `submissions:manage`. Docs: https://www.app2email.com/docs/api/submit-info/apply-submit-setup

Scope: `submissions:manage`. A sandbox key may only make a dry run. The one call that builds a solution: settings, lists, connections, forms and automations in one document (the SubmitSetup schema; GET /submit/guide has complete examples). Always send it with `dry_run` true first: the answer lists every problem with its path and a fix, and writes nothing. When `problems` is empty, send it again without `dry_run`. What exists under the same key is replaced (lists, connections, forms by `key`; automations by `name` within a form); everything else is left alone. With any problem nothing is written at all: 400 `invalid_setup` with the problems in `error.details`. `publish` names the forms to publish to WhatsApp after a clean apply; otherwise call POST /submit/forms/{key}/publish. A form that cannot be published does not undo the rest: the answer is still 200, `applied.published` names the forms that went live and `problems` says why another did not. `preset` in place of the parts installs a ready-made solution. If a save fails half-way (rare) the answer is 500 with `error.details.applied`: send the same document again, every part replaces what is there.


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| dry_run | boolean |  | true: check only. The answer lists every problem and what would be written; nothing is changed. |
| replace | boolean |  | Left out or true: a form whose key already exists is replaced by the one in the document. false: such a form is not overwritten - the answer is 409 `form_exists` and nothing is written. Lists, connections and automations of the same key / name are always replaced. |
| preset | string |  | A preset's key, instead of lists, connections, forms and automations. |
| settings | object |  | As PUT /submit/settings. |
|   enabled | boolean |  | true switches Submit-Info on for the number. |
|   config | object |  | The number's Submit-Info settings. |
| lists | array of object |  | As PUT /submit/lists/{key}, with the key inside. |
| connections | array of object |  | As PUT /submit/connections/{key}, with `key` inside each one. |
| forms | array of object |  | As POST /submit/forms. |
| automations | array of object |  | As POST /submit/automations. |
| publish | array of string |  | Form keys to publish to WhatsApp after everything was written without a problem. Ignored by a dry run. |


Example answer:

```json
{
  "success": true,
  "request_id": "s2stp",
  "dry_run": true,
  "note": "Dry run: no problem found, nothing was saved. Send the same document without dry_run to apply it.",
  "applied": {
    "lists": [
      "products"
    ],
    "connections": [
      "erp"
    ],
    "forms": [
      "quote"
    ],
    "automations": [
      "Price a quote request in the ERP",
      "Tell the owner when a quote is accepted"
    ],
    "published": []
  },
  "problems": []
}
```


### `GET /submit/presets`

The ready-made setups (presets), or one complete preset. Scope: `submissions:manage`. Docs: https://www.app2email.com/docs/api/submit-info/list-submit-presets

Scope: `submissions:manage`. The presets, each with key, name, description and category (Customers or Field staff): quote, application, documents, meter_reading, problem_report, contact_request, complaint, maintenance, feedback, job_completed, proof_of_delivery, expense, inspection, incident, leave_request. Each is a complete setup document (a form with stages, the lists it needs and the automations that go with it). `?key=` returns that one as `preset`: read it, change what you need and send it to POST /submit/setup; or send `{"preset": "<key>"}` there to install it as it is. An unknown key answers 400 `invalid_setup`.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| key | query | string |  | One preset's key: the answer then has key and preset, the complete setup document. |


Example answer:

```json
{
  "success": true,
  "request_id": "p1pre",
  "presets": [
    {
      "key": "quote",
      "name": "Quote request",
      "description": "What is needed, quantity, photos and address. Staff enter the amount; the customer accepts or declines with a button.",
      "category": "Customers"
    },
    {
      "key": "meter_reading",
      "name": "Meter reading",
      "description": "Meter number, reading and a photo. The usage since the last reading is calculated; odd readings are queried.",
      "category": "Customers"
    },
    {
      "key": "job_completed",
      "name": "Job completed",
      "description": "Field staff log a finished job: the job from a list, work done, parts, hours, photos and the location.",
      "category": "Field staff"
    }
  ]
}
```


### `GET /submit/forms`

The forms of the number. Scope: `submissions:manage`. Docs: https://www.app2email.com/docs/api/submit-info/list-forms

Scope: `submissions:manage`. Every form with its key, name, whether it is enabled, archived and published, whether the working copy differs from the published version (`changed`), its state on WhatsApp, its links and how many submissions it has. Definitions are left out: GET /submit/forms/{key} has one form's definition and fields.


Example answer:

```json
{
  "success": true,
  "request_id": "f1lst",
  "forms": [
    {
      "id": 7,
      "key": "meter_reading",
      "name": "Meter reading",
      "enabled": true,
      "archived": false,
      "position": 0,
      "published": {
        "hash": "3f9a1c0b7d2e",
        "published_at": "2026-11-13T04:00:00.000Z"
      },
      "changed": false,
      "flow": {
        "id": "1234567890123456",
        "status": "PUBLISHED",
        "validation_errors": [],
        "checked_at": "2026-11-13T04:00:00.000Z",
        "last_error": "",
        "can_send": true
      },
      "links": {
        "web": "https://www.app2email.com/form/k3xbq9rtzp2mwv7/meter_reading",
        "wa_me": "https://wa.me/4976659348270?text=meter",
        "words": [
          "meter",
          "reading"
        ]
      },
      "counts": {
        "open": 12,
        "total": 148
      },
      "created": "2026-11-12T22:10:00.000Z",
      "updated": "2026-11-13T04:00:00.000Z"
    }
  ],
  "count": 1
}
```


### `POST /submit/forms`

Create a form from a definition or a preset. Scope: `submissions:manage`. Docs: https://www.app2email.com/docs/api/submit-info/create-form

Scope: `submissions:manage`. Not with a sandbox key. Send `name` and `definition` (the SubmitFormDefinition schema explains every key; a minimal form is a title and one step with one field). `name` alone makes a starter form with one question to change. `preset` installs a ready-made solution instead: its form with the lists and automations that belong to it (`applied` in the answer names them). The definition is checked as a whole: 400 `invalid_form` lists every problem with its path (`definition.steps[0].fields[1].label`) and a fix, and nothing is saved. The answer is the form with its normalized definition and its links. The web page works at once; to open the form inside WhatsApp call POST /submit/forms/{key}/publish next. A number has at most 100 forms.


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| key | string |  | The form's key: lower case letters, digits and _, starting with a letter, at most 40 characters (check is reserved). Left out: made from the name. It is part of the web address and cannot be changed later. |
| name | string |  | The name in the dashboard and the inbox. Needed with definition. |
| definition | object |  | A form as one document. The same JSON drives the WhatsApp form (app2email generates it: there is nothing to draw), the web page, the checks on every answer, the inbox columns and the exports. `steps` hold the fields; `stages` are the states a submission moves through; `who`, `trigger`, `after`, `web`, `notify`, `calculated` and `retention_days` are optional and take their defaults when left out. Limits: 12 steps, 12 fields in a step, 60 fields in a form, one location field, 64 KB of JSON. A save is checked as a whole: with any problem nothing is saved and the 400 answer lists each one with its path and a fix. The saved form comes back normalized, with every default filled in. Saving changes the working copy; WhatsApp keeps showing the published version until POST /submit/forms/{key}/publish is called again. Conditions: a step or a field with `show_if` appears only when its rule holds, and the rule may only look at fields of earlier steps. A rule is {"field": "<key>", <operator>: <value>} with the operators equals, not_equals, in, not_in, contains, empty, not_empty, gt, gte, lt, lte. Every operator written in one rule must hold. When the field's value is an array (multiselect, tags) a rule holds when any item matches, except not_equals and not_in, which need every item. Rules combine as {"all": [rule, ...]} (every one) or {"any": [rule, ...]} (at least one); groups nest 2 deep with up to 10 rules each. null = no condition. Examples: {"field": "deliver", "equals": true}; {"all": [{"field": "amount", "gt": 5000}, {"field": "category", "in": ["plant", "vehicle"]}]}. |
|   title | string | yes | The form's public name, 1 to 60 characters. |
|   description | string |  | Under the title on the web page and in the forms menu, up to 300 characters. |
|   prefix | string |  | 2 to 4 letters A-Z that start every reference of this form (MR-7Q3M2A). "" = the settings' default_prefix. |
|   steps | array of object | yes | 1 to 12 steps, in the order they are asked. One step is one screen; app2email splits a step over several screens by itself when WhatsApp's limits demand it. |
|   stages | array of object |  | 2 to 12 stages a submission moves through. The first one is where a new submission starts. At least one of kind open and one of kind done. Left out: New (open), In progress (open), Done (done). |
|   who | object |  | Who may submit. |
|   trigger | object |  | The message that opens the form on WhatsApp, and the words that send it. |
|   after | object |  | What happens right after a submission. |
|   web | object |  | The web page of the form. |
|   notify | object |  | The e-mail the business gets. |
|   calculated | array of object |  | 0 to 20 calculated fields: values worked out from the answers each time they change, stored in extra. Formulas (calculated fields, the calculate action, and {= ... } inside any text): numbers, 'texts' in single quotes, field keys, + - * / %, the comparisons == != > >= < <=, and / or / not, brackets, and the functions if(condition, then, else): then when the condition holds, otherwise else (null without an else). min(a, b, ...): The smallest number. max(a, b, ...): The largest number. round(x, decimals): x rounded, half away from zero; decimals 0 to 10, default 0. abs(x): x without its sign. num(x): x as a number, null when it is not one. len(x): The length of a text, or the number of items of a list. coalesce(a, b, ...): The first value that is not empty. lower(x): x in lower case. upper(x): x in upper case. concat(a, b, ...): The values joined as one text. lookup('<list>', id, '<column>'): A column of the item with that id in a list of the number, for example a price. previous('<field>'): The same contact's last value of that field in this form. count_files('<field>'): How many files a photo or document field holds. days_since(date): Whole days from a date (YYYY-MM-DD) to today; negative for a date to come. No loops and no assignment; at most 500 characters; a division by zero or a missing number gives null. Examples: reading - previous('reading'); quantity * lookup('products', product, 'price'); if(usage < 0, 'check', 'ok'); round(amount * 1.2, 2); days_since(purchase_date) > 30 and count_files('receipt') == 0. |
|   retention_days | integer |  | 0 = keep. Otherwise closed submissions and their files are erased this many days after closing (30 to 3650). |
| preset | string |  | Instead of a definition: install this preset (GET /submit/presets): its form together with the lists and automations that belong to it. key and name, when given, rename its form. |


### `GET /submit/forms/{key}`

One form: definition, fields, links and WhatsApp state. Scope: `submissions:manage`. Docs: https://www.app2email.com/docs/api/submit-info/get-form

Scope: `submissions:manage`. The form's working definition with every default filled in, `fields` (every field and calculated value as a column: the keys to read in a submission's answers and extra), `links` (the web page, the wa.me link, the words), `published` and `changed` (does WhatsApp show the latest version?) and `flow` (Meta's status and complaints). Read it before changing a definition: PUT takes the whole definition back.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| key | path | string | yes | The form's key (GET /submit/forms). |


Example answer:

```json
{
  "success": true,
  "request_id": "f3get",
  "form": {
    "id": 7,
    "key": "meter_reading",
    "name": "Meter reading",
    "enabled": true,
    "archived": false,
    "position": 0,
    "published": {
      "hash": "3f9a1c0b7d2e",
      "published_at": "2026-11-13T04:00:00.000Z"
    },
    "changed": false,
    "flow": {
      "id": "1234567890123456",
      "status": "PUBLISHED",
      "validation_errors": [],
      "checked_at": "2026-11-13T04:00:00.000Z",
      "last_error": "",
      "can_send": true
    },
    "links": {
      "web": "https://www.app2email.com/form/k3xbq9rtzp2mwv7/meter_reading",
      "wa_me": "https://wa.me/4976659348270?text=meter",
      "words": [
        "meter",
        "reading"
      ]
    },
    "counts": {
      "open": 12,
      "total": 148
    },
    "created": "2026-11-12T22:10:00.000Z",
    "updated": "2026-11-13T04:00:00.000Z",
    "definition": {
      "title": "Meter reading",
      "description": "Send us this month's reading.",
      "prefix": "MR",
      "steps": [
        {
          "key": "reading",
          "title": "Your reading",
          "text": "",
          "show_if": null,
          "fields": [
            {
              "key": "meter_no",
              "type": "text",
              "label": "Meter number",
              "help": "On the front of the meter",
              "required": true,
              "default": "{contact.meter_no}",
              "max_length": 20
            },
            {
              "key": "reading",
              "type": "number",
              "label": "Meter reading",
              "required": true,
              "min": 0,
              "max": 999999,
              "decimals": 0,
              "unit": "kWh"
            },
            {
              "key": "photo",
              "type": "photo",
              "label": "Photo of the meter",
              "required": true,
              "max_files": 1,
              "source": "camera"
            },
            {
              "key": "moving",
              "type": "yesno",
              "label": "Are you moving out?",
              "required": true
            },
            {
              "key": "billing_ref",
              "type": "text",
              "label": "Billing reference",
              "internal": true
            }
          ]
        },
        {
          "key": "move",
          "title": "Your move",
          "text": "We will close the account on that day.",
          "show_if": {
            "field": "moving",
            "equals": true
          },
          "fields": [
            {
              "key": "move_date",
              "type": "date",
              "label": "Moving date",
              "required": true,
              "min_days": -30,
              "max_days": 90
            },
            {
              "key": "new_address",
              "type": "textarea",
              "label": "New address for the final bill",
              "required": false,
              "max_length": 300
            }
          ]
        }
      ],
      "stages": [
        {
          "key": "received",
          "name": "Received",
          "kind": "open",
          "color": "blue",
          "set_by": [],
          "require_note": false,
          "message": ""
        },
        {
          "key": "queried",
          "name": "Queried",
          "kind": "open",
          "color": "amber",
          "set_by": [],
          "require_note": true,
          "message": "We have a question about your reading {reference}: {note}"
        },
        {
          "key": "checked",
          "name": "Checked",
          "kind": "done",
          "color": "green",
          "set_by": [
            "manager"
          ],
          "require_note": false,
          "message": "Thanks {contact.name}, your reading of {reading} kWh is recorded."
        }
      ],
      "who": {
        "mode": "anyone",
        "numbers": [],
        "tag": ""
      },
      "trigger": {
        "words": [
          "meter",
          "reading"
        ],
        "header": "",
        "body": "Tap the button to send your reading.",
        "button": "Open form",
        "footer": ""
      },
      "after": {
        "review_step": true,
        "reply": "Thanks {contact.name}. We have your {form} - reference {reference}.",
        "allow_additions": false,
        "status_page": true
      },
      "web": {
        "enabled": true,
        "verify": "optional",
        "ask_email": false,
        "success_text": ""
      },
      "notify": {
        "email": true,
        "to": [],
        "attach_files": true
      },
      "calculated": [
        {
          "key": "usage",
          "label": "Usage",
          "formula": "reading - previous('reading')",
          "unit": "kWh",
          "decimals": 0
        }
      ],
      "retention_days": 0
    },
    "fields": [
      {
        "key": "meter_no",
        "label": "Meter number",
        "type": "text",
        "step": "reading",
        "internal": false
      },
      {
        "key": "reading",
        "label": "Meter reading",
        "type": "number",
        "step": "reading",
        "internal": false,
        "unit": "kWh"
      },
      {
        "key": "photo",
        "label": "Photo of the meter",
        "type": "photo",
        "step": "reading",
        "internal": false
      },
      {
        "key": "moving",
        "label": "Are you moving out?",
        "type": "yesno",
        "step": "reading",
        "internal": false
      },
      {
        "key": "billing_ref",
        "label": "Billing reference",
        "type": "text",
        "step": "reading",
        "internal": true
      },
      {
        "key": "move_date",
        "label": "Moving date",
        "type": "date",
        "step": "move",
        "internal": false
      },
      {
        "key": "new_address",
        "label": "New address for the final bill",
        "type": "textarea",
        "step": "move",
        "internal": false
      },
      {
        "key": "usage",
        "label": "Usage",
        "type": "number",
        "step": "",
        "internal": true,
        "unit": "kWh",
        "calculated": true
      }
    ]
  }
}
```


### `PUT /submit/forms/{key}`

Change a form: name, on or off, archive, definition. Scope: `submissions:manage`. Docs: https://www.app2email.com/docs/api/submit-info/update-form

Scope: `submissions:manage`. Not with a sandbox key. Any of `name`, `enabled`, `archived`, `position`, `definition` (400 `nothing_to_change` with none). A `definition` replaces the whole working copy, so read the form, change it and send all of it back; it is checked as a whole (400 `invalid_form`, nothing saved). The web page follows the saved definition. WhatsApp keeps showing the published version: call POST /submit/forms/{key}/publish to make a changed definition live there. Submissions already made keep their answers; a removed field stays readable in them.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| key | path | string | yes | The form's key (GET /submit/forms). |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| name | string |  |  |
| enabled | boolean |  | false: the form stops answering its words and links. |
| archived | boolean |  | true: hide the form and stop taking submissions. Its submissions stay. |
| position | integer |  | Its place in the lists and in the forms menu, lowest first. |
| definition | object |  | A form as one document. The same JSON drives the WhatsApp form (app2email generates it: there is nothing to draw), the web page, the checks on every answer, the inbox columns and the exports. `steps` hold the fields; `stages` are the states a submission moves through; `who`, `trigger`, `after`, `web`, `notify`, `calculated` and `retention_days` are optional and take their defaults when left out. Limits: 12 steps, 12 fields in a step, 60 fields in a form, one location field, 64 KB of JSON. A save is checked as a whole: with any problem nothing is saved and the 400 answer lists each one with its path and a fix. The saved form comes back normalized, with every default filled in. Saving changes the working copy; WhatsApp keeps showing the published version until POST /submit/forms/{key}/publish is called again. Conditions: a step or a field with `show_if` appears only when its rule holds, and the rule may only look at fields of earlier steps. A rule is {"field": "<key>", <operator>: <value>} with the operators equals, not_equals, in, not_in, contains, empty, not_empty, gt, gte, lt, lte. Every operator written in one rule must hold. When the field's value is an array (multiselect, tags) a rule holds when any item matches, except not_equals and not_in, which need every item. Rules combine as {"all": [rule, ...]} (every one) or {"any": [rule, ...]} (at least one); groups nest 2 deep with up to 10 rules each. null = no condition. Examples: {"field": "deliver", "equals": true}; {"all": [{"field": "amount", "gt": 5000}, {"field": "category", "in": ["plant", "vehicle"]}]}. |
|   title | string | yes | The form's public name, 1 to 60 characters. |
|   description | string |  | Under the title on the web page and in the forms menu, up to 300 characters. |
|   prefix | string |  | 2 to 4 letters A-Z that start every reference of this form (MR-7Q3M2A). "" = the settings' default_prefix. |
|   steps | array of object | yes | 1 to 12 steps, in the order they are asked. One step is one screen; app2email splits a step over several screens by itself when WhatsApp's limits demand it. |
|   stages | array of object |  | 2 to 12 stages a submission moves through. The first one is where a new submission starts. At least one of kind open and one of kind done. Left out: New (open), In progress (open), Done (done). |
|   who | object |  | Who may submit. |
|   trigger | object |  | The message that opens the form on WhatsApp, and the words that send it. |
|   after | object |  | What happens right after a submission. |
|   web | object |  | The web page of the form. |
|   notify | object |  | The e-mail the business gets. |
|   calculated | array of object |  | 0 to 20 calculated fields: values worked out from the answers each time they change, stored in extra. Formulas (calculated fields, the calculate action, and {= ... } inside any text): numbers, 'texts' in single quotes, field keys, + - * / %, the comparisons == != > >= < <=, and / or / not, brackets, and the functions if(condition, then, else): then when the condition holds, otherwise else (null without an else). min(a, b, ...): The smallest number. max(a, b, ...): The largest number. round(x, decimals): x rounded, half away from zero; decimals 0 to 10, default 0. abs(x): x without its sign. num(x): x as a number, null when it is not one. len(x): The length of a text, or the number of items of a list. coalesce(a, b, ...): The first value that is not empty. lower(x): x in lower case. upper(x): x in upper case. concat(a, b, ...): The values joined as one text. lookup('<list>', id, '<column>'): A column of the item with that id in a list of the number, for example a price. previous('<field>'): The same contact's last value of that field in this form. count_files('<field>'): How many files a photo or document field holds. days_since(date): Whole days from a date (YYYY-MM-DD) to today; negative for a date to come. No loops and no assignment; at most 500 characters; a division by zero or a missing number gives null. Examples: reading - previous('reading'); quantity * lookup('products', product, 'price'); if(usage < 0, 'check', 'ok'); round(amount * 1.2, 2); days_since(purchase_date) > 30 and count_files('receipt') == 0. |
|   retention_days | integer |  | 0 = keep. Otherwise closed submissions and their files are erased this many days after closing (30 to 3650). |


Example answer:

```json
{
  "success": true,
  "request_id": "f4upd",
  "form": {
    "id": 7,
    "key": "meter_reading",
    "name": "Meter reading",
    "enabled": true,
    "archived": false,
    "position": 0,
    "published": {
      "hash": "3f9a1c0b7d2e",
      "published_at": "2026-11-13T04:00:00.000Z"
    },
    "changed": true,
    "flow": {
      "id": "1234567890123456",
      "status": "PUBLISHED",
      "validation_errors": [],
      "checked_at": "2026-11-13T04:00:00.000Z",
      "last_error": "",
      "can_send": true
    },
    "links": {
      "web": "https://www.app2email.com/form/k3xbq9rtzp2mwv7/meter_reading",
      "wa_me": "https://wa.me/4976659348270?text=meter",
      "words": [
        "meter",
        "reading"
      ]
    },
    "counts": {
      "open": 12,
      "total": 148
    },
    "created": "2026-11-12T22:10:00.000Z",
    "updated": "2026-11-13T04:00:00.000Z",
    "definition": {
      "title": "Meter reading",
      "description": "Send us this month's reading.",
      "prefix": "MR",
      "steps": [
        {
          "key": "reading",
          "title": "Your reading",
          "text": "",
          "show_if": null,
          "fields": [
            {
              "key": "meter_no",
              "type": "text",
              "label": "Meter number",
              "help": "On the front of the meter",
              "required": true,
              "default": "{contact.meter_no}",
              "max_length": 20
            },
            {
              "key": "reading",
              "type": "number",
              "label": "Meter reading",
              "required": true,
              "min": 0,
              "max": 999999,
              "decimals": 0,
              "unit": "kWh"
            },
            {
              "key": "photo",
              "type": "photo",
              "label": "Photo of the meter",
              "required": true,
              "max_files": 1,
              "source": "camera"
            },
            {
              "key": "moving",
              "type": "yesno",
              "label": "Are you moving out?",
              "required": true
            },
            {
              "key": "billing_ref",
              "type": "text",
              "label": "Billing reference",
              "internal": true
            }
          ]
        },
        {
          "key": "move",
          "title": "Your move",
          "text": "We will close the account on that day.",
          "show_if": {
            "field": "moving",
            "equals": true
          },
          "fields": [
            {
              "key": "move_date",
              "type": "date",
              "label": "Moving date",
              "required": true,
              "min_days": -30,
              "max_days": 90
            },
            {
              "key": "new_address",
              "type": "textarea",
              "label": "New address for the final bill",
              "required": false,
              "max_length": 300
            }
          ]
        }
      ],
      "stages": [
        {
          "key": "received",
          "name": "Received",
          "kind": "open",
          "color": "blue",
          "set_by": [],
          "require_note": false,
          "message": ""
        },
        {
          "key": "queried",
          "name": "Queried",
          "kind": "open",
          "color": "amber",
          "set_by": [],
          "require_note": true,
          "message": "We have a question about your reading {reference}: {note}"
        },
        {
          "key": "checked",
          "name": "Checked",
          "kind": "done",
          "color": "green",
          "set_by": [
            "manager"
          ],
          "require_note": false,
          "message": "Thanks {contact.name}, your reading of {reading} kWh is recorded."
        }
      ],
      "who": {
        "mode": "anyone",
        "numbers": [],
        "tag": ""
      },
      "trigger": {
        "words": [
          "meter",
          "reading"
        ],
        "header": "",
        "body": "Tap the button to send your reading.",
        "button": "Open form",
        "footer": ""
      },
      "after": {
        "review_step": true,
        "reply": "Thanks {contact.name}. We have your {form} - reference {reference}.",
        "allow_additions": false,
        "status_page": true
      },
      "web": {
        "enabled": true,
        "verify": "optional",
        "ask_email": false,
        "success_text": ""
      },
      "notify": {
        "email": true,
        "to": [],
        "attach_files": true
      },
      "calculated": [
        {
          "key": "usage",
          "label": "Usage",
          "formula": "reading - previous('reading')",
          "unit": "kWh",
          "decimals": 0
        }
      ],
      "retention_days": 0
    },
    "fields": [
      {
        "key": "meter_no",
        "label": "Meter number",
        "type": "text",
        "step": "reading",
        "internal": false
      },
      {
        "key": "reading",
        "label": "Meter reading",
        "type": "number",
        "step": "reading",
        "internal": false,
        "unit": "kWh"
      },
      {
        "key": "photo",
        "label": "Photo of the meter",
        "type": "photo",
        "step": "reading",
        "internal": false
      },
      {
        "key": "moving",
        "label": "Are you moving out?",
        "type": "yesno",
        "step": "reading",
        "internal": false
      },
      {
        "key": "billing_ref",
        "label": "Billing reference",
        "type": "text",
        "step": "reading",
        "internal": true
      },
      {
        "key": "move_date",
        "label": "Moving date",
        "type": "date",
        "step": "move",
        "internal": false
      },
      {
        "key": "new_address",
        "label": "New address for the final bill",
        "type": "textarea",
        "step": "move",
        "internal": false
      },
      {
        "key": "usage",
        "label": "Usage",
        "type": "number",
        "step": "",
        "internal": true,
        "unit": "kWh",
        "calculated": true
      }
    ]
  }
}
```


### `DELETE /submit/forms/{key}`

Delete a form (archived when it has submissions). Scope: `submissions:manage`. Docs: https://www.app2email.com/docs/api/submit-info/delete-form

Scope: `submissions:manage`. Not with a sandbox key. A form without submissions is deleted, and its WhatsApp version is retired: form messages already sent stop opening. A form that has submissions is never deleted, because they belong to it: it is archived instead (no longer offered, its submissions stay) and the answer says `deleted` false, `archived` true with a note. PUT /submit/forms/{key} `{"archived": false}` brings an archived form back.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| key | path | string | yes | The form's key (GET /submit/forms). |


Example answer:

```json
{
  "success": true,
  "request_id": "f5del",
  "deleted": true,
  "archived": false,
  "key": "meter_reading"
}
```


### `POST /submit/forms/{key}/publish`

Publish a form to WhatsApp. Scope: `submissions:manage`. Docs: https://www.app2email.com/docs/api/submit-info/publish-form

Scope: `submissions:manage`. Not with a sandbox key. Builds the WhatsApp form from the saved definition, uploads it to Meta and publishes it. From then on the form's words, POST /submit/forms/{key}/send and the menu open it inside WhatsApp. Call it after creating a form and after every change of its definition. 400 `invalid_form` when the definition cannot be built into a WhatsApp form (the message says what to change). 409 `form_not_published` when the form is archived, the number's encryption key is not accepted by WhatsApp yet, or WhatsApp found problems in the generated form (`error.details.validation_errors` has them). 502 `whatsapp_flow_failed` when WhatsApp refused a call: try again in a minute. People who still have an older message keep the version it was sent with. A form that is not published still works through its web link.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| key | path | string | yes | The form's key (GET /submit/forms). |


Example answer:

```json
{
  "success": true,
  "request_id": "f6pub",
  "form": {
    "id": 7,
    "key": "meter_reading",
    "name": "Meter reading",
    "enabled": true,
    "archived": false,
    "position": 0,
    "published": {
      "hash": "3f9a1c0b7d2e",
      "published_at": "2026-11-13T04:00:00.000Z"
    },
    "changed": false,
    "flow": {
      "id": "1234567890123456",
      "status": "PUBLISHED",
      "validation_errors": [],
      "checked_at": "2026-11-13T04:00:00.000Z",
      "last_error": "",
      "can_send": true
    },
    "links": {
      "web": "https://www.app2email.com/form/k3xbq9rtzp2mwv7/meter_reading",
      "wa_me": "https://wa.me/4976659348270?text=meter",
      "words": [
        "meter",
        "reading"
      ]
    },
    "counts": {
      "open": 12,
      "total": 148
    },
    "created": "2026-11-12T22:10:00.000Z",
    "updated": "2026-11-13T04:00:00.000Z",
    "definition": {
      "title": "Meter reading",
      "description": "Send us this month's reading.",
      "prefix": "MR",
      "steps": [
        {
          "key": "reading",
          "title": "Your reading",
          "text": "",
          "show_if": null,
          "fields": [
            {
              "key": "meter_no",
              "type": "text",
              "label": "Meter number",
              "help": "On the front of the meter",
              "required": true,
              "default": "{contact.meter_no}",
              "max_length": 20
            },
            {
              "key": "reading",
              "type": "number",
              "label": "Meter reading",
              "required": true,
              "min": 0,
              "max": 999999,
              "decimals": 0,
              "unit": "kWh"
            },
            {
              "key": "photo",
              "type": "photo",
              "label": "Photo of the meter",
              "required": true,
              "max_files": 1,
              "source": "camera"
            },
            {
              "key": "moving",
              "type": "yesno",
              "label": "Are you moving out?",
              "required": true
            },
            {
              "key": "billing_ref",
              "type": "text",
              "label": "Billing reference",
              "internal": true
            }
          ]
        },
        {
          "key": "move",
          "title": "Your move",
          "text": "We will close the account on that day.",
          "show_if": {
            "field": "moving",
            "equals": true
          },
          "fields": [
            {
              "key": "move_date",
              "type": "date",
              "label": "Moving date",
              "required": true,
              "min_days": -30,
              "max_days": 90
            },
            {
              "key": "new_address",
              "type": "textarea",
              "label": "New address for the final bill",
              "required": false,
              "max_length": 300
            }
          ]
        }
      ],
      "stages": [
        {
          "key": "received",
          "name": "Received",
          "kind": "open",
          "color": "blue",
          "set_by": [],
          "require_note": false,
          "message": ""
        },
        {
          "key": "queried",
          "name": "Queried",
          "kind": "open",
          "color": "amber",
          "set_by": [],
          "require_note": true,
          "message": "We have a question about your reading {reference}: {note}"
        },
        {
          "key": "checked",
          "name": "Checked",
          "kind": "done",
          "color": "green",
          "set_by": [
            "manager"
          ],
          "require_note": false,
          "message": "Thanks {contact.name}, your reading of {reading} kWh is recorded."
        }
      ],
      "who": {
        "mode": "anyone",
        "numbers": [],
        "tag": ""
      },
      "trigger": {
        "words": [
          "meter",
          "reading"
        ],
        "header": "",
        "body": "Tap the button to send your reading.",
        "button": "Open form",
        "footer": ""
      },
      "after": {
        "review_step": true,
        "reply": "Thanks {contact.name}. We have your {form} - reference {reference}.",
        "allow_additions": false,
        "status_page": true
      },
      "web": {
        "enabled": true,
        "verify": "optional",
        "ask_email": false,
        "success_text": ""
      },
      "notify": {
        "email": true,
        "to": [],
        "attach_files": true
      },
      "calculated": [
        {
          "key": "usage",
          "label": "Usage",
          "formula": "reading - previous('reading')",
          "unit": "kWh",
          "decimals": 0
        }
      ],
      "retention_days": 0
    },
    "fields": [
      {
        "key": "meter_no",
        "label": "Meter number",
        "type": "text",
        "step": "reading",
        "internal": false
      },
      {
        "key": "reading",
        "label": "Meter reading",
        "type": "number",
        "step": "reading",
        "internal": false,
        "unit": "kWh"
      },
      {
        "key": "photo",
        "label": "Photo of the meter",
        "type": "photo",
        "step": "reading",
        "internal": false
      },
      {
        "key": "moving",
        "label": "Are you moving out?",
        "type": "yesno",
        "step": "reading",
        "internal": false
      },
      {
        "key": "billing_ref",
        "label": "Billing reference",
        "type": "text",
        "step": "reading",
        "internal": true
      },
      {
        "key": "move_date",
        "label": "Moving date",
        "type": "date",
        "step": "move",
        "internal": false
      },
      {
        "key": "new_address",
        "label": "New address for the final bill",
        "type": "textarea",
        "step": "move",
        "internal": false
      },
      {
        "key": "usage",
        "label": "Usage",
        "type": "number",
        "step": "",
        "internal": true,
        "unit": "kWh",
        "calculated": true
      }
    ]
  },
  "note": "Published. The form's words and its send route now open this version on WhatsApp."
}
```


### `POST /submit/forms/{key}/send`

Send a form to a contact, with values filled in. Scope: `submissions:manage`. Docs: https://www.app2email.com/docs/api/submit-info/send-form

Scope: `submissions:manage`. Not with a sandbox key. Sends the form to one contact, with `prefill` values you already know (a job number, an account, the documents wanted). The WhatsApp form goes out when the form is published and the contact wrote to the number in the last 24 hours; a form that is not published goes out as a message with a button to the contact's personal web link. Outside the 24 hour window, or when a form message went to the contact less than 2 minutes ago, nothing is sent: the answer is still 200 with `sent` false and `note` saying why. `link` is always returned: when nothing was sent, send it yourself, for example in an approved template. `link_only` true sends nothing and just returns the link. `parent` makes the new submission a follow-up of an earlier one. The answers arrive as `submission.created`. 403 `submit_not_enabled` while Submit-Info is switched off; 409 `form_not_published` when the form is switched off or archived; 403 `recipient_opted_out` when the contact asked not to be messaged.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| key | path | string | yes | The form's key (GET /submit/forms). |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| to | string | yes | The contact's WhatsApp number with country code, digits only, or their business-scoped user id. |
| name | string |  | Their name, when you know it. |
| prefill | object |  | Values the form starts with: {key: value}. A field reads one with default {prefill.<key>}; a hidden field carries it into the submission unseen. |
| parent | string |  | A submission (id or reference) the new one adds to: a follow-up. |
| text | string |  | The message with the form button. Left out: the form's own trigger body. |
| link_only | boolean |  | true: send nothing, only make the personal link and return it. |


Example answer:

```json
{
  "success": true,
  "request_id": "f7snd",
  "sent": true,
  "sent_flow": true,
  "link": "https://www.app2email.com/form/k3xbq9rtzp2mwv7/meter_reading?t=si1.eyJuIjoxMzJ9.c2FtcGxl",
  "session_id": 518,
  "to": "61412345678",
  "note": "Sent as a WhatsApp form."
}
```


### `GET /submit/lists`

The choice lists (sites, jobs, price lists). Scope: `submissions:manage`. Docs: https://www.app2email.com/docs/api/submit-info/list-submit-lists

Scope: `submissions:manage`. Lists hold choices outside the forms. A select field with `list` set to a list's key shows its items, read fresh each time the form opens, so a list can change every day without publishing anything. Formulas read the other columns of an item: `lookup('products', product, 'price')`.


Example answer:

```json
{
  "success": true,
  "request_id": "l1lst",
  "lists": [
    {
      "key": "products",
      "name": "Products",
      "items": [
        {
          "id": "pump-s",
          "title": "Pump, small",
          "description": "Up to 40 l/min",
          "price": 240
        },
        {
          "id": "pump-l",
          "title": "Pump, large",
          "description": "Up to 120 l/min",
          "price": 610
        }
      ],
      "count": 2,
      "updated": "2026-11-13T04:00:00.000Z"
    }
  ],
  "count": 1
}
```


### `PUT /submit/lists/{key}`

Create a list or replace its items. Scope: `submissions:manage`. Docs: https://www.app2email.com/docs/api/submit-info/set-submit-list

Scope: `submissions:manage`. Not with a sandbox key. Makes the list when the key is new; otherwise replaces its name and ALL its items (send the full list every time, for example from a nightly sync of jobs or prices). Each item needs a unique `id` (stored as the answer) and a `title` (what people see; left out, the id); any other key is a column for formulas. A plain text instead of an object is an item whose id and title are that text. Up to 1,000 items and 200 KB; a form shows the first 200. Forms pick the change up at once: no publish is needed. A number has at most 50 lists.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| key | path | string | yes | The list's key: lower case letters, digits and _, starting with a letter. |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| name | string |  | Left out: the key. |
| items | array of object | yes | ALL the items: they replace what is stored. Up to 1,000 items and 200 KB. |


Example answer:

```json
{
  "success": true,
  "request_id": "l2set",
  "list": {
    "key": "products",
    "name": "Products",
    "items": [
      {
        "id": "pump-s",
        "title": "Pump, small",
        "description": "Up to 40 l/min",
        "price": 240
      },
      {
        "id": "pump-l",
        "title": "Pump, large",
        "description": "Up to 120 l/min",
        "price": 610
      }
    ],
    "count": 2,
    "updated": "2026-11-13T04:00:00.000Z"
  }
}
```


### `DELETE /submit/lists/{key}`

Delete a list. Scope: `submissions:manage`. Docs: https://www.app2email.com/docs/api/submit-info/delete-submit-list

Scope: `submissions:manage`. Not with a sandbox key. A select field that still names the list then shows one line, Nothing to choose, until the list is made again or the question is changed. `used_by` in the answer names those forms.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| key | path | string | yes | The list's key: lower case letters, digits and _, starting with a letter. |


Example answer:

```json
{
  "success": true,
  "request_id": "l3del",
  "deleted": true,
  "key": "products",
  "used_by": [
    "quote"
  ],
  "note": "Deleted. The forms in used_by still name this list: their question now shows \"Nothing to choose\" until the list is made again or the question is changed."
}
```


### `GET /submit/submissions`

The submissions, filtered and paged (JSON or CSV). Scope: `submissions:manage`. Docs: https://www.app2email.com/docs/api/submit-info/list-submissions

Scope: `submissions:manage`. Latest change first; deleted ones are left out. Filter by form, stage (`status`, or `status_kind` open / done / cancelled), assignee, priority, tag, channel, contact, a search text, the creation time or the parent. `form`, `status`, `status_kind`, `assignee`, `priority`, `tag` and `channel` take several values with commas. To keep another system in step, poll with `updated_after` set to the largest `updated` you have seen and `sort=updated_asc`, or use the `submission.*` webhook events and skip polling. Page with `next_cursor` (the same filter and sort). `format=csv` (or the header `Accept: text/csv`) answers the same page as CSV, one column per field when one `form` is given; the next cursor is then in the header `X-Next-Cursor`. Lists leave out files and activity: GET /submit/submissions/{id} has them. A filter value that cannot be read answers 400 `invalid_submission` and names it; an unknown `parent` answers an empty list.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| form | query | string |  | Only this form (its key). Several: keys with commas. |
| status | query | string |  | Only these stages: stage keys of the form, with commas. |
| status_kind | query | string |  | Only stages of this kind: open, done or cancelled (several with commas). |
| assignee | query | string |  | Only what these members hold: member ids with commas. 0 = not assigned. |
| priority | query | string |  | low, normal, high or urgent; several with commas. |
| tag | query | string |  | Only submissions with one of these tags (commas). |
| channel | query | string |  | whatsapp, web, api or staff; several with commas. |
| contact | query | string |  | Only this person's (number with country code, or business-scoped user id). |
| q | query | string |  | The reference, a name or an answer contains this text. |
| created_from | query | string |  | Created on or after this day (YYYY-MM-DD) or ISO 8601 time. |
| created_to | query | string |  | Created up to and including this day (YYYY-MM-DD), or before this ISO 8601 time. |
| updated_after | query | string |  | Changed after this ISO 8601 time: for syncing. |
| parent | query | string |  | Only the follow-ups of this submission (id or reference). |
| sort | query | string (updated \| created \| due \| priority \| updated_asc \| created_asc \| due_asc \| priority_asc) |  | updated (default), created, due or priority; add _asc for the opposite order. |
| format | query | string (json \| csv) |  | csv: a text/csv answer. |
| limit | query | integer |  | How many (1 to 200, default 50). |
| cursor | query | string |  | The next_cursor of the previous answer, unchanged. Leave out for the first page. |


Example answer:

```json
{
  "success": true,
  "request_id": "s1lst",
  "submissions": [
    {
      "id": 4182,
      "reference": "MR-7Q3M2A",
      "form": {
        "key": "meter_reading",
        "name": "Meter reading"
      },
      "channel": "whatsapp",
      "status": "received",
      "status_name": "Received",
      "status_kind": "open",
      "status_color": "blue",
      "priority": "normal",
      "tags": [
        "north"
      ],
      "due": null,
      "assignee": {
        "id": 12,
        "name": "Sam"
      },
      "contact": {
        "identity": "61412345678",
        "name": "John Smith",
        "phone": "61412345678",
        "email": "",
        "verified": true
      },
      "conversation_id": 8762,
      "answers": {
        "meter_no": "A-1182",
        "reading": 48213,
        "photo": [
          9917
        ],
        "moving": false
      },
      "extra": {
        "usage": 312
      },
      "location": null,
      "parent": null,
      "summary": "A-1182 · 48213",
      "files_count": 1,
      "files_pending": 0,
      "unread": true,
      "link": "https://www.app2email.com/s/4mXk9QpL2vTz8RwY3nBc6HdJ5sFg7Ka1",
      "created": "2026-11-13T04:00:00.000Z",
      "updated": "2026-11-13T04:00:00.000Z",
      "status_changed": "2026-11-13T04:00:00.000Z",
      "closed": null
    }
  ],
  "count": 1
}
```


### `POST /submit/submissions`

Create a submission from data you already hold. Scope: `submissions:manage`. Docs: https://www.app2email.com/docs/api/submit-info/create-submission

Scope: `submissions:manage`. Not with a sandbox key. For a system that already has the answers (a web shop, a call centre, an import). `form` is the form's key; `answers` are checked exactly like a customer's (required fields, ranges, choice ids: 400 `invalid_submission` names each field in `error.details`); `extra` fills internal fields; `files` attach base64 files to photo and document fields (up to 20 in one request, 10 MB each); `assignee` and `location` are optional. The submission gets a reference, starts in the form's first stage (or `status`), has channel `api`, and runs the form's automations like any other. No message is sent to the contact by this call itself; the form's automations may send one. `submission.created` is sent. Send an `Idempotency-Key` header to retry safely: the same key and body within 24 hours gets the first answer again.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| Idempotency-Key | header | string |  | Optional. A unique value for this message or list (eg a UUID). The same request with the same key within 24 hours gets the first answer again, and nothing is sent twice. Ignored by dry runs. |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| form | string | yes | The form's key. An archived form takes no submissions. |
| contact | string |  | The person's WhatsApp number with country code, digits only, or their business-scoped user id. Left out: a submission without a WhatsApp contact. |
| contact_name | string |  |  |
| contact_email | string |  |  |
| answers | object | yes | Field key -> value, typed as the field types say. Checked like a customer's answers: required fields, ranges, choice ids. |
| extra | object |  | Values for internal fields, and anything else to keep with it. |
| status | string |  | A stage key to start in. Left out: the form's first stage. |
| assignee | integer |  | A member's id (GET /submit/members) to assign it to at once. |
| location | object |  | Where it is: a pin and / or an address. lat and lng come together. |
|   lat | number |  |  |
|   lng | number |  |  |
|   name | string |  |  |
|   address | string |  |  |
| files | array of object |  | Files for photo and document fields: up to 20 in one request, 10 MB each. Add more with POST /submit/submissions/{id}/files. |


### `GET /submit/submissions/{id}`

One submission with files, activity and what can be done. Scope: `submissions:manage`. Docs: https://www.app2email.com/docs/api/submit-info/get-submission

Scope: `submissions:manage`. By id or by reference. Everything about it: the answers and `extra`, `files` (each `url` fetches the bytes without a key for 7 days), `events` (the activity list: who did what, every note, reply and automation step), `fields` (how to label each answer), `stages` (where it can move, with `require_note`), `actions` (the manual automations to run with POST /submit/submissions/{id}/run) and `buttons` (sent to the submitter, not pressed yet). A deleted submission answers 404.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The submission's id, or its reference (MR-7Q3M2A). |


Example answer:

```json
{
  "success": true,
  "request_id": "s3get",
  "submission": {
    "id": 4182,
    "reference": "MR-7Q3M2A",
    "form": {
      "key": "meter_reading",
      "name": "Meter reading"
    },
    "channel": "whatsapp",
    "status": "received",
    "status_name": "Received",
    "status_kind": "open",
    "status_color": "blue",
    "priority": "normal",
    "tags": [
      "north"
    ],
    "due": null,
    "assignee": {
      "id": 12,
      "name": "Sam"
    },
    "contact": {
      "identity": "61412345678",
      "name": "John Smith",
      "phone": "61412345678",
      "email": "",
      "verified": true
    },
    "conversation_id": 8762,
    "answers": {
      "meter_no": "A-1182",
      "reading": 48213,
      "photo": [
        9917
      ],
      "moving": false
    },
    "extra": {
      "usage": 312
    },
    "location": null,
    "parent": null,
    "summary": "A-1182 · 48213",
    "files_count": 1,
    "files_pending": 0,
    "unread": true,
    "link": "https://www.app2email.com/s/4mXk9QpL2vTz8RwY3nBc6HdJ5sFg7Ka1",
    "created": "2026-11-13T04:00:00.000Z",
    "updated": "2026-11-13T04:00:00.000Z",
    "status_changed": "2026-11-13T04:00:00.000Z",
    "closed": null,
    "files": [
      {
        "id": 9917,
        "field": "photo",
        "name": "IMG_5237.jpg",
        "mime": "image/jpeg",
        "size": 281733,
        "state": "stored",
        "source": "flow",
        "url": "https://api.app2email.com/submit/file/c2FtcGxlLWZpbGUtbGluay1ub3QtcmVhbA",
        "created": "2026-11-13T04:00:00.000Z"
      }
    ],
    "events": [
      {
        "id": 60411,
        "kind": "created",
        "actor": {
          "kind": "contact",
          "id": 0,
          "name": "John Smith"
        },
        "text": "",
        "data": {},
        "public": true,
        "created": "2026-11-13T04:00:00.000Z"
      }
    ],
    "fields": [
      {
        "key": "meter_no",
        "label": "Meter number",
        "type": "text",
        "step": "reading",
        "internal": false
      },
      {
        "key": "reading",
        "label": "Meter reading",
        "type": "number",
        "step": "reading",
        "internal": false,
        "unit": "kWh"
      },
      {
        "key": "photo",
        "label": "Photo of the meter",
        "type": "photo",
        "step": "reading",
        "internal": false
      },
      {
        "key": "moving",
        "label": "Are you moving out?",
        "type": "yesno",
        "step": "reading",
        "internal": false
      },
      {
        "key": "billing_ref",
        "label": "Billing reference",
        "type": "text",
        "step": "reading",
        "internal": true
      },
      {
        "key": "move_date",
        "label": "Moving date",
        "type": "date",
        "step": "move",
        "internal": false
      },
      {
        "key": "new_address",
        "label": "New address for the final bill",
        "type": "textarea",
        "step": "move",
        "internal": false
      },
      {
        "key": "usage",
        "label": "Usage",
        "type": "number",
        "step": "",
        "internal": true,
        "unit": "kWh",
        "calculated": true
      }
    ],
    "stages": [
      {
        "key": "received",
        "name": "Received",
        "kind": "open",
        "color": "blue",
        "set_by": [],
        "require_note": false
      },
      {
        "key": "queried",
        "name": "Queried",
        "kind": "open",
        "color": "amber",
        "set_by": [],
        "require_note": true
      },
      {
        "key": "checked",
        "name": "Checked",
        "kind": "done",
        "color": "green",
        "set_by": [
          "manager"
        ],
        "require_note": false
      }
    ],
    "actions": [
      {
        "id": 31,
        "label": "Send to billing"
      }
    ],
    "buttons": []
  }
}
```


### `PATCH /submit/submissions/{id}`

Change a submission: stage, assignee, tags, answers. Scope: `submissions:manage`. Docs: https://www.app2email.com/docs/api/submit-info/update-submission

Scope: `submissions:manage`. Not with a sandbox key. Any of: `status` (a stage key; with `note` when the stage has `require_note`, else 409 `stage_not_allowed`), `priority`, `assignee` (a member id; 0 or null = nobody), `due` (null takes it off), `tags` / `tags_add` / `tags_remove`, `answers` and `extra` (only the keys given change, null removes one; calculated values are worked out again) and `location`. A `note` without `status` is written as an internal note. 400 `nothing_to_change` when the body names none of them; `changed` false when the submission already had these values. Each change is written to the activity list under the key's name. Moving to a stage sends that stage's `message` to the submitter, when it has one. Events: `submission.status_changed`, `submission.assigned`, `submission.updated`, `submission.note_added`, one per kind of change; the form's automations run on them.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The submission's id, or its reference (MR-7Q3M2A). |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| status | string |  | A stage key of the submission's form. |
| note | string |  | With status: the note of the change (needed when the stage has require_note; a stage's message can show it to the submitter as {note}). Alone: written as an internal note. |
| priority | string (low \| normal \| high \| urgent) |  |  |
| assignee | integer |  | A member's id (GET /submit/members). 0 or null = nobody. |
| due | string |  | ISO 8601. null or an empty text takes the due time off. |
| tags | array of string |  | ALL the tags: they replace what is there. Up to 20, 40 characters each. |
| tags_add | array of string |  | Tags to add. |
| tags_remove | array of string |  | Tags to remove. |
| answers | object |  | Answers to change: only the keys given are changed; null removes a value. Checked like a customer's answers. |
| extra | object |  | Internal fields and other values to change: only the keys given are changed; null removes a value. |
| location | object |  | Where it is: a pin and / or an address. lat and lng come together. |
|   lat | number |  |  |
|   lng | number |  |  |
|   name | string |  |  |
|   address | string |  |  |


Example answer:

```json
{
  "success": true,
  "request_id": "s4upd",
  "changed": true,
  "submission": {
    "id": 4182,
    "reference": "MR-7Q3M2A",
    "form": {
      "key": "meter_reading",
      "name": "Meter reading"
    },
    "channel": "whatsapp",
    "status": "checked",
    "status_name": "Checked",
    "status_kind": "done",
    "status_color": "green",
    "priority": "normal",
    "tags": [
      "north"
    ],
    "due": null,
    "assignee": {
      "id": 12,
      "name": "Sam"
    },
    "contact": {
      "identity": "61412345678",
      "name": "John Smith",
      "phone": "61412345678",
      "email": "",
      "verified": true
    },
    "conversation_id": 8762,
    "answers": {
      "meter_no": "A-1182",
      "reading": 48213,
      "photo": [
        9917
      ],
      "moving": false
    },
    "extra": {
      "usage": 312
    },
    "location": null,
    "parent": null,
    "summary": "A-1182 · 48213",
    "files_count": 1,
    "files_pending": 0,
    "unread": false,
    "link": "https://www.app2email.com/s/4mXk9QpL2vTz8RwY3nBc6HdJ5sFg7Ka1",
    "created": "2026-11-13T04:00:00.000Z",
    "updated": "2026-11-13T04:20:00.000Z",
    "status_changed": "2026-11-13T04:20:00.000Z",
    "closed": "2026-11-13T04:20:00.000Z",
    "files": [
      {
        "id": 9917,
        "field": "photo",
        "name": "IMG_5237.jpg",
        "mime": "image/jpeg",
        "size": 281733,
        "state": "stored",
        "source": "flow",
        "url": "https://api.app2email.com/submit/file/c2FtcGxlLWZpbGUtbGluay1ub3QtcmVhbA",
        "created": "2026-11-13T04:00:00.000Z"
      }
    ],
    "events": [
      {
        "id": 60411,
        "kind": "created",
        "actor": {
          "kind": "contact",
          "id": 0,
          "name": "John Smith"
        },
        "text": "",
        "data": {},
        "public": true,
        "created": "2026-11-13T04:00:00.000Z"
      }
    ],
    "fields": [
      {
        "key": "meter_no",
        "label": "Meter number",
        "type": "text",
        "step": "reading",
        "internal": false
      },
      {
        "key": "reading",
        "label": "Meter reading",
        "type": "number",
        "step": "reading",
        "internal": false,
        "unit": "kWh"
      },
      {
        "key": "photo",
        "label": "Photo of the meter",
        "type": "photo",
        "step": "reading",
        "internal": false
      },
      {
        "key": "moving",
        "label": "Are you moving out?",
        "type": "yesno",
        "step": "reading",
        "internal": false
      },
      {
        "key": "billing_ref",
        "label": "Billing reference",
        "type": "text",
        "step": "reading",
        "internal": true
      },
      {
        "key": "move_date",
        "label": "Moving date",
        "type": "date",
        "step": "move",
        "internal": false
      },
      {
        "key": "new_address",
        "label": "New address for the final bill",
        "type": "textarea",
        "step": "move",
        "internal": false
      },
      {
        "key": "usage",
        "label": "Usage",
        "type": "number",
        "step": "",
        "internal": true,
        "unit": "kWh",
        "calculated": true
      }
    ],
    "stages": [
      {
        "key": "received",
        "name": "Received",
        "kind": "open",
        "color": "blue",
        "set_by": [],
        "require_note": false
      },
      {
        "key": "queried",
        "name": "Queried",
        "kind": "open",
        "color": "amber",
        "set_by": [],
        "require_note": true
      },
      {
        "key": "checked",
        "name": "Checked",
        "kind": "done",
        "color": "green",
        "set_by": [
          "manager"
        ],
        "require_note": false
      }
    ],
    "actions": [
      {
        "id": 31,
        "label": "Send to billing"
      }
    ],
    "buttons": []
  }
}
```


### `DELETE /submit/submissions/{id}`

Delete a submission, or erase it for good. Scope: `submissions:manage`. Docs: https://www.app2email.com/docs/api/submit-info/delete-submission

Scope: `submissions:manage`. Not with a sandbox key. Without `erase` the submission is hidden from every list and can be restored on the dashboard for 30 days; after that it is erased. With `erase=true` its rows, files and activity are removed now, for a privacy request: this cannot be undone, so confirm with the user first (erase also finds a submission that was deleted before). `submission.deleted` is sent, with `erased` saying which.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The submission's id, or its reference (MR-7Q3M2A). |
| erase | query | boolean |  | true: remove the rows and files for good. |


Example answer:

```json
{
  "success": true,
  "request_id": "s8del",
  "deleted": "MR-7Q3M2A",
  "id": 4182,
  "erased": false,
  "note": "The submission is hidden. It is erased for good after 30 days; until then the dashboard can restore it."
}
```


### `POST /submit/submissions/{id}/notes`

Write an internal note on a submission. Scope: `submissions:manage`. Docs: https://www.app2email.com/docs/api/submit-info/add-submission-note

Scope: `submissions:manage`. Not with a sandbox key. A note for the team, up to 4,000 characters. The submitter never sees it. It appears in the activity list under the key's name, `submission.note_added` is sent, and automations with the trigger `note_added` run.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The submission's id, or its reference (MR-7Q3M2A). |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| text | string | yes |  |


### `POST /submit/submissions/{id}/reply`

Message the submitter, with up to 3 buttons. Scope: `submissions:manage`. Docs: https://www.app2email.com/docs/api/submit-info/reply-to-submission

Scope: `submissions:manage`. Not with a sandbox key. Sends `text` to the person who made the submission: on WhatsApp, or by e-mail when they gave only an e-mail address (`by` says which). When WhatsApp cannot take a normal message for them right now the reply is held (`held` true): they get a short notice, and the reply the moment they tap it or write to the number, exactly as a reply from the Inbox. `buttons` (up to 3) let them answer with one tap: each can move the submission to a stage (`set_status`), which is how a quote is accepted or a fix confirmed; a press arrives as `submission.customer_replied`. `file` sends a document or picture with it, `link` adds a button to their status page. A web submission whose number was never confirmed is answered by e-mail only. The reply is in the activity list and on the submitter's status page. 403 `submit_not_enabled` while Submit-Info is switched off; 502 `whatsapp_error` when it could not be sent at all.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The submission's id, or its reference (MR-7Q3M2A). |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| text | string |  | The message. Needed unless a file is sent. |
| buttons | array of object |  | Up to 3 buttons. Pressing one moves the submission to set_status (when given), sends submission.customer_replied and fires automations with the button trigger. |
| file | object |  | A file sent with the reply. It is stored with the submission too. |
|   name | string | yes |  |
|   mime | string |  |  |
|   data | string | yes | The bytes, base64. 10 MB at most. |
| link | boolean |  | true: add a button that opens the submitter's own page with the status and the history. |


Example answer:

```json
{
  "success": true,
  "request_id": "s6rpl",
  "sent": true,
  "held": false,
  "by": "whatsapp",
  "event": {
    "id": 60421,
    "kind": "reply_out",
    "actor": {
      "kind": "api",
      "id": 3,
      "name": "API key Billing sync"
    },
    "text": "Is this still the right meter? The number on the photo is A-1128.",
    "data": {
      "state": "sent"
    },
    "public": true,
    "created": "2026-11-13T04:20:00.000Z"
  }
}
```


### `POST /submit/submissions/{id}/files`

Attach a file to a submission. Scope: `submissions:manage`. Docs: https://www.app2email.com/docs/api/submit-info/add-submission-file

Scope: `submissions:manage`. Not with a sandbox key. One file as base64, 10 MB at most (413 `media_too_large` above that): a report, a signed form, a photo taken later. With `field` it joins that photo or document field's files; without it, it is a loose file of the submission. The file type is worked out from the bytes, not from `mime`. A submission holds at most 60 files. `submission.updated` is sent with `change.files.added`, and automations with the trigger `file_added` run.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The submission's id, or its reference (MR-7Q3M2A). |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| field | string |  | A photo or document field's key. Left out: a loose file of the submission. |
| name | string | yes |  |
| mime | string |  |  |
| data | string | yes | The bytes, base64. 10 MB at most. |


### `POST /submit/submissions/{id}/run`

Run a manual automation on a submission. Scope: `submissions:manage`. Docs: https://www.app2email.com/docs/api/submit-info/run-submission-action

Scope: `submissions:manage`. Not with a sandbox key. Runs one automation whose trigger is `manual` on this submission now: the same thing as its button in the inbox. `automation_id` is one of the submission's `actions[].id` (GET /submit/submissions/{id}); the automation must be switched on and belong to the submission's form (400 `invalid_automation` otherwise). The automation's conditions are still checked. The answer is the run with every step: what was sent to an outside system and what came back. A step that fails is inside the run (`steps[].ok` false, `status` failed), not an error of this call; when the server is busy the run is queued (`status` waiting) and shows in GET /submit/runs. Whatever the actions do is real: replies are sent, stages change, systems are called.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The submission's id, or its reference (MR-7Q3M2A). |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| automation_id | integer | yes | A manual automation of the submission's form: one of the submission's actions[].id. |


Example answer:

```json
{
  "success": true,
  "request_id": "s9run",
  "run": {
    "id": 9031,
    "automation_id": 31,
    "automation": "Price a quote request in the ERP",
    "submission": "QR-4HT9XC",
    "trigger": "manual",
    "status": "ok",
    "attempt": 1,
    "steps": [
      {
        "n": 1,
        "type": "http",
        "ok": true,
        "ms": 412,
        "summary": "POST https://erp.example.com/api/quotes -> 201",
        "error": "",
        "request": {
          "method": "POST",
          "url": "https://erp.example.com/api/quotes",
          "body": "{\"reference\":\"QR-4HT9XC\",\"product\":\"pump-s\",\"quantity\":3}"
        },
        "response": {
          "status": 201,
          "body": "{\"id\":\"Q-20931\",\"total\":720}"
        }
      },
      {
        "n": 2,
        "type": "set_status",
        "ok": true,
        "ms": 9,
        "summary": "Moved to Quoted",
        "error": ""
      },
      {
        "n": 3,
        "type": "reply",
        "ok": true,
        "ms": 388,
        "summary": "Sent on WhatsApp with 2 buttons",
        "error": ""
      }
    ],
    "error": "",
    "test": false,
    "created": "2026-11-13T04:00:00.000Z",
    "finished": "2026-11-13T04:00:00.000Z",
    "due": null
  }
}
```


### `GET /submit/members`

The team: who works in the shared inbox. Scope: `submissions:manage`. Docs: https://www.app2email.com/docs/api/submit-info/list-submit-members

Scope: `submissions:manage`. The owner, the dashboard's members and the people invited to just the inbox, each with their role, what they may do now (`abilities`), which forms they see and how many open submissions they hold. A member's `id` is what `assignee` takes in PATCH /submit/submissions/{id} and what `member:<id>` means in an assign action.


Example answer:

```json
{
  "success": true,
  "request_id": "m1lst",
  "members": [
    {
      "id": 12,
      "email": "sam@example.com",
      "name": "Sam",
      "role": "agent",
      "status": "active",
      "abilities": {
        "note": true,
        "reply": true,
        "edit": true,
        "stage": true,
        "assign": false,
        "files": true,
        "export": true,
        "delete": false,
        "run": true,
        "forms": false,
        "automations": false,
        "team": false
      },
      "overrides": {
        "export": true
      },
      "forms": [],
      "own_only": false,
      "see_unassigned": true,
      "hide_contacts": false,
      "notify": {
        "assigned": true,
        "created": false
      },
      "invite_expired": false,
      "invited": "2026-11-12T22:00:00.000Z",
      "accepted": "2026-11-12T22:14:00.000Z",
      "last_seen": "2026-11-13T04:00:00.000Z",
      "open_count": 7
    }
  ],
  "count": 1
}
```


### `POST /submit/members`

Invite a person to the shared inbox by e-mail. Scope: `submissions:manage`. Docs: https://www.app2email.com/docs/api/submit-info/invite-submit-member

Scope: `submissions:manage`. Not with a sandbox key. Sends an invitation e-mail with a link that works for 14 days. The person signs in (or makes a login) with that address and from then on sees the inbox, never the dashboard. `role` is a starting set of abilities (admin, manager, agent, viewer); `abilities` switches single ones on or off; `forms`, `own_only`, `see_unassigned` and `hide_contacts` narrow what they see. `email_sent` false means the e-mail could not go out: pass `invite_link` on yourself. An address that is a member already, or a full team (200 members), answers 400 `invalid_member`. Sends a real e-mail to a person: confirm the address with the user first.


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| name | string |  |  |
| role | string (admin \| manager \| agent \| viewer) | yes | A named starting set of abilities. `admin`: Every ability. `manager`: note, reply, edit, stage, assign, files, export, delete, run. `agent`: note, reply, edit, stage, files, run. `viewer`: Sees submissions, changes nothing. |
| abilities | object |  | Changes to the role's set: {ability: true or false}. In an update it replaces the member's earlier changes. `note`: Write internal notes. `reply`: Reply to the submitter. `edit`: Edit answers and internal fields. `stage`: Change the stage. `assign`: Assign to anyone (an agent may always take a submission themselves). `files`: Add and remove files. `export`: Export. `delete`: Delete and restore. `run`: Run manual automations. `forms`: Manage forms and lists. `automations`: Manage automations and connections. `team`: Manage the team. |
| forms | array of string |  | Only these forms (keys). [] = every form. |
| own_only | boolean |  | Sees only what is assigned to them. |
| see_unassigned | boolean |  | With own_only: also sees unassigned submissions, to pick them up. |
| hide_contacts | boolean |  | Numbers, e-mail addresses and answers of type phone or email are masked for this member. |
| notify | object |  |  |
|   assigned | boolean |  | E-mail them when a submission is assigned to them. |
|   created | boolean |  | E-mail them for every new submission they may see. |
| email | string | yes | They sign in with this address. It cannot be changed later: remove the member and invite the new address. |


### `PUT /submit/members/{id}`

Change a member's role, abilities or forms. Scope: `submissions:manage`. Docs: https://www.app2email.com/docs/api/submit-info/update-submit-member

Scope: `submissions:manage`. Not with a sandbox key. Any of `name`, `role`, `abilities`, `forms`, `own_only`, `see_unassigned`, `hide_contacts`, `notify`; what is left out stays (400 `invalid_member` when the body names none). `abilities` replaces the member's own changes to the role's set: `{"delete": false}` takes one ability away from a manager. The owner's own row cannot be changed (400 `invalid_member`).


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The member's id (GET /submit/members). |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| name | string |  |  |
| role | string (admin \| manager \| agent \| viewer) |  | A named starting set of abilities. `admin`: Every ability. `manager`: note, reply, edit, stage, assign, files, export, delete, run. `agent`: note, reply, edit, stage, files, run. `viewer`: Sees submissions, changes nothing. |
| abilities | object |  | Changes to the role's set: {ability: true or false}. In an update it replaces the member's earlier changes. `note`: Write internal notes. `reply`: Reply to the submitter. `edit`: Edit answers and internal fields. `stage`: Change the stage. `assign`: Assign to anyone (an agent may always take a submission themselves). `files`: Add and remove files. `export`: Export. `delete`: Delete and restore. `run`: Run manual automations. `forms`: Manage forms and lists. `automations`: Manage automations and connections. `team`: Manage the team. |
| forms | array of string |  | Only these forms (keys). [] = every form. |
| own_only | boolean |  | Sees only what is assigned to them. |
| see_unassigned | boolean |  | With own_only: also sees unassigned submissions, to pick them up. |
| hide_contacts | boolean |  | Numbers, e-mail addresses and answers of type phone or email are masked for this member. |
| notify | object |  |  |
|   assigned | boolean |  | E-mail them when a submission is assigned to them. |
|   created | boolean |  | E-mail them for every new submission they may see. |


Example answer:

```json
{
  "success": true,
  "request_id": "m3upd",
  "member": {
    "id": 12,
    "email": "sam@example.com",
    "name": "Sam",
    "role": "manager",
    "status": "active",
    "abilities": {
      "note": true,
      "reply": true,
      "edit": true,
      "stage": true,
      "assign": false,
      "files": true,
      "export": true,
      "delete": false,
      "run": true,
      "forms": false,
      "automations": false,
      "team": false
    },
    "overrides": {
      "delete": false
    },
    "forms": [],
    "own_only": false,
    "see_unassigned": true,
    "hide_contacts": false,
    "notify": {
      "assigned": true,
      "created": false
    },
    "invite_expired": false,
    "invited": "2026-11-12T22:00:00.000Z",
    "accepted": "2026-11-12T22:14:00.000Z",
    "last_seen": "2026-11-13T04:00:00.000Z",
    "open_count": 7
  }
}
```


### `DELETE /submit/members/{id}`

Remove a member from the inbox. Scope: `submissions:manage`. Docs: https://www.app2email.com/docs/api/submit-info/remove-submit-member

Scope: `submissions:manage`. Not with a sandbox key. The person loses access at once. What they did stays in the activity lists under their name, and what they hold stays assigned to their name until it is reassigned (PATCH /submit/submissions/{id} `assignee`). The owner cannot be removed (400 `invalid_member`).


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The member's id (GET /submit/members). |


Example answer:

```json
{
  "success": true,
  "request_id": "m4rem",
  "deleted": 12,
  "note": "The member has no access any more. What they hold stays assigned to their name until it is reassigned."
}
```


### `GET /submit/automations`

The automations. Scope: `submissions:manage`. Docs: https://www.app2email.com/docs/api/submit-info/list-automations

Scope: `submissions:manage`. Every automation with its whole document, a one-sentence summary (`sentence`), how often it ran and failed, and its last error. `form` empty means it runs for every form.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| form | query | string |  | Only the automations of this form (its key). |


Example answer:

```json
{
  "success": true,
  "request_id": "a1lst",
  "automations": [
    {
      "name": "Price a quote request in the ERP",
      "form": "quote",
      "enabled": true,
      "trigger": "submitted",
      "options": {},
      "conditions": {
        "all": [
          {
            "field": "quantity",
            "gt": 0
          }
        ]
      },
      "actions": [
        {
          "type": "http",
          "connection": "erp",
          "method": "POST",
          "path": "/quotes",
          "query": {},
          "headers": {
            "X-Source": "whatsapp"
          },
          "body": {
            "reference": "{reference}",
            "customer": {
              "name": "{contact.name}",
              "phone": "{contact.phone}"
            },
            "product": "{product}",
            "quantity": "{quantity}",
            "photos": "{files.photos}"
          },
          "save": {
            "erp_id": "$.id",
            "quote_amount": "$.total"
          },
          "on_fail": "retry"
        },
        {
          "type": "set_status",
          "status": "quoted",
          "note": "Priced by the ERP"
        },
        {
          "type": "reply",
          "text": "Your quote {reference}: {quote_amount} USD for {quantity} x {product}. Shall we go ahead?",
          "buttons": [
            {
              "id": "accept",
              "title": "Accept",
              "set_status": "accepted"
            },
            {
              "id": "decline",
              "title": "Decline",
              "set_status": "declined"
            }
          ],
          "file": "",
          "link": true
        }
      ],
      "id": 31,
      "position": 0,
      "sentence": "When a Quote request is submitted, if quantity > 0: call ERP (POST /quotes), move to Quoted, reply with Accept / Decline",
      "runs": 18,
      "failures": 1,
      "last_run": "2026-11-13T04:00:00.000Z",
      "last_error": "",
      "created": "2026-11-12T22:30:00.000Z",
      "updated": "2026-11-12T22:30:00.000Z"
    }
  ]
}
```


### `POST /submit/automations`

Create an automation: when, if, do. Scope: `submissions:manage`. Docs: https://www.app2email.com/docs/api/submit-info/create-automation

Scope: `submissions:manage`. Not with a sandbox key. `trigger` says when it runs (submitted, a stage change, a button the customer pressed, overdue, manual ...), `conditions` is a rule that must hold (or null), `actions` run in order: reply, e-mail, move the stage, assign, calculate, call an outside system through a connection and save parts of its answer, wait, and more. The SubmitAutomationInput schema lists every trigger, action, placeholder and formula function. The document is checked as a whole: 400 `invalid_automation` with each problem's path and a fix. Before switching one on, try it on a real submission with POST /submit/automations/try. A number has at most 200 automations.


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| name | string | yes | What it is called in the list, up to 80 characters. POST /submit/setup replaces an automation with the same name on the same form. |
| form | string |  | The key of the form it belongs to, or "" for every form. |
| enabled | boolean |  |  |
| position | integer |  | Its place in the list, lowest first. |
| trigger | string (submitted \| status_changed \| assigned \| updated \| note_added \| file_added \| customer_replied \| button \| overdue \| due \| manual) | yes | When it runs. `submitted`: A submission is complete: its files are stored (or 3 minutes passed without them, which is noted on the submission). `status_changed`: The stage changed. Options - to: Stage keys it moved to. [] = any. from: Stage keys it moved from. [] = any. `assigned`: The assignee changed. `updated`: Answers or internal fields were edited. Options - fields: Only when one of these field keys changed. [] = any. `note_added`: A member or the API wrote a note. `file_added`: A file was added after the submission was made. `customer_replied`: The submitter added text or files: after tapping Add more, with a follow-up form, or on their status page. `button`: The submitter pressed a button of a reply. Options - button: The button's id (a-z, 0-9 and _, up to 20 characters). "" = any button. `overdue`: The submission is still in the same stage after this long. Fires once per stay in a stage. Options - minutes: Needed: 5 to 43200 (30 days). stages: Only in these stage keys. [] = every open stage. `due`: The due time passed while the submission is open. Fires once per due time. `manual`: A member presses its button on the submission, or POST /submit/submissions/{id}/run names it. Options - label: The button's text, up to 30 characters. Left out: the automation's name. |
| options | object |  | The trigger's options (see trigger). {} when it has none. |
| conditions | object |  | A rule is {"field": "<key>", <operator>: <value>} with the operators equals, not_equals, in, not_in, contains, empty, not_empty, gt, gte, lt, lte. Every operator written in one rule must hold. When the field's value is an array (multiselect, tags) a rule holds when any item matches, except not_equals and not_in, which need every item. Rules combine as {"all": [rule, ...]} (every one) or {"any": [rule, ...]} (at least one); groups nest 2 deep with up to 10 rules each. null = no condition. Examples: {"field": "deliver", "equals": true}; {"all": [{"field": "amount", "gt": 5000}, {"field": "category", "in": ["plant", "vehicle"]}]}. In a form (show_if) the field must belong to an EARLIER step. `equals`: The value is this. `not_equals`: The value is not this. `in`: The value is one of these (an array). `not_in`: The value is none of these (an array). `contains`: The text contains this (case does not matter), or the array has this item. `empty`: true: there is no value. `not_empty`: true: there is a value. `gt`: Greater than (numbers, dates). `gte`: Greater than or equal. `lt`: Less than. `lte`: Less than or equal. |
|   field | string |  | A field key (or an extra key). Automations may also name status, status_kind, channel, form, priority, tags, assignee, verified, files_count, contact.name, contact.phone. |
|   equals |  |  |  |
|   not_equals |  |  |  |
|   in | array of object |  |  |
|   not_in | array of object |  |  |
|   contains |  |  |  |
|   empty | boolean |  |  |
|   not_empty | boolean |  |  |
|   gt |  |  |  |
|   gte |  |  |  |
|   lt |  |  |  |
|   lte |  |  |  |
|   all | array of object |  | A group: every rule in it must hold. |
|   any | array of object |  | A group: at least one rule in it must hold. |
| actions | array of object | yes | 1 to 20 actions, run in order. |


### `POST /submit/automations/try`

Try an automation on a real submission, saving and sending nothing. Scope: `submissions:manage`. Docs: https://www.app2email.com/docs/api/submit-info/try-automation

Scope: `submissions:manage`. A sandbox key may use it. A rehearsal. Send the automation document (it need not be saved; the id of a saved one works too) and a real submission's id or reference of the same form: the conditions are evaluated and every action is prepared with that submission's values, so the answer shows each step with the filled-in texts and requests. Nothing is written to the submission and nothing is sent to the customer. With `call` true the http, openapi and mcp actions really call the outside system, so you can see its answer and check your `save` paths; without it their requests are only shown. A call that fails is a failed step inside the run, never an error of this route. The run of a try is not stored: its `id` is 0.


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| automation | object | yes | An automation: when (`trigger` with its `options`) - if (`conditions`, a rule or null) - do (`actions`, in order). Only the keys listed here are accepted: an unknown key in the document, in `options` or in an action is a problem (`unknown_key`), so a misspelt key is never ignored. Every run is logged step by step, with what was sent and what came back (GET /submit/runs). A change an automation makes can set off other automations, at most 3 levels deep; one submission gets at most 30 runs an hour. Outside calls refuse private and loopback addresses, do not follow redirects, wait at most 15 seconds and read at most 256 KB; a number makes at most 60 a minute and 2,000 a day. Every text of an action, a stage message and the form's reply takes placeholders in curly brackets; a name that is not known stays as typed. {<field key>}: The answer to that field, an internal field, a calculated value or a value an automation saved (any key of answers or extra). {reference}: The submission's reference, for example MR-7Q3M2A. {form}: The form's name. {form_key}: The form's key. {status}: The stage key. {status_name}: The stage's name. {channel}: whatsapp, web, api or staff. {priority}: low, normal, high or urgent. {tags}: The tags, comma separated. {created}: When it was submitted, in the business's local time (yyyy-MM-dd HH:mm). {updated}: When it last changed (local time). {due}: The due time (local time), empty when there is none. {contact.name}: The submitter's name. {contact.phone}: Their number. {contact.email}: Their e-mail address. {assignee.name}: The assigned member's name. {assignee.email}: Their e-mail address. {link}: The submitter's own status page. {desk_link}: The submission in the staff inbox. {answers}: Every answer as Label: value lines. {files}: A link to every file, one per line. Another system can fetch a link for 7 days. {files.<field key>}: The links of that field's files, as one text with a link per line. {note}: The note of the stage change, or the note that set the automation off. {button}: The id of the button the submitter pressed. {business}: The business name. {submission}: In a JSON body or in arguments only: the whole submission object (its times are ISO 8601). {id}, {status_kind}, {verified}, {files_count}, {contact.identity}, {assignee.id}, {prefill.<key>}, {location.address}: More values of the submission that can be read the same way. {= formula }: The result of a formula, for example {= round(quantity * 1.1, 2) }. Formulas (calculated fields, the calculate action, and {= ... } inside any text): numbers, 'texts' in single quotes, field keys, + - * / %, the comparisons == != > >= < <=, and / or / not, brackets, and the functions if(condition, then, else): then when the condition holds, otherwise else (null without an else). min(a, b, ...): The smallest number. max(a, b, ...): The largest number. round(x, decimals): x rounded, half away from zero; decimals 0 to 10, default 0. abs(x): x without its sign. num(x): x as a number, null when it is not one. len(x): The length of a text, or the number of items of a list. coalesce(a, b, ...): The first value that is not empty. lower(x): x in lower case. upper(x): x in upper case. concat(a, b, ...): The values joined as one text. lookup('<list>', id, '<column>'): A column of the item with that id in a list of the number, for example a price. previous('<field>'): The same contact's last value of that field in this form. count_files('<field>'): How many files a photo or document field holds. days_since(date): Whole days from a date (YYYY-MM-DD) to today; negative for a date to come. No loops and no assignment; at most 500 characters; a division by zero or a missing number gives null. Examples: reading - previous('reading'); quantity * lookup('products', product, 'price'); if(usage < 0, 'check', 'ok'); round(amount * 1.2, 2); days_since(purchase_date) > 30 and count_files('receipt') == 0. A rule is {"field": "<key>", <operator>: <value>} with the operators equals, not_equals, in, not_in, contains, empty, not_empty, gt, gte, lt, lte. Every operator written in one rule must hold. When the field's value is an array (multiselect, tags) a rule holds when any item matches, except not_equals and not_in, which need every item. Rules combine as {"all": [rule, ...]} (every one) or {"any": [rule, ...]} (at least one); groups nest 2 deep with up to 10 rules each. null = no condition. Examples: {"field": "deliver", "equals": true}; {"all": [{"field": "amount", "gt": 5000}, {"field": "category", "in": ["plant", "vehicle"]}]}. |
|   name | string | yes | What it is called in the list, up to 80 characters. POST /submit/setup replaces an automation with the same name on the same form. |
|   form | string |  | The key of the form it belongs to, or "" for every form. |
|   enabled | boolean |  |  |
|   position | integer |  | Its place in the list, lowest first. |
|   trigger | string (submitted \| status_changed \| assigned \| updated \| note_added \| file_added \| customer_replied \| button \| overdue \| due \| manual) | yes | When it runs. `submitted`: A submission is complete: its files are stored (or 3 minutes passed without them, which is noted on the submission). `status_changed`: The stage changed. Options - to: Stage keys it moved to. [] = any. from: Stage keys it moved from. [] = any. `assigned`: The assignee changed. `updated`: Answers or internal fields were edited. Options - fields: Only when one of these field keys changed. [] = any. `note_added`: A member or the API wrote a note. `file_added`: A file was added after the submission was made. `customer_replied`: The submitter added text or files: after tapping Add more, with a follow-up form, or on their status page. `button`: The submitter pressed a button of a reply. Options - button: The button's id (a-z, 0-9 and _, up to 20 characters). "" = any button. `overdue`: The submission is still in the same stage after this long. Fires once per stay in a stage. Options - minutes: Needed: 5 to 43200 (30 days). stages: Only in these stage keys. [] = every open stage. `due`: The due time passed while the submission is open. Fires once per due time. `manual`: A member presses its button on the submission, or POST /submit/submissions/{id}/run names it. Options - label: The button's text, up to 30 characters. Left out: the automation's name. |
|   options | object |  | The trigger's options (see trigger). {} when it has none. |
|   conditions | object |  | A rule is {"field": "<key>", <operator>: <value>} with the operators equals, not_equals, in, not_in, contains, empty, not_empty, gt, gte, lt, lte. Every operator written in one rule must hold. When the field's value is an array (multiselect, tags) a rule holds when any item matches, except not_equals and not_in, which need every item. Rules combine as {"all": [rule, ...]} (every one) or {"any": [rule, ...]} (at least one); groups nest 2 deep with up to 10 rules each. null = no condition. Examples: {"field": "deliver", "equals": true}; {"all": [{"field": "amount", "gt": 5000}, {"field": "category", "in": ["plant", "vehicle"]}]}. In a form (show_if) the field must belong to an EARLIER step. `equals`: The value is this. `not_equals`: The value is not this. `in`: The value is one of these (an array). `not_in`: The value is none of these (an array). `contains`: The text contains this (case does not matter), or the array has this item. `empty`: true: there is no value. `not_empty`: true: there is a value. `gt`: Greater than (numbers, dates). `gte`: Greater than or equal. `lt`: Less than. `lte`: Less than or equal. |
|   actions | array of object | yes | 1 to 20 actions, run in order. |
| submission | string | yes | A real submission to try it on: id or reference. |
| call | boolean |  | true: http, openapi and mcp actions really call the outside system, so its answer and the save paths can be checked. false: their requests are built and shown, not sent. |
| context | object |  | What the trigger would know, when the automation reads it: {from, to, note} of a stage change, {button} of a pressed button, {note} of a note. |


Example answer:

```json
{
  "success": true,
  "request_id": "a6try",
  "run": {
    "id": 0,
    "automation_id": 0,
    "automation": "Price a quote request in the ERP",
    "submission": "QR-4HT9XC",
    "trigger": "submitted",
    "status": "ok",
    "attempt": 1,
    "steps": [
      {
        "n": 1,
        "type": "http",
        "ok": true,
        "ms": 412,
        "summary": "POST https://erp.example.com/api/quotes -> 201",
        "error": "",
        "request": {
          "method": "POST",
          "url": "https://erp.example.com/api/quotes",
          "body": "{\"reference\":\"QR-4HT9XC\",\"product\":\"pump-s\",\"quantity\":3}"
        },
        "response": {
          "status": 201,
          "body": "{\"id\":\"Q-20931\",\"total\":720}"
        }
      },
      {
        "n": 2,
        "type": "set_status",
        "ok": true,
        "ms": 9,
        "summary": "Moved to Quoted",
        "error": ""
      },
      {
        "n": 3,
        "type": "reply",
        "ok": true,
        "ms": 388,
        "summary": "Sent on WhatsApp with 2 buttons",
        "error": ""
      }
    ],
    "error": "",
    "test": true,
    "created": "2026-11-13T04:00:00.000Z",
    "finished": "2026-11-13T04:00:00.000Z",
    "due": null
  }
}
```


### `GET /submit/automations/{id}`

One automation. Scope: `submissions:manage`. Docs: https://www.app2email.com/docs/api/submit-info/get-automation

Scope: `submissions:manage`. The whole document with its id, summary sentence and counters. Read it before changing it: PUT takes the whole document back.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The automation's id (GET /submit/automations). |


Example answer:

```json
{
  "success": true,
  "request_id": "a3get",
  "automation": {
    "name": "Price a quote request in the ERP",
    "form": "quote",
    "enabled": true,
    "trigger": "submitted",
    "options": {},
    "conditions": {
      "all": [
        {
          "field": "quantity",
          "gt": 0
        }
      ]
    },
    "actions": [
      {
        "type": "http",
        "connection": "erp",
        "method": "POST",
        "path": "/quotes",
        "query": {},
        "headers": {
          "X-Source": "whatsapp"
        },
        "body": {
          "reference": "{reference}",
          "customer": {
            "name": "{contact.name}",
            "phone": "{contact.phone}"
          },
          "product": "{product}",
          "quantity": "{quantity}",
          "photos": "{files.photos}"
        },
        "save": {
          "erp_id": "$.id",
          "quote_amount": "$.total"
        },
        "on_fail": "retry"
      },
      {
        "type": "set_status",
        "status": "quoted",
        "note": "Priced by the ERP"
      },
      {
        "type": "reply",
        "text": "Your quote {reference}: {quote_amount} USD for {quantity} x {product}. Shall we go ahead?",
        "buttons": [
          {
            "id": "accept",
            "title": "Accept",
            "set_status": "accepted"
          },
          {
            "id": "decline",
            "title": "Decline",
            "set_status": "declined"
          }
        ],
        "file": "",
        "link": true
      }
    ],
    "id": 31,
    "position": 0,
    "sentence": "When a Quote request is submitted, if quantity > 0: call ERP (POST /quotes), move to Quoted, reply with Accept / Decline",
    "runs": 18,
    "failures": 1,
    "last_run": "2026-11-13T04:00:00.000Z",
    "last_error": "",
    "created": "2026-11-12T22:30:00.000Z",
    "updated": "2026-11-12T22:30:00.000Z"
  }
}
```


### `PUT /submit/automations/{id}`

Change an automation, or switch it on or off. Scope: `submissions:manage`. Docs: https://www.app2email.com/docs/api/submit-info/update-automation

Scope: `submissions:manage`. Not with a sandbox key. Send the whole document (with `trigger` and `actions`) to replace it, or a body with neither of those to change only the keys it has: `{"enabled": false}` switches it off and keeps the rest. The result is checked as a whole (400 `invalid_automation`). Runs that are waiting (a `wait` action, a retry) continue with the new document.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The automation's id (GET /submit/automations). |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| name | string |  | What it is called in the list, up to 80 characters. POST /submit/setup replaces an automation with the same name on the same form. |
| form | string |  | The key of the form it belongs to, or "" for every form. |
| enabled | boolean |  |  |
| position | integer |  | Its place in the list, lowest first. |
| trigger | string (submitted \| status_changed \| assigned \| updated \| note_added \| file_added \| customer_replied \| button \| overdue \| due \| manual) |  | When it runs. `submitted`: A submission is complete: its files are stored (or 3 minutes passed without them, which is noted on the submission). `status_changed`: The stage changed. Options - to: Stage keys it moved to. [] = any. from: Stage keys it moved from. [] = any. `assigned`: The assignee changed. `updated`: Answers or internal fields were edited. Options - fields: Only when one of these field keys changed. [] = any. `note_added`: A member or the API wrote a note. `file_added`: A file was added after the submission was made. `customer_replied`: The submitter added text or files: after tapping Add more, with a follow-up form, or on their status page. `button`: The submitter pressed a button of a reply. Options - button: The button's id (a-z, 0-9 and _, up to 20 characters). "" = any button. `overdue`: The submission is still in the same stage after this long. Fires once per stay in a stage. Options - minutes: Needed: 5 to 43200 (30 days). stages: Only in these stage keys. [] = every open stage. `due`: The due time passed while the submission is open. Fires once per due time. `manual`: A member presses its button on the submission, or POST /submit/submissions/{id}/run names it. Options - label: The button's text, up to 30 characters. Left out: the automation's name. |
| options | object |  | The trigger's options (see trigger). {} when it has none. |
| conditions | object |  | A rule is {"field": "<key>", <operator>: <value>} with the operators equals, not_equals, in, not_in, contains, empty, not_empty, gt, gte, lt, lte. Every operator written in one rule must hold. When the field's value is an array (multiselect, tags) a rule holds when any item matches, except not_equals and not_in, which need every item. Rules combine as {"all": [rule, ...]} (every one) or {"any": [rule, ...]} (at least one); groups nest 2 deep with up to 10 rules each. null = no condition. Examples: {"field": "deliver", "equals": true}; {"all": [{"field": "amount", "gt": 5000}, {"field": "category", "in": ["plant", "vehicle"]}]}. In a form (show_if) the field must belong to an EARLIER step. `equals`: The value is this. `not_equals`: The value is not this. `in`: The value is one of these (an array). `not_in`: The value is none of these (an array). `contains`: The text contains this (case does not matter), or the array has this item. `empty`: true: there is no value. `not_empty`: true: there is a value. `gt`: Greater than (numbers, dates). `gte`: Greater than or equal. `lt`: Less than. `lte`: Less than or equal. |
|   field | string |  | A field key (or an extra key). Automations may also name status, status_kind, channel, form, priority, tags, assignee, verified, files_count, contact.name, contact.phone. |
|   equals |  |  |  |
|   not_equals |  |  |  |
|   in | array of object |  |  |
|   not_in | array of object |  |  |
|   contains |  |  |  |
|   empty | boolean |  |  |
|   not_empty | boolean |  |  |
|   gt |  |  |  |
|   gte |  |  |  |
|   lt |  |  |  |
|   lte |  |  |  |
|   all | array of object |  | A group: every rule in it must hold. |
|   any | array of object |  | A group: at least one rule in it must hold. |
| actions | array of object |  | 1 to 20 actions, run in order. |


Example answer:

```json
{
  "success": true,
  "request_id": "a4upd",
  "automation": {
    "name": "Price a quote request in the ERP",
    "form": "quote",
    "enabled": false,
    "trigger": "submitted",
    "options": {},
    "conditions": {
      "all": [
        {
          "field": "quantity",
          "gt": 0
        }
      ]
    },
    "actions": [
      {
        "type": "http",
        "connection": "erp",
        "method": "POST",
        "path": "/quotes",
        "query": {},
        "headers": {
          "X-Source": "whatsapp"
        },
        "body": {
          "reference": "{reference}",
          "customer": {
            "name": "{contact.name}",
            "phone": "{contact.phone}"
          },
          "product": "{product}",
          "quantity": "{quantity}",
          "photos": "{files.photos}"
        },
        "save": {
          "erp_id": "$.id",
          "quote_amount": "$.total"
        },
        "on_fail": "retry"
      },
      {
        "type": "set_status",
        "status": "quoted",
        "note": "Priced by the ERP"
      },
      {
        "type": "reply",
        "text": "Your quote {reference}: {quote_amount} USD for {quantity} x {product}. Shall we go ahead?",
        "buttons": [
          {
            "id": "accept",
            "title": "Accept",
            "set_status": "accepted"
          },
          {
            "id": "decline",
            "title": "Decline",
            "set_status": "declined"
          }
        ],
        "file": "",
        "link": true
      }
    ],
    "id": 31,
    "position": 0,
    "sentence": "When a Quote request is submitted, if quantity > 0: call ERP (POST /quotes), move to Quoted, reply with Accept / Decline",
    "runs": 18,
    "failures": 1,
    "last_run": "2026-11-13T04:00:00.000Z",
    "last_error": "",
    "created": "2026-11-12T22:30:00.000Z",
    "updated": "2026-11-12T22:30:00.000Z"
  }
}
```


### `DELETE /submit/automations/{id}`

Delete an automation. Scope: `submissions:manage`. Docs: https://www.app2email.com/docs/api/submit-info/delete-automation

Scope: `submissions:manage`. Not with a sandbox key. It stops running, and its waiting runs are dropped. The run log of what it did stays for 30 days.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The automation's id (GET /submit/automations). |


Example answer:

```json
{
  "success": true,
  "request_id": "a5del",
  "deleted": true,
  "id": 31
}
```


### `GET /submit/runs`

The automation run log, step by step. Scope: `submissions:manage`. Docs: https://www.app2email.com/docs/api/submit-info/list-automation-runs

Scope: `submissions:manage`. Latest first, kept 30 days. Each run names its automation, submission and trigger and lists every step: the action, whether it worked, how long it took, and for outside calls the request that was sent and the start of the answer. Use `status=failed` to find what went wrong, `status=waiting` for runs paused by a wait or between retries. Page with `next_cursor`. An `automation` or `submission` filter that names nothing answers 404.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| automation | query | integer |  | Only this automation's runs (its id). |
| submission | query | string |  | Only the runs on this submission (id or reference). |
| status | query | string (running \| ok \| failed \| waiting \| skipped) |  | Only this status. |
| limit | query | integer |  | How many (1 to 200, default 50). |
| cursor | query | string |  | The next_cursor of the previous answer, unchanged. Leave out for the first page. |


Example answer:

```json
{
  "success": true,
  "request_id": "r1lst",
  "runs": [
    {
      "id": 9031,
      "automation_id": 31,
      "automation": "Price a quote request in the ERP",
      "submission": "QR-4HT9XC",
      "trigger": "submitted",
      "status": "ok",
      "attempt": 1,
      "steps": [
        {
          "n": 1,
          "type": "http",
          "ok": true,
          "ms": 412,
          "summary": "POST https://erp.example.com/api/quotes -> 201",
          "error": "",
          "request": {
            "method": "POST",
            "url": "https://erp.example.com/api/quotes",
            "body": "{\"reference\":\"QR-4HT9XC\",\"product\":\"pump-s\",\"quantity\":3}"
          },
          "response": {
            "status": 201,
            "body": "{\"id\":\"Q-20931\",\"total\":720}"
          }
        },
        {
          "n": 2,
          "type": "set_status",
          "ok": true,
          "ms": 9,
          "summary": "Moved to Quoted",
          "error": ""
        },
        {
          "n": 3,
          "type": "reply",
          "ok": true,
          "ms": 388,
          "summary": "Sent on WhatsApp with 2 buttons",
          "error": ""
        }
      ],
      "error": "",
      "test": false,
      "created": "2026-11-13T04:00:00.000Z",
      "finished": "2026-11-13T04:00:00.000Z",
      "due": null
    }
  ],
  "count": 1
}
```


### `GET /submit/connections`

The connections to outside systems. Scope: `submissions:manage`. Docs: https://www.app2email.com/docs/api/submit-info/list-connections

Scope: `submissions:manage`. The systems automations can call: plain HTTP APIs, APIs described by an OpenAPI document, and MCP servers. Each with its kind, address, sign-in type (`has_secret`, never the secret), how many operations or tools are known, the last time it worked, its last error and the automations that use it.


Example answer:

```json
{
  "success": true,
  "request_id": "c1lst",
  "connections": [
    {
      "key": "erp",
      "name": "ERP",
      "kind": "http",
      "base_url": "https://erp.example.com/api",
      "auth": {
        "type": "bearer",
        "name": "",
        "username": "",
        "has_secret": true
      },
      "headers": {
        "X-Tenant": "acme"
      },
      "spec_url": "",
      "enabled": true,
      "functions_count": 0,
      "functions_at": null,
      "last_ok": "2026-11-13T04:00:00.000Z",
      "last_error": "",
      "used_by": [
        "Price a quote request in the ERP"
      ]
    },
    {
      "key": "helpdesk",
      "name": "Helpdesk",
      "kind": "openapi",
      "base_url": "https://helpdesk.example.com/api",
      "auth": {
        "type": "header",
        "name": "X-Auth-Token",
        "username": "",
        "has_secret": true
      },
      "headers": {},
      "spec_url": "https://helpdesk.example.com/openapi.json",
      "enabled": true,
      "functions_count": 2,
      "functions_at": "2026-11-13T04:00:00.000Z",
      "last_ok": "2026-11-13T04:00:00.000Z",
      "last_error": "",
      "used_by": []
    }
  ]
}
```


### `PUT /submit/connections/{key}`

Create or change a connection (HTTP, OpenAPI or MCP). Scope: `submissions:manage`. Docs: https://www.app2email.com/docs/api/submit-info/set-connection

Scope: `submissions:manage`. Not with a sandbox key. Makes the connection when the key is new (`name` and `kind` are needed then), else changes it: a body without `kind` changes only the keys it names. `kind` http: a base address and a sign-in. openapi: also `spec_url` (or `spec`), an OpenAPI 3 document in JSON. mcp: `base_url` is the MCP server's address. `auth.secret` is write-only: it is stored encrypted, never returned, and kept when a later PUT leaves it out (a changed address needs it again). Addresses must be https and public. Saving does not call the outside system: a posted `spec` is read into operations at once, a `spec_url` and an MCP server's tools are read by POST /submit/connections/{key}/refresh. Next: POST /submit/connections/{key}/test, then refresh (openapi, mcp) and GET /submit/connections/{key}/functions to see what an action can call. A number has at most 30 connections.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| key | path | string | yes | The connection's key: lower case letters, digits and _, starting with a letter. |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| name | string |  |  |
| kind | string (http \| openapi \| mcp) |  | `http`: A base address and a sign-in. An http action names the method, path, query, headers and JSON body. `openapi`: An OpenAPI 3.0 or 3.1 document in JSON (spec_url, or spec posted once; up to 2 MB; YAML and Swagger 2 are not read). app2email keeps a short list of its operations; an openapi action picks one and fills its parameters. `mcp`: An MCP server on streamable HTTP (base_url) with a token or no sign-in (OAuth and SSE-only servers are not supported). app2email lists its tools; an mcp action picks one and fills its arguments. |
| base_url | string |  | https only. http: the base every path is added to. openapi: the API's base; left empty, the document's first server is used. mcp: the server's address. |
| headers | object |  | Up to 5 fixed headers sent with every call. Not secret: they are shown again. |
| spec_url | string |  | openapi only: where the OpenAPI document (JSON) is read from. |
| enabled | boolean |  | false: actions that use it fail without calling out. |
| auth | object |  |  |
|   type | string (none \| bearer \| header \| basic \| query) | yes | `none`: No sign-in. `bearer`: Authorization: Bearer <secret>. `header`: The header called name carries the secret. `basic`: Basic sign-in with username and the secret as the password. `query`: The query parameter called name carries the secret. |
|   name | string |  | header: the header's name. query: the parameter's name. |
|   username | string |  | basic only. |
|   secret | string |  | The token, key or password. Write-only: never shown again. Left out: the stored one is kept. |
| spec | object |  | openapi only: the OpenAPI document itself, posted once instead of spec_url. |


Example answer:

```json
{
  "success": true,
  "request_id": "c2set",
  "connection": {
    "key": "erp",
    "name": "ERP",
    "kind": "http",
    "base_url": "https://erp.example.com/api",
    "auth": {
      "type": "bearer",
      "name": "",
      "username": "",
      "has_secret": true
    },
    "headers": {
      "X-Tenant": "acme"
    },
    "spec_url": "",
    "enabled": true,
    "functions_count": 0,
    "functions_at": null,
    "last_ok": null,
    "last_error": "",
    "used_by": []
  }
}
```


### `DELETE /submit/connections/{key}`

Delete a connection. Scope: `submissions:manage`. Docs: https://www.app2email.com/docs/api/submit-info/delete-connection

Scope: `submissions:manage`. Not with a sandbox key. Refused while an automation still uses it: 409 `connection_in_use`, and the message names those automations. The stored secret is deleted with it.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| key | path | string | yes | The connection's key: lower case letters, digits and _, starting with a letter. |


Example answer:

```json
{
  "success": true,
  "request_id": "c3del",
  "deleted": true,
  "key": "erp"
}
```


### `POST /submit/connections/{key}/test`

Test a connection: can app2email reach it and sign in?. Scope: `submissions:manage`. Docs: https://www.app2email.com/docs/api/submit-info/test-connection

Scope: `submissions:manage`. A sandbox key may use it. Makes one real call from app2email's server: http reads the base address, openapi fetches the document, mcp opens a session with the server. The answer says whether it worked (`ok`), how far it got (`stage`), the HTTP status, the error in words and the time taken. A failed test answers 200 with `ok` false: read `stage` and `error` (`stage` is `response` when it worked). Nothing is changed in the outside system.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| key | path | string | yes | The connection's key: lower case letters, digits and _, starting with a letter. |


Example answer:

```json
{
  "success": true,
  "request_id": "c4tst",
  "ok": true,
  "stage": "response",
  "status": 200,
  "error": "",
  "ms": 231
}
```


### `POST /submit/connections/{key}/refresh`

Read a connection's operations or tools again. Scope: `submissions:manage`. Docs: https://www.app2email.com/docs/api/submit-info/refresh-connection

Scope: `submissions:manage`. Not with a sandbox key. For openapi: fetches the document again and rebuilds the list of operations. For mcp: asks the server for its tools again. Call it after the outside system changed. An automation that names an operation or tool that is gone fails at its next run, so check GET /submit/automations afterwards. 502 `connection_failed` when the document or the server cannot be read; the old list is kept then.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| key | path | string | yes | The connection's key: lower case letters, digits and _, starting with a letter. |


Example answer:

```json
{
  "success": true,
  "request_id": "c5ref",
  "connection": {
    "key": "helpdesk",
    "name": "Helpdesk",
    "kind": "openapi",
    "base_url": "https://helpdesk.example.com/api",
    "auth": {
      "type": "header",
      "name": "X-Auth-Token",
      "username": "",
      "has_secret": true
    },
    "headers": {},
    "spec_url": "https://helpdesk.example.com/openapi.json",
    "enabled": true,
    "functions_count": 2,
    "functions_at": "2026-11-13T04:00:00.000Z",
    "last_ok": "2026-11-13T04:00:00.000Z",
    "last_error": "",
    "used_by": []
  },
  "functions": [
    {
      "id": "createTicket",
      "title": "Create a ticket",
      "method": "POST",
      "path": "/tickets",
      "has_body": true,
      "params": [
        {
          "name": "subject",
          "in": "body",
          "type": "string",
          "required": true,
          "description": "The ticket's title."
        },
        {
          "name": "priority",
          "in": "body",
          "type": "string",
          "required": false,
          "description": "low, normal or high."
        }
      ]
    },
    {
      "id": "getTicket",
      "title": "One ticket",
      "method": "GET",
      "path": "/tickets/{id}",
      "has_body": false,
      "params": [
        {
          "name": "id",
          "in": "path",
          "type": "string",
          "required": true,
          "description": ""
        }
      ]
    }
  ]
}
```


### `GET /submit/connections/{key}/functions`

What an action can call on a connection. Scope: `submissions:manage`. Docs: https://www.app2email.com/docs/api/submit-info/list-connection-functions

Scope: `submissions:manage`. The operations of an openapi connection or the tools of an mcp connection, each with its parameters: name, where it goes (path, query, header, body), type and whether it is required. An openapi action takes a function's `id` as `operation` and fills `params` by name; an mcp action takes it as `tool` and fills `arguments`. An http connection has no functions: its actions name method and path themselves.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| key | path | string | yes | The connection's key: lower case letters, digits and _, starting with a letter. |


Example answer:

```json
{
  "success": true,
  "request_id": "c6fun",
  "functions": [
    {
      "id": "createTicket",
      "title": "Create a ticket",
      "method": "POST",
      "path": "/tickets",
      "has_body": true,
      "params": [
        {
          "name": "subject",
          "in": "body",
          "type": "string",
          "required": true,
          "description": "The ticket's title."
        },
        {
          "name": "priority",
          "in": "body",
          "type": "string",
          "required": false,
          "description": "low, normal or high."
        }
      ]
    },
    {
      "id": "getTicket",
      "title": "One ticket",
      "method": "GET",
      "path": "/tickets/{id}",
      "has_body": false,
      "params": [
        {
          "name": "id",
          "in": "path",
          "type": "string",
          "required": true,
          "description": ""
        }
      ]
    }
  ],
  "functions_at": "2026-11-13T04:00:00.000Z"
}
```


### `GET /submit/report`

Submission counts by form, stage, day and assignee. Scope: `submissions:manage`. Docs: https://www.app2email.com/docs/api/submit-info/get-submit-report

Scope: `submissions:manage`. The submissions made in the last `days` days (1 to 365, default 30) counted by form, by stage, by day (in the business time zone) and by assignee, with how many are open now and the average hours from submission to a closed stage. 400 `invalid_range` when `days` is not 1 to 365.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| days | query | integer |  | How many days back, 1 to 365. Default 30. |


Example answer:

```json
{
  "success": true,
  "request_id": "r9rep",
  "days": 30,
  "timezone": "Australia/Sydney",
  "open_now": 14,
  "closed_avg_hours": 6.4,
  "by_form": [
    {
      "form": "meter_reading",
      "name": "Meter reading",
      "count": 148,
      "open": 12
    },
    {
      "form": "quote",
      "name": "Quote request",
      "count": 23,
      "open": 2
    }
  ],
  "by_stage": [
    {
      "form": "meter_reading",
      "status": "received",
      "status_kind": "open",
      "count": 12
    },
    {
      "form": "meter_reading",
      "status": "checked",
      "status_kind": "done",
      "count": 134
    }
  ],
  "by_day": [
    {
      "day": "2026-11-12",
      "count": 9
    },
    {
      "day": "2026-11-13",
      "count": 4
    }
  ],
  "by_assignee": [
    {
      "id": 12,
      "name": "Sam",
      "count": 61,
      "open": 7
    },
    {
      "id": 0,
      "name": "",
      "count": 14,
      "open": 7
    }
  ]
}
```


## Tickets-and-Pay


### `GET /tickets/events`

The events, newest first. Scope: `tickets:manage`. Docs: https://www.app2email.com/docs/api/tickets-and-pay/list-ticket-events

Scope: `tickets:manage`. The events of the number, newest first, each with its next date, how many tickets are sold and the lowest price. `status` filters by state, `archived=true` lists the archived ones instead, `q` searches the name, the slug and the code (EV-XXXXX). The rows have no `dates`, `types` or `problems`: GET /tickets/events/{id} has them. Page with `next_cursor`.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| status | query | string (draft \| published \| ended \| cancelled) |  | Only events in this state. Left out: all four. |
| archived | query | boolean |  | true: the archived events only. Left out: the ones that are not archived. |
| q | query | string |  | Search in the name, the slug or the EV- code (2 to 80 characters). |
| limit | query | integer |  | How many (1 to 200, default 50). |
| cursor | query | string |  | The next_cursor of the previous answer, unchanged. Leave out for the first page. |


Example answer:

```json
{
  "success": true,
  "request_id": "t1ev2",
  "events": [
    {
      "id": 12,
      "slug": "summer-quiz",
      "code": "EV-7H3KQ",
      "name": "Summer Quiz",
      "summary": "A night of questions on the terrace.",
      "description": "",
      "status": "published",
      "sales": "on",
      "visibility": "public",
      "schedule": "single",
      "seating": "none",
      "archived": false,
      "timezone": "Australia/Sydney",
      "currency": "AUD",
      "capacity": 120,
      "held_back": 0,
      "url": "https://www.app2email.com/events/k3XbQ9rTzP2mWv7/summer-quiz",
      "cover_url": "",
      "settings": {
        "doors_min": 30,
        "sales_end": "start",
        "sales_end_min": 60,
        "place": "venue",
        "venue": {
          "name": "The Terrace",
          "address": "12 Harbour Street, Sydney",
          "map": "",
          "lat": 0,
          "lng": 0,
          "pin": false,
          "note": "",
          "hide_address": false
        },
        "online": {
          "url": "",
          "note": ""
        },
        "age": "",
        "age_text": "",
        "access_info": "",
        "max_per_order": 10,
        "max_per_buyer": 0,
        "show_remaining": "low",
        "fee": {
          "ticket_minor": 0,
          "order_minor": 0,
          "show": "included"
        },
        "tax": {
          "rate": 0,
          "label": "VAT",
          "inclusive": true
        },
        "donation": {
          "enabled": false,
          "amounts": []
        },
        "checkout": {
          "email": "optional"
        },
        "names": "buyer",
        "questions": [],
        "terms_text": "",
        "terms_url": "",
        "marketing_optin": false,
        "seat": {
          "pick": "buyer",
          "no_single": true
        },
        "reminders": [
          1440
        ],
        "reminder_note": "",
        "holder_changes": true,
        "refund_policy": "none",
        "refund_days": 7,
        "refund_text": "",
        "waitlist": "off",
        "door": {
          "opens_min": 120,
          "reentry": "no",
          "gates": [
            {
              "id": "g1",
              "name": "Main entrance",
              "type_ids": []
            }
          ]
        },
        "brand": {
          "color": ""
        },
        "ticket_style": null
      },
      "from_price": 12.0,
      "from_price_label": "A$12.00",
      "tickets_sold": 86,
      "dates_count": 1,
      "next_date": {
        "id": 31,
        "event_id": 12,
        "start": "2026-12-12T08:30:00.000Z",
        "end": "2026-12-12T10:30:00.000Z",
        "start_local": "2026-12-12T19:30",
        "end_local": "2026-12-12T21:30",
        "label": "",
        "capacity": 120,
        "sales": "on",
        "status": "scheduled",
        "sold": null,
        "people": null,
        "held": null,
        "left": null,
        "checked_in": null,
        "sold_out": false,
        "changed": null,
        "cancelled": null
      },
      "seat_plan": null,
      "sales_start": null,
      "published": "2026-11-06T01:00:00.000Z",
      "ended": null,
      "cancelled": null,
      "cancel_reason": "",
      "created_by": "API key Zapier",
      "created": "2026-11-06T01:00:00.000Z",
      "updated": "2026-11-06T01:00:00.000Z"
    }
  ],
  "next_cursor": null,
  "count": 1
}
```


### `POST /tickets/events`

Create an event as a draft with one date and one ticket type. Scope: `tickets:manage`. Docs: https://www.app2email.com/docs/api/tickets-and-pay/create-ticket-event

Scope: `tickets:manage`. Not with a sandbox key. Makes a draft with one date and the ticket type General admission at `price` (0 or left out: free). `start` is local time in the number's time zone (2026-12-12T19:30) or ISO 8601 with an offset, and must be in the future. Time zone and currency start as the number's. Nothing is on sale until POST /tickets/events/{id}/publish. 409 `ticket_limit_reached` at 200 events. Send an `Idempotency-Key` header to retry safely: the same key and body within 24 hours gets the first answer again (an error does not use the key up).


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| Idempotency-Key | header | string |  | Optional. A unique value for this message or list (eg a UUID). The same request with the same key within 24 hours gets the first answer again, and nothing is sent twice. Ignored by dry runs. |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| name | string | yes |  |
| start | string | yes | In the future. Local time in the number's time zone (2026-12-12T19:30) or ISO 8601 with an offset. |
| price | number |  | The price of the one ticket type, in the number's currency. 0 or left out: a free event. |


### `GET /tickets/events/{id}`

One event with its dates and ticket types. Scope: `tickets:manage`. Docs: https://www.app2email.com/docs/api/tickets-and-pay/get-ticket-event

Scope: `tickets:manage`. By id, slug or code (EV-XXXXX). With its scheduled dates (soonest first, at most 50; `dates_more` says there are more, and GET /tickets/events/{id}/dates pages through all of them), its ticket types that are not archived and, for a draft, `problems`: what still stops publishing (empty: it can be published).


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The event: its id, its slug (eg summer-quiz) or its code (EV-XXXXX). |


Example answer:

```json
{
  "success": true,
  "request_id": "t3eg4",
  "event": {
    "id": 12,
    "slug": "summer-quiz",
    "code": "EV-7H3KQ",
    "name": "Summer Quiz",
    "summary": "A night of questions on the terrace.",
    "description": "",
    "status": "published",
    "sales": "on",
    "visibility": "public",
    "schedule": "single",
    "seating": "none",
    "archived": false,
    "timezone": "Australia/Sydney",
    "currency": "AUD",
    "capacity": 120,
    "held_back": 0,
    "url": "https://www.app2email.com/events/k3XbQ9rTzP2mWv7/summer-quiz",
    "cover_url": "",
    "settings": {
      "doors_min": 30,
      "sales_end": "start",
      "sales_end_min": 60,
      "place": "venue",
      "venue": {
        "name": "The Terrace",
        "address": "12 Harbour Street, Sydney",
        "map": "",
        "lat": 0,
        "lng": 0,
        "pin": false,
        "note": "",
        "hide_address": false
      },
      "online": {
        "url": "",
        "note": ""
      },
      "age": "",
      "age_text": "",
      "access_info": "",
      "max_per_order": 10,
      "max_per_buyer": 0,
      "show_remaining": "low",
      "fee": {
        "ticket_minor": 0,
        "order_minor": 0,
        "show": "included"
      },
      "tax": {
        "rate": 0,
        "label": "VAT",
        "inclusive": true
      },
      "donation": {
        "enabled": false,
        "amounts": []
      },
      "checkout": {
        "email": "optional"
      },
      "names": "buyer",
      "questions": [],
      "terms_text": "",
      "terms_url": "",
      "marketing_optin": false,
      "seat": {
        "pick": "buyer",
        "no_single": true
      },
      "reminders": [
        1440
      ],
      "reminder_note": "",
      "holder_changes": true,
      "refund_policy": "none",
      "refund_days": 7,
      "refund_text": "",
      "waitlist": "off",
      "door": {
        "opens_min": 120,
        "reentry": "no",
        "gates": [
          {
            "id": "g1",
            "name": "Main entrance",
            "type_ids": []
          }
        ]
      },
      "brand": {
        "color": ""
      },
      "ticket_style": null
    },
    "from_price": 12.0,
    "from_price_label": "A$12.00",
    "tickets_sold": 86,
    "dates_count": 1,
    "next_date": {
      "id": 31,
      "event_id": 12,
      "start": "2026-12-12T08:30:00.000Z",
      "end": "2026-12-12T10:30:00.000Z",
      "start_local": "2026-12-12T19:30",
      "end_local": "2026-12-12T21:30",
      "label": "",
      "capacity": 120,
      "sales": "on",
      "status": "scheduled",
      "sold": 86,
      "people": 86,
      "held": 2,
      "left": 32,
      "checked_in": 0,
      "sold_out": false,
      "changed": null,
      "cancelled": null
    },
    "seat_plan": null,
    "sales_start": null,
    "published": "2026-11-06T01:00:00.000Z",
    "ended": null,
    "cancelled": null,
    "cancel_reason": "",
    "created_by": "API key Zapier",
    "created": "2026-11-06T01:00:00.000Z",
    "updated": "2026-11-06T01:00:00.000Z",
    "dates": [
      {
        "id": 31,
        "event_id": 12,
        "start": "2026-12-12T08:30:00.000Z",
        "end": "2026-12-12T10:30:00.000Z",
        "start_local": "2026-12-12T19:30",
        "end_local": "2026-12-12T21:30",
        "label": "",
        "capacity": 120,
        "sales": "on",
        "status": "scheduled",
        "sold": 86,
        "people": 86,
        "held": 2,
        "left": 32,
        "checked_in": 0,
        "sold_out": false,
        "changed": null,
        "cancelled": null
      }
    ],
    "dates_more": false,
    "types": [
      {
        "id": 44,
        "event_id": 12,
        "name": "Adult",
        "description": "",
        "role": "ticket",
        "status": "active",
        "visibility": "public",
        "sort": 1,
        "price_mode": "fixed",
        "price": 12.0,
        "price_label": "A$12.00",
        "price_all_in": 12.0,
        "price_all_in_label": "A$12.00",
        "min_price": 0,
        "admits": 1,
        "quantity": 0,
        "pool_id": 0,
        "opens_after": 0,
        "needs": 0,
        "needs_each": false,
        "min_per_order": 1,
        "max_per_order": 0,
        "sales_start": null,
        "sales_end": null,
        "sales_end_days": 0,
        "date_ids": [],
        "door_note": "",
        "created": "2026-11-06T01:00:00.000Z",
        "updated": "2026-11-06T01:00:00.000Z"
      }
    ]
  }
}
```


### `PATCH /tickets/events/{id}`

Change an event. Scope: `tickets:manage`. Docs: https://www.app2email.com/docs/api/tickets-and-pay/update-ticket-event

Scope: `tickets:manage`. Not with a sandbox key. Send only the keys to change: `name`, `summary`, `description`, `visibility`, `sales` (on or paused), `capacity`, `held_back`, `timezone`, `currency` (refused once an order exists), `sales_start`, `slug` (until the first publish) and `settings` (merged key by key at the top level, then checked as a whole). `notify` true tells ticket holders when the venue changed. The status, the schedule, the seat plan and the pictures are changed on the dashboard: 400 `invalid_ticket_event` names a key that cannot be changed here. A capacity below what is sold is saved and `note` says so. 400 `nothing_to_change` without any of the keys. `ticket.event.sold_out` is sent when a lower limit makes a date full.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The event: its id, its slug (eg summer-quiz) or its code (EV-XXXXX). |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| name | string |  |  |
| summary | string |  |  |
| description | string |  |  |
| visibility | string (public \| unlisted) |  |  |
| sales | string (on \| paused) |  |  |
| capacity | integer |  | People per date. 0 = no limit. |
| held_back | integer |  | Places per date only staff can sell (0 to capacity). |
| timezone | string |  | An IANA time zone. The clock times of the coming dates stay. |
| currency | string |  | ISO 4217. Refused once the event has an order. |
| sales_start | string |  | Local time in the event's time zone (2026-12-12T19:30) or ISO 8601 with an offset (2026-12-12T19:30:00+11:00). null = from the moment it is published. |
| slug | string |  | 3 to 60 characters of a-z, 0-9 and -. Only until the first publish. |
| settings | object |  | Options to change: doors_min, sales_end, sales_end_min, place, venue {name, address, map, lat, lng, pin, note, hide_address}, online {url, note}, age, age_text, access_info, max_per_order, max_per_buyer, show_remaining, fee {ticket_minor, order_minor, show}, tax {rate, label, inclusive}, donation {enabled, amounts}, checkout {email}, names, questions, terms_text, terms_url, marketing_optin, seat {pick, no_single}, reminders, reminder_note, holder_changes, refund_policy, refund_days, refund_text, waitlist, door {opens_min, reentry, gates [{id, name, type_ids}]}, brand {color}, ticket_style. A key sent replaces the stored key; the others stay. Amounts are in the smallest unit of the currency, as GET shows them. |
| notify | boolean |  | true: tell ticket holders when the venue changed. |


Example answer:

```json
{
  "success": true,
  "request_id": "t4eu5",
  "event": {
    "id": 12,
    "slug": "summer-quiz",
    "code": "EV-7H3KQ",
    "name": "Summer Quiz",
    "summary": "A night of questions on the terrace.",
    "description": "",
    "status": "published",
    "sales": "paused",
    "visibility": "public",
    "schedule": "single",
    "seating": "none",
    "archived": false,
    "timezone": "Australia/Sydney",
    "currency": "AUD",
    "capacity": 120,
    "held_back": 0,
    "url": "https://www.app2email.com/events/k3XbQ9rTzP2mWv7/summer-quiz",
    "cover_url": "",
    "settings": {
      "doors_min": 30,
      "sales_end": "start",
      "sales_end_min": 60,
      "place": "venue",
      "venue": {
        "name": "The Terrace",
        "address": "12 Harbour Street, Sydney",
        "map": "",
        "lat": 0,
        "lng": 0,
        "pin": false,
        "note": "",
        "hide_address": false
      },
      "online": {
        "url": "",
        "note": ""
      },
      "age": "",
      "age_text": "",
      "access_info": "",
      "max_per_order": 10,
      "max_per_buyer": 0,
      "show_remaining": "low",
      "fee": {
        "ticket_minor": 0,
        "order_minor": 0,
        "show": "included"
      },
      "tax": {
        "rate": 0,
        "label": "VAT",
        "inclusive": true
      },
      "donation": {
        "enabled": false,
        "amounts": []
      },
      "checkout": {
        "email": "optional"
      },
      "names": "buyer",
      "questions": [],
      "terms_text": "",
      "terms_url": "",
      "marketing_optin": false,
      "seat": {
        "pick": "buyer",
        "no_single": true
      },
      "reminders": [
        1440
      ],
      "reminder_note": "",
      "holder_changes": true,
      "refund_policy": "none",
      "refund_days": 7,
      "refund_text": "",
      "waitlist": "off",
      "door": {
        "opens_min": 120,
        "reentry": "no",
        "gates": [
          {
            "id": "g1",
            "name": "Main entrance",
            "type_ids": []
          }
        ]
      },
      "brand": {
        "color": ""
      },
      "ticket_style": null
    },
    "from_price": 12.0,
    "from_price_label": "A$12.00",
    "tickets_sold": 86,
    "dates_count": 1,
    "next_date": {
      "id": 31,
      "event_id": 12,
      "start": "2026-12-12T08:30:00.000Z",
      "end": "2026-12-12T10:30:00.000Z",
      "start_local": "2026-12-12T19:30",
      "end_local": "2026-12-12T21:30",
      "label": "",
      "capacity": 120,
      "sales": "on",
      "status": "scheduled",
      "sold": 86,
      "people": 86,
      "held": 2,
      "left": 32,
      "checked_in": 0,
      "sold_out": false,
      "changed": null,
      "cancelled": null
    },
    "seat_plan": null,
    "sales_start": null,
    "published": "2026-11-06T01:00:00.000Z",
    "ended": null,
    "cancelled": null,
    "cancel_reason": "",
    "created_by": "API key Zapier",
    "created": "2026-11-06T01:00:00.000Z",
    "updated": "2026-11-06T01:00:00.000Z",
    "dates": [
      {
        "id": 31,
        "event_id": 12,
        "start": "2026-12-12T08:30:00.000Z",
        "end": "2026-12-12T10:30:00.000Z",
        "start_local": "2026-12-12T19:30",
        "end_local": "2026-12-12T21:30",
        "label": "",
        "capacity": 120,
        "sales": "on",
        "status": "scheduled",
        "sold": 86,
        "people": 86,
        "held": 2,
        "left": 32,
        "checked_in": 0,
        "sold_out": false,
        "changed": null,
        "cancelled": null
      }
    ],
    "dates_more": false,
    "types": [
      {
        "id": 44,
        "event_id": 12,
        "name": "Adult",
        "description": "",
        "role": "ticket",
        "status": "active",
        "visibility": "public",
        "sort": 1,
        "price_mode": "fixed",
        "price": 12.0,
        "price_label": "A$12.00",
        "price_all_in": 12.0,
        "price_all_in_label": "A$12.00",
        "min_price": 0,
        "admits": 1,
        "quantity": 0,
        "pool_id": 0,
        "opens_after": 0,
        "needs": 0,
        "needs_each": false,
        "min_per_order": 1,
        "max_per_order": 0,
        "sales_start": null,
        "sales_end": null,
        "sales_end_days": 0,
        "date_ids": [],
        "door_note": "",
        "created": "2026-11-06T01:00:00.000Z",
        "updated": "2026-11-06T01:00:00.000Z"
      }
    ]
  },
  "note": "Saved."
}
```


### `POST /tickets/events/{id}/publish`

Publish an event so tickets can be bought. Scope: `tickets:manage`. Docs: https://www.app2email.com/docs/api/tickets-and-pay/publish-ticket-event

Scope: `tickets:manage`. Not with a sandbox key. No body. Puts the event on sale on its page (`url`) and in the WhatsApp chat. Needs ticket sales switched on for the number (403 `tickets_not_enabled`) and in its plan (403 `plan_not_allowed`). 409 `ticket_event_not_publishable` lists what is missing in `details.problems`. An event that is already published answers 200 and `note` says so.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The event: its id, its slug (eg summer-quiz) or its code (EV-XXXXX). |


Example answer:

```json
{
  "success": true,
  "request_id": "t5ep6",
  "event": {
    "id": 12,
    "slug": "summer-quiz",
    "code": "EV-7H3KQ",
    "name": "Summer Quiz",
    "summary": "A night of questions on the terrace.",
    "description": "",
    "status": "published",
    "sales": "on",
    "visibility": "public",
    "schedule": "single",
    "seating": "none",
    "archived": false,
    "timezone": "Australia/Sydney",
    "currency": "AUD",
    "capacity": 120,
    "held_back": 0,
    "url": "https://www.app2email.com/events/k3XbQ9rTzP2mWv7/summer-quiz",
    "cover_url": "",
    "settings": {
      "doors_min": 30,
      "sales_end": "start",
      "sales_end_min": 60,
      "place": "venue",
      "venue": {
        "name": "The Terrace",
        "address": "12 Harbour Street, Sydney",
        "map": "",
        "lat": 0,
        "lng": 0,
        "pin": false,
        "note": "",
        "hide_address": false
      },
      "online": {
        "url": "",
        "note": ""
      },
      "age": "",
      "age_text": "",
      "access_info": "",
      "max_per_order": 10,
      "max_per_buyer": 0,
      "show_remaining": "low",
      "fee": {
        "ticket_minor": 0,
        "order_minor": 0,
        "show": "included"
      },
      "tax": {
        "rate": 0,
        "label": "VAT",
        "inclusive": true
      },
      "donation": {
        "enabled": false,
        "amounts": []
      },
      "checkout": {
        "email": "optional"
      },
      "names": "buyer",
      "questions": [],
      "terms_text": "",
      "terms_url": "",
      "marketing_optin": false,
      "seat": {
        "pick": "buyer",
        "no_single": true
      },
      "reminders": [
        1440
      ],
      "reminder_note": "",
      "holder_changes": true,
      "refund_policy": "none",
      "refund_days": 7,
      "refund_text": "",
      "waitlist": "off",
      "door": {
        "opens_min": 120,
        "reentry": "no",
        "gates": [
          {
            "id": "g1",
            "name": "Main entrance",
            "type_ids": []
          }
        ]
      },
      "brand": {
        "color": ""
      },
      "ticket_style": null
    },
    "from_price": 12.0,
    "from_price_label": "A$12.00",
    "tickets_sold": 86,
    "dates_count": 1,
    "next_date": {
      "id": 31,
      "event_id": 12,
      "start": "2026-12-12T08:30:00.000Z",
      "end": "2026-12-12T10:30:00.000Z",
      "start_local": "2026-12-12T19:30",
      "end_local": "2026-12-12T21:30",
      "label": "",
      "capacity": 120,
      "sales": "on",
      "status": "scheduled",
      "sold": 86,
      "people": 86,
      "held": 2,
      "left": 32,
      "checked_in": 0,
      "sold_out": false,
      "changed": null,
      "cancelled": null
    },
    "seat_plan": null,
    "sales_start": null,
    "published": "2026-11-06T01:00:00.000Z",
    "ended": null,
    "cancelled": null,
    "cancel_reason": "",
    "created_by": "API key Zapier",
    "created": "2026-11-06T01:00:00.000Z",
    "updated": "2026-11-06T01:00:00.000Z",
    "dates": [
      {
        "id": 31,
        "event_id": 12,
        "start": "2026-12-12T08:30:00.000Z",
        "end": "2026-12-12T10:30:00.000Z",
        "start_local": "2026-12-12T19:30",
        "end_local": "2026-12-12T21:30",
        "label": "",
        "capacity": 120,
        "sales": "on",
        "status": "scheduled",
        "sold": 86,
        "people": 86,
        "held": 2,
        "left": 32,
        "checked_in": 0,
        "sold_out": false,
        "changed": null,
        "cancelled": null
      }
    ],
    "dates_more": false,
    "types": [
      {
        "id": 44,
        "event_id": 12,
        "name": "Adult",
        "description": "",
        "role": "ticket",
        "status": "active",
        "visibility": "public",
        "sort": 1,
        "price_mode": "fixed",
        "price": 12.0,
        "price_label": "A$12.00",
        "price_all_in": 12.0,
        "price_all_in_label": "A$12.00",
        "min_price": 0,
        "admits": 1,
        "quantity": 0,
        "pool_id": 0,
        "opens_after": 0,
        "needs": 0,
        "needs_each": false,
        "min_per_order": 1,
        "max_per_order": 0,
        "sales_start": null,
        "sales_end": null,
        "sales_end_days": 0,
        "date_ids": [],
        "door_note": "",
        "created": "2026-11-06T01:00:00.000Z",
        "updated": "2026-11-06T01:00:00.000Z"
      }
    ]
  },
  "note": "Published. Tickets can be bought at https://www.app2email.com/events/k3XbQ9rTzP2mWv7/summer-quiz."
}
```


### `POST /tickets/events/{id}/cancel`

Cancel an event and refund or void its tickets. Scope: `tickets:manage`. Docs: https://www.app2email.com/docs/api/tickets-and-pay/cancel-ticket-event

Scope: `tickets:manage`. Not with a sandbox key. Cancels every scheduled date of the event. `refund` says what happens to the tickets: all = everything paid goes back, prices = the ticket prices without booking fees and donations, none = the tickets are voided and no money moves. `confirm` must be the word CANCEL. The answer comes at once (`started` true); the orders are refunded one by one in the background through the business's own payment provider, the ticket holders are told unless `notify` is false, `ticket.order.refunded` is sent for each order and `ticket.event.cancelled` for each date when it has finished. It cannot be undone. 409 `ticket_not_allowed` when the event is already cancelled or has ended. Send an `Idempotency-Key` header to retry safely: the same key and body within 24 hours gets the first answer again (an error does not use the key up).


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The event: its id, its slug (eg summer-quiz) or its code (EV-XXXXX). |
| Idempotency-Key | header | string |  | Optional. A unique value for this message or list (eg a UUID). The same request with the same key within 24 hours gets the first answer again, and nothing is sent twice. Ignored by dry runs. |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| refund | string (all \| prices \| none) | yes | all: everything paid goes back. prices: the ticket prices without booking fees and donations. none: the tickets are voided and no money moves. |
| reason | string |  | Told to the ticket holders. |
| notify | boolean |  | false: do not tell the ticket holders. |
| confirm | string (CANCEL) | yes | Must be the word CANCEL. |


Example answer:

```json
{
  "success": true,
  "request_id": "t6ex7",
  "event": {
    "id": 12,
    "slug": "summer-quiz",
    "code": "EV-7H3KQ",
    "name": "Summer Quiz",
    "summary": "A night of questions on the terrace.",
    "description": "",
    "status": "cancelled",
    "sales": "on",
    "visibility": "public",
    "schedule": "single",
    "seating": "none",
    "archived": false,
    "timezone": "Australia/Sydney",
    "currency": "AUD",
    "capacity": 120,
    "held_back": 0,
    "url": "https://www.app2email.com/events/k3XbQ9rTzP2mWv7/summer-quiz",
    "cover_url": "",
    "settings": {
      "doors_min": 30,
      "sales_end": "start",
      "sales_end_min": 60,
      "place": "venue",
      "venue": {
        "name": "The Terrace",
        "address": "12 Harbour Street, Sydney",
        "map": "",
        "lat": 0,
        "lng": 0,
        "pin": false,
        "note": "",
        "hide_address": false
      },
      "online": {
        "url": "",
        "note": ""
      },
      "age": "",
      "age_text": "",
      "access_info": "",
      "max_per_order": 10,
      "max_per_buyer": 0,
      "show_remaining": "low",
      "fee": {
        "ticket_minor": 0,
        "order_minor": 0,
        "show": "included"
      },
      "tax": {
        "rate": 0,
        "label": "VAT",
        "inclusive": true
      },
      "donation": {
        "enabled": false,
        "amounts": []
      },
      "checkout": {
        "email": "optional"
      },
      "names": "buyer",
      "questions": [],
      "terms_text": "",
      "terms_url": "",
      "marketing_optin": false,
      "seat": {
        "pick": "buyer",
        "no_single": true
      },
      "reminders": [
        1440
      ],
      "reminder_note": "",
      "holder_changes": true,
      "refund_policy": "none",
      "refund_days": 7,
      "refund_text": "",
      "waitlist": "off",
      "door": {
        "opens_min": 120,
        "reentry": "no",
        "gates": [
          {
            "id": "g1",
            "name": "Main entrance",
            "type_ids": []
          }
        ]
      },
      "brand": {
        "color": ""
      },
      "ticket_style": null
    },
    "from_price": 12.0,
    "from_price_label": "A$12.00",
    "tickets_sold": 86,
    "dates_count": 0,
    "next_date": null,
    "seat_plan": null,
    "sales_start": null,
    "published": "2026-11-06T01:00:00.000Z",
    "ended": null,
    "cancelled": "2026-11-06T01:00:00.000Z",
    "cancel_reason": "The venue is closed",
    "created_by": "API key Zapier",
    "created": "2026-11-06T01:00:00.000Z",
    "updated": "2026-11-06T01:00:00.000Z",
    "dates": [],
    "dates_more": false,
    "types": [
      {
        "id": 44,
        "event_id": 12,
        "name": "Adult",
        "description": "",
        "role": "ticket",
        "status": "active",
        "visibility": "public",
        "sort": 1,
        "price_mode": "fixed",
        "price": 12.0,
        "price_label": "A$12.00",
        "price_all_in": 12.0,
        "price_all_in_label": "A$12.00",
        "min_price": 0,
        "admits": 1,
        "quantity": 0,
        "pool_id": 0,
        "opens_after": 0,
        "needs": 0,
        "needs_each": false,
        "min_per_order": 1,
        "max_per_order": 0,
        "sales_start": null,
        "sales_end": null,
        "sales_end_days": 0,
        "date_ids": [],
        "door_note": "",
        "created": "2026-11-06T01:00:00.000Z",
        "updated": "2026-11-06T01:00:00.000Z"
      }
    ]
  },
  "started": true,
  "note": "Cancelled. Orders are refunded one by one in the background; ticket.event.cancelled is sent for each date when it has finished."
}
```


### `GET /tickets/events/{id}/dates`

The dates of an event with what is sold and left. Scope: `tickets:manage`. Docs: https://www.app2email.com/docs/api/tickets-and-pay/list-ticket-dates

Scope: `tickets:manage`. The dates of an event, soonest first, each with what is sold, held in baskets, left and checked in. `status` is scheduled (the default), ended, cancelled or all; `from` and `to` are days (YYYY-MM-DD in the event's time zone) or ISO 8601 times. Page with `next_cursor`.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The event: its id, its slug (eg summer-quiz) or its code (EV-XXXXX). |
| status | query | string (scheduled \| ended \| cancelled \| all) |  | Default scheduled. |
| from | query | string |  | Dates that start on or after this day (YYYY-MM-DD in the event's time zone) or ISO 8601 time. |
| to | query | string |  | Dates that start up to this day (included) or ISO 8601 time. |
| limit | query | integer |  | How many (1 to 200, default 50). |
| cursor | query | string |  | The next_cursor of the previous answer, unchanged. Leave out for the first page. |


Example answer:

```json
{
  "success": true,
  "request_id": "t7dl8",
  "dates": [
    {
      "id": 31,
      "event_id": 12,
      "start": "2026-12-12T08:30:00.000Z",
      "end": "2026-12-12T10:30:00.000Z",
      "start_local": "2026-12-12T19:30",
      "end_local": "2026-12-12T21:30",
      "label": "",
      "capacity": 120,
      "sales": "on",
      "status": "scheduled",
      "sold": 86,
      "people": 86,
      "held": 2,
      "left": 32,
      "checked_in": 0,
      "sold_out": false,
      "changed": null,
      "cancelled": null
    }
  ],
  "next_cursor": null,
  "count": 1,
  "timezone": "Australia/Sydney"
}
```


### `POST /tickets/events/{id}/dates`

Add a date to an event. Scope: `tickets:manage`. Docs: https://www.app2email.com/docs/api/tickets-and-pay/create-ticket-date

Scope: `tickets:manage`. Not with a sandbox key. `start` is local time in the event's time zone or ISO 8601 with an offset, in the future. `end` defaults to 120 minutes after `start` (it must be after it, at most 31 days later). `capacity`: -1 = the event's (the default), 0 = no limit, else people. 409 `ticket_limit_reached` at 400 scheduled dates; 409 `ticket_not_allowed` when the event is cancelled; 400 `invalid_ticket_event` when the event already has a date at that time. Send an `Idempotency-Key` header to retry safely: the same key and body within 24 hours gets the first answer again (an error does not use the key up).


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The event: its id, its slug (eg summer-quiz) or its code (EV-XXXXX). |
| Idempotency-Key | header | string |  | Optional. A unique value for this message or list (eg a UUID). The same request with the same key within 24 hours gets the first answer again, and nothing is sent twice. Ignored by dry runs. |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| start | string |  | Needed for a new date, in the future. Local time in the event's time zone (2026-12-12T19:30) or ISO 8601 with an offset (2026-12-12T19:30:00+11:00). |
| end | string |  | After start, at most 31 days later. Default for a new date: 120 minutes after start. |
| label | string |  |  |
| capacity | integer |  | -1 = the event's (the default of a new date), 0 = no limit, else people. |
| sales | string (on \| paused) |  | Only when changing a date. |
| notify | boolean |  | Only when changing a date. true: tell ticket holders about a new time. |


### `PATCH /tickets/dates/{date_id}`

Change a date: time, label, capacity, sales on or paused. Scope: `tickets:manage`. Docs: https://www.app2email.com/docs/api/tickets-and-pay/update-ticket-date

Scope: `tickets:manage`. Not with a sandbox key. Send only the keys to change: `start`, `end`, `label`, `capacity`, `sales` (on or paused). `notify` true tells the ticket holders about a new time, on WhatsApp or by email. A date with valid tickets cannot be moved into the past. 400 `nothing_to_change` without any of the keys. `ticket.event.sold_out` is sent when a lower limit makes a date full.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| date_id | path | string | yes | The date's id. |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| start | string |  | Needed for a new date, in the future. Local time in the event's time zone (2026-12-12T19:30) or ISO 8601 with an offset (2026-12-12T19:30:00+11:00). |
| end | string |  | After start, at most 31 days later. Default for a new date: 120 minutes after start. |
| label | string |  |  |
| capacity | integer |  | -1 = the event's (the default of a new date), 0 = no limit, else people. |
| sales | string (on \| paused) |  | Only when changing a date. |
| notify | boolean |  | Only when changing a date. true: tell ticket holders about a new time. |


Example answer:

```json
{
  "success": true,
  "request_id": "t9du1",
  "date": {
    "id": 31,
    "event_id": 12,
    "start": "2026-12-12T09:00:00.000Z",
    "end": "2026-12-12T11:00:00.000Z",
    "start_local": "2026-12-12T20:00",
    "end_local": "2026-12-12T22:00",
    "label": "",
    "capacity": 120,
    "sales": "on",
    "status": "scheduled",
    "sold": 86,
    "people": 86,
    "held": 2,
    "left": 32,
    "checked_in": 0,
    "sold_out": false,
    "changed": "2026-11-06T01:00:00.000Z",
    "cancelled": null
  },
  "note": "Saved. Ticket holders were told."
}
```


### `POST /tickets/dates/{date_id}/cancel`

Cancel one date and refund or void its tickets. Scope: `tickets:manage`. Docs: https://www.app2email.com/docs/api/tickets-and-pay/cancel-ticket-date

Scope: `tickets:manage`. Not with a sandbox key. Cancels this one date; the other dates of the event go on. `refund`: all = everything paid goes back, prices = the ticket prices without booking fees and donations, none = the tickets are voided and no money moves. `confirm` must be the word CANCEL. The answer comes at once (`started` true); the orders are refunded one by one in the background, the ticket holders are told unless `notify` is false, `ticket.order.refunded` is sent for each order and `ticket.event.cancelled` when it has finished. It cannot be undone. 409 `ticket_not_allowed` when the date is already cancelled or has ended. Send an `Idempotency-Key` header to retry safely: the same key and body within 24 hours gets the first answer again (an error does not use the key up).


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| date_id | path | string | yes | The date's id. |
| Idempotency-Key | header | string |  | Optional. A unique value for this message or list (eg a UUID). The same request with the same key within 24 hours gets the first answer again, and nothing is sent twice. Ignored by dry runs. |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| refund | string (all \| prices \| none) | yes | all: everything paid goes back. prices: the ticket prices without booking fees and donations. none: the tickets are voided and no money moves. |
| reason | string |  | Told to the ticket holders. |
| notify | boolean |  | false: do not tell the ticket holders. |
| confirm | string (CANCEL) | yes | Must be the word CANCEL. |


Example answer:

```json
{
  "success": true,
  "request_id": "t1dx2",
  "date": {
    "id": 31,
    "event_id": 12,
    "start": "2026-12-12T08:30:00.000Z",
    "end": "2026-12-12T10:30:00.000Z",
    "start_local": "2026-12-12T19:30",
    "end_local": "2026-12-12T21:30",
    "label": "",
    "capacity": 120,
    "sales": "on",
    "status": "cancelled",
    "sold": 86,
    "people": 86,
    "held": 2,
    "left": 32,
    "checked_in": 0,
    "sold_out": false,
    "changed": null,
    "cancelled": "2026-11-06T01:00:00.000Z"
  },
  "started": true,
  "note": "Cancelled. Orders are refunded one by one in the background; ticket.event.cancelled is sent for each date when it has finished."
}
```


### `GET /tickets/dates/{date_id}/door`

The door list of a date for your own scanner. Scope: `tickets:manage`. Docs: https://www.app2email.com/docs/api/tickets-and-pay/get-ticket-door-list

Scope: `tickets:manage`. For a scanner of your own. Each ticket of the date comes with `code_sha256`, the lower-case hex SHA-256 of the text in its QR code: hash what you scan and look it up, so the codes themselves never leave app2email. No contact, email or money is in the list. The first calls page through the date (while `more` is true, send `cursor` as `since`); later the same call with the last `cursor` answers only what changed, and `gone` lists the ids that are no longer tickets of this date. Record an admission with POST /tickets/check-ins.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| date_id | path | string | yes | The date's id. |
| since | query | string |  | The cursor of an earlier answer. Left out: from the start. |
| limit | query | integer |  | How many (1 to 2000, default 2000). |


Example answer:

```json
{
  "success": true,
  "request_id": "t2dd3",
  "date": {
    "id": 31,
    "event_id": 12,
    "start": "2026-12-12T08:30:00.000Z",
    "end": "2026-12-12T10:30:00.000Z",
    "start_local": "2026-12-12T19:30",
    "end_local": "2026-12-12T21:30",
    "label": "",
    "capacity": 120,
    "sales": "on",
    "status": "scheduled",
    "sold": null,
    "people": null,
    "held": null,
    "left": null,
    "checked_in": null,
    "sold_out": false,
    "changed": null,
    "cancelled": null
  },
  "counts": {
    "sold": 86,
    "in": 0,
    "to_come": 86
  },
  "tickets": [
    {
      "id": 501,
      "code_sha256": "5f1d0c4b8e2a7936d1c0b5a4f3e2d1c0b9a8f7e6d5c4b3a2f1e0d9c8b7a6f5e4",
      "status": "valid",
      "type_id": 44,
      "type_name": "Adult",
      "role": "ticket",
      "holder_name": "John Smith",
      "seat_label": "",
      "admits": 1,
      "check_in": {
        "people": 0,
        "inside": 0,
        "entries": 0,
        "first_at": null,
        "last_at": null,
        "last_out_at": null,
        "gate": ""
      },
      "door_note": "",
      "id_check": "",
      "order_reference": "TK-7H3KQ9",
      "passed_on": false,
      "answers": []
    }
  ],
  "gone": [],
  "cursor": "u1793926800000000.501",
  "more": false,
  "count": 1
}
```


### `GET /tickets/events/{id}/types`

The ticket types and extras of an event. Scope: `tickets:manage`. Docs: https://www.app2email.com/docs/api/tickets-and-pay/list-ticket-types

Scope: `tickets:manage`. The ticket types and the extras (role addon) of an event, in their order, with the price as typed and the all-in price a buyer pays. `archived=true` includes the archived ones.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The event: its id, its slug (eg summer-quiz) or its code (EV-XXXXX). |
| archived | query | boolean |  | true: include the archived ticket types. |


Example answer:

```json
{
  "success": true,
  "request_id": "t3tl4",
  "types": [
    {
      "id": 44,
      "event_id": 12,
      "name": "Adult",
      "description": "",
      "role": "ticket",
      "status": "active",
      "visibility": "public",
      "sort": 1,
      "price_mode": "fixed",
      "price": 12.0,
      "price_label": "A$12.00",
      "price_all_in": 12.0,
      "price_all_in_label": "A$12.00",
      "min_price": 0,
      "admits": 1,
      "quantity": 0,
      "pool_id": 0,
      "opens_after": 0,
      "needs": 0,
      "needs_each": false,
      "min_per_order": 1,
      "max_per_order": 0,
      "sales_start": null,
      "sales_end": null,
      "sales_end_days": 0,
      "date_ids": [],
      "door_note": "",
      "created": "2026-11-06T01:00:00.000Z",
      "updated": "2026-11-06T01:00:00.000Z"
    }
  ],
  "currency": "AUD"
}
```


### `POST /tickets/events/{id}/types`

Add a ticket type or an extra to an event. Scope: `tickets:manage`. Docs: https://www.app2email.com/docs/api/tickets-and-pay/create-ticket-type

Scope: `tickets:manage`. Not with a sandbox key. `name` is needed; everything else has a default (a free ticket that admits one person and has no limit of its own). `role` addon makes an extra such as parking, bought together with a ticket. `price_mode` choose lets the buyer name the amount, from `min_price`. `pool_id`, `opens_after` and `needs` point at a pool or another ticket type of the same event (0 = none). 409 `ticket_limit_reached` at 40 ticket types. Send an `Idempotency-Key` header to retry safely: the same key and body within 24 hours gets the first answer again (an error does not use the key up).


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The event: its id, its slug (eg summer-quiz) or its code (EV-XXXXX). |
| Idempotency-Key | header | string |  | Optional. A unique value for this message or list (eg a UUID). The same request with the same key within 24 hours gets the first answer again, and nothing is sent twice. Ignored by dry runs. |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| name | string |  | Needed for a new ticket type. |
| price | number |  | In the event's currency, with at most its decimals. Default 0. |
| role | string (ticket \| addon) |  | Default ticket. |
| description | string |  |  |
| visibility | string (public \| hidden) |  | Default public. |
| price_mode | string (fixed \| choose) |  | Default fixed. |
| min_price | number |  | price_mode choose: the least amount. Default 0. |
| admits | integer |  |  |
| quantity | integer |  | 0 = no limit of its own. |
| pool_id | integer |  | A pool of the same event. 0 = none. |
| opens_after | integer |  | Another ticket type of the same event. 0 = none. |
| needs | integer |  | Another ticket type of the same event. 0 = none. |
| needs_each | boolean |  |  |
| min_per_order | integer |  |  |
| max_per_order | integer |  | 0 = the event's order limit. |
| sales_start | string |  | Local time in the event's time zone (2026-12-12T19:30) or ISO 8601 with an offset (2026-12-12T19:30:00+11:00). null = with the event. |
| sales_end | string |  | Local time in the event's time zone (2026-12-12T19:30) or ISO 8601 with an offset (2026-12-12T19:30:00+11:00). null = with the event's rule. |
| sales_end_days | integer |  |  |
| date_ids | array of integer |  | Dates of the same event. [] = every date. |
| door_note | string |  |  |
| sort | integer |  | Default: last. |
| status | string (active \| archived) |  | Only when changing a ticket type. |


### `PATCH /tickets/types/{type_id}`

Change or archive a ticket type. Scope: `tickets:manage`. Docs: https://www.app2email.com/docs/api/tickets-and-pay/update-ticket-type

Scope: `tickets:manage`. Not with a sandbox key. Send only the keys to change. `status` archived takes the ticket type off sale everywhere, at any time (the tickets sold stay valid); back to active is refused with 409 `ticket_limit_reached` while the event has 40 active ticket types. A ticket type on a seat plan is linked to its seat category on the dashboard, not here. 400 `nothing_to_change` without any key. `ticket.event.sold_out` is sent when a lower limit makes a date full.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| type_id | path | string | yes | The ticket type's id. |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| name | string |  | Needed for a new ticket type. |
| price | number |  | In the event's currency, with at most its decimals. Default 0. |
| role | string (ticket \| addon) |  | Default ticket. |
| description | string |  |  |
| visibility | string (public \| hidden) |  | Default public. |
| price_mode | string (fixed \| choose) |  | Default fixed. |
| min_price | number |  | price_mode choose: the least amount. Default 0. |
| admits | integer |  |  |
| quantity | integer |  | 0 = no limit of its own. |
| pool_id | integer |  | A pool of the same event. 0 = none. |
| opens_after | integer |  | Another ticket type of the same event. 0 = none. |
| needs | integer |  | Another ticket type of the same event. 0 = none. |
| needs_each | boolean |  |  |
| min_per_order | integer |  |  |
| max_per_order | integer |  | 0 = the event's order limit. |
| sales_start | string |  | Local time in the event's time zone (2026-12-12T19:30) or ISO 8601 with an offset (2026-12-12T19:30:00+11:00). null = with the event. |
| sales_end | string |  | Local time in the event's time zone (2026-12-12T19:30) or ISO 8601 with an offset (2026-12-12T19:30:00+11:00). null = with the event's rule. |
| sales_end_days | integer |  |  |
| date_ids | array of integer |  | Dates of the same event. [] = every date. |
| door_note | string |  |  |
| sort | integer |  | Default: last. |
| status | string (active \| archived) |  | Only when changing a ticket type. |


Example answer:

```json
{
  "success": true,
  "request_id": "t5tu6",
  "type": {
    "id": 44,
    "event_id": 12,
    "name": "Adult",
    "description": "",
    "role": "ticket",
    "status": "active",
    "visibility": "public",
    "sort": 1,
    "price_mode": "fixed",
    "price": 14.0,
    "price_label": "A$14.00",
    "price_all_in": 14.0,
    "price_all_in_label": "A$14.00",
    "min_price": 0,
    "admits": 1,
    "quantity": 80,
    "pool_id": 0,
    "opens_after": 0,
    "needs": 0,
    "needs_each": false,
    "min_per_order": 1,
    "max_per_order": 0,
    "sales_start": null,
    "sales_end": null,
    "sales_end_days": 0,
    "date_ids": [],
    "door_note": "",
    "created": "2026-11-06T01:00:00.000Z",
    "updated": "2026-11-06T01:00:00.000Z"
  },
  "note": "Saved."
}
```


### `GET /tickets/events/{id}/availability`

What is on sale and how many are left for a date. Scope: `tickets:manage`. Docs: https://www.app2email.com/docs/api/tickets-and-pay/get-ticket-availability

Scope: `tickets:manage`. For one date of an event: `on_sale` (buyers can buy now), `closed` (cancelled or ended when the date takes no order from anyone), `sold_out`, and every active ticket type with its `state` as a buyer meets it, how many are `left` (null: nothing limits it), the most one order may take (`max`) and the all-in price. `date_id` is needed when the event has several scheduled dates (400 `invalid_ticket_event` without it). Buyers buy on the event's `url`.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The event: its id, its slug (eg summer-quiz) or its code (EV-XXXXX). |
| date_id | query | integer |  | The date's id. Needed when the event has more than one scheduled date. |


Example answer:

```json
{
  "success": true,
  "request_id": "t6av7",
  "event": {
    "id": 12,
    "name": "Summer Quiz",
    "slug": "summer-quiz",
    "status": "published",
    "sales": "on",
    "currency": "AUD",
    "url": "https://www.app2email.com/events/k3XbQ9rTzP2mWv7/summer-quiz"
  },
  "date": {
    "id": 31,
    "event_id": 12,
    "start": "2026-12-12T08:30:00.000Z",
    "end": "2026-12-12T10:30:00.000Z",
    "start_local": "2026-12-12T19:30",
    "end_local": "2026-12-12T21:30",
    "label": "",
    "capacity": 120,
    "sales": "on",
    "status": "scheduled",
    "sold": 86,
    "people": 86,
    "held": 2,
    "left": 32,
    "checked_in": 0,
    "sold_out": false,
    "changed": null,
    "cancelled": null
  },
  "on_sale": true,
  "closed": "",
  "sold_out": false,
  "max_per_order": 10,
  "types": [
    {
      "type_id": 44,
      "name": "Adult",
      "role": "ticket",
      "visibility": "public",
      "state": "on_sale",
      "left": 32,
      "max": 10,
      "price": 12.0,
      "price_label": "A$12.00",
      "sales_end": "2026-12-12T08:30:00.000Z"
    }
  ]
}
```


### `GET /tickets/orders`

The ticket orders, newest first. Scope: `tickets:manage`. Docs: https://www.app2email.com/docs/api/tickets-and-pay/list-ticket-orders

Scope: `tickets:manage`. Newest first. Left out, `status` gives every order except the unfinished checkouts (pending and expired). Find a buyer's orders with `contact`, `email` or `q` (the reference, the buyer's or a holder's name, a seat label, a promo code). `from` and `to` filter by the day the order was made; `attention=true` gives the orders that need a look (a failed or disputed payment, a refund that does not add up); `tickets=true` adds each order's tickets. `page_url` opens the tickets without a login: give it only to the buyer. Page with `next_cursor`.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| event_id | query | integer |  | Only orders of this event (its id). |
| date_id | query | integer |  | Only orders for this date (its id). |
| status | query | string (pending \| confirmed \| partly_refunded \| refunded \| cancelled \| expired) |  | Only orders in this state. Left out: every state except pending and expired. |
| kind | query | string (online \| free \| comp \| outside) |  | online: paid by card. free: a free order. comp: complimentary. outside: paid outside. |
| contact | query | string |  | The buyer: a WhatsApp number with country code, digits only, or a business-scoped user id. |
| email | query | string |  | The buyer's email address. |
| q | query | string |  | Search in the reference, the buyer's or a holder's name, a seat label or a promo code (2 to 80 characters). |
| from | query | string |  | Orders made from this day (YYYY-MM-DD in the number's time zone) or ISO 8601 time. |
| to | query | string |  | Orders made up to this day (included) or ISO 8601 time. |
| attention | query | boolean |  | true: only orders that need a look. |
| tickets | query | boolean |  | true: each order carries its tickets. |
| limit | query | integer |  | How many (1 to 200, default 50). |
| cursor | query | string |  | The next_cursor of the previous answer, unchanged. Leave out for the first page. |


Example answer:

```json
{
  "success": true,
  "request_id": "t7ol8",
  "orders": [
    {
      "id": 8812,
      "reference": "TK-7H3KQ9",
      "status": "confirmed",
      "kind": "comp",
      "channel": "api",
      "source": "",
      "event": {
        "id": 12,
        "name": "Summer Quiz",
        "slug": "summer-quiz"
      },
      "date": {
        "id": 31,
        "start": "2026-12-12T08:30:00.000Z",
        "start_local": "2026-12-12T19:30",
        "label": ""
      },
      "buyer": {
        "name": "John Smith",
        "contact": "61412345678",
        "email": "",
        "no_whatsapp": false
      },
      "currency": "AUD",
      "total": 0,
      "total_label": "A$0.00",
      "tickets_total": 0,
      "order_fee": 0,
      "donation": 0,
      "discount": 24.0,
      "fees": 0,
      "tax": 0,
      "refunded": 0,
      "refunded_label": "",
      "ticket_count": 2,
      "people_count": 2,
      "addon_count": 0,
      "promo_code": "",
      "payment": {
        "id": null,
        "method": "",
        "note": ""
      },
      "comp_reason": "guest",
      "staff_note": "",
      "created_by": "API key Zapier",
      "attention": "",
      "close_reason": "",
      "refund_request": null,
      "answers": {},
      "marketing_optin": false,
      "erased": false,
      "page_url": "https://www.app2email.com/t/oq3k7m2xw5ya4n6bt2hc7r5dz3ef",
      "expires": null,
      "confirmed": "2026-11-06T01:00:00.000Z",
      "cancelled": null,
      "refunded_at": null,
      "created": "2026-11-06T01:00:00.000Z",
      "updated": "2026-11-06T01:00:00.000Z"
    }
  ],
  "next_cursor": null,
  "count": 1
}
```


### `POST /tickets/orders`

Issue complimentary tickets or record a sale paid outside. Scope: `tickets:manage`. Docs: https://www.app2email.com/docs/api/tickets-and-pay/create-ticket-order

Scope: `tickets:manage`. Not with a sandbox key. Issues the tickets at once and never takes money: `kind` comp makes complimentary tickets (every price 0), `kind` outside records a sale that was paid outside app2email (cash, a bank transfer, a card machine) at the ticket prices. `items` names the ticket types and quantities; on an event with a seat plan the best free seats are taken unless `seat_keys` names them. Unless `notify` is false the buyer gets the tickets on WhatsApp (when `buyer.contact` is given) and by email (when `buyer.email` is given); with neither, share `order.page_url` yourself. `check_in_now` checks every ticket in at once (a sale at the door). `ticket.order.confirmed` is sent. Sales windows and hidden ticket types do not bind an order made here; the places kept for the door stay kept. 409 `tickets_sold_out` when there is no room, 409 `tickets_not_on_sale` for a date that is cancelled or over, 403 `tickets_not_enabled` while ticket sales are switched off. Send an `Idempotency-Key` header to retry safely: the same key and body within 24 hours gets the first answer again (an error does not use the key up).


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| Idempotency-Key | header | string |  | Optional. A unique value for this message or list (eg a UUID). The same request with the same key within 24 hours gets the first answer again, and nothing is sent twice. Ignored by dry runs. |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| event_id | string | yes | The event: its id, its slug or its code (EV-XXXXX). |
| date_id | integer |  | Needed when the event has more than one scheduled date. |
| kind | string (comp \| outside) | yes | comp: complimentary tickets, every price 0. outside: a sale paid outside app2email (cash, a bank transfer, a card machine); the prices are recorded, no money is taken. |
| items | array of object | yes | What to issue: one entry per ticket type. |
| buyer | object |  | Who gets the tickets. All optional. |
|   name | string |  |  |
|   contact | string |  | A WhatsApp number with country code, digits only, or a business-scoped user id. |
|   email | string |  |  |
| holder_names | array of string |  | One name per ticket, in the order of items. Empty or left out: the buyer's name. |
| comp_reason | string (guest \| artist \| press \| sponsor \| staff \| prize \| other) |  | kind comp. |
| payment_method | string (cash \| bank \| card_machine \| other) |  | kind outside. |
| payment_note | string |  | kind outside: a note about the payment. |
| note | string |  | An internal note on the order. |
| notify | boolean |  | false: do not send the tickets to the buyer. |
| check_in_now | boolean |  | true: check every ticket in at once (a sale at the door). |
| gate | string |  | With check_in_now: the id of the entrance. Default: the event's first. |


### `GET /tickets/orders/{id}`

One order with its tickets, by id or reference. Scope: `tickets:manage`. Docs: https://www.app2email.com/docs/api/tickets-and-pay/get-ticket-order

Scope: `tickets:manage`. By id or reference (TK-XXXXXX). The order with its money, the buyer and every ticket with its status and check-in state. `page_url` (on the order and on each valid ticket) opens the tickets without a login: treat it like a password and give it only to the buyer.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The order: its id or its reference (TK-XXXXXX). |


Example answer:

```json
{
  "success": true,
  "request_id": "t9og1",
  "order": {
    "id": 8812,
    "reference": "TK-7H3KQ9",
    "status": "confirmed",
    "kind": "comp",
    "channel": "api",
    "source": "",
    "event": {
      "id": 12,
      "name": "Summer Quiz",
      "slug": "summer-quiz"
    },
    "date": {
      "id": 31,
      "start": "2026-12-12T08:30:00.000Z",
      "start_local": "2026-12-12T19:30",
      "label": ""
    },
    "buyer": {
      "name": "John Smith",
      "contact": "61412345678",
      "email": "",
      "no_whatsapp": false
    },
    "currency": "AUD",
    "total": 0,
    "total_label": "A$0.00",
    "tickets_total": 0,
    "order_fee": 0,
    "donation": 0,
    "discount": 24.0,
    "fees": 0,
    "tax": 0,
    "refunded": 0,
    "refunded_label": "",
    "ticket_count": 2,
    "people_count": 2,
    "addon_count": 0,
    "promo_code": "",
    "payment": {
      "id": null,
      "method": "",
      "note": ""
    },
    "comp_reason": "guest",
    "staff_note": "",
    "created_by": "API key Zapier",
    "attention": "",
    "close_reason": "",
    "refund_request": null,
    "answers": {},
    "marketing_optin": false,
    "erased": false,
    "page_url": "https://www.app2email.com/t/oq3k7m2xw5ya4n6bt2hc7r5dz3ef",
    "expires": null,
    "confirmed": "2026-11-06T01:00:00.000Z",
    "cancelled": null,
    "refunded_at": null,
    "created": "2026-11-06T01:00:00.000Z",
    "updated": "2026-11-06T01:00:00.000Z",
    "tickets": [
      {
        "id": 501,
        "order_id": 8812,
        "order_reference": "TK-7H3KQ9",
        "event_id": 12,
        "date_id": 31,
        "type_id": 44,
        "type_name": "Adult",
        "role": "ticket",
        "seq": 1,
        "status": "valid",
        "holder_name": "John Smith",
        "answers": {},
        "seat": null,
        "admits": 1,
        "check_in": {
          "people": 0,
          "inside": 0,
          "entries": 0,
          "first_at": null,
          "last_at": null,
          "last_out_at": null,
          "gate": ""
        },
        "currency": "AUD",
        "price": 0,
        "price_label": "A$0.00",
        "face": 12.0,
        "refunded": 0,
        "refunded_at": null,
        "block_reason": "",
        "passed_on": false,
        "replaces_id": 0,
        "replaced_by_id": 0,
        "page_url": "https://www.app2email.com/t/kz5n2r7bq4hx3m6wy2ta5d7ce4gf",
        "created": "2026-11-06T01:00:00.000Z",
        "updated": "2026-11-06T01:00:00.000Z"
      },
      {
        "id": 502,
        "order_id": 8812,
        "order_reference": "TK-7H3KQ9",
        "event_id": 12,
        "date_id": 31,
        "type_id": 44,
        "type_name": "Adult",
        "role": "ticket",
        "seq": 2,
        "status": "valid",
        "holder_name": "John Smith",
        "answers": {},
        "seat": null,
        "admits": 1,
        "check_in": {
          "people": 0,
          "inside": 0,
          "entries": 0,
          "first_at": null,
          "last_at": null,
          "last_out_at": null,
          "gate": ""
        },
        "currency": "AUD",
        "price": 0,
        "price_label": "A$0.00",
        "face": 12.0,
        "refunded": 0,
        "refunded_at": null,
        "block_reason": "",
        "passed_on": false,
        "replaces_id": 0,
        "replaced_by_id": 0,
        "page_url": "https://www.app2email.com/t/kb7m4q2xr6ta3n5wz2hc4d7ey5gj",
        "created": "2026-11-06T01:00:00.000Z",
        "updated": "2026-11-06T01:00:00.000Z"
      }
    ]
  }
}
```


### `POST /tickets/orders/{id}/refund`

Refund an order or some of its tickets. Scope: `tickets:manage`. Docs: https://www.app2email.com/docs/api/tickets-and-pay/refund-ticket-order

Scope: `tickets:manage`. Not with a sandbox key. Refunds every valid ticket of the order, or only `ticket_ids`. `what`: all (the default) or prices (without booking fees and donations). `money` says how the money goes back: provider = through the business's own Stripe or PayPal account (real money, it cannot be undone), recorded = it was handed back outside, outside = the business refunded it at Stripe or PayPal itself, none = cancel without a refund. Left out, it follows the order: provider for an online order, recorded for a sale paid outside, none for free and complimentary tickets. The refunded tickets stop working at once and their places go back on sale; the buyer is told unless `notify` is false. `ticket.order.refunded` is sent. 409 `refund_not_possible` when nothing is left to refund, 409 `payments_not_connected`, 502 `payment_provider_error`. Send an `Idempotency-Key` header to retry safely: the same key and body within 24 hours gets the first answer again (an error does not use the key up).


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The order: its id or its reference (TK-XXXXXX). |
| Idempotency-Key | header | string |  | Optional. A unique value for this message or list (eg a UUID). The same request with the same key within 24 hours gets the first answer again, and nothing is sent twice. Ignored by dry runs. |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| ticket_ids | array of integer |  | Tickets of this order. Left out or []: every valid ticket of the order. |
| what | string (all \| prices) |  | all: everything paid for the tickets. prices: without booking fees and donations. |
| money | string (provider \| recorded \| outside \| none) |  | provider: back through the business's own Stripe or PayPal account. recorded: the money was handed back outside. outside: the business refunded it at Stripe or PayPal itself. none: cancel without a refund. Left out: provider for an online order, recorded for a sale paid outside, none for free and complimentary tickets. |
| reason | string |  |  |
| notify | boolean |  | false: do not tell the buyer. |


Example answer:

```json
{
  "success": true,
  "request_id": "t1or2",
  "order": {
    "id": 8812,
    "reference": "TK-7H3KQ9",
    "status": "partly_refunded",
    "kind": "online",
    "channel": "web",
    "source": "",
    "event": {
      "id": 12,
      "name": "Summer Quiz",
      "slug": "summer-quiz"
    },
    "date": {
      "id": 31,
      "start": "2026-12-12T08:30:00.000Z",
      "start_local": "2026-12-12T19:30",
      "label": ""
    },
    "buyer": {
      "name": "John Smith",
      "contact": "61412345678",
      "email": "",
      "no_whatsapp": false
    },
    "currency": "AUD",
    "total": 24.0,
    "total_label": "A$24.00",
    "tickets_total": 24.0,
    "order_fee": 0,
    "donation": 0,
    "discount": 0,
    "fees": 0,
    "tax": 0,
    "refunded": 12.0,
    "refunded_label": "A$12.00",
    "ticket_count": 2,
    "people_count": 2,
    "addon_count": 0,
    "promo_code": "",
    "payment": {
      "id": 15,
      "method": "stripe",
      "note": ""
    },
    "comp_reason": "",
    "staff_note": "",
    "created_by": "customer",
    "attention": "",
    "close_reason": "",
    "refund_request": null,
    "answers": {},
    "marketing_optin": false,
    "erased": false,
    "page_url": "https://www.app2email.com/t/oq3k7m2xw5ya4n6bt2hc7r5dz3ef",
    "expires": null,
    "confirmed": "2026-11-06T01:00:00.000Z",
    "cancelled": null,
    "refunded_at": "2026-11-06T01:00:00.000Z",
    "created": "2026-11-06T01:00:00.000Z",
    "updated": "2026-11-06T01:00:00.000Z",
    "tickets": [
      {
        "id": 501,
        "order_id": 8812,
        "order_reference": "TK-7H3KQ9",
        "event_id": 12,
        "date_id": 31,
        "type_id": 44,
        "type_name": "Adult",
        "role": "ticket",
        "seq": 1,
        "status": "valid",
        "holder_name": "John Smith",
        "answers": {},
        "seat": null,
        "admits": 1,
        "check_in": {
          "people": 0,
          "inside": 0,
          "entries": 0,
          "first_at": null,
          "last_at": null,
          "last_out_at": null,
          "gate": ""
        },
        "currency": "AUD",
        "price": 12.0,
        "price_label": "A$12.00",
        "face": 12.0,
        "refunded": 0,
        "refunded_at": null,
        "block_reason": "",
        "passed_on": false,
        "replaces_id": 0,
        "replaced_by_id": 0,
        "page_url": "https://www.app2email.com/t/kz5n2r7bq4hx3m6wy2ta5d7ce4gf",
        "created": "2026-11-06T01:00:00.000Z",
        "updated": "2026-11-06T01:00:00.000Z"
      },
      {
        "id": 502,
        "order_id": 8812,
        "order_reference": "TK-7H3KQ9",
        "event_id": 12,
        "date_id": 31,
        "type_id": 44,
        "type_name": "Adult",
        "role": "ticket",
        "seq": 2,
        "status": "refunded",
        "holder_name": "John Smith",
        "answers": {},
        "seat": null,
        "admits": 1,
        "check_in": {
          "people": 0,
          "inside": 0,
          "entries": 0,
          "first_at": null,
          "last_at": null,
          "last_out_at": null,
          "gate": ""
        },
        "currency": "AUD",
        "price": 12.0,
        "price_label": "A$12.00",
        "face": 12.0,
        "refunded": 12.0,
        "refunded_at": "2026-11-06T01:00:00.000Z",
        "block_reason": "",
        "passed_on": false,
        "replaces_id": 0,
        "replaced_by_id": 0,
        "page_url": "",
        "created": "2026-11-06T01:00:00.000Z",
        "updated": "2026-11-06T01:00:00.000Z"
      }
    ]
  },
  "refunded": 12.0,
  "refunded_label": "A$12.00",
  "note": "Refunded A$12.00 through Stripe. The tickets are no longer valid."
}
```


### `POST /tickets/orders/{id}/resend`

Send the buyer their tickets again. Scope: `tickets:manage`. Docs: https://www.app2email.com/docs/api/tickets-and-pay/resend-ticket-order

Scope: `tickets:manage`. Not with a sandbox key. No body. The buyer gets the tickets again: a WhatsApp message (inside their 24 hour window, else a template) when the order has a number, and an email when it has an address. `sent` lists what happened per channel. 409 `ticket_not_allowed` when the order has no valid ticket, or neither a WhatsApp number nor an email address. Send an `Idempotency-Key` header to retry safely: the same key and body within 24 hours gets the first answer again (an error does not use the key up).


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The order: its id or its reference (TK-XXXXXX). |
| Idempotency-Key | header | string |  | Optional. A unique value for this message or list (eg a UUID). The same request with the same key within 24 hours gets the first answer again, and nothing is sent twice. Ignored by dry runs. |


Example answer:

```json
{
  "success": true,
  "request_id": "t2os3",
  "sent": [
    {
      "channel": "whatsapp",
      "result": "sent",
      "detail": ""
    }
  ],
  "note": "Sent again."
}
```


### `GET /tickets/issued`

The tickets (attendees) with their check-in state. Scope: `tickets:manage`. Docs: https://www.app2email.com/docs/api/tickets-and-pay/list-tickets

Scope: `tickets:manage`. One row per ticket, by id, with the holder, the seat, the price, the check-in state and the buyer. `event_id`, `date_id` or `order` is needed (400 `invalid_ticket_order` without one). Left out, `status` gives the valid and the blocked tickets and `role` the admission tickets (addon: the extras, all: both). `checked_in=true` gives who is in, `checked_in=false` who has not come yet. Page with `next_cursor`.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| event_id | query | integer |  | The tickets of this event (its id). |
| date_id | query | integer |  | The tickets of this date (its id). |
| type_id | query | integer |  | Only this ticket type (its id). |
| order | query | string |  | The tickets of this order: its id or its reference (TK-XXXXXX). |
| status | query | string (valid \| blocked \| refunded \| cancelled \| transferred) |  | Only tickets in this state. Left out: valid and blocked. |
| checked_in | query | boolean |  | true: only tickets that were used at the door. false: only the ones that were not. |
| role | query | string (ticket \| addon \| all) |  | Default ticket. |
| q | query | string |  | Search in the holder's or the buyer's name, the reference or a seat label (2 to 80 characters). |
| limit | query | integer |  | How many (1 to 200, default 50). |
| cursor | query | string |  | The next_cursor of the previous answer, unchanged. Leave out for the first page. |


Example answer:

```json
{
  "success": true,
  "request_id": "t3il4",
  "tickets": [
    {
      "id": 501,
      "order_id": 8812,
      "order_reference": "TK-7H3KQ9",
      "event_id": 12,
      "date_id": 31,
      "type_id": 44,
      "type_name": "Adult",
      "role": "ticket",
      "seq": 1,
      "status": "valid",
      "holder_name": "John Smith",
      "answers": {},
      "seat": null,
      "admits": 1,
      "check_in": {
        "people": 0,
        "inside": 0,
        "entries": 0,
        "first_at": null,
        "last_at": null,
        "last_out_at": null,
        "gate": ""
      },
      "currency": "AUD",
      "price": 0,
      "price_label": "A$0.00",
      "face": 12.0,
      "refunded": 0,
      "refunded_at": null,
      "block_reason": "",
      "passed_on": false,
      "replaces_id": 0,
      "replaced_by_id": 0,
      "page_url": "https://www.app2email.com/t/kz5n2r7bq4hx3m6wy2ta5d7ce4gf",
      "created": "2026-11-06T01:00:00.000Z",
      "updated": "2026-11-06T01:00:00.000Z",
      "buyer": {
        "name": "John Smith",
        "contact": "61412345678",
        "email": ""
      }
    }
  ],
  "next_cursor": null,
  "count": 1
}
```


### `GET /tickets/issued/{id}`

One ticket. Scope: `tickets:manage`. Docs: https://www.app2email.com/docs/api/tickets-and-pay/get-ticket

Scope: `tickets:manage`. By its id (digits). The text of a ticket's QR code is never accepted in an address: POST /tickets/check-ins takes it. The answer also has the order's id, reference, status and buyer.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The ticket's id (digits). The text of a ticket's QR code is never accepted in an address. |


Example answer:

```json
{
  "success": true,
  "request_id": "t4ig5",
  "ticket": {
    "id": 501,
    "order_id": 8812,
    "order_reference": "TK-7H3KQ9",
    "event_id": 12,
    "date_id": 31,
    "type_id": 44,
    "type_name": "Adult",
    "role": "ticket",
    "seq": 1,
    "status": "valid",
    "holder_name": "John Smith",
    "answers": {},
    "seat": null,
    "admits": 1,
    "check_in": {
      "people": 0,
      "inside": 0,
      "entries": 0,
      "first_at": null,
      "last_at": null,
      "last_out_at": null,
      "gate": ""
    },
    "currency": "AUD",
    "price": 0,
    "price_label": "A$0.00",
    "face": 12.0,
    "refunded": 0,
    "refunded_at": null,
    "block_reason": "",
    "passed_on": false,
    "replaces_id": 0,
    "replaced_by_id": 0,
    "page_url": "https://www.app2email.com/t/kz5n2r7bq4hx3m6wy2ta5d7ce4gf",
    "created": "2026-11-06T01:00:00.000Z",
    "updated": "2026-11-06T01:00:00.000Z"
  },
  "order": {
    "id": 8812,
    "reference": "TK-7H3KQ9",
    "status": "confirmed",
    "buyer": {
      "name": "John Smith",
      "contact": "61412345678",
      "email": ""
    }
  }
}
```


### `POST /tickets/issued/{id}/void`

Void one ticket without a refund. Scope: `tickets:manage`. Docs: https://www.app2email.com/docs/api/tickets-and-pay/void-ticket

Scope: `tickets:manage`. Not with a sandbox key. The ticket stops working at the door and its place is back on sale. No money moves: to give money back use POST /tickets/orders/{id}/refund with `ticket_ids`. The buyer is told only with `notify` true. `ticket.order.refunded` is sent, with `money` none. 409 `ticket_not_allowed` when the ticket is already refunded, cancelled or passed on. Send an `Idempotency-Key` header to retry safely: the same key and body within 24 hours gets the first answer again (an error does not use the key up).


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The ticket's id (digits). The text of a ticket's QR code is never accepted in an address. |
| Idempotency-Key | header | string |  | Optional. A unique value for this message or list (eg a UUID). The same request with the same key within 24 hours gets the first answer again, and nothing is sent twice. Ignored by dry runs. |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| reason | string |  |  |
| notify | boolean |  | true: tell the buyer. |


Example answer:

```json
{
  "success": true,
  "request_id": "t5iv6",
  "ticket": {
    "id": 502,
    "order_id": 8812,
    "order_reference": "TK-7H3KQ9",
    "event_id": 12,
    "date_id": 31,
    "type_id": 44,
    "type_name": "Adult",
    "role": "ticket",
    "seq": 2,
    "status": "cancelled",
    "holder_name": "John Smith",
    "answers": {},
    "seat": null,
    "admits": 1,
    "check_in": {
      "people": 0,
      "inside": 0,
      "entries": 0,
      "first_at": null,
      "last_at": null,
      "last_out_at": null,
      "gate": ""
    },
    "currency": "AUD",
    "price": 0,
    "price_label": "A$0.00",
    "face": 12.0,
    "refunded": 0,
    "refunded_at": null,
    "block_reason": "",
    "passed_on": false,
    "replaces_id": 0,
    "replaced_by_id": 0,
    "page_url": "",
    "created": "2026-11-06T01:00:00.000Z",
    "updated": "2026-11-06T01:00:00.000Z"
  },
  "order": {
    "id": 8812,
    "reference": "TK-7H3KQ9",
    "status": "confirmed",
    "kind": "comp",
    "channel": "api",
    "source": "",
    "event": {
      "id": 12,
      "name": "Summer Quiz",
      "slug": "summer-quiz"
    },
    "date": {
      "id": 31,
      "start": "2026-12-12T08:30:00.000Z",
      "start_local": "2026-12-12T19:30",
      "label": ""
    },
    "buyer": {
      "name": "John Smith",
      "contact": "61412345678",
      "email": "",
      "no_whatsapp": false
    },
    "currency": "AUD",
    "total": 0,
    "total_label": "A$0.00",
    "tickets_total": 0,
    "order_fee": 0,
    "donation": 0,
    "discount": 24.0,
    "fees": 0,
    "tax": 0,
    "refunded": 0,
    "refunded_label": "",
    "ticket_count": 2,
    "people_count": 2,
    "addon_count": 0,
    "promo_code": "",
    "payment": {
      "id": null,
      "method": "",
      "note": ""
    },
    "comp_reason": "guest",
    "staff_note": "",
    "created_by": "API key Zapier",
    "attention": "",
    "close_reason": "",
    "refund_request": null,
    "answers": {},
    "marketing_optin": false,
    "erased": false,
    "page_url": "https://www.app2email.com/t/oq3k7m2xw5ya4n6bt2hc7r5dz3ef",
    "expires": null,
    "confirmed": "2026-11-06T01:00:00.000Z",
    "cancelled": null,
    "refunded_at": null,
    "created": "2026-11-06T01:00:00.000Z",
    "updated": "2026-11-06T01:00:00.000Z",
    "tickets": [
      {
        "id": 501,
        "order_id": 8812,
        "order_reference": "TK-7H3KQ9",
        "event_id": 12,
        "date_id": 31,
        "type_id": 44,
        "type_name": "Adult",
        "role": "ticket",
        "seq": 1,
        "status": "valid",
        "holder_name": "John Smith",
        "answers": {},
        "seat": null,
        "admits": 1,
        "check_in": {
          "people": 0,
          "inside": 0,
          "entries": 0,
          "first_at": null,
          "last_at": null,
          "last_out_at": null,
          "gate": ""
        },
        "currency": "AUD",
        "price": 0,
        "price_label": "A$0.00",
        "face": 12.0,
        "refunded": 0,
        "refunded_at": null,
        "block_reason": "",
        "passed_on": false,
        "replaces_id": 0,
        "replaced_by_id": 0,
        "page_url": "https://www.app2email.com/t/kz5n2r7bq4hx3m6wy2ta5d7ce4gf",
        "created": "2026-11-06T01:00:00.000Z",
        "updated": "2026-11-06T01:00:00.000Z"
      },
      {
        "id": 502,
        "order_id": 8812,
        "order_reference": "TK-7H3KQ9",
        "event_id": 12,
        "date_id": 31,
        "type_id": 44,
        "type_name": "Adult",
        "role": "ticket",
        "seq": 2,
        "status": "cancelled",
        "holder_name": "John Smith",
        "answers": {},
        "seat": null,
        "admits": 1,
        "check_in": {
          "people": 0,
          "inside": 0,
          "entries": 0,
          "first_at": null,
          "last_at": null,
          "last_out_at": null,
          "gate": ""
        },
        "currency": "AUD",
        "price": 0,
        "price_label": "A$0.00",
        "face": 12.0,
        "refunded": 0,
        "refunded_at": null,
        "block_reason": "",
        "passed_on": false,
        "replaces_id": 0,
        "replaced_by_id": 0,
        "page_url": "",
        "created": "2026-11-06T01:00:00.000Z",
        "updated": "2026-11-06T01:00:00.000Z"
      }
    ]
  },
  "note": "Voided. The ticket no longer works at the door and its place is back on sale. No money was moved."
}
```


### `POST /tickets/check-ins`

Check a ticket in (or out) by its code or id. Scope: `tickets:manage`. Docs: https://www.app2email.com/docs/api/tickets-and-pay/check-in-ticket

Scope: `tickets:manage`. Not with a sandbox key. Send `code` (the text of the ticket's QR code; a link or other text around it is fine) with `date_id`, or `ticket_id`. The answer is always 200 when the request was understood: `result` ok and `admitted` true mean let the person in; any other `result` (already_in, not_inside, unknown, refunded, cancelled, transferred, blocked, wrong_event, wrong_date, wrong_gate, too_early, too_late) is a refusal with the reason in `note`, not an error. `direction` out checks out, for events that count people leaving; `people` admits a part of a group ticket; `force` admits although it is too early, too late or the wrong entrance. `check_in.id` is the handle for the undo. `ticket.checked_in` is sent the first time a ticket is admitted. The code of a whole order is not taken: 400 `invalid_ticket_check_in`. Send an `Idempotency-Key` header to retry safely: the same key and body within 24 hours gets the first answer again (an error does not use the key up).


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| Idempotency-Key | header | string |  | Optional. A unique value for this message or list (eg a UUID). The same request with the same key within 24 hours gets the first answer again, and nothing is sent twice. Ignored by dry runs. |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| code | string |  | The text of the ticket's QR code. A link or other text around it is fine. Needs date_id. |
| ticket_id | integer |  | The ticket's id, instead of code. |
| date_id | integer |  | The date the person is entering. Needed with code; with ticket_id it defaults to the ticket's own date. |
| direction | string (in \| out) |  | out: check out, for events that count people leaving. |
| people | integer |  | For a group ticket: how many people enter now. 0 = everyone who is not in yet. |
| gate | string |  | The id of the entrance, one of the event's settings.door.gates. Default: the first. |
| force | boolean |  | true: admit although it is too early, too late or the wrong entrance. |


Example answer:

```json
{
  "success": true,
  "request_id": "t6ci7",
  "result": "ok",
  "admitted": true,
  "people": 1,
  "check_in": {
    "id": 90211,
    "at": "2026-11-06T01:00:00.000Z",
    "direction": "in",
    "gate": "g1",
    "forced": false
  },
  "ticket": {
    "id": 501,
    "order_id": 8812,
    "order_reference": "TK-7H3KQ9",
    "event_id": 12,
    "date_id": 31,
    "type_id": 44,
    "type_name": "Adult",
    "role": "ticket",
    "seq": 1,
    "status": "valid",
    "holder_name": "John Smith",
    "answers": {},
    "seat": null,
    "admits": 1,
    "check_in": {
      "people": 1,
      "inside": 1,
      "entries": 1,
      "first_at": "2026-11-06T01:00:00.000Z",
      "last_at": "2026-11-06T01:00:00.000Z",
      "last_out_at": null,
      "gate": "g1"
    },
    "currency": "AUD",
    "price": 0,
    "price_label": "A$0.00",
    "face": 12.0,
    "refunded": 0,
    "refunded_at": null,
    "block_reason": "",
    "passed_on": false,
    "replaces_id": 0,
    "replaced_by_id": 0,
    "page_url": "https://www.app2email.com/t/kz5n2r7bq4hx3m6wy2ta5d7ce4gf",
    "created": "2026-11-06T01:00:00.000Z",
    "updated": "2026-11-06T01:00:00.000Z"
  },
  "first": null,
  "note": "Checked in."
}
```


### `POST /tickets/check-ins/{scan_id}/undo`

Take a check-in back. Scope: `tickets:manage`. Docs: https://www.app2email.com/docs/api/tickets-and-pay/undo-ticket-check-in

Scope: `tickets:manage`. Not with a sandbox key. No body. Takes one accepted check-in back (`scan_id` is `check_in.id` of the check-in answer), so the ticket can be used again. Once per check-in, while its date has not ended. 404 `ticket_check_in_not_found`; 409 `ticket_not_allowed` when it was already taken back or the date has ended.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| scan_id | path | string | yes | The check-in's id: check_in.id of the answer of POST /tickets/check-ins. |


Example answer:

```json
{
  "success": true,
  "request_id": "t7cu8",
  "undone": true,
  "ticket": {
    "id": 501,
    "order_id": 8812,
    "order_reference": "TK-7H3KQ9",
    "event_id": 12,
    "date_id": 31,
    "type_id": 44,
    "type_name": "Adult",
    "role": "ticket",
    "seq": 1,
    "status": "valid",
    "holder_name": "John Smith",
    "answers": {},
    "seat": null,
    "admits": 1,
    "check_in": {
      "people": 0,
      "inside": 0,
      "entries": 0,
      "first_at": null,
      "last_at": null,
      "last_out_at": null,
      "gate": ""
    },
    "currency": "AUD",
    "price": 0,
    "price_label": "A$0.00",
    "face": 12.0,
    "refunded": 0,
    "refunded_at": null,
    "block_reason": "",
    "passed_on": false,
    "replaces_id": 0,
    "replaced_by_id": 0,
    "page_url": "https://www.app2email.com/t/kz5n2r7bq4hx3m6wy2ta5d7ce4gf",
    "created": "2026-11-06T01:00:00.000Z",
    "updated": "2026-11-06T01:00:00.000Z"
  },
  "note": "Taken back."
}
```


### `GET /tickets/codes`

The promo and access codes with their uses. Scope: `tickets:manage`. Docs: https://www.app2email.com/docs/api/tickets-and-pay/list-ticket-codes

Scope: `tickets:manage`. The promo codes (a discount) and the access codes (they unlock hidden ticket types), by id, each with how many orders and tickets used it. `q` searches in the code, `enabled` filters. Page with `next_cursor`.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| q | query | string |  | Search in the code (2 to 80 characters). |
| enabled | query | boolean |  | true: only codes that are switched on. false: only the ones switched off. |
| limit | query | integer |  | How many (1 to 200, default 50). |
| cursor | query | string |  | The next_cursor of the previous answer, unchanged. Leave out for the first page. |


Example answer:

```json
{
  "success": true,
  "request_id": "t8kl9",
  "codes": [
    {
      "id": 7,
      "code": "EARLY10",
      "kind": "percent",
      "value": 10,
      "currency": "",
      "event_ids": [
        12
      ],
      "type_ids": [],
      "unlocks": [],
      "starts": "",
      "ends": "2026-12-01",
      "limit": 100,
      "limit_unit": "orders",
      "enabled": true,
      "batch": "",
      "uses": {
        "orders": 0,
        "tickets": 0
      },
      "created": "2026-11-06T01:00:00.000Z",
      "updated": "2026-11-06T01:00:00.000Z"
    }
  ],
  "next_cursor": null,
  "count": 1
}
```


### `POST /tickets/codes`

Create a promo or access code. Scope: `tickets:manage`. Docs: https://www.app2email.com/docs/api/tickets-and-pay/create-ticket-code

Scope: `tickets:manage`. Not with a sandbox key. `code` is 3 to 20 characters of A-Z, 0-9, _ and - (stored in upper case). `kind` percent takes a whole `value` from 1 to 100, `kind` amount an amount in `currency` (the default is the number's). `event_ids` and `type_ids` limit where it counts ([] = everywhere), `unlocks` lists hidden ticket types the code opens (then `value` may be 0), `starts` and `ends` are days, `limit` caps the uses per `limit_unit`. 409 `ticket_not_allowed` when a code with this name exists; 409 `ticket_limit_reached` at 1,000 codes. Send an `Idempotency-Key` header to retry safely: the same key and body within 24 hours gets the first answer again (an error does not use the key up).


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| Idempotency-Key | header | string |  | Optional. A unique value for this message or list (eg a UUID). The same request with the same key within 24 hours gets the first answer again, and nothing is sent twice. Ignored by dry runs. |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| code | string |  | Needed for a new code; it cannot be changed later. 3 to 20 characters of A-Z, 0-9, _ and -. |
| kind | string (percent \| amount) |  | Default percent. |
| value | number |  | kind percent: a whole number from 1 to 100. kind amount: an amount in currency. 0 only for a code that unlocks ticket types. |
| currency | string |  | kind amount. Default: the currency new events of the number start with. |
| event_ids | array of integer |  | Events of this number. Default []: every event. |
| type_ids | array of integer |  | Ticket types of this number. Default []: every ticket type. |
| unlocks | array of integer |  | Hidden ticket types of this number that the code opens. |
| starts | string |  | Empty or YYYY-MM-DD. |
| ends | string |  | Empty or YYYY-MM-DD. |
| limit | integer |  | 0 = no limit. |
| limit_unit | string (orders \| tickets) |  | Default orders. |
| enabled | boolean |  |  |


### `PATCH /tickets/codes/{id}`

Change a promo code or switch it off. Scope: `tickets:manage`. Docs: https://www.app2email.com/docs/api/tickets-and-pay/update-ticket-code

Scope: `tickets:manage`. Not with a sandbox key. By id or by the code itself. Send only the keys to change; the code's own text cannot be changed (make a new code instead). `enabled` false switches it off. 400 `nothing_to_change` without any key.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The promo code: its id, or the code itself. |


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| code | string |  | Needed for a new code; it cannot be changed later. 3 to 20 characters of A-Z, 0-9, _ and -. |
| kind | string (percent \| amount) |  | Default percent. |
| value | number |  | kind percent: a whole number from 1 to 100. kind amount: an amount in currency. 0 only for a code that unlocks ticket types. |
| currency | string |  | kind amount. Default: the currency new events of the number start with. |
| event_ids | array of integer |  | Events of this number. Default []: every event. |
| type_ids | array of integer |  | Ticket types of this number. Default []: every ticket type. |
| unlocks | array of integer |  | Hidden ticket types of this number that the code opens. |
| starts | string |  | Empty or YYYY-MM-DD. |
| ends | string |  | Empty or YYYY-MM-DD. |
| limit | integer |  | 0 = no limit. |
| limit_unit | string (orders \| tickets) |  | Default orders. |
| enabled | boolean |  |  |


Example answer:

```json
{
  "success": true,
  "request_id": "t1ku2",
  "code": {
    "id": 7,
    "code": "EARLY10",
    "kind": "percent",
    "value": 10,
    "currency": "",
    "event_ids": [
      12
    ],
    "type_ids": [],
    "unlocks": [],
    "starts": "",
    "ends": "2026-12-01",
    "limit": 100,
    "limit_unit": "orders",
    "enabled": false,
    "batch": "",
    "uses": {
      "orders": 0,
      "tickets": 0
    },
    "created": "2026-11-06T01:00:00.000Z",
    "updated": "2026-11-06T01:00:00.000Z"
  }
}
```


### `DELETE /tickets/codes/{id}`

Delete a promo code no order has used. Scope: `tickets:manage`. Docs: https://www.app2email.com/docs/api/tickets-and-pay/delete-ticket-code

Scope: `tickets:manage`. Not with a sandbox key. By id or by the code itself. Only a code no order has used can be deleted: 409 `ticket_not_allowed` otherwise (switch it off with PATCH /tickets/codes/{id} instead).


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| id | path | string | yes | The promo code: its id, or the code itself. |


Example answer:

```json
{
  "success": true,
  "request_id": "t2kd3",
  "deleted": 7
}
```


### `GET /tickets/waitlist`

The waiting list of a sold-out date. Scope: `tickets:manage`. Docs: https://www.app2email.com/docs/api/tickets-and-pay/list-ticket-waitlist

Scope: `tickets:manage`. The people waiting for a place on one date, in the order they joined. `date_id` is needed (400 `invalid_ticket_event` without it). Left out, `status` gives the waiting and the notified entries. Page with `next_cursor`. `ticket.waitlist.joined` reports each new entry.


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| date_id | query | integer |  | The date's id. Needed. |
| status | query | string (waiting \| notified \| converted \| removed \| expired) |  | Only entries in this state. Left out: waiting and notified. |
| limit | query | integer |  | How many (1 to 200, default 50). |
| cursor | query | string |  | The next_cursor of the previous answer, unchanged. Leave out for the first page. |


Example answer:

```json
{
  "success": true,
  "request_id": "t3wl4",
  "entries": [
    {
      "id": 77,
      "event_id": 12,
      "date_id": 31,
      "type_id": 0,
      "name": "Sample Contact",
      "contact": "61412345678",
      "email": "",
      "quantity": 2,
      "status": "waiting",
      "notified": null,
      "notify_count": 0,
      "order_id": 0,
      "created": "2026-11-06T01:00:00.000Z"
    }
  ],
  "next_cursor": null,
  "count": 1
}
```


### `GET /tickets/stats`

Sales and check-in figures of an event or one date. Scope: `tickets:manage`. Docs: https://www.app2email.com/docs/api/tickets-and-pay/get-ticket-stats

Scope: `tickets:manage`. The figures of one event, or of one of its dates with `date_id`: confirmed orders, people sold, held in baskets, left and checked in, the money (gross, discounts, fees, tax, donations, refunded, net) and the split by ticket type, by channel and by promo code. Money is in the event's currency. `event_id` is needed (400 `invalid_ticket_event` without it).


Parameters:

| Name | In | Type | Required | Meaning |
| --- | --- | --- | --- | --- |
| event_id | query | string |  | The event: its id, its slug or its code (EV-XXXXX). Needed. |
| date_id | query | integer |  | Only this date (its id). Left out: all dates of the event. |


Example answer:

```json
{
  "success": true,
  "request_id": "t4st5",
  "event_id": 12,
  "date_id": null,
  "currency": "AUD",
  "orders": 41,
  "sold": 86,
  "held": 2,
  "left": 32,
  "capacity": 120,
  "checked_in": 0,
  "money": {
    "gross": 1008.0,
    "discounts": 0,
    "fees": 0,
    "tax": 0,
    "donations": 0,
    "refunded": 12.0,
    "net": 996.0,
    "net_label": "A$996.00"
  },
  "by_type": [
    {
      "type_id": 44,
      "name": "Adult",
      "role": "ticket",
      "sold": 86,
      "checked_in": 0,
      "gross": 1008.0
    }
  ],
  "by_channel": [
    {
      "channel": "web",
      "orders": 40,
      "tickets": 84,
      "gross": 1008.0
    },
    {
      "channel": "api",
      "orders": 1,
      "tickets": 2,
      "gross": 0
    }
  ],
  "by_code": []
}
```


### `GET /settings/tickets`

The ticket settings and whether ticket sales are switched on. Scope: `tickets:manage`. Docs: https://www.app2email.com/docs/api/tickets-and-pay/get-ticket-settings

Scope: `tickets:manage`. Works for every number, also before ticket sales are set up. `available` says whether ticket sales are open for this number at all (false: every other ticket call answers 403 `tickets_not_enabled`), `configured` whether the number has ticket settings, `enabled` and `selling` whether tickets are sold now, and `why` not (tables_missing, no_config, removed, off, plan). Also the address of the events page, the currency and the time zone new events start with, which of the business's payment providers can take a ticket payment, and `config`: the settings with every default filled in. Nothing is changed by this call.


Example answer:

```json
{
  "success": true,
  "request_id": "t8sg1",
  "available": true,
  "configured": true,
  "enabled": true,
  "selling": true,
  "why": "",
  "events_url": "https://www.app2email.com/events/k3XbQ9rTzP2mWv7",
  "currency": "AUD",
  "timezone": "Australia/Sydney",
  "payments": {
    "stripe": true,
    "paypal": false
  },
  "config": {
    "organiser": {
      "name": "",
      "email": "",
      "phone": ""
    },
    "hold_minutes": 10,
    "notify": {
      "sale": "each",
      "email": ""
    },
    "brand": {
      "logo": 0,
      "color": "",
      "background": "",
      "hide_powered": false
    },
    "ticket_style": {
      "layout": "classic",
      "accent": "",
      "background": "#FFFFFF",
      "text": "#111111",
      "image": 0,
      "image_as": "cover",
      "logo": 0,
      "font": "inter",
      "fields": {
        "holder": true,
        "seat": true,
        "type": true,
        "reference": true,
        "venue": true,
        "doors": true,
        "price": false,
        "terms": false
      },
      "footer": ""
    },
    "wa": {
      "keywords": [
        "tickets",
        "ticket",
        "events"
      ],
      "intro_text": "Tap the button to see what's on and get your tickets.",
      "cta": "Get tickets",
      "mine_keywords": [
        "my tickets",
        "my ticket"
      ],
      "send_pdf": false,
      "texts": {
        "none_text": "There are no events on sale right now.",
        "pay_text": "Order {reference}\n{lines}\nTotal: {total}\n\nWe are holding your tickets for {time}. Tap Pay now to finish."
      }
    },
    "privacy": {
      "retention_days": 0,
      "url": ""
    },
    "texts": {
      "refund_none": "No refunds unless the event is cancelled or its date or venue changes.",
      "hold_ended": "Your tickets were released because the time ran out. Please choose again."
    }
  }
}
```


### `PUT /settings/tickets`

Switch ticket sales on or off and change the settings. Scope: `tickets:manage`. Docs: https://www.app2email.com/docs/api/tickets-and-pay/update-ticket-settings

Scope: `tickets:manage`. Not with a sandbox key. `enabled` switches ticket sales on or off; `config` holds whole sections of the settings (organiser, hold_minutes, notify, brand, ticket_style, wa, privacy, texts): a section sent replaces the stored section, the others stay. The first call makes the ticket settings of the number. Switching off never strands what was sold: the tickets, refunds and the door go on working. 403 `tickets_not_enabled` while ticket sales are not open for this number, 403 `plan_not_allowed`, 400 `invalid_setting` with `details.problems`, 400 `nothing_to_change` with neither key. The answer is the one of GET /settings/tickets plus `note`.


Request body:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| enabled | boolean |  | Switch ticket sales on or off. |
| config | object |  | Whole sections of the settings: organiser {name, email, phone}, hold_minutes (5 to 30), notify {sale, email}, brand {logo, color, background, hide_powered}, ticket_style {layout, accent, background, text, image, image_as, logo, font, fields, footer}, wa {keywords, intro_text, cta, mine_keywords, send_pdf, texts}, privacy {retention_days, url}, texts. A section sent replaces the stored section; the others stay. |


Example answer:

```json
{
  "success": true,
  "request_id": "t9sp2",
  "available": true,
  "configured": true,
  "enabled": true,
  "selling": true,
  "why": "",
  "events_url": "https://www.app2email.com/events/k3XbQ9rTzP2mWv7",
  "currency": "AUD",
  "timezone": "Australia/Sydney",
  "payments": {
    "stripe": true,
    "paypal": false
  },
  "config": {
    "organiser": {
      "name": "",
      "email": "",
      "phone": ""
    },
    "hold_minutes": 10,
    "notify": {
      "sale": "each",
      "email": ""
    },
    "brand": {
      "logo": 0,
      "color": "",
      "background": "",
      "hide_powered": false
    },
    "ticket_style": {
      "layout": "classic",
      "accent": "",
      "background": "#FFFFFF",
      "text": "#111111",
      "image": 0,
      "image_as": "cover",
      "logo": 0,
      "font": "inter",
      "fields": {
        "holder": true,
        "seat": true,
        "type": true,
        "reference": true,
        "venue": true,
        "doors": true,
        "price": false,
        "terms": false
      },
      "footer": ""
    },
    "wa": {
      "keywords": [
        "tickets",
        "ticket",
        "events"
      ],
      "intro_text": "Tap the button to see what's on and get your tickets.",
      "cta": "Get tickets",
      "mine_keywords": [
        "my tickets",
        "my ticket"
      ],
      "send_pdf": false,
      "texts": {
        "none_text": "There are no events on sale right now.",
        "pay_text": "Order {reference}\n{lines}\nTotal: {total}\n\nWe are holding your tickets for {time}. Tap Pay now to finish."
      }
    },
    "privacy": {
      "retention_days": 0,
      "url": ""
    },
    "texts": {
      "refund_none": "No refunds unless the event is cancelled or its date or venue changes.",
      "hold_ended": "Your tickets were released because the time ran out. Please choose again."
    }
  },
  "note": "Saved."
}
```
