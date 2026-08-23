# B 型 · 文档阅读方案

---

## 使用场景

文档阅读模板适合**长文本内容的消费和知识沉淀**场景，是三层模板中功能最丰富的一层。

| 场景 | 说明 | 典型篇幅 |
|:---|:---|:---:|
| **分析报告** | 竞品分析、技术调研、市场研究的长篇报告 | 500-5000 字 |
| **技术文档** | API 手册、架构说明、最佳实践指南 | 1000-10000 字 |
| **长文阅读** | 博客/Newsletter/论文的摘要整理 | 200-3000 字 |
| **知识沉淀** | 个人笔记、学习总结、项目复盘 | 500-5000 字 |
| **会议纪要** | 结构化会议记录，含待办、决策、讨论点 | 200-2000 字 |

### 不适合的场景

- **结构化数据浏览**（搜索+排序+分页 → 用 A 型表格）
- **多类目知识浏览**（顶部标签切换 → 用 C 型知识库）
- **协作编辑**（B 型是只读展示，不是编辑器）

---

## 方案设计

### 架构

```
Layer 1: style-guide.css (CSS 变量 + 组件基座)
Layer 2: layout-doc.html (骨架: 侧边栏TOC + 主内容区)
Layer 3: html-gen.py → doc 子命令 (Markdown→HTML 渲染器)
```

### 数据流

```
Markdown 文件 ──→ html-gen doc ──→ 单文件 HTML
                 │                  ├── 自动 TOC
                 │                  ├── 表格渲染
                 │                  ├── 代码高亮
                 │                  ├── 进度条
                 │                  ├── callout 提示框
                 │                  ├── 锚点链接
                 │                  ├── 代码行号
                 │                  └── 外链归档
                 └── 元信息自动计算
```

### 关键设计决策

| 决策 | 选择 | 理由 |
|:---|:---|:---|
| **Markdown 渲染** | 手写渲染器 | 零外部依赖，精准控制输出。仅需覆盖我们使用的语法子集 |
| **CSS 框架** | 参考 Docsify dark.css | 经过了大量实际文档的检验，适合深色主题文档阅读 |
| **侧边栏 TOC** | 固定 260px + 粘性定位 | 长文导航的黄金宽度，内容区 max-width 880px 保证阅读体验 |
| **滚动高亮** | JS 根据 `getBoundingClientRect().top ≤ 100` 判断 | 纯前端，无交叉观察者依赖 |
| **代码行号** | CSS counter + JS 拆分 line 元素 | 纯前端可选，单行跳过，不影响复制按钮 |
| **Callout** | 正则检测 `> **Note:**` 模式 | 利用原有 Markdown blockquote 语法，无需新语法 |
| **外链归档** | 服务端 `re.findall` 提取 + 追加 | 文档生成时一次性完成，客户零开销 |
| **图片灯箱** | 纯 CSS overlay + JS | 无第三方库，支持 Escape / 点击外部关闭 |

### 手写 Markdown 渲染器支持语法

````
# h1  ## h2  ### h3                    — 标题
**bold**  *italic*                      — 行内格式
`code`                                 — 行内代码
``` ```
 代码块                              — 围栏代码块
[link](url)                            — 链接 (target=_blank)
| table | with | cells |               — 表格
- list item                            — 无序列表
1. list item                           — 有序列表
---                                    — 分隔线
> blockquote                           — 引用
> **Note:** text                       — Callout 提示框
> **Warning:** text                    — Callout 警告
> **Tip:** text                        — Callout 提示
> **Danger:** text                     — Callout 危险
````

---

## 行业对标

