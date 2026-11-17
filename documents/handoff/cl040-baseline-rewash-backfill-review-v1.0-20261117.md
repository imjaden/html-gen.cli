# 评审报告 — CL040（基线二次洗白 + 回填工具健壮性）v1.0

- 日期：2026-11-17 · 评审范围：`git log --oneline github/main..HEAD`（`/Users/jadenli/CodeSpace/html-gen.cli`）
- 受审 4 笔：`73efd66` / `4b0a98f` / `97cf20c` / `535d0a4`（闭环 HTML-GEN-CL040）
- **范围外只报不审**：`a927a7b`（`docs@design: CL037 slimdown…`，1 文件 334 行文档，属他线设计稿，未纳入本轮判据、不随本批推送）
- 设计真值：`documents/solutions/cl040-baseline-rewash-backfill-robustness-design-v1.0-20261113.md`
- 上轮待修项：HG-SEC-249/250/252/253/254/256/257/258（`documents/handoff/drama-backfill-cl038-cl039-review-v1.0-20261112.md`）

---

## 0. 结论

**CONDITIONAL · 88 / 100**

- 无 🔴 阻断项。安全级两条（249 二次洗白 / 250 门禁零覆盖）**均已闭合**，且由我独立复跑 + 5 条变异（M1–M5）逐条证伪，不是只看提交信息。
- 扣分集中在 `256`（AGENTS.md 计数未落，且仓内无「计数待批」回执）与 `258`（`--force` help 文案与「第二次 force 回 true」的行为字面冲突）。
- 新增 1 条 🟡：`dangling_legacy` 的 join 参照系是**旧行**而非产物行 ⇒ 「改名当场暴露」这条设计承诺实际晚一轮生效（不丢数据，但报不当天）。
- 放行前建议补两件小事：`--force` help 文案措辞、AGENTS.md 两行（受保护文件，需审批窗口落地）。

---

## 1. 逐条闭合表

