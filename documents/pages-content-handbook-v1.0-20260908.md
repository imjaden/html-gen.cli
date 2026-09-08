---
title: html-gen 落地页与内容案例手册
topic: html-gen
type: summary
version: 1.0
date: 2026-09-08
author: hermes-v0.20.6(2026.8.27)
profile: dev
provider: deepseek
model: deepseek-v4-flash
tags: [html-gen, index, landing, demos, drama, provinces, countries, pages-index, registry, handbook, summary]
---

# html-gen 落地页与内容案例 v1.0

> 本文是站点展示层与内容案例的主题手册，覆盖三面：① 首页落地页与索引（根 index.html + demos/index.html 双源、pages-index skill、demos-index 表）；② drama「以剧读史」内容案例（knowledge 入口 + 多表格内容页）；③ provinces/countries 双表数据案例（provinces-match.py 数据工程）。内容以 2026-09-08 当前实现为准（HEAD 835a682 实测：根 index.html、demos/index.html、data/、scripts/、demos/_registry.json、features.md 互证）；设计文档年代数字仅作历史基线。

## 1. 功能定位

- **落地页双源**：根 index.html 是 GitHub Pages 首页（CNAME html-gen.lab.jaden.tech 的 dogfood 落地页），demos/index.html 是 4 模板展示子页。二者为**独立维护的两份副本**（双源），靠防漂移测试兜底。
- **内容案例**：drama（knowledge+table 组合：以剧读史知识库 + 每剧 概述 doc/时间轴 table/36 计策 table）、provinces/countries（两张互相关联的 A 型表格 + 数据匹配脚本）。
- 共同载体：`html-gen demo --rebuild` 自动扫描 demos/*.html 生成 demos/_registry.json（featured 由双首页链接驱动）；`skills/pages-index/SKILL.md` 沉淀落地页实现规范。

## 2. 演进主线与审计结论（均无 CL 编号）

| 族 | 时段 | 内容 | 结论链 |
|:--|:--|:--|:--|
| A 落地页/索引 | 2026-08-22~25 | 根落地页 + 双源同步 + 索引优化 | 设计 95/A → 实现 100/A → UI polish 100/A → 回归 100/A → sync 75/B → 复查 100/A → optimize 95/A → 复查 100/A → pages-index sync 100/A |
| B drama | 2026-08-06 + 08-22 | kb 框架改造 + 朱院长（2006）剧集 | 设计 CONDITIONAL 90/A → 实现 100/A → 朱院长 95/A → 尾项复核 100/A |
| C provinces | 2026-08-24 | 省表 + 国家表关联 | 设计 v1.0 70/B → v1.1 100/A → v1.2 变更 100/A → 实现 100/A → 尾项复核 100/A |

测试计数演进：73 → 146 → 154 → 180 → 183（文档时代）→ 现仓 268 collected。

## 3. 落地页与索引（族 A）

### 3.1 页面结构与命令形态

- **根 index.html（537 行，手工维护，非 html-gen 生成）**：
  - 一屏 hero：`.hero-title` / `.hero-tagline`「零依赖 Python CLI：Markdown/JSON → 自包含单文件 HTML · 深色主题 · 中文优先」/ `.hero-badges` 4 项（⚡零依赖·🌙深色·🇨🇳中文优先·📦单文件）/ ⚡ 安装两条 code-block（`bash install.sh install` / `export PATH=...`——属性内嵌引号须 `&quot;` 转义，HG-SEC-038 教训）/ 🚀 4 命令（doc/table/knowledge/slide）/ github-corner（rel=noopener）。
  - 二屏 `.templates`（id="templates"）：`.template-grid` 四卡（A 表格📊/B 文档📄/C 知识库📚/D 幻灯片🖼️），每卡 tpl-icon + name + tpl-guide（demos/templates 前缀）+ 行数 + scenario-pill + 6 条 features + cli-box（copy-btn data-copy）+ 「案例演示」demo-item 列表；断点 1500px→2 列、1100px→1 列。
  - `.scroll-hint`（↓ 滑屏）+ A/B 双形式回顶 + 主题切换 themeBtn（`html-gen:index_theme` key，与模板页 key 隔离）+ footer（GitHub/Gitee/PyPI favicon 外链）。
  - 动态两屏：`updateHeroHeight() = (window.innerHeight - 55) + 'px'`（resize 重算；CSS 80vh 兜底；常量三处同步 index.html/AGENTS.md/SKILL.md）。
  - 复制按钮双通道：clipboard API + execCommand fallback；hero 1 + 四卡 4 + 优化轮新增 = 现仓 11 处 data-copy。
- **demos/index.html（4 模板展示页）**：被 README/usage-guide/hermes-profile-skills-list 多处引用不能移动；demo --rebuild featured 数据源。
- **README.md**：精简 27 行（-68%），一句话定位 + 目录 + 站点链接 + 本地开发（`python3 -m http.server 8089`）+ 精简快速开始。
- **skills/pages-index/SKILL.md**：沉淀落地页行为（骨架/主题/corner/两屏/复制/双源/测试/坑 八节），代码片段与实现逐行一致；`html-gen prompt pages-index --brief` 输出 9 章节。
- **demos/demos-index.html**：A 型 table 索引（`html-gen table -d data/_demos-data.json` 生成，--title「DEMO 案例索引」）。
- **demos/_registry.json**：`{version, count, demos:[{name,title,type,entry,featured,referenced,referenced_by}]}`（现仓 count 56）；`html-gen demo --rebuild` rglob demos/*.html 自动扫描，featured 需双首页加链接。
- 回归测试 tests/test_index_landing.py（现仓 18 用例）：断言真实行为非快照（hero 比例、corner 可点、hover animationName、滑屏、回顶、data-copy 精确值、无旧仓库名链接）；file:// 加载无 http 依赖。
- 双源防漂移：tests/test_demos_index.py test_05_dual_source_consistency 断言 12 项功能特征双源齐全。

### 3.2 双源同步纪律

- 根 index.html 与 demos/index.html 独立副本（1C），模板特性更新需同步两处 + 补防漂移测试特征。
- 根页链接必须指 `demos/` 前缀相对路径；**迁移清单逐条显式 17 处**（SEC-007：通配符漏 2 文件教训），验证步骤 404 兜底。
- 内部 target=_blank 一律 rel="noopener"（根页 17/17、demos 18/18）。
- 深浅色对称保护：`:root.light a:hover` 全局规则会压制 (0,1,0) 组件规则（HG-SEC-031）。
- 浅色模式硬编码深色系色值不达 WCAG AA → 语义变量（--text-*/--border-*/--code-*）。
- 提交单元自洽：测试依赖的数据必须随 commit（HG-SEC-029 🔴 教训）。

