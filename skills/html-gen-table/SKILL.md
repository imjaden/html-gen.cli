---
name: html-gen-table
description: Use when building data table HTML pages with html-gen. Covers column config, actions, tabs, sorting, CSV export, and row selection for the A-type layout-table template.
version: 2.4.0
author: dev
license: MIT
metadata:
  hermes:
    tags: [html-gen, table, data-table, json-to-html, template]
    related_skills: [html-gen-doc, html-gen-knowledge]
---

# html-gen · 数据列表模板 (A 型)

## 概述

`layout-table.html` 是 html-gen 的 A 型模板 — 将 JSON 数据渲染为可交互的数据表格。支持搜索、排序、分页、Tab 分类过滤、操作列按钮、行选择、CSV 导出、列可见性控制和列宽拖拽。生成自包含单文件 HTML，零外部依赖。

## 何时使用

- 将 JSON 数据列表渲染为可交互 HTML 表格
- 文件索引、项目管理、数据浏览等列表展示场景
- 需要搜索/排序/分页的只读数据展示
- 演示操作按钮功能（使用 `desc` 模式）

## CLI 用法

```shell
# 简单数组格式（向后兼容）
html-gen table -d data.json --title "数据表格" -o index.html

# 结构化格式（推荐）
html-gen table -d data.json --title "项目列表" -o projects.html
```

## 数据格式

### 简单格式（JSON 数组）

```json
[{"名称": "项目A", "数量": 10}, {"名称": "项目B", "数量": 20}]
```

列名自动从第一条记录的 key 推导，所有列默认可排序。

### 结构化格式（推荐）

```json
{
  "columns": [
    {"key": "name", "label": "名称", "sortable": true, "locale": "zh"},
    {"key": "count", "label": "数量", "type": "number", "sortable": true},
    {"key": "actions", "label": "操作", "type": "actions", "actions": [...]}
  ],
  "data": [...],
  "output": "demos/xxx.html",   // 渲染目标 (无 CLI -o 时生效; 均无 → 中断 exit 1)
  "tabs": [
    {"key": "all", "label": "全部"},
    {"key": "Python", "label": "🐍 Python", "field": "lang"}
  ],
  "options": {"pageSize": 30, "exportCSV": true, "rowSelect": true}
}
```

## 列配置 (COLUMNS)

> **键规范单一事实源**: 列属性（22 键）、列类型（6 类）及其取值/默认值的完整定义只在
> **`html-gen help table`** 的「列属性」「列类型」段（实现: `html-gen.py` 的
> `TEMPLATE_CONTRACT['table']`，由 `tests/test_help_contract.py` 对 `layout-table.html`
> 实测消费做双向守卫）。本篇不再维护键表 —— 复制即漂移（CL013 起因: 「默认收起」列属性
> 长期未被任何面向人的文档收录，下游据旧文档把正确写法判成「臆造属性」）。

### 用法要点（键名与取值以 `html-gen help table` 为准）

- **列宽** `width` 仅作初始值：列宽拖拽会记忆到 localStorage（`html-gen:table:col-widths`），
  刷新后覆盖配置；改配置后需清 localStorage 或重新拖拽才生效。
- **两种「隐藏」语义不同**：一种**永不可见**（表格/筛选/分栏详情全部排除），另一种是
  **默认收起**且 ⚙️ 面板可开启、分栏详情仍全列渲染 —— 语义与键名对照见 help（此差异是 CL013 的直接动因）。
- **点击筛选默认关**：单元格点击筛选必须显式开启；标签列（pills）的标签点击筛选默认开、可关。
- **HTML 转义默认开启**（CL010 起）：只有显式关闭才豁免，不要把它当成 opt-in。
- **分栏模式列集**：任一列标记为「分栏可见」时，分栏表只显示这些列；也可用选项显式指定分栏列集。
- **数字列**务必设 `type: "number"`（JSON 注入后数字可能变字符串，否则按文本排序）。
- **中文排序**设 `locale: "zh"`（走 `localeCompare(text, 'zh')`）。

### 操作按钮 (actions)

操作按钮列（`type: "actions"`）的按钮子键与优先级（`copyKey` > `hrefKey` > `handler`/`desc`）
见 `html-gen help table` 的「actions[] 操作按钮子键」段。示例：

```json
{
  "icon": "📋",        // Emoji 图标
  "label": "复制",     // title 提示文本
  "copyKey": "name",   // 模式1: 复制字段值到剪贴板
  "hrefKey": "url",    // 模式2: 新标签页打开 URL
  "desc": "复制名称"   // 模式3: 点击弹 Toast 展示描述（演示用）
}
```

只生效第一个匹配的模式；`handler` 为自定义 JS 函数名（模板调 `window.{handler}(event, row)`）。

## Tab 分类过滤 (TABS)

Tab 键（`key` / `label` / `field` / `match` / `contains` / `value`）、匹配语义与默认字段见
`html-gen help table` 的「Tab 属性」段。示例：

```json
[
  {"key": "all", "label": "全部"},
  {"key": "Python", "label": "🐍 Python", "field": "lang"},
  {"key": "工具", "label": "🔧 工具", "field": "group"}
]
```

- 第一个 Tab 的 key 用于「全部」；`contains: true` 走逗号/顿号分隔的包含匹配；Tab 计数 = 匹配行数。
- Tab 选择自动保存到 localStorage。

