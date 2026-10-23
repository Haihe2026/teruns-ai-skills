# Teruns AI Skills · Listing Studio

[![check](https://github.com/Haihe2026/teruns-ai-skills/actions/workflows/check.yml/badge.svg)](https://github.com/Haihe2026/teruns-ai-skills/actions/workflows/check.yml) [![Agent Skills](https://img.shields.io/badge/Agent%20Skills-SKILL.md-2ea44f)](https://agentskills.io) [![Works with](https://img.shields.io/badge/works%20with-Claude%20Code%20%C2%B7%20Codex%20%C2%B7%20Cursor-555)](#安装) [![License: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

[English](README.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [日本語](README.ja.md) · **简体中文**

用一张真实商品照片，生成符合平台规范的商品图——支持 Amazon、Shopify、TikTok Shop、Etsy，
在 Claude Code、Codex、Cursor 或任何能读取 `SKILL.md` 的 Agent 里直接完成。
2K 或 4K 输出，图中文字自动使用店铺所在站点的语言。

| Skill | 作用 | 费用 |
| --- | --- | --- |
| [`listing-image-audit`](skills/listing-image-audit/SKILL.md) | 体检现有商品图：尺寸、格式、主图纯白底、商品占比、透明背景、CMYK、缺少的图类型 | **免费**，离线运行 |
| [`amazon-main-image`](skills/amazon-main-image/SKILL.md) | 一张 Amazon 主图：纯白 RGB 255 背景，商品约占画面 85%，无文字无道具 | 1 张 |
| [`listing-image-set`](skills/listing-image-set/SKILL.md) | 整套 Listing 图：主图、卖点图、细节图、场景图、尺寸图、包装清单图 | 5–7 张 |
| [`aplus-content`](skills/aplus-content/SKILL.md) | Amazon A+ 模块图（精确尺寸）及标题和正文文案 | 5–9 张 |
| [`teruns-catalog`](skills/teruns-catalog/SKILL.md) | 帮你选择合适的 skill | 免费 |

点数：**2K 图 1 点，4K 图 2 点。** 生成失败不扣点。
**首张 2K 图免费**——每个新的 teruns.com 账号赠送一次。
套餐：[teruns.com/#pricing](https://teruns.com/#pricing)。

## 安装

任意 Agent（skills CLI）：

```bash
npx skills add Haihe2026/teruns-ai-skills
npx skills add Haihe2026/teruns-ai-skills --skill listing-image-audit   # 只装免费体检
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

然后打开 `/plugins`，启用 **teruns-skill-systems**。

## 试试这样说

> 按 Amazon 规则检查 ./photos 里的图片。

> 用 ./bottle.jpg 做一套 Amazon.de 的 Listing 图，2K。

> 用这张照片做一张 Amazon 白底主图。

## 工作流程

1. skill 询问商品照片、目标店铺和商品信息，并与你确认。
2. 展示出图计划和所需点数，你确认之前不会出图。
3. 首次使用时给出一个 teruns.com 链接，点一下即可绑定账号。
4. 逐张出图，先出主图，整套图里商品保持一致。
5. 交付前用免费体检逐张检查。

点数不足时，skill 会给出 teruns.com 付款链接（Stripe 或 PayPal）。付款后说"继续"，即从中断处接着做。

## 隐私与安全

- 本仓库和你的电脑上都没有任何模型 API Key。脚本只用 Python 标准库，只连接 `teruns.com`。
- `listing-image-audit` 完全不联网。
- 出图时，你的参考照片会发送到 teruns.com 用于生成图片。
- 登录凭证保存在 `~/.teruns/credentials.json`（仅你本人可读），可在 teruns.com 账号里随时撤销。
- 付款信息只在 Stripe 或 PayPal 页面填写，绝不在对话中填写。

详见 [SECURITY.md](SECURITY.md)。

## AI 生成图片说明

生成的图片会在文件元数据中标记为 AI 生成。部分平台和欧盟《人工智能法》要求披露 AI 生成图片，请遵守所在平台规则。每张图都必须如实展示你的真实商品。

## 开发者

目录结构、本地测试方法见[英文 README](README.md#for-developers)，接口约定见 [docs/api.md](docs/api.md)。

## 许可

[MIT](LICENSE)。出图在 Teruns 服务端完成，通过 [teruns.com](https://teruns.com) 计费。
