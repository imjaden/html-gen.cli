---
name: html-gen
description: Use when asked to generate HTML from markdown or JSON using html-gen, create data table pages, knowledge bases, slide presentations, or document pages. Use when user references html-gen CLI or wants markdown converted to styled HTML.
version: 2.3.0
author: dev
license: MIT
metadata:
  hermes:
    tags: [html-gen, template, markdown-to-html, json-to-html, cli, data-table, knowledge-base, slide, document]
    related_skills: [html-gen-table]
---

# html-gen — HTML 模板 CLI 生成器

## 概述

`html-gen` 是一个零依赖 Python CLI 工具，将 Markdown/JSON 数据注入 HTML 模板，输出自包含单文件 HTML。深色主题，4 种模板类型。

## 四型总览

| 类型 | 模板文件 | 命令 | 输入 | 输出场景 |
|:---|:---|:---|:---|:---|
| A 型 · 数据表格 | `layout-table.html` | `table` | JSON 数据 | 文件索引、项目列表、数据浏览 |
| B 型 · 文档阅读 | `layout-doc.html` | `doc` | Markdown | 分析报告、技术文档、长文阅读 |
| C 型 · 知识库 | `layout-knowledge.html` | `knowledge` | JSON 条目+类目 | 知识库、面试准备、项目 Wiki |
| D 型 · 幻灯片 | `layout-slide.html` | `slide` | Markdown | 课件演示、会议分享、分段阅读 |

> A 型表格的详细列配置、操作按钮、Tab 过滤等高级功能参见 `html-gen-table` skill。

## CLI 命令

```shell
# B 型 — Markdown → 文档
html-gen doc -i report.md -o report.html

> 默认隐藏侧边栏/工具栏（Bare 模式）；独立完整浏览加 `?sidebar=1&toolbar=1` [--title "标题"] [--subtitle "副标题"]（自动剥离 YAML frontmatter）

# D 型 — Markdown → 幻灯片
html-gen slide -i slides.md -o slides.html [--title "标题"] [--subtitle "副标题"]

# A 型 — JSON → 数据表格
html-gen table -d data.json [--title "标题"] [-o index.html]

# C 型 — JSON → 知识库
html-gen knowledge -d data.json [-g groups.json] [--title "标题"] [--welcome "欢迎语"] [-o kb.html]
```

输出均为自包含单文件 HTML（CSS 内联，零外部依赖）。

## 支持的 Markdown 语法

`md_to_html()` 内置渲染器支持以下语法子集。**AI 生成 Markdown 时必须遵守此规范**：

### 块级元素

| 语法 | 写法 | 说明 |
|:---|:---|:---|
| h1 标题 | `# 标题` | 全文档唯一 |
| h2 标题 | `## 标题` | 自动加入 TOC、slide 分页边界 |
| h3 标题 | `### 标题` | 自动加入 TOC |
| 无序列表 | `- 列表项` | 连续自动合并为 `<ul>` |
| 有序列表 | `1. 列表项` | 连续自动合并为 `<ol>` |
| 表格 | `\| A \| B \|` + `\|:---\|:---\|` | 第二行为对齐分隔行 |
| 围栏代码块 | ` ```lang ` … ` ``` ` | 支持变长 fence 嵌套 |
| 引用 | `> 文字` | 单行模式 |
| 分隔线 | `---` | 连续 3+ 短横 |
| Callout 提示框 | `> **Note:** 内容` | 支持 Note/Tip/Warning/Danger/Caution + 中文对应词 |

### 行内元素

| 语法 | 写法 | 说明 |
|:---|:---|:---|
| 加粗 | `**文字**` | 全局有效，表格内也支持 |
| 斜体 | `*文字*` | `**` 优先匹配 |
| 行内代码 | `` `code` `` | 在 `<pre><code>` 内无效 |
| 链接 | `[文字](url)` | 自动 `target="_blank"` |
| 图片 | `不解析` | 用纯 HTML `<img>` 代替 |

### 不支持

- 缩进子列表（平铺即可）
- 图片 Markdown 语法 `![alt](url)`
- HTML 标签（会被转义）
- Emoji 短码 `:smile:`（直接用 Unicode Emoji）

### Callout 关键词对照

```
> **Note:** ...     > **注意**：...
> **Tip:** ...      > **提示**：...
> **Warning:** ...  > **警告**：...
> **Danger:** ...   > **危险**：...
> **Caution:** ...  > **注意**：...
```

## B 型 · 文档阅读 (doc)

**输入**: Markdown 文件  
**输出**: 侧边栏 TOC + 内容区 HTML 文档

自动功能：
- 从 h2/h3 生成侧边栏目录，点击平滑滚动
- 滚动时自动高亮当前章节
- 代码块悬停复制按钮 + CSS 行号
- h2/h3 悬浮 ¶ 锚点链接，点击复制 `#id`
- 顶部阅读进度条
- 图片点击灯箱放大
- 外链自动归档到文档底部
- 文件元信息（路径/创建时间/字数/阅读时长）

**用法**:
```shell
html-gen doc -i report.md -o report.html

> 默认隐藏侧边栏/工具栏（Bare 模式）；独立完整浏览加 `?sidebar=1&toolbar=1` --title "标题" --subtitle "副标题"
```

## D 型 · 幻灯片 (slide)

