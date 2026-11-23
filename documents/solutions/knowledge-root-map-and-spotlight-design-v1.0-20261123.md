---
title: knowledge 模板「根页返回 + 菜单地图 + 统一搜索面板」设计
version: v1.0
date: 2026-11-23
status: design-only
closed_loop: HTML-GEN-CL047
author: html-gen-ops
scope: 仅设计，不改源码（等指示实施）
source: 用户 2026-11-23 讨论四条期望（全采推荐）
---

# knowledge 模板 · 根页返回 + 菜单地图 + 统一搜索面板

> 本文件只出设计，**不动源码**。实施另起一步（编号已申请：**HTML-GEN-CL047**）。
> 目标版本 **v3.6（2026-11-23）**：模板行为变更（根页状态机 + 搜索入口），需全量重渲 knowledge 产物。

## 1. 需求 → 验收判据（AC）

| # | 用户期望 | AC（可机器验证） |
|:--|:--|:--|
| R1 | 点左上角 `div.sidebar-title` 回知识库根页 | AC1：任意条目打开后点标题 ⇒ `#welcomePanel` 带 `.active`、`#frameWrap` 无 `.active`、URL 无 `item=`、`localStorage['html-gen:kw_item']` 被清除 |
| R2 | 根页加「菜单地图表格」：列=横向页签标题，单元格=该组左侧菜单清单 | AC2：`#kwMap` 内 `table` 的**列数 = GROUPS.length + 1**（首列为行表头列）、每格条目数之和 = ITEMS.length、点击任一格内条目 ⇒ 走 `selectItem()` |
| R3 | 一个搜索功能，覆盖所有菜单**标题 + 副标题 + 描述**；**保留浏览器原生搜索** | AC3：`⌘/Ctrl+K` 与侧栏 🔍 打开同一面板；输入命中 `title/section/desc/page_title/group` 任一面即出现在结果；`⌘F` **不再被拦截**（`defaultPrevented === false`，原生查找可用） |
| R4 | 统一搜索弹出面板结构（默认输入框 + 实时匹配清单），参考 `tool-nav-manager/index.html` | AC4：面板 DOM 与 tool-nav-manager 同构（overlay / modal / input-wrapper / results / hint），`↑↓←→` 移动、`Enter` 打开、`Esc`/外点关闭、无匹配空态 |

## 2. 现状核对（证据行号，2026-11-23 复核）

| 事实 | 位置 | 影响 |
|:--|:--|:--|
| `div.sidebar-title` 点击 = **复制路径/URL**（`copyText`） | `layout-knowledge.html:278-284` | R1 要改点击语义，**复制能力须另给入口**（§3.2） |
| 根页 `#welcomePanel` 存在，含标题 + `<!--WELCOME_TEXT-->` + 徽章图例 `#wLegend` | `:212-216`、CSS `:139-145` | R2 只需在此面板加地图表；但面板是**居中列 + 440px 文案宽**，放表要改布局 |
| `selectItem()` 执行即 `welcomePanel.remove('active')`，全模板**无一行**把它加回 | `:428` | 这就是「无返回途径」的根因 |
| `switchGroup()` 会**自动选中该组首条** | `:346-348` | 不改成回根页，地图表永远看不到（行为变更，需在验收里体现） |
| 现有搜索 = 侧栏过滤式：`#kwSearchWrap` + `doKwFilter()`，≥2 字、匹配 `.kw-item-text`（**条目名**） | `:199-200`、`:521-541` | R3 的匹配面必须扩到 section/desc/page_title/group；入口与 UI 由面板取代 |
| v3.5 起 `⌘/Ctrl+F` 被**捕获阶段拦截**打开侧栏搜索 | `:478-486`（CL044） | **与 R3 直接冲突** ⇒ CL044 的拦截必须移除（§3.4、§6） |
| ITEMS 键：`title/group/section/badge/url/desc/page_title`；数据面 `_chaitin` 12 条（无 desc）、`_cloudwise` 28 条（14 条带 desc） | `:229`、`data/*.json` | 副标题←`section`、描述←`desc`、全名←`page_title`；**无新增数据键** |
| 参考件 `tool-nav-manager/index.html`：`.search-overlay/.search-modal` + `SearchHandler`（`↑↓←→`/`Enter`/`Esc`/外点/空态/`.sel` 高亮），匹配面 = 标题+分组+启动类型 | 只读，`:321-334`、`:979-1060`、`:930-938` | 面板结构与键盘行为照抄；**触发方式不照抄**（它拦 ⌘F，与本需求相反） |

