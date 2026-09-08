---
title: doc/slide 模板手册
topic: html-gen
type: summary
version: 1.0
date: 2026-09-08
author: hermes-v0.20.6(2026.8.27)
profile: dev
provider: deepseek
model: deepseek-v4-flash
tags: [html-gen, doc, slide, layout-doc, layout-slide, markdown, url-params, show-md, width, bare, h4-h6, typography, sidebar, toolbar, handbook, summary]
---

# html-gen doc/slide 模板 v1.0

> 本文是 B 型文档（layout-doc）与 D 型幻灯片（layout-slide）模板的主题手册：模板 UI 的运行时 URL 入参机制（sidebar/toolbar、width 三级、show-md）、Markdown 渲染规范（h1-h6 标题、TOC 边界、Callout、转义链）、排版基座、以及前置设计蓝图（统一侧边栏、slide 工具栏）。内容以 2026-09-08 当前实现为准（layout-doc.html / layout-slide.html / layout-knowledge.html / html-gen.py 实测互证）。

## 1. 功能定位

doc/slide 共用同一 Markdown 引擎（html-gen.py `md_to_html()`），模板层各自承担阅读交互。两条设计主线：

- **运行时 URL 入参驱动 UI**：`layout-doc` 的展示偏好全部走 `?参数=值` → body class → CSS 的同一范式（sidebar/toolbar、width、show-md），缺省值向后兼容；slide 无 URLSearchParams 机制（生成端输出 + CSS 默认隐藏）。
- **Markdown 渲染与安全**：标题 h1-h6 全支持（h4-h6 仅加锚点不进 TOC）、Callout 提示框、转义链、纯文本渲染安全约束。

演进素材覆盖 7 个子项：doc-body 三级宽度 / meta 路径 show-md / doc bare 模式 / h4-h6 标题 / 排版审计 / sidebar+table 设计蓝图 / slide 工具栏设计。

## 2. 演进子项与审计形态

| 子项 | 日期 | 内容 | 审计形态 |
|:--|:--|:--|:--|
| sidebar+table 布局设计 v3.2 | 2026-07-14 | 统一侧边栏 + A 型表格增强蓝图 | 设计级（无 review） |
| slide 工具栏设计 v1.0（内文 v2.3） | 2026-07-14 | 标题区重构 + 右上语言/主题工具栏 | 设计级（无 review） |
| layout-doc bare 模式 v1.0→v1.1 | 2026-08-06~12 | sidebar/toolbar URL 入参显隐 | 初审 CONDITIONAL（🔴 N1/N2）→ 复审 PASS |
| h4-h6 标题渲染 | 2026-08-12 | 标题泄漏修复 + 锚点 | 初版 CONDITIONAL → 复检 PASS → verify（100 passed） |
| doc-body 三级宽度 | 2026-08-19 | `?width=narrow\|medium\|wide` | review PASS 100/A |
| doc meta 路径 show-md | 2026-08-19~21 | 脱敏文件名路径行 + `?show-md=1` | **REJECT 85/B（🔴 M4-1）→ dev-prompt 修正实施，无独立 audit 文件** |
| 排版审计（字体倒挂修复） | 2026-08-27 | 容器基座 + blockquote 紧凑 | commit-range 初轮 80/B → recheck PASS 100/A |

**审计形态备注**：doc-meta 族在 review REJECT 之后没有独立 implementation audit 文件——修正经 design 采纳后由 dev-prompt（2026-08-21）驱动实施，验证内嵌该 prompt「验证」节；实现在 git d3d605d。手册按此如实标注。

## 3. 模板运行时机制

### 3.1 URL 入参 → body class 对照（layout-doc.html，当前语义）

| URL | body class / 效果 |
|:--|:--|
| `?width=narrow` | `width-narrow` → `.doc-body{max-width:720px}` |
| `?width=medium` 或缺省 | 不加 class → 默认 960px |
| `?width=wide` | `width-wide` → `.doc-body{max-width:1280px}` |
| `?show-md=1` | `show-md` → `.meta-path{display:inline}`（默认 display:none，隐私） |
| `?sidebar=0` | **不加** `show-sidebar` → 侧边栏隐藏（缺省/`=1` 展示——默认展示语义） |
| `?toolbar=0` | **不加** `show-toolbar` → 语言/主题工具栏隐藏（同上） |

