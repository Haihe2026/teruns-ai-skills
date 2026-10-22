---
name: teruns-catalog
description: Explain and choose between Teruns AI skills — currently Listing Studio for ecommerce listing images (listing-image-set, amazon-main-image, aplus-content, and the free listing-image-audit). Use when a user asks what Teruns offers, which Teruns skill fits a task, how Teruns credits or pricing work, or how to buy access.
---

# Teruns Skill Catalog

Match the user's job to a skill listed in `../../catalog.json` (in this repository) and
explain how access works. Reply in the language the user writes in.

## What to recommend

| The user wants to… | Skill | Cost |
| --- | --- | --- |
| check existing listing photos, find why a main image was rejected | `listing-image-audit` | free, offline |
| one compliant Amazon main image | `amazon-main-image` | 1 image |
| a whole listing image set (Amazon, Shopify, TikTok Shop, Etsy) | `listing-image-set` | 5–7 images |
| Amazon A+ Content images and copy | `aplus-content` | about 5–9 images |

Credits: a 2K image costs 1 credit, a 4K image 2 credits. Failed renders are not charged.
Every new account gets one free 2K image — enough to try `amazon-main-image` at no cost.

## Workflow

1. Ask for the concrete deliverable only when it is not already clear.
2. Recommend the smallest skill that does the job, with its version from `catalog.json`.
   If the user only needs a check, start with the free `listing-image-audit`.
3. Explain inputs, output and limits before discussing payment.
4. Plans and current prices are on https://teruns.com/#pricing — the website is the
   source of truth. Do not quote prices from memory or invent payment links; use the
   product's `checkout_url` from `catalog.json`.
5. Never ask for card, bank, PayPal or password details in chat. Stripe or PayPal
   collect payment on their own pages. After payment, credits appear on the same
   teruns.com account the skill is linked to.

Do not promise a sales, ranking or revenue outcome.