| 条目 | 判定 | 证据 |
|:--|:--|:--|
| **HG-SEC-249** 二次洗白 | **闭合** | 四路径全部独立复跑（scratch 根 `cl040v3`，真仓零写入）：P2 普通 `--update` rc=1 且基线 sha256 前后相同；P4 `--force` → `corner=False verified=False`；P5 普通 `--update` 再拒 rc=1、字节不变、`verified` 仍 False；P7 第二次 `--force` → `verified=True`（终止性成立）。代码：`scripts/baseline.py:346-371`（`verify_ok`/`drops`/`old` 三判据 + `verified = bool(verify_ok and not drops)`），留痕：`:435-437` |
| **HG-SEC-250** 门禁零覆盖 | **闭合** | `test_baseline_gate.py:178` `test_10` 存在且真杀变异：M1（删 `_param_regressions` 调用）红、M2（删 `verified=false` 拒绝分支）红、M3（`verified` 写回 `not force`）红且**失败点正是第 8 步**（`tests/test_baseline_gate.py:257` `AssertionError: False is not true : verify 绿且无参数回归 ⇒ verified 必须回到 True`）。判别前提写在用例里（第 3 步断言 `--verify` rc=0，`:213-220`） |
| **HG-SEC-252** legacy 悬空 | **闭合** | 三表实测 `dangling=[]`（daming 22 行/idiom 22 键、zhuyuanzhang 17/17、yongzheng 26 行/idiom 3 键），`走为上` 在行名中、`走为上计` 已无；`legacy` 仍不进产物：`baseline.py --check` → `基线一致: 50/50`（`data/_render-baseline.json` 本批零改动，`verified=true`） |
| **HG-SEC-253** 静默丢数据 | **闭合**（含 2 条 🟢） | 前置校验覆盖**两个方向**：`scripts/backfill-table-json.py:119-140`（`len(old_rows) != len(data)` 对称判据）；我另造反向夹具（源 2 行 → 产物 5 行）实测 **rc=2 且未写盘**。行标识唯一校验 `:123-130`；`--drop-orphans` 为显式放行且清 `legacy`（`:132-134`+`:145`）。孤儿 loop 的 `zip`（`:148`）在行数校验之后，唯一绕过口即显式 `--drop-orphans` ⇒ **无第三静默截断路径**。残余见 🟡 HG-SEC-260 |
| **HG-SEC-254** 差异标签 | **闭合** | `field_diff` 三类各带真值且方向正确（`:44-62`）；实测输出 `+note='n1' -idiom='值1' ~strategy='旧名'→'新名'`（probe）；`SKIP_KEYS` 死代码已删（`grep SKIP_KEYS` 仅剩 docstring 说明行 `:47`）；`'<dropped>'`/`'<none>'` 仅存于注释与测试断言 |
| **HG-SEC-256** 文档算术 | **部分闭合** | `documents/testing.md`：`42 个可 verify 产物`（`:57`，实测 `len(build_jobs)=42`）、`= **50 项**`（`:57`，实测 `len(SUBSET)=50`）、`48 文件`（`:43`，实测 `ls tests/test_*.py | wc -l = 48`）、`103 subtests`（`:43`，实测 `pytest -n 0` 原文 `478 passed, 103 subtests passed`）、`10 例`（`:106`，实测 `--co` = 10）。守卫仅绑 2 个数字（`test_baseline_gate.py:172/174`）。**缺口**：`AGENTS.md:6`（期望 473）/`:44`（473 tests · 47 文件）未改，而 `README.md:137`、`README.zh.md:135` 都写「权威见 AGENTS.md」⇒ 指向错数字；仓内亦无「计数待批」回执（`grep -rln 计数待批 documents/` 只命中设计稿 §8）。设计 §8 允许「待批文本」形式延后落地，故不阻断，但**不得报「计数已同步」** |
| **HG-SEC-257** tmp 判据 | **闭合** | 新正则 `tests/test_selenium_infra.py:94`；13 形态探针 13/13 符合预期：`/tmp`、`/private/tmp`、`/var/tmp`、`/private/var/tmp`、`/var/folders/`、无尾斜杠引号形态、`/private/var/folders`，且**不误伤** `/tmpdir/x`、`mytmpdir/`、`tmp/`、`relative/tmp/file`、`/var/fold`。注入探针实测：新形态 2 命中、`/tmpdir/legit` 0 命中。`noqa: tmp-path-guard` 仓内共 4 处（2 处为 env 字符串夹具 `:48/:50`，2 处为守卫自身 `:94/:97`）—— 属既有自证豁免机制，**未新增逃逸面** |
| **HG-SEC-258** 文案/权限/索引 | **部分闭合** | `scripts/baseline.py`、`scripts/backfill-table-json.py` 均 `-rwxr-xr-x`（755）✓；`cli-reference.md` 已补两行索引 ✓；`--update`/`--force` 文案已改（`:453-458`）但 `--force` 的「不会写 verified=true」与实测冲突（见 🟢 HG-SEC-263）；`--dry-run` 已实装（`:88-95`，`--apply` 互斥 rc=2）✓ |

---

## 2. 新发现（编号延续，上轮止于 258）

### 🟡 HG-SEC-260 · `dangling_legacy` 的参照系是旧行，改名「当场」不报

- 位置：`scripts/backfill-table-json.py:71-77`（`keys = {row_key(r, i) for i, r in enumerate(raw.get('data', []))}`）+ 调用点 `:162`
- 事实：`:162` 在 `raw['data'] = data`（`:168`）之前执行，`raw['data']` 仍是旧行 ⇒ legacy 键永远能 join 到旧行，「本次运行发生的改名」不报。文档/注释写「改名即断链的**当场**暴露面」（`:69`），实际晚一轮。
- 实测（scratch `cl040probe`）：旧行 `strategy=旧名` + 产物行 `strategy=新名`，一次 `--apply` → rc=0，无任何 ⚠️，写盘后 `legacy={'idiom':{'旧名':'值1'}}` 悬空；**第二次** dry-run 才报 `⚠️ legacy 悬空键 1 条 …['idiom.旧名']`。数据未丢（值在 legacy 里），故不阻断。
- 影响：改名当批提交会带进一条悬空 legacy，只有下次跑该工具才暴露；`test_04` 只覆盖「文件里已存在的旧名」，覆盖不到「本次改名」。
- 修法：`def dangling_legacy(raw, rows)`，用**产物行**做 join（调用改 `dangling_legacy(raw, data)`），`test_04` 补一条「本次改名即报」的夹具。

