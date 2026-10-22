# Teruns AI Skills · Listing Studio

[English](README.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · **日本語** · [简体中文](README.zh-CN.md)

実際の商品写真 1 枚から、Amazon・Shopify・TikTok Shop・Etsy の規約に沿った商品画像を作成します。
Claude Code、Codex、Cursor など `SKILL.md` を読めるエージェントの中でそのまま使えます。
2K / 4K 出力、画像内の文字はストアの言語で入ります。

| Skill | 内容 | 費用 |
| --- | --- | --- |
| [`listing-image-audit`](skills/listing-image-audit/SKILL.md) | 既存画像をチェック：サイズ、形式、メイン画像の純白背景、商品の占有率、透過、CMYK、不足している画像の種類 | **無料**・オフライン |
| [`amazon-main-image`](skills/amazon-main-image/SKILL.md) | Amazon メイン画像 1 枚：純白 RGB 255、商品が画面の約 85%、文字・小物なし | 1 枚 |
| [`listing-image-set`](skills/listing-image-set/SKILL.md) | 一式：メイン、インフォグラフィック、クローズアップ、使用シーン、サイズ、同梱物 | 5〜7 枚 |
| [`aplus-content`](skills/aplus-content/SKILL.md) | Amazon A+ モジュール画像（正確なサイズ）と見出し・本文 | 5〜9 枚 |
| [`teruns-catalog`](skills/teruns-catalog/SKILL.md) | 最適な skill 選びを手伝います | 無料 |

クレジット：**2K 画像 = 1、4K 画像 = 2。** 生成に失敗した場合は消費されません。
**最初の 2K 画像 1 枚は無料**です（teruns.com の新規アカウントごとに 1 回）。
プラン：[teruns.com/#pricing](https://teruns.com/#pricing)。

## インストール

すべてのエージェント（skills CLI）：

```bash
npx skills add Haihe2026/teruns-ai-skills
npx skills add Haihe2026/teruns-ai-skills --skill listing-image-audit   # 無料チェックのみ
```

Claude Code：

```
/plugin marketplace add Haihe2026/teruns-ai-skills
/plugin install teruns-skill-systems@teruns
```

Codex：

```bash
codex plugin marketplace add Haihe2026/teruns-ai-skills
```

その後 `/plugins` を開き、**teruns-skill-systems** を有効にします。

## 使い方の例

> ./photos の画像を Amazon の規約でチェックして。

> ./bottle.jpg から Amazon.co.jp 用の商品画像一式を 2K で作って。

> この写真から Amazon の白背景メイン画像を作って。

## 流れ

1. 商品写真・ストア・商品情報を確認します。
2. 画像プランと必要なクレジットを提示します。承認するまで生成しません。
3. 初回のみ teruns.com のリンクでアカウントを連携します（ワンクリック）。
4. メイン画像から 1 枚ずつ生成し、セット全体で商品の見た目を統一します。
5. 納品前に無料チェックで全画像を検証します。

クレジットが足りない場合は teruns.com の決済リンク（Stripe / PayPal）を表示します。
支払い後に「続けて」と伝えると、止まったところから再開します。

## プライバシーとセキュリティ

- リポジトリにもお使いの PC にも、モデルの API キーは置きません。スクリプトは Python 標準ライブラリのみで、通信先は `teruns.com` だけです。
- `listing-image-audit` は一切通信しません。
- 生成時には、画像を作るために参考写真を teruns.com に送信します。
- ログイントークンは `~/.teruns/credentials.json`（本人のみ読み取り可）に保存され、teruns.com のアカウントからいつでも無効化できます。
- 支払い情報は Stripe または PayPal のページでのみ入力し、チャットには入力しません。

詳しくは [SECURITY.md](SECURITY.md) をご覧ください。

## AI 生成画像について

生成画像のメタデータには AI 生成である旨が記録されます。マーケットプレイスや EU AI 法で表示が求められる場合があるため、各ストアのルールに従ってください。すべての画像は実際の商品を正確に表す必要があります。

## 開発者向け

構成とローカルテスト：[英語版 README](README.md#for-developers)。API 仕様：[docs/api.md](docs/api.md)。

## ライセンス

[MIT](LICENSE)。画像生成は Teruns のサービス上で行われ、[teruns.com](https://teruns.com) で課金されます。
