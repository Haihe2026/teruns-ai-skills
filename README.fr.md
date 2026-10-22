# Teruns AI Skills · Listing Studio

[English](README.md) · [Deutsch](README.de.md) · **Français** · [日本語](README.ja.md) · [简体中文](README.zh-CN.md)

À partir d'une vraie photo de produit, créez des images de fiche conformes pour Amazon,
Shopify, TikTok Shop et Etsy — directement dans Claude Code, Codex, Cursor ou tout agent
qui lit `SKILL.md`. Sortie 2K ou 4K, texte dans la langue de votre boutique.

| Skill | Rôle | Coût |
| --- | --- | --- |
| [`listing-image-audit`](skills/listing-image-audit/SKILL.md) | Vérifie vos images : taille, format, fond blanc pur de l'image principale, remplissage, transparence, CMJN, types d'images manquants | **Gratuit**, hors ligne |
| [`amazon-main-image`](skills/amazon-main-image/SKILL.md) | Une image principale Amazon : blanc pur RVB 255, produit sur environ 85 % du cadre, sans texte ni accessoires | 1 image |
| [`listing-image-set`](skills/listing-image-set/SKILL.md) | Un jeu complet : principale, infographie, gros plan, mise en situation, dimensions, contenu du colis | 5–7 images |
| [`aplus-content`](skills/aplus-content/SKILL.md) | Images de modules A+ Amazon aux tailles exactes, avec titres et textes | 5–9 images |
| [`teruns-catalog`](skills/teruns-catalog/SKILL.md) | Aide à choisir le bon skill | Gratuit |

Crédits : **image 2K = 1 crédit, image 4K = 2 crédits.** Les rendus échoués ne sont pas facturés.
Offres : [teruns.com/#pricing](https://teruns.com/#pricing).

## Installation

Tout agent (skills CLI) :

```bash
npx skills add Haihe2026/teruns-ai-skills
npx skills add Haihe2026/teruns-ai-skills --skill listing-image-audit   # seulement l'audit gratuit
```

Claude Code :

```
/plugin marketplace add Haihe2026/teruns-ai-skills
/plugin install teruns-skill-systems@teruns
```

Codex :

```bash
codex plugin marketplace add Haihe2026/teruns-ai-skills
```

Ouvrez ensuite `/plugins` et activez **teruns-skill-systems**.

## Exemples

> Vérifie les images de ./photos selon les règles d'Amazon.

> Crée un jeu d'images de fiche Amazon.fr à partir de ./bottle.jpg, en 2K.

> Fais une image principale Amazon sur fond blanc à partir de cette photo.

## Fonctionnement

1. Le skill demande la photo, la boutique et les informations produit, puis les confirme avec vous.
2. Il affiche le plan d'images et le nombre de crédits. Rien n'est généré sans votre accord.
3. La première fois, il vous donne un lien teruns.com pour connecter votre compte.
4. Les images sont générées une par une, l'image principale d'abord ; le produit reste identique dans tout le jeu.
5. L'audit gratuit contrôle chaque image avant la livraison.

S'il manque des crédits, le skill affiche un lien de paiement teruns.com (Stripe ou PayPal).
Après paiement, dites « continuer » et il reprend là où il s'était arrêté.

## Confidentialité et sécurité

- Aucune clé d'API de modèle dans ce dépôt ni sur votre ordinateur. Les scripts n'utilisent
  que la bibliothèque standard Python et ne contactent que `teruns.com`.
- `listing-image-audit` ne fait aucun appel réseau.
- Lors d'un rendu, votre photo de référence est envoyée à teruns.com pour créer vos images.
- Votre jeton de connexion est stocké dans `~/.teruns/credentials.json` (lisible par vous
  seul) et peut être révoqué depuis votre compte teruns.com.
- Les données de paiement se saisissent uniquement sur les pages Stripe ou PayPal, jamais dans la conversation.

Voir [SECURITY.md](SECURITY.md).

## Images générées par IA

Les images générées sont marquées comme générées par IA dans leurs métadonnées. Certaines
places de marché et l'AI Act européen exigent de le signaler ; suivez les règles de votre
boutique. Chaque image doit montrer fidèlement votre vrai produit.

## Développeurs

Structure et tests locaux : [README en anglais](README.md#for-developers). Contrat d'API : [docs/api.md](docs/api.md).

## Licence

[MIT](LICENSE). Le rendu s'effectue sur le service Teruns et est facturé via [teruns.com](https://teruns.com).
