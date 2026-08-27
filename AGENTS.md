# AGENTS.md — html-gen 项目指南

## 项目概述

`html-gen` 是一个零依赖 Python CLI 工具，将 Markdown/JSON 数据注入 HTML 模板，输出自包含单文件 HTML。深色主题，中文优先。

## 三层架构

```
Layer 1: style-guide.css        CSS 变量 + 基础组件（按钮/表格/弹窗/分页）
Layer 2: layout-*.html          模板骨架（A 型表格 / B 型文档 / C 型知识库）
Layer 3: html-gen.py            CLI 生成器（doc / table / knowledge）
```

## 核心文件

| 文件 | 用途 |
|:---|:---|
| `html-gen.py` | 主 CLI，3 个子命令，958 行 |
| `scripts/company-report.py` | 公司调研报告生成器，从 schema JSON 生成完整 C 型知识库（groups/data/html + content/metrics 内容页自动生成） |
| `style-guide.css` | Layer 1 深色主题 CSS 基座，183 行 |
| `layout-doc.html` | B 型文档模板：侧边栏 TOC + 内容区 |
| `layout-table.html` | A 型表格模板：搜索 + 排序 + 分页 |
| `layout-knowledge.html` | C 型知识库模板：顶部标签栏 + 左侧章节 + iframe/内联内容 |
| `scripts/company-research-schema.json` | 公司调研 schema 定义（company/groups/items/output） |

## CLI 子命令

```shell
# doc — Markdown 转 B 型文档
html-gen doc -i report.md -o report.html [--title "标题"] [--subtitle "副标题"]

# table — JSON 转 A 型数据表格
html-gen table -d data.json [--title "标题"] [--subtitle "段落描述"] [-o index.html]
#   --title    优先级: CLI > JSON 顶层 title > "数据表格"
#   --subtitle 页面级段落描述(纯文本, \n 换行); JSON 顶层 subtitle 兜底, 显式传空串清空

# knowledge — JSON 转 C 型知识库
html-gen knowledge -d data.json [-g groups.json] [--title "标题"] [--welcome "欢迎语"] [-o kb.html]

# demo — 案例清单与详情（按模板分组 / --json / --all / --open / --rebuild）
html-gen demo list
html-gen demo drama-knowledge
html-gen demo --rebuild

# prompt — 项目 skills 输出
html-gen prompt <skill> [--brief] [--json]

# help — 6 主题（doc/slide/table/knowledge/prompt/demo）
html-gen help demo
```

## 模板注入机制

- 模板使用 `<!--KEY-->` 占位符，CLI 通过 `inject()` 函数替换
- CSS 在生成时内联：替换 `<link rel="stylesheet" href="style-guide.css">` 为 `<style>...</style>`
- 输出为自包含单文件 HTML，无外部依赖

## 模板类型详解

### layout-doc.html（B 型文档）
- 左侧粘性侧边栏 + 右侧内容区
- 自动生成 TOC（h2/h3），实时高亮当前章节
- TOC 搜索（🔍 按钮，150ms debounce，≥2 字符触发过滤）
- **Bare 模式**：默认隐藏侧边栏/工具栏，`?sidebar=1&toolbar=1` 展示；知识库嵌入自动降级
- **正文宽度三级**：`?width=narrow|medium|wide`（默认 960px，不持久化）
- **md 路径行**：meta 区显示源文件名（`basename` 脱敏），默认 CSS 隐藏，`?show-md=1` 显示
- 折叠/展开侧边栏（48px 收起态，`[` 快捷键）
- 侧边栏宽度拖拽（200-400px，localStorage 持久化）
- H3 子项开关，中/英双语，🌙/☀️ 主题切换
- 标题点击复制路径（textContent 获取 meta 路径，脱敏文件名）
- 代码复制（剪贴板 + fallback）、行号、Callout 提示框、阅读进度条、图片灯箱

