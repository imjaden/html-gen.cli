# 中国省份数据表 + 国家双向关联 — 设计文档 v1.0

**文档**: `documents/solutions/provinces-table-design-v1.0-20260824.md`
**日期**: 2026-08-24
**类型**: Design Document
**状态**: 待评审
**需求来源**: 探讨确认清单 1A 2A 3A 4A 5A 6A（2026-08-24）

---

## 一、背景与目标

以剧读史/国家速查表等 table demo 之后，新增两个相互关联的数据表：

1. **中国省份速查表**（模板 A 新建）：34 省级行政区，含基础数据 + 与全球国家的交叉关联字段
2. **全球国家速查表补充**：现有 `demos/countries/countries-table.html`（195 国）增加关联省份字段

目标：双表互查——查省份时看到"这个省的面积/人口/GDP 接近哪些国家"，查国家时反向看到"这个国家的面积/人口/GDP 接近哪些省份"，形成数据联想。

## 二、字段设计

### A. 省份表（新建 `data/_provinces-data.json`）— 11 列

| # | key | label | 类型 | 说明 |
|:--:|:---|:---|:---|:---|
| 1 | province | 省份名称 | string, freeze, split | 省份/自治区/直辖市/特别行政区 |
| 2 | abbr | 简称 | string | 京/津/冀/鲁/新/港澳… |
| 3 | capital | 省会/首府 | string | 含特别行政区（香港/澳门无省会，填"—"） |
| 4 | region_tags | 区域 | pills | 华北/东北/华东/华中/华南/西南/西北；港澳台归"华南" |
| 5 | area_wan | 面积(万km²) | number, thousands | 统一万km²（澳门 0.0033） |
| 6 | pop_wan | 人口(万) | number, thousands | 七普 2020 常住人口 |
| 7 | gdp_yi | GDP(亿元) | number, thousands | 2023 年地区生产总值 |
| 8 | area_country | 面积相近国家 | pills | 2-3 个，匹配规则见 §四 |
| 9 | pop_country | 人口相近国家 | pills | 2-3 个 |
| 10 | gdp_country | GDP相近国家 | pills | 2-3 个 |
| 11 | note | 备注 | string | 口径差异/特殊情况（如港澳特别行政区） |

- tabs：全部 + 七大区域（华北/东北/华东/华中/华南/西南/西北），`field: region_tags, contains: true`
- options：pageSize 30、exportCSV、searchFields [province, abbr, capital]

### B. 国家表补充（`data/_countries-data.json` 追加 3 列）

| # | key | label | 类型 | 说明 |
|:--:|:---|:---|:---|:---|
| 12 | area_province | 面积相近省份 | pills | 2-3 个 |
| 13 | pop_province | 人口相近省份 | pills | 2-3 个 |
| 14 | gdp_province | GDP相近省份 | pills | 2-3 个 |

195 国全部补齐；匹配不到质量合格省份的国家该字段留空。

## 三、数据口径（决策 1A/2A）

| 数据 | 口径 | 说明 |
|:---|:---|:---|
| 省份面积 | 官方国土面积（万km²） | 含管辖海域不计；新疆 166.49 / 澳门 0.0033 |
| 省份人口 | 七普 2020 常住人口（万人） | 静态权威口径；广东 12601 / 澳门 68 |
| 省份 GDP | 2023 年地区生产总值（亿元） | 最新完整年度；广东 135673 |
| 国家侧 | 复用国家表现有值 | `_countries-data.json` 的 area_km2/pop_wan/gdp_yi，不做二次采集 |
| 港澳台 | 归"华南"区域 | note 注明"特别行政区/地区，口径与内地有差异" |
| 单位 | 面积统一万km²；GDP 统一亿元 | 不按量级切换单位，保持列内一致 |

## 四、关联匹配规则（决策 3A）

1. **初筛阈值**（脚本自动计算，基于国家表/省份表数值）：
   - 面积：|Δ| ≤ 30%（相对省份值）
   - 人口：|Δ| ≤ 20%
   - GDP：|Δ| ≤ 30%
2. **优先级**（初筛命中多个时排序）：
   a. 地理相邻（接壤/同区域）> b. 知名度高（大众熟悉）> c. 发展阶段相近（人均 GDP 接近）
