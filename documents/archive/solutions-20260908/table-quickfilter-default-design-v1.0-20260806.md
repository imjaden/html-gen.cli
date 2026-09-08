# html-gen table 筛选默认行为调整 — 设计文档

## 版本

v1.0 (2026-08-06)

## 背景与问题来源

探讨 countries-table.html 迭代时暴露模板默认行为问题：**单元格点击筛选（quickFilter）默认开启**，导致数据浏览型表格误触（点国家列即筛选）；而标签（pills）点击筛选为上一轮新增（默认开）。用户讨论后确认统一"保守默认 + 显式声明"路线。

待确认清单问答（用户回复 1A 2A 3B 4A 5A 6A 7A）定稿：

| 项 | 确认 |
|:--|:--|
| 1 quickFilter 实现 | A=`col.quickFilter === true` 显式开启（默认关） |
| 2 drama 行为变化 | A=接受默认关（单元格点击不再筛选） |
| 3 第 1 列点击分栏 | B=模板默认：无配置时第 1 列点击即分栏（影响所有 table 页面） |
| 4 skills 显式配置 | A=category/profiles 补 pillFilter:true，其余列接受默认关 |
| 5 test_table_features test_06 | A=其测试页某列显式配 quickFilter:true，保持用例 |
| 6 重新生成 | A=drama 3 表 + skills 表 + countries 表全部重新生成 |
| 7 文档同步 | A=features.md + AGENTS.md + 模板注释全部 |

## 目标形态

**现状**：
- 普通单元格点击筛选默认开：`col.quickFilter !== false` 即可点筛（精确整值匹配）
- 标签点击筛选默认开：`col.pillFilter !== false`（contains 匹配，上轮新增）
- 第 1 列无默认点击行为（countries/skills 靠显式 `onCellClick:'split'`）

**目标**：
- 普通单元格点击筛选**默认关**：`col.quickFilter === true` 才启用
- 标签点击筛选**保持默认开**：`col.pillFilter !== false`（列级 `pillFilter: false` 可关）
- **第 1 列默认分栏**：无显式配置时，点击第 1 列（首个有 key 的数据列）→ 分栏预览展示该行元信息
- 各案例显式声明筛选意图（skills/countries 补配置），文档同步默认行为说明

## 事实核查（影响设计的关键现状）

1. **drama 3 表**（daming-timeline / daming-strategy / history-strategy）：列定义无 `onClick`/`onCellClick`/`preview` 配置；数据行含 `url` 字段但未配跳转列 → **当前行点击无跳转**。默认关 + 第 1 列默认分栏后：第 1 列点击开分栏（元信息），其余列无操作。如需行点击跳详情页（`col.onClick:'url'`），属后续可选项，不在本次范围。
2. **skills 表**：name 列已显式 `onCellClick:'split'`；category/profiles 为 pills 列（标签筛选默认开）。默认关后其余列（version/description）点击无操作，与现状差异小。
3. **countries 表**：12 列已显式 `quickFilter:false`；country_zh 显式 `onCellClick:'split'`；region_tags 为 pills。默认关后行为不变。
4. **test_table_features.py test_06**：测试页为 phase2-demo（源 `data/_phase2-demo.json`），依赖"点击单元格 → filter pill 显示"的默认行为，默认关后必失败，需在数据源某列显式配 `quickFilter:true`。

## 设计决策 (D)

### D1 — quickFilter 默认关（1A）

**改动**：`layout-table.html` L525

```js
// 现状
} else if (col.quickFilter !== false) {
// 目标
} else if (col.quickFilter === true) {
```

**语义**：普通单元格点击筛选仅列级显式 `"quickFilter": true` 时启用（精确整值匹配）。未配置列点击无筛选。

**保留**：`quickFilterBy(key, value, mode)` 函数与 `mode:'contains'` 分支（pillFilter 复用，不受影响）。

**注释**：判断处补默认行为说明。

### D2 — pillFilter 默认开 + 显式声明（4A）

**改动**：`layout-table.html` L504 保持 `col.pillFilter !== false`（默认开），注释说明"标签点击筛选默认开启，`pillFilter: false` 可关闭"。

**数据显式声明**（意图文档）：
- `data/_skills-table-config.json`：category、profiles 列补 `"pillFilter": true`
- `data/_countries-data.json`：region_tags 列补 `"pillFilter": true`

### D3 — 第 1 列默认分栏（3B）

**改动**：`layout-table.html` renderRows 单元格 onclick 决策逻辑

```js
// 目标优先级（从高到低）：
// 1. col.onCellClick === 'split' → openSplitAt(rowIdx)（显式）
// 2. col.quickFilter === true → quickFilterBy（显式筛选）
// 3. col === firstKeyCol（首个有 key 的非 actions 列）→ openSplitAt(rowIdx)（默认分栏）
// 4. 其余列 → 无 onclick
```