**输入**: Markdown 文件（每个 `##` 为一页）  
**输出**: h2 分页幻灯片 + 底部圆点导航

自动功能：
- 封面页（h1 标题 + 副标题 + 元信息 + 节数统计）
- h2 自动分页，每个二级标题独立一页
- 键盘翻页：← → Space Home End
- 底部圆点导航（已读/当前/未读三色）
- 右上角页码 n/N（3s 渐隐）
- F 键全屏演示
- localStorage 进度保存
- 侧边栏 TOC（h3 默认隐藏，可通过 H3 开关显示）
- >50 h2 时显示性能警告

**用法**:
```shell
html-gen slide -i slides.md -o slides.html --title "标题" --subtitle "副标题"
```

## A 型 · 数据表格 (table)

**输入**: JSON 数据（简单数组 或 结构化对象）  
**输出**: 可搜索/排序/分页的交互表格

### 简单格式

```json
[{"名称": "项目A", "数量": 10}, {"名称": "项目B", "数量": 20}]
```

列名自动从首条 key 推导。

### 结构化格式

```json
{
  "columns": [
    {"key": "name", "label": "名称", "sortable": true, "locale": "zh"},
    {"key": "stars", "label": "Stars", "type": "number"},
    {"key": "actions", "label": "操作", "type": "actions", "actions": [
      {"icon": "📋", "label": "复制", "copyKey": "name"},
      {"icon": "🔗", "label": "打开", "hrefKey": "url"},
      {"icon": "👁️", "label": "详情", "desc": "查看详细信息"}
    ]}
  ],
  "data": [
    {"name": "project-a", "stars": 120, "url": "https://github.com/..."}
  ],
  "tabs": [
    {"key": "all", "label": "全部"},
    {"key": "Python", "label": "🐍 Python", "field": "lang"}
  ],
  "options": {"pageSize": 30, "exportCSV": true, "rowSelect": true}
}
```

列类型: `string`(默认) / `number` / `actions`。详见 `html-gen-table` skill。

## C 型 · 知识库 (knowledge)

**输入**: JSON 条目 + 可选类目分组  
**输出**: 顶部标签栏 + 左侧章节 + 右侧内容区

### 数据格式

```json
[
  {
    "title": "条目名称",
    "group": "所属类目",
    "section": "子分类",
    "badge": "标记",
    "desc": "<p>HTML 内容（内联渲染）</p>",
    "url": "detail.html"
  }
]
```

- `title`(必填): 条目名称
- `group`(必填): 所属类目，对应顶部 Tab
- `section`(可选): 子分类，侧栏分组
- `badge`(可选): 标记文本
- `desc`: 内联 HTML 内容（与 url 二选一）
- `url`: 外部 HTML 路径（iframe 加载，与 desc 二选一）

### 类目分组（可选）

```json
[
  {"key": "Agent 框架", "label": "🤖 Agent 框架", "icon": "🤖"},
  {"key": "HTML 工具", "label": "🌐 HTML 工具", "icon": "🌐"}
]
```

不提供 groups 时，从条目的 `group` 字段自动推导。

### 用法

```shell
# 自动推导类目
html-gen knowledge -d data.json --title "知识库" -o kb.html

# 指定类目
html-gen knowledge -d data.json -g groups.json --title "知识库" --welcome "从上方类目选择" -o kb.html
```

## AI 工作流程

当用户要求生成 HTML 页面时：

1. **确定类型**: 根据用户需求选择 A/B/C/D 型
2. **准备数据**: 
   - B/D 型: 按规范编写 Markdown 文件
   - A/C 型: 按 schema 编写 JSON 数据文件
3. **生成**: 执行对应 CLI 命令
4. **交付**: 输出 `.html` 文件路径

### 典型场景

**场景 1: 将笔记转为文档**
```shell
html-gen doc -i notes.md -o notes.html --title "学习笔记"
```

**场景 2: 生成课件幻灯片**
```shell
html-gen slide -i lecture.md -o lecture.html --title "第3讲" --subtitle "课件"
```

**场景 3: 生成项目索引页**
```json
// data.json
[{"name": "repo-a", "stars": 120, "lang": "Python"}]
```
```shell
html-gen table -d data.json --title "项目列表" -o index.html
```

## 常见问题

### Q: Markdown 中的 `<script>` 会被执行吗？
不会。`_md_escape()` 转义 `&` `<` `>`，安全。

### Q: 生成的 HTML 为什么没有图片？
Markdown 图片语法 `![alt](url)` 不解析。用 `<img src="...">` 代替。

### Q: 列表缩进子项没渲染？
不支持缩进子列表，改为平铺写法。

## 验证清单

- [ ] Markdown 语法符合上述规范（无缩进子列表、无 `![img]`）
- [ ] JSON 数据格式正确（A/C 型）
- [ ] CLI 命令执行成功，输出 `✅ 已生成: xxx.html`
- [ ] 生成的 HTML 在浏览器中正常渲染
- [ ] 链接、表格、代码块显示正确


## 变更记录
- v2.3.0 (2026-08-06): 新增 frontmatter 自动剥离; 修复 doc/slide 侧边栏 sticky 失效
- v2.2.0 (2026-08-06): 新增 quickFilter/freeze 列属性、datetime/pills 列类型、clickModes 选项