### layout-table.html（A 型表格）
- **页面级段落描述**：`--subtitle` / JSON 顶层 `subtitle`（优先级 CLI > JSON），h1 下方段落区，纯文本安全转义 + `\n` → `<br>`，显式传空串清空；无 subtitle 不渲染
- **Cinema 纪律化宽度模型**：`table-layout:fixed`，每列强制显式 width（默认 120px，actions 100px），无 colgroup，td `max-width:0` 强制截断
- 实时搜索（300ms debounce）+ Cmd+F Spotlight 弹窗搜索
- 多字段排序（Shift+点击二级排序），数字/中文 locale 排序
- 客户端分页（默认 30 条/页，可配置）
- **密度切换**：紧凑(28px) / 标准(34px) / 舒适(42px)，设置面板横向展示
- **五种点击模式**（`options.clickModes` 控制）：
  - 🔗 新标签页：`window.open(url, '_blank', 'noopener,noreferrer')`
  - 📋 弹出面板：居中 overlay，键值列表（textContent 安全渲染）；支持自定义渲染器（`options.modalRenderer: 'skills'`）
  - 📑 分栏预览：表格 + 预览并排，拖拽分栏线，比例预设 (▦)，▲▼ 导航；支持 SKILL.md 加载
  - 📂 行内展开：手风琴模式，点击展开详情网格
  - 🎯 单元格点击：`col.onCellClick: 'split'` 直接打开分栏
- **快速过滤**：点击单元格值 → 筛选该列该值的行，filter pill 可关闭；`col.quickFilter: true` 启用 (默认关)
- **列冻结**：`col.freeze: true` → sticky 列，动态计算 left 偏移（基于 `col.width`）
- **右侧固定列**：`col.stickyRight: true` → 水平滚动时保持在视口右侧
- **分栏模式列过滤**：`col.preview: true` → 仅预览列显示于分栏表格；`options.columnsSplit` 指定分栏列集
- **列隐藏**：`col.hide: true` → 永不可见
- **快捷键**：↑↓ 键盘导航行，Enter 点击，F 全屏
- **批量操作**：选中行出现工具栏（全选/取消/导出 CSV）
- **视图预设**：保存/加载/删除设置（密度/模式/排序/列可见性，最多 10 个，≤2KB）
- 列名从 JSON 首条 key 自动推导
- 支持单元格 HTML（`<a>`、`<code>` 等）
- 支持操作按钮列（`copyKey` / `hrefKey` / `desc` / `handler`）、多标签页、CSV 导出
- `handler` 模式：自定义 JS 函数名，由模板 `window.{handler}(event, row)` 调用
- 列可见性 localStorage 持久化（`html-gen:table:col-visibility`）
- 列宽度 localStorage 持久化（`html-gen:table:col-widths`），拖拽 resize 直接操作 DOM
- 列宽拖拽可禁用（`options.columnResize: false`）
- 设置面板：⚙️ 下拉，密度/点击模式/列可见性/视图预设，内部点击不关闭，✕ 关闭按钮
- `printColWidths()` 控制台调试函数
- 安全：`copyAction()` 含 execCommand fallback（headless Chrome 兼容）

### layout-knowledge.html（C 型知识库）
- 顶部横向标签栏（按 group 分组），与侧边栏标题行对齐
- 左侧章节列表（按 section 分组，badge 标记显式）
- 侧边栏搜索（🔍 按钮，150ms debounce，≥2 字符过滤，无匹配 section 自动隐藏）
- **Bare 模式**：默认隐藏侧边栏/工具栏，`?sidebar=1&toolbar=1` 展示；知识库嵌入自动降级
- 折叠/展开侧边栏（48px 收起态，`[` 快捷键）
- 双内容模式：有 `url` → iframe 加载，有 `desc` → 内联渲染
- section 标题可点击：单条目 section 点击标题直接加载 (K2)
- 空状态显示欢迎面板
- 上次选择状态 localStorage 恢复（group + item）

## Markdown → HTML 转换规则

