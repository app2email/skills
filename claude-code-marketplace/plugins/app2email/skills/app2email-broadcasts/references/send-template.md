# POST /messages: the request body

Sends one approved template to one recipient, or to several when `to` lists several numbers (or `recipients` gives each number its own values). The parameters are checked against the template before sending; on a mismatch the error includes a complete, correct `example_request` for that template. Nothing is sent when the request itself is invalid. `dry_run` checks without sending; `background` answers 202 and sends after; `send_at` schedules it (202, status scheduled). `type` text, image, video, document or interactive sends a free-form message to one contact within 24 hours of the contact's last message (422 outside_24h_window otherwise). `segment` sends a template to a saved segment's contacts. A business-scoped user id works wherever a number does. Also `audio`, `sticker`, `location`, `contacts`, `reaction` and the newer interactive kinds; template carousels, limited-time offers, catalog, MPM, SPM, flow and OTP buttons. `callback_data` comes back in message.status. MARKETING templates follow `marketing_api` / messages.marketing_route (`sent_via` in the answer).

## Fields

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


### Template



| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| name | string | yes | Exact name of an APPROVED template. |
| language | object |  | Required when the template exists in more than one language. |
|   code | string | yes | Template language code, eg 'en', 'en_US', 'nl'. |
| components | array of object |  | Values for the template's placeholders and media. Leave out for templates without parameters. |

### Component



| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| type | string (header \| body \| button \| carousel \| limited_time_offer) | yes |  |
| sub_type | string (url \| quick_reply \| copy_code \| flow \| catalog \| mpm \| spm \| order_details) |  | Buttons only. |
| index | string |  | Buttons only: position of the button in the template, starting at 0. |
| parameters | array of object |  |  |
| cards | array of object |  | type 'carousel': one entry per card of the approved template, {card_index, components: [header, body, button...]}. |

### Parameter

One value. Set 'type' and the matching field, eg {"type":"text","text":"John"} or {"type":"image","image":{"link":"https://..."}}.

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| type | string (text \| image \| video \| document \| location \| currency \| date_time \| payload \| coupon_code \| action \| product \| limited_time_offer) | yes |  |
| parameter_name | string |  | For templates with NAMED placeholders, eg 'first_name' for {{first_name}}. |
| text | string |  | type 'text'. No new lines, tabs or more than 4 spaces in a row. |
| image | object |  | Give exactly one of: link, data or id. To send the template's own sample media instead, leave the header component out. |
|   link | string |  | Public http(s) URL. app2email downloads the file (no login, no private network addresses) and uploads it to WhatsApp. |
|   data | string |  | The file, base64 encoded. A 'data:<mime>;base64,' prefix is accepted. |
|   id | string |  | A media id already uploaded to WhatsApp for this number. |
|   filename | string |  | Shown to the recipient for documents. Also helps detect the file type. |
|   mime_type | string |  | Optional. The type is detected from the file where possible. |
| video | object |  | Give exactly one of: link, data or id. To send the template's own sample media instead, leave the header component out. |
| document | object |  | Give exactly one of: link, data or id. To send the template's own sample media instead, leave the header component out. |
| location | object |  |  |
|   latitude | string | yes |  |
|   longitude | string | yes |  |
|   name | string |  |  |
|   address | string |  |  |
| currency | object |  |  |
|   fallback_value | string |  |  |
|   code | string |  |  |
|   amount_1000 | integer |  |  |
| date_time | object |  |  |
|   fallback_value | string |  |  |
| payload | string |  | type 'payload': quick reply button payload. |
| coupon_code | string |  | type 'coupon_code': copy code button value. |
| action | object |  | type 'action': flow / catalog button data, as WhatsApp Cloud API. |
| product | object |  | type 'product': a product header. |
|   product_retailer_id | string |  |  |
|   catalog_id | string |  |  |
| limited_time_offer | object |  | type 'limited_time_offer': when the offer ends (ms since 1970). |
|   expiration_time_ms | integer |  |  |

### Media

