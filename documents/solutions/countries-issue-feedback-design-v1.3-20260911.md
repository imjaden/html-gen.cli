# A 型表格 GitHub Issue 反馈通道设计 v1.3 (2026-09-11)

> 闭环: HTML-GEN-CL009（修订并入）· 模式: 独立（不入调度队列）
> v1.3 修订: 首条真实反馈 issue #2 暴露三处缺陷 → 表单改版（**字段下拉 + 值 textarea**）+ **主键双层保护**
> 决策（全量）: A1 B1 C1 D1 E1 F2 G1 H1 I1 J1 + K1 L1 M1 N1 O1
> 前置: v1.0（首版）→ v1.1（评审 findings）→ v1.2（文案/`--issue` 修复）→ 本版

## 1. 背景与需求

v1.2 上线后收到首条真实反馈 issue **#2**：

```
title: [数据反馈] countries · 阿尔及利亚 · country_zh
字段=country_zh ｜ 当前值=阿尔及利亚 ｜ 建议值=「针对 Note 字段进行补充」
来源=外交部国家概况 ｜ 补充说明=（民族/宗教/自然地理/简史 大段正文）
```

反馈者真实意图是更新 **note**，但表单只能表达 `country_zh`——由此暴露三处缺陷：

| # | 缺陷 | 根因 | 后果 |
|:-:|:--|:--|:--|
| P1 | **主键可写** | `feedback-targets.yaml` 的 `editable` 含 `country_zh` / `country_en` | 反馈可改写主键，数据失去锚点 |
| P2 | **字段错位** | 页面按「点击的列」预填 `field`（O1 决策），而主键列正是分栏默认触发列 | 点国家名 → 预填 `country_zh`，与意图无关 |
| P3 | **无字段选择控件** | `字段` 是自由文本 input | 用户无法从既定列中挑选，反馈落不到明确字段 |

机制约束（v1.0 已核实，本版决定性）：**GitHub Issue Form 的 URL 预填只支持 `input` / `textarea`，
`dropdown` 不可预填** → 「下拉选字段」与「页面自动带出点击列」互斥，本版选择前者（D1）。

需求（用户原文要点）：① 主键不可修改；② 单独提供「字段下拉 + textarea」组成 `key: value`，
使反馈精确更新到明确的字段。

## 2. 决策记录

| 项 | 决策 | 说明 |
|:--|:--|:--|
| A1 | `key_field` + `alt_key` 同时移出 `editable`，并加**代码层硬保护** | 双层；单层失效不致误写主键 |
| B1 | `字段` 控件改 **dropdown**（选项文本 `标签｜key`），值改 **textarea** | 用户从既定列中选，杜绝自由文本 |
| C1 | 改**按案例模板** `data-fix-countries.yml`，选项与 `editable` 一一对应 | 打破 v1.0 的 T1「一份通用模板」，以 L1 校验兜住漂移 |
| D1 | 页面只预填行上下文（page/dataset/row/row_en），**不再预填 field / current** | 消除 P2 错位；代价 = 放弃「点击列自动带入」 |
| E1 | 一条 issue 一个字段（key: value） | forms 无重复块机制；多字段请另开一条 |
| F2 | 删除「当前值」字段 | 与下拉选项无法对应，且冗余易误导 |
| G1 | 保留「行标识」input（预填主键值，标注请勿修改） | 仍需它定位行；改坏 → 脚本拒绝 |
| H1 | label 文本保持不变（`字段` 等），仅改控件类型 | 旧 issue body 仍可解析 |
| I1 | issue #2 走一次性处置：正文写入 `note` → 回评 → 关闭 | 内容是真实有效的 |
| J1 | 并入 HTML-GEN-CL009（设计升 v1.3 + 重跑实现审计） | 功能未验收，本质是同一闭环的修订 |
| K1 | 下拉选项文本 `标签｜key`；解析取**末段 `｜` 之后**为 key，回退整串精确匹配 key | key 段稳定，标签可改不影响历史解析 |
| L1 | 模板手工维护 + 提供 `--check-template` 一致性校验 | 一期单案例，不造生成器 |
| M1 | 模板名来自数据 JSON `options.feedback.template`（默认回退 `data-fix.yml`） | 案例自描述，复用不改代码 |
| N1 | 新增 `--issue N --field <key>`（人工裁决入口，如处置 #2） | 可复用、可审计 |
| O1 | body 解析双形态：裸 key（旧）/ `标签｜key`（新）+ 未知值拒绝 | 与 H1 一致 |