| 维度 | B 型 · 文档阅读 | Docsify | VuePress | GitBook |
|:---|:---|:---|:---|:---|
| **定位** | 单文件文档阅读 | SPA 文档站点 | SSG 文档站点 | 托管文档平台 |
| **部署** | 单文件 HTML | 静态服务器 | 构建后静态文件 | SaaS |
| **渲染** | 服务端预渲染 | 客户端 JS 渲染 | 构建时 SSG | 服务端渲染 |
| **搜索** | ❌ 暂无 | ✅ 全文搜索 | ✅ algolia | ✅ 内置 |
| **TOC** | ✅ 自动 | ✅ 插件 | ✅ 自动 | ✅ 自动 |
| **代码高亮** | ✅ 行号 + 复制 | ✅ prism.js | ✅ prism/shiki | ✅ prism |
| **图片** | ✅ 灯箱 | ✅ 缩放 | ✅ 缩放 | ✅ 缩放 |
| **Callout** | ✅ 原生 | ✅ 插件 | ✅ 插件 | ✅ 内置 |
| **离线** | ✅ 单文件完整 | ❌ 依赖 CDN | ✅ 全构建 | ❌ 需网络 |
| **文件大小** | ~35KB（含内容） | ~100KB+CDN | ~50KB+构建产物 | N/A |
| **外部依赖** | 零 | marked.js | Vue/Webpack | SaaS |

**核心差异**：B 型不是文档站框架的替代品，而是「我需要把一个 Markdown 文件发给别人看」场景下的最优解。无需安装、无需构建、无需网络，生成即用。

---

## 功能清单

### 已实现 ✅

| 功能 | 说明 | 优先级 |
|:---|:---|---:|
| Markdown → HTML 渲染 | 手写渲染器，支持 h1-h3/表格/列表/代码块/链接/图片 | P0 |
| 自动侧边栏 TOC | 从 h2/h3 生成目录树，点击平滑滚动 | P0 |
| 滚动章节高亮 | 滚动时自动标记当前阅读位置 | P0 |
| 代码复制按钮 | 悬停显示，一键复制代码块内容 | P0 |
| 代码行号 | 多行代码块左侧行号（CSS counter），单行跳过 | P1 |
| Callout 提示框 | `> **Note/Tip/Warning/Danger**` → 蓝/绿/黄/红 | P1 |
| 锚点链接 ¶ | h2/h3 悬浮显示 ¶，点击复制 `#section-id` 到剪贴板 | P1 |
| 外链归档 | 自动提取全文 https:// 链接，去重排序追加到底部 | P1 |
| 阅读进度条 | 顶部 2px 固定钴蓝色进度条 | P0 |
| 图片灯箱 | 点击放大，overlay 展示，Escape 关闭 | P0 |
| 自动元信息 | 路径/创建时间/编辑时间/字数/阅读时长 | P0 |
| inline 全局格式化 | 表格内 `**bold**` `code` `[link]` 正确渲染 | P0 |
| 深色主题 | Docsify-inspired surface-950 深色主题 | P0 |
| 零外部依赖 | 单文件 HTML，无需加载 CDN | P0 |

### 待实现 🔜

| 功能 | 说明 | 优先级 |
|:---|:---|:---:|
| Back-to-top 按钮 | 长文阅读中快速回到顶部 | P2 |
| 浮动 TOC | 小屏设备上的悬浮目录按钮 | P2 |
| 正文宽度 65ch | 优化大屏阅读体验，限制行宽 | P2 |
| 面包屑导航 | 显示文档层级路径 | P2 |
| 上/下一篇导航 | 多文档间的顺序导航按钮 | P2 |
| 键盘快捷键 | j/k 滚行、Enter 打开链接、? 帮助、t 回到顶部 | P3 |
| 交互式进度条 | 显示剩余分钟数、章节标题 | P3 |
| 图片懒加载 | 长文档首次加载优化 | P3 |
| 全文搜索 | 多文档全文搜索（需要索引支撑） | P3 |
| Tags 系统 | 文档标签筛选和分类浏览 | P3 |
| 视频/音频嵌入 | 支持 iframe/embed 标签 | P3 |

---

## 快速开始

```shell
# 从 Markdown 生成文档
html-gen doc -i report.md -o report.html

# 指定标题
html-gen doc -i analysis.md --title "竞品分析报告" -o output.html

# 直接打开
open report.html
```

