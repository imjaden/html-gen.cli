# 中国省份表 + 国家双向关联 — review报告 v1.0

> 日期: 2026-08-24
> 文件: `documents/solutions/provinces-table-design-v1.0-20260824.md`
> 项目路径: /Users/jadenli/CodeSpace/html-gen.cli
> 聚焦 commit: `51bf5b5`（docs@html-gen: provinces table + countries cross-link design v1.0，未 push，ahead github/main 1）
> 需求来源: 探讨确认清单 1A 2A 3A 4A 5A 6A（2026-08-24 用户全选）
> review维度: 合理性 / 严格性 / 安全性 / 治理规范（commit + 命名）
> review者: Security Reviewer (L2)

## 数据验证

| 验证项 | 方法 | 结果 |
|:-------|:-----|:-----|
| commit 51bf5b5 仅 1 设计文档 | `git show 51bf5b5 --stat` | ✅ 137 行，单文件 |
| 设计文档存在且正文可读 | `read_file` 137 行 | ✅ |
| 国家表 195 行 / 14 列 | `python3 json.load(data/_countries-data.json)` | ✅ 与设计 §二 B 声明一致 |
| 国家表 `gdp_yi` 单位 | 列定义 label | ❌ 实为 **亿美元**（label "GDP(亿美元)"），设计 §三 声称"GDP 统一亿元"——自相矛盾 |
| 国家表数值缺值 | json 扫描 | ⚠️ `gdp_yi` 缺 6 国（也门/南苏丹/厄立特里亚/古巴/朝鲜/梵蒂冈），`area_km2`/`pop_wan` 各缺 1 国（梵蒂冈）——匹配脚本需 None 防护，设计未提 |
| 测试基线 | `grep 'def test_' tests/*.py` 求和 | ❌ 实际 **154**（设计 §七/TC-09 写"当前 146"） |
| test_countries_table.py 测试数 | `grep -c 'def test_'` | ✅ 13（含 test_11_thousands_format/test_12_search_fields_limited 等，无表头断言，加列不破坏成立） |
| 模板能力：searchFields / format thousands / freeze / 序号列 | `grep layout-table.html` | ✅ 均支持（L427 searchFields、L543 `col.format==='thousands'`、L506/534 freeze、L518 col-index-num） |
| 广东数据事实 | 设计文档数值 vs 官方口径 | ✅ 135673 亿 / 12601 万 / 17.97 万km² 一致；新疆 166.49 / 澳门 0.0033 一致 |
| 单位换算影响量化 | `execute_code` 实测国家表 | ❌ 广东 GDP 相近：naive（亿元 vs 亿美元不换算）**0 命中**；归一化 ÷7.08 后 **10 命中**（韩国/墨西哥/西班牙/巴西/俄罗斯/意大利/加拿大/澳大利亚/印尼/土耳其）。面积：naive **0 命中**；归一化 ÷10000 后 15 命中（柬埔寨/乌拉圭/叙利亚…） |
| §四 荷兰示例真实性 | 实测荷兰数值 | ❌ 荷兰 4.15 万km² vs 广东 17.97 万km² → Δ=76.9%，远超 30% 阈值；GDP Δ=36.7% 亦超阈值——示例与规则矛盾 |
| demo --rebuild 自动注册 | `sed -n 790,850p html-gen.py` | ✅ `rglob('*.html')` 自动扫描，新 demos/provinces/ 无需手改 registry（featured 需 demos/index.html 加链接） |
| YAML frontmatter | `head` | ✅ 项目惯例无 frontmatter（index-landing review 已确认 13 个设计文档均同）；本文件用 `**状态**: 待评审` 头段，文件名 v1.0 与标题 v1.0 一致 |
| commit/命名规范 | `git log` + 文件名比对 | ✅ `docs@html-gen:` 符合项目 type@scope 惯例；`provinces-table-design-v1.0-20260824.md` 符合 Style A（kebab-case、无点/下划线、8 位日期） |

## 合理性评估

| # | 检查项 | 结论 |
|:-:|:-------|:-----|
| R1 | 方案完整性闭环（字段表/数据口径/单位/关联规则/数据源策略/测试/生成命令） | ✅ 六要素齐全，§六 生成命令与现有 `html-gen table` 用法一致（countries 同款）；§五 ops 备草稿 + dev 实施分工清晰 |
| R2 | 需求追溯：探讨 1A-6A 全选 ↔ 设计决策 | ✅ §三(1A/2A 口径)、§四(3A 规则)、§五(4A 数据源)、§七(5A 测试)、§八(3D 扩展仅记录) 一一对应 |
| R3 | 边界明确：小省/微国家留空、扩展方向不入表 | ✅ §四 3 允许 1 个/留空；§八 11 项 + §十"扩展方向不入表不得被当成缺口"显式声明 |
| R4 | 集成不破坏现有：国家表加列 / 测试 / registry | ✅ 国家表加列仅追加 3 pills 列，test_countries 无表头断言；`html-gen demo --rebuild` 自动扫描新目录（实测代码路径） |
| R5 | 双表互查价值落地形态 | 🟢 关联列 pills 为纯数据展示，无点击跳转联动（国家 pill → 国家表）；符合决策范围（§八 扩展方向未含联动导航），v1 数据联想可接受，记录不阻断 |

