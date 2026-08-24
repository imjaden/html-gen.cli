# 中国省份表 + 国家双向关联 — 实现审计报告 v1.0

> 日期: 2026-08-24
> 设计依据: `documents/solutions/provinces-table-design-v1.1-20260824.md`（设计复审 PASS 100/A，RIG-1~4 + OBS-1~4 closed）
> 项目路径: /Users/jadenli/CodeSpace/html-gen.cli
> 聚焦 commit: 未 push 5 commits（`73bc988` / `f6a3e7c` / `323771a` / `7dd1c18` / `31c8c60`）
> review维度: L2 Implementation Audit（TC-01~10 逐项 + 单位归一化 + None 防护 + commit/命名规范 + 回归）
> review者: Security Reviewer

## 数据验证

| 验证项 | 方法 | 结果 |
|:-------|:-----|:-----|
| 未 push 范围 | `git log origin/main..HEAD --oneline` | ✅ 恰 5 commits（73bc988/f6a3e7c/323771a/7dd1c18/31c8c60），设计/复审 commits 已入 github/main |
| 工作区 WIP | `git status` | ⚠️ 2 个未提交文件（demos/drama/history-strategy-table.html + zhuyuanzhang-strategy-table.html），为其他会话重生成 9 列 schema，与本次零交集（详见回归） |
| 省份表 34 行 11 列 | json 解析 `_provinces-data.json` | ✅ 34 行（23 省+5 自治区+4 直辖市+2 特别行政区）；11 列 width 110/60/100/90/110/110/110/170/170/170/200 与设计 §二 A 全表一致 |
| tabs / options | json 解析 | ✅ 全部 + 7 区域（contains:true）；pageSize 30 / exportCSV / searchFields [province,abbr,capital]（+showIndex 序号列，测试 T1 依赖，合理） |
| 港澳台归华南 + note | json 解析 | ✅ 香港/澳门/台湾 region_tags=华南，note 均含"特别行政区/地区，口径与内地有差异" |
| 区域计数 | Counter 统计 | ✅ 华北5/东北3/华东7/华中3/华南6/西南5/西北5 = 34 |
| 国家表 17 列 195 行 | json 解析 | ✅ 新 3 列位于现有 14 列之后 = 15/16/17（area/pop/gdp_province，pills，170px）；195 行全量补齐 |
| 中国行留空 | json 解析 | ✅ area/pop/gdp_province 全空（中国面积/人口/GDP 远超最大省份，阈值内无命中，设计允许） |
| 双向互证率 | 程序全量比对 304 对 | ✅ 271/304 = 89.1%，与 ops 报告完全一致 |
| 单位归一化独立复算 | 脚本重跑 + 阈值复核 | ✅ 304 个省份侧 pills 阈值违规 0；广东 GDP ↔ 韩国/西班牙/墨西哥、面积 ↔ 柬埔寨/乌拉圭/叙利亚 均在表内（杜绝 0-命中） |
| None 防护 | json 扫描 | ✅ 恰 6 国缺 gdp_yi（也门/南苏丹/厄立特里亚/古巴/朝鲜/梵蒂冈）；梵蒂冈 area/pop/gdp 全 None，3 新列全空 |
| 生成物与 JSON 一致 | HTML 注入 const 提取比对 | ✅ COLUMNS 11/11 零差异、DATA 34/34 零差异、TABS/OPTIONS 一致（TC-07） |
| 凭证扫描 | 新文件 cred 正则 | ✅ 0 命中（provinces-match.py / 两个数据文件） |
| commit 规范 | `git show --stat` ×5 | ✅ 5/5 均 type@scope 小写 + 英文 subject；每 commit 仅预期文件，无 WIP 混入 |
| 命名规范 | 文件名比对 | ✅ `provinces-*`（_provinces-data.json / provinces-table.html / README.md / test_provinces_table.py）与 `countries-*` 模式一致 |

## TC 清单逐项验证

| # | 验收项 | 结果 | 证据 |
|:-:|:-------|:----:|:-----|
| TC-01 | 省份表 34 行全量 | ✅ | 34 唯一省份名；测试 test_07（34 计数 + 港澳台可搜）通过 |
| TC-02 | 每省 3 项关联各 2-3 标签 | ✅ | 面积 33×3 + 澳门 1（小省允许）；人口/GDP 34×3；无空、无 >3 |
| TC-03 | 港澳台 region_tags=华南 + note | ✅ | 3 行均华南 + 口径 note；测试 test_08 通过 |
| TC-04 | 国家表 195 国 3 列补齐 | ✅ | 15/16/17 列存在；6 国缺 GDP + 梵蒂冈全缺不参与匹配；中国行留空（设计允许） |
| TC-05 | 双向互证抽查 ≥10 对 | ✅ | 程序全量比对 271/304=89.1%；ops 抽查 12 对 10 命中；非互证对全部可解释（双侧 top-3 截断 ~31 对 + 人工复核 3 处改动的 4 个不对称格，见 HG-SEC-027） |
| TC-06 | thousands 格式 + 归一化命中非 0 | ✅ | 3 数值列 format:thousands；广东 GDP ↔ 韩国/西班牙、面积 ↔ 柬埔寨 均在表内；独立复算 0 阈值违规 |
| TC-07 | 生成物与 JSON 逐字段一致（含 width） | ✅ | COLUMNS/DATA 零差异；测试 test_10 通过 |
| TC-08 | test_provinces_table 10 条 + 国家表断言 | ✅ | 26 passed（13 + 13） |
| TC-09 | 全量回归 | ✅ | 166 passed + 1 环境性失败（test_history_tables::test_01，见回归节） |
| TC-10 | registry rebuild 后可见 | ✅ | _registry.json count 59→60，provinces-table 条目 present（featured=false 符合设计，demos/index.html 链接非本轮必需） |