- **默认语义转折（源码层演进，无设计素材）**：2026-08-18 fe49bcb 按 bare 设计「默认隐藏」实施，30 分钟后 71db848 反转「默认展示，嵌入端显式传 0」。当前代码 = 默认展示（`params.get('sidebar') !== '0'`）；features.md L45 仍写旧语义（滞后待核）。
- github-corner / home-link 跟随 toolbar 显示态（`body:not(.show-toolbar)` 隐藏）。
- layout-knowledge 装载器恒拼 `…sidebar=0&toolbar=0&t=<时间戳>`；overview 类 URL 再拼 `width=wide`。
- layout-slide **无** URL 入参解析（show-md/width/sidebar 均不适用；slide 的 meta 路径行为 = 生成端输出 + CSS 默认隐藏）。
- 宽度**不持久化**是有意决策（URL 是唯一状态源）；show-md/sidebar/toolbar 同理纯入参驱动。

### 3.2 裸模式（bare）目标形态（设计 v1.1 语义 + 现状反转注记）

设计目标四态：知识库嵌入（默认）两隐藏；`?sidebar=1&toolbar=1` 全展示；`?sidebar=1` 仅侧边栏；`?toolbar=1` 仅工具栏。实现经反转后：嵌入场景由 layout-knowledge 显式拼 `sidebar=0&toolbar=0` 达成（等效裸模式），独立打开默认全展示。设计要点仍有效：

- 显隐由**双独立 class**（show-sidebar/show-toolbar）驱动，CSS/JS 一一对应；禁「三 class 组合 + no-* 死 class」（N1）。
- show-* 只控 display，**不触碰 collapsed 折叠/宽度逻辑**（N5）。
- CSS 级联：原规则 `.doc-sidebar`/`.top-toolbar` 已带 `display:flex`，默认隐藏规则（同特异性 0,1,0）须改写原规则或置后，否则静默失效（N6）。
- knowledge iframe src 含 `?t=` 时间戳，测试比对需剥离（N3）。

### 3.3 正文三级宽度

- 三级：narrow=720px（纯文字长文）、medium=960px（默认，现状）、wide=1280px（表格/宽图/多栏/嵌入 iframe 填满）。**wide 不用 max-width:none**（避免超宽屏正文无限拉伸）。
- 移动端 `@media (max-width:768px)` 下 max-width 自然失效，wide 同样被约束，无需额外处理。
- 实现：CSS 2 条 + JS 3 行（与 sidebar/toolbar 解析同处）；已生成产物须重新生成才生效。

### 3.4 meta 路径行（doc/slide，脱敏）

- 生成端（cmd_doc/cmd_slide）恒输出 `<span class="meta-path"> · 路径: <code>{basename}</code></span>`（`os.path.basename` 脱敏，无目录结构）。
- doc 默认隐藏、`?show-md=1` 显示；slide 无运行时显隐，CSS 默认隐藏（隐私）。
- 标题点击复制语义：优先匹配 `meta` 中 `/路径:\s*(.+)/` → 复制脱敏文件名（M4-1 修复后 URL/绝对路径/`~/`/纯文件名都过第二道闸门 `[\\w.\- ]+$`）；无路径行 fallback 复制 URL。

## 4. Markdown 渲染规范（引擎 + 模板）

### 4.1 标题 h1-h6 与 TOC 边界

- `md_to_html()` 标题匹配**从最长前缀开始**：`######`→`#####`→`####`→`###`→`##`→`#`；h1-h6 全部生成 slug id + `_md_escape()`。
- **TOC 仅收录 h2/h3**（`.doc-body h2,h3` → toc-h2/toc-h3）——h4-h6 不进 TOC 是有意决策（避免三层以上导航）；h3 默认隐藏、H3 开关（🔍 面板或独立开关）显示。
- h4-h6 渲染后**独立循环**追加 `.anchor-link`（id fallback 用索引 `'section-'+i`，勿用 textContent——含空格会生成非法 id）；点击复制「当前 URL+#id」。
- h4-h6 字号 0.95/0.88/0.82rem，dark（#c0c0c0/#b0b0b0/#a0a0a0）+ light（#444/#555/#666）双主题递减。
- **h7+ 不支持**（会泄漏为段落）——生成 prompt 约束兜底（优先 h1-h3，深层级可用 h4-h6，禁 h7+）。
- 支持面：加粗/斜体/行内代码/链接（自动 target=_blank）/pipe table/围栏代码（变长 fence 嵌套、行号、复制）/无序与有序列表/引用/分隔线/Callout。**不支持**缩进子列表（需平铺）、`![图片]`（用 `<img>`）、HTML 标签（会被转义）。
- Callout：`> **Note:/Tip:/Warning:/Danger:/Caution:**` 及中文 注意/提示/警告/危险；CSS 以 `.doc-body blockquote.callout` 高特异性覆盖紧凑基座。