`md_to_html()` 在 `html-gen.py` 中实现，零依赖纯 Python：
- h1–h6 标题（自动加 id 锚点，h4-h6 不入 TOC）
- `**加粗**`、`*斜体*`、`` `代码` ``、`[链接](url)`
- 围栏代码块（支持变长 fence 嵌套）
- 表格（Markdown pipe table）
- 无序/有序列表（连续自动合并为 `<ul>`）
- Callout：`> **Note/Warning/Tip/Danger/注意/警告/提示/危险**：内容`
- 分隔线 `---`、引用 `> 文字`
- 不解析图片（安全限制）

## 数据格式

### table 输入

**简单格式**（JSON 数组，向后兼容）：
```json
[{"列名1": "值1", "列名2": "值2"}, ...]
```

**结构化格式**（v2.0 新增）：
```json
{
  "title": "项目速查表",          // 可选，页面标题（默认 "数据表格"，CLI --title 覆盖）
  "subtitle": "共 N 条记录\n按需换行", // 可选，h1 下方段落描述（CLI --subtitle 覆盖，显式传空串清空）
  "columns": [
    {"key": "name", "label": "项目", "sortable": true, "locale": "zh"},
    {"key": "stars", "label": "Stars", "type": "number"},
    {"key": "actions", "label": "操作", "type": "actions", "actions": [
      {"label": "复制", "icon": "📋", "copyKey": "name"},
      {"label": "打开", "icon": "🔗", "hrefKey": "url"}
    ]}
  ],
  "data": [{"name": "hermes-agent", "stars": 50200, "url": "https://..."}],
  "tabs": [
    {"key": "all", "label": "全部"},
    {"key": "AI框架", "label": "🤖 AI框架", "field": "group"}
  ],
  "options": {"exportCSV": true, "rowSelect": true, "pageSize": 30}
}
```

列类型 (`col.type`)：
- `string`（默认）：文本排序
- `number`：数值排序（parseFloat 比较）
- `actions`：操作按钮列，支持 `copyKey`（复制）和 `hrefKey`（跳转）
- `pills`：标签样式渲染，逗号分隔值转 tag pills

列属性：
- `col.sortable`：是否可排序（默认 true）
- `col.locale`：排序 locale（如 `"zh"` 用于中文排序）
- `col.freeze`：列冻结（sticky，动态计算 left 偏移基于 col.width）
- `col.stickyRight`：右侧固定列（水平滚动时粘在视口右侧）
- `col.preview`：分栏模式下是否显示（默认 false）
- `col.hide`：永远隐藏（默认 false）
- `col.onClick`：`"url"` 使整行可点击跳转到 row.url
- `col.onCellClick`：`"split"` 点击单元格直接打开分栏预览
- `col.quickFilter`：true 启用点击筛选 (默认关)
- `col.pillFilter`：false 禁用标签筛选 (默认开)
- `col.width`：列宽（如 `"150px"`），影院模型下必设，默认 fallback 120px
- `col.escape`：HTML 转义（默认 false）
- `col.render`：自定义渲染函数（已废弃，优先用 type 或 onCellClick）

Tab 定义：`field` 指定匹配的数据字段（默认 `group` 或 `category`）
- `tab.contains`：逗号分隔包含匹配（如 `"field": "profiles", "contains": true`）

Options（均可选）：
- `pageSize`：每页条数（默认 30）
- `exportCSV`：显示导出按钮（默认 false）
- `rowSelect`：行选择 + 批量操作工具栏（默认 false）
- `search`：搜索框可见性（默认 true）
- `clickModes`：允许的点击模式 `["tab", "modal", "split", "expand"]`（默认 `["tab"]`）
- `columnResize`：列宽拖拽（默认 true，false 时隐藏 resize handle）
- `columnsSplit`：分栏模式专用列集（如 `["name", "actions"]`）
- `modalRenderer`：自定义模态框渲染器（如 `"skills"` 激活结构化详情面板）