Give exactly one of: link, data or id. To send the template's own sample media instead, leave the header component out.

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| link | string |  | Public http(s) URL. app2email downloads the file (no login, no private network addresses) and uploads it to WhatsApp. |
| data | string |  | The file, base64 encoded. A 'data:<mime>;base64,' prefix is accepted. |
| id | string |  | A media id already uploaded to WhatsApp for this number. |
| filename | string |  | Shown to the recipient for documents. Also helps detect the file type. |
| mime_type | string |  | Optional. The type is detected from the file where possible. |

### FreeFormText



| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| body | string | yes | The text. Up to 4096 characters. |
| preview_url | boolean |  | true: show a preview of a link in the text. |

### FreeFormMedia

Give exactly one of: link, data or id. 'filename' is shown to the recipient for documents.

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| link | string |  | Public http(s) URL. app2email downloads the file and uploads it to WhatsApp. |
| data | string |  | The file, base64 encoded. A 'data:<mime>;base64,' prefix is accepted. |
| id | string |  | A media id from POST /media (or uploaded to WhatsApp for this number). |
| filename | string |  | Needed with 'data' for documents. |
| mime_type | string |  | Optional. The type is detected from the file where possible. |
| caption | string |  | Optional text under the image, video or document. |

### Recipient



| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| to | string | yes | One number, with country code. |
| components | array of object |  | Only what differs for this number, eg its body values. The rest comes from template.components. |
| recipient_identity_key_hash | string |  | Optional: this contact's identity_key_hash (see the request's). |

## Examples (from the spec)


**Body with two text values**

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

**Image header from a link, plus a URL button value**

```json
{
  "to": "61412345678",
  "type": "template",
  "template": {
    "name": "new_arrivals",
    "language": {
      "code": "en"
    },
    "components": [
      {
        "type": "header",
        "parameters": [
          {
            "type": "image",
            "image": {
              "link": "https://example.com/photo.jpg"
            }
          }
        ]
      },
      {
        "type": "body",
        "parameters": [
          {
            "type": "text",
            "text": "John"
          }
        ]
      },
      {
        "type": "button",
        "sub_type": "url",
        "index": "0",
        "parameters": [
          {
            "type": "text",
            "text": "summer-sale"
          }
        ]
      }
    ]
  }
}
```

**PDF header sent as base64 in the request**