**firstKeyCol 计算**：`COLUMNS.find(function(c){ return c.key && c.type !== 'actions'; })`（模块初始化处）。

**注意**：
- pills 列 / actions 列走各自分支（早 return），不参与普通单元格 onclick
- 有 `col.onCellClick`（split/modal 等）或 `quickFilter:true` 的列不被默认覆盖
- 分栏预览内容由 split 模式决定：有 preview 列显示 preview 列集，否则显示全部可见列（countries 已全列 preview → 元信息全字段；drama 无 preview → 显示全部列）

### D4 — drama 行为确认（2A，含事实修正）

- 默认关后 drama 表单元格点击不再筛选
- 第 1 列（D3）点击 → 分栏预览（元信息）；其余列无操作
- **修正认知**：drama 表现状并无 `onClick:'url'` 行跳转配置（此前讨论中"触发整行 url 跳转"不成立）；如需行点击跳详情页，另行配置（后续项，本次不做）

### D5 — 测试调整（5A）

- `data/_phase2-demo.json`：给某列（如首个可筛列）补 `"quickFilter": true` → 重新生成 phase2-demo.html → test_06 继续验证快速筛选功能（显式开启后生效）
- 新增用例：无显式配置的表，第 1 列点击 → 分栏模式（drama 表第 1 列验证）
- 更新用例：未配 quickFilter 的列点击 → 无 filter pill（默认关验证）
- countries/skills 现有断言（显式配置）不受影响

### D6 — 重新生成（6A）

模板改动后重新生成：
- drama 3 表：`daming-timeline-table.html` / `daming-strategy-table.html` / `history-strategy-table.html`
- skills 表：`demos/hermes-profile-skills-list.html`（`html-gen table -d data/_skills-table-config.json -o ... --title "Hermes Skills 列表"`）
- countries 表：`demos/countries/countries-table.html`（`--title "全球国家速查表（195 国）"`）
- phase2-demo：`demos/phase2-demo.html`（`-d data/_phase2-demo.json`，title 以现有生成物为准）

### D7 — 文档同步（7A）

- `features.md`：快速过滤条目更新为"默认关，列级 quickFilter:true 启用"；补 pillFilter（默认开）说明
- `AGENTS.md`：快速过滤描述更新（原"`col.quickFilter: false` 禁用" → "默认关，`col.quickFilter: true` 启用；标签筛选默认开，`col.pillFilter: false` 关闭"）
- `layout-table.html` 模板注释：quickFilter / pillFilter / 第 1 列默认分栏三处默认行为说明

## 改动文件清单

| 文件 | 改动 |
|:--|:--|
| layout-table.html | D1 判断 + D3 第 1 列默认分栏 + 注释 |
| data/_skills-table-config.json | category/profiles 补 pillFilter:true |
| data/_countries-data.json | region_tags 补 pillFilter:true |
| data/_phase2-demo.json | 某列补 quickFilter:true（D5） |
| demos/ 4 个生成物 | 重新生成（D6） |
| tests/test_table_features.py | test_06 适配（数据源已显式配置，断言可保留） |
| tests/test_drama_knowledge.py | 新增/更新第 1 列分栏与默认关断言 |
| features.md / AGENTS.md | 默认行为说明同步 |

## 测试规划

- test_table_features.py test_06：phase2-demo 显式 quickFilter:true 列点击 → filter pill（保留）
- 新增（drama）：第 1 列（剧情时间）点击 → wrapper.split-mode；其他列点击 → 无 filter pill
- 回归：countries 10 用例（显式配置，预期不变）、skills、drama 知识库、全量 83+ 通过

## 风险与兼容

- **行为变化**：未显式配置的普通列点击从"筛选"变"无操作"（drama 全部列、skills version/description 等）——用户已确认接受
- **第 1 列默认分栏**：现有页面第 1 列已显式 split（countries/skills）不受影响；drama 第 1 列获得新分栏能力（新增行为，非破坏）
- **向后兼容**：显式配置（quickFilter:true/false、onCellClick、pillFilter）全部保留，新默认只影响"未配置"的列
- **文档**：AGENTS.md 描述与模板注释同步，避免新旧默认混淆

## 待办清单（dev 阶段）

- [ ] D1 layout-table.html quickFilter 判断改为 `=== true` + 注释
- [ ] D2 数据显式声明（skills ×2 / countries ×1）+ pillFilter 注释
- [ ] D3 layout-table.html 第 1 列默认分栏（firstKeyCol + onclick 决策）
- [ ] D5 phase2-demo.json 某列 quickFilter:true
- [ ] D6 重新生成 4 个 demo（drama 3 + skills + countries + phase2）
- [ ] D7 features.md / AGENTS.md / 模板注释同步
- [ ] 测试更新（drama 第 1 列分栏 + 默认关断言）+ 全量回归
- [ ] git commit（不 push）
