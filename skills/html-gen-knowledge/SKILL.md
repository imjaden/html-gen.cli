---
name: html-gen-knowledge
description: html-gen C 型知识库模板规范。使用 html-gen knowledge 命令生成分 tab 侧栏的知识库页面时参考。
version: 1.0.0
author: dev
license: MIT
metadata:
  related_skills: [html-gen, html-gen-table, html-gen-doc]
---

# html-gen C 型知识库规范

## 概述
C 型知识库通过顶部 tab 分组、左侧 section-as-menu 的导航结构，以 iframe 或内联 HTML 展示内容。专为多主题知识索引场景设计。

## 何时使用
- 多主题知识索引（如以剧读史、技术文档索引）
- 需要 tab 切换 + 侧栏导航的知识库
- section 与 item 一对一时可跳过 item 行直接点击 section 标题

## CLI 用法

```
html-gen knowledge -d data.json [-g groups.json] [--title "标题"] [--welcome "欢迎语"] [-o kb.html]
```

> 逐 flag 清单、默认值（`--title` 默认「知识库」、`--welcome` 默认欢迎文案）与输出目标三态
> 见 **`html-gen help knowledge`** 的「CLI 参数」段。

## 数据格式

条目 **9 键**（契约真值 = `TEMPLATE_CONTRACT['knowledge']['data']['item']`，`html-gen help knowledge` 的「item 条目键」段同源）：

| 键 | 必填 | 说明 |
|:---|:---:|:---|
| `title` | ✅ | 条目名称（侧栏文本，单行 ellipsis；长名配 `page_title`） |
| `group` | ✅ | 所属类目，**必须与 `groups[].key` 全等**（对不上会自建 tab 或被丢弃） |
| `section` | | 子分类（侧栏分组）；`title === section` 且组内仅 1 条时自动跳过该行（K2 rule） |
| `badge` | | 侧栏条目右侧徽标（如 `P0` / `skill`） |
| `desc` | △ | 条目正文 HTML，**内联渲染**；与 `url` 二选一 |
| `url` | △ | 详情页地址，**iframe 加载**；与 `desc` 二选一；必须与知识库页同源 |
| `icon` | | 条目 emoji（无 `groups` 文件时用它推导类目图标） |
| `width` | | iframe 宽度 `narrow` / `medium` / `wide`（追加 `?width=`；缺省 `medium`，`url` 含 `overview` 时默认 `wide`） |
| `page_title` | | 侧栏悬停 tooltip 的全名（缺省用 `title`） |

数据源三态：顶层数组 / `{items: […]}` / `{data: […]}`；结构化 dict 顶层可带 `"output"`
（仅 data 文件识别，groups 文件忽略）。输出目标优先级 `-o` > JSON `output` > 均无则 exit 1。

### 最小可跑示例（2 类目 / 4 条目 / 1 个 url + 3 个 desc）

`data.json`：

```json
[
  {"title": "三步上手", "group": "指南", "section": "基础", "badge": "P0",
   "desc": "<p>装好 → 备 JSON → 跑一条命令。</p>"},
  {"title": "常见坑", "group": "指南", "section": "基础",
   "page_title": "常见坑（组名对不上 / url 与 desc 同时给）",
   "desc": "<p>group 必须与 groups[].key 全等。</p>"},
  {"title": "宽屏嵌入", "group": "示例", "section": "iframe",
   "url": "overview.html", "width": "wide",
   "page_title": "宽屏嵌入（url 含 overview ⇒ 自动 wide）"},
  {"title": "常规嵌入", "group": "示例", "section": "iframe",
   "url": "detail.html", "width": "medium"}
]
```

`groups.json`：

```json
[{"key": "指南", "label": "指南", "icon": "🧭"},
 {"key": "示例", "label": "示例", "icon": "🧩"}]
```

命令与产物：

```
html-gen knowledge -d data.json -g groups.json --title "我的知识库" \
  --welcome "点侧栏标题回根页；⌘/Ctrl+K 打开搜索面板。" -o kb.html
```

### 写完自检（6 条，机器可判）

1. 新标记齐全：`grep -c 'kwGoRoot\|kw-map-table\|kw-spot-overlay' kb.html` ≥ 3
2. `⌘F` 已归还浏览器：`grep -c "e.key !== 'f'" kb.html` = 0；`grep -c kwSearchWrap kb.html` = 0
3. 根页地图：行数 = 去重后的 `section` 数，格内条目之和 = 条目总数
4. 每个 `item.group` 都能在 `groups[].key` 里找到；每条恰好有 `url` 或 `desc` 之一
5. iframe 目标与 `kb.html` 同源，相对路径以 `kb.html` 所在目录为基准
6. 改的是模板能力（不是数据）时，按 `documents/templates.md` §影响面矩阵 逐面清点

