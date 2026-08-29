# A 型 · 数据表格方案

---

## 使用场景

数据表格适用于**结构化数据的浏览和检索**场景，是三层模板中最基础、最通用的一层。

| 场景 | 说明 | 典型数据量 |
|:---|:---|:---:|
| **文件索引** | 文档/图片/代码文件的目录清单，含路径、大小、日期 | 10-500 行 |
| **收藏管理** | 来自各平台的书签、收藏、笔记汇总表格 | 10-200 行 |
| **项目列表** | 多项目概览（名称、状态、Star 数、最后提交日期） | 5-50 行 |
| **数据浏览** | JSON/CSV 的快速预览，替代电子表格 | 10-1000 行 |
| **审计日志** | 操作记录、版本变更、事件追踪 | 50-10000 行 |

### 不适合的场景

- **长文本阅读**（>200 字/字段 → 用 B 型文档）
- **多类目知识库**（需要标签切换 → 用 C 型知识库）
- **图表/可视化**（数据表格不提供绘图功能）

---

## 方案设计

### 架构

```
Layer 1: style-guide.css (CSS 变量 + 组件基座)
Layer 2: layout-table.html (模板骨架)
Layer 3: html-gen.py → table 子命令 (数据注入)
```

### 数据流

```
JSON 文件 ──→ html-gen table ──→ 单文件 HTML
             │                    ├── 搜索
             │                    ├── 排序
             │                    └── 分页
             └── 列定义自动推导
```

### 关键设计决策

| 决策 | 选择 | 理由 |
|:---|:---|:---|
| **数据格式** | JSON 原生 | CLI 工具链天然适配，可直接从 API/脚本输出 |
| **列定义** | 自动推导 | 减少配置文件，第一个 record 的 keys 即为列名 |
| **排序** | 客户端 JS | 无需后端，数据量 10K 以内表现良好 |
| **分页** | 客户端 JS | 每页 30 条，自动计算页数 |
| **搜索** | 客户端 JS | 实时过滤，按任意字段匹配 |
| **样式** | style-guide.css inline | 零外部依赖，单文件嵌入 |

### 移动端响应

表格在屏幕宽度 <768px 时启用横向滚动，列头固定。移动端隐藏非关键列（摘要模式）。

---

## 行业对标

| 维度 | A 型 · 数据表格 | Airtable | Notion 表格 | Excel Online |
|:---|:---|:---|:---|:---|
| **定位** | 文件级数据展示 | 协作数据库 | 团队知识库 | 电子表格 |
| **部署** | 单文件 HTML | SaaS | SaaS | SaaS |
| **数据源** | 本地 JSON | 内置数据库 | 内置数据库 | 云端文件 |
| **搜索** | ✅ 实时 | ✅ 实时 | ✅ 实时 | ✅ 查找 |
| **排序** | ✅ 多字段 | ✅ 多字段 | ✅ 多字段 | ✅ 多字段 |
| **分页** | ✅ 客户端 | ✅ 虚拟滚动 | ✅ 虚拟滚动 | ❌ 无分页 |
| **离线** | ✅ 完整 | ❌ 需要网络 | ❌ 需要网络 | ✅ 桌面版 |
| **依赖** | 零外部依赖 | 需要 JS 框架 | 需要 JS 框架 | 浏览器 |
| **文件大小** | ~13KB | N/A | N/A | N/A |

**核心差异**：A 型追求极简和零依赖，适合作为 CI/CD 产物、静态站点的一部分或临时数据查看工具。不是 Notion/Airtable 的替代品，而是在「需要快速展示结构化数据」场景下的轻量级补充。

---

## 功能清单

### 已实现 ✅

| 功能 | 说明 | 优先级 |
|:---|:---|---:|
| JSON 数据注入 | 从 JSON 文件读取，自动推导列名 | P0 |
| 实时搜索 | 按任意字段全文匹配，输入即过滤 | P0 |
| 多字段排序 | 点击表头切换升/降序，支持多重排序 | P0 |
| 客户端分页 | 每页 30 条，自动计算总页数和条目数 | P0 |
| 深色主题 | 与 style-guide.css 一致的 surface-950 深色背景 | P0 |
| 搜索无结果提示 | 搜索不到内容时显示 "没有匹配项" | P0 |
| 显示 N/M 计数 | 工具栏显示 "显示 X / Y 条" | P0 |
| 列自动宽度 | 表头固定，内容自适应 | P0 |
| 零外部依赖 | 单文件 HTML，无需加载 CDN 脚本 | P0 |
| 序号列 (showIndex) | OPTIONS.showIndex 渲染首列序号，Cinema 模型 42px 显式宽度 | P0 |
| 整行详情字段 (splitFull) | 字段在分栏详情占整行宽，`\n`→`<br>` 段落渲染（原文/白话/历任皇帝） | P0 |
| 默认筛选 (defaultFilter) | options.defaultFilter {key,value} 加载后自动筛选（大明时间轴默认嘉靖） | P0 |
| pills 列整格 split | 标签列整格点击开分栏，pill 点击筛选 stopPropagation 共存 | P0 |
| 行高统一 | td 7px 8px + cell-pill vertical-align:middle → 全类型表 34-35px | P0 |
| 列隐藏 (initialHidden/hide) | 默认隐藏列（设置面板可开）；永不可见列 | P1 |
| 列冻结 / 右侧固定 | col.freeze sticky 左列；col.stickyRight 视口右侧固定 | P1 |
| 分栏模式列过滤 | col.preview 仅预览列显示于分栏；options.columnsSplit 指定列集 | P1 |
| 视图预设 | 保存/加载/删除设置（密度/模式/排序/列可见性，≤2KB×10） | P1 |
| 操作按钮列 | actions 列：copyKey/hrefKey/desc/handler 四种按钮 | P1 |
| 多标签页 | TABS 定义标签切换 + count | P1 |
| CSV 导出 / 批量操作 | exportCSV / rowSelect 工具栏（全选/取消/导出） | P2 |
| 列宽拖拽记忆 | 拖拽 resize 直接操作 DOM，localStorage 持久化 (html-gen:table:col-widths) | P2 |
| 快捷搜索 (Cmd+F) | Spotlight 弹窗搜索 (150ms debounce) | P2 |
| 密度切换 / 设置面板 | 紧凑/标准/舒适 + ⚙️ 下拉（列可见性/视图预设） | P2 |

