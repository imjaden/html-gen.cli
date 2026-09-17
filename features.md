# features.md — html-gen 功能清单

> IRIS v1.0 格式。每行 `{功能描述} {状态标记} — {关联文档/产出}`
>
> **键规范单一事实源**: 数据契约键（列属性 / 列类型 / options / Tab / actions / videos / item /
> groups / 数据源 / URL 状态 / CLI 参数）**只在** `html-gen help <type>`（实现: `html-gen.py` 的
> `TEMPLATE_CONTRACT`）中枚举。本文档记录**能力与输入形态**，不再复制键表 —— 复制即漂移（CL013 起因）。

## CLI 命令

### 主命令组 (html-gen CLI)
html-gen doc — Markdown 转 B 型文档 (frontmatter 自动剥离) ✅ — layout-doc.html
html-gen doc --metadata / --title / --subtitle — 页面标题与元信息 ✅ — html-gen help doc
html-gen slide — Markdown 转 D 型幻灯片 (h2 分页) ✅ — layout-slide.html
html-gen table — JSON 转 A 型数据表格 ✅ — layout-table.html
html-gen table --feedback-repo — GitHub Issue 反馈通道开关 (table 专属, 默认不注入) ✅ — html-gen help table
html-gen prompt github-issue-feedback — GitHub Issue 反馈通道接入规范 skill (跨项目复用: 表单/配置/脚本/安全红线) ✅ — skills/github-issue-feedback/SKILL.md
html-gen knowledge — JSON 转 C 型知识库 (类目自动推导 / --groups 覆盖) ✅ — layout-knowledge.html
html-gen help — 显示帮助 ✅ — html-gen.py
html-gen help <topic> — 按主题显示帮助 (doc/slide/table/knowledge/prompt/demo) ✅ — html-gen.py
**CLI 参数 (四渲染子命令)** — 长形 flag 清单 / 默认值 / env 兜底 / 「显式空串禁用」约定 ✅ — `html-gen help <type>` 的「CLI 参数」段

### 脚本工具
scripts/company-report.py — 公司调研报告生成器 (schema → C 型知识库) ✅ — scripts/company-research-schema.json

---

## 模板功能

### layout-doc.html (B 型文档) — 448 行
自动 TOC 生成 (h2/h3 锚点 + 滚动高亮) ✅ — layout-doc.html
TOC 搜索 (🔍 按钮, 150ms debounce, ≥2 字符过滤) ✅ — layout-doc.html
侧边栏 sticky 修复 (桌面 sticky, mobile fixed) ✅ — layout-doc.html
Bare 模式 (默认展示侧边栏/工具栏, URL 参数显式隐藏, 知识库嵌入降级) ✅ — layout-doc.html
正文宽度三级 (窄/中/宽, 默认 960px; URL 状态键见 help) ✅ — layout-doc.html
md 源路径行 (URL 参数开启时显示, 默认隐藏, basename 脱敏) ✅ — layout-doc.html
侧边栏折叠/展开 (48px 收起态, `[` 快捷键) ✅ — layout-doc.html
侧边栏按键分离 (`[` 折叠 / `]` 展开, 输入框豁免) ✅ — layout-doc.html
侧边栏宽度拖拽 (200-400px, localStorage 持久化) ✅ — layout-doc.html
侧边栏标题点击复制路径 (textContent 安全获取) ✅ — layout-doc.html
H3 子项开关 (显示/隐藏 TOC 中 h3 条目) ✅ — layout-doc.html
中/英双语界面切换 (🇨🇳/🇺🇸) ✅ — layout-doc.html
🌙/☀️ 深色/浅色主题切换 (20+ 组件覆盖) ✅ — layout-doc.html
代码块复制按钮 (剪贴板 API + fallback execCommand) ✅ — layout-doc.html
代码行号 (Counter CSS) ✅ — layout-doc.html
Callout 提示框 (Note/Tip/Warning/Danger / 注意/警告/提示/危险) ✅ — layout-doc.html
Markdown pipe table 渲染 ✅ — layout-doc.html
阅读进度条 (顶部 2px cobalt 线) ✅ — layout-doc.html
图片灯箱 (点击放大, Esc 关闭) ✅ — layout-doc.html
Section anchor link (¶ 复制) ✅ — layout-doc.html

