# C 型 · 知识库方案

---

## 使用场景

知识库模板适合**多类目知识的浏览和检索**场景，是三层模板中最综合、交互最复杂的一层。

| 场景 | 说明 | 典型条目数 |
|:---|:---|:---:|
| **技能知识库** | 编程技能/工具链的整理（Agent、HTML、CLI 等） | 10-100 条 |
| **面试准备** | 按主题分类的面试题和答案整理 | 10-50 条 |
| **项目 Wiki** | 多个项目的文档集合，按项目/模块归类 | 10-200 条 |
| **学习笔记系统** | 按学科/课程分类的学习笔记汇总 | 20-300 条 |

### 不适合的场景

- **单篇长文**（仅一个类目 → 用 B 型文档）
- **结构化数据浏览**（需要排序/搜索表格 → 用 A 型表格）
- **实时协作**（C 型是只读知识索引，不是编辑器）

---

## 方案设计

### 架构

```
Layer 1: style-guide.css (CSS 变量 + 组件基座)
Layer 2: layout-knowledge.html (骨架: 顶部标签 + 左侧章节 + 右侧内容)
Layer 3: html-gen.py → knowledge 子命令 (JSON 数据注入)
```

### 数据流

```
JSON 数据文件 ──→ html-gen knowledge ──→ 单文件 HTML
                  │                       ├── 顶部标签栏
  (可选)          │                       ├── 左侧章节列表
  groups.json ────┤                       ├── 右侧内容面板
                  │                       └── 欢迎面板
                  └── 自动推导类目分组
```

### 界面结构

```
┌─ 顶部标签栏 ─────────────────────────────────────────────────┐
│  [技能]  [工具]  [框架]  [最佳实践]                           │
├─ 左侧章节 ──────────┬─ 右侧内容 ─────────────────────────────┤
│  ▸ Hermes Agent     │  # 标题                                │
│  ▸ OpenClaw         │                                        │
│  ▸ Claude Code      │  内联内容 / iframe / 欢迎面板          │
│  ▸ Codex CLI        │                                        │
│  ▸ OpenCode         │                                        │
└──────────────────────┴────────────────────────────────────────┘
```

### 关键设计决策

| 决策 | 选择 | 理由 |
|:---|:---|:---|
| **导航模式** | 顶部标签 + 左侧章节 | 两级导航，适合 3-10 个类目 × 每个类目 3-30 条 |
| **数据格式** | JSON 嵌入 | 与 A/B 型一致，CLI 工具链天然适配 |
| **类目分组** | 自动推导 + 可选 groups.json | 快速上手时可省去分组配置文件 |
| **内容渲染** | 内联 HTML | 内容字段直接作为 HTML 展示，支持格式化文本 |
| **欢迎面板** | 空状态展示 `--welcome` 文本 | 未选中条目时的提示信息 |
| **熟练度 badge** | 颜色编码（红/黄/蓝/灰） | 快速标识掌握程度 |
| **移动端** | 顶部可滑动标签 + 侧边栏可收起 | 小屏设备上的可用性保障 |

---

## 行业对标

| 维度 | C 型 · 知识库 | Notion Wiki | Confluence | GitBook |
|:---|:---|:---|:---|:---|
| **定位** | 知识索引 + 浏览 | 团队知识库 | 企业知识库 | 文档发布平台 |
| **部署** | 单文件 HTML | SaaS | SaaS/自建 | SaaS |
| **数据源** | JSON 注入 | 内置数据库 | 内置数据库 | Markdown |
| **导航** | 标签 + 章节 | 侧边栏树 | 侧边栏树 | 侧边栏树 |
| **搜索** | ❌ 暂无 | ✅ 全文 | ✅ 全文 | ✅ 全文 |
| **标签切换** | ✅ | ⚠️ 需配置 | ✅ | ⚠️ 需配置 |
| **熟练度 badge** | ✅ 内置 | ❌ 自建 | ❌ 插件 | ❌ 自建 |
| **离线** | ✅ 单文件 | ❌ 需网络 | ❌ 需网络 | ❌ 需网络 |
| **外部依赖** | 零 | 需要 JS 框架 | 需要网络 | CDN |
| **文件大小** | ~22KB（含 15 条） | N/A | N/A | N/A |

**核心差异**：C 型专注于「知识索引 + 快速浏览」场景，是知识库的轻量级前端。适合知识管理流程中「先收拢再深度消费」的前半步。

---

## 功能清单

### 已实现 ✅

