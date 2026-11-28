---
title: html-gen 模板三层与 Markdown 规则
topic: html-gen
type: reference
version: 1.0
date: 2026-11-09
author: ops
source: AGENTS.md 外移（HTML-GEN-CL023）
---

# html-gen 模板三层与 Markdown 规则

> 由 `AGENTS.md` 外移（HTML-GEN-CL023）：细则只在本文件维护，`AGENTS.md` 只留指针，两处不重复同一段文本。

## 模板注入机制

- 模板使用 `<!--KEY-->` 占位符，CLI 通过 `inject()` 函数替换
- CSS 在生成时内联：替换 `<link rel="stylesheet" href="style-guide.css">` 为 `<style>...</style>`
- 输出为自包含单文件 HTML，无外部依赖

## 模板类型详解

### layout-doc.html（B 型文档）
- 左侧粘性侧边栏 + 右侧内容区
- 自动生成 TOC（h2/h3），实时高亮当前章节
- TOC 搜索（🔍 按钮，150ms debounce，≥2 字符触发过滤）
- **Bare 模式 / 正文宽度三级 / md 路径行**：URL 状态键与取值口径见 `html-gen help doc` 的「URL 状态」段（默认展示侧边栏/工具栏，URL 参数显式隐藏；宽度窄/中/宽默认 960px 不持久化；md 路径行默认 CSS 隐藏，basename 脱敏）
- 折叠/展开侧边栏（48px 收起态，`[` 快捷键）
- 侧边栏宽度拖拽（200-400px，localStorage 持久化）
- H3 子项开关，中/英双语，🌙/☀️ 主题切换
- 标题点击复制路径（textContent 获取 meta 路径，脱敏文件名）
- 代码复制（剪贴板 + fallback）、行号、Callout 提示框、阅读进度条、图片灯箱

### layout-table.html（A 型表格）
- **键规范**（列类型 6 / 列属性 22 / Tab 6 / 选项 16 / options.feedback 5 / actions 7 / videos 5 / URL 状态 3 / CLI 参数 9）见 `html-gen help table` 的键规范段（单一事实源：`TEMPLATE_CONTRACT['table']`，由 `tests/test_help_contract.py` 双向守卫）
- **页面级段落描述**：`--subtitle` / JSON 顶层 `subtitle`（优先级 CLI > JSON），h1 下方段落区，纯文本安全转义 + `\n` → `<br>`，显式传空串清空；无 subtitle 不渲染
- **Cinema 纪律化宽度模型**：`table-layout:fixed`，每列强制显式 width（默认 120px，actions 100px），无 colgroup，td `max-width:0` 强制截断
- 实时搜索（300ms debounce）+ Cmd+F Spotlight 弹窗搜索
- 多字段排序（Shift+点击二级排序），数字/中文 locale 排序
- 客户端分页（默认 30 条/页，可配置）
- **密度切换**：紧凑(28px) / 标准(34px) / 舒适(42px)，设置面板横向展示
- **五种点击模式**（由选项控制）：
  - 🔗 新标签页：`window.open(url, '_blank', 'noopener,noreferrer')`
  - 📋 弹出面板：居中 overlay，键值列表（textContent 安全渲染）；支持自定义渲染器（`options.modalRenderer: 'skills'`）
  - 📑 分栏预览：表格 + 预览并排，拖拽分栏线，比例预设 (▦)，▲▼ 导航；支持 SKILL.md 加载
  - 📂 行内展开：手风琴模式，点击展开详情网格
  - 🎯 单元格点击：`col.onCellClick: 'split'` 直接打开分栏
- **快速过滤**：点击单元格值 → 筛选该列该值的行，filter pill 可关闭；列属性启用（默认关，键名见 help）
- **列冻结**：sticky 列，动态计算 left 偏移（基于该列 width 配置）
- **右侧固定列**：水平滚动时保持在视口右侧
- **媒体列**（CL026）：`type: 'image'`（值为图片 URL 或 `{src|alt}`，单元格出缩略图、点击灯箱放大，分栏详情出大图；`src` 仅放行 http(s)/file/data:image(png|jpeg|gif|webp|svg+xml)，其余伪协议不渲染）与 `videos` 项可选 `cover`（有封面时单元格/分栏先出封面图，点击外链到该视频）。缩略图高度随密度走（紧凑 18 / 标准 22 / 舒适 30px），不撑行。
  - CL028 加固：外链**目标**另有过一道白名单 `linkSafe`（只放行 http(s)）—— `video.url` 非 http(s) 时 pill / 封面 / 分栏链接都降级为纯文本，不产生可点击面（`noopener` 已挡同源 XSS，这条是纵深）。
  - CL028 文本口径：搜索/排序/quickFilter/CSV 统一走 `cellTextFor`（媒体类型取 `mediaTextValue`）。**行为差异**：`0` / `false` 这类假值过去被 `String(row[k] || '')` 折成空串，现在按原值参与筛选与导出（更正确，但若旧页面依赖「0 视为空」需显式处理）。
  - CL030 加固：外链白名单同口径延伸到 `actions.hrefKey` 与 `clickMode: 'tab'` 的行级 `row.url`（非法目标渲染 `action-btn-disabled` 不可点按钮 / 行点击直接 no-op）；属性上下文一律用 `escapeHtmlAttr`（`title` 曾用 `escapeHtml`，双引号不转义 ⇒ 可注入事件属性）；`onclick` 的 JSON 注入走 `jsAttr`（单引号属性内 `'` 也转义）。
