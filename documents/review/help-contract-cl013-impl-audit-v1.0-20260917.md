# help 契约四模板补齐 — 实现审计报告 v1.0

> 日期: 2026-09-17 · 闭环: **HTML-GEN-CL013 [5/6] 实现审计** · 角色: review（独立复跑，不采信 ops 自报）
> 被审对象: `7b99701`（`docs@help:` dev 会话产出, 12 文件）+ `3044139`（`docs@sync:` ops 交互会话落地 AGENTS.md, 1 文件）+ `98a2e4d`（`docs@verify:` ops 核查报告, 1 文件）
> 累积改动: 3 笔 / 14 文件（`git diff --name-only 90e6bef..HEAD`）
> 基线: `90e6bef`（= github/main 起点; 归档快照 `/tmp/cl013-base`）
> 需求源（唯一）: `documents/solutions/html-gen-help-contract-design-v1.3-20260917.md`（§C / §D CL013 行 / §F / §G）
> 设计评审: 既有两轮（v1.0 80/B · v1.1 85/B；v1.3 属审计 finding 直接订正，不另开评审轮）
> **结论: PASS —— 94/100（D1–D7 全成立 · X1–X3 可接受 · O1–O6 登记如实 · 0 阻断 finding）**

---

## ① 逐条复跑结论（命令 + 实测输出摘要）

以下 8 项均为 review 独立执行，非引用 ops/dev 自报。

### 1.1 前置取证

```
pwd && git rev-parse --show-toplevel && git rev-parse --short HEAD && git status --short
```
实测: `pwd` = `/Users/jadenli/CodeSpace/html-gen.cli`（锚点核验通过）· HEAD = `98a2e4d` · `git status --short` 空（干净）。

### 1.2 ops harness 全量复跑

```
python3 cache/closed-loop/HTML-GEN-CL013-verify.py
```
实测: **RESULT: PASS** —— `PASS=57  FAIL=0  N-A=1  WARN=0`（完整日志 `cache/closed-loop/cl013-harness-run-review.log`）。

与 ops 最终日志 `cl013-harness-run-ops-final.log`（`PASS=56`）对读: 差异 1 条 = **T03b**（本批累积改动 90e6bef..HEAD ⊆ 授权集）。ops 跑时 HEAD=3044139（累积 13 文件，无 T03b 或未计入），review 跑时 HEAD=98a2e4d（累积 14 文件，T03b 单独 PASS）。属判据数量差异（笔③ ops 报告提交后累积面多 1 文件），非结果分歧 —— 两轮均 `FAIL=0`。

关键三段对读（与 ops 完全一致）:
- pytest: 守卫 `22 passed, 80 subtests` / 全量 `334 passed, 80 subtests in 132.45s` / 基线 `/tmp/cl013-base` `326 passed`
- 变异: `T70 变异①（table 列属性删除）→ 断言转红且指名键 red=True named=True` + 还原后全绿
- 产物: `T60 重建产物与入库产物字节一致 sha_rebuild=556d58839fe0c000 sha_committed=556d58839fe0c000`

### 1.3 判据非恒真反证（修前副本跑同一 harness）

把 harness 的 `REPO` 常量指向 `/tmp/cl013-base` 归档副本（副本无 `.git`，脚本另生成于 `/tmp/cl013-verify-base.py`）跑全量:
```
python3 /tmp/cl013-verify-base.py   # 完整日志 /tmp/cl013-verify-base.log
```
实测: **31 FAIL**（其中 **30 个为内容判据真红** + 1 个副本无 git 的环境噪音 T01）。ops 报告口径「29 FAIL」为「90e6bef 完整工作树」跑（有 git，T01 PASS + T70 变异正常）。

30 个内容判据在修前真红，覆盖:
- 契约面: T10 ×3（doc/slide/knowledge 修前为 `legacy` 骨架）+ T11 ×4（cli 修前 `[]`）+ T12（doc url_state 空）+ T13（slide behaviors 0）+ T14 ×2（item/groups `None`）+ T15（table cli 0≠9）
- help 渲染面: T21 ×2（无 width=narrow/sidebar=0）+ T22（无「搜索」）+ T23 ×3（无 --groups/--welcome/默认文案）+ T27（无「无 URL 状态」说明）
- 独立提取面: T40 ×4（契约 cli 空）+ T41（doc URL 契约空）+ T42（item 契约空）+ T43（groups 契约空）
- 文档面: T50（裸键表 6 条）+ T45（dev 测试 item 提取空）+ T51（AGENTS.md 键定义行 **26 条**）+ T52b（逐文件列和 340≠326）