## groups 格式

类目键（key / label / icon）见 `html-gen help knowledge` 的「groups 类目键」段。示例：

```json
[{"key": "类目key", "label": "显示名", "icon": "🏛️"}]
```

## 模板特性
- 顶部横向标签栏（按 group 分组）；切页签一律回根页，不再自动选中该组首条
- 左侧 section-as-menu（section 标题可点击跳转）
- **根页 = 欢迎语 + 菜单地图表**（列 = 横向页签，行 = `section`，格内条目名 + badge，点击直达）
- 点侧栏标题回根页（清 URL `item=` 与 localStorage）；复制路径走标题右侧 ⧉ 按钮
- **搜索面板**：`⌘/Ctrl+K` 或侧栏 🔍 打开（匹配 条目名 / 子分类 / 描述 / 全名 / 类目；`↑↓←→` / `Enter` / `Esc`；命中 `<mark>` 高亮；无匹配空态）
- `⌘F` / `Ctrl+F` **不拦截**，浏览器原生查找照旧可用（面板走 `⌘K`，两条路互不冲突）
- 折叠/展开侧边栏（`[` 快捷键，localStorage）
- 双内容模式（`url` → iframe / `desc` → 内联）
- localStorage 状态恢复（group + item）；`?view=root` 强制回根页

## 注意事项
- iframe 内容必须与知识库页面同源
- 单条 section (title===section && count===1) 自动跳过 kw-item 渲染
- Selenium headless 测试: iframe 内元素需 `driver.switch_to.frame()` 切换

## 内部分发（不同 Agent 怎么拿到本规范）

同一份规范有 4 个出口，**按调用方能力选**，不要让人去猜：

| 场景 | 能力 | 推荐通道 | 命令 / 地址 |
|:---|:---|:---|:---|
| Hermes 其他会话（本机、能跑 CLI） | 执行命令 + 读文件 | ① `html-gen prompt html-gen-knowledge`（stdout 即本页 markdown）<br>② 直接读 `skills/html-gen-knowledge/SKILL.md`（含 `references/`） | `html-gen prompt html-gen-knowledge --json` → `data.content` / `data.references` |
| Hermes 会话（要一次吃全量上下文） | 同上 | `prompts/all.md`：9 个 skill 的正文 + references 原文合集 | `html-gen prompt --site --dir /tmp/hgp && cat /tmp/hgp/all.md` |
| 只读网页的 Agent（Doubao / 浏览器插件 / 无 shell） | 只能抓 URL，不能跑命令 | ① 单页文档 `…/prompts/kb/html-gen-knowledge.html`（一页装完，解析最省事）<br>② 门户深链 `…/prompts/?group=knowledge&item=html-gen-knowledge`（可切其它模板）<br>③ `…/prompts/html-gen-knowledge.md`（纯 markdown，噪声最小） | 线上根：`https://html-gen.cli.jaden.tech/` |
| CI / 脚本 | 无交互 | `--json` 信封 `{status,error,data:{content,references}}` | 便于程序解析，不依赖终端宽度 |

**给外部 Agent 的开场句（可直接粘）**：

> 你是 html-gen C 型知识库案例作者。先完整读取 `<URL>`，按其中「数据格式（9 键）」「最小可跑示例」「写完自检」三节产出 `data.json` 与 `groups.json`，再按「影响面矩阵」确认改动面。

⚠️ 只读型 Agent **优先给 `kb/*.html` 或 `*.md` 原始地址**：`?group=&item=` 深链靠 JS 路由（C 型模板），抓取工具常常只拿到门户骨架。

## 变更记录
- v1.0.0 (2026-08-08): 首次提炼自 drama 知识库实施经验 + AGENTS.md
- v2.0.0 (2026-11-23): 对齐 html-gen v3.6 — 根页菜单地图 + 搜索面板（`⌘/Ctrl+K`）+ 点标题回根页 + `⌘F` 归还浏览器；移除跨组同名跟随与侧栏过滤面板
- v2.1.0 (2026-11-27): item 键 7 → **9**（补 `width` / `page_title`）；新增最小可跑示例（2 类目 4 条目）与 6 条自检清单 —— 让 AI 只读本页即可写出合规案例