## 4. drama 内容案例（族 B）

### 4.1 形态

```
demos/drama-knowledge.html（knowledge 入口，C 型：groups + kb-data items）
  ├─ 每剧：drama/{drama}-overview.html（doc，章节式，?width=wide 适配 iframe 嵌入）
  ├─ drama/{drama}-timeline-table.html（table：时间轴，可 tabs 双表/options.defaultFilter）
  └─ drama/{drama}-strategy-table.html（table：36 计策/剧中有实例的计谋）
原 13 个详情页 md/html 保留为表格行点击详情目标（onClick url / split，新标签页）
```

- groups（现仓 4 组）：中国历史 🏛️ / 朱元璋（2006）⚔️ / 大明王朝1566（2007）📜 / 雍正王朝（1999）👑。
- kb-data（现仓 12 条）：`[{title, group, section, url}]`，title===section 单条目/组/节；url 相对 demos/。
- 生成命令：`html-gen knowledge -d data/_drama-kb-data.json`；`html-gen table -d data/_drama-table-*.json -o demos/drama/*-table.html`；`html-gen doc -i demos/drama/*-overview.md`。
- 表格数据 `{columns,data,tabs,options}`：分剧分化（history-strategy 11 列 36 行含 videos；daming/yongzheng/zhuyuanzhang 各 7 列）；timeline 含 source 列（出处标注：史实/剧中设定/演义）；options.defaultFilter={key:"era",value:"洪武"} 支持默认筛选。

### 4.2 模板支撑（layout-knowledge.html）