结论: 判据**非恒真**成立 —— 修前红 / 修后绿，判据有区分度。

### 1.4 两件专项取证独立复跑

```
python3 cache/closed-loop/cl013-d7-fidelity.py
python3 cache/closed-loop/cl013-t51-precheck.py
```
实测:
- **d7-fidelity（D7 保真三问）**: Q1 `True`（本批 md 重建 == 入库新产物，忽略 meta 行）/ Q2 `True`（旧 md + 当前生成器 head 段 == 入库新产物 head 段 → 顺序变化归因模板演进）/ Q3 返回 `总 0`。
- **t51-precheck（键定义行双态）**: 修前(工作树)=0 / 修后(补丁产物)=0。

**两脚本的脆弱依赖（🟢 观察，见 §4）**: d7-fidelity Q3 硬编码 `git show HEAD~1:demos/table-guide.html` 取「旧产物」，review 复跑时 HEAD 已前进到 98a2e4d、HEAD~1=3044139 的 table-guide.html 已是重生成后产物 → diff 自然为 0。t51-precheck 的「修前」标签硬读「工作树 AGENTS.md」，而工作树已是修后状态 → 「修前」标签失真读成修后内容。

为此 review 另做**独立复算**（不依赖两脚本的标签/HEAD 假设）:
- **Q3 实质**: `git show 90e6bef:demos/table-guide.html`（真基线旧产物）vs HEAD 新产物 → `总 110 = meta 2 + head 2 + 其余 106`，与 ops 报告 D7 的「meta 2 + head 2 + 键名移除 106」**逐字吻合**。其余 106 行经抽样确认全为「键名移除 / 叙述改写 / 引用契约」，无隐藏改动。
- **T51 双态**: `git show 90e6bef:AGENTS.md` 跑 DEF_ROW 判据 → **26 条键定义行**；HEAD AGENTS.md → **0 条**。独立证实 ops 的「修前 26 / 修后 0」论据，且证明 T51 键定义行判据非恒真。

### 1.5 全量 pytest 独立复跑（步骤 4）

```
/opt/homebrew/Caskroom/miniconda/base/envs/py3.12/bin/pytest tests/ -q -n 0
```
实测: **334 passed, 80 subtests passed in 135.50s**（`ls tests/test_*.py | wc -l` = 31）。与 harness T31 一致。

### 1.6 既有断言 0 处改动核实（步骤 5）

```
git diff 90e6bef..HEAD --stat -- tests/
```
实测: 仅 `tests/test_help_contract.py | 339 +++---（+306/-33）` 1 个文件改动；**其余 tests/ 文件 0 改动**。符合「本批仅允许改 tests/test_help_contract.py」。

### 1.7 范围合规（步骤 6）

`git diff --name-only 90e6bef..HEAD` = 14 文件，逐笔核 `git show --name-only` 确认三笔归属:
- 笔① 7b99701: 12 文件（html-gen.py / tests/test_help_contract.py / AGENTS.md 外 9 文档文件 + demos/table-guide.md/.html）
- 笔② 3044139: 1 文件（AGENTS.md）
- 笔③ 98a2e4d: 1 文件（documents/review/help-contract-cl013-ops-verify-v1.0-20260917.md）

14 文件全部落在白名单内（`html-gen.py` / `tests/test_help_contract.py` / `AGENTS.md` / `features.md` / `README.md` / `README.zh.md` / `skills/html-gen-cli-spec/SKILL.md` / `skills/html-gen-{table,doc,slide,knowledge}/SKILL.md` / `demos/table-guide.md` / `demos/table-guide.html` / ops 报告）。**白名单外零改动**。

### 1.8 契约口径逐条复核（步骤 7，对照设计 §C/§3 实测）