## 严格性评估

| # | 检查项 | 结论 |
|:-:|:-------|:-----|
| S1 | 11 列字段表 / options / tabs / searchFields 与模板能力匹配 | ✅ 全部能力实测存在（searchFields L427、tabs contains、freeze、thousands、序号列 L518） |
| S2 | 关联规则可执行性（阈值+优先级+双向互证+人工复核） | ⚠️ 结构可执行，但核心换算缺失（RIG-1 🔴）阻断正确实施；示例错误（RIG-4 🟡）降低参考质量 |
| S3 | TC-01~10 可验收性 | ✅ 每项均可实测（行数/tab/排序/搜索/pills/生成物一致性/registry）；基线数字需修正（RIG-3） |

### Findings

**🔴 RIG-1（HG-SEC-018）— 单位换算缺失，关联匹配核心数据路径阻断**

§三 数据口径声明"国家侧复用 `_countries-data.json` 的 area_km2/pop_wan/gdp_yi，不做二次采集"且"单位：面积统一万km²；GDP 统一亿元"，但国家表实际单位是 **area_km2（km²）+ gdp_yi（亿美元）**。§四 初筛"脚本自动计算，基于国家表/省份表数值"未定义任何换算步骤。

实测后果（基于真实数据）：
- 广东 GDP 相近匹配：不换算直接比较 → **0 命中**；按 2023 年均汇率 ÷7.08 归一化 → 10 命中（韩国/墨西哥/西班牙/巴西/俄罗斯/意大利/加拿大/澳大利亚/印尼/土耳其）。
- 广东面积匹配：不换算（万km² vs km²）→ **0 命中**；÷10000 归一化 → 15 命中。

即：按设计字面实施，核心卖点（GDP/面积"相近"关联）全部静默失败；若 dev 用宽松阈值"补救"则产出垃圾匹配。

修复建议（v1.1）：
1. §三 明确国家侧归一化：面积 `area_km2 / 10000 → 万km²`；GDP `gdp_yi × FX → 亿元`（FX 指定数值与来源，如 2023 年均 7.08，国家统计局/IMF 口径二选一）。换算 ≠ 二次采集，不违背 4A。
2. 匹配脚本声明 None 防护：6 国缺 `gdp_yi`（也门/南苏丹/厄立特里亚/古巴/朝鲜/梵蒂冈）、梵蒂冈缺全部数值，跳过不参与该维度匹配（与 TC-04 留空规则衔接）。
3. TC 增加单位换算对照断言（如"广东 gdp 归一化后命中含韩国/西班牙，且不含 0-命中 case"），把"0 命中"错误模式钉死。

**🟡 RIG-2（HG-SEC-019）— 列宽未指定（Cinema 影院模型）**

§二 A 字段表无 width 列。AGENTS.md 规定 `table-layout:fixed` 每列强制显式宽度（默认 fallback 120px），11 列 × 120px 下 `备注`（口径差异长文本）与 3 个"相近国家" pills 列（2-3 标签）会被 `max-width:0` 强制截断；国家表追加的 3 列（area_province/pop_province/gdp_province，各 2-3 个省份标签）同问题。

修复建议：v1.1 字段表补充每列 width（参照 countries 显式宽度做法）：province 110px / abbr 60px / capital 100px / region_tags 90px / 数值列 110px / 关联 pills 列 160-180px / note 200px+。

**🟡 RIG-3（HG-SEC-020）— 测试基线 146 过时（实际 154）**

§七"当前 146 → 预计 +13 左右"与 TC-09"全量 146+13 无回归"均基于过时基线；实测 `grep 'def test_' tests/*.py` = **154**（2026-08-23 AGENTS/features 已同步为 154）。且 T 清单仅 T1-T10（10 条）与"~13 tests"表述不一致（未计入国家表 1-2 条补充断言）。

修复建议：基线改 154；测试数表述统一（10 条省份表 + 1-2 国家表断言 = 预计 +11~12）；TC-09 数字同步。

**🟡 RIG-4（HG-SEC-021）— §四 双向一致性示例与规则自相矛盾**

"如广东面积↔面积相近国家含'荷兰'时"——实测荷兰面积 4.15 万km²，与广东 17.97 万km² Δ=76.9%（阈值 30%），GDP Δ=36.7% 亦超限。示例为事实错误，dev 若照抄将产出错误关联对。

