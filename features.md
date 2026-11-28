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
scripts/baseline.py — 渲染基线门禁 (模板源码 + 产物 sha256 + 参数存在性钉子) ✅
scripts/backfill-table-json.py — 产物 → 数据源回填 (columns/data + 字段级差异 + legacy 保全) ✅

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
代码块复制按钮 (canonical copyText: isSecureContext 前置 + execCommand('copy') 回退 + 返回值检查) ✅ — layout-doc.html
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

### layout-table.html (A 型表格) — 1751 行
键规范 (列类型 6 / 列属性 22 / Tab 6 / options 16 / feedback 5 / actions 7 / videos 5 / URL 状态 3 / CLI 9) ✅ — html-gen help table
实时搜索 (300ms debounce) ✅ — layout-table.html
Cmd+F Spotlight 弹窗搜索 (匹配计数, 实时同步) ✅ — layout-table.html
Cmd+F / Ctrl+F 侧栏搜索 (拦截原生查找, 窄屏展开侧栏) ✅ — layout-knowledge.html
多字段排序 (locale/数字/日期/字符串, Shift+点击二级排序) ✅ — layout-table.html
默认排序 (options.defaultSort {key,asc}, 加载即排序 + 表头箭头点亮; 数值列按起始年 + 稳定序) ✅ — layout-table.html
常驻行高亮 (options.highlight {key,values}, tr.hl-row 只高亮不筛选; 冻结列/右侧固定列背景同步覆盖) ✅ — layout-table.html
默认筛选 (options.defaultFilter {key,value,mode}, 加载后自动筛选 + filter pill) ✅ — layout-table.html
分享按钮开关 (options.share=false 不渲染 ↗️ 拷贝分享链接) ✅ — layout-table.html
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
copyAction() / shareLink() 走 canonical copyText (execCommand('copy') 回退 + 返回值检查 + 失败反馈, headless Chrome 兼容) ✅ — layout-table.html