### 4.2 安全与转义

- 纯文本行 `<` `>` `&` 自动转义（防 XSS）；`**bold**` 等 Markdown 语法在转义后仍正常渲染。
- 仅 `<script>` 上下文注入值（columns/data/tabs/options/groups/items）做 `</` → `<\/` 转义；HTML 上下文（content/title/metadata）不做（误转义会出现 `<\/h2>` 字面标签）。
- 标题文本走 `_md_escape()`，与行内转义一致。
- 数据渲染一律 textContent / 白名单 URL，禁 innerHTML 注入用户内容。

### 4.3 排版基座（2026-08-27 排版审计定稿）

- 容器基座：`.doc-body { font-size:0.88rem }`；`.slide-page { font-size:0.88rem }`。
- blockquote 紧凑：两模板 blockquote `margin:0.1rem 0; padding:2px 16px`。
- callout 保持（3A）：`blockquote.callout { padding:10px 16px; margin:0.75rem 0 }` 特异性覆盖，不受紧凑化影响。
- 标题 h1-h6（1.5~0.82rem）/ table 0.8rem / code 0.78rem 全部显式声明，不依赖容器继承。

## 5. 前置设计蓝图（设计级，无 review）

### 5.1 sidebar+table 统一布局（sidebar-table-design v3.2，内文 v3.3）

决策记录 10 条（原文编号 1-10）：48px 折叠宽度 / 折叠钮在侧边栏底部 / knowledge 改侧边栏+内容区 / doc 标题复制同 slide / 默认点击模式新标签 / 分栏比例 40:60 / 密度默认 34px / localStorage 记忆 / Phase 1+2 全实施 / 侧边栏优先。

- 功能矩阵目标：折叠/展开、标题点击复制、页码/进度、H3 开关、TOC 搜索、章节高亮、localStorage 记忆、宽度拖拽 200-400px、`[` 快捷键（INPUT/TEXTAREA 豁免）。
- 现状交叉：doc 已实现折叠/`[` 键/宽度拖拽（`html-gen:doc:sidebar-width`）/H3 开关/标题复制/TOC 搜索；knowledge 已实现 `.kw-sidebar` 260px/48px + 拖拽。
- 渲染安全三铁律：`row.url` 仅 iframe `sandbox="allow-same-origin"` 禁脚本；`row.desc` textContent 禁 innerHTML；URL 白名单 `/^(https?:|\/|~\/)/`，非白名单静默降级键值对。
- localStorage 规划键 `html-gen:sidebar:*` / `html-gen:table:*`，统一 `restore(key,fallback,validate)`（try/JSON.parse/validate）；素材期键名与实现期细化的 `html-gen:doc:*`/`html-gen:layoutslide_*` 有演进差。

### 5.2 slide 工具栏/标题（slide-toolbar-design v1.0，内文 v2.3）

- `div.logo` → `div.slide-title`；hover title=完整标题；点击复制文件路径（`$HOME`→`~`）+ Toast。
- 工具栏 `#topToolbar`：fixed top:12 right:16 z-900 胶囊；🇨🇳🇺🇸 语言按钮 + divider + 🌙 主题钮；默认中文/深色。
- 页码 i18n：zh「共 38 页」/「3 / 38」；en「38 pages」/「3 / 38」（最小 i18n 范围，仅 `.sub` 走 `t(key,params)`）。
- 持久化键已前缀化（`html-gen:layoutslide_lang` 等）；clipboard 走 try/catch + execCommand 兜底。
- 现状交叉：layout-slide L229 `#slideTitle`、L261-262 工具栏按钮形态与设计一致。

## 6. 关键决策（原文编号）

### 6.1 doc bare 模式（documents/archive/solutions-20260908/layout-doc-bare-design-v1.1-20260806.md，D1-D6）