### 🟢 HG-SEC-261 · `--check --json` 不暴露 `verified=false`（越权状态对机器不可见）

- 位置：`scripts/baseline.py:419-421`（`json.dumps({'ok', 'total', 'mismatches'})`）
- 事实：⚠️ 只走 stderr 文本；`--check --json` 实测键为 `['mismatches','ok','total']`，无 `verified`。cron/CI 读 JSON 时 `ok=true` 与「钉子已失效的基线」无法区分。
- 修法：JSON 面加 `"verified": base.get('verified')`（或在 `ok` 不变的前提下加 `"authority_lost": base.get('verified') is False`），并补一条断言。

### 🟢 HG-SEC-262 · 输入路径异常抛裸 traceback（与「rc=1 = 受控 IO 失败」自述不符）

- 位置：`scripts/backfill-table-json.py:99-103`
- 实测：`--pair nope.html=nope.json` → rc=1 且 stderr 含 `Traceback`；`--pair a.html`（缺 `=`）→ 同样裸 traceback。
- 修法：`if '=' not in spec:` → 打用法 + rc=2；`read_text` 包 `except OSError` → 打路径 + rc=1。

### 🟢 HG-SEC-263 · `--force` help「不会写 verified=true」与行为字面冲突

- 位置：`scripts/baseline.py:457-458` vs `tests/test_baseline_gate.py:253-257`
- 事实：test_10 第 8 步断言第二次 `--force` **必须**写回 `verified=True`（我已实测 P7）；help 的措辞容易被读成「force 永远留 false」。
- 修法：改为「跳过上述拒绝（仍跑 verify；force 本身不置 true，恢复常态须 verify 绿且无参数回归）」。

### 🟡 HG-SEC-264 · AGENTS.md 计数未落且无「计数待批」回执

- 位置：`AGENTS.md:6`（期望 473）、`AGENTS.md:44`（473 tests · 47 文件），实测 478 / 48 文件 / 103 subtests
- 影响：`README.md:137`、`README.zh.md:135`、`documents/testing.md:41` 均声明「权威见 AGENTS.md」⇒ 三处指针指向错数字；下一轮按 AGENTS 跑门禁会误判 5 例差异。
- 说明：AGENTS.md 属受保护文件，需审批窗口落地，设计 §8 已给两条精确文本：
  - `:6` `（期望 473 passed）` → `（期望 478 passed）`
  - `:44` `- 473 tests（47 文件，含 103 subtests）` → `- 478 tests（48 文件，含 103 subtests）`
- 修法：审批窗口两行 patch + `wc -c AGENTS.md` 复核 ≤ 4,000B；同时在 handoff 回执写明「计数待批」直至落地。

### 🟢 HG-SEC-265 · `testing.md` 仍有三个数字无守卫

- 事实：`test_08` 只绑了「42 件」与「50 项」（`tests/test_baseline_gate.py:172/174`）；「48 文件」「103 subtests」「10 例」（`documents/testing.md:43/110`）无断言，仍可静默漂移（256 的复发面）。
- 修法：文件数可低成本守：`self.assertIn(f'{len(list((ROOT/"tests").glob("test_*.py")))} 文件', doc)`；subtests 计数不适合进单测（需全量跑），建议只在 `documents/testing.md` 标注「以 `pytest -n 0` 汇总行为准」。

### 🟢 HG-SEC-266 · 同一产物 `changed` + `param-lost` 各记一条，漂移计数虚高（既有行为）

- 位置：`scripts/baseline.py:413-418`
- 实测：漏参重渲后 `--check` 报 `漂移 2/50`，实际只有 1 个产物变了（`demos/countries-table.html` 同时命中 `changed` 与 `param-lost:corner`）。
- 影响：仅计数可读性（rc 正确），但会让人误判影响面。CL040 之前即如此，非本批引入。
- 修法：同一 `rel` 命中多条时按 `rel` 聚合打印（`changed+param-lost:corner`），`total` 口径不变。

---

## 3. 变异自证（M1–M5，改完即 `git checkout --` 还原）