### layout-slide.html (D 型幻灯片) — 685 行
交互行为清单 (分页/导航/全屏/进度点/记忆/侧栏 H3 开关/侧栏关键字过滤/性能警告) ✅ — html-gen help slide
h2 分页 (每页一个 h2 section) ✅ — layout-slide.html
H3 双列模式 (h2 下 ≥2 个 h3 → 并排列) ✅ — layout-slide.html
H3 单列回退 (仅 1 个 h3 → 全宽) ✅ — layout-slide.html
封面页 (标题 + 副标题 + 元数据) ✅ — layout-slide.html
底部导航点 (点击跳转页面) ✅ — layout-slide.html
自动 TOC 生成 (h2 条目, 页面跳转) ✅ — layout-slide.html
TOC 搜索 (🔍 按钮, 150ms debounce, ≥2 字符过滤) ✅ — layout-slide.html
侧边栏 sticky 修复 (桌面 sticky) ✅ — layout-slide.html
侧边栏折叠/展开 (48px 收起态, `[`/`]` 按键) ✅ — layout-slide.html
侧边栏按键分离 (`[` 折叠 / `]` 展开) ✅ — layout-slide.html
侧边栏宽度拖拽 (200-400px, localStorage 持久化) ✅ — layout-slide.html
侧边栏标题点击复制路径 (textContent + URL 白名单) ✅ — layout-slide.html
页码实时更新 (封面 "共 N 页"/内容页 "M / N", 中英双语) ✅ — layout-slide.html
H3 子项开关 (localStorage 记忆, 载入恢复) ✅ — layout-slide.html
中/英双语界面切换 (🇨🇳/🇺🇸) ✅ — layout-slide.html
🌙/☀️ 深色/浅色主题切换 ✅ — layout-slide.html
右上角工具栏 (语言/主题, glass-morphism) ✅ — layout-slide.html
键盘翻页 (← → PageUp PageDown Home End) ✅ — layout-slide.html