修复建议：改为真实命中对，如 面积 广东↔柬埔寨/乌拉圭、人口 广东↔墨西哥/日本、GDP 广东↔韩国/西班牙（均已实测在阈值内）。

### 附注 (🟢 OBS，非阻断)

- **OBS-1（HG-SEC-022）**：匹配脚本未命名/未定位（建议 `scripts/provinces-match.py`），草稿 `data/_provinces-source.json`"不入 git"但 .gitignore 无防护（`git add .` 有误提交风险，建议加入 .gitignore 或置入 gitignored 目录）。
- **OBS-2（HG-SEC-023）**：港澳台归"华南"与主流教材惯例（台湾→华东）不同——已为用户确认决策（2A），建议 §三 或 note 注明归因依据；另港澳人口非七普覆盖（澳门 68 万为 2021 当地普查），note 已声明口径差异，建议 README 数据源行补齐（countries/README.md 已有"来源"行，省份 README 需对齐：国家统计局/各省统计公报）。
- **OBS-3（HG-SEC-024）**：国家表 3 新列编号 12/13/14 是省份表编号延续，但国家表现有 14 列，实际插入位置为 15/16/17——建议标注"追加列"避免 dev 误解列序。
- **OBS-4（HG-SEC-025）**：双向匹配阈值方向不对称（相对省份值 vs 相对国家值，反向阈值可差至 42.9%）——建议明确"单方向匹配一次 + 反向回填同对"，保证两表语义互证（§四 4 已含人工复核兜底）。

## 安全事项

🟢 SEC-1 — 无新增注入面：新增列为静态 JSON 字符串（省份/国家名称），经模板现有 pills/textContent 安全渲染（countries 已同机制），无 innerHTML 直插、无外部依赖、无新增 API。设计不引入代码路径变更。

🟢 SEC-2 — 数据完整性：关联对由脚本生成 + ops 人工复核，名称必须与表内实体精确匹配（防 typo 断链导致双向互证失败）；建议匹配脚本输出前做实体名交集校验。属数据治理范畴，非代码漏洞。

## 评分

| 级别 | ID | 扣分 |
|:----:|:---|:----:|
| 🔴 HIGH | RIG-1（单位换算缺失，核心数据路径） | -15 |
| 🟡 MEDIUM | RIG-2（列宽未指定） | -5 |
| 🟡 MEDIUM | RIG-3（测试基线过时） | -5 |
| 🟡 MEDIUM | RIG-4（示例与规则矛盾） | -5 |
| 🟢 LOW | OBS-1~4 + SEC-1/2 | 0（记录） |

得分: **70 / 100 → Rating B（CONDITIONAL PASS）**

## 结论

**⏳ CONDITIONAL PASS（70/B）** — 非 PASS，不满足设计文档 §十"Design Review PASS ≥90（🔴 0）"。

方案架构正确、六要素闭环、模板能力全部实测可用；但 1 个 🔴（单位换算缺失）阻断核心"相近"关联的正确实施，3 个 🟡 需修正。按流程：**不生成 dev 实施 prompt**；RIG 清单交 ops 修 v1.1 后复审。扩展方向（§八）不入表已显式声明为"非缺口"，不计缺口。

## RIG 清单（ops 修 v1.1）

1. 🔴 RIG-1：§三 补充国家侧单位归一化（面积 ÷10000；GDP ×FX 汇率口径指定），匹配脚本 None 防护，TC 增加换算对照断言
2. 🟡 RIG-2：§二 A + §二 B 补充每列 width（备注/关联 pills 列 ≥160px）
3. 🟡 RIG-3：§七 / TC-09 基线 146 → 154，测试数表述统一
4. 🟡 RIG-4：§四 荷兰示例 → 真实命中对（广东↔柬埔寨/乌拉圭/墨西哥/韩国 等）
5. 🟢 OBS-1~4 建议一并处理：脚本命名 + gitignore、台湾华南归因/README 来源行、国家表列编号标注、双向回填机制

## 待确认清单

| □ | 项 | 类别 |
|:-:|:---|:-----|
| □ | RIG-1: FX 汇率口径（2023 年均 7.08 vs 指定来源） | 严格性 🔴 |
| □ | RIG-2: 11 + 3 列宽度明细 | 严格性 🟡 |
| □ | RIG-3: 基线 154 + 测试数表述 | 严格性 🟡 |
| □ | RIG-4: 荷兰示例替换为实测命中对 | 严格性 🟡 |
| □ | OBS-1: 匹配脚本定位 + `_provinces-source.json` gitignore | 合理性 🟢 |
| □ | OBS-2: 台湾华南归因 + README 数据源行 | 合理性 🟢 |
| □ | OBS-3: 国家表追加列编号标注 | 合理性 🟢 |
| □ | OBS-4: 单方向匹配 + 反向回填机制 | 合理性 🟢 |
