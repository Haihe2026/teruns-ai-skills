# Teruns Skills API (v1)

The contract between the public skills in this repository and the teruns.com backend.
The skills hold no model API keys: they only call these endpoints through
`scripts/teruns_client.py`. Everything that costs money happens on teruns.com.

- Base URL: `https://teruns.com/api/v1` (override with `TERUNS_API_BASE` for testing)
- Format: JSON in and out, UTF-8
- Auth: `Authorization: Bearer <access_token>` on every endpoint except `/device/*`
- Client header: `X-Teruns-Client: skills/<version>`

## 1. Link a computer to an account (device flow)

The agent cannot open a browser or see cookies, so login works like a TV sign-in:
the skill shows a link, the user approves it on teruns.com, the skill receives a token.

### `POST /device/start`

```json
{ "client": "teruns-skills", "client_version": "0.2.0", "skill": "listing-image-set" }
```

`200`:

```json
{
  "device_code": "opaque-secret-for-polling",
  "user_code": "TRNS-4821",
  "verify_url": "https://teruns.com/link?code=TRNS-4821",
  "interval": 3,
  "expires_in": 600
}
```

`verify_url` opens a page where the user signs in (or signs up), sees the `user_code`,
and clicks Approve. The free trial (section 4) is granted the first time an account is
approved.
Record `skill` so conversions can be attributed per skill.

### `POST /device/token`

```json
{ "device_code": "opaque-secret-for-polling" }
```

| Status | Body | Meaning |
| --- | --- | --- |
| `428` | `{"error":"authorization_pending"}` | User has not approved yet; poll again after `interval` |
| `200` | `{"access_token":"...","account":"j***@gmail.com","credits":0,"trial_images":1}` | Approved |
| `410` | `{"error":"expired_token"}` | Code expired; start again |
| `400` | `{"error":"access_denied"}` | User rejected |

The access token is long-lived (suggested 180 days), revocable from the account page,
and stored by the client at `~/.teruns/credentials.json` with mode 600.

## 2. Balance

### `GET /balance`

```json
{ "credits": 92, "trial_images": 0, "plan": "starter", "renews_at": "2026-11-22", "pricing_url": "https://teruns.com/#pricing" }
```

`trial_images`: free 2K renders left (0 or 1, see section 4).


## 3. Generate one image

### `POST /images/generate`

Headers: `Idempotency-Key: <uuid>`. The same key within 24 hours must return the
first successful result and must not charge again. Store only successful results under
the key: after a `402`, `429` or `5xx` the client retries with the same key and the
server must process it as new. The client reuses the key on retries.

Output files: embed an "AI-generated" marker in each delivered image (XMP
`DigitalSourceType = trainedAlgorithmicMedia`, or C2PA) so sellers can meet EU AI Act
and marketplace disclosure rules.

```json
{
  "skill": "listing-image-set",
  "slot": "amazon_main",
  "marketplace": "amazon.de",
  "locale": "de-DE",
  "size": "2K",
  "aspect": "1:1",
  "output_size": [2000, 2000],
  "prompt": "Full prompt written by the skill ...",
  "product": {
    "name": "Insulated bottle 750 ml",
    "brand": "NORTHLOOP",
    "color": "matte sage green",
    "material": "stainless steel",
    "dimensions": "7.5 x 7.5 x 26 cm",
    "included": ["bottle", "cap"],
    "selling_points": ["keeps cold 24 h", "leak-proof cap"],
    "visible_text_on_product": ["NORTHLOOP", "750 ml"]
  },
  "reference_images": [{ "filename": "bottle.jpg", "data": "<base64>" }],
  "client_version": "0.2.0"
}
```

Field notes:

- `size`: `2K` or `4K`. Credits: 2K = 1, 4K = 2.
- `aspect`: `1:1`, `4:3`, `3:4`, `16:9`, `9:16`, `97:60` (A+ header) and so on.
  The server picks the nearest native model size.
- `output_size`: optional exact final pixels. When present the server crops or pads
  (padding colour pure white `#FFFFFF` for `amazon_main`) and returns exactly that size.
- `prompt`: the skill always sends a complete prompt. The server may use it as is,
  or wrap it with its own slot templates and platform rules (recommended over time —
  that is where Teruns' know-how stays private).
- `locale`: language for any text drawn in the image. Text in the image must be in
  this language only.
- `reference_images`: up to 4, each up to 15 MB (JPEG, PNG, WebP).

`200`:

```json
{
  "images": [{ "url": "https://cdn.teruns.com/out/abc.png", "width": 2000, "height": 2000 }],
  "credits_charged": 1,
  "credits_left": 91,
  "trial_used": false,
  "trial_images_left": 0,
  "request_id": "same-as-idempotency-key"
}
```

`images[].url` must be downloadable without auth for at least 1 hour.
`b64` may be returned instead of `url`.

Errors:

| Status | Body |
| --- | --- |
| `401` | `{"error":"invalid_token"}` |
| `402` | `{"error":"insufficient_credits","credits_needed":1,"credits_left":0,"checkout_url":"https://teruns.com/checkout?ref=listing-image-set&need=1"}` |
| `402` | `{"error":"trial_2k_only","credits_needed":2,"credits_left":0,"trial_images_left":1,"checkout_url":"..."}` — a 4K request when only the free 2K trial is left |
| `413` | `{"error":"reference_too_large"}` |
| `422` | `{"error":"policy_violation","detail":"..."}` — no charge |
| `409` | `{"error":"request_in_progress"}` — same Idempotency-Key still rendering; retry later, no charge |
| `429` | `{"error":"rate_limited","retry_after":20}` |
| `5xx` | no charge; client may retry with the same Idempotency-Key |

`checkout_url` points to the one shared checkout for all image skills and carries the
source skill: `https://teruns.com/checkout?ref=<skill>&need=<credits_needed>`. Credits are
one balance per account, usable by every Teruns image skill.
After payment the site binds the purchase to the account and grants credits; the user
returns to the agent and says "continue", and the skill retries the same request.

## 4. Free trial and charging rules

Free trial: every account gets **one free 2K image**.

- Granted once per account, the first time a device is approved for it. Require a
  verified email before granting; also recommended: at most one trial per device and a
  daily cap per IP, to stop throwaway accounts.
- Used automatically by the first `2K` request (any slot), before paid credits.
  The response then has `credits_charged: 0`, `trial_used: true`.
- Not usable for `4K`. A `4K` request with no paid credits returns `402 trial_2k_only`.
- Does not expire. Not refunded once an image is delivered.

Charging rules:

- Charge only after an image is delivered. Failed or refused generations are free.
- One request = one image. A 7-image set is 7 requests, so a failure in the middle
  costs only what was delivered.
- The free `listing-image-audit` skill makes no API calls at all.

## 5. Model

Rendering uses `gpt-image-2.5-sunburst` server-side. The model name is not part of
this contract, so the backend can change models without a skill release.
