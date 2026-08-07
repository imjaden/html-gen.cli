# 以剧读史知识库表格化改造 — 设计文档

## 版本

v1.0 (2026-08-06)

## 背景与问题来源

用户预览 `demos/drama-knowledge.html`（commit 94fded2 已提交）后提出框架改造需求，核心是**侧栏一级菜单化 + 内容页表格化**：

1. 左侧的概述、时间轴、36计策菜单没有子菜单；点击时间轴菜单，则加载选中朝代的时间轴内容页。
2. 当前 概述、时间轴、36计策菜单的子菜单，可以作为该菜单内容面中的章节。
3. 时间轴菜单：内容页按朝代分多个 table 列表（table 模板）：
   - 中国历史按朝代划分（列：朝代、开始年代、结束年份、开创者（及谥号）、民族、主要事件）
   - 大明1566 按年号划分（列：年号、皇帝（及谥号）、开始年代、结束年份、主要事件）
4. 36计策菜单：以 36 计为维度展示的 table 列表（列：计策、历史事件、主要人物、结局）

待确认清单问答（用户回复 1A 2A 3A 4B 5A 6A 7A）定稿：

| 项 | 确认 |
|:--|:--|
| 1 实现形态 | A=内容页走 table 模板独立页 + knowledge iframe 加载 |
| 2 侧栏改造 | A=改 knowledge 模板，section 可点击直接加载 |
| 3 原详情页 | A=保留为表格行点击详情（onClick url / split） |
| 4 中国历史 Tab | B=含「千古名计」跨朝代表表（36计策菜单同样存在） |
| 5 大明时间轴表 | A=年号总览表 + 剧情节点表 双表 |
| 6 36计策行粒度 | A=剧中有实例的计谋（6-8 行） |
| 7 多 table 组织 | A=table 模板 tabs（tab=年号/分组） |

## 目标形态

**现状**（commit 94fded2）：
- 侧栏 = section 分组（概述/时间轴/36计策）+ item 列表（24 条）
- 内容 = desc 内联（概述/中国历史）/ 详情页 iframe（时间轴/36计策）

**目标**：
- 侧栏 = 3 个一级菜单（概述/时间轴/36计策，**无子菜单**），点击菜单直接加载当前 group 的内容页
- 内容页 = table 模板独立页（时间轴/36计策）+ doc 独立页（概述，章节式）
- 表格行点击 → 原详情页（13 个详情页保留复用）

## 数据模型

### groups（不变，2 个）

中国历史 🏛️ / 大明王朝1566 📜

### items（重写为 6 条：group × section 内容页索引）

**注意：title = section 名，必然跨 group 重复（概述×2 等）→ 模板必须按 (group, title) 查找（见 K1）。**

```json
[
  {"title": "概述",   "group": "中国历史",   "section": "概述",   "url": "drama/history-overview.html"},
  {"title": "时间轴", "group": "中国历史",   "section": "时间轴", "url": "drama/history-timeline-table.html"},
  {"title": "36计策", "group": "中国历史",   "section": "36计策", "url": "drama/history-strategy-table.html"},
  {"title": "概述",   "group": "大明王朝1566", "section": "概述", "url": "drama/daming-overview.html"},
  {"title": "时间轴", "group": "大明王朝1566", "section": "时间轴", "url": "drama/daming-timeline-table.html"},
  {"title": "36计策", "group": "大明王朝1566", "section": "36计策", "url": "drama/daming-strategy-table.html"}
]
```

侧栏渲染规则：section 标题 = 一级菜单；当某 section 仅 1 个 item 且 item.title === section 时（内容页约定），**不渲染 item 行**，section 标题直接可点（K2）。

### 表格内容页数据（新增 4 个 data 文件，走 html-gen table 结构化格式）

**T1. data/_drama-table-history-timeline.json — 朝代表（中国历史·时间轴）**

单表 5 行（一行一朝代），列：朝代 / 开始年代 / 结束年份 / 开创者（及谥号）/ 民族 / 主要事件

| 朝代 | 开始 | 结束 | 开创者（及谥号） | 民族 | 主要事件 |
|:--|:--|:--|:--|:--|:--|
| 唐 | 618 | 907 | 唐高祖李渊（神尧大圣大光孝皇帝） | 汉族（陇西李氏，胡汉交融） | 贞观之治、开元盛世、安史之乱 |
| 宋 | 960 | 1279 | 宋太祖赵匡胤（启运立极英武睿文神德圣功至明大孝皇帝） | 汉族 | 重文轻武、靖康之变、南宋偏安 |
| 元 | 1271 | 1368 | 元世祖忽必烈（圣德神功文武皇帝） | 蒙古族 | 行省制、四等人制、红巾军起义 |
| 明 | 1368 | 1644 | 明太祖朱元璋（高皇帝） | 汉族 | 废丞相设内阁、厂卫、土木堡之变 |
| 清 | 1644 | 1912 | 清太祖努尔哈赤（高皇帝，追尊） | 满族 | 康雍乾盛世、鸦片战争、辛亥革命 |