## 3. 数据契约

### 3.1 表单字段（`data-fix-countries.yml`）

| 控件 | id | label | 预填 | 必填 | 说明 |
|:--|:--|:--|:-:|:-:|:--|
| input | page | 页面 | ✅ | ✅ | 🔒 请勿修改 |
| input | dataset | 数据集 | ✅ | ✅ | 🔒 请勿修改 |
| input | row | 行标识 | ✅ | ✅ | 🔒 主键值；脚本**永不写入** |
| input | row_en | 行英文标识 | ✅ | ⬜ | 🔒 二次校验 |
| **dropdown** | field | 字段 | ⬜ | ✅ | 15 个可写列，选项 `标签｜key`（`multiple: false`） |
| **textarea** | value | 建议值 | ⬜ | ✅ | 数值列的 description 注明「只填数字」 |
| input | source | 来源 | ⬜ | ✅ | 权威出处 |
| textarea | note | 补充说明 | ⬜ | ⬜ | 多行原样保留 |

注：v1.2 的 `current`（当前值）字段删除（F2）；`###` 段落标题即 label 文本（解析按此精确匹配）。

### 3.2 下拉选项（= `editable`，按数据列顺序）

```
首都｜capital_zh            首都英文｜capital_en        纬度｜capital_lat
经度｜capital_lon           大洲｜region_tags          面积 km²｜area_km2
人口(万)｜pop_wan           GDP(亿美元)｜gdp_yi        定位｜loc_url
主要民族｜ethnic_groups     主要信仰｜religions        面积相近省份｜area_province
人口相近省份｜pop_province  GDP相近省份｜gdp_province  备注｜note
```

**不含**：`country_zh`（主键）、`country_en`（匹配键）、`videos`（保护列）。

### 3.3 URL 预填参数（页面生成）

```
https://github.com/<repo>/issues/new
  ?template=<options.feedback.template，缺省 data-fix.yml>
  &title=[数据反馈] <dataset> · <row> · <模板标签?>
  &page=<location.pathname 去前导 />
  &dataset=<options.feedback.dataset>
  &row=<row[key]>
  &row_en=<row[altKey]>
```

**不再包含** `field` 与 `current`（D1）。title 亦不再拼接字段名（字段由用户选）。

### 3.4 label→key 映射（脚本侧）

`标签｜key` → 取末段 `｜` 之后（strip）为 key；无 `｜` 时整串按 key 精确匹配（旧 issue 兼容）；
两者皆不匹配 → `[跳过] 字段值无法识别`。

## 4. 模板改动点（layout-table.html）

| 项 | v1.2 | v1.3 |
|:--|:--|:--|
| `buildFeedbackUrl` 参数 | page/dataset/row/row_en/field/current | page/dataset/row/row_en + **template** |
| 列上下文（`openSplitAt(idx,colKey)`/`splitField`） | 用于预填 field/current | **保留实现但不再参与 URL**（无害；供未来复用） |
| 按钮/门控/encodeURIComponent/noopener | — | 不变 |

## 5. CLI 参数矩阵（html-gen.py table）

| 来源 | 参数 | 优先级 | 语义 |
|:--|:--|:--|:--|
| CLI | `--feedback-repo OWNER/REPO` | 1 | 显式空串 = 禁用 |
| env | `HTML_GEN_FEEDBACK_REPO` | 2 | 兜底 |
| JSON | `options.feedback.repo` | 3 | 案例级默认 |
| JSON | `options.feedback.template` | — | 表单模板名（默认 `data-fix.yml`），供页面拼 URL |