- section 一级菜单化：`selectSection(group, sec)` 按 (group, section) 查找；section 下仅 1 item 且 title===sec（内容页约定）→ 不渲染 kw-item 行，标题直接可点。
- **title 跨组必然重复** → selectItem 按 (group, title) 双参查找（K1；「大明组点击概述不串到中国历史」是专属回归断言）。
- 状态恢复：localStorage `html-gen:kw_group`/`html-gen:kw_item` + URL 参数优先；旧 item 值失效自然回退默认，无需迁移。
- source 标注纪律：虚构事件（剧中设定）与史实/演义/史载有争议必须分列（D2-1）。
- 列宽双写：生成物 COLUMNS 列宽压缩后必须回填 data JSON，否则重新生成回退旧宽度（HG-SEC-005）。

## 5. provinces/countries 数据案例（族 C）

### 5.1 形态

```
data/_provinces-data.json（34 省级行政区，11 列）
   └─ html-gen table → demos/provinces-table.html（现仓平铺根，design 期 demos/provinces/ 子目录）
data/_countries-data.json（195 国，现仓 18 列：provinces 关联 3 列 + videos + note）
   └─ html-gen table → demos/countries-table.html
scripts/provinces-match.py（匹配脚本：读两数据 → 归一化 → 双向独立 top-3 命中 → 草稿不入 git）
```

- 省份列：province(110,freeze,split)/abbr(60)/capital(100)/region_tags(90,pills)/area_wan(110,number)/pop_wan(110)/gdp_yi(110)/area_country(170,pills)/pop_country(170)/gdp_country(170)/note(200)；tabs = 全部 + 7 大区域（contains:true）；options = pageSize 30 / exportCSV / searchFields [province,abbr,capital] / showIndex。
- 国家表 3 个关联列 = 现仓第 14/15/16 列（country_zh..religions 后），随后 videos(17)/note(18)。
- 数据口径：省份面积 = 官方万km²；人口 = 七普 2020（万）；GDP = 2023 亿元。国家侧归一化：area_km2÷10000 → 万km²；gdp_yi×7.08（2023 年均汇率）→ 亿元；人口直比。
- 匹配规则：阈值 面积 |Δ|≤30% / 人口 ≤20% / GDP ≤30%（归一化后，禁止跨单位比较）；优先级 = 地理相邻 > 知名度 > 发展阶段相近；每项 2-3 个；v1.2 后**双向独立 top-3**（不强求对称）。
- 无命中国家留空 + note 标注超限（动态取极值：新疆 166.49 / 澳门 0.0033 / 广东 / 西藏，非硬编码）；None 防护按维度（6 国缺 gdp_yi 仅 GDP 维度跳过；梵蒂冈 3 列全空）。
- 数据源说明：demos/provinces-table.md / countries-table.md（主题/创建日期/来源（国家统计局、各省统计公报、七普 2020）/模板类型/数据文件/特性/字段清单/双向关联口径）。
- company-research-*.json + company-report.py/cloudwise-*.py 属 C 型公司知识库体系，与 provinces（A 型表格 + 匹配脚本）**零代码依赖**（勿混为一谈）。

### 5.2 数据纪律

- 生成命令：`html-gen table -d data/_provinces-data.json -o demos/provinces-table.html --title "中国省份速查表"`；countries 同理（195 国）；`html-gen demo --rebuild` 注册。
- 单位换算先行（RIG-1 🔴：naive 跨单位比较静默 0 命中）；测试对照断言钉死 0-命中错误模式。
- backfill 事实源 = 最终 _provinces-data.json（HG-SEC-027：脚本硬编码 PROVINCES 致人工复核编辑后不对称格 → a331ac1 修复读最终表）。
- 草稿 data/_provinces-source.json 必须 gitignore（.gitignore 命中），防 git add . 误提交。
- 双向 top-3 截断造成 miss（30 个 rank 4-8）是设计内行为，互证率 90.1% 属正常，勿当缺陷修。

## 6. 关键决策（原文编号）

### 6.1 落地页（族 A）