| 编号 | 决策 |
|:--|:--|
| D1 | 入参 `sidebar=1`/`toolbar=1` 展示，缺省/非 1 隐藏；与 `?t=` 正交（URLSearchParams） |
| D2 | CSS 默认隐藏 + 双独立 class（show-sidebar/show-toolbar）；不触碰 collapsed/宽度逻辑 |
| D3 | layout-knowledge 不改；iframe src 带 `?t=` 时间戳 |
| D4 | 重新生成 22 个 doc 产物（drama 15 + demos 根 7） |
| D5 | 测试：加载 URL 带参 + 新增 bare 4 参数组合用例；knowledge 嵌入可见性断言 |
| D6 | 文档同步（AGENTS.md / skills/html-gen / features.md） |
| N1(🔴) | 三 class 组合死 class → 双独立 class |
| N2(🔴) | 产物清单漏 2 → 补全 22 逐一列名 |
| N3/N4/N5(🟡) | iframe `?t=` 表述 / 测试计数 / collapsed 死交互 |
| N6(🟢) | 同特异性级联顺序——默认隐藏规则须置后或改写原 display:flex |

### 6.2 doc-body 三级宽度（documents/archive/root-20260908/doc-body-width-levels-design-v1.0-20260819.md）

| 决策行 | 内容 |
|:--|:--|
| 参数名/取值/默认 | `width` = narrow/medium/wide；默认 medium 960px（缺省即默认，向后兼容） |
| 实现方式 | body class 方案，与 show-sidebar/show-toolbar 同构 |
| 不持久化 | URL 是唯一状态源，不写 localStorage |
| 范围 | 仅 layout-doc.html；已生成 html 重新生成才生效 |

### 6.3 doc meta show-md（documents/archive/root-20260908/doc-meta-path-showmd-design-v1.0-20260819.md + dev-prompt I1-I8）

| 编号 | 决策 |
|:--|:--|
| 确认 1-4 | meta 输出路径行 + URL 入参显隐；`show-md=1` 显示缺省隐藏；只显示 basename；默认不展示（隐私） |
| M4-1(🔴) | 第二道 URL 闸门 `/^(https?:|\/|~\/)/` 不匹配纯文件名 → 复制+toast 静默失效；修复 = 正则加 `[\w.\- ]+$` 分支 |
| slide 处理 | slide 不做运行时显隐（无 URLSearchParams），生成端统一输出 + 默认隐藏 |
| I1-I8 | 两 cmd meta 追加路径行（basename 脱敏）/ doc CSS+JS show-md / L311 正则扩展 / 测试并入 test_templates.py / 产物重生成 / features.md 补 |

### 6.4 h4-h6（documents/archive/root-20260908/heading-levels-fix-design-v1.0-20260812.md，决策 1-6 + D-新增）

| 编号 | 决策 |
|:--|:--|
| 1 | 修复范围 = C 模板加 h4-h6 渲染 + 生成 prompt 约束，双管齐下 |
| 2 | h4-h6 **不进 TOC**（TOC 保持 h2/h3） |
| 3 | 独立 CSS：h4 0.95rem / h5 0.88rem / h6 0.82rem，dark+light |
| 4 | h4-h6 加 id + 锚点（复制链接） |
| 5 | prompt 约束优先 h1-h3，深层可用 h4-h6，**禁 h7+** |
| 6 | 测试：md_to_html 回归 + Selenium 渲染 |
| D-新增 | JS 拆分 anchor 循环：h4-h6 独立循环追加 `.anchor-link`，TOC 循环保持 h2/h3（初版 review 遗漏） |

### 6.5 排版审计（documents/archive/review-20260908/html-gen-typography-review-v1.0-20260827.md）

- 决策依据 1A 容器基座 / 2A blockquote 紧凑 / 3A callout 保持 / 4A 仅 doc/slide / 5A 重生成产物。
- 初轮 CONDITIONAL 80/B：HG-SEC-041（🔴 slide-demo.html 变量基座丢失，深色失效）+ HG-SEC-042（🟡 双 style 块旧覆新）。
- recheck（8347dd8）PASS 100/A：单 style 块、:root 37 变量恢复、blockquote 紧凑生效。

## 7. 已知坑