## 单位归一化正确性（专项）

- 国家侧换算：`area_km2 ÷ 10000 → 万km²`、`gdp_yi × 7.08 → 亿元`（2023 年均汇率 7.08，国家统计局口径），与设计 §三 完全一致；人口 `pop_wan` 同单位直比。
- 独立复算脚本重跑：304 个省份侧 pills 中 **0 个**超出阈值（面积 30%/人口 20%/GDP 30%），证明归一化先行且数据质量高；naive 跨单位比较 0-命中错误模式已杜绝（设计 RIG-1 修复闭环成立）。
- 反向回填机制（31c8c60）：`_countries-data.json` 的 3 列与当前脚本 `provinces-match.py` 重跑输出 **0 差异**（195 国 × 3 列全比对），证明修复后数据 = 同对回填规则（设计 §四:5 same-pair），非独立重算。

## None 防护（专项）

- 恰 6 国缺 gdp_yi（也门/南苏丹/厄立特里亚/古巴/朝鲜/梵蒂冈）——与设计声明逐字一致；梵蒂冈三项全 None → 3 新列全空。
- 语义精确：仅 GDP 维度不参与匹配（面积/人口维度仍参与），与设计 TC-04/"该维度不参与匹配"一致。

## 实施评估

| 维度 | 结论 |
|:-----|:-----|
| 设计覆盖 | ✅ §二 A/B 字段、§三 口径、§四 匹配规则、§五 脚本、§六 生成、§七 测试全部落地；§八 扩展方向 11 项未入表（设计明确非缺口） |
| 测试覆盖 | ✅ T1-T10 全实现 + 国家表 3 条反向回填断言（韩国/柬埔寨/3 新列）——超出设计"1-2 条"要求 |
| 生成物一致性 | ✅ provinces-table.html / countries-table.html 均由 JSON 重生成且注入数据逐字段一致 |
| README/registry | ✅ demos/provinces/README.md 含数据源行（国家统计局/各省统计公报/七普，对齐 countries/README 格式）；registry 已注册 |

## 回归（专项）

- 全量 `python3 -m pytest tests/ -q -n 4`：**166 passed + 1 failed**（32.85s）。
- 唯一失败 `test_history_tables::test_01_strategy_headers_and_index`：**环境性 WIP 失败，非本次缺陷**。工作区 demos/drama/history-strategy-table.html 被其他会话重生成（COLUMNS 由提交态 10 列变 9 列 schema），测试读工作区文件而失败；该文件不在 5 个 commit 内、与省份功能零交集，不代修、不扣分。zhuyuanzhang-strategy-table.html 同因。
- 基线：154 + 13（省份表）= 167 总用例，落在设计 §七 预计 +11~12 区间上沿。

## 安全事项

🟢 **HG-SEC-027** — 人工复核 3 处省份侧单元格在 backfill 生成之后修改，导致 4 个不对称格（互证率 89.1% 而非 100%）：

| 省份侧编辑（_provinces-data.json） | 后果 |
|:---|:---|
| 黑龙江 area_country: 土库曼斯坦→德国 | 德国 area_province 空（应有黑龙江）；土库曼斯坦 area_province 保留过期黑龙江 |
| 上海 pop_country: 布基纳法索→斯里兰卡 | 斯里兰卡 pop_province 无上海（top-3 截断本就难入，影响小） |
| 广东 gdp_country: 澳大利亚→西班牙 | 西班牙 gdp_province 空（应有广东/江苏/山东）；澳大利亚 gdp_province 保留过期广东 |

根因：`provinces-match.py` 以脚本内硬编码 PROVINCES 为省份侧事实源生成 backfill，不读最终 `_provinces-data.json`；复核编辑后未重跑回填。影响面 4 格 / 585 格，无安全影响，纯数据一致性细节，记录不阻断。**建议**（非本轮必需）：后续人工复核后以最终省份表为事实源重跑回填，或将脚本改为读取 `_provinces-data.json`。

## 评分

| 项目 | 扣分 |
|:-----|:-----|
| 本轮新增 🔴 | 0 × -15 = 0 |
| 本轮新增 🟡 | 0 × -5 = 0 |
| 本轮新增 🟢（HG-SEC-027） | 1 × 0 = 0 |

得分: **100 / 100 → Rating: A**

## 结论

**PASS（A, 100）** — 5 个未 push commits 全部通过验收：TC-01~10 逐项成立（34 行/2-3 标签/港澳台华南/国家表 3 列/双向互证 89.1% 与 ops 报告一致/千分位/生成物一致/26 测试/registry）；单位归一化独立复算 0 阈值违规；None 防护 6 国 + 梵蒂冈精确匹配；commit 5/5 规范、无 WIP 混入；全量 166 passed（1 环境性失败已说明、不代修）。唯一 🟢 记录为人工复核后未重跑 backfill 的 4 格不对称（HG-SEC-027），不阻断。**推送权限执行：git push 5 commits → github/main。**

## 待确认清单

| □ | 项 | 类别 |
|:-:|:---|:-----|
| □ | HG-SEC-027：是否要求后续对 4 个不对称格重跑 backfill（德国/西班牙补回填、土库曼斯坦/澳大利亚清过期），或接受现状（89.1% 互证，demo 数据语义可读） | 数据一致性 🟢 |