| 编号 | 决策 |
|:--|:--|
| 1C | 根 index.html 与 demos/index.html 两份独立维护，接受漂移风险 |
| 2A+B+C | Hero = 价值定位 + 安装 + 4 条快速开始命令（无导航锚点） |
| 3A | 首屏 = 真 100vh 整屏 hero，滚动进入模板区 |
| 4B | README 精简为仓库说明，功能移交首页 |
| 5A/6A | 案例演示区保留；模板使用说明相对路径改 demos/templates/ 前缀 |
| SEC-007(🟡) | 路径迁移清单须完整逐条（通配符漏 2 templates 文件教训） |
| HG-SEC-013 | 内链 target=_blank 补 rel="noopener" |
| HG-SEC-029(🔴) | 提交单元自洽：依赖数据随 commit |
| HG-SEC-030 | 浅色对比度不达 WCAG AA → 语义变量化 |
| HG-SEC-031 | 深浅色对称 CSS 保护（a:hover 特异性压制） |
| HG-SEC-038(🟡) | PATH data-copy 内引号须 &quot; 转义（live DOM 截断） |
| HG-SEC-039 | 测试断言精确值而非非空（截断缺陷未被测试暴露的教训） |
| 决策 1A/2/3A/4A/5A/6A | 行内复制采纳 / 对比卡转置 / hero badges / footer favicon 图标化 / 品牌圆标 / 减留白 + 动态两屏 −55 |

### 6.2 drama（族 B）

| 编号 | 决策 |
|:--|:--|
| 1A~7A | 内容页走 table 独立页 + iframe 加载；侧栏 section 可点击；原详情页保留行点击；「千古名计」跨朝代表；大明双表；36 计策行粒度 6-8 行；多 table 用 tabs |
| K1 | selectItem 按 (group,title) 双参查找（title 跨组重复必串组） |
| K2 | section 一级菜单化 + 折叠规则（1 item 且 title===sec 不渲染行） |
| K3 | localStorage 状态恢复兼容（旧值回退默认，无需迁移） |
| T1-T4 | 四张表格数据模型（朝代/大明时间轴/千古名计/大明计谋） |
| D2-1/D2-2/D4-1 | source 列标注纪律 / 补完整 columns 结构化 JSON / section 点击断言 |
| 1B/2A/3A/4B | 菜单标签带年份；沿用三 section 框架；时间轴含剧前剧后；豆瓣链接三剧覆盖 |
| HG-SEC-005 | 列宽回填 data JSON（生成物压缩后回填，防重生成回退） |

### 6.3 provinces（族 C）

| 编号 | 决策 |
|:--|:--|
| 探讨 1A~6A | 双表互查 / 34 省字段集 / 关联规则 / 数据源策略 / 测试规划 / 扩展记录 |
| v1.2 1A/2A | 国家侧独立匹配（top-3 不挤掉阈值内）；无命中留空 + note 超限说明 |
| v1.2 3A/4B | 双向独立语义抽查（强对称不作验收）；ops 直改 + review 尾项复核 |
| RIG-1(🔴) | 单位换算（÷10000 / ×7.08）缺失阻断核心路径 |
| RIG-2/3/4(🟡) | 列宽显式指定 / 测试基线校正 / 示例须真实数据复算（荷兰反例） |
| OBS-1~4 | 脚本+草稿 gitignore / 港澳台归华南注明 / 国家表 3 列=15/16/17 位 / 方向不对称 |
| HG-SEC-027 | backfill 事实源 = 读最终省份表（a331ac1 修复） |
| 决策 4A/5A/3D | 数据源 ops 闭环草稿不入 git / 新增 test_provinces_table / 扩展方向 11 项不入本轮 |

## 7. 已知坑

