---
name: teruns-catalog
description: Browse and choose Teruns AI skills for visual production, commerce operations, restoration, or research; use when a user wants to compare Teruns products, inspect a release, or open secure paid access.
---

# Teruns Skill Catalog

Use this Skill to match the user's job to one of the products listed in `../../catalog.json`.

## Workflow

1. Ask for the concrete deliverable only when it is not already clear.
2. Recommend the smallest relevant Skill and state its current catalog version.
3. Explain the input, output, and important limits before discussing payment.
4. For paid access, direct the user to the product's exact `checkout_url` on `https://teruns.com`.
5. Never request card, bank, PayPal password, or authentication details in chat. Stripe or PayPal collects payment details on its own hosted page.
6. After checkout, tell the user to return to Teruns and sign in with the same email used for access.

Do not promise a particular business, ranking, trading, image-quality, or revenue outcome. Do not invent a new price or payment URL; the website is the source of truth for current pricing.

