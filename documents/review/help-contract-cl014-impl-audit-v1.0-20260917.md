# help 契约 `?show-md` 纳入 doc URL 守卫 — 实现审计报告 v1.0

> 日期: 2026-09-17 · 闭环: **HTML-GEN-CL014 [5/6] 实现审计** · 角色: review（独立复跑，不采信 ops/dev 自报）
> 被审对象: `0b387ca`（`feat@cli:` [3/6] dev 实施）+ 设计链 `e6933aa` / `1e473c2` / `5b95469` + 评审 `d9a0e29` + 核查 `0463e39`
> 起点基线: `4e58407`（= github/main 起点）· 审计时 HEAD = `0463e39` · github/main = `d9a0e29`（本地领先 3 笔）
> 需求源（唯一）: `cache/draft/TODO-20260917.md` HTML-GEN-CL014 条目（gitignored，只读）
> 设计（唯一）: `documents/solutions/html-gen-help-contract-design-v1.4-20260917.md`（§0 订正 / §3.2 / §9 F1–F11 / §10 V1–V6 / §11）
> 设计评审: `documents/review/html-gen-help-contract-design-review-v1.4-20260917.md`（[2/6] CONDITIONAL PASS 88/100）
> ops 核查: `documents/review/help-contract-cl014-ops-verify-v1.0-20260917.md`（[4/6] PASS）
> 上游 finding: CL013 实现审计 HG-SEC-180（🟢）+ CL013 [6/6] 观察项 O1
> **结论: PASS —— 95/100（D1–D5 全成立 · HG-SEC-180/O1 就地闭合 · 0 阻断 finding · 1 🟢 record）**

---

## ① 逐条复跑结论（命令 + 实测输出摘要）

以下 8 项均为 review 独立执行，不引用 ops/dev 自报。

### 1.1 前置取证与链构成自证

```
pwd && git rev-parse --show-toplevel && git rev-parse --short HEAD && git status --short \
  && git log --oneline 4e58407..HEAD && git rev-parse --short github/main
```

实测: `pwd` = `/Users/jadenli/CodeSpace/html-gen.cli`（锚点核验 ✅）· HEAD = `0463e39` · `git status --short` 空（干净）· github/main = `d9a0e29`。

链构成（`4e58407..HEAD` 共 **6 笔**）:

| 笔 | 实测 subject | 归属 | 与任务书锚点 |
|:--|:--|:--|:--|
| ① | `docs@design: help 契约设计 v1.4 — CL014 ?show-md 口径扩容订正 + 事实卡` | [1/6] 设计 | ✅ 匹配 |
| — | `docs@design: …补记 — F12/F13 + O-CL014-1 升级` | [1/6] 设计补记 | 额外设计迭代 |
| ② | `audit@review: help 契约设计 v1.4 评审 PASS` | [2/6] 评审 | ✅ 匹配 |
| — | `docs@design: …二次补记 — HG-SEC-182 订正 + HG-SEC-184 正则折入` | [1/6] 设计补记 | 额外设计迭代 |
| ③ | `feat@cli: ?show-md 纳入 doc URL 契约守卫 …` | [3/6] dev 实施 | ✅ 匹配 |
| ④ | `docs@verify: …ops 独立核查 PASS(44 项…)` | [4/6] ops 核查 | ✅ 匹配 |

**链构成判定**: 4 锚点笔全部在场且 subject 相符；另有 2 笔 `docs@design` 迭代（补记 + 二次补记）属设计阶段正常演进，其中二次补记（`5b95469`）在评审（`d9a0e29`）之后、dev（`0b387ca`）之前折入 HG-SEC-182/184，构成「评审 CONDITIONAL → 设计补记闭环 → 实施」的合规序列。**非链构成异常**。

### 1.2 ops harness 全量复跑（含 slow）

```
/usr/bin/python3 cache/closed-loop/HTML-GEN-CL014-verify.py
```

实测: **RESULT: PASS —— `PASS=44  FAIL=0  N-A=0  WARN=0`**。关键三段与 ops 留档 `cl014-harness-run-ops-final.log` 对读一致:

- fixture: `FX-1..FX-5` 全 PASS（见 1.4）；
- T60 全量 pytest: `334 passed, 1 warning in 132.01s`；
- T70/T71/T72 变异: `rc=1` + 指名 `show-md` + live 树零污染；
- T53 生成物保真: `BYTE-IDENTICAL(去时间戳)`；
- T80 范围: 白名单外 `无`（共 9 文件）；T82 推送面: 领先 github/main 3 笔，gitee(origin/main)=`7821427`（本批不推 gitee）。