## 6. .github/ISSUE_TEMPLATE 规格

- **新增** `data-fix-countries.yml`（9 → 8 字段：删 `current`；`field` 改 dropdown；`name: 数据反馈`、`title: "[数据反馈] "`、`labels: ["data-fix"]`）
- **删除** `data-fix.yml`（避免 issue chooser 双入口）
- **保留** `config.yml`（`blank_issues_enabled: false`）
- **一致性校验**：`scripts/countries-issue-sync.py --check-template`
  比对「模板 dropdown 选项的 key 集合」↔「config `editable`」，并比对选项标签 ↔ 数据 `columns[].label`；
  不一致 → exit 1 + 列出差异（防手工漂移）

## 7. 同步脚本规格（scripts/countries-issue-sync.py）

### 7.1 CLI

```
[--config …] [--target countries] [--list | --dry-run | --apply] [--close]
[--issue N] [--field KEY] [--repo …] [--limit N] [--check-template] [--json]
```

- `--field KEY`：仅与 `--issue N` 联用，**显式覆盖** issue 所填字段（人工裁决入口，N1）
- `--check-template`：只读一致性校验（L1），与其它模式互斥，exit 0/1

### 7.2 校验链（在 v1.2 六项之上强化）

1. `page` 匹配 target（全路径或 basename）
2. `dataset` 匹配
3. **字段解析**：`--field` 覆盖 → 否则 `标签｜key` → 裸 key（O1/K1）
4. **硬保护**：`field ∈ {key_field, alt_key}` 或 `∈ protected` → **拒绝**（A1，配置误列也拦）
5. `field ∈ editable`
6. 行唯一定位（key → alt 退化；0 或多命中拒绝）
7. 类型：`types[field]=='number'` → 可 `float()`；否则非空字符串
8. 建议值非空；`suggested == current` → 跳过（幂等）
9. 冲突：同 (row, field) 多条 → 取最新

### 7.3 输出与退出码

- 输出形态同 v1.2（`[列表]/[预览]/[更新]/[跳过]/[冲突]/[执行]/[回评]`），字段名显示为 key
- 退出码：0 成功（含无待处理/全跳过）/ 1 校验失败或外部调用失败 / 2 参数错误

## 8. 配置规格（scripts/feedback-targets.yaml）

```yaml
targets:
  countries:
    repo: imjaden/html-gen.cli
    label: data-fix
    dataset: countries
    template: data-fix-countries.yml      # 新增（M1）
    page: demos/countries-table.html
    data: data/_countries-data.json
    html: demos/countries-table.html
    key_field: country_zh
    alt_key: country_en
    editable: [capital_zh, capital_en, capital_lat, capital_lon, region_tags, area_km2,
               pop_wan, gdp_yi, loc_url, ethnic_groups, religions,
               area_province, pop_province, gdp_province, note]        # 15 项（去两键列）
    protected: [videos]
    key_guard: [country_zh, country_en]   # 新增：主键/匹配键硬保护（A1，双保险）
    types: {capital_lat: number, capital_lon: number, area_km2: number, pop_wan: number, gdp_yi: number}
    parse_fields: {page: 页面, dataset: 数据集, row: 行标识, row_en: 行英文标识,
                   field: 字段, suggested: 建议值, source: 来源, note: 补充说明}  # id 沿用 suggested（label 不变, H1）; current 移除（F2）
    rebuild: { args: [--github-url …, --home-url …, --favicon …, --feedback-repo …] }
```

## 9. 测试计划（tests/test_issue_feedback.py）