| 变异 | 目标用例 | 结果 |
|:--|:--|:--|
| M1 删 `_param_regressions` 调用（`baseline.py:348` → `drops = []`） | `test_10` | **KILLED** ✅ `1 failed` |
| M2 删 `verified=false` 拒绝分支（`:362-366`） | `test_10` | **KILLED** ✅ `1 failed` |
| M3 `verified` 写回 `not force`（`:371`） | `test_10` | **KILLED** ✅ 失败点 `tests/test_baseline_gate.py:257`（第 8 步终止性） |
| M4 删行数校验（`backfill:120-122`） | `test_backfill_tool::test_01` | **KILLED** ✅ `1 failed` |
| M5 `added`/`dropped` 互换（`backfill:52-53`） | `test_backfill_tool::test_03` | **KILLED** ✅ `1 failed` |

每次变异后 `git status --short` 均为空、`git diff --stat` 为空 ⇒ 工作树已完全还原（脚本：`~/.hermes/profiles/ops/cache/scratch/cl040_mutate.py`）。

---

## 4. 复跑记录（真实末行）

| 命令 | 末行 / 结果 |
|:--|:--|
| `python3 -m pytest tests/ -q -n 4` | `478 passed, 5 warnings in 64.71s (0:01:04)` |
| `python3 -m pytest tests/ -q -n 0`（计数用） | `478 passed, 103 subtests passed in 251.37s (0:04:11)` |
| `python3 scripts/baseline.py --check` | `基线一致: 50/50（/Users/jadenli/CodeSpace/html-gen.cli）`（rc=0） |
| `python3 scripts/baseline.py --verify` | `产物与当前模板一致`（rc=0） |
| `python3 -m pytest tests/test_baseline_gate.py tests/test_backfill_tool.py -q -n 0` | `14 passed, 1 warning in 1.31s` |
| `python3 scripts/backfill-table-json.py --pair demos/drama/daming-strategy-table.html=data/_drama-table-daming-strategy.json` | `字段差异 0 行` / `（dry-run，未写盘）`（rc=0） |
| `git log --oneline github/main..HEAD` | 5 行：`a927a7b`(CL037，范围外) + `535d0a4` / `97cf20c` / `4b0a98f` / `73efd66` |
| `git status --short` | 空 |

补充实测（均为 scratch 根，真仓零写入）：

- 四路径探针 `cl040v3`：`P0 rc=0 corner True verified True` → `P1 漏参后 --verify rc=0` → `P2 普通 --update rc=1` + 基线字节一致 YES → `P4 --force rc=0 corner False verified False` → `P5 普通 --update rc=1` + 字节一致 YES → `P6 --check rc=0` + stderr `⚠️ 基线为越权建立（verified=false）…` → `P7 第二次 --force rc=0 verified True`。
- 反向行数夹具：`反方向（源2→产物5） rc=2 未写盘=True`。

---

## 5. 约定遵守核查

| 项 | 结论 |
|:--|:--|
| path-scoped 提交 | ✅ 四笔文件集互不夹带（`73efd66` = baseline.py+test_baseline_gate；`4b0a98f` = backfill+数据2+新测；`97cf20c` = test_selenium_infra；`535d0a4` = 5 份文档），未见 `git add -A` 吞工作树痕迹 |
| subject 全英文 | ✅ `fix@baseline` / `feat@backfill` / `test@infra` / `docs@testing` |
| 零第三方依赖 | ✅ 两脚本 import 仅 `argparse/hashlib/html/json/re/shutil/subprocess/sys/tempfile/datetime/pathlib` |
| 无跨仓改动 | ✅ 13 个路径全在本仓 |
| 产物/基线字节 | ✅ `data/_render-baseline.json` 未改（`--check` 50/50、`--verify` 全 current），与本批「不动产物」的口径一致 |
| 未 push | ✅ 本地领先 `github/main` 5 笔（含范围外 CL037） |

---

## 6. 建议处置顺序

1. **可放行**：本批 4 笔在评审后推送（CL037 `a927a7b` 不在本轮判据内，建议单独走它自己的评审/推送）。
2. 随下一批收口（🟡）：HG-SEC-260（dangling 参照系 + 补夹具）、HG-SEC-264（AGENTS.md 两行，审批窗口）。
3. 顺手修（🟢）：HG-SEC-261/262/263/265/266，均 < 10 行改动，可并成一笔 `fix@tooling`。
