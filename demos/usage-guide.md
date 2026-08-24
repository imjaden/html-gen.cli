# html-gen · CLI 使用说明

---

> 三层模板架构的 CLI 生成器：将 Markdown/JSON 注入模板，输出自包含单文件 HTML。
> 零外部依赖，生成即用。

---

## 一、概述

`html-gen` 是 HTML 模板系统的 **Layer 3** — CLI 生成器。它读取 Layer 2 模板，注入数据，输出单HTML 文件。

### 三层架构

```
Layer 1: style-guide.css       组件基座（CSS 变量/按钮/表格/弹窗/分页）
Layer 2: layout-*.html         模板骨架（A 型表格 / B 型文档 / C 型知识库）
Layer 3: html-gen.py            CLI 生成器（doc / table / knowledge）
```

### 安装

```shell
pip install -e /path/to/html-templates
```

或直接运行：

```shell
python /path/to/html-gen.py <子命令> [参数]
```

---

## 二、子命令总览

| 子命令 | 模板 | 输入 | 输出场景 |
|:---|:---|:---|:---|
| `doc` | layout-doc.html | `.md` Markdown | 分析报告、技术文档、长文阅读 |
| `table` | layout-table.html | `.json` 数据 | 文件索引、收藏管理、项目列表 |
| `knowledge` | layout-knowledge.html | `.json` 条目 + 类目 | 知识库、面试准备、项目 Wiki |

---

## 三、doc — Markdown 转文档

### 用法

```shell
html-gen doc -i report.md -o report.html
html-gen doc -i analysis.md --title "竞品分析报告" -o output.html
```

### 参数

| 参数 | 说明 | 必填 |
|:---|:---|:---:|
| `-i, --input` | 输入 Markdown 文件路径 | ✅ |
| `-o, --output` | 输出 HTML 路径（默认同目录同名.html） | |
| `--title` | 覆盖文档标题（默认从 `# 标题` 提取） | |
| `--subtitle` | 副标题（显示在侧边栏和页头） | |

### 自动元信息

生成时自动注入以下元信息到文档顶部：

| 项目 | 来源 | 格式示例 |
|:---|:---|:---|
| 路径 | 文件绝对路径 | `~/Documents/report.md` |
| 创建时间 | 文件 `st_ctime` | `2026-07-07 14:30` |
| 编辑时间 | 文件 `st_mtime` | `2026-07-07 16:45` |
| 字数 | `len(text.split())` | `1,234` |
| 阅读时长 | 字数 ÷ 200 | `6 分钟` |

### 支持的 Markdown 语法

| 语法 | 写法 | 说明 |
|:---|:---|:---|
| **标题** | `# h1` / `## h2` / `### h3` | 仅 3 级，h2/h3 自动加入 TOC |
| **加粗** | `**文字**` | 全局有效，表格内也支持 |
| **斜体** | `*文字*` | `**` 优先匹配 |
| **行内代码** | `` `code` `` | 在 `<pre><code>` 内无效 |
| **链接** | `[文字](url)` | 自动 `target="_blank"` |
| **图片** | 不解析（安全限制） | 用纯 HTML `<img>` |
| **围栏代码块** | ` ``` ` 或 ` ```` ` | 支持变长 fence 嵌套，关闭行必须纯反引号无文字 |
| **表格** | `\| A \| B \|` | 第二行 `\|:---\|:---\|` 标记对齐 |
| **无序列表** | `- 列表项` | 连续自动合并 |
| **有序列表** | `1. 列表项` | 连续自动合并 |
| **分隔线** | `---` | 连续 3+ 短横 |
| **引用** | `> 文字` | 单行模式 |
| **Callout** | `> **Note:** 文字` | 支持 Note/Tip/Warning/Danger + 中文 |

### 更多功能

| 功能 | 说明 |
|:---|:---|
| **自动 TOC** | 从 h2/h3 生成侧边栏目录，平滑滚动 |
| **滚动高亮** | 当前阅读章节自动高亮 |
| **代码复制** | 悬停出现复制按钮，`execCommand` 兜底 |
| **代码行号** | 多行代码块左侧 CSS 行号，单行跳过 |
| **锚点链接** | h2/h3 悬浮 ¶，点击复制 `#id` |
| **Callout 提示框** | Note/Tip/Warning/Danger 彩色边框 |
| **外链归档** | 自动提取链接，去重排序追加到底部 |
| **阅读进度条** | 顶部固定 2px 进度条 |
| **图片灯箱** | 点击放大，Escape/外部点击关闭 |
| **零外部依赖** | 自包含单文件 HTML |

---

## 四、table — JSON 转数据表格

### 用法

```shell
html-gen table -d data.json -o index.html
html-gen table -d data.json --title "项目列表"
```

### 参数

| 参数 | 说明 | 必填 |
|:---|:---|:---:|
| `-d, --data` | JSON 数据文件路径 | ✅ |
| `--title` | 页面标题（默认「数据表格」） | |
| `-o, --output` | 输出 HTML 路径（默认 `index.html`） | |

### 数据格式