| 功能 | 说明 | 优先级 |
|:---|:---|---:|
| 顶部标签栏 | 按大类目切换，标签自动匹配 | P0 |
| 左侧章节列表 | 当前类目下的条目列表，含熟练度 badge | P0 |
| 右侧内容面板 | 选中条目后展示内容（HTML 内联渲染） | P0 |
| 欢迎面板 | 未选定条目时显示提示信息 | P0 |
| 自动分组推导 | 从数据 JSON 的 `group` 字段自动归类 | P0 |
| 可选 groups.json | 自定义类目顺序、图标、显示名称 | P0 |
| 深色主题 | 与 style-guide.css 一致的 surface-950 深色主题 | P0 |
| 零外部依赖 | 单文件 HTML，无需加载 CDN | P0 |
| URL 参数同步 | 点击菜单/页签实时写 group/item 到 URL；带 URL 打开定位指定页（拷贝中文原文链接） | P0 |
| 记忆恢复 | URL 参数优先 > localStorage（kw_group/kw_item）> 默认；group 单独恢复 | P0 |
| iframe 加载 + 内联渲染 | 有 url → iframe 加载；有 desc → 内联渲染；空态欢迎面板 | P0 |
| 概述页宽屏 | url 含 overview 时 iframe 自动附加 width=wide（doc 1280px） | P0 |
| 跨组 section 保持 | 切顶部 tab 时左侧选中 section 跨组跟随（如 36计策 ↔ 36计策） | P0 |
| section 图标 | 数据 section_icon 字段渲染图标前缀（📋/📅/🧮） | P1 |
| 侧边栏折叠/搜索 | 折叠 48px（`[` 快捷键）；🔍 搜索 150ms debounce 过滤 | P1 |
| 裸模式 (Bare) | 默认隐藏 sidebar/toolbar，?sidebar=1&toolbar=1 展示；嵌入 iframe 自动降级 | P1 |
| 单条目 section 直开 | 单条目 section 点击标题直接加载 (K2) | P1 |

### 待实现 🔜

| 功能 | 说明 | 优先级 |
|:---|:---|:---:|
| 搜索 | 跨类目搜索条目标题和内容 | P1 |
| 标签筛选 | 按标签/熟练度筛选当前类目下的条目 | P2 |
| 书签/收藏 | 标记常用条目，在顶部显示收藏夹 | P2 |
| iframe 深度内容 | 点击条目后在 iframe 中加载外部内容 | P2 |
| 内容编辑 | 内联编辑条目，支持 JSON 写回 | P3 |
| 版本历史 | 条目的修改记录追踪 | P3 |
| 键盘导航 | ← → 切换标签，↑↓ 切换条目，Enter 打开 | P3 |
| 折叠/展开 | 条目支持折叠展开，节省空间 | P3 |

---

## 快速开始

```shell
# 最简单的启动
html-gen knowledge -d data.json -o kb.html

# 带自定义分组和标题
html-gen knowledge \\
  -d data.json -g groups.json \\
  --title "HTML 技能知识库" \\
  --welcome "从上方类目选择" \\
  -o kb.html
```

### 数据格式

```json
[
  {
    "title": "Hermes Agent 介绍",
    "group": "Agent 框架",
    "badge": "🟢",
    "content": "<p>Hermes Agent 是...</p>"
  }
]
```

### groups.json（可选）

```json
[
  { "key": "Agent 框架", "label": "Agent 框架", "icon": "🤖" },
  { "key": "HTML 工具",  "label": "HTML 工具",  "icon": "🌐" }
]
```

### 命令行参数

```
html-gen knowledge -h
  -d, --data FILE     条目 JSON 数据（必需）
  -g, --groups FILE   类目分组 JSON（可选）
  --title TEXT        知识库标题
  --subtitle TEXT     副标题
  --welcome TEXT      欢迎面板文本
  -o, --output FILE   输出 HTML
```

---

## 模板案例

该模板的精选案例（html-gen demo list ★ featured，路径相对 demos/）：

| 案例 | 说明 | 文件 |
|:---|:---|:---|
| [以剧读史 · 影视历史知识库](../drama-knowledge.html) | 中国历史 / 大明王朝1566 / 雍正王朝 3 组 · 概述/时间轴/36计策 | drama-knowledge.html |
| [长亭科技 · 商业分析知识库](../chaitin-business-analysis.html) | 4 个大类 · 14 个条目 · 售前架构师视角 | chaitin-business-analysis.html |
| [云智慧 · 商业分析知识库](../cloudwise-business-analysis.html) | 智能运维 AIOps · 监控宝/透视宝/压测宝 · 12 条目 | cloudwise-business-analysis.html |
| [knowledge 模板 demo](../features/knowledge-demo.html) | 模板基础功能演示 | features/knowledge-demo.html |

---

## 迭代记录

| 版本 | 日期 | 变更 |
|:---|:---:|:---|
| v1.0 | 2026-07-05 | 初版：顶部标签 + 左侧章节 + 右侧内容 |
| v2.0 | 2026-08-11 | Bare 模式 + 折叠/搜索/记忆恢复 + 单条目直开 |
| v2.1 | 2026-08-18 | URL 参数同步（group/item 实时写 URL + 恢复优先）+ section 图标 + 隐藏搜索/折叠按钮 |
| v2.2 | 2026-08-19 | 跨组 section 保持；概述页 iframe 宽屏 width=wide；标题点击复制中文 URL |
| v2.3 | 2026-08-23 | 新增「模板案例」章节（★ featured 精选） |