| # | 坑 | 处置 |
|:--|:--|:--|
| P1 | 双源漂移（头号） | 独立副本接受漂移 + 12 项功能特征防漂移测试 + AGENTS.md 备注治理 |
| P2 | 相对路径/17 处清单 | 逐条显式清单（禁通配符）+ 404 兜底验证（SEC-007） |
| P3 | 单位换算静默 0 命中 | 归一化先行 + 对照断言钉死（RIG-1） |
| P4 | 列宽未指定截断 | Cinema fixed 模型每列显式 width，pills ≥160px（RIG-2） |
| P5 | 匹配示例与规则矛盾 | 示例用真实数据复算（RIG-4 荷兰 Δ76.9% 反例） |
| P6 | backfill 事实源漂移 | 读最终省份表 + 复核后重跑（HG-SEC-027） |
| P7 | title 跨组重复串组 | (group,title) 双参查找（K1） |
| P8 | URL 映射错误 | 生成物 grep 0 残留验证（strategy→timeline 错映射教训） |
| P9 | 列宽双写漂移 | 生成物压缩后回填 JSON（HG-SEC-005） |
| P10 | 属性内引号截断 | `&quot;` 转义 + 精确值断言（HG-SEC-038/039） |
| P11 | 深浅色 CSS 不对称 | 全局 a:hover 压制 → 对称保护（HG-SEC-031） |
| P12 | 提交单元不自洽 | 依赖数据随 commit（HG-SEC-029） |
| P13 | 草稿数据入库 | gitignore 防护（_provinces-source.json） |
| P14 | 首页文案滞后 | drama 卡片「3 组」/AGENTS.md「2 组」vs 现仓 4 组（待核） |

## 8. 漂移与待核记录（文档时代 vs 现仓）

- 国家表列序：design 14+3 = 15/16/17 位 → 现仓 18 列（provinces 3 列在 14/15/16，videos 17，note 18）。
- provinces 产物路径：demos/provinces/provinces-table.html（子目录）→ 现仓平铺 demos/provinces-table.html + .md。
- registry 计数 59/60 → 56（过期 demo 清理后）。
- drama kb 组数 2 → 4（文案滞后：根 index.html C 卡 desc「3 组」、AGENTS.md「2 组」）。
- 落地页 hero 常量 −110 → −55（三处同步）。
- drama 表列结构多次演进（现仓 7-11 列分剧分化，含 videos/source/defaultFilter）。

## 9. 参考文档

- 保留原位：根 index.html、demos/index.html、demos/demos-index.html、demos/drama-knowledge.html、demos/drama/、demos/countries-table.html、demos/provinces-table.html、data/_drama-*.json、data/_provinces-data.json、data/_countries-data.json、scripts/provinces-match.py、skills/pages-index/SKILL.md、demos/_registry.json、features.md、AGENTS.md、review-log.md / .review-level.yaml（历史不追改）。
- 本族过程文档（18 份）已归档（2026-09-08 执行） → `documents/archive/{solutions,root,review}-20260908/`：

| 素材 | 归档路径 | 归档桶 |
|:--|:--|:--|
| index-landing 设计 v1.0 | documents/archive/root-20260908/index-landing-design-v1.0-20260822.md | root |
| index-landing 设计评审 / 实现 / ui-polish / 回归 | documents/archive/review-20260908/index-landing-{design-review-v1.0,implementation-review-v1.0,ui-polish-implementation-review-v1.0,regression-implementation-review-v1.0}-20260823.md | review |
| index-landing sync 复查 | documents/archive/review-20260908/index-landing-sync-review-v1.0-20260824.md | review |
| 索引优化复查 | documents/archive/review-20260908/html-gen-index-optimize-review-v1.0-20260825.md | review |
| pages/skills/demos 三处 index 同步 | documents/archive/review-20260908/pages-index-skill-demos-index-sync-review-v1.0-20260824.md | review |
| drama-kb-table 设计 | documents/archive/root-20260908/drama-kb-table-design-v1.0-20260806.md | root |
| drama 验证 prompt | documents/archive/root-20260908/verify-prompt-doc-drama-20260806.md | root |
| drama kb 评审 / 实现评审 / 朱院长实现评审 | documents/archive/review-20260908/drama-{kb-table-review-v1.0,kb-table-implementation-review-v1.0,zhuyuanzhang-implementation-review-v1.0}-20260806/20260822.md | review |
| provinces 设计 v1.2 | documents/archive/solutions-20260908/provinces-table-design-v1.2-20260824.md | solutions |
| provinces 设计评审 v1.0/v1.1 / v1.2 变更 / 实现评审 | documents/archive/review-20260908/provinces-table-{design-review-v1.0,design-review-v1.1,design-v1.2-change-review,implementation-review-v1.0}-20260824.md | review |