| 维度 | 设计目标 | 实测 | 结论 |
|:--|:--|:--|:--|
| table CLI | 9 | 9（--data/--title/--subtitle/--output/--github-url/--home-url/--favicon/--feedback-repo/--quiet） | ✅ |
| doc CLI | 9 | 9（--input/--output/--title/--subtitle/--metadata/--github-url/--home-url/--favicon/--quiet） | ✅ |
| slide CLI | 8 | 8（无 --metadata） | ✅ |
| knowledge CLI | 10 | 10（--data/--groups/--title/--subtitle/--welcome/--output/--github-url/--home-url/--favicon/--quiet） | ✅ |
| doc url_state | 3 | `?sidebar`/`?toolbar`/`?width`（params.get 提取 sidebar/toolbar/width） | ✅ |
| slide behaviors | 8 | 分页/导航/全屏/进度点/记忆/侧栏H3/侧栏搜索/性能警告 | ✅ |
| slide 无 URL 状态 | 如实写明 | `url_state_note` + help 渲染「无 —— slide 不使用 URL 参数…」 | ✅ |
| knowledge item | 7 | title/group/section/badge/desc/url/icon | ✅ |
| knowledge groups | 3 | key/label/icon | ✅ |
| knowledge 数据源 | 三态 | 数组 / `{items|data}` / 顶层 `output` | ✅ |
| table 各维度 | 22/13/6/6/5/7/5 | 22/13/6/6/5/7/5（+ url_state 3 / behaviors 4 / top_level 7） | ✅ 未削弱 |

### 1.9 断言强度抽查（步骤 8，独立变异，/tmp 副本内执行）

```
# 变异①: 删 doc url_state 的 ?width 条目 → test_17 应红
# 变异②: 删 knowledge item 的 icon 条目 → test_19 应红
```
实测（均在 `/tmp/cl013-mut-review` / `/tmp/cl013-mut-kb` 副本，零污染 live 树）:
- 变异①: `test_17_doc_url_state_matches_template` **FAILED**，指名 `'width'` + 来源 `layout-doc.html` + 修复动作「在 TEMPLATE_CONTRACT["doc"]["data"]["url_state"] 补该键 (键名口径与 table 一致, 带 ? 前缀)」
- 变异②: `test_19_knowledge_item_keys_dual_source` **FAILED**，指名 `'icon'` + 来源 `layout-knowledge.html + html-gen.py (双源)` + 修复动作

结论: doc/knowledge 维度断言**真会红并指名键**，非恒真。

---

## ② D1–D7 判定表（dev 申报 7 条偏差）

| # | 内容 | 判定 | 依据（review 独立实测） |
|:--|:--|:--|:--|
| D1 | doc/slide `url_state` 双落点（`data` 分区 + 节点顶层，同一 list 对象别名） | **成立** | `html-gen.py:896-897` 让两键指向**同一 list 对象**（引用别名非拷贝，单一真源）；渲染经 `_spec_entries`（L1164-1169）`data[dim] 优先`只走一次；harness T28 无重复渲染 + T12/T41 双通过。设计 §A 未 pin 落点，任务书 R1 要求 `data.url_state`、CL012 渲染器读节点顶层，别名调和是唯一同时满足两方的折中 |
| D2 | 设计 §D item 双源正则 `item\.get\('([a-z]+)'\)` 恒为空集 → 收窄为容忍第二参数 | **成立（设计 errata）** | review 独立复算: 字面正则命中 `[]`（空），容忍形态 `item\.get\('([a-z]+)'` 命中 `['group','icon']`；生成器两处调用 `html-gen.py:617` `item.get('group','其他')` / `:620` `item.get('icon','')` 均带默认值。收窄必要（否则双源断言退化为恒真单向 ⊆）。最贴设计写法即「去掉结尾 `\)` 容忍第二参数」——设计意图是「生成器自动分组推导」，实际调用带默认值 |
| D3 | 任务书 R2 写「table/knowledge 另 HTML_GEN_FEEDBACK_REPO」，实测仅 cmd_table 消费 → 只在 table 段写 | **成立（任务书字面有误）** | `feedback_repo_args` 唯一调用点 `html-gen.py:574`（cmd_table 内）；`--feedback-repo` 仅注册 table 子解析器 `:1280`；`HTML_GEN_FEEDBACK_REPO` 仅 `:144` 读取。按实测收窄成立 |
| D4 | knowledge ② 示例段补段首注记行，三块示例逐字保留 | **成立** | `HELP_KNOWLEDGE_EXAMPLES`（L1042-1063）段首注记「以下为示例, 键名以键规范段 (item/groups/数据源与输出目标) 为准。」+ 三块（条目数据 / 输出目标 / 类目分组）逐字保留。示例块未列 icon 属正常（② 示例是叙述非规范，icon 由 ① 键规范段定义） |
| D5 | AGENTS.md 未由 dev 写（受保护），改产补丁，ops 交互会话落地 | **成立** | review 实测 `shasum -a 256 AGENTS.md` = `42d1273e90967f14b7eaf98e3e9346f09f6aac8b42a791ff9aae89b3c67fe378`，与补丁产物 `cache/handoff/cl013-agents-md.new.md` **逐字节相同**（`diff -q` 空）；git status 干净（无半写状态） |
| D6 | 顺手订正陈旧计数: README/README.zh 246→334、features.md 312→引用 AGENTS.md、cli-spec 删「--version 未实现」 | **成立（不越界）** | README.md/.zh diff 确认 246→334（"authoritative count"）；features.md「312 用例」→「见 AGENTS.md（唯一计数源）」；cli-spec §3 删「`--version` 未实现」观察项（CL016 已实现 `html-gen version`）。三处文件均在 §F 白名单内。**注**: features.md 统计表另有「CLI 参数 16→36」「localStorage keys 17→24」两处计数订正，超出 D6 字面申报但属同族消除漂移，方向正确，🟢 观察（见 §4） |
| D7 | demos/table-guide.html 重生成带入 2 处无关漂移（head 顺序 + meta 时间戳） | **成立** | Q1/Q2 独立复跑均 True；Q3 实质独立复算 `110 = meta 2 + head 2 + 键名改写 106`，2 处 head 顺序变化归因模板演进（Q2 证）、meta 时间戳归因重建时刻，非本批 md 改写引入 |