### knowledge 输入（JSON 数组）
```json
[{
  "title": "条目名称",      // 必填
  "group": "所属类目",      // 必填，对应顶部 Tab
  "section": "子分类",      // 可选，侧栏分组
  "badge": "标记",          // 可选，如熟练度
  "desc": "<p>HTML内容</p>", // 与 url 二选一
  "url": "detail.html"      // 与 desc 二选一，iframe 加载
}]
```

### groups 输入（JSON 数组）
```json
[{"key": "类目key", "label": "显示名", "icon": "🏢"}]
```

## 代码规范

- 只使用 Python 标准库，零外部依赖
- git commit 格式：`type@scope: subject`（如 `feat: initial project setup - html-gen CLI + A/B/C templates`）
- 不执行 `git push`，只 commit
- 中文注释和用户界面消息
- Python 模板注入使用 `inject(template, **kwargs)` 函数
- CSS 使用 `--cobalt-*` 色系深色主题变量

## 测试治理

- Selenium 测试：headless Chrome，`localStorage.clear()` setUp，`window.__testErrors` 跟踪
- Chromedriver: `/Users/jadenli/CodeSpace/script-miner/cache/chromedriver/chromedriver`
- 测试文件命名：`tests/test_{feature}.py`，继承 `unittest.TestCase`
- 每个测试方法独立加载页面，`_errors()` 检查 JS 错误
- 当前 188 tests（20 文件；测试文件：test_drama_knowledge 16 / test_templates 18 / test_hermes_skills 15 / test_provinces_table 13 / test_countries_table 13 / test_index_landing 18 / test_table_features 14 / test_demo_cmd 10 / test_knowledge_sidebar 8 / test_doc_width 8 / test_history_tables 7 / test_doc_sidebar 7 / test_doc_bare 6 / test_sticky_width 6 / test_heading_levels 6 / test_initial_hidden_split 5 / test_prompt_cmd 5 / test_demos_index 6 / test_slide_h3_toggle 4 / test_datetime_clickmode 3 等）
- **全量命令**（pytest-xdist 并行，见 pytest.ini `addopts = -n 4`）：
  ```bash
  python3 -m pytest tests/ -q -n 4     # 并行全量 (~26s)
  python3 -m pytest tests/ -q -n 0     # 单线程调试
  ```
- **等待机制约定**：
  - setUp 页面加载 wait 用 `WebDriverWait`（主元素：table `.data-table` / knowledge `.kw-tab` / doc `.doc-body` / slide `.slide-sidebar`）
  - 交互 wait 用调低后的固定 sleep（0.3/0.4/0.5/0.6/0.8/0.9 → 减半；0.08/0.1/0.15/0.2/0.25 不动）
  - sleep 调低用 `skills/test-speed-optimization/scripts/speedup_sleeps.py`（--dry-run/--apply/--restore）
- 依赖：`pytest-xdist>=3.8.0`（见 requirements-dev.txt）

## 目录结构