（谥号数据以正史为准，dev 阶段核定全谥/简谥展示）

**T2. data/_drama-table-daming-timeline.json — 大明时间轴（tabs 双表）**

tabs: [年号总览, 剧情节点]

- tab 年号总览（1 行）：年号 / 皇帝（及谥号）/ 开始年代 / 结束年份 / 主要事件
  - 嘉靖 / 明世宗朱厚熜（肃皇帝）/ 1522 / 1566 / 改稻为桑、严嵩专权、海瑞上疏
- tab 剧情节点（7 行）：剧情时间 / 事件 / 主要人物 / 影响 / 结局（行内 url → 原详情页）

| 剧情时间 | 事件 | 主要人物 | 影响 | 结局 |
|:--|:--|:--|:--|:--|
| 嘉靖三十九年(1560) | 改稻为桑国策出台 | 嘉靖、严嵩、严世蕃 | 国策走形，与民争利 | 埋下毁堤淹田伏笔 |
| 嘉靖三十九年夏 | 毁堤淹田九县 | 严世蕃、郑泌昌、何茂才 | 新政失民心，海瑞登场 | 杨金水装疯、郑何被清算 |
| 嘉靖三十九年(1560)前后 | 海瑞赴任淳安 | 海瑞、郑泌昌、何茂才 | 清官声望立住 | 站稳脚跟 |
| 嘉靖四十年(1561)前后 | 审通倭案 | 海瑞、郑泌昌、何茂才 | 严党浙江暴露 | 郑何落网 |
| 嘉靖四十年(1561) | 严嵩倒台 | 嘉靖、徐阶、严嵩 | 清流上位、内部分化 | 严世蕃问斩 |
| 嘉靖四十四年(1565) | 海瑞上治安疏 | 海瑞、嘉靖 | 全剧高潮 | 下诏狱、留中不发 |
| 嘉靖四十五年十二月 | 嘉靖驾崩·海瑞出狱 | 嘉靖、裕王、海瑞 | 时代落幕、新朝开启 | 海瑞名动天下 |

**T3. data/_drama-table-history-strategy.json — 千古名计表（中国历史·36计策，4B）**

单表 8 行（跨朝代经典计谋），列：计策 / 历史事件 / 主要人物 / 结局

| 计策 | 历史事件 | 主要人物 | 结局 |
|:--|:--|:--|:--|
| 卧薪尝胆 | 越王勾践灭吴 | 勾践、夫差 | 勾践称霸 |
| 围魏救赵 | 桂陵之战 | 孙膑、庞涓 | 齐军大胜 |
| 明修栈道，暗度陈仓 | 楚汉相争 | 韩信、刘邦 | 还定三秦 |
| 远交近攻 | 秦灭六国 | 范雎、秦王政 | 秦统一天下 |
| 空城计 | 街亭之战后（演义） | 诸葛亮、司马懿 | 化险为夷 |
| 苦肉计 | 赤壁之战 | 黄盖、周瑜 | 火攻成功 |
| 欲擒故纵 | 七擒孟获 | 诸葛亮、孟获 | 南中平定 |
| 杯酒释兵权 | 北宋初立 | 赵匡胤 | 兵权收归 |

（千古名计首批仅表格摘要，无详情页，行不跳转；详情页后续渐进补充）

**T4. data/_drama-table-daming-strategy.json — 大明计谋表（36计策）**

单表 6 行（剧中有实例），列：计策 / 历史事件 / 主要人物 / 结局（行内 url → 原详情页）

| 计策 | 历史事件 | 主要人物 | 结局 |
|:--|:--|:--|:--|
| 李代桃僵 | 毁堤淹田 | 严世蕃、郑泌昌、何茂才 | 郑何被清算 |
| 破釜沉舟 | 海瑞上疏 | 海瑞、嘉靖 | 下狱后获释 |
| 分而治之 | 嘉靖御下二十年 | 嘉靖、严嵩、徐阶 | 朝局制衡 |
| 顺水推舟 | 严嵩固宠 | 严嵩 | 终致倾覆 |
| 韬光养晦 | 徐阶倒严 | 徐阶、严嵩 | 严党覆灭 |
| 将计就计 | 海瑞审通倭案 | 海瑞、郑泌昌、何茂才 | 郑何落网 |

### 概述内容页（doc 独立页，章节式，替代原 desc 内联）

- `demos/drama/history-overview.md` → `.html`（章节：朝代脉络 / 代表影视剧 / 观剧指南）
- `demos/drama/daming-overview.md` → `.html`（章节：剧集总览 / 嘉靖朝的底色 / 看懂朝堂三方）

（原 desc 内容迁移进 md，doc 模板提供 TOC 章节导航，呼应需求第 2 点"子菜单作为章节"）

## 模板改动（layout-knowledge.html）

### K1 — selectItem 按 (group, title) 查找（2A 必需，含 bug 修复）

**现状**：`ITEMS.find(i => i.title === title)` 全局按 title 查找；新 items title 必然重复（概述×2、时间轴×2、36计策×2），不改必串组。

