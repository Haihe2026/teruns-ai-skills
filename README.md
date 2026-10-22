# Teruns AI Skills

Public GitHub catalog for installable, versioned AI Skills by [Teruns](https://teruns.com).

This repository contains the public plugin manifest and catalog Skill used to discover Teruns products. Paid products route to the official Teruns checkout, where Stripe and PayPal process payment securely.

## Install

The portable plugin starts at [`plugin.json`](./plugin.json). The catalog Skill is available at [`skills/teruns-catalog/SKILL.md`](./skills/teruns-catalog/SKILL.md).

```text
teruns-ai-skills/
├── plugin.json
├── catalog.json
└── skills/
    └── teruns-catalog/
        └── SKILL.md
```

## How paid access works

1. Browse the public catalog in this repository.
2. Choose a product.
3. Open the product's exact `checkout_url` on `https://teruns.com`.
4. Complete payment on the hosted Stripe or PayPal page.
5. Return to Teruns using the same email to access the paid product.

Payment credentials are never collected by this repository or by the Skill conversation.

## Links

- Storefront: https://teruns.com
- Pricing: https://teruns.com/#pricing
- Privacy: https://teruns.com/privacy
- Existing tools: https://teruns.com/radar

## License

The public catalog and manifest are released under the [MIT License](./LICENSE). Paid Skill implementations and Teruns service content are not included in this repository.