与 ops 留档零差异（同一 harness、同一口径、同一 `FAIL=0`）。

### 1.3 判据非恒真反证（修前红，独立验证）

ops 留档 `cl014-harness-run-pre-impl-r2.log` = `30 PASS / 9 FAIL / 3 N-A`（`--skip-slow` 跑，3 项 N-A = T53/T60/T70）。任务书引用的 `cl014-harness-run-pre-impl.log` 同为 `9 FAIL / 3 N-A`（27 PASS，较 r2 少 3 PASS 系 harness 早版，口径一致）。

我**不采信该留档**，改用 `git show 5b95469:<file>`（修前 = `0b387ca` 的父提交）独立复算三面:

| 面 | 命令 | 修前实测 | 修后实测 | 红→绿 |
|:--|:--|:--|:--|:--|
| 契约面 | `git show 5b95469:html-gen.py \| grep -c "'?show-md'"` | **0**（url_state 仅 `?sidebar/?toolbar/?width` 3 项） | 1（4 项） | ✅ |
| 测试面 | `git show 5b95469:tests/test_help_contract.py \| grep 'params.get'` | 正则 `[a-z]+`（**漏连字符键**） | `[a-z][a-z0-9-]*` | ✅ |
| 文档面 | `git show 5b95469:demos/doc-guide.md \| grep -c 'show-md'` | **0** | 1 | ✅ |
| 模板面（未变） | `git show 5b95469:layout-doc.html \| <钉定正则>` | **4 键**（含 show-md） | 4 键 | 不变 |

**结论**: 修前「模板消费 4 键 ≠ 契约 3 键」「契约缺 ?show-md」「文档面 0 行」三面齐红；修后全绿。判据**非恒真**成立（同一 harness 同一口径 9 FAIL → 0 FAIL）。核心事实「修前红」由我独立复算确认，非转述。

### 1.4 harness fixture 自检（A4 前半）

harness `run_fixtures()` 在 `load_gen()` / 判实现**之前**运行，任一 fixture 不过即 `sys.exit(1)` + `RESULT: FAIL (fixture)`。实测 5 条 fixture 全 PASS:

| fixture | 性质 | 断言 |
|:--|:--|:--|
| FX-1 | 阳性 | 钉定正则提取 show-md，契约含 show-md ⇒ PASS |
| FX-2 | 阴性+指名 | 契约缺 show-md ⇒ FAIL 且致命项指名 `show-md` |
| FX-3 | 阴性-老正则 | 老 `[a-z]+` 提不到连字符键（证明放宽必要） |
| FX-4 | 阴性-中间态 | `[a-z-]+` 对含数字键 `tab2` 漏捕（HG-SEC-184 必要性） |
| FX-5 | 阳性-钉定 | `[a-z][a-z0-9-]*` 覆盖连字符 + 数字键 |

**充分性判定（防「与实现共享同一误解」）**: 任务书 §2.3 写「3 条 fixture」，实测 harness 已扩为 **5 条**（`FX-4/FX-5` 系 HG-SEC-184 折入后新增，属超集，非缺陷）。充分性成立：① FX-1 用 harness **自持**钉定正则（非实现测试正则）对合成文本 `params.get('show-md')` 作阳性对照——若 harness 复用实现的老 `[a-z]+`（即共享同一误解），FX-1 会因提取空集而立即 FAIL 停机；② FX-3 显式编码「老正则不足」这一教训；③ harness 判据另有两处**独立硬锚点**（T10 硬编码 4 键期望、T15/F8 语义对模板 L81-83/273 + basename），与正则无关，双重免疫「正则与实现同误解」。故 fixture 自检**足以**防共享误解。

### 1.5 全量 pytest 独立复跑 + tests 改动面

```
/usr/bin/python3 -m pytest tests/ -q -n0
```

实测（我独立直跑，非经 harness subprocess）: **`334 passed, 1 warning in 132.08s`**（0 failed，≥ 基线 334）。`ls tests/test_*.py | wc -l` = **31**。`git diff --name-only 4e58407..HEAD -- tests/` = **仅 `tests/test_help_contract.py`**（其余 tests/ 文件 0 改动）。

### 1.6 独立变异（判据强度，my /tmp 路径，非 harness 的 /tmp/cl014-mut）

在 `/tmp/cl014-audit-mut` 副本（rsync，排除 .git/cache/prompts/src）删契约 `?show-md` 条目后跑 `pytest tests/test_help_contract.py -n0`:

```
[变异] ?show-md 契约条目: 删前 1 处 → 删后 0 处
[变异后 pytest] rc=1
FAILED tests/test_help_contract.py::TestHelpContract::test_17_doc_url_state_matches_template
AssertionError: Items in the first set but not the second:
  'show-md' : doc.url_state: 消费键 ['show-md','sidebar','toolbar','width'] != 契约键 ['sidebar','toolbar','width']
  — 来源 layout-doc.html; 修复: 在 TEMPLATE_CONTRACT["doc"]["data"]["url_state"] 补该键 (键名口径与 table 一致, 带 ? 前缀)
1 failed, 21 passed in 0.28s
[live 污染] git status --porcelain 行数: 0
```

**结论**: 守卫转红并**指名 `show-md` + 来源文件 + 修复动作**，live 工作树零污染。判据强度成立（非恒真）。

### 1.7 机制断言逐条复算（勿采信设计 §9 / ops 报告）

```
grep -n "params.get(" layout-doc.html   → L263(sidebar) / L264(toolbar) / L267(width) / L273(show-md) = 4 处
提取键集（三种正则对照）:
  钉定 [a-z][a-z0-9-]* → ['show-md','sidebar','toolbar','width']  (4)
  [a-z-]+              → ['show-md','sidebar','toolbar','width']  (4)
  老 [a-z]+            → ['sidebar','toolbar','width']            (3, 漏 show-md)
契约 url_state 键集 → ['?sidebar','?toolbar','?width','?show-md']；顶层 is data.url_state = True
html-gen help doc URL 状态段 → 4 行，末行:
  ?show-md: meta 区源文件名显示开关 show-md=1 (默认隐藏, 仅显示 basename 脱敏文件名)
```

**判定要点逐条**:

- ① **契约键集 == 模板消费集（4 == 4）**: 模板钉定正则提取 4 项 = 契约去 `?` 前缀 4 项，等式成立（`test_17` 即此等式）。
- ② **help 渲染行文本与契约说明逐字一致**: help 行 `?show-md: meta 区源文件名显示开关 show-md=1 (默认隐藏, 仅显示 basename 脱敏文件名)` 与契约 `desc` 逐字一致（`render_help` 由契约驱动，`html-gen` = `/Users/jadenli/.local/bin/html-gen` → `exec python3 …/html-gen.py`，跑的是**库内**真源，非 stale 副本）。
- ③ **说明语义与实现逐条对应**: 「默认隐藏」↔ `layout-doc.html:82` `.meta-path { display: none; }`；「仅 basename 脱敏」↔ `html-gen.py` `os.path.basename(str(md))` 注入（`?show-md` 判定 `=== '1'`，L273）；「show-md=1 才显示」↔ L83 `body.show-md .meta-path { display: inline; }`。无冲突。
- ④ **其余三维度未被削弱**（我自跑提取正则，非读测试文件）: `table {top_level:7, column_types:6, columns:22, tabs:6, options:13, feedback:5, actions:7, videos:5}` · `slide {url_state:0, behaviors:8}`（behaviors 8 项 = 分页/导航/全屏/进度点/记忆/侧栏H3/侧栏搜索/性能警告）· `knowledge {item:7, groups:3, data_source:3}` · `doc cli: 9` —— 与设计 §3 逐值一致，零扰动。

### 1.8 范围合规 + 文档面 + 生成物保真

`git diff --name-status 4e58407..HEAD` = **9 文件**（含 1 处 `R061` rename），全部落在授权白名单:

```
M .review-level.yaml · M demos/doc-guide.html · M demos/doc-guide.md
A documents/review/help-contract-cl014-ops-verify-v1.0-20260917.md
A documents/review/html-gen-help-contract-design-review-v1.4-20260917.md
R061 documents/solutions/…v1.3…md → …v1.4…md（git mv）
M html-gen.py · M review-log.md · M tests/test_help_contract.py
```

文档面: `demos/doc-guide.md:176` 表含 `show-md` 行（语义「默认隐藏；只显示 basename，不显示完整路径」）· 生成物内容单元格 `<code>show-md</code>` = 1（L876；另 L878 描述单元格 `<code>show-md=1</code>`）。**弱代理提示**: 全文子串 7 处 = 内容单元格 1 + 描述单元格 1 + 模板内联 JS/CSS 5（L314/L316/L991/L992×2）——**勿用全文 grep 当判据**（见 §⑤ HG-SEC-186）。