### 命令行参数

```
html-gen doc -h
  -i, --input FILE   输入 Markdown 文件（必需）
  -o, --output FILE  输出 HTML 文件
  --title TEXT       覆盖文档标题
  --subtitle TEXT    副标题（显示在侧边栏和页头）
```

### URL 入参控制展示设置

打开页面时可追加 URL 参数控制宽度、侧边栏、工具栏等展示设置（知识库 iframe 嵌入时自动附加）：

| 参数 | 取值 | 效果 |
|:---|:---|:---|
| `width` | `wide` / `narrow` | 内容区宽度：wide=1280px 宽屏 / narrow=720px 窄栏（默认 960px） |
| `sidebar` | `0` / `1` | 侧边栏显示：`sidebar=0` 隐藏（默认显示） |
| `toolbar` | `0` / `1` | 工具栏显示：`toolbar=0` 隐藏（默认显示） |

示例：

```
# 宽屏 + 隐藏侧边栏/工具栏（知识库嵌入模式）
report.html?width=wide&sidebar=0&toolbar=0

# 窄栏专注阅读
report.html?width=narrow
```

说明：
- 侧边栏/工具栏隐藏仅控制 `display`，功能保留（`[` 快捷键、搜索等仍可用）
- 知识库（C 型）加载 doc 页时自动附加 `sidebar=0&toolbar=0&t=<时间戳>`；概述类页面（url 含 overview）额外附加 `width=wide`
- `?t=` 时间戳用于绕过浏览器缓存，与展示参数正交

---

## 模板案例

该模板的精选案例（html-gen demo list ★ featured，路径相对 demos/）：

| 案例 | 说明 | 文件 |
|:---|:---|:---|
| [使用指南](../html-gen-usage-guide-v1.0-20260707.html) | html-gen 完整使用说明 | html-gen-usage-guide-v1.0-20260707.html |
| [A 型 · 表格模板说明](template-A-guide-v1.0-20260707.html) | 使用场景 · 方案设计 · 功能清单 | templates/template-A-guide-v1.0-20260707.html |
| [B 型 · 文档模板说明](template-B-guide-v1.0-20260707.html) | 使用场景 · 方案设计 · URL 入参控制 | templates/template-B-guide-v1.0-20260707.html |
| [Markdown 语法规范](template-B-markdown-spec-v1.0-20260707.html) | 支持的语法子集 · 规则 · 常见错误 | templates/template-B-markdown-spec-v1.0-20260707.html |
| [C 型 · 知识库模板说明](template-C-guide-v1.0-20260707.html) | 使用场景 · 方案设计 · 数据格式 | templates/template-C-guide-v1.0-20260707.html |
| [D 型 · 幻灯片模板说明](template-D-guide-v1.0-20260707.html) | 使用场景 · 方案设计 · 演示模式 | templates/template-D-guide-v1.0-20260707.html |
| [Slide 幻灯片版](template-D-slide-demo.html) | h2 分页 · 键盘翻页 · 圆点导航 · 全屏演示 | templates/template-D-slide-demo.html |

---

## 迭代记录

| 版本 | 日期 | 变更 |
|:---|:---:|:---|
| v1.0 | 2026-07-05 | 初版：Docsify 风格 TOC + 代码复制 + Markdown 渲染 |
| v1.1 | 2026-07-06 | 进度条 + 灯箱 + 锚点链接 + 代码行号 + callout + 外链归档 |
| v2.0 | 2026-08-11 | Bare 模式（默认隐藏 sidebar/toolbar，?sidebar=1&toolbar=1 展示）；折叠/拖拽/搜索/H3 开关/中英双语/主题切换 |
| v2.1 | 2026-08-18 | meta 去路径行；标题点击复制 fallback 完整 URL |
| v2.2 | 2026-08-19 | URL 入参控制展示设置（width=wide/narrow、sidebar/toolbar 正交） |
| v2.3 | 2026-08-23 | 新增「模板案例」章节（★ featured 精选） |