```json
[
  {
    "项目": "Hermes Agent",
    "Star": 50200,
    "语言": "Python",
    "最后提交": "2026-07-06"
  }
]
```

### 列定义规则

| 规则 | 说明 |
|:---|:---|
| **自动推导** | 从第一条记录的 key 自动生成列名 |
| **顺序** | 按 JSON 字段顺序排列 |
| **列宽** | 自动适应内容 |
| **支持 HTML** | 单元格内容可包含 `<a>` `<code>` 等标签 |

### 功能特性

| 功能 | 说明 |
|:---|:---|
| **实时搜索** | 按任意字段全文匹配，输入即过滤 |
| **多字段排序** | 点击表头切换升/降序 |
| **客户端分页** | 每页 30 条，自动计算页数 |
| **深色主题** | 与 style-guide.css 一致 |
| **无数据提示** | 搜索无结果时显示「无匹配数据」 |

---

## 五、knowledge — JSON 转知识库

### 用法

```shell
# 最简单的启动（自动从数据推导类目）
html-gen knowledge -d data.json -o kb.html

# 带自定义分组
html-gen knowledge -d data.json -g groups.json \
  --title "技能知识库" \
  --welcome "从上方类目选择" \
  -o kb.html
```

### 参数

| 参数 | 说明 | 必填 |
|:---|:---|:---:|
| `-d, --data` | 条目 JSON 数据 | ✅ |
| `-g, --groups` | 类目分组 JSON（可选，自动推导） | |
| `--title` | 知识库标题 | |
| `--subtitle` | 副标题 | |
| `--welcome` | 欢迎面板提示文本 | |
| `-o, --output` | 输出 HTML 路径 | |

### 数据格式

```json
[
  {
    "title": "Hermes Agent",
    "group": "Agent 框架",
    "section": "核心工具",
    "badge": "能讲",
    "desc": "<p>功能说明...</p>",
    "url": "detail.html"
  }
]
```

### 字段说明

| 字段 | 说明 | 必填 |
|:---|:---|:---|
| `title` | 条目名称（侧栏显示） | ✅ |
| `group` | 所属类目（对应横向 Tab） | ✅ |
| `section` | 子分类（侧栏分组） | |
| `badge` | 标记文本（如熟练度） | |
| `desc` | 内联 HTML 内容（无 url 时显示） | |
| `url` | 外部 HTML 路径（优先于 desc，iframe 加载） | |

### groups.json（可选）

```json
[
  { "key": "Agent 框架", "label": "Agent 框架", "icon": "🤖" },
  { "key": "HTML 工具",  "label": "HTML 工具",  "icon": "🌐" }
]
```

### 功能特性

| 功能 | 说明 |
|:---|:---|
| **顶部标签栏** | 横向切换大类目，左侧章节跟随 |
| **左侧章节列表** | 含熟练度/标记 badge |
| **双内容模式** | 有 `url` → iframe 加载；有 `desc` → 内联渲染 |
| **欢迎面板** | 空状态提示，显示类目图例 |
| **移动端自适应** | 侧边栏可收起 |

---

## 六、路径与模板

### 文件结构

```
html-templates/
├── style-guide.css             Layer 1 样式基座
├── layout-doc.html             Layer 2 B 型文档模板
├── layout-table.html           Layer 2 A 型表格模板
├── layout-knowledge.html       Layer 2 C 型知识库模板
└── html-gen.py                 Layer 3 CLI 生成器

html-demos/
├── index.html                  模板展示首页
├── demos-index.html            A 型文档索引
├── template-*-guide.html       各方案使用说明
├── *_demo.html                 各类型案例
└── chaitin/                    商业分析案例子目录
```

### 预览

```shell
# 从 skills/ 目录启动，确保 CSS 相对路径正确
hs ~/CodeSpace/script-miner/skills --index html-demos/index.html -o
```

---

## 七、常见问题

### Q: 生成的 HTML 代码块内 `**bold**` 被渲染了？

确保 `inline_format` 不在 `<pre><code>` 内执行（v1.1+ 已修复）。

### Q: 复制按钮点了没反应？

`navigator.clipboard` 在 `http://` 非安全上下文中不可用。v1.1+ 用 `execCommand` 兜底。

### Q: 代码行号显示不正常？

移除 `.code-with-lines .line { display: block }`。行间间距由 `<pre>` 的 `line-height` 统一控制（v1.1+ 已修复）。

### Q: C 型知识库内容显示「请配置 desc 内容」？

JSON 中字段名必须是 `desc`（不是 `content`）。v1.0+ 已统一。

### Q: B 型文档中 `> **Note:**` 没有渲染为 callout？

支持半角冒号和全角冒号（`**Note:**` / `**注意**：`）。如不生效，检查关键词拼写。

### Q: 文档中的外链底部没有归档？

只有 `https?://` 开头的链接会被归档。相对路径和 `#` 锚点不归档。

---

## 迭代记录

| 版本 | 日期 | 变更 |
|:---|:---:|:---|
| v1.0 | 2026-07-07 | 初版：html-gen 完整使用说明 |