- **分栏详情跨列与空值**（CL025）：列属性 `splitSpan` = `"full"`（整行，旧 `splitFull` 等价）或正整数 N（`grid-column:span N`，上限 6；数字与数字字符串 `"2"` 等价）；选项 `hideEmptyCells: true` 时空值字段整格不渲染、剩余格自动重排（缺省 false 保持全列，向后兼容）。
- **分栏详情声明式行布局**（CL031）：选项 `options.splitGrid = { grid, hide, skipEmpty }`。`grid` 是「行数组的数组」，格元素三态：`"key"` / `{key, span: "full"|N}` / `"*"`（catch-all，只认最后一个，展开为「未显式引用 + 未 hide」的列，展开集为空则该行**零节点不留空轨**）。JS 逐格写 `grid-row` / `grid-column`（`display:contents` 不产生行边界，见 `documents/solutions/table-split-grid-design-v1.0-20261109.md` §3）；轨道数 = 各行 span 之和的最大值。`hide` 里的列保留数据但不渲染；`skipEmpty` 缺省继承 `hideEmptyCells`。**不写该键 ⇒ 走原扁平 auto-fill，行为不变**；`splitSpan`/`splitFull` 在 `splitGrid` 存在时让位，`preview`/`columnsSplit` 属表格侧、与它零交叉。
  - `span: "full"`（CL033 起）：该行**唯一格** ⇒ 占满整行（`1 / -1`）；行内**还有兄弟格** ⇒ 只吃「本行剩余轨」——先扣掉其后兄弟格所需轨，其余填满（不做隐式换行，`grid` 行数与视觉行数保持 1:1）。「剩余轨」的基准是 `maxCols`（= 各行 span 之和的最大值，写在容器 `--kv-cols` 上），不是本行 span 之和 ⇒ 短行里的 full 会一直填到整行宽度。CL031 时恒写 `1 / -1`，会让行中/行首的 full 盖住同行兄弟格且无任何提示。
  - 逐格 `grid-row` 属**意图显式**（抗未来 `grid-auto-flow` 变动）：当前行首恒落第 1 轨 + CSS 稀疏自动流的排布结果与仅写 `grid-column` 一致 ⇒ 删掉 `grid-row` 是**等价变异**（`test_01b` 只守「短行不吸收下一行」的结果，不构成它的判别力，评审已复核）。
