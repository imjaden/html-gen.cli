---
title: 回执 hermes-manager — doc 宽度新增 xwide（1600）档
topic: html-gen
type: handoff-receipt
version: 1.0
date: 2026-11-28
status: done
target_repo: html-gen
in_reply_to: ~/CodeSpace/hermes-manager/documents/handoff/20261128-to-html-gen-width-xwide-prompt.md
role: ops
---

# 回执：`?width=xwide` 已落地（方案 A）

## 改动摘要

`layout-doc.html`（HTML-GEN-CL048，v3.8）：

```css
/* ── Content width levels: ?width=narrow|medium|wide|xwide (default medium=960px) ── */
.doc-body { max-width: 960px; }
body.width-narrow .doc-body { max-width: 720px; }
body.width-wide   .doc-body { max-width: 1280px; }
body.width-xwide  .doc-body { max-width: min(100%, 1600px); }
```

```js
var w = params.get('width');
if (w === 'narrow') document.body.classList.add('width-narrow');
else if (w === 'wide') document.body.classList.add('width-wide');
else if (w === 'xwide') document.body.classList.add('width-xwide');   // 跟随容器, 上限 1600
```

- 走方案 A（新增 `xwide`），`narrow/medium/wide` 行为与既有页面完全不变
- 不持久化（仍是 URL 参数语义）；未改 knowledge / table 两套布局
- 版本随本批：`__version__ = "3.8"`、`__release_date__ = "2026-11-28"`（同批未发版）

## 验收判据实测（Chrome 无头 / 真机浏览器，`demos/doc-guide.html`）

| 判据 | 场景 | 实测 |
|:---|:---|:---|
| 1 | `?width=xwide` @1920 视口（容器 1600） | `.doc-body` 渲染宽 **1600px**，`maxWidth = min(100%, 1600px)` |
| 1 | `?width=xwide` @1600 视口（容器 1334） | 渲染宽 **1334px** = 容器宽（跟随，未超 1600） |
| 1 | `?width=xwide` @1280 视口（容器 1014） | 渲染宽 **1014px** = 容器宽 |
| 2 | `?width=narrow` @1920 | **720px** |
| 2 | 无参数 @1920 | **960px** |
| 2 | `?width=wide` @1920 | **1280px** |
| 3 | 单测 | `tests/test_doc_width.py` 新增 4 条（CSS 规则 / URL 白名单 / Selenium 上限 1600 / 跟随容器）；全量 **515 passed, 106 subtests** |
| 4 | 回归 | 只新增一个 body class 与一条 `max-width` 规则；无参数时不加 class，深浅色 / 侧栏 TOC / lightbox 代码零改动；`baseline --check` **49/49** |

## 上游用法

知识站正文若仍用注入覆盖，可以删掉那段规范外 CSS，改传 `?width=xwide` 即可：

```
/demos/xxx.html?width=xwide&sidebar=0&toolbar=0
```

`wide`(1280) 与 `xwide`(≤1600) 并存：容器 <1600 时两者等价，>1600 时 `xwide` 才吃到 1600 上限。

## 备注

- CHANGELOG 口径：本项目无独立 `CHANGELOG.md`，功能变更记在 `features.md`（本批已加一行 `doc 模板 ?width= 增第四档 xwide`）
- 该档位对 1920 屏不再留 ~250px 右侧空白；1600 屏下由 1280 → 1334 吃掉整容器