## 单元格点击行为（默认）

点击行为优先级链（从高到低）：
1. 列上的显式单元格点击行为（分栏 / 弹窗）
2. 列上的点击筛选开关（显式 true）
3. **第 1 列（首个有 key 的数据列）→ 默认打开分栏预览**（展示该行元信息）
4. 其余列 → 无操作

即：普通单元格默认无筛选；需要按值筛选的列显式开启；标签列默认可点筛选。

## 全局选项 (OPTIONS)

13 个 options 顶层键（含 `searchFields` / `showIndex` / `defaultFilter` / `feedback` /
`clickMode` 单数兼容别名）及其默认值见 `html-gen help table` 的「选项」段；
`options.feedback` 子键（5 项）见「options.feedback 子键」段。

## URL 状态分享 (🔗)

URL 状态键（`?tab` / `?q` / `?split`）的取值口径见 `html-gen help table` 的「URL 状态」段。
行为：

- 状态变化用 `history.replaceState` 静默同步（不产生历史记录），默认参数（空值）自动剔除
- **tabs 行居右按钮区 `.tabs-actions`**（CL005）：↗ 分享按钮拷贝规范化 URL（clipboard + execCommand fallback，headless 兼容）；🏠 home 入口（`--home-url` 注入，与 share 同容器 36px 圆角深底，font-size 1rem 图标同尺寸）
- 排序 / 快速过滤触发时自动 closeSplit（下标语义失效保护）
- 加载时按 tab → q → split 顺序恢复（HG-SEC-076）

## 操作按钮 Emoji 参考

| 类别 | Emoji |
|:---|:---|
| 查看/导航 | 👁️ 查看 · 🔗 打开 · 👀 预览 · 📍 定位 |
| 编辑/修改 | ✏️ 编辑 · 📝 重命名 · 📁 移动 · 📌 置顶 · ⭐ 收藏 |
| 操作/执行 | ▶️ 播放 · ⬇️ 下载 · 🚀 运行 · 🧬 克隆 |
| 复制/分享 | 📋 复制 · 📎 链接 · 💻 命令 · 🗂️ 路径 · 📤 分享 |
| 删除/清理 | 🗑️ 删除 · 📥 归档 · 🧹 清理 |
| 信息/诊断 | ℹ️ 元信息 · 📄 日志 · 📊 状态 · 🕐 历史 · 🔍 Diff |

## 常见场景

### 文件管理器

```json
{"actions": [
  {"icon": "👁️", "label": "预览", "desc": "预览文件内容"},
  {"icon": "📋", "label": "复制路径", "copyKey": "path"},
  {"icon": "🗑️", "label": "删除", "desc": "永久删除（需确认）"}
]}
```

### CRUD 管理

```json
{"actions": [
  {"icon": "👁️", "label": "查看", "desc": "查看详细信息"},
  {"icon": "✏️", "label": "编辑", "desc": "修改记录内容"},
  {"icon": "🔗", "label": "打开", "hrefKey": "url"},
  {"icon": "🗑️", "label": "删除", "desc": "永久删除（需二次确认）"}
]}
```

## 常见问题

### Q: 操作按钮点击没反应？
检查 `col.type` 是否设为 `"actions"`，actions 数组中每个按钮必须至少配置 `copyKey`、`hrefKey` 或 `desc` 之一。

### Q: 数字列排序不正确？
设置 `col.type: "number"`。JSON 注入后数字可能变字符串，`type: "number"` 确保使用 `parseFloat` 比较。

### Q: 中文排序混乱？
设置 `col.locale: "zh"` 使用 `localeCompare(text, 'zh')`。

### Q: Tab 切换后分页错误？
每次切换 Tab 自动重置到第 1 页。Tab 状态保存在 localStorage key `htmlgen_tab`。

## 验证清单

- [ ] 数据 JSON 格式正确（简单数组或结构化对象）
- [ ] 列 key 与数据字段名一致
- [ ] `type: "actions"` 列配置了 actions 数组
- [ ] Tab 的 field 与数据字段匹配
- [ ] 运行 `html-gen table -d data.json -o output.html` 正常生成
- [ ] 生成的 HTML 在浏览器中表格正常渲染
- [ ] 排序、搜索、分页功能正常
- [ ] 操作按钮点击有响应（copyKey 复制 / hrefKey 跳转 / desc Toast）


## 变更记录
- v2.5.0 (2026-08-29): 分享/Home 按钮统一放 tabs 行居右 `.tabs-actions`（↗ 图标 + home-link 流式同容器 36px，CL005）
- v2.4.0 (2026-08-29): 新增 URL 状态分享（?tab&q&split replaceState 同步/恢复 + 🔗 拷贝按钮）
- v2.3.0 (2026-08-06): quickFilter 默认关（显式 true 启用）+ pillFilter/onCellClick/preview 列属性; tabs value/contains 匹配; pills 顿号分隔; 第 1 列默认分栏
- v2.2.0 (2026-08-06): 新增 quickFilter/freeze 列属性、datetime/pills 列类型、clickModes 选项; 兼容单数 clickMode
- v2.1.0: 列冻结、右侧固定列、分栏列过滤增强、单元格点击分栏、自定义模态框渲染器、SKILL.md 加载