生成物保真: `python html-gen.py doc -i demos/doc-guide.md -o /tmp/cl014-audit-regen.html` 后与库内 `demos/doc-guide.html` 比对——归一化时间戳 **BYTE-IDENTICAL**，且**原始 diff 0 行**（doc 的 meta 时间戳取自 md stat，非生成时刻 ⇒ 确定性，无时间戳漂移）。确认为**库内产物同源**。

---

## ② D 组判定表（dev 申报偏差逐条独立判定）

| # | dev 申报内容 | 判定 | 依据（review 独立实测） |
|:--|:--|:--|:--|
| D1 | html-gen.py 落点 +3 行（1 契约条目 + 2 注释）而非字面 +1 | **成立（接受）** | 注释在源码层（`html-gen.py:811-812`，`# CL014: …` + `# 说明文本只用等号/裸词形态…`），**不入契约数据**；desc 无 ASCII「词元:」片段（T14 PASS）；help 行文本逐字未变；零行为影响。属纪律留痕（防后人回改成 `[a-z]+` 口径），保留 |
| D2 | A5 用 `cp -a <绝对路径>` 替代仓内 `cp -R .` | **成立** | 语义等价；我独立变异用 rsync 同结论（转红 + 指名 + live 零污染） |
| D3 | A5 跑毕 `rm -rf /tmp/cl014-mut` | **成立** | 不影响可复跑性（harness/我的副本均自建）；证据已回执留档 |
| D4 | §10 V5 行数口径 = 单侧计数（CSS 增侧 / corner 删侧 / title 合计） | **成立** | dev §③ 归类 +14/-12 四类（本批 +6/-1 · CSS +5/-2 · corner +2/-8 · title +1/-1），基线重算 = 增 8 / 删 11，与设计 §9 F12「CSS 5/corner 8/title 2」逐值对齐。属**表述口径**非数值错误；无第五类 ⇒ 未停手成立 |
| D5 | 「无按实测收窄项」 | **成立** | R1 语义三点（默认隐藏 / 显式 `show-md=1` 才显示 / 仅 basename）由 `layout-doc.html:82/83/273` + `html-gen.py` basename 逐条支撑（T15 四项 PASS），按字面实现即可 |

**关键独立判点（任务 §3 括号内三问）**:

1. **正则放宽是否必要** — **必要**。老 `[a-z]+` 提取恒 3 键、漏 `show-md`（连字符使 `show` 后要求 `'` 而实得 `-`）；放宽是补守卫的唯一路径（1.7 实测三种正则对照证之）。
2. **是否应更通用** — **钉定 `[a-z][a-z0-9-]*` 恰当**。对当前 4 键（全 lowercase + 连字符）与未来含数字键（`?tab2`）均覆盖，且不误捕非 URL 键（`layout-doc.html` 内 `params.get('…')` 仅 4 处、全为 URL 键；table 用 `_params`、knowledge 用 `urlParams`，文件隔离无误伤）。再放宽（如 `\w+`）会引入 underscore 等非真实 URL 键的过匹配，无必要。HG-SEC-184 折入（`[a-z-]+` → `[a-z][a-z0-9-]*`）是正确收窄。
3. **md 行措辞是否与契约语义冲突** — **不冲突**。`demos/doc-guide.md:176`「默认隐藏；只显示 basename，不显示完整路径」与契约「默认隐藏, 仅显示 basename 脱敏文件名」语义一致，且与模板/生成器实测逐条对应（1.7 判点③）。

---

## ③ HG-SEC-180 / O1 闭合判定（四项判据逐条）

| 判据 | 实测 | 结论 |
|:--|:--|:--|
| ① `?show-md` 被契约声明 | `TEMPLATE_CONTRACT['doc']['url_state']` = `['?sidebar','?toolbar','?width','?show-md']`（4 项，带 `?` 前缀，顶层与 data 同一 list 对象） | ✅ |
| ② 守卫等式（模板消费 == 契约）对它成立 | 模板钉定正则提取 4 键 == 契约去前缀 4 键；`test_17` 全绿（22 passed） | ✅ |
| ③ 变异时该键导致守卫转红 | 删 `?show-md` → `test_17` 红并指名 `show-md` + 来源 + 修复动作（1.6） | ✅ |
| ④ help 对用户可见 | `html-gen help doc` URL 状态段 4 行，末行 `?show-md: …` 与契约逐字一致 | ✅ |

四项齐 ⇒ **HG-SEC-180 / O1 就地闭合**。

---

## ④ 范围合规与范围外声明