- **分栏模式列过滤**：标记为「分栏可见」的列显示于分栏表格；可用选项显式指定分栏列集
- **列隐藏双语义**：「永不可见」vs「默认收起·可开启·分栏仍全列」—— 语义与键名对照见 `html-gen help table`
- **快捷键**：↑↓ 键盘导航行，Enter 点击，F 全屏
- **批量操作**：选中行出现工具栏（全选/取消/导出 CSV）
- **URL 状态分享**（CL004/CL005/CL036）：`?tab&q&split&density` 参数 replaceState 同步 + 加载恢复（tab 白名单 / split 越界忽略 / q 仅 input.value / density 白名单）；**分享/Home 按钮自 CL036 起落在 `.table-header` 内、紧跟统计 pill**（原为 tabs 行居右 `.tabs-actions`，单视图页会退化成「只有按钮的一行」）：🔗 拷贝含视图的分享链接（clipboard + execCommand fallback）+ 🏠 home 入口（`--home-url` 注入，同容器 36px 圆角深底）；`.tabs-row` 在无 tab 且 `.tabs-actions` 为空时挂 `no-tabs` 整行折叠（**只 CSS 隐藏，DOM 必须保留**：跨仓 `normalize_skeleton` 会往 `.tabs-actions` 搬 ▦/⚙ 控件）；排序/quickFilter 变化自动 closeSplit
- **密度三档 + 字号变量**（CL036）：字号收口到 `--table-fs`（`:root` 默认 0.82rem），三档只改变量与内边距 —— `default` 0.82rem / 8px 10px、`compact` 0.7rem / 2px 8px、`comfortable` 0.94rem / 12px 14px；`th` = `calc(var(--table-fs)*0.88)`、`.cell-pill`/`.video-pill` = `*0.86`、`.stat-pill` = `*0.8` 联动。来源优先级：`?density=` > localStorage（用户显式选过）> `options.density` > `default`；⚙ 面板的密度入口**始终渲染**（原先 `tabCount>1 || density!=='default'` 会把单视图页入口整段藏掉）
- **视图预设**：保存/加载/删除设置（密度/模式/排序/列可见性，最多 10 个，≤2KB）
- 列名从 JSON 首条 key 自动推导
- 支持单元格 HTML（`<a>`、`<code>` 等）
- 支持操作按钮列（复制字段值 / 打开链接 / 描述兜底 / 自定义 handler 四种模式）、多标签页、CSV 导出
- `handler` 模式：自定义 JS 函数名，由模板 `window.{handler}(event, row)` 调用
- 列可见性 / 列宽度 localStorage 持久化（`html-gen:table:col-visibility` / `html-gen:table:col-widths`），拖拽 resize 直接操作 DOM
- 列宽拖拽可禁用（选项关闭）
- 设置面板：⚙️ 下拉，密度/点击模式/列可见性/视图预设，内部点击不关闭，✕ 关闭按钮
- `printColWidths()` 控制台调试函数
- 安全：`copyAction()` 含 execCommand fallback（headless Chrome 兼容）
- **Videos 视频列**：行字段为对象数组 `[{url,title,duration,platform}]`，每视频一个 pill（图标+标题+时长）；`col.videos.maxShow` 折叠 "+N" 点击展开（不折叠回，re-render 重置）；平台图标映射 douyin/抖音🎵 bilibili/B站/b站📺 youtube▶️ 其他📹；pill 点击新标签页（noopener,noreferrer）；默认搜索排除 videos；split/expand 数组特判渲染

### layout-knowledge.html（C 型知识库）
- **键规范**（点击模式 3 / item 9 / groups 3 / 数据源与输出目标 / CLI 参数 10）见 `html-gen help knowledge` 的键规范段（单一事实源：`TEMPLATE_CONTRACT['knowledge']`）
- 顶部横向标签栏（按 group 分组），与侧边栏标题行对齐
- 左侧章节列表（按 section 分组，badge 标记显式）；条目文本单行 `ellipsis`（侧栏 260px，约容 24 列），全名走 `title` 属性悬停提示：取 `item.page_title` → 回退 `item.title`
- 搜索面板（`⌘/Ctrl+K` 或 🔍 按钮 → 浮层 Spotlight：默认输入框 + 输入即匹配清单，`↑↓←→` 选择、`Enter` 打开、
  `Esc`/外点关闭、`<mark>` 命中高亮、无匹配空态；匹配面 = 条目标题 `title` / 副标题 `section` / 描述 `desc` /
  全名 `page_title` / 分组，**不含 `url` 与正文**）。面板 DOM 与 script-miner `tool-nav-manager` 的 Spotlight 同构
- `⌘F` / `Ctrl+F` **不拦截**：浏览器原生查找照旧可用（v3.6 起，撤销 v3.5 的捕获阶段拦截）
- 根页（`#welcomePanel`）：标题 + 欢迎语（`--welcome`）+ 徽章图例 + **菜单地图表**（列 = 横向页签，行 = `section`，
  格内条目名 + badge，点击直达该条目）；点侧栏标题 `.sidebar-title` 回根页，复制路径走标题右侧 ⧉ 按钮
- 页签切换只切类目并回根页（v3.6 起不再自动选中该组首条）
- **嵌入降级**：条目带 `url` 时以 iframe 加载详情页，并在该 URL 追加 `sidebar=0&toolbar=0` 使其进入 Bare 模式（知识库页自身无 sidebar/toolbar URL 状态；键口径见 `html-gen help doc` 的「URL 状态」段）
- 折叠/展开侧边栏（48px 收起态，`[` 快捷键）
- 双内容模式：条目带详情页地址 → iframe 加载；带正文 HTML → 内联渲染（键名见 `html-gen help knowledge`）
- section 标题可点击：单条目 section 点击标题直接加载 (K2)
- 根页（未选条目时的落点）：欢迎语 + 菜单地图表（列 = 页签 / 行 = section / 点格内条目直达）
- 上次选择状态 localStorage 恢复（group + item）；`?view=root` 强制回根页

## 影响面矩阵（改模板能力必查）