## 3. 设计方案

### 3.1 状态机（根页 vs 条目）

- 新增 `var KW_VIEW = 'root' | 'item'`；`selectItem()` 置 `item`，`kwGoRoot()` 置 `root`。
- `kwGoRoot()`（新，全局）：`welcomePanel.classList.add('active')`、`frameWrap.classList.remove('active')`、`kwBody.innerHTML=''`、`contentFrame.src='about:blank'`、`activeItem=null`、清 `.kw-item.active` 与 `.kw-section-title.active`、`localStorage.removeItem('html-gen:kw_item')`，URL 用 `history.replaceState` 删 `item`（保留 `group`）。
- 首次加载：`?item=` 命中 ⇒ 直接进条目（现状不变）；`?view=root` 或 `item` 缺省 ⇒ 根页。
- `switchGroup()`：**改为**渲染侧栏 + `kwGoRoot()`（不再自动选首条）。跨组同名跟随逻辑（`:336-345`）随之删除——收益是语义可预期，代价是「切页签后原条目消失」，已在 §6 列为行为变更。
- 侧栏折叠态下点标题：先 `_kwReveal`-式展开再回根页？**不**——折叠态标题不可见（`.kw-sidebar.collapsed .kw-sidebar-header{display:none}`），无需处理。

### 3.2 标题点击语义与「复制路径」的安置

| 旧 | 新 |
|:--|:--|
| 点 `.sidebar-title` → 复制路径/URL | 点 `.sidebar-title` → **回根页**；复制路径改由**新增** `#kwCopyPathBtn`（`⧉`，`.kw-sidebar-header` 右侧，`title="复制页面路径"`）承担，复用现有 canonical `copyText()` 块（四模板逐字节一致，**不得改写该块**） |

### 3.3 菜单地图表格（根页）

- 容器 `#kwMap`，插在 `#welcomePanel` 的 `.w-sub` 之后、`#wLegend` 之前；`--welcome` 欢迎语保留。
- 结构（**列 = 横向页签，行 = section**，用户采纳推荐）：

```
| 章节 \ 类目 | 🏢 公司概况 | 🧩 产品体系 | 📊 经营分析 |
| 概述        | 公司画像 · 发展历程 | — | — |
| 产品        | — | 产品矩阵 · 产品架构 | — |
```

- 行 = 各 section 的并集（按 ITEMS 里 section 首次出现顺序）；空组合显示 `—`，整行为空则跳过。
- 单元格内每个条目渲染为 `<button class="kw-map-item">名字 <span class="kw-item-badge">badge</span></button>`，`onclick="selectItem(group,title)"`。
- 数据/渲染全部走 `GROUPS` + `ITEMS`（现成），**不新增注入键**；所有文案经 `escHtml()/escAttr()`（模板已有 `escAttr`，需补 `escHtml` 或复用 `escAttr` 语义，实施时确认不引 XSS 面）。
- CSS：`#welcomePanel` 在 `#kwMap` 存在时切为 `align-items:stretch; justify-content:flex-start; max-width:1100px; width:100%`；表格 `border-collapse:separate; border-spacing:0`，首列 sticky；深色 `--surface-*` / 强调 `--cobalt-*` 变量（禁硬编码新色）；亮色主题走 `:root.light`。
- 响应式：≤768px 表格横向滚动（`overflow-x:auto`），首列 sticky 保持；条目多时单元格内换行不省略。

### 3.4 统一搜索面板（Spotlight 同构）

DOM（对齐 tool-nav-manager，前缀 `kw` 避免与 table 的 `qs-` 混淆）：