---

## ③ X1–X3 裁定（ops / 环境侧披露）

**X1（ops 自身动作）**:
- (a) AGENTS.md 落地: 成立。sha256 逐字节匹配补丁产物（见 D5），首轮 BLOCKED fail-closed 未留任何半写状态（git status 干净、diff 空）。
- (b) ops 改自己判据 2 处: 成立，**非「为过而放宽」**。T52b 正则补含数字文件名（`test_slide_h3_toggle`）是「修正漏检」；T51 由「grep 单键」改为「键定义行形态」是「强化」（防弱代理假通过）。review 独立验证 ops 的「修前 29 FAIL / 修后 45→56 PASS」论据: 反证得 31 FAIL（30 内容 + 1 噪音），T51 双态独立复算 26/0 —— **论据成立**。

**X2（dev 回读 ops harness 的耦合）**: **不构成实质独立性损害**。T40–T44 是 ops 用自己的正则从 `layout-*.html` / `html-gen.py` 重新提取（不以 dev 测试为输入），仍是独立证据。D1 别名确为 dev 适配 ops 口径的产物，但别名正确性由 ops 的 T12/T28/T41 **独立验证**（单一真源 / 无重复渲染 / 内容一致），非「塞键变绿」。可接受，无需补独立证据。

**X3（knowledge Bare 模式语义存疑）**: **可接受为登记观察项**。实测 `layout-knowledge.html` 无 sidebar/toolbar URL 参数读写（L396 仅给 iframe 详情页追加 `sidebar=0&toolbar=0`），AGENTS.md 该句疑历史漂移。本批按「只去键名、不动极性」最小改动合理，语义订正另批，**不据此判本批 FAIL**。

---

## ④ 观察项 O1–O6 裁定（登记是否如实 / 是否另立批）

| # | 事项 | 登记是否如实 | 裁定 | 另立批？ |
|:--|:--|:--|:--|:--|
| O1 | `?show-md`（layout-doc.html:273）未被 §D 正则 `params\.get\('([a-z]+)'\)` 覆盖（连字符不匹配） | ✅ 如实（review 实测 L273 `params.get('show-md')` 真实存在且无守卫） | 补它 = doc 契约 URL 3→4（口径扩容）→ 须另批 + 评审 | **应另立批** |
| O2 | repo `skills/` 是镜像，真源 `~/.hermes/profiles/dev/skills/software-development/html-gen*` | ✅ 如实 | 本批只改镜像，正向同步会覆盖回；跨 profile 写需用户授权 | **应另立批（需授权）** |
| O3 | `prompts/`（31 文件 tracked 生成物）未重建，与 skills 漂移 | ✅ 如实 | 与 O4/O5 同类（生成物刷新），可合并一小批 | 可合并小批 |
| O4 | `src/html_gen/`（gitignored 构建产物）未重建 | ✅ 如实 | 设计 §OUT 明确不做，分发前重建即可 | 不需另批 |
| O5 | `skills/html-gen-table/references/table-demo-prompt.md` 仍枚举键名骨架，无 help 指针 | ✅ 如实（review 实测 L10/L12/L13/L18/L22-23 枚举键名，且**不完整**：列类型漏 videos、列属性漏 hide/initialHidden/splitFull/pillFilter 等） | **真缺口（低危）**: 它是 demo 生成提示词的脚手架，键名枚举不完整且有漂移风险，非「面向人的键规范」；但按 §F「键表只在契约」的严格口径应改引用。**最小闭合集**: 在「数据规范」骨架块 +「列类型」块加一行指针「完整键表见 `html-gen help table`，本骨架仅作生成提示，不保证完整」 | **建议另立小批（可与 O3 合并）** |
| O6 | knowledge「Bare 模式」语义漂移（同 X3） | ✅ 如实 | 语义订正另批 | 应另立批 |