### layout-table.html (A 型表格) — 1440 行
键规范 (列类型 6 / 列属性 22 / Tab 6 / options 13 / feedback 5 / actions 7 / videos 5 / URL 状态 3 / CLI 9) ✅ — html-gen help table
实时搜索 (300ms debounce) ✅ — layout-table.html
Cmd+F Spotlight 弹窗搜索 (匹配计数, 实时同步) ✅ — layout-table.html
多字段排序 (locale/数字/日期/字符串, Shift+点击二级排序) ✅ — layout-table.html
客户端分页 (默认 30 条/页, 页大小可配) ✅ — layout-table.html
密度切换 (紧凑 28px / 标准 34px / 舒适 42px, localStorage) ✅ — layout-table.html
弹出面板模式 (Modal overlay, 键值列表, Esc 关闭, textContent) ✅ — layout-table.html
分栏预览模式 (表格 40% + 预览 60%, 拖拽分栏线 25-75%) ✅ — layout-table.html
行内展开模式 (手风琴, 点击展开详情网格, colspan 全宽) ✅ — layout-table.html
新标签页打开模式 (window.open + noopener,noreferrer) ✅ — layout-table.html
点击模式 (可配置模式列表, 兼容单数写法) ✅ — layout-table.html
快速过滤 (默认关, 列属性启用, filter pill ✕ 关闭) ✅ — layout-table.html
列冻结 (sticky 列, 自动 left 偏移) ✅ — layout-table.html
分栏模式列过滤 (仅预览列显示) ✅ — layout-table.html
列隐藏双语义 (默认收起·面板可开启 vs 永不可见; 键名与语义差异见 help) ✅ — html-gen help table
列可见性切换 (⚙️ 下拉面板, 复选框) ✅ — layout-table.html
列宽拖拽 (resize handle, 最小 40px, localStorage 持久化, 可禁用) ✅ — layout-table.html
多标签页 (按字段/精确值/包含匹配过滤, localStorage 记忆) ✅ — layout-table.html
操作按钮列 (复制字段 / 打开链接 / 描述 / 自定义 handler 四种模式) ✅ — layout-table.html
列可见性 localStorage 持久化 (html-gen:table:col-visibility) ✅ — layout-table.html
列宽度 localStorage 持久化 (html-gen:table:col-widths) ✅ — layout-table.html
CSV 导出 (全部 / 选中行, BOM UTF-8) ✅ — layout-table.html
批量操作工具栏 (全选/取消/导出选中, 选中行数显式) ✅ — layout-table.html
键盘导航 (↑↓ 移动焦点, Enter 点击行, 自动滚动) ✅ — layout-table.html
全屏模式 (⛶ 按钮 / F 键, wrapper.fullscreen) ✅ — layout-table.html
分栏比例预设 (▦ 下拉: 100%/3:7/4:6/5:5/6:4, localStorage) ✅ — layout-table.html
分栏面板导航 (▲▼ 按钮切换上/下一条) ✅ — layout-table.html
视图预设 (保存/加载/删除, 最多 10 个, ≤2KB, localStorage) ✅ — layout-table.html
行选择复选框 (rowSelect, select-all) ✅ — layout-table.html
统计面板 (总数/筛选数/选中数 pill) ✅ — layout-table.html
Toast 通知 (2.5s 自动消失) ✅ — layout-table.html
HTML 转义 (escapeHtml, 默认转义, textContent 安全渲染) ✅ — layout-table.html
iframe sandbox (allow-same-origin, 无脚本) ✅ — layout-table.html
URL 白名单校验 (https?/ / ~/ 前缀) ✅ — layout-table.html
Cinema 纪律化宽度 (table-layout:fixed, 每列显式 width, td max-width:0, 无 colgroup) ✅ — layout-table.html
Pills 标签列 (逗号分隔→tag pills, 标签筛选默认开可关) ✅ — layout-table.html
Videos 视频列 (行值对象数组: 地址/标题/时长/平台, 折叠 +N 点击展开, 平台图标映射 douyin🎵/bilibili📺/youtube▶️, 点击新标签页 noopener,noreferrer, 默认搜索排除) ✅ — layout-table.html
Datetime 排序 (日期列专用, Date.parse 比较) ✅ — layout-table.html
右侧固定列 (position:sticky) ✅ — layout-table.html
分栏列过滤增强 (分栏列集 + 预览列 fallback) ✅ — layout-table.html
单元格点击分栏 (列属性配置) ✅ — layout-table.html
列宽拖拽禁用 (选项关闭) ✅ — layout-table.html
自定义模态框渲染器 (skills 结构化详情) ✅ — layout-table.html
SKILL.md 加载 (split 面板 fetch + 简单 Markdown 渲染) ✅ — layout-table.html
设置面板 UX (密度横向/内部点击不关闭/✕关闭按钮) ✅ — layout-table.html
printColWidths() 调试函数 ✅ — layout-table.html
copyAction() clipboard fallback (execCommand, headless Chrome 兼容) ✅ — layout-table.html

### layout-knowledge.html (C 型知识库) — 477 行
条目 / 类目键规范 (item 7 / groups 3) ✅ — html-gen help knowledge
顶部横向标签栏 (按 group 分组, 彩色圆点, 与侧边栏标题行对齐) ✅ — layout-knowledge.html
左侧章节列表 (按 section 分组, badge 标记) ✅ — layout-knowledge.html
侧边栏搜索 (🔍 按钮, 150ms debounce, ≥2 字符, section 自动隐藏) ✅ — layout-knowledge.html
侧边栏折叠/展开 (48px 收起态, `[` 快捷键, 图标点击展开) ✅ — layout-knowledge.html
侧边栏宽度拖拽 (200-400px, localStorage 持久化) ✅ — layout-knowledge.html
侧边栏标题点击复制路径 (textContent + URL 白名单 + Toast) ✅ — layout-knowledge.html
中英双语 (🇨🇳/🇺🇸, 条目数 i18n) ✅ — layout-knowledge.html
🌙/☀️ 深色/浅色主题切换 (18+ 组件覆盖) ✅ — layout-knowledge.html
右上角工具栏 (语言/主题, glass-morphism) ✅ — layout-knowledge.html
iframe 内容加载 (条目 url 字段 → sandbox iframe) ✅ — layout-knowledge.html
内联内容渲染 (条目 desc 字段 → textContent) ✅ — layout-knowledge.html
欢迎面板 (首次加载 / 无选中, 类目图例) ✅ — layout-knowledge.html
选中状态 localStorage 恢复 (group + item) ✅ — layout-knowledge.html
Badge 彩色标记 (知道/理解/能讲/能输出, 4 色方案) ✅ — layout-knowledge.html