```
#kwSpotOverlay.search-overlay > #kwSpotModal.search-modal
  .search-input-wrapper > 图标 + #kwSpotInput.search-input + #kwSpotClose.search-close-btn
  #kwSpotResults.search-results   (网格 / 分组清单)
  #kwSpotHint.search-hint         (↑↓ 选择 · Enter 打开 · Esc 关闭)
```

- 触发：`⌘/Ctrl+K`（`preventDefault`，幂等 toggle）+ 侧栏 🔍 `#kwSearchBtn`（改造：`toggleKwSpot()` 取代 `toggleKwSearch()`）。**`⌘F` 不再拦截**（删 CL044 的捕获段）。
- 匹配面（`queryKwItems(q)`）：`title` / `section` / `desc` / `page_title` / `group`（组名用小写化 + 去空白比较）；`q` 为空 ⇒ 清单留空 + hint 文案，不展示全量（避免 44 条噪音）。
- 排序：title 前缀命中 > title 包含 > section 命中 > desc/page_title/group 命中；同分按 `group` 顺序、再按组内原序（稳定）。
- 结果项：`名字` + 面包屑 `组 / section` + `badge` +（有 `desc` 时）单行摘要（`text-overflow:ellipsis`）；`<mark>` 高亮命中片段（用**分片拼接 + 转义**，禁止 `innerHTML` 直插原文）。
- 键盘：`↑↓←→` 移动（`.sel`）、`Enter` 打开选中项（无选中则首个）、`Esc` 关、点遮罩关闭；焦点 50ms 后落输入框（同参考件）。
- 无匹配：`.empty-state`「没有匹配的条目」+ 提示「试试点 🔍 或换关键词」。
- 打开面板**不改**侧栏/内容区（纯浮层）；面板关闭后焦点回到 `body`。

### 3.5 侧栏过滤的去留

- `#kwSearchWrap`（侧栏输入框）**移除**；`toggleKwSearch()` / `doKwFilter()` 的函数体保留但仅供面板复用（`doKwFilter` 的「整节隐藏」逻辑在面板不用，标 `/* deprecated: 侧栏过滤已由面板取代 */`）。
- 窄屏补 `.open` 的 `_kwRevealSidebar()`、`_kwHideSidebarOnMobile()` 随侧栏搜索一并删除（面板是全屏浮层，无「输入框在隐藏侧栏里」的问题）。
- 影响：`tests/test_knowledge_sidebar.py::test_09/10/11`（CL044 判据）需改写（§5）。

### 3.6 数据契约 / CLI / 模板键

- **无新增数据键**、**无新增模板键**（复用 `<!--TITLE-->`、`<!--WELCOME_TEXT-->`、`<!--GROUPS-->`、`<!--ITEMS-->`）。
- `html-gen help knowledge` 的键规范段：补一行「根页地图表与搜索面板由模板内建，无新键；`--welcome` 仍只影响根页欢迎语」。
- `TEMPLATE_CONTRACT`：不需改（无新键）；若实施中发现必须新增，按 AGENTS「三面同步」在**同一笔**里改 help/契约/`tests/test_help_contract.py`。

### 3.7 版本与产物

- `__version__ = "3.6"`，`__release_date__ = "2026-11-23"`；README ×2 版本行同步。
- 重渲 4 个 knowledge 产物：`demos/knowledge-demo.html`、`demos/drama-knowledge.html`、`demos/chaitin-business-analysis.html`、`demos/cloudwise-business-analysis.html`；`scripts/baseline.py --update` 后 `--check` 须 50/50。
- 产物戳应为 `html-gen v3.6+tpl<新 sha>`；`--table-fs` / 结构计数不在 knowledge 判据内，无需变。

### 3.8 测试计划（486 → 预计 491）