---

## ⑤ 范围外声明

- **`cache/**` 全 gitignored**: 本轮 review 产生的 `cache/closed-loop/cl013-harness-run-review.log`、`/tmp/cl013-verify-base.py`、`/tmp/cl013-verify-base.log`、`/tmp/cl013-mut-review`、`/tmp/cl013-mut-kb`、`/tmp/cl013-tg-*` 均不入提交，勿提交勿恢复。
- **他线未跟踪文件**: 无（harness T80 `git ls-files --others --exclude-standard` 空）。
- **本批外既有红项**: ① CL012 遗留 `HG-SEC-177..179`（非本批，已于 CL012 审计折 CL013/设计 v1.3）；② `HG-SEC-134`（pre-existing，非本批引入）；③ O1–O6 观察项（本批范围外，已登记待另批）。以上均**不属本批**，勿在本批提交中处置。

---

## ⑥ 结论 + 分数

- **结论: PASS**。8 项逐条复跑全通过；D1–D7 全成立（含 1 处设计 errata D2 + 1 处任务书字面误 D3）；X1–X3 可接受（X1(b) 判据强化论据经独立验证成立，X2 不损害独立性，X3 登记合理）；O1–O6 登记如实；白名单外零改动；判据非恒真已反证（31 FAIL）；断言强度已独立变异验证（doc/knowledge 维度真红并指名键）。
- **Score: 94 / 100**（L2 百分制；参考 CL012 实现审计 93/100）
- **扣分（均为非阻断 🟢）**:
  1. D1 别名调和引入「url_state 双落点」认知负担，需注释解释（虽单一真源正确）— 未扣硬分，留观察
  2. O5 table-demo-prompt.md 键名骨架残留（真缺口低危）
  3. 两专项脚本（d7-fidelity / t51-precheck）对 HEAD 位置/工作树状态有脆弱依赖（硬编码 HEAD~1 / 假设工作树=修前），导致 review 复跑时 Q3 返回 0、t51 标签失真
  4. features.md 的 D6 外两处计数订正（CLI 16→36、localStorage 17→24）超出字面申报

---

## 待处置编号（需用户或后续批次处理）

| # | 事项 | 落点 | 处置建议 |
|:--|:--|:--|:--|
| A1 | O1 `?show-md` 守卫盲区 | `layout-doc.html:273` + 设计 §D doc URL 正则 | 另批 + 评审（doc 契约 URL 3→4 口径扩容） |
| A2 | O5 table-demo-prompt.md 键名骨架残留 | `skills/html-gen-table/references/table-demo-prompt.md` L10/L12/L13/L18/L22-23 | 加 help 指针（最小闭合集见 §4 O5），可与 O3 合并小批 |
| A3 | O3 prompts/ 生成物漂移 + O4 src/html_gen 分发前重建 | `prompts/`（31 文件）/ `src/html_gen/` | 合并一小批重建 |
| A4 | O6/X3 knowledge「Bare 模式」语义订正 | `AGENTS.md` knowledge 节 + `layout-knowledge.html` | 语义订正另批 |
| A5 | O2 skills 镜像/真源跨 profile 同步 | `~/.hermes/profiles/dev/skills/software-development/html-gen*` | 需用户授权后另批 |
| A6 | 两专项脚本 HEAD 位置脆弱依赖（🟢 加固建议） | `cache/closed-loop/cl013-d7-fidelity.py` / `cl013-t51-precheck.py` | 后续把 `HEAD~1` 改为显式基线 ref、t51 的「修前」改读 `git show 90e6bef:AGENTS.md`（非阻塞） |
| A7 | features.md D6 外两处计数订正复核 | `features.md` 统计表「CLI 长形参数 36」「localStorage keys 24」 | 复核数字口径（36=四模板长形 flag 之和非去重；24 需与模板 localStorage key 实际数对账） |