- **范围合规**: 9 文件全落白名单，白名单外 0 文件（1.8）；`git status --short` 空。
- **`cache/**` 全 gitignored**: 本轮产生的 `/tmp/cl014-audit-*.py/.html`、`/tmp/cl014_audit_mutate.py`、`/tmp/cl014-audit-mut/`、harness 日志均不入提交。
- **他线未跟踪文件**: 无（`git ls-files --others --exclude-standard` 空，经 harness T81 确认）。
- **本批外既有红项（不属本批，勿在本批提交处置）**:
  - `HG-SEC-181`（O5 `table-demo-prompt.md` 键名骨架残留）→ 另批「守卫面补全批」；
  - `HG-SEC-183`（table `?tab/?q/?split` 无模板→契约提取守卫）→ 另批「守卫面补全批」；
  - `HG-SEC-185`（doc 无 `behaviors` 段，标题点击复制第三行为面）→ 另批「doc behaviors 段补齐」；
  - `O-CL014-1`（生成物刷新：全量 15/18 `demos/*.html` 带硬编码 imjaden corner）→ 另批「生成物刷新批」；
  - `HG-SEC-182`（设计 F13 计数归因）→ 已由 `5b95469` 二次补记订正，本批复核确认已闭合。
- **并行线核验**: 审计起始与结束时 `git rev-parse --short github/main` 均为 `d9a0e29`，无并行线推进，可安全推送。

---

## ⑤ 新增观察项（编号 · 归属批 · 理由）

| 编号 | 严重度 | 发现 | 归属批 · 理由 |
|:--|:--|:--|:--|
| HG-SEC-186 | 🟢 record | ops 核查报告 §4 与 harness `T51` 把「全文 show-md 子串计数 7 处」误标为「模板 JS 内联 7 处」——实际全文 7 = 内容单元格 1（L876）+ 描述单元格 1（L878，`<code>show-md=1</code>`）+ 模板内联 JS/CSS 5（L314 注释 / L316 CSS / L991 注释 / L992 ×2）。任务书 §2.8 的「实测 5 处」方为内联准确值。**判据（`<code>show-md</code>` 精确匹配 ≥1 + T53 逐字节保真）本身正确**，零行为影响 | **归属批** = 未来 harness 修订（可选，低优先级；`cache/` gitignored ops 工具面，不入库）；**理由** = 弱代理标注词义混淆，属精度瑕疵，非本批代码缺陷，不阻断 |

**任务书自身口径漂移（非本批缺陷，仅记录）**: ① 任务书 §2.3「3 条 fixture」→ 实测 5 条（HG-SEC-184 折入后扩 FX-4/FX-5，超集）；② 任务书 §5「已用到 HG-SEC-181」→ 实际 max = HG-SEC-185（[2/6] 评审已分配 182–185）。两者均为任务书在 [2/6] 前撰写所致，不影响判据执行。

---

## ⑥ 结论 + 分数

- **结论: PASS**。8 项逐条复跑全独立通过（不采信 ops/dev 自报）；D1–D5 全成立；HG-SEC-180/O1 四项判据齐备就地闭合；白名单外 0 改动；判据非恒真已反证（修前 9 FAIL 三面红 → 修后 0）；断言强度已独立变异验证（转红 + 指名 `show-md` + 来源 + 修复动作）；机制断言（契约 4 == 模板 4、help 逐字、他维度零扰动）逐条复算成立；生成物保真 BYTE-IDENTICAL。
- **Score: 95 / 100**（L2 百分制；参考 CL013 实现审计 94/100、CL012 93/100）。
- **扣分（唯一 🟢，非阻断）**: HG-SEC-186 —— ops harness `T51` / ops 报告 §4 的「内联 7 处」标注把「全文 7」误写为「内联 7」（实为内联 5 / 全文 7），弱代理词义混淆；判据正确，零行为影响。

**待处置编号（均另有归属批，非本批新增阻断）**:

| # | 事项 | 归属批 |
|:--|:--|:--|
| HG-SEC-181（O5） | `table-demo-prompt.md` 键名骨架残留 | 守卫面补全批 |
| HG-SEC-183 | table `?tab/?q/?split` 无提取守卫 | 守卫面补全批 |
| HG-SEC-185 | doc 无 `behaviors` 段（标题复制第三行为面） | doc behaviors 段补齐 |
| O-CL014-1 | 生成物刷新（15/18 带硬编码 corner） | 生成物刷新批 |
| HG-SEC-186 | harness T51 弱代理标注词义混淆 | 未来 harness 修订（可选） |
| HG-SEC-182 | 设计 F13 计数归因 | 已闭合（`5b95469`） |