| 用例 | 断言 |
|:--|:--|
| 改写 `test_09` | `⌘F` **不再**拦截：`defaultPrevented===false`、侧栏过滤面板不被打开 |
| 改写 `test_10` | `⌘K` 打开面板：`#kwSpotOverlay.active`、焦点在 `#kwSpotInput`；连按两次仍 active（幂等）；`Esc` 关闭 |
| 改写 `test_11` | 窄屏不再需要 `.open` 补丁：面板打开时 `#kwSpotModal` 可见且宽度 ≤ 视口 |
| 新 `test_12` | 点条目 → 点 `.sidebar-title` → 根页（`welcomePanel.active`、URL 无 `item`、`localStorage` 已清） |
| 新 `test_13` | `#kwMap table` 列数 = GROUPS+1；格内条目总数 = ITEMS 总数；点格内条目 → `selectItem` 生效 |
| 新 `test_14` | 搜索命中 `desc`（cloudwise 数据 14 条有 desc）：输入 desc 独有词 → 结果 ≥1 且含目标条目；输入正文独有词 → 0 条 |
| 静态守卫（改 `TestTemplateStaticGuards`） | 模板含 `kwGoRoot` / `kwSpotOverlay` / `kw-map-table`；4 个 KB 产物各含同标记；**且** 产物不再含 CL044 的 `e.key !== 'f'` 分支 |
| 变异实验 | ① 把 `kwGoRoot()` 的 `add('active')` 注释掉 ⇒ test_12 必红 ② 把 `⌘K` 的 `preventDefault` 去掉 ⇒ test_10 必红（还原即绿） |

### 3.9 风险与回退

| 风险 | 处置 |
|:--|:--|
| 移除 ⌘F 拦截被看成「功能倒退」 | `features.md` 同批把「⌘F 打开侧栏搜索」行改为「⌘K 打开搜索面板；⌘F 归还浏览器原生查找」，并在 CL044 记录追加「v3.6 由面板取代」 |
| 切页签不再自动选首条，有人依赖「跨组跟随」 | 设计保留 `localStorage` 记忆组；如用户反馈要跟随，再加「同标题跨组跟随」开关（本批不做） |
| 根页表格在窄屏挤 | `overflow-x:auto` + 首列 sticky；AC2 不依赖视觉 |
| 面板 innerHTML 注入 | 所有字段过 `escHtml`，高亮用分片 + 转义；静态守卫加一条「结果渲染走 escHtml」的 grep 断言 |
| 与 table 的 `qs-overlay` 语义分叉 | 本批**只做 knowledge**（用户已采纳）；公共块抽取等第二批 |

## 4. 明确不做

- 不统一 doc / slide 的 TOC 搜索、不改 table 的 `qs-overlay`（含 `?q=` URL 同步）。
- 不做正文全文检索（面板仍只搜「菜单面」：标题/副标题/描述/组名），正文依赖原生 ⌘F。
- 不做搜索词 URL 同步（`?q=`）与搜索结果计数持久化。

## 5. 实施步骤（6 步，每步带验证）

1. 模板改：`kwGoRoot` + 标题点击改绑 + `#kwCopyPathBtn`；验证 `node --check` 逐 script 块。
2. 模板改：`#kwMap` 渲染（CSS + JS）；验证：真机点格内条目跳转、窄屏横滚。
3. 模板改：面板 DOM + `SearchHandler` 同构（含高亮、键盘、空态）；删除 CL044 捕获段与 `#kwSearchWrap`。
4. 测试改写/新增（§3.8）；先跑 `-n 0` 单文件，再做两次变异。
5. 版本 3.6 + 文档三面（`features.md` / `documents/templates.md` / `help` 键规范段）+ 重渲 4 产物 + `baseline --update`。
6. 全量 `pytest -q -n 4`（期望 491）+ `baseline --check` 50/50 + `AGENTS.md` 计数（受保护，需单独授权）→ 提交两笔（源码/产物分离）。

## 6. 行为变更清单（给评审，逐条确认）

| # | 变更 | 影响面 |
|:--|:--|:--|
| B1 | `.sidebar-title` 点击：复制路径 → 回根页 | 复制能力迁到 `#kwCopyPathBtn` |
| B2 | `⌘/Ctrl+F` 不再拦截 | 浏览器原生查找恢复；CL044 判据改写 |
| B3 | 侧栏过滤面板 `#kwSearchWrap` 移除，🔍 改开浮层面板 | `test_09/10/11` 改写 |
| B4 | `switchGroup` 不再自动选首条，一律回根页 | 跨组同名跟随删除 |
| B5 | 根页从「居中欢迎语」变为「欢迎语 + 菜单地图」 | CSS 布局、亮/暗主题各一套 |