```json
{
  "to": "61412345678",
  "type": "template",
  "template": {
    "name": "invoice_ready",
    "language": {
      "code": "en"
    },
    "components": [
      {
        "type": "header",
        "parameters": [
          {
            "type": "document",
            "document": {
              "data": "JVBERi0xLjQKJ...",
              "filename": "invoice-1234.pdf"
            }
          }
        ]
      },
      {
        "type": "body",
        "parameters": [
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

**Template with named placeholders**

```json
{
  "to": "61412345678",
  "type": "template",
  "template": {
    "name": "welcome",
    "language": {
      "code": "en_US"
    },
    "components": [
      {
        "type": "body",
        "parameters": [
          {
            "type": "text",
            "parameter_name": "first_name",
            "text": "John"
          },
          {
            "type": "text",
            "parameter_name": "code",
            "text": "X7Q2"
          }
        ]
      }
    ]
  }
}
```

**Same message to several numbers**

```json
{
  "to": "61412345678,61498765432,61400111222",
  "type": "template",
  "campaign_name": "Order updates 21 Oct",
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

**Each number with its own values (recipients)**

```json
{
  "type": "template",
  "campaign_name": "Order updates",
  "template": {
    "name": "order_update",
    "language": {
      "code": "en"
    },
    "components": [
      {
        "type": "header",
        "parameters": [
          {
            "type": "image",
            "image": {
              "link": "https://example.com/photo.jpg"
            }
          }
        ]
      }
    ]
  },
  "recipients": [
    {
      "to": "61412345678",
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
    },
    {
      "to": "61498765432",
      "components": [
        {
          "type": "body",
          "parameters": [
            {
              "type": "text",
              "text": "Mary"
            },
            {
              "type": "text",
              "text": "#1235"
            }
          ]
        }
      ]
    }
  ]
}
```

**Check everything without sending**

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
  },
  "dry_run": true
}
```

**Big list: answer now, send after**

```json
{
  "to": "61412345678,61498765432,61400111222",
  "type": "template",
  "campaign_name": "October newsletter",
  "background": true,
  "template": {
    "name": "october_newsletter",
    "language": {
      "code": "en"
    }
  }
}
```

**Free-form text reply (within 24 hours)**

```json
{
  "to": "61412345678",
  "type": "text",
  "text": {
    "body": "Thanks, it arrives on Friday.",
    "preview_url": false
  }
}
```

**Free-form image from a link, with a caption**

```json
{
  "to": "61412345678",
  "type": "image",
  "image": {
    "link": "https://example.com/photo.jpg",
    "caption": "Your parcel"
  }
}
```

**Free-form PDF as base64, quoting a message**

```json
{
  "to": "61412345678",
  "type": "document",
  "reply_to": "wamid.HBgLNjE0MTIzNDU2NzgVAgARGBJTQU1QTEVfVEVTVF9FVkVOVAA=",
  "document": {
    "data": "JVBERi0xLjQKJ...",
    "filename": "invoice-1234.pdf",
    "caption": "Invoice #1234"
  }
}
```

**Several numbers, sent at a set time**

```json
{
  "to": "61412345678,61498765432,61400111222",
  "type": "template",
  "campaign_name": "Order updates 2 Nov",
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
  },
  "send_at": "2026-11-02T09:00:00+11:00"
}
```

**Reply buttons (within 24 hours)**

```json
{
  "to": "61412345678",
  "type": "interactive",
  "interactive": {
    "type": "button",
    "body": {
      "text": "Confirm your booking for Friday 10:00?"
    },
    "action": {
      "buttons": [
        {
          "type": "reply",
          "reply": {
            "id": "yes",
            "title": "Confirm"
          }
        },
        {
          "type": "reply",
          "reply": {
            "id": "no",
            "title": "Change"
          }
        }
      ]
    }
  }
}
```

**A list to pick from (within 24 hours)**

```json
{
  "to": "61412345678",
  "type": "interactive",
  "interactive": {
    "type": "list",
    "body": {
      "text": "Which time suits you?"
    },
    "action": {
      "button": "Pick a time",
      "sections": [
        {
          "title": "Friday",
          "rows": [
            {
              "id": "fri10",
              "title": "10:00"
            },
            {
              "id": "fri14",
              "title": "14:00",
              "description": "afternoon"
            }
          ]
        }
      ]
    }
  }
}
```

**A contact known by a business-scoped user id**

```json
{
  "recipient": "61.AbC123xyz",
  "type": "text",
  "text": {
    "body": "Thanks, it arrives on Friday."
  }
}
```

**A template to a saved segment, values from each contact**

```json
{
  "segment": "VIP, consented",
  "type": "template",
  "campaign_name": "November offer",
  "template": {
    "name": "november_offer",
    "language": {
      "code": "en"
    },
    "components": [
      {
        "type": "body",
        "parameters": [
          {
            "type": "text",
            "parameter_name": "first_name"
          }
        ]
      }
    ]
  }
}
```

**Text**

```json
{
  "to": "61412345678",
  "type": "text",
  "text": {
    "body": "Your order has shipped.",
    "preview_url": false
  }
}
```

**Image**

```json
{
  "to": "61412345678",
  "type": "image",
  "image": {
    "link": "https://example.com/photo.jpg",
    "caption": "Your parcel"
  }
}
```

**Video**

```json
{
  "to": "61412345678",
  "type": "video",
  "video": {
    "link": "https://example.com/howto.mp4",
    "caption": "How to set it up"
  }
}
```

**Document**

```json
{
  "to": "61412345678",
  "type": "document",
  "document": {
    "link": "https://example.com/invoice-1234.pdf",
    "filename": "invoice-1234.pdf",
    "caption": "Invoice"
  }
}
```

**Audio and voice message**

```json
{
  "to": "61412345678",
  "type": "audio",
  "audio": {
    "id": "1013859600285441",
    "voice": true
  }
}
```

**Sticker**

```json
{
  "to": "61412345678",
  "type": "sticker",
  "sticker": {
    "link": "https://example.com/stickers/thanks.webp"
  }
}
```

**Location**

```json
{
  "to": "61412345678",
  "type": "location",
  "location": {
    "latitude": -33.8568,
    "longitude": 151.2153,
    "name": "Sydney Opera House",
    "address": "Bennelong Point, Sydney NSW 2000"
  }
}
```

**Contact card**

```json
{
  "to": "61412345678",
  "type": "contacts",
  "contacts": [
    {
      "name": {
        "formatted_name": "Jane Citizen",
        "first_name": "Jane",
        "last_name": "Citizen"
      },
      "phones": [
        {
          "phone": "+61 412 345 678",
          "type": "CELL",
          "wa_id": "61412345678"
        }
      ],
      "emails": [
        {
          "email": "jane@example.com",
          "type": "WORK"
        }
      ],
      "org": {
        "company": "Example Pty Ltd"
      }
    }
  ]
}
```

**Reaction**

```json
{
  "to": "61412345678",
  "type": "reaction",
  "reaction": {
    "message_id": "wamid.HBgLNjE0MTIzNDU2NzgVAgASGBQzQUZCMTY0MDc2MUYwNzBDNTY5MAA=",
    "emoji": "👍"
  }
}
```

**Reply buttons**

```json
{
  "to": "61412345678",
  "type": "interactive",
  "interactive": {
    "type": "button",
    "body": {
      "text": "Confirm your booking for Friday 10:00?"
    },
    "action": {
      "buttons": [
        {
          "type": "reply",
          "reply": {
            "id": "yes",
            "title": "Confirm"
          }
        },
        {
          "type": "reply",
          "reply": {
            "id": "no",
            "title": "Change"
          }
        }
      ]
    }
  }
}
```

**List**

```json
{
  "to": "61412345678",
  "type": "interactive",
  "interactive": {
    "type": "list",
    "body": {
      "text": "Which time suits you?"
    },
    "action": {
      "button": "Times",
      "sections": [
        {
          "title": "Friday",
          "rows": [
            {
              "id": "fri10",
              "title": "10:00"
            },
            {
              "id": "fri11",
              "title": "11:00"
            }
          ]
        }
      ]
    }
  }
}
```

**URL button**

```json
{
  "to": "61412345678",
  "type": "interactive",
  "interactive": {
    "type": "cta_url",
    "body": {
      "text": "Your invoice is ready."
    },
    "action": {
      "name": "cta_url",
      "parameters": {
        "display_text": "Open invoice",
        "url": "https://example.com/invoice/1234"
      }
    }
  }
}
```

**Media carousel**

```json
{
  "to": "61412345678",
  "type": "interactive",
  "interactive": {
    "type": "carousel",
    "body": {
      "text": "Three of our latest arrivals, each under $25:"
    },
    "action": {
      "cards": [
        {
          "card_index": 0,
          "type": "cta_url",
          "header": {
            "type": "image",
            "image": {
              "link": "https://example.com/img/echeveria.jpg"
            }
          },
          "body": {
            "text": "*Blue Echeveria*"
          },
          "action": {
            "name": "cta_url",
            "parameters": {
              "display_text": "Buy now",
              "url": "https://shop.example.com/echeveria"
            }
          }
        },
        {
          "card_index": 1,
          "type": "cta_url",
          "header": {
            "type": "image",
            "image": {
              "link": "https://example.com/img/haworthia.jpg"
            }
          },
          "body": {
            "text": "*Zebra Haworthia*"
          },
          "action": {
            "name": "cta_url",
            "parameters": {
              "display_text": "Buy now",
              "url": "https://shop.example.com/haworthia"
            }
          }
        }
      ]
    }
  }
}
```

**Product carousel**

```json
{
  "to": "61412345678",
  "type": "interactive",
  "interactive": {
    "type": "carousel",
    "body": {
      "text": "Picked for you this week:"
    },
    "action": {
      "cards": [
        {
          "card_index": 0,
          "type": "product",
          "action": {
            "product_retailer_id": "SKU-1234",
            "catalog_id": "194836987003835"
          }
        },
        {
          "card_index": 1,
          "type": "product",
          "action": {
            "product_retailer_id": "SKU-5678",
            "catalog_id": "194836987003835"
          }
        }
      ]
    }
  }
}
```

**Location request**

```json
{
  "to": "61412345678",
  "type": "interactive",
  "interactive": {
    "type": "location_request_message",
    "body": {
      "text": "Where should we pick you up? Tap to share your location."
    },
    "action": {
      "name": "send_location"
    }
  }
}
```

**Contact info request**

```json
{
  "to": "61412345678",
  "type": "interactive",
  "interactive": {
    "type": "request_contact_info",
    "body": {
      "text": "Please share your phone number so we can call you back."
    },
    "action": {
      "name": "request_contact_info"
    }
  }
}
```

**Flow**

```json
{
  "to": "61412345678",
  "type": "interactive",
  "interactive": {
    "type": "flow",
    "header": {
      "type": "text",
      "text": "Book a table"
    },
    "body": {
      "text": "Pick a day and time."
    },
    "action": {
      "name": "flow",
      "parameters": {
        "flow_message_version": "3",
        "flow_id": "1234567890123456",
        "flow_cta": "Book now",
        "flow_token": "booking-5521",
        "flow_action": "navigate",
        "flow_action_payload": {
          "screen": "WELCOME"
        }
      }
    }
  }
}
```

**Single product**

```json
{
  "to": "61412345678",
  "type": "interactive",
  "interactive": {
    "type": "product",
    "body": {
      "text": "The one you asked about:"
    },
    "action": {
      "catalog_id": "194836987003835",
      "product_retailer_id": "SKU-1234"
    }
  }
}
```

**Product list**

```json
{
  "to": "61412345678",
  "type": "interactive",
  "interactive": {
    "type": "product_list",
    "header": {
      "type": "text",
      "text": "Our picks"
    },
    "body": {
      "text": "Popular this week."
    },
    "action": {
      "catalog_id": "194836987003835",
      "sections": [
        {
          "title": "Succulents",
          "product_items": [
            {
              "product_retailer_id": "SKU-1234"
            },
            {
              "product_retailer_id": "SKU-5678"
            }
          ]
        }
      ]
    }
  }
}
```

**Catalog**

```json
{
  "to": "61412345678",
  "type": "interactive",
  "interactive": {
    "type": "catalog_message",
    "body": {
      "text": "Browse our catalog."
    },
    "action": {
      "name": "catalog_message",
      "parameters": {
        "thumbnail_product_retailer_id": "SKU-1234"
      }
    }
  }
}
```

**Call permission request**

```json
{
  "to": "61412345678",
  "type": "interactive",
  "interactive": {
    "type": "call_permission_request",
    "body": {
      "text": "May we call you on WhatsApp about your order?"
    },
    "action": {
      "name": "call_permission_request"
    }
  }
}
```

**Call button**

```json
{
  "to": "61412345678",
  "type": "interactive",
  "interactive": {
    "type": "voice_call",
    "body": {
      "text": "Questions? Call us on WhatsApp."
    },
    "action": {
      "name": "voice_call",
      "parameters": {
        "display_text": "Call us",
        "ttl_minutes": 60
      }
    }
  }
}
```

**Address request**

```json
{
  "to": "919876543210",
  "type": "interactive",
  "interactive": {
    "type": "address_message",
    "body": {
      "text": "Where should we deliver?"
    },
    "action": {
      "name": "address_message",
      "parameters": {
        "country": "IN"
      }
    }
  }
}
```

**Order details**

```json
{
  "to": "919876543210",
  "type": "interactive",
  "interactive": {
    "type": "order_details",
    "body": {
      "text": "Your order is ready to pay."
    },
    "action": {
      "name": "review_and_pay",
      "parameters": {
        "reference_id": "ORDER-1234",
        "type": "digital-goods",
        "payment_type": "upi",
        "payment_configuration": "my-config",
        "currency": "INR",
        "total_amount": {
          "value": 21000,
          "offset": 100
        },
        "order": {
          "status": "pending",
          "subtotal": {
            "value": 21000,
            "offset": 100
          },
          "items": [
            {
              "retailer_id": "SKU-1234",
              "name": "Gift card",
              "amount": {
                "value": 21000,
                "offset": 100
              },
              "quantity": 1
            }
          ]
        }
      }
    }
  }
}
```

**Order status**

```json
{
  "to": "919876543210",
  "type": "interactive",
  "interactive": {
    "type": "order_status",
    "body": {
      "text": "Your order has shipped."
    },
    "action": {
      "name": "review_order",
      "parameters": {
        "reference_id": "ORDER-1234",
        "order": {
          "status": "shipped",
          "description": "Arrives Friday"
        }
      }
    }
  }
}
```

**Template**

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
            "text": "Jane"
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

**Template, named parameters**

```json
{
  "to": "61412345678",
  "type": "template",
  "template": {
    "name": "order_update_named",
    "language": {
      "code": "en"
    },
    "components": [
      {
        "type": "body",
        "parameters": [
          {
            "type": "text",
            "parameter_name": "first_name",
            "text": "Jane"
          },
          {
            "type": "text",
            "parameter_name": "order_id",
            "text": "#1234"
          }
        ]
      }
    ]
  }
}
```

**Template, location header**

```json
{
  "to": "61412345678",
  "type": "template",
  "template": {
    "name": "pickup_ready",
    "language": {
      "code": "en"
    },
    "components": [
      {
        "type": "header",
        "parameters": [
          {
            "type": "location",
            "location": {
              "latitude": "-33.8568",
              "longitude": "151.2153",
              "name": "Our shop",
              "address": "1 George St, Sydney"
            }
          }
        ]
      },
      {
        "type": "body",
        "parameters": [
          {
            "type": "text",
            "text": "Jane"
          }
        ]
      }
    ]
  }
}
```

**Carousel template**

```json
{
  "to": "61412345678",
  "type": "template",
  "template": {
    "name": "summer_succulents",
    "language": {
      "code": "en"
    },
    "components": [
      {
        "type": "body",
        "parameters": [
          {
            "type": "text",
            "text": "Jane"
          }
        ]
      },
      {
        "type": "carousel",
        "cards": [
          {
            "card_index": 0,
            "components": [
              {
                "type": "header",
                "parameters": [
                  {
                    "type": "image",
                    "image": {
                      "link": "https://example.com/img/card0.jpg"
                    }
                  }
                ]
              },
              {
                "type": "button",
                "sub_type": "quick_reply",
                "index": "0",
                "parameters": [
                  {
                    "type": "payload",
                    "payload": "more-0"
                  }
                ]
              },
              {
                "type": "button",
                "sub_type": "url",
                "index": "1",
                "parameters": [
                  {
                    "type": "text",
                    "text": "card-0"
                  }
                ]
              }
            ]
          },
          {
            "card_index": 1,
            "components": [
              {
                "type": "header",
                "parameters": [
                  {
                    "type": "image",
                    "image": {
                      "link": "https://example.com/img/card1.jpg"
                    }
                  }
                ]
              },
              {
                "type": "button",
                "sub_type": "quick_reply",
                "index": "0",
                "parameters": [
                  {
                    "type": "payload",
                    "payload": "more-1"
                  }
                ]
              },
              {
                "type": "button",
                "sub_type": "url",
                "index": "1",
                "parameters": [
                  {
                    "type": "text",
                    "text": "card-1"
                  }
                ]
              }
            ]
          }
        ]
      }
    ]
  }
}
```

**Product card carousel template**

```json
{
  "to": "61412345678",
  "type": "template",
  "template": {
    "name": "product_picks",
    "language": {
      "code": "en"
    },
    "components": [
      {
        "type": "carousel",
        "cards": [
          {
            "card_index": 0,
            "components": [
              {
                "type": "header",
                "parameters": [
                  {
                    "type": "product",
                    "product": {
                      "product_retailer_id": "SKU-1234",
                      "catalog_id": "194836987003835"
                    }
                  }
                ]
              }
            ]
          },
          {
            "card_index": 1,
            "components": [
              {
                "type": "header",
                "parameters": [
                  {
                    "type": "product",
                    "product": {
                      "product_retailer_id": "SKU-5678",
                      "catalog_id": "194836987003835"
                    }
                  }
                ]
              }
            ]
          }
        ]
      }
    ]
  }
}
```

**Limited-time offer template**

```json
{
  "to": "61412345678",
  "type": "template",
  "template": {
    "name": "flash_sale",
    "language": {
      "code": "en"
    },
    "components": [
      {
        "type": "header",
        "parameters": [
          {
            "type": "image",
            "image": {
              "link": "https://example.com/img/sale.jpg"
            }
          }
        ]
      },
      {
        "type": "limited_time_offer",
        "parameters": [
          {
            "type": "limited_time_offer",
            "limited_time_offer": {
              "expiration_time_ms": 1767225600000
            }
          }
        ]
      },
      {
        "type": "button",
        "sub_type": "copy_code",
        "index": "0",
        "parameters": [
          {
            "type": "coupon_code",
            "coupon_code": "SAVE20"
          }
        ]
      },
      {
        "type": "button",
        "sub_type": "url",
        "index": "1",
        "parameters": [
          {
            "type": "text",
            "text": "summer"
          }
        ]
      }
    ]
  }
}
```

**Coupon code template**

```json
{
  "to": "61412345678",
  "type": "template",
  "template": {
    "name": "welcome_coupon",
    "language": {
      "code": "en"
    },
    "components": [
      {
        "type": "button",
        "sub_type": "copy_code",
        "index": "0",
        "parameters": [
          {
            "type": "coupon_code",
            "coupon_code": "WELCOME10"
          }
        ]
      }
    ]
  }
}
```

**Catalog template**

```json
{
  "to": "61412345678",
  "type": "template",
  "template": {
    "name": "browse_catalog",
    "language": {
      "code": "en"
    },
    "components": [
      {
        "type": "button",
        "sub_type": "catalog",
        "index": "0",
        "parameters": [
          {
            "type": "action",
            "action": {
              "thumbnail_product_retailer_id": "SKU-1234"
            }
          }
        ]
      }
    ]
  }
}
```

**Multi-product template**

```json
{
  "to": "61412345678",
  "type": "template",
  "template": {
    "name": "new_arrivals",
    "language": {
      "code": "en"
    },
    "components": [
      {
        "type": "header",
        "parameters": [
          {
            "type": "text",
            "text": "Succulents"
          }
        ]
      },
      {
        "type": "button",
        "sub_type": "mpm",
        "index": "0",
        "parameters": [
          {
            "type": "action",
            "action": {
              "thumbnail_product_retailer_id": "SKU-1234",
              "sections": [
                {
                  "title": "Popular",
                  "product_items": [
                    {
                      "product_retailer_id": "SKU-1234"
                    },
                    {
                      "product_retailer_id": "SKU-5678"
                    }
                  ]
                }
              ]
            }
          }
        ]
      }
    ]
  }
}
```

**Single-product template**

```json
{
  "to": "61412345678",
  "type": "template",
  "template": {
    "name": "product_of_the_week",
    "language": {
      "code": "en"
    },
    "components": [
      {
        "type": "header",
        "parameters": [
          {
            "type": "product",
            "product": {
              "product_retailer_id": "SKU-1234",
              "catalog_id": "194836987003835"
            }
          }
        ]
      }
    ]
  }
}
```

**Flow button template**

```json
{
  "to": "61412345678",
  "type": "template",
  "template": {
    "name": "book_a_table",
    "language": {
      "code": "en"
    },
    "components": [
      {
        "type": "button",
        "sub_type": "flow",
        "index": "0",
        "parameters": [
          {
            "type": "action",
            "action": {
              "flow_token": "booking-5521",
              "flow_action_data": {
                "party_size": 2
              }
            }
          }
        ]
      }
    ]
  }
}
```

**One-time password template**

```json
{
  "to": "61412345678",
  "type": "template",
  "template": {
    "name": "login_code",
    "language": {
      "code": "en"
    },
    "components": [
      {
        "type": "body",
        "parameters": [
          {
            "type": "text",
            "text": "482913"
          }
        ]
      },
      {
        "type": "button",
        "sub_type": "url",
        "index": "0",
        "parameters": [
          {
            "type": "text",
            "text": "482913"
          }
        ]
      }
    ]
  }
}
```

**Marketing template via the Marketing Messages API**

```json
{
  "to": "61412345678",
  "type": "template",
  "template": {
    "name": "november_offer",
    "language": {
      "code": "en"
    },
    "components": [
      {
        "type": "body",
        "parameters": [
          {
            "type": "text",
            "text": "Jane"
          }
        ]
      }
    ]
  },
  "marketing_api": "mm_api",
  "product_policy": "CLOUD_API_FALLBACK",
  "message_activity_sharing": true,
  "callback_data": "campaign-nov"
}
```

**Mark as read and typing**

```json
{
  "messaging_product": "whatsapp",
  "status": "read",
  "message_id": "wamid.HBgLNjE0MTIzNDU2NzgVAgASGBQzQUZCMTY0MDc2MUYwNzBDNTY5MAA=",
  "typing_indicator": {
    "type": "text"
  }
}
```

**Meta's own body, unchanged**

```json
{
  "messaging_product": "whatsapp",
  "recipient_type": "individual",
  "to": "+61412345678",
  "type": "text",
  "text": {
    "preview_url": false,
    "body": "Your order has shipped."
  },
  "biz_opaque_callback_data": "order-1234"
}
```

**callback_data, back in message.status**

```json
{
  "to": "61412345678",
  "type": "text",
  "text": {
    "body": "Your table is booked for 7 pm."
  },
  "callback_data": "booking-5521"
}
```

**Remove a reaction**

```json
{
  "to": "61412345678",
  "type": "reaction",
  "reaction": {
    "message_id": "wamid.HBgLNjE0MTIzNDU2NzgVAgASGBQzQUZCMTY0MDc2MUYwNzBDNTY5MAA=",
    "emoji": ""
  }
}
```

**Audio file from a link**

```json
{
  "to": "61412345678",
  "type": "audio",
  "audio": {
    "link": "https://example.com/audio/welcome.mp3"
  }
}
```

**Carousel with quick-reply buttons**

```json
{
  "to": "61412345678",
  "type": "interactive",
  "interactive": {
    "type": "carousel",
    "body": {
      "text": "Which one do you like?"
    },
    "action": {
      "cards": [
        {
          "card_index": 0,
          "header": {
            "type": "image",
            "image": {
              "link": "https://example.com/img/plant0.jpg"
            }
          },
          "action": {
            "buttons": [
              {
                "type": "quick_reply",
                "quick_reply": {
                  "id": "more-0",
                  "title": "More like this"
                }
              }
            ]
          }
        },
        {
          "card_index": 1,
          "header": {
            "type": "image",
            "image": {
              "link": "https://example.com/img/plant1.jpg"
            }
          },
          "action": {
            "buttons": [
              {
                "type": "quick_reply",
                "quick_reply": {
                  "id": "more-1",
                  "title": "More like this"
                }
              }
            ]
          }
        }
      ]
    }
  }
}
```