```
html-gen.cli/
├── index.html                 # 落地页（动态两屏 hero + 四模板网格 + 上箭头 A/B 返回首页 + 🌙☀️ 主题切换 + 📋 复制按钮 + footer）
├── html-gen.py                 # Layer 3 CLI 生成器
├── scripts/                     # 脚本与 schema（company-report 生成器）
├── style-guide.css             # Layer 1 样式基座
├── layout-doc.html             # Layer 2 B 型文档模板
├── layout-table.html           # Layer 2 A 型表格模板
├── layout-knowledge.html       # Layer 2 C 型知识库模板

├── data/                       # 数据文件（*_data.json, *_groups.json）
├── tests/                      # Selenium + 回归测试 (188 tests)
├── skills/                    # 项目 skills prompt
    │   ├── html-gen/SKILL.md
    │   ├── html-gen-table/SKILL.md
    │   │   └── references/table-demo-prompt.md
    │   ├── html-gen-doc/SKILL.md
    │   ├── html-gen-knowledge/SKILL.md
    │   └── pages-index/SKILL.md   # pages index 落地页规范（hero+矩阵/主题/复制/两屏/corner/双源）
    └── demos/                      # 生成的 HTML 示例（独立案例根级扁平，URL=/demos/{name}.html）
    ├── index.html              # 模板展示首页
    ├── demos-index.html        # A 型文档索引（数据源 data/_demos-data.json）
    ├── usage-guide.html        # CLI 使用说明
    ├── table-guide.html        # A 型 · 数据表格方案
    ├── doc-guide.html          # B 型 · 文档阅读方案
    ├── markdown-spec.html      # Markdown 语法规范
    ├── knowledge-guide.html    # C 型 · 知识库方案
    ├── slide-guide.html        # D 型 · 幻灯片方案
    ├── slide-demo.html         # D 型 Slide 演示
    ├── hermes-profile-skills-list.html  # 主力 demo: Hermes Skills 列表
    ├── table-features-demo.html # 表格功能全演示（数据源 data/_table-features-demo.json）
    ├── table-actions-demo.html # 操作按钮 demo
    ├── knowledge-demo.html     # 知识库功能 demo
    ├── countries-table.html    # 全球 195 国速查表（数据源说明 countries-table.md）
    ├── provinces-table.html    # 中国 34 省速查表（数据源说明 provinces-table.md）
    ├── drama-knowledge.html    # 以剧读史影视历史知识库（中国历史 + 大明王朝1566）
    ├── chaitin-business-analysis.html  # 长亭科技商业分析知识库
    ├── cloudwise-business-analysis.html # 云智慧商业分析知识库
    ├── chaitin/                # 长亭内容子页（知识库引用）+ menu-design 菜单方案
    ├── cloudwise/              # 云智慧内容子页（知识库引用）
    └── drama/                  # 以剧读史内容子页（知识库引用；时间轴 + 36计策，md 源 + html）

> **双源漂移（1C 决策，2026-08-23）**：根 `index.html`（落地页）与 `demos/index.html`（模板展示首页）为**两份独立副本**，非同一文件。改动落地页结构时需同步两处；`demos/index.html` 是 `html-gen demo --rebuild` 的 featured 数据源，根 index.html 不参与。github-corner 模式亦不同：layout 模板层（demo 页）用「pointer-events:none 穿透 + hit 36px」防遮挡右上角工具栏；根落地页无工具栏，用全图标可点 + hover 波浪动画（HG-SEC-014 文档化，2026-08-23）。两页共用主题按钮（right:88px 避让 corner，`html-gen:index_theme` localStorage key）与复制按钮/断点/footer；github-corner 浅色模式用深三角+白 octocat（`--gh-corner-fill`/`--gh-octocat` 变量，`:root.light .github-corner` 覆盖全局 a 链接色）；根页 hero 为**动态两屏**（JS: hero 高 = 视口高−55px，第二屏标题露出首屏底部；scroll-hint fixed 底部、滚动淡出），demos 页无 hero。**防漂移测试**：`tests/test_demos_index.py::test_05_dual_source_consistency` 断言双源关键功能特征一致（2026-08-24）。
```

## 项目独立性

本项目完全自包含，零外部依赖：
- 所有 Python import 仅使用标准库（json, re, sys, os, argparse, subprocess, pathlib, datetime）
- 模板和 CSS 通过 `Path(__file__).resolve().parent` 自定位，无需外部配置
- `company-report.py` 调用同目录的 `html-gen.py knowledge`，通过 subprocess 运行；items 含 `content`（正文 md）+ `metrics`（数据卡表格）时自动生成内容页（doc 产物）
- 内容页数据卡模式：schema items.metrics → 内容页顶部"核心数据"表格（6 卡对齐：成立/客户/产品/专利/融资/荣誉）
- 数据采集：`scripts/qcc-cloudwise.py`（企查查 selenium 采集，登录态 30s 手工窗口）
- 输出均为自包含单文件 HTML，无外部资源引用