**改动**：
- `renderSidebar()` 的 item onclick 传当前 group：`selectItem('{group}','{title}')`
- `window.selectItem = function(group, title)` → `ITEMS.find(i => i.group === group && i.title === title)`
- localStorage 恢复逻辑同步：`ITEMS.some(i => i.group === savedGroup && i.title === savedItem)` 已带 group 过滤，无需改；`selectItem` 调用处补齐 group 参数

**兼容**：chaitin 等旧数据（title 本就唯一）不受影响。

### K2 — section 一级菜单化（无子菜单）

**现状**：`kw-section-title` 纯展示（cursor:default），item 列表才可点。

**改动**（`renderSidebar()`）：
- section 标题加 `onclick="selectSection('{sec}')"`，CSS 加 `cursor:pointer` + hover 反馈
- `window.selectSection = function(sec)`：找到当前 group 下 `section === sec` 的第一个 item 并 `selectItem(group, item.title)`
- **折叠规则**：某 section 的 items 长度为 1 且 `items[0].title === sec`（内容页约定）→ 不渲染 item 行，该 section 只渲染可点击标题（即"无子菜单"）
- **向后兼容**：多 item 的 section（chaitin 等旧数据）维持 item 列表渲染不变；section 标题可点=加载该 section 第一个 item
- active 高亮：点击 section 后，标题行加 active 类（复用 `kw-item.active` 配色）

### K3 — 状态恢复兼容

**现状**：localStorage 存 `html-gen:kw_group` / `html-gen:kw_item`。

**改动**：沿用两键（item 值=section 名）；旧值（如"改稻为桑国策出台"）不在新 ITEMS → 恢复校验失败自然回退默认 group，无需迁移。

## 表格内容页生成（复用 layout-table 能力）

- `html-gen table -d data/_drama-table-*.json -o demos/drama/*-table.html`
- 有详情页的表（T2 剧情节点 / T4）：`col.onClick: "url"` 整行跳转 `row.url`（新标签页打开原详情页）
- tabs：T2 用 tabs（年号总览 / 剧情节点）；T1/T3/T4 单表
- options：`pageSize: 10`、`exportCSV: true`、`search: true`
- 表标题/副标题：如「大明王朝1566 · 时间轴」「以剧读史 · 剧情设定」

## 生成流程（dev 阶段）

1. 改 `layout-knowledge.html`（K1-K3）
2. 写 4 个 table data JSON + 2 个概述 md（迁移原 desc 内容）
3. `html-gen table` 生成 4 个表格内容页；`html-gen doc` 生成 2 个概述页
4. 重写 `data/_drama-kb-data.json`（6 条索引）
5. `html-gen knowledge` 重新生成 `demos/drama-knowledge.html`
6. 13 个原详情页 md/html 保留不动（表格行详情目标）
7. 更新 `tests/test_drama_knowledge.py`，全量回归

## 测试规划

更新 `tests/test_drama_knowledge.py`（9 → 约 12 用例）：

- T1 Tab 渲染与默认组（不变）
- T2 侧栏 3 个一级菜单渲染（中国历史：概述/时间轴/36计策）
- T3 section 无子菜单（对应 section 下无 `kw-item` 行）
- T4 大明组点击「时间轴」→ iframe 加载 `daming-timeline-table.html`
- T5 点击「概述」→ iframe 加载 `daming-overview.html`
- T6 点击「36计策」→ iframe 加载 `daming-strategy-table.html`
- T7 title 重复修复：大明组点击「概述」不串到中国历史（iframe src 断言）
- T8 状态恢复（group + section 名，刷新后恢复）
- T9 表格内容页 tabs（大明时间轴表 2 个 tab 渲染）
- T10 表格行点击跳详情（校验行 url/onClick 配置）
- T11 回归：chaitin 旧结构 demo 正常（多 item section 渲染不受影响）
- T12 `__testErrors` 无错

## 风险与兼容

- **模板改动向后兼容**：多 item section 逻辑不变 → chaitin 案例回归必须通过
- **localStorage 旧值**：旧 item title 不在新 ITEMS，首次打开自动回退默认，无需迁移
- **表格数据量小**（1-7 行）：table 模板能力（搜索/排序/分页/CSV）全量可用，无性能问题
- **千古名计无详情页**：首批仅表格摘要，行不跳转；后续渐进补 doc 页
- **谥号数据**：以正史为准，dev 阶段核定全谥/简谥展示

## 待办清单（dev 阶段）

- [ ] D1 模板改动 layout-knowledge.html（K1-K3）
- [ ] D2 4 个 table data JSON + 2 个概述 md
- [ ] D3 生成 6 个内容页（4 table + 2 doc）
- [ ] D4 重写 data/_drama-kb-data.json
- [ ] D5 重新生成 demos/drama-knowledge.html
- [ ] D6 更新测试 + 全量回归（73+ 通过）
- [ ] D7 AGENTS.md 目录/测试数同步
- [ ] D8 git commit（不 push）