3. **数量**：每项取 2-3 个（决策 2A）；小省/微国家匹配不到 2 个时允许 1 个或留空
4. **双向一致性**：省份表 34 省 × 3 项 ↔ 国家表 195 国 × 3 项，同一对关系两表字段互相对应（如广东面积↔面积相近国家含"荷兰"时，荷兰的"面积相近省份"含广东）；不强求严格对称（国家可关联 2-3 省，省份也可关联 2-3 国），但语义应互相印证
5. **人工复核**：脚本初筛结果落盘后，ops 复核每省 3 项，修正明显不合理（如微国家匹配、知名度低、发展阶段悬殊）

## 五、数据源策略（决策 4A）

- ops 闭环内先备数据源：34 省基础数据（面积/人口/GDP）+ 匹配脚本
  - 匹配脚本：读 `data/_countries-data.json`（195 国数值）↔ 省份基础表，按 §四 规则生成双向关联草稿
  - 落盘：`data/_provinces-source.json`（草稿，不入 git；dev 实施中间产物）
  - ops 人工复核清单：逐省确认 3 项关联合理性
- dev 实施时读数据源，组装 `_provinces-data.json` + 国家表 3 列 + 生成物 + 测试

## 六、生成与集成

| 产物 | 命令 | 输出 |
|:---|:---|:---|
| 省份表 | `html-gen table -d data/_provinces-data.json -o demos/provinces/provinces-table.html --title "中国省份速查表"` | demos/provinces/provinces-table.html |
| 国家表 | `html-gen table -d data/_countries-data.json -o demos/countries/countries-table.html --title "全球国家速查表（195 国）"` | 重生成 |
| README | 省份表 README（对齐 countries/README.md 格式） | demos/provinces/README.md |
| registry | `html-gen demo --rebuild` | 注册 provinces demo |

## 七、测试（决策 5A）

- 新增 `tests/test_provinces_table.py`（参照 test_countries_table 模式，~13 tests）：
  - T1 表头 11 列 + 序号列
  - T2 region_tags pills 拆分（华北/东北…标签渲染）
  - T3 关联国家列 pills 渲染（面积/人口/GDP 各 2-3 标签）
  - T4 区域 tab 分组（华北 tab 过滤）
  - T5 排序（面积/人口/GDP 数值排序）
  - T6 搜索（简称/省会）
  - T7 34 行数据完整（含港澳台）
  - T8 港澳台 region_tags 归"华南"
  - T9 无 JS 错误（全 tab × 列遍历）
  - T10 生成物 COLUMNS/DATA 与 JSON 逐字段一致
- 国家表补充 1-2 条断言：新 3 列 pills 渲染正常（如中国行 gdp_province 含"广东"）
- 全量回归 `python3 -m pytest tests/ -q -n 4`（当前 146 → 预计 +13 左右）

## 八、扩展方向（决策 3D：仅记录，不入本轮表）

1. 接壤关系双向列（省份接壤国家 ↔ 国家接壤省份）——地理意义最强，下轮优先
2. 人均 GDP（省份人均 ↔ 国家人均，发展阶段可比）
3. 人口密度计算列
4. 气候/温度带双向对照
5. 省会 ↔ 首都经纬度（distance/split 定位复用）
6. 时区对照
7. 民族构成对照（国家表已有"主要民族"列）
8. 世界遗产/5A 景区数量
9. 车牌代码/电话区号 ↔ 国家 ISO 代码
10. 最高峰/地形对照
11. 海岸线（沿海省份 ↔ 沿海国家）

## 九、TC 清单（dev 实施验收）

- TC-01 省份表 34 行全量（23 省 + 5 自治区 + 4 直辖市 + 2 特别行政区）
- TC-02 每省 3 项关联（面积/人口/GDP）各 2-3 个标签（允许 1 个/空：小省微国家）
- TC-03 港澳台 region_tags=华南 + note 口径说明
- TC-04 国家表 195 国 3 列补齐（匹配不到留空）
- TC-05 双向关系语义互证抽查 ≥10 对（省↔国）
- TC-06 面积/人口/GDP 列 thousands 格式正确
- TC-07 生成物与 JSON 逐字段一致（COLUMNS/DATA）
- TC-08 test_provinces_table.py ~13 tests 全过
- TC-09 国家表新列 1-2 断言 + 全量 146+13 无回归
- TC-10 registry rebuild 后 provinces demo 可见

## 十、评审通过标准

- Design Review PASS ≥90（🔴 0）
- 实现审计 PASS ≥90；扩展方向不入表（§八）不得被当成缺口
