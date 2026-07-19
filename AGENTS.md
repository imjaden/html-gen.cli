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
| `html-gen.py` | 主 CLI，3 个子命令，301 行 |
| `company-report.py` | 公司调研报告生成器，从 schema JSON 生成完整 C 型知识库 |
| `style-guide.css` | Layer 1 深色主题 CSS 基座，184 行 |
| `layout-doc.html` | B 型文档模板：侧边栏 TOC + 内容区 |
| `layout-table.html` | A 型表格模板：搜索 + 排序 + 分页 |
| `layout-knowledge.html` | C 型知识库模板：顶部标签栏 + 左侧章节 + iframe/内联内容 |
| `company-research-schema.json` | 公司调研 schema 定义（company/groups/items/output） |

## CLI 子命令

```shell
# doc — Markdown 转 B 型文档
html-gen doc -i report.md -o report.html [--title "标题"] [--subtitle "副标题"]

# table — JSON 转 A 型数据表格
html-gen table -d data.json [--title "标题"] [-o index.html]

# knowledge — JSON 转 C 型知识库
html-gen knowledge -d data.json [-g groups.json] [--title "标题"] [--welcome "欢迎语"] [-o kb.html]
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
- 折叠/展开侧边栏（48px 收起态，`[` 快捷键）
- 侧边栏宽度拖拽（200-400px，localStorage 持久化）
- H3 子项开关，中/英双语，🌙/☀️ 主题切换
- 标题点击复制路径（textContent 安全获取）
- 代码复制（剪贴板 + fallback）、行号、Callout 提示框、阅读进度条、图片灯箱

### layout-table.html（A 型表格）
- 实时搜索（300ms debounce）+ Cmd+F Spotlight 弹窗搜索
- 多字段排序（Shift+点击二级排序），数字/中文 locale 排序
- 客户端分页（默认 30 条/页，可配置）
- **密度切换**：紧凑(28px) / 标准(34px) / 舒适(42px)
- **四种点击模式**（`options.clickModes` 控制）：
  - 🔗 新标签页：`window.open(url, '_blank', 'noopener,noreferrer')`
  - 📋 弹出面板：居中 overlay，键值列表（textContent 安全渲染）
  - 📑 分栏预览：表格 40% + 预览 60%，拖拽分栏线 (25-75%)
  - 📂 行内展开：手风琴模式，点击展开详情网格
- **快速过滤**：点击单元格值 → 筛选该列该值的行，filter pill 可关闭
- **列冻结**：`col.freeze: true` → sticky 列，自动计算 left 偏移
- **分栏模式列过滤**：`col.preview: true` → 仅预览列显示于分栏表格
- **列隐藏**：`col.hide: true` → 永不可见
- **快捷键**：↑↓ 键盘导航行，Enter 点击，F 全屏
- **批量操作**：选中行出现工具栏（全选/取消/导出 CSV）
- **视图预设**：保存/加载/删除设置（密度/模式/排序/列可见性，最多 10 个，≤2KB）
- 列名从 JSON 首条 key 自动推导
- 支持单元格 HTML（`<a>`、`<code>` 等）
- 支持操作按钮列（`copyKey` / `hrefKey` / `desc` / `handler`）、多标签页、CSV 导出、列宽拖拽
- `handler` 模式：自定义 JS 函数名，由模板 `window.{handler}(event, row)` 调用
- 列可见性 localStorage 持久化（`html-gen:table:col-visibility`）

### layout-knowledge.html（C 型知识库）
- 顶部横向标签栏（按 group 分组），与侧边栏标题行对齐
- 左侧章节列表（按 section 分组，badge 标记显式）
- 侧边栏搜索（🔍 按钮，150ms debounce，≥2 字符过滤，无匹配 section 自动隐藏）
- 折叠/展开侧边栏（48px 收起态，`[` 快捷键）
- 双内容模式：有 `url` → iframe 加载，有 `desc` → 内联渲染
- 空状态显示欢迎面板
- 上次选择状态 localStorage 恢复（group + item）

## Markdown → HTML 转换规则

`md_to_html()` 在 `html-gen.py` 中实现，零依赖纯 Python：
- h1–h3 标题（自动加 id 锚点）
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

列属性：
- `col.sortable`：是否可排序（默认 true）
- `col.locale`：排序 locale（如 `"zh"` 用于中文排序）
- `col.freeze`：列冻结（sticky，自动计算 left 偏移）
- `col.preview`：分栏模式下是否显示（默认 false）
- `col.hide`：永远隐藏（默认 false）
- `col.onClick`：`"url"` 使整行可点击跳转到 row.url

Tab 定义：`field` 指定匹配的数据字段（默认 `group` 或 `category`）
- `tab.contains`：逗号分隔包含匹配（如 `"field": "profiles", "contains": true`）

Options（均可选）：
- `pageSize`：每页条数（默认 30）
- `exportCSV`：显示导出按钮（默认 false）
- `rowSelect`：行选择 + 批量操作工具栏（默认 false）
- `search`：搜索框可见性（默认 true）
- `clickModes`：允许的点击模式 `["tab", "modal", "split", "expand"]`（默认 `["tab"]`）

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

## 目录结构

```
html-gen/
├── html-gen.py                 # Layer 3 CLI 生成器
├── company-report.py           # 公司报告生成器（高层封装）
├── style-guide.css             # Layer 1 样式基座
├── layout-doc.html             # Layer 2 B 型文档模板
├── layout-table.html           # Layer 2 A 型表格模板
├── layout-knowledge.html       # Layer 2 C 型知识库模板
├── company-research-schema.json # 公司调研 schema
├── data/                       # 数据文件（*_data.json, *_groups.json）
└── demos/                      # 生成的 HTML 示例
    ├── index.html              # 模板展示首页
    ├── demos-index.html        # A 型文档索引
    ├── template-*-guide.*      # 各模板使用说明
    ├── *_demo.html             # 各类型案例
    └── chaitin/                # 长亭科技商业分析案例
```

## 项目独立性

本项目完全自包含，零外部依赖：
- 所有 Python import 仅使用标准库（json, re, sys, os, argparse, subprocess, pathlib, datetime）
- 模板和 CSS 通过 `Path(__file__).resolve().parent` 自定位，无需外部配置
- `company-report.py` 调用同目录的 `html-gen.py knowledge`，通过 subprocess 运行
- 输出均为自包含单文件 HTML，无外部资源引用

最初从 `script-miner` 项目抽离，现已完全独立运行。
