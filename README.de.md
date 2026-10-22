# Teruns AI Skills · Listing Studio

[English](README.md) · **Deutsch** · [Français](README.fr.md) · [日本語](README.ja.md) · [简体中文](README.zh-CN.md)

Aus einem echten Produktfoto werden regelkonforme Listing-Bilder für Amazon, Shopify,
TikTok Shop und Etsy — direkt in Claude Code, Codex, Cursor oder jedem Agenten, der
`SKILL.md` liest. Ausgabe in 2K oder 4K, Texte im Bild in der Sprache Ihres Shops.

| Skill | Funktion | Kosten |
| --- | --- | --- |
| [`listing-image-audit`](skills/listing-image-audit/SKILL.md) | Prüft vorhandene Bilder: Größe, Format, rein weißer Hintergrund des Hauptbilds, Bildfüllung, Transparenz, CMYK, fehlende Bildtypen | **Kostenlos**, offline |
| [`amazon-main-image`](skills/amazon-main-image/SKILL.md) | Ein Amazon-Hauptbild: rein weiß RGB 255, Produkt füllt ca. 85 % des Bildes, kein Text, keine Requisiten | 1 Bild |
| [`listing-image-set`](skills/listing-image-set/SKILL.md) | Komplettes Set: Hauptbild, Infografik, Detail, Lifestyle, Maße, Lieferumfang | 5–7 Bilder |
| [`aplus-content`](skills/aplus-content/SKILL.md) | Amazon-A+-Modulbilder in exakten Größen, dazu Überschriften und Texte | 5–9 Bilder |
| [`teruns-catalog`](skills/teruns-catalog/SKILL.md) | Hilft bei der Wahl des passenden Skills | Kostenlos |

Credits: **2K-Bild = 1 Credit, 4K-Bild = 2 Credits.** Fehlgeschlagene Bilder werden nicht berechnet.
**Ihr erstes 2K-Bild ist kostenlos** — jedes neue teruns.com-Konto erhält eines.
Tarife: [teruns.com/#pricing](https://teruns.com/#pricing).

## Installation

Jeder Agent (skills CLI):

```bash
npx skills add Haihe2026/teruns-ai-skills
npx skills add Haihe2026/teruns-ai-skills --skill listing-image-audit   # nur die kostenlose Prüfung
```

Claude Code:

```
/plugin marketplace add Haihe2026/teruns-ai-skills
/plugin install teruns-skill-systems@teruns
```

Codex:

```bash
codex plugin marketplace add Haihe2026/teruns-ai-skills
```

Dann `/plugins` öffnen und **teruns-skill-systems** aktivieren.

## Beispiele

> Prüfe die Bilder in ./photos nach den Amazon-Regeln.

> Erstelle aus ./bottle.jpg ein Listing-Bilderset für Amazon.de in 2K.

> Mach aus diesem Foto ein Amazon-Hauptbild mit weißem Hintergrund.

## Ablauf

1. Der Skill fragt nach Produktfoto, Shop und Produktdaten und bestätigt sie mit Ihnen.
2. Er zeigt den Bildplan und die Credits. Gerendert wird erst nach Ihrer Zustimmung.
3. Beim ersten Mal erhalten Sie einen teruns.com-Link, um Ihr Konto zu verbinden.
4. Die Bilder entstehen einzeln, das Hauptbild zuerst; das Produkt bleibt im ganzen Set identisch.
5. Die kostenlose Prüfung kontrolliert jedes Bild vor der Übergabe.

Reichen die Credits nicht, zeigt der Skill einen Bezahllink auf teruns.com (Stripe oder PayPal).
Nach der Zahlung sagen Sie „weiter“, und es geht dort weiter, wo es aufgehört hat.

## Datenschutz und Sicherheit

- Keine Modell-API-Schlüssel im Repository oder auf Ihrem Rechner. Die Skripte nutzen nur
  die Python-Standardbibliothek und sprechen nur mit `teruns.com`.
- `listing-image-audit` stellt keinerlei Netzwerkverbindung her.
- Beim Rendern wird Ihr Referenzfoto an teruns.com gesendet, um Ihre Bilder zu erstellen.
- Ihr Login-Token liegt in `~/.teruns/credentials.json` (nur für Sie lesbar) und kann im
  teruns.com-Konto widerrufen werden.
- Zahlungsdaten geben Sie nur auf Seiten von Stripe oder PayPal ein, nie im Chat.

Siehe [SECURITY.md](SECURITY.md).

## KI-generierte Bilder

Gerenderte Bilder sind in ihren Metadaten als KI-generiert gekennzeichnet. Einige Marktplätze
und der EU AI Act verlangen eine Kennzeichnung; beachten Sie die Regeln Ihres Shops. Jedes
Bild muss Ihr echtes Produkt wahrheitsgetreu zeigen.

## Für Entwickler

Struktur und lokale Tests: [englische README](README.md#for-developers). API-Vertrag: [docs/api.md](docs/api.md).

## Lizenz

[MIT](LICENSE). Das Rendern läuft über den Teruns-Dienst und wird über [teruns.com](https://teruns.com) abgerechnet.
