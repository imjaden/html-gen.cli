---
name: html-gen-table
description: Use when building data table HTML pages with html-gen. Covers column config, actions, tabs, sorting, CSV export, and row selection for the A-type layout-table template.
version: 2.3.0
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
  "tabs": [
    {"key": "all", "label": "全部"},
    {"key": "Python", "label": "🐍 Python", "field": "lang"}
  ],
  "options": {"pageSize": 30, "exportCSV": true, "rowSelect": true}
}
```

## 列配置 (COLUMNS)

| 字段 | 类型 | 必填 | 说明 |
|:---|:---|:---:|:---|
| `key` | string | ✅ | 数据字段名 |
| `label` | string | ✅ | 表头显示名 |
| `sortable` | bool | | 是否可排序（默认 true） |
| `type` | string | | `string`(默认) / `number` / `datetime` / `pills` / `actions` |
| `locale` | string | | 排序 locale，如 `"zh"` |
| `width` | string | | CSS 宽度，如 `"120px"` |
| `freeze` | bool | | 列冻结 (sticky left) |
| `quickFilter` | bool | | 点击单元格值精确筛选，**默认关**，显式 `true` 才启用 |
| `pillFilter` | bool | | pills 列标签点击筛选（contains 匹配），默认开，`false` 关闭 |
| `onCellClick` | string | | 单元格点击行为：`"split"` 分栏预览 / `"modal"` 弹出详情 |
| `preview` | bool | | 分栏模式下显示的列（split 预览/表格仅显示 preview 列，未配 preview 列则全显） |
| `class` | string | | 单元格 CSS class |
| `escape` | bool | | 是否 HTML 转义值（安全） |
| `render` | func | | 自定义渲染函数 |
| `onClick` | string | | 行点击行为（`"url"` 跳转到 row.url） |
| `actions` | array | | 仅 `type: "actions"`，操作按钮数组 |

### 列类型详情

**type: "string"** (默认) — 文本排序，使用 `localeCompare`；配合 `locale: "zh"` 实现中文拼音排序

**type: "number"** — 数值排序，使用 `parseFloat` 比较，空值视为 0

**type: "datetime"** — 日期排序，使用 `Date.parse` 比较，空值视为 0；渲染原样展示 ISO 日期字符串

**type: "pills"** — 标签样式，逗号/顿号/中文逗号分隔字符串渲染为 tag pills（分隔符 `[,，、]+`）；标签点击筛选默认开（`pillFilter: false` 关闭）

**type: "actions"** — 操作按钮列，每个按钮支持三种模式：

```json
{
  "icon": "📋",        // Emoji 图标
  "label": "复制",     // title 提示文本
  "copyKey": "name",  // 模式1: 复制字段值到剪贴板
  "hrefKey": "url",   // 模式2: 新标签页打开 URL
  "desc": "复制名称"   // 模式3: 点击弹 Toast 展示描述（演示用）
}
```

优先级：`copyKey` > `hrefKey` > `desc`，只生效第一个匹配的。

## Tab 分类过滤 (TABS)

```json
[
  {"key": "all", "label": "全部"},
  {"key": "Python", "label": "🐍 Python", "field": "lang"},
  {"key": "工具", "label": "🔧 工具", "field": "group"}
]
```

- `key`: Tab 标识，第一个 Tab 的 key 用于"全部"
- `label`: 显示文本（可含 Emoji）
- `field`: 匹配的数据字段名（默认 `group` 或 `category`）
- `contains`: 数组字段包含匹配（值用逗号/顿号分隔时，如 `"field": "region_tags", "contains": true`）
- `value`: contains 模式下匹配的目标值（不配则用 key 匹配）；Tab 计数 = 匹配行数
- Tab 选择自动保存到 localStorage

## 单元格点击行为（默认）

点击行为优先级链（从高到低）：
1. `col.onCellClick: 'split'` / `'modal'`（显式配置）
2. `col.quickFilter: true`（显式筛选）
3. **第 1 列（首个有 key 的数据列）→ 默认打开分栏预览**（展示该行元信息）
4. 其余列 → 无操作

即：普通单元格默认无筛选；需要按值筛选的列显式配 `quickFilter: true`；标签列默认可点筛选（pillFilter）。

## 全局选项 (OPTIONS)

| 选项 | 类型 | 默认 | 说明 |
|:---|:---|:---:|:---|
| `pageSize` | int | 30 | 每页条数 |
| `exportCSV` | bool | false | 显示 CSV 导出按钮 |
| `rowSelect` | bool | false | 启用行选择（checkbox） |
| `search` | bool | true | 显示搜索框 |
| `clickModes` | array | `["tab"]` | 允许的点击模式 `"tab"`/`"modal"`/`"split"`/`"expand"`; 兼容单数 `clickMode` |

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
- v2.3.0 (2026-08-06): quickFilter 默认关（显式 true 启用）+ pillFilter/onCellClick/preview 列属性; tabs value/contains 匹配; pills 顿号分隔; 第 1 列默认分栏
- v2.2.0 (2026-08-06): 新增 quickFilter/freeze 列属性、datetime/pills 列类型、clickModes 选项; 兼容单数 clickMode
- v2.1.0: 列冻结、右侧固定列、分栏列过滤增强、单元格点击分栏、自定义模态框渲染器、SKILL.md 加载