---

## 数据格式

> 键规范**只在** `html-gen help <type>`（实现: `html-gen.py` 的 `TEMPLATE_CONTRACT`）；
> 本节只记输入形态 —— 键表复制即漂移（CL013 起因）。

### table 输入
键规范段 (顶层键 / 列类型 / 列属性 / Tab 属性 / 选项 / options.feedback / actions[] / videos / URL 状态 / CLI 参数) ✅ — html-gen help table
简单 JSON 数组 (向后兼容, 列名自首条推导) ✅ — html-gen.py (cmd_table)
结构化 JSON 对象 (columns/data/tabs/options + 顶层 title/subtitle/output) ✅ — html-gen.py (cmd_table)
输出目标三态 (CLI -o > JSON 顶层 output > 中断 exit 1) ✅ — html-gen.py (cmd_table, CL003)

### knowledge 输入
键规范段 (item / groups / 数据源与输出目标 / CLI 参数) ✅ — html-gen help knowledge
数组 或 `{items|data}` 结构化对象 (条目键见 help) ✅ — layout-knowledge.html
groups JSON (类目定义, 键见 help) ✅ — layout-knowledge.html
输出目标三态 (CLI -o > JSON 顶层 output > 中断 exit 1; 仅 data 文件识别) ✅ — html-gen.py (cmd_knowledge, CL003)

### doc/slide 输入
键规范段 (doc: URL 状态 + CLI 参数; slide: 交互行为 + CLI 参数) ✅ — html-gen help doc / html-gen help slide
Markdown 文件 (.md) ✅ — html-gen.py (cmd_doc/cmd_slide)
Markdown 语法子集 (块级/行内/Callout/不支持项) ✅ — html-gen help doc
Markdown 预处理 (h3 标记、页码移除, 生成预处理器副本) ✅ — html-gen.py

---

## 基础设施

### CSS 基座
style-guide.css (--cobalt-* 色系深色主题, CSS 变量) ✅ — style-guide.css
:root.light 浅色主题 (20+ 组件覆盖) ✅ — layout-*.html

### 模板注入
inject() 函数 (<!--KEY--> 占位符替换) ✅ — html-gen.py
inline_style() (CSS link → <style> 内联) ✅ — html-gen.py
_SCRIPT_KEYS (</ 转义, 防 XSS) ✅ — html-gen.py
自包含单文件输出 (零外部资源引用) ✅ — html-gen.py

### 帮助契约
TEMPLATE_CONTRACT — 四模板键规范单一事实源 (数据契约 + CLI 参数 + URL 状态 + 交互行为) ✅ — html-gen.py
render_help() / render_help_spec() — help 由契约渲染 (三段式: ②示例 / ③说明 / ①键规范) ✅ — html-gen.py
test_help_contract.py — 契约 ⇄ 模板消费 ⇄ help 渲染 三维双向守卫 + 变异自证 ✅ — tests/test_help_contract.py
未知键 stderr 提示 (table: 列属性/列类型/选项/反馈子键; 不阻断) ✅ — html-gen.py (cmd_table)