| 用例 | 断言 |
|:--|:--|
| TC-02′ URL 无 field/current | 分栏打开后 URL 含 page/dataset/row/row_en/template，**不含** field/current |
| TC-05′ 页面不预填字段 | 点击任意列（含主键列）→ URL 仍无 field/current |
| TC-23 下拉文本解析（K1） | `备注｜note` → `note`；`备注｜note｜x` → `x` 段规则；裸 `note` → `note`（O1） |
| TC-24 主键硬保护（A1） | issue 填 `country_zh` / `country_en` → 拒绝（即使 config 误列亦拒绝） |
| TC-25 未知字段值 | 下拉值改为未知名 → 跳过并说明 |
| TC-26 value 多行（F2/I1） | 多行建议值原样写入（`\n` 保留），JSON 往返逐字 |
| TC-27 `--issue N --field KEY`（N1） | 覆盖生效；仅与 `--issue` 联用（单独 `--field` → exit 2） |
| TC-28 `--check-template`（L1） | 一致 → exit 0；篡改模板选项 → exit 1 + 差异清单 |
| TC-29 current 字段移除 | 模板 YAML 不含 `id: current`；parse_fields 无 `current` |

## 10. 文档同步面

AGENTS.md（表单/脚本/参数说明）· features.md（计数）· documents/table-template-handbook §9（反馈通道章节）·
skills/html-gen/SKILL.md（+ `prompt --site` 重生成）· 设计 v1.3 · review-log/.review-level.yaml（评审回填）

## 11. 验收清单

- [ ] 模板 dropdown 只能选到 15 个可写列；`country_zh`/`country_en`/`videos` 均不在选项
- [ ] 提交主键/匹配键 → 脚本拒绝（硬保护，配置层删除 + 代码层拦截）
- [ ] `标签｜key` 与裸 key 双形态解析；未知值跳过并说明
- [ ] 多行建议值原样写入（issue #2 的补充说明 → `note`）
- [ ] 页面 URL 不再含 field/current；模板名来自 `options.feedback.template`
- [ ] `--check-template` 通过；篡改即报差异
- [ ] `--issue 2 --field note --apply` 后 JSON 仅 `note` 变化 + 产物重建 + 回评 + 关闭
- [ ] 全量测试全绿；线上表单链路可用
- [ ] 实现审计 PASS

## 12. 复用指引

| 层 | 复用成本 |
|:--|:--|
| 模板按钮 / `buildFeedbackUrl` / `--feedback-repo` | 零改动 |
| 数据 JSON | `options.feedback = {dataset,key,altKey,repo,template}` |
| 配置 | 新增一份 target（含 `editable` / `key_guard` / `template` / `parse_fields`） |
| **表单** | **每个案例一份** `data-fix-<case>.yml`（dropdown 选项案例专属），用 `--check-template` 保证与 config 一致 |
| 不适用 | doc / knowledge / slide（无「数据行」概念） |

## 13. 风险与边界

- **能力取舍**：dropdown 不可预填 → 永久放弃「点击列自动带入」（D1）；若日后更看重，需回退 input 方案（B2）
- **模板漂移**：per-case 模板手工维护，靠 `--check-template` 兜底；标签可改、**key 段必须稳定**
- **历史 issue**：`#2` 这类「字段=主键」的旧提交在新规则下被拒（不误改数据）；如需落库走 `--issue 2 --field note`
- **多字段反馈**：一条一字段（E1）；多字段请另开 issue
- **主键保护双层**：配置（editable/key_guard）+ 代码（硬保护），单层失效不致误写

## 14. 版本演进

| 版本 | 日期 | 要点 |
|:--|:--|:--|
| v1.0 | 2026-09-10 | 首版：按钮 + 预填 + 白名单写回 + 配置驱动 |
| v1.1 | 2026-09-10 | 折入设计评审 HG-SEC-110..118（repo 落 JSON / gh list-form / 解析边界 / rebuild.args） |
| v1.2 | 2026-09-10 | 审计后跟进：「数据纠错」→「数据反馈」、`--issue` 改 `gh issue view` 直查 |
| v1.3 | 2026-09-11 | **issue #2 驱动**：字段下拉 + 值 textarea、主键双层保护、per-case 模板与一致性校验、页面停止预填 field/current |