### 待实现 🔜

| 功能 | 说明 | 优先级 |
|:---|:---|:---:|
| 批量选择 | 多行勾选，支持批量复制/删除 | P1 |
| 行详情面板 | 点击行展开详情侧栏，展示完整字段 | P1 |
| 导出 CSV | 一键导出当前筛选结果 | P2 |
| 自定义筛选 | 按指定字段 + 操作符（= / != / contains）组合过滤 | P2 |
| 列拖拽调整 | 拖拽表头调整列宽和列顺序 | P3 |
| 单元格编辑 | 双击单元格直接编辑值，支持 JSON 写回 | P3 |
| 多数据源切换 | 页面内切换不同 JSON 数据集 | P3 |
| 键盘导航 | ↑↓ 选行，Enter 展开详情 | P3 |

---

## 快速开始

```shell
# 准备数据
cat data.json

# 生成表格
html-gen table -d data.json -o index.html

# 在浏览器打开
open index.html
```

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

> **输出目标（CL003）**：结构化 JSON 顶层可带 `"output": "demos/xxx.html"` 指定渲染目标。优先级 CLI `-o` > JSON `output`；均无 → 提示中断（exit 1）。简单数组格式无元数据能力，必须 CLI `-o`。

### 数据源维护指南

#### 数据源与产物的关系

**数据 JSON 是唯一事实源，生成的 HTML 是产物**：

- 源：`data/_drama-table-*.json`（结构化格式：`columns` + `data` + 可选 `tabs`/`options`/`title`/`subtitle`）
- 产物：`demos/drama/*.html`（`html-gen table` 生成）
- **永不手改产物 HTML**：直接改 `const COLUMNS` / `const DATA` 会在下次重新生成时被静默覆盖，且源 JSON 保持旧值 → 双源漂移

映射链：`layout-table.html` 的 `<!--COLUMNS-->` 占位符 ← `html-gen.py` 注入 `json.dumps(columns)` ← 数据 JSON 的 `columns` 数组。

#### const COLUMNS 如何修改

HTML 里的 `const COLUMNS` 与数据 JSON 的 `columns` 数组一一对应，每个对象是一个列定义。**改列 = 改 JSON 的 columns 数组 + 重新生成**：

```json
{
  "columns": [
    { "key": "strategy", "label": "计名", "sortable": true, "locale": "zh",
      "width": "90px", "freeze": true, "preview": true, "onCellClick": "split" }
  ],
  "data": [
    { "strategy": "瞒天过海", "category": "胜战计" }
  ]
}
```

列属性速查（对应 COLUMNS 元素属性）：

| 字段 | 说明 |
|:---|:---|
| `key` | 必填，列标识，与 `data` 行内字段名一致 |
| `label` | 表头显示名 |
| `type` | `string`（默认）/ `number` / `pills` / `actions` |
| `sortable` | 是否可排序（默认 true） |
| `locale` | 排序 locale，如 `"zh"` 中文排序 |
| `width` | 必填（影院宽度模型，默认 fallback 120px） |
| `freeze` | sticky 冻结列 |
| `stickyRight` | 右侧固定列 |
| `preview` | 分栏模式是否显示 |
| `hide` | 永远隐藏（数据保留） |
| `initialHidden` | 表格默认隐藏，仅预览可见 |
| `splitFull` | 分栏预览整行宽 + `\n` 转 `<br>`（多行文本用这个） |
| `onCellClick` | `"split"` 点击单元格直接开分栏 |
| `quickFilter` / `pillFilter` | 点击筛选相关 |

#### 字段操作三路径

**修改字段内容**：改 `data` 数组 → 目标行对象 → 对应 key 的值 → 重新生成。