| # | 坑 | 说明/出处 |
|:--|:--|:--|
| P1 | 标题复制第二道闸门静默失效 | meta 路径为纯文件名时 URL 白名单不匹配 → 复制无提示不执行；正则须含 `[\w.\- ]+$`（M4-1） |
| P2 | CSS 同特异性级联顺序 | 默认隐藏规则须置后或改写原 display:flex，否则静默失效（N6/fe49bcb） |
| P3 | 死 class | 无对应 CSS 的 class（no-*）纯视觉无效且误导（N1） |
| P4 | collapsed 死交互 | 默认隐藏下 `[`/toggleSidebar 仍执行；show-* 只控 display 不碰 48px（N5） |
| P5 | h4-h6 不进 TOC | 有意决策；文档/测试锁定「TOC 仅 h2/h3」（决策 2） |
| P6 | h7+ 泄漏为段落 | 模板不认；prompt 约束兜底（决策 5） |
| P7 | 标题分支顺序 | startswith 必须长→短（###### 先于 #），防误吞 |
| P8 | id 用 textContent 生成非法 id | fallback 用索引 `'section-'+i`（复检观察） |
| P9 | 产物同步误伤第一个 style 块 | 「从模板提取替换」须区分基座块 vs 业务样式块（HG-SEC-041 根因） |
| P10 | 重复 style 块旧覆新 | 修复看似做了实际没生效（HG-SEC-042） |
| P11 | 排版测试盲区 | 新用例未覆盖 slide-demo → SEC-041/042 不被测试暴露 |
| P12 | knowledge iframe 断言须去 `?t=` | src 含时间戳，比对先剥离（N3/D5） |
| P13 | clipboard 需 secure context | 不可用时 execCommand textarea 兜底，两路 try/catch |
| P14 | localStorage 键前缀演进 | 素材裸键 → `html-gen:doc:*`/`html-gen:layoutslide_*`；引用键名注明版本 |
| P15 | 渲染安全三铁律 | url 白名单、desc textContent、iframe sandbox（蓝图 §2.5） |
| P16 | 已生成产物不含新逻辑 | URL 入参/渲染改动须重新生成（A.5/D 族影响面） |

## 8. 差异与待核记录

- features.md L45 bare 行仍写「默认隐藏 + ?sidebar=1 展示」→ 与当前代码（默认展示 + ?sidebar=0 隐藏）矛盾（71db848 反转未同步文档）。
- `help doc` Markdown 语法节只列 h1-h3，未列 h4-h6（引擎已支持）。
- bare 默认值反转 commit 71db848 无配套 design/review 素材（源码层决策）。
- 文件名版本滞后：sidebar-table 文件名 v3.2/内文 v3.3；slide-toolbar 文件名 v1.0/内文 v2.3；heading-levels review 文件名 v1.0/内文 v1.1（复检报告）。引用版本以内文为准。
- layout-doc-bare 两次 review 测试计数 100 vs 103 同日并存（口径漂移）。
- doc/slide CLI 无 --showmd/--no-meta/--width 生成端选项（运行时 URL 入参是模板层机制；实跑 doc -h/slide -h 仅 -i/-o/--title/--subtitle/--github-url/--home-url/--favicon/--quiet）。

## 9. 参考文档

- 保留原位：features.md、layout-doc.html、layout-slide.html、layout-knowledge.html、style-guide.css、html-gen.py、demos/（B 型产物）、review-log.md / .review-level.yaml（历史不追改）。
- 本族过程文档（17 份）已归档（2026-09-08 执行） → `documents/archive/{solutions,root,review}-20260908/`：

| 素材 | 归档路径 | 归档桶 |
|:--|:--|:--|
| doc-body 三级宽度设计 + verify? | documents/archive/root-20260908/doc-body-width-levels-design-v1.0-20260819.md | root |
| doc-body 评审 + process prompt | documents/archive/review-20260908/doc-body-width-levels-{review-v1.0,review-prompt}-20260819.md | review |
| doc meta show-md 设计 | documents/archive/root-20260908/doc-meta-path-showmd-design-v1.0-20260819.md | root |
| doc meta 评审 / dev-prompt / process prompt | documents/archive/review-20260908/doc-meta-path-showmd-{review-v1.0,dev-prompt,review-prompt}-20260819/20260821.md | review |
| layout-doc bare 设计 v1.1 | documents/archive/solutions-20260908/layout-doc-bare-design-v1.1-20260806.md | solutions |
| layout-doc bare 初审 / 复审 | documents/archive/review-20260908/layout-doc-bare-{review-v1.0,review-v1.1}-20260812.md | review |
| heading-levels-fix 设计 | documents/archive/root-20260908/heading-levels-fix-design-v1.0-20260812.md | root |
| heading-levels 复检 / process prompt | documents/archive/review-20260908/heading-levels-fix-{review-v1.0,review-prompt}-20260812.md | review |
| heading-levels verify | documents/archive/root-20260908/verify-prompt-heading-levels-20260812.md | root |
| 排版审计 | documents/archive/review-20260908/html-gen-typography-review-v1.0-20260827.md | review |
| sidebar+table 设计 v3.2 | documents/archive/root-20260908/sidebar-table-design-v3.2-20260714.md | root |
| slide 工具栏设计 v1.0 | documents/archive/root-20260908/slide-toolbar-design-v1.0-20260714.md | root |
