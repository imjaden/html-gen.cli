# doc-body 三级宽度（URL 入参）— 设计文档

## 版本

v1.0 (2026-08-19)

## 背景与问题来源

用户在 `demos/drama/history-overview.html`（B 型文档，layout-doc.html 生成）中观察到：当隐藏左侧边栏（`?sidebar=0`，知识库 iframe 嵌入场景）后，内容区域 `.doc-body { max-width: 960px }` 仍锁死 960px，在宽屏下右侧留白过大，内容显示"很窄"。

需求：提供窄/中/宽 3 级内容宽度，当前 960px 为默认（中）级别，通过 URL 入参切换。

待确认清单（用户回复 1A 2A）定稿：

| 项 | 确认 |
|:--|:--|
| 1 持久化 | A=不持久化，纯 URL 入参驱动（与 sidebar/toolbar 一致） |
| 2 交付形式 | A=正式设计文档，走 heading-levels 流程（设计 → review → dev） |

## 目标形态

**现状**：
- `.doc-body { max-width: 960px }` 固定常量（layout-doc.html L81）
- 隐藏侧边栏时 doc-main 变宽，但正文仍限 960px

**目标**：
- URL 入参 `?width=narrow|medium|wide` 切换正文最大宽度
- 默认 medium = 960px（无参数时行为不变，向后兼容）
- 纯 URL 驱动，不 localStorage 持久化

## 决策记录

| 项 | 决策 |
|:--|:--|
| 参数名 | `width`（页面无同名参数冲突） |
| 取值 | `narrow` / `medium` / `wide`（语义化，避免 s/m/l 歧义） |
| 默认 | `medium` = 960px（当前值，无参数即默认） |
| 实现方式 | body class 方案（与 show-sidebar/show-toolbar 完全一致） |
| 不持久化 | 每次加载按 URL 参数决定，不写 localStorage |
| 实现范围 | 仅 layout-doc.html 模板；生成的 html 重新生成生效 |

## 三级宽度值

| 级别 | 参数 | max-width | 适用场景 |
|:--|:--|:--|:--|
| 窄 | `?width=narrow` | 720px | 纯文字长文阅读（类阅读 App 窄栏） |
| 中 | 无参数 / `?width=medium` | 960px | 默认，通用（现状） |
| 宽 | `?width=wide` | 1280px | 表格/宽图/多栏内容，嵌入 iframe 填满 |

注：wide 不用 100%（max-width:none），保留 1280px 上限避免超宽屏幕下正文无限拉伸；同时避免与 padding 0 80px 在极端宽度下的冲突。

## 实现方案

### 1. layout-doc.html CSS（L81 后追加）

```css
/* ── Content width levels: ?width=narrow|medium|wide (default medium=960px) ── */
body.width-narrow .doc-body { max-width: 720px; }
body.width-wide .doc-body { max-width: 1280px; }
```

### 2. layout-doc.html JS（L245 后追加，与 sidebar/toolbar 解析同处）

```js
// ── Content width: ?width=narrow|medium|wide (不持久化, 默认 medium) ──
var w = params.get('width');
if (w === 'narrow') document.body.classList.add('width-narrow');
else if (w === 'wide') document.body.classList.add('width-wide');
// medium 或未指定: 不加 class, 用默认 960px
```

### 3. 移动端兼容

- 现有 `@media (max-width: 768px)` L182 将 `.doc-body { padding: 0 16px 40px; }`
- max-width 在移动端自然失效（视口 < 720px 时正文占满），无需额外处理
- wide 级在窄屏同样被媒体查询约束，安全

### 4. 重新生成产物

- `demos/drama/history-overview.html` 等已生成页面需重新生成才含新逻辑
- 全量: 重新生成 demos 下 B 型文档（或仅需用到的页面）

## 测试

### 回归测试（tests/test_templates.py 或 test_doc_width.py 新增）

- test_doc_width_default: 无 width 参数 → doc-body max-width 960px
- test_doc_width_narrow: ?width=narrow → body.width-narrow → max-width 720px
- test_doc_width_wide: ?width=wide → body.width-wide → max-width 1280px
- test_doc_width_no_persist: 不同 URL 间无 localStorage 写入（html-gen:doc_width 不出现）

### Selenium

- test_doc_width_render: 3 种 width 参数下 doc-body 计算样式正确 + 0 JS errors
- test_doc_width_embed: ?sidebar=0&toolbar=0&width=wide 组合下正文宽度 > 960px

## 影响范围

| 文件 | 改动 |
|:--|:--|
| layout-doc.html | CSS 2 条 + JS 3 行 |
| demos/*.html | 重新生成（若需立即生效） |
| tests/ | 新增宽度级别测试 |
| features.md | B 型文档条目补充（URL 宽度入参） |
| AGENTS.md | 可选：B 型文档功能清单补充（若项目惯例维护） |

## 风险

- 低：纯增量，无参数行为完全不变
- wide 1280px 与 padding 0 80px 的组合：1280+160=1440px，doc-main 需 ≥1440px 才满宽，符合预期（嵌入 iframe 通常够宽）
- 不持久化是有意决策：URL 是唯一状态源，刷新/分享链接即得同宽度