> **单源权威**：本节是全仓唯一的「改了模板要连带改哪里」清单；`demos/*-guide.md` 只放本模板的 8 行摘要并指回本节。
> 触发条件：新增/改名模板键、改交互行为（快捷键、根页、搜索、状态恢复）、改公共 CSS 变量或结构、升版本号。

| 面 | 落点（本仓路径） | 判据命令 |
|:---|:---|:---|
| **指令面** | `html-gen.py` 的 `TEMPLATE_CONTRACT['<theme>']`（键名/默认值）+ `html-gen help <theme>` 渲染 | `python3 html-gen.py help <theme>`；`pytest tests/test_help_contract.py -q` |
| **Skills 面** | `skills/html-gen-<theme>/SKILL.md`（模板专篇）+ `skills/html-gen/SKILL.md`（总入口 C/B/A/D 段与变更记录） | `python3 html-gen.py prompt html-gen-<theme> \| grep -c '<新能力关键词>'` |
| **文档面** | `demos/<theme>-guide.md`（→ 同名 `.html`）+ `documents/templates.md`（本文件）+ `features.md` | `grep -c '<新能力关键词>' demos/<theme>-guide.md`；四份 guide 标题话术 `<名称>（模板X）` |
| **案例面** | `demos/<theme>-demo.html` + `data/_*data.json`（数据/条目）+ `data/_demos-data.json`（demos-index 卡片话术） | `python3 html-gen.py demo --rebuild`；卡片话术计数（`🗂/📄/📚`） |
| **测试面** | `tests/test_help_contract.py`（键名⇄契约）、`tests/test_templates.py`（静态守卫）、`tests/test_<theme>*.py`（Selenium） | `pytest tests/test_help_contract.py tests/test_templates.py tests/test_<theme>*.py -q` |
| **基线/门禁面** | `scripts/baseline.py`（`TABLE_PRODUCTS` / `DOC_PRODUCTS` / `SLIDE_PRODUCTS` / `KB_PRODUCTS`）+ `data/_render-baseline.json` + `documents/docs-index.md` | `python3 scripts/baseline.py --update` → `--check`（50/50）→ `--verify`；`hm-docs-index.py --root . --check` |
| **打包面** | `src/html_gen/{layout-<theme>.html, html-gen.py, style-guide.css, skills/*}`（pip 包源） | `python3 scripts/build-package.py`；`tests/test_baseline_gate.py` 的打包源 sha 守卫 |
| **跨仓/发布面** | script-miner `skills/html-templates/layout-<theme>.html`（+ `efficiency/tests/test_html_templates_vendor.py`、`projects-manager.py:VENDORED_FILES`）；hermes-manager 对应页；版本三件 `__version__` / `README.md` / `README.zh.md` / `AGENTS.md` 计数 | 各仓自家 `--check`；`grep -c "e.key !== 'f'"` 等旧标记归零 |

**标准流程（按依赖顺序，1→8）**

1. `TEMPLATE_CONTRACT` 与 `html-gen help <theme>`（先定键名/默认值）
2. `layout-<theme>.html` 行为与样式
3. `skills/html-gen-<theme>/SKILL.md` + `skills/html-gen/SKILL.md`
4. `demos/<theme>-guide.md` + 本文件 + `features.md`
5. `data/_*data.json` + `_demos-data.json` 话术 + 重渲 `<theme>-demo`
6. 测试三面：契约 / 静态守卫 / Selenium
7. 产物重渲 → `baseline --update` → `--check` 49/49 → `--verify` → `docs-index` 重生成
8. `build-package.py`（打包源）→ 跨仓 vendored/页面 → 版本三件与测试计数

> 反例（CL047，2026-11-23）：模板改完只走了 1/2/6/7，**漏了 3、5、8**（`skills/*` 未更新、`prompts/index.html` 仍 v3.4、`src/html_gen` 打包源仍 v3.5），靠事后全量扫描才发现。本节即为堵这个洞而设。

## Markdown → HTML 转换规则

`md_to_html()` 在 `html-gen.py` 中实现，零依赖纯 Python：
- h1–h6 标题（自动加 id 锚点，h4-h6 不入 TOC）
- `**加粗**`、`*斜体*`、`==高亮==`（→ `<mark class="hl">`）、`` `代码` ``、`[链接](url)`
- 围栏代码块（支持变长 fence 嵌套）
- 表格（Markdown pipe table）
- 无序/有序列表（连续自动合并为 `<ul>`）
- Callout：`> **Note/Warning/Tip/Danger/注意/警告/提示/危险**：内容`
- 分隔线 `---`、引用 `> 文字`
- 不解析图片（安全限制）