### layout-knowledge.html (C 型知识库) — 593 行
条目 / 类目键规范 (item 7 / groups 3) ✅ — html-gen help knowledge
顶部横向标签栏 (按 group 分组, 彩色圆点, 与侧边栏标题行对齐) ✅ — layout-knowledge.html
左侧章节列表 (按 section 分组, badge 标记) ✅ — layout-knowledge.html
搜索面板 (⌘/Ctrl+K 与 🔍, 与 tool-nav-manager Spotlight 同构: 输入即匹配 / ↑↓←→ / Enter 打开 / Esc 关 / `<mark>` 高亮 / 无匹配空态) ✅ — layout-knowledge.html
搜索匹配面 (条目标题 title + 副标题 section + 描述 desc + 全名 page_title + 分组; 不含 url/正文) ✅ — layout-knowledge.html
⌘F / Ctrl+F 归还浏览器原生查找 (v3.6 起不再拦截) ✅ — layout-knowledge.html
根页菜单地图 (列 = 横向页签 / 行 = section / 格内条目 + badge / 点击直达) ✅ — layout-knowledge.html
根页返回 (点 sidebar-title 回根页, 清 URL `item=` 与 localStorage) ✅ — layout-knowledge.html
侧边栏折叠/展开 (48px 收起态, `[` 快捷键, 图标点击展开) ✅ — layout-knowledge.html
侧边栏宽度拖拽 (200-400px, localStorage 持久化) ✅ — layout-knowledge.html
侧边栏标题点击回根页 (v3.6; 复制路径迁 ⧉ 按钮: URL 解码 + Toast) ✅ — layout-knowledge.html
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
剪贴板回退 canonical copyText (isSecureContext 前置 / execCommand('copy') 检查返回值 / 失败可见反馈 / 禁假成功) ✅ — layout-{doc,slide,table,knowledge}.html
剪贴板回退统一 CL015 (v3.4, 2026-09-27) — 四模板 canonical copyText 逐字节一致 + 8 调用点收敛 + 产物全量重生成 + 守卫测试 T1-T11 ✅ — documents/solutions/html-gen-clipboard-fallback-design-v1.2-20260927.md
knowledge 模板 ⌘F/Ctrl+F 打开侧栏搜索 (v3.5, 2026-11-17) — 捕获阶段拦截原生查找 + 幂等 + 窄屏补 `.open` + 按钮 title 标快捷键；产物 4 页重生成 + 静态守卫 2 例 ✅ — layout-knowledge.html
table 模板 顶部筛选条 options.filterBar {column,allLabel,persist} (v3.7, 2026-11-28) — 「所有 + 各值(带计数)」chips，点击即按该列精确筛选、与单元格 pills 双向联动、选中态存 localStorage(html-gen:table:filter)；契约/help/守卫同步 ✅ — layout-table.html
demos-index 案例索引改造 (v3.7) — 场景列(功能性/演示性/案例型/说明文档) + 标题即新页签链接 + 剔除跳转桩/自引用/引用子页(22→19) + 5 例主题改名(chaitin/cloudwise/drama/countries/provinces) 保留旧路径与根级短链跳转 ✅ — html-gen.py cmd_demo
demos-index 案例索引定名与话术统一 (v3.8, 2026-11-28) — 页面 h1「HG 案例索引」/ `<title>`「HG 案例索引 · v{major}.{minor}」；标题去 emoji 并统一为「{X} 模板 · {中文名}[ · 功能演示]」；模板列改显式 `CASE_TEMPLATE` 覆盖（说明性文档不再被 DOM 嗅探误判成「文档（模板B）」：slide-guide→幻灯片（模板D）等）；`CASE_INDEX_SKIP` 增 `slimdown/archive.html`（未用模板的独立页）18→17 行；3 例改名 markdown-spec→doc-features-demo / usage-guide→cli-guide / slide-demo→slide-features-demo（旧路径桩 + 别名 canonical:false） ✅ — html-gen.py / demos/demos-index.html
table 模板 `<title>` 与 h1 可分离 `PAGE_TITLE` 键 (v3.8) — 缺省回退 TITLE，供「h1 简洁 / title 带版本」的索引页使用 ✅ — layout-table.html
doc 模板 `?width=` 增第四档 `xwide` (v3.8, 2026-11-28) — `body.width-xwide .doc-body{max-width:min(100%,1600px)}`（跟随容器、上限 1600；`narrow/medium/wide` 行为不变、仍不持久化）—— 供嵌在宽容器（≈1340-1600）里的知识站正文使用 ✅ — layout-doc.html / documents/doc-slide-template-handbook
落地页 index.html 展示优化 (v3.8) — 去 tagline 尾缀「深色主题 · 中文优先」；「模板使用说明」→「在线说明」；`.cli-box` 单行截断+`title` 兜底（拷贝仍走 `data-copy` 全量命令）；`.features li` 去 `::marker` 只留 `::before`、单行截断；移动端 hero 边距 24→14px、卡片占满、竞品对比表横向滚动 ✅ — index.html
CLI 短别名 `htmlgen` (v3.8) — `pyproject.toml [project.scripts]` 与 `install.sh` 同步注册（不用 `hg`：与 Mercurial 官方命令冲突） ✅ — pyproject.toml / install.sh
说明性文档图表英文化 + 安装前置 (v3.8) — 5 份 guide 的 7 个数据流/结构块改纯英文（中文在等宽字体占 2 格导致框线错位，实测 3 块必然错位）；table/doc/knowledge/slide 四份 guide 的「快速开始」补 pip install / git clone / 直跑三选一 ✅ — demos/*-guide.md
knowledge 模板 根页地图 + 统一搜索面板 (v3.6, 2026-11-23) — 标题点击回根页（复制路径迁 ⧉）+ 菜单地图表（列=页签/行=section）+ ⌘/Ctrl+K Spotlight 面板（标题/副标题/描述/全名/分组）+ **⌘F 归还原生查找**（撤销 v3.5 拦截）；4 产物重生成 + Selenium 15 例 + 静态守卫 2 例 ✅ — layout-knowledge.html
localStorage try/catch + 类型校验 ✅ — layout-*.html
path traversal 校验 (_safe_path) ✅ — scripts/company-report.py
script 上下文 </ 转义 (inject) ✅ — html-gen.py

### 测试
test_help_contract.py (22 个: 契约结构/双向闭合/白名单纪律/CLI 参数/模板维度/变异) ✅ — tests/test_help_contract.py
test_templates.py (doc/slide/table/knowledge 回归) ✅ — tests/test_templates.py
pytest 全量绿 ✅ — CI/提交前置（计数见 AGENTS.md「测试计数」子节）

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
| `html-gen:table:density` | 密度三档 (default/compact/comfortable)；CL036 起入口恒在, `?density=` 与 `options.density` 亦可设 | table |
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
| Python 文件 | 5 (html-gen / company-report / countries-issue-sync / test×2；行数见 `documents/cli-reference.md`) |
| 模板文件 | 4 (doc 444行 / slide 681行 / table 1143行 / knowledge 342行) |
| CSS 基座 | 1 (style-guide.css) |
| 数据文件 | 7 |
| Demo 文件 | 56 (registry: 21 独立 + 35 引用子页) |
| 设计文档 | 4 |
| 测试用例 | 见 AGENTS.md「测试计数」子节 (唯一计数源; 此处不再复制) |
| CLI 子命令 | 7 (doc/slide/table/knowledge/prompt/demo/help) |
| CLI 长形参数 | 36 (table 9 / doc 9 / slide 8 / knowledge 10; 见 `html-gen help <type>`) |
| localStorage keys | 24 |
| 数据卡 metrics | company-report content 页自动生成（6 卡模式） |
| GitHub Corner | demo 页右上角双层可点区防遮挡；根落地页全图标可点 + hover 波浪动画 |
| 零外部依赖 | ✅ (Python stdlib only) |