**添加字段（新增一列）**：
1. `columns` 数组 push 一个对象（必给 `key`/`label`/`width`，按需 `preview`/`initialHidden`/`splitFull`）
2. `data` 数组**每一行**都要补该 key（缺失渲染空单元格）
3. 重新生成

**添加字段（新增一行）**：`data` 数组 push 一个包含所有 columns key 的对象。

**删除字段（删一列）**：
- 彻底删：`columns` 移除定义 + 所有行删除该 key → 重新生成
- 保留数据仅隐藏：列上加 `"hide": true`，可逆

**删除字段（删一行）**：`data` 数组移除该对象。

#### 页面级描述（title / subtitle）

table 模板支持 h1 下方段落式描述（`--subtitle`，纯文本安全转义，`\n` → `<br>` 换行）。取值优先级：**CLI 显式入参 > JSON 顶层字段 > 默认值**。

```json
{
  "title": "中国历史 · 三十六计",
  "subtitle": "第一行\n第二行",
  "columns": [],
  "data": []
}
```

- CLI 传 `--subtitle` 覆盖 JSON；传 `--subtitle ""` 清空描述
- 简单数组格式（纯数组）无法内嵌元数据，仅 CLI 可传
- 无 subtitle 时描述区不渲染，输出与旧版一致

#### 生成 / 验证 / 提交纪律

```shell
# 重新生成（title 必须与现 <title> 一致，否则标题漂移）
html-gen table -d data/_drama-table-history-strategy.json \
  --title "中国历史 · 三十六计" --subtitle "..." \
  -o demos/drama/history-strategy-table.html

# 验证（定向或全量）
python3 -m pytest tests/test_history_tables.py -q -n 0
python3 -m pytest tests/ -q -n 4

# 提交（数据 + 产物成对）
git add data/_drama-table-history-strategy.json demos/drama/history-strategy-table.html
git commit -m "data@drama: ..."
```

#### 案例：多行字段内容（借刀杀人 event）

历史教训：某次直接修改了产物 `demos/drama/history-strategy-table.html` 里 `const DATA` 的 `event` 字段（借刀杀人 → "计策演变 + 经典案例"多行长文本），源 JSON 未同步。后果：下次重新生成会覆盖手改内容；源 JSON 保持旧值 → 双源漂移。

正确路径：
1. 把长文本写入 `data/_drama-table-history-strategy.json` 借刀杀人行的 `"event"`（JSON 内换行用 `\n` 转义）
2. 该列加 `"splitFull": true`（分栏预览才把 `\n` 转 `<br>`，否则多行文本折叠成一行）
3. 重新生成 + 跑测试 + 成对提交

### 命令行参数

```
html-gen table -h
  -d, --data PATH    JSON 数据文件（必需）
  --title TEXT       页面标题（优先级: CLI > JSON 顶层 title > "数据表格"）
  --subtitle TEXT    页面级段落描述（纯文本, \n 换行; JSON 顶层 subtitle 兜底, 显式传空串清空）
  -o, --output FILE  输出 HTML 路径（必填: CLI -o 或 JSON 顶层 output 二选一; 均无 → 提示中断 exit 1）
```

---

## 模板案例

该模板的精选案例（html-gen demo list ★ featured，路径相对 demos/）：

| 案例 | 说明 | 文件 |
|:---|:---|:---|
| [DEMO 案例索引](demos-index.html) | 全量案例索引 · 标题/模板/链接 | demos-index.html |
| [Hermes Skills 清单](hermes-profile-skills-list.html) | 98 个 Skill · 15 个分类 · 全 Profile | hermes-profile-skills-list.html |
| [全球国家速查表](countries-table.html) | 国家速查 · 地区/首都/货币 | countries-table.html |
| [中国省份速查表](provinces-table.html) | 34 省 · 面积/GDP/人口 | provinces-table.html |
| [表格功能全演示](table-features-demo.html) | 密度/模态/分栏/展开/过滤/冻结/预设 | table-features-demo.html |
| [操作按钮 demo](table-actions-demo.html) | copyKey/hrefKey/handler 操作列 | table-actions-demo.html |

---

## 迭代记录

| 版本 | 日期 | 变更 |
|:---|:---:|:---|
| v1.0 | 2026-07-01 | 初版：JSON 注入 + 搜索 + 排序 + 分页 |
| v1.1 | 2026-07-06 | 列自动推导（移除 cols.json）、搜索无结果提示 |
| v2.0 | 2026-07-22 | 结构化格式：columns/tabs/options；操作按钮列、多标签、CSV 导出、列可见性、列宽拖拽 |
| v2.1 | 2026-08-18 | 行高统一 34-35px；showIndex 序号列；splitFull 整行字段；defaultFilter 默认筛选；pills 列整格 split |
| v2.2 | 2026-08-19 | 36计/时间轴重构列模型；视图预设；设置面板；列冻结/右侧固定；分栏列过滤 |
| v2.3 | 2026-08-23 | 新增「模板案例」章节（★ featured 精选） |