### 安全
escapeHtml (div.textContent 渲染) ✅ — layout-table.html
URL 白名单 (https?/ / ~/) ✅ — layout-doc.html/layout-slide.html
iframe sandbox (allow-same-origin, 无脚本) ✅ — layout-table.html
window.open noopener,noreferrer ✅ — layout-table.html
textContent 渲染 (desc 绝不用 innerHTML) ✅ — layout-table.html/layout-knowledge.html
clipboard API try/catch fallback ✅ — layout-table.html
localStorage try/catch + 类型校验 ✅ — layout-*.html
path traversal 校验 (_safe_path) ✅ — scripts/company-report.py
script 上下文 </ 转义 (inject) ✅ — html-gen.py

### 测试
test_help_contract.py (22 个: 契约结构/双向闭合/白名单纪律/CLI 参数/模板维度/变异) ✅ — tests/test_help_contract.py
test_templates.py (doc/slide/table/knowledge 回归) ✅ — tests/test_templates.py
pytest 全量绿 ✅ — CI/提交前置（计数见 AGENTS.md 测试治理节）

---

## localStorage 命名空间

| Key | 用途 | 模板 |
|:---|:---|:---|
| `html-gen:doc_lang` | 语言 (zh/en) | doc |
| `html-gen:doc_theme` | 主题 (dark/light) | doc |
| `html-gen:doc:h3-visible` | H3 开关 | doc |
| `html-gen:doc:sidebar-collapsed` | 侧边栏折叠 | doc |
| `html-gen:doc:sidebar-width` | 侧边栏宽度 | doc |
| `html-gen:layoutslide_lang` | 语言 (zh/en) | slide |
| `html-gen:layoutslide_theme` | 主题 (dark/light) | slide |
| `html-gen:layoutslide_page` | 阅读位置 (当前页) | slide |
| `html-gen:layoutslide:h3-visible` | H3 开关 | slide |
| `html-gen:sidebar:collapsed` | 侧边栏折叠 | slide |
| `html-gen:slide:sidebar-width` | 侧边栏宽度 | slide |
| `html-gen:kw_group` | 当前 Tab 类目 | knowledge |
| `html-gen:kw_item` | 当前选中条目 | knowledge |
| `html-gen:kw:collapsed` | 侧边栏折叠 | knowledge |
| `html-gen:kw_lang` | 语言 (zh/en) | knowledge |
| `html-gen:kw_theme` | 主题 (dark/light) | knowledge |
| `html-gen:kw:sidebar-width` | 侧边栏宽度 | knowledge |
| `html-gen:table:density` | 密度 (default/compact/comfortable) | table |
| `html-gen:table:click-mode` | 点击模式 (tab/modal/split/expand) | table |
| `html-gen:table:col-visibility` | 列可见性 (JSON) | table |
| `html-gen:table:col-widths` | 列宽度 (JSON) | table |
| `html-gen:table:split-ratio` | 分栏比例 (25-75) | table |
| `html-gen:table:presets` | 视图预设 (JSON array, max 10) | table |
| `html-gen:table:tab` | Tab 选择 | table |

---

## 项目统计

| 指标 | 数值 |
|:---|---:|
| Python 文件 | 5 (html-gen / company-report / countries-issue-sync / test×2；行数见 AGENTS.md) |
| 模板文件 | 4 (doc 444行 / slide 681行 / table 1143行 / knowledge 342行) |
| CSS 基座 | 1 (style-guide.css) |
| 数据文件 | 7 |
| Demo 文件 | 56 (registry: 21 独立 + 35 引用子页) |
| 设计文档 | 4 |
| 测试用例 | 见 AGENTS.md「测试治理」节 (唯一计数源; 此处不再复制) |
| CLI 子命令 | 7 (doc/slide/table/knowledge/prompt/demo/help) |
| CLI 长形参数 | 36 (table 9 / doc 9 / slide 8 / knowledge 10; 见 `html-gen help <type>`) |
| localStorage keys | 24 |
| 数据卡 metrics | company-report content 页自动生成（6 卡模式） |
| GitHub Corner | demo 页右上角双层可点区防遮挡；根落地页全图标可点 + hover 波浪动画 |
| 零外部依赖 | ✅ (Python stdlib only) |
