# slimdown 案例（`b0f4b4f`）闭环编号登记 + 自包含复核 + CL036 密度一致性核查（方案 v1.0 · 待评审）

- 日期：2026-11-17 · 编号：`HTML-GEN-CL037` · 分类：治理（追溯断链）· 优先级：P2
- 需求条目：`cache/draft/TODO-20261109.md:24`（状态 READY）
- 来源：`review-log.md:2620` — HG-SEC-231「`b0f4b4f` 无闭环编号（近 40 笔中 36 笔带 CL），5,823 行 17 文件的新案例在 `hm loop artifacts`/draft 无归属」
- 状态：**方案定稿，源码 / 数据 / 测试零改动**（本文档是本批唯一产物；不 verify、不标完成）
- 约束：只改本仓；不 push；不改写 `b0f4b4f`（**已在 `origin/main`**，任何 rebase/amend 都是改写已推历史）；不动工作树里与本笔无关的残留

---

## 0. 结论摘要

| # | 待答问题 | 结论 | 关键证据 |
|:--|:--|:--|:--|
| 1 | `b0f4b4f` 本体范围 / 是否自包含 | **自包含达标**：6 个 import 全标准库、`subprocess` 列表式无 shell、路径全部相对 `ROOT`、无外部 CSS/字体/JS；唯一外链是 favicon（19/19 demos 既有约定）；**重建 3/3 逐字节一致** | §1.2 · AC-1..AC-5 |
| 2 | 编号登记到何处 | `review-log.md` 新增一段（tracked 主台账）+ 本设计文档（持久落点）+ `cache/draft/TODO-20261109.md:24` 补方案指针（gitignored）；提交信息不改写；hm loop 侧不代改 | §2 |
| 3 | 与 CL036 密度变量是否一致 | `exercises.html` **6/6 命中**（三档变量 + 0.88/0.86/0.8 联动）；`plan.html` / `archive.html` 为**纸张面、无 `.data-table` ⇒ N/A**（需在评审报告写明理由，否则易被误判 FAIL） | §3 |
| 4 | 已知缺陷分级 | **0 P0 / 1 P1（产物零回归守卫）/ 3 P2 / 4 记录项**；登记动作本身不受缺陷阻塞 | §4 |

**一句话**：编号缺的是「归属链」而不是「代码质量」；本批交付的是可复核的登记方案与判据，代码面只建议补 1 例重建守卫（需计数审批）。

---

## 1. 审查对象与实测事实（本轮只读探针）

复跑环境：`/Users/jadenli/CodeSpace/html-gen.cli`，`git status` 空，`origin/main..HEAD` = 4 笔（与 CL037 无关）。

### 1.1 提交范围与现状漂移

- `b0f4b4f` 2026-11-12 13:52，author = committer = `Jaden.Li <jaden.li@jaden.tech>`，17 文件 +5,823/−4。
- 归属：**他人笔**（非本调度会话产出），且 `git merge-base --is-ancestor b0f4b4f origin/main` = 真 ⇒ 已推送，**不可改写**。
- `b0f4b4f..HEAD` 共 29 笔，其中触碰 slimdown 的只有 2 笔：

  | commit | 主题 | 影响 |
  |:--|:--|:--|
  | `1520089` | `fix@data: use ascii tab keys for slimdown theme tabs` | `_slimdown-exercises.json` 的 `tabs[].key` 改 ASCII + `value`/`contains` |
  | `87f2369` | `chore@baseline: … (HTML-GEN-CL032)` | 按当前模板全量重刷，含 `demos/slimdown/exercises.html` |

- 实测差异：`git diff --numstat b0f4b4f..HEAD -- demos/slimdown` ⇒ 仅 `exercises.html` +56/−17（现 2,353 行）；
  **`plan.html`（812 行）/ `archive.html`（352 行）与 `b0f4b4f` 逐字节相同**。
- ⇒ **审查口径**：审查对象是「存量产物 + 提交意图」，不是 `b0f4b4f` 的 tree。按 tree 取值比对会与工作树不符（记录项 F6），评审时须写明。

### 1.2 自包含核对（结论：PASS）

| 维度 | 判据 | 实测 | 结论 |
|:--|:--|:--|:--|
| 标准库 | `scripts/build-slimdown.py` 全部 import 在 stdlib | `argparse / json / re / subprocess / sys / pathlib`（`:18-23`） | PASS |
| 无 shell | 无 `shell=True` / `os.system` / 字符串拼命令 | `subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)`（`:77`），`cmd` 为 list | PASS |
| 无绝对路径 | 除 `Path(__file__)` 外不写死路径 | `ROOT = Path(__file__).resolve().parent.parent`（`:25`）；`grep '/Users\|file://'` 仅 `exercises.html:1101` 一行**注释** | PASS |
| 无外部 CSS/字体/JS | `<script src>` / `<link rel="stylesheet">` / `@import` / `url(http` 零命中 | 三页 + `_src/` 全零 | PASS |
| 唯一外链 | favicon | 三页各 1 处 `https://www.jaden.tech/static/img/favicon.png`；`demos/*.html` 19/19 同款（HG-SEC-236 已记 🟢 既有约定） | 记录项 F3 |
| 可重建 | 同数据重复构建逐字节一致 | **今日实测** scratch 树 `--apply` 后 `exercises/plan/archive` 3/3 sha256 **IDENTICAL**（`bb35c277…`/`c4453385…`/`d4468c61…`） | PASS |
| 幂等（无时间戳） | 产物不含构建时刻 | 产物内唯一日期是模板戳 `版本：1.0(2026-07-01)` 与数据 `updated: 2026-11-12` | PASS |

A5 复跑配方（本日已验证；`--apply` 只写 scratch，真仓零写入）：

```bash
S=$TMPDIR/cl037-repro && rm -rf "$S" && mkdir -p "$S"/{data,scripts,demos/slimdown/_src}
cd /Users/jadenli/CodeSpace/html-gen.cli
cp html-gen.py style-guide.css layout-*.html "$S"/
cp data/_slimdown-{exercises,plan}.json "$S"/data/
cp demos/slimdown/_src/* "$S"/demos/slimdown/_src/ ; cp scripts/build-slimdown.py "$S"/scripts/
( cd "$S" && python3 scripts/build-slimdown.py --apply )
for f in exercises plan archive; do
  a=$(shasum -a 256 "$S/demos/slimdown/$f.html" | cut -d' ' -f1)
  b=$(shasum -a 256 "demos/slimdown/$f.html" | cut -d' ' -f1)
  [ "$a" = "$b" ] && echo "$f IDENTICAL" || echo "$f DIFF $a $b"
done
```

### 1.3 数据契约（结论：PASS）

```bash
python3 - <<'PY'
import json
ex=json.load(open('data/_slimdown-exercises.json')); plan=json.load(open('data/_slimdown-plan.json'))
rows=ex['data']; ids={r['id'] for r in rows}
items=[i for d in plan['days'] for i in d['items']]
print(len(rows), len(ids), len(plan['days']), len(items), sorted({i['id'] for i in items}-ids))
PY
# 实测: 72 72 7 25 []
```

- 72 条 `id` 唯一（`ex01`..`ex72`），动作 `name` 零重复；方案 7 天 25 条安排；方案引用动作 **0 条缺口**（`ex70/71/72` 三条补齐有效）。
- `exercises.html` 的 `options` 为 `{pageSize, clickMode:"modal", search, exportCSV, columnResize}`——**未设 `density`**，故密度取「localStorage > options > default」链的 default（0.82rem），符合 CL036 默认档口径。

### 1.4 安全 / 隐私面

- **分享链接输入面已转义（非缺陷，列出以防误判）**：`#p=` 解码出的 `reps` 属外部可控串，但其 4 条渲染路径全部过 `esc()`（`plan.js:19` 转 `& < > " '`；编辑行 `:102-104`、动作选择器 `:151-155`、日卡/周卡构建 `:300-360`）；未知 id 丢弃并计数、非法片段静默忽略、全程无 `eval`/`new Function`。
- **隐私口径需澄清（P2，F2）**：`archive.html:196-203` 的基线表「现在」列是空 `<input>`（`data-b=...`，仅存 `localStorage: slimdown:baseline:v1`），但「阶段一目标」列写着 `60.0 kg` / `78 cm` / `≥87 cm` / `28` 等**个人目标值**；而 `:206` note 与 `README.md`「公开页不含个人身体数值」是**全称否定**。目标值算不算「身体数值」须一句定语收口。
- **「整周 518 字符」主张复现成立**（F7）：payload 本体 446 字符；以本机 `file:///Users/jadenli/CodeSpace/html-gen.cli/demos/slimdown/plan.html` 为基址 ⇒ 518；若换 `https://` 基址则是 492。⇒ 主张正确但**绑定基址口径**，评审勿用别的基址复算后判「数字不符」。

---

## 2. 闭环编号登记方案

### 2.1 落点与理由

| 落点 | tracked | 作用 | 本步动否 |
|:--|:--|:--|:--|
| `review-log.md`（文件末尾追加一段） | 是 | 全仓 CL 主台账（每批一段，含区间 / 结论 / 报告指针）；CL037 当前**只有两处旁证**（`:2658`、`:2682` 的「不属本批」表述），**无独立段 ⇒ 主登记点** | [2/6] 执行 |
| `documents/solutions/slimdown-case-attribution-design-v1.0-20261117.md` | 是 | 编号的持久落点：`b0f4b4f` 提交信息不可改，编号只能活在文档层 | **本步提交** |
| `cache/draft/TODO-20261109.md:24` | 否（`cache/` gitignored） | 会话台账；已有 `闭环: HTML-GEN-CL037` 的 READY 行，仅需补「方案:」指针 | [2/6] 执行（不入提交） |
| `TODO-handoff.md` | 是 | 会话轮转入口；可选加一行尾项（T5） | 待用户定（非必需） |
| `hm loop artifacts` / hm draft | 他仓 | 不代改（本批禁跨仓读写）；口径见 §2.4 | 不做 |

### 2.2 `review-log.md` 追加段（确切文本，置于文件末尾、现有 CL038/CL039 段之后）

```markdown
## 2026-11-17 — HTML-GEN-CL037 slimdown 案例归属登记（登记 + 复核，非独立评审）

> 受审区间: 单笔 `b0f4b4f`（2026-11-12 13:52，17 文件 +5823/−4，已在 `origin/main`）
> 归属: 他人笔（非本调度会话产出）；编号由 HG-SEC-231 补登，**不改写提交信息**
> 方案: `documents/solutions/slimdown-case-attribution-design-v1.0-20261117.md`
> 口径: 审查对象 = 存量产物 + 提交意图（`plan/archive` 与 `b0f4b4f` 同字节；`exercises.html` 经 1520089/87f2369 重渲 +56/−17）

### Summary

自包含复核 6/6 达标（stdlib 6 import / `subprocess` 列表式无 shell / 路径经 `ROOT` 相对化 / 无外部 CSS·字体·JS）；
scratch 树重建 3/3 sha256 逐字节一致；数据契约 72 id 唯一 + 7 天 25 条 + 引用 0 缺口；
CL036 密度变量在 `exercises.html` 6/6 命中，`plan/archive` 无 `.data-table` ⇒ N/A（纸张面，README 已明示刻意不同源）。

### 发现

- P1 产物零回归守卫：`scripts/baseline.py:116` 把 `demos/slimdown/` 整目录 `CASE_SKIP`（3 页 0 条基线），`tests/` 无任何断言 ⇒ 模板/数据改动后静默漂移只能靠手工重建发现。
- P2 隐私措辞：`archive.html:206` + `README.md`「公开页不含个人身体数值」与该页「阶段一目标」列的 `60.0 kg/78 cm/≥87 cm` 存在字面冲突（目标值 vs 实测值未区分）。
- P2 favicon 外链（三页各 1 处）与 `AGENTS.md:22`「产物必须自包含单文件」字面冲突，属 19/19 demos 既有约定（HG-SEC-236）。
- 记录：`innerHTML` 8 处已全部过 `esc()`；518 字符主张成立但绑定 `file://` 基址；`build-slimdown.py` 无 `--root`（探针须整树 cp）。

### 处理

- 登记不阻塞代码：本段 + 方案文档即闭环依据；`cache/draft/TODO-20261109.md:24` 由 READY 翻 DONE 待 F1/F2 定论后执行。
- 未 push；未改写 `b0f4b4f`。
```

追加命令（[2/6] 可复跑，path-scoped）：

```bash
cd /Users/jadenli/CodeSpace/html-gen.cli
# 段文本见上；用编辑器/patch 追加后：
git add review-log.md
git commit -q --only -- review-log.md -m "docs@review: register CL037 for the slimdown case (HG-SEC-231)"
git log -1 --format='%h %an <%ae> | %s'
# 期望: Jaden.Li <jaden.li@jaden.tech> | docs@review: register CL037 ...
```

### 2.3 draft 行改动点（gitignored，不入提交）

`cache/draft/TODO-20261109.md:24` 现文（节选）：

```
- [ ] **slimdown 案例（他人笔 b0f4b4f）**: …（…; 状态: READY; 闭环: HTML-GEN-CL037; kind: queued; priority: low; 需求: review HG-SEC-231…; 验收: 补闭环编号登记 + 产物自包含核对 + 与 CL036 密度变量一致性核查）
```

改法（**只加不改**，`[ ]`/`READY` 留到关闭时再翻）：

1. 行尾追加：` 〔方案: documents/solutions/slimdown-case-attribution-design-v1.0-20261117.md；复核: 自包含 6/6 + 重建 3/3 + 密度 exercises 6/6、plan/archive N/A；待决: F1 重建守卫（+1 计数需审批）/ F2 隐私措辞〕`
2. 验收项措辞对齐本方案 §4 AC，避免「已核对」被读成「已关闭」。

### 2.4 hm loop 归属口径（不代改，只定口径）

- **编号真源在本仓**：`review-log.md` 的 CL037 段 + 本设计文档路径。hm 侧关闭 HG-SEC-231 时引用这两处，不在 hm 另起编号。
- **`git log --grep CL037` 恒为 0 是预期**（提交信息不改写）⇒ 任何以「grep 不到 CL号」判 FAIL 的判据都不成立，见 AC-9。
- 若 hm 侧确需补 artifact，由用户或 ops 会话在 hm 执行（本会话**禁跨仓读写**，未执行、未落转交件）。

---

## 3. 与 CL036 密度变量一致性核查

### 3.1 口径真值（CL036，`layout-table.html`）

| 项 | 值 | 位置 |
|:--|:--|:--|
| `--table-fs` 默认 | `0.82rem` | `layout-table.html:104` |
| `.data-table.dense` | `0.7rem` | `:162` |
| `.data-table.comfortable` | `0.94rem` | `:165` |
| `th` 联动 | `×0.88` | `:107` |
| `.cell-pill` / `.video-pill` | `×0.86` | `:50` / `:54` |
| 表尾 note | `×0.8` | `:41` |

### 3.2 三页判定

| 页面 | `.data-table` 行 | `var(--table-fs)` | ×0.88 | ×0.86 | ×0.8 | `DENSITY_FS` | 判定 |
|:--|--:|--:|--:|--:|--:|--:|:--|
| `exercises.html`（table 模板） | 68 | 5 | 1 | 2 | 1 | 2 | **PASS 6/6** |
| `plan.html`（纸张面） | 0 | 0 | 0 | 0 | 0 | 0 | **N/A** |
| `archive.html`（纸张面） | 0 | 0 | 0 | 0 | 0 | 0 | **N/A** |

补充：`exercises.html:1871` `DENSITY_FS = {default:'0.82rem', compact:'0.7rem', comfortable:'0.94rem'}` 与 CSS 三档同值；`:1922` 密度入口无条件渲染（CL036 单视图页修复）；`:1518` 分享链接带 `density=`。
`plan.html` / `archive.html` 用 `_src/base.css` 的 px 字面量（`th 11px / td 12px` 等，`base.css:36-37`），且无密度面板——**这与 README「视觉不同源是刻意的」一致**，不是漏改。

### 3.3 核查命令与期望输出

```bash
cd /Users/jadenli/CodeSpace/html-gen.cli
for f in exercises plan archive; do
  printf '%-10s table=%s fs=%s th88=%s pill86=%s foot8=%s dens=%s\n' "$f" \
    "$(grep -c 'data-table' demos/slimdown/$f.html)" \
    "$(grep -o 'var(--table-fs)' demos/slimdown/$f.html | wc -l | tr -d ' ')" \
    "$(grep -o '\* 0\.88' demos/slimdown/$f.html | wc -l | tr -d ' ')" \
    "$(grep -o '\* 0\.86' demos/slimdown/$f.html | wc -l | tr -d ' ')" \
    "$(grep -o '\* 0\.8)' demos/slimdown/$f.html | wc -l | tr -d ' ')" \
    "$(grep -c 'DENSITY_FS' demos/slimdown/$f.html)"
done
# 期望:
# exercises  table=68 fs=5 th88=1 pill86=2 foot8=1 dens=2
# plan       table=0  fs=0 th88=0 pill86=0 foot8=0 dens=0
# archive    table=0  fs=0 th88=0 pill86=0 foot8=0 dens=0
```

变异探针（**本轮实测**，判据判别力，不是恒真）：把 `exercises.html:348` 的 `0.82rem` 改成 `0.92rem` 写到 scratch ⇒
第一组计数**一个都没变**（仍 `68/5/1/2/1/2`），但下面的值断言掉到 `0`。
⇒ 结论：只用计数会漏「值漂移」，值断言是必需的第二道。判据须两组并用：

```bash
grep -c ':root { --table-fs: 0.82rem; }' demos/slimdown/exercises.html          # 期望 1
grep -c '\.data-table\.dense { --table-fs: 0.7rem; }' demos/slimdown/exercises.html        # 期望 1
grep -c '\.data-table\.comfortable { --table-fs: 0.94rem; }' demos/slimdown/exercises.html # 期望 1
```

### 3.4 判级规则（写死在方案里，避免评审各自发挥）

- `exercises.html` 任一档变量或任一联动比例缺失/数值漂移 ⇒ **FAIL**（违反 CL036 硬约束）。
- `plan/archive` 出现 `--table-fs` 但无密度入口（半套实现）⇒ **COND**。
- `plan/archive` 零命中且评审报告**写明 N/A 理由**（非 table 模板页 + README 已知取舍）⇒ **PASS**；未写明 ⇒ **COND**（口径缺失，不是代码缺陷）。

### 3.5 覆盖缺口（并入 F1）

`tests/test_cl036_table_density_actions.py` 的断言只作用于**临时目录里新生成的页面**，不覆盖已提交的 `demos/slimdown/exercises.html`；`scripts/baseline.py` 又把整目录 skip ⇒ 该产物「既无测试也无基线」。

---

## 4. 已知缺陷分级与 AC 清单

### 4.1 分级

| ID | 级别 | 现象（实测） | 落点 | 建议修法 | 阻塞登记? |
|:--|:--|:--|:--|:--|:--|
| F1 | **P1** | slimdown 三页零回归守卫：`baseline.py:116` 目录型 `CASE_SKIP`（基线文件 `slimdown` 命中 0）+ `tests/` 无断言 ⇒ 重刷/改模板后静默漂移 | `scripts/baseline.py:116`、`tests/` | 新增 `tests/test_slimdown_rebuild.py` 1 例（scratch 树 `--apply` → 3/3 sha256 等于仓内值；顺带把 3.3 的密度值断言并进去）；计数 478→**479 需 AGENTS.md 审批** | 否 |
| F2 | P2 | 隐私口径字面冲突：「阶段一目标」列有 `60.0 kg/78 cm/≥87 cm`，note/README 说「公开页不含个人身体数值」 | `archive.html:191/196-206`、`demos/slimdown/README.md` | note 改为「不写个人**实测**值；目标值属方案参数」，README 同步一句 | 否 |
| F3 | P2 | favicon 外链 3 处 vs `AGENTS.md:22`「产物必须自包含」 | `_src/*.tpl:7`（继承到三页） | 文档层登记例外（`documents/` 一处 + 本段），不删 icon（19/19 demos 一致，删了反而制造新漂移） | 否 |
| F4 | 记录 | `plan.js` 8 处 `innerHTML` 易被误判 XSS；实为 4 条渲染路径全过 `esc()`（`plan.js:19`），`#p=` 值不可注 | `demos/slimdown/_src/plan.js` | 不改；评审报告写明「已核」 | 否 |
| F5 | P2 | `build-slimdown.py` 只能写仓内 `OUT`，无 `--root/--out` ⇒ 复现探针必须整树 `cp`（易被抄成「直接 `--apply`」污染工作树） | `scripts/build-slimdown.py:26-30` | 加 `--root`（默认仓根，行为不变）；或只在 README 写清探针配方（本方案 §1.2 A5 已给） | 否 |
| F6 | 记录 | `b0f4b4f` 的 tree ≠ 现行产物（`exercises.html` +56/−17） | — | 评审口径固定为「存量产物 + 提交意图」 | 否 |
| F7 | 记录 | 「518 字符」成立但绑定 `file://` 基址（payload 446 / https 基址 492） | `plan.html`「分享长度」提示 | 写明基址口径 | 否 |
| F8 | 记录 | 数据契约 PASS 证据（72/72/7/25/0） | `data/_slimdown-*.json` | 作为 AC-6 证据留档 | 否 |

分级口径：P0 = 安全/数据/产物不可用；P1 = 可静默漂移且无自动发现手段；P2 = 文档/口径/可维护性；记录 = 已核无风险但易被误判。

### 4.2 AC 清单（每条可复跑）

| AC | 判据 | 命令（摘） | 通过条件 |
|:--|:--|:--|:--|
| AC-1 | 生成器纯标准库 | `grep -n '^import\|^from' scripts/build-slimdown.py` | 6 行，全部 stdlib |
| AC-2 | 无 shell 注入面 | `grep -cE 'shell=True\|os\.system\|os\.popen' scripts/build-slimdown.py` | `0` |
| AC-3 | 无绝对路径 | `grep -nE '/Users/\|file://' demos/slimdown scripts/build-slimdown.py` | 仅 `exercises.html:1101` 注释 1 行 |
| AC-4 | 外链枚举 | `grep -c 'jaden.tech/static/img/favicon.png' demos/slimdown/*.html` | 每页 1；且 `<script src\|<link rel="stylesheet"\|@import` 全 0 |
| AC-5 | 逐字节可重建 | §1.2 A5 配方 | `3/3 IDENTICAL` |
| AC-6 | 数据契约 | §1.3 one-liner | `72 72 7 25 []` |
| AC-7 | CL036 密度（table 页） | §3.3 两组命令 | 第一组 `68/5/1/2/1/2`，第二组 `1/1/1` |
| AC-8 | CL036 密度（纸张面 N/A） | §3.3 第一组 plan/archive 行 | 全 0 **且**评审报告写明 N/A 理由 |
| AC-9 | 登记闭环 | `git log -1 --format=%s \| grep CL037` 可为空（预期）；`grep -c 'CL037' review-log.md` ≥1 **且必须新增独立段**（现为 2，两处都是 `:2658`/`:2682` 的「不属本批」旁证，不计） | 存在 `## 2026-11-17 — HTML-GEN-CL037` 段、编号与 HG-SEC-231 互指、不改写 `b0f4b4f` |
| AC-10 | 隐私措辞 | `grep -n '个人身体数值' demos/slimdown/README.md demos/slimdown/archive.html` | 改为「实测值 / 目标值」区分口径 |

### 4.3 判定为 review COND 或 FAIL 的条件

**FAIL（任一即成立）**

1. AC-5 出现任何 `DIFF` ⇒ `b0f4b4f` 的「重复构建逐字节一致」承诺被证伪，案例不可复现。
2. AC-7 `exercises.html` 三档变量或 0.88/0.86/0.8 任一缺失/数值漂移 ⇒ 违反 CL036 硬约束。
3. 登记动作触碰历史：出现 `rebase`/`amend`/`filter-branch` 作用于 `b0f4b4f`，或对已推区间强推。
4. `review-log.md` 段缺失、编号与 HG-SEC-231 不互指，或段内声称的复核结论与 AC 实测不符（自证不实）。
5. 把 F2 的「目标值」直接当「个人实测数据泄露」定性并据此删数据（过度修复，改变方案语义）。

**COND（可放行但需记录/下批）**

1. AC-1..AC-6、AC-8、AC-9 全绿，但 F1 未落（无重建守卫）⇒ 允许 COND，须在报告写明「漂移面仍无自动发现手段」。
2. AC-8 未写明 N/A 理由 ⇒ COND（口径缺失）。
3. F2 措辞未改 ⇒ COND。
4. F5 未加 `--root` 但 README/方案已有探针配方 ⇒ 不构成 COND（记录项）。

**PASS**：AC-1..AC-10 全绿，或 F1/F2 明确转下批并在 `cache/draft` 立条目。

---

## 5. 影响面与提交计划

| 步骤 | 文件 | 行数预算 | 提交 |
|:--|:--|:--|:--|
| 本步（[1/6] 方案） | `documents/solutions/slimdown-case-attribution-design-v1.0-20261117.md` | 新增 ~1 文件 | `docs@design: CL037 slimdown attribution + self-containment + CL036 density plan (HTML-GEN-CL037)`，path-scoped `--only` |
| [2/6] 登记 | `review-log.md` | +~30 行 | `docs@review: register CL037 for the slimdown case (HG-SEC-231)` |
| [2/6] 台账 | `cache/draft/TODO-20261109.md:24` | +1 句 | 不入提交（gitignored） |
| 可选 | `TODO-handoff.md` T5 行 | +1 行 | 待用户定 |
| 仅在 F1 落地时 | `tests/test_slimdown_rebuild.py`（+1 例） | — | **需 AGENTS.md 计数审批**（478→479） |

- author/committer：`Jaden.Li <jaden.li@jaden.tech>`（仓内 git config 已如此，无需 `--author`）。
- 回退：单文件 `git rm` / 单笔 `git revert`；不产生历史改写。
- 零外部依赖、零模板/CLI 契约改动 ⇒ 不触发三面同步（`help` / `TEMPLATE_CONTRACT` / `test_help_contract`）。

---

## 6. 下一步待人工 / 评审

1. **评审本方案**（review profile）：重点看 §3.4 判级规则与 §4.3 FAIL 条件是否同意——这两节决定后续是否被误判。
2. **[2/6] 登记执行**：按 §2.2 落 `review-log.md` 段 + §2.3 补 draft 指针（本步未做，属实现）。
3. **F1 决策（需用户选）**：
   - A：本批就加重建守卫（+1 测试计数，需 AGENTS.md 审批）；
   - B：转下批（本批 COND 放行，`cache/draft` 立条目）；
   - C：改走 baseline 纳入（成本最高：需给 `baseline.py` 加自建链支持）。
4. **F2 措辞**：是否本轮改（`archive.html` note + 案例 README 各一句）。
5. **hm 侧 HG-SEC-231 关闭**：由用户/ops 会话在 hm 执行（本会话禁跨仓读写，未动 hm 任何文件）。

---

## 7. 附：本轮实测原始输出（只读探针，可复跑）

```
$ python3 scripts/build-slimdown.py --dry-run
[dry] /Library/Developer/CommandLineTools/usr/bin/python3 …/html-gen.py table -d data/_slimdown-exercises.json -o demos/slimdown/exercises.html --title 训练动作库 · slimdown --home-url plan.html
[dry] write demos/slimdown/plan.html (52,598 bytes)
[dry] write demos/slimdown/archive.html (24,054 bytes)
rc=0   # 之后 git status 仍为空（dry-run 零写入）

$ # scratch 树 --apply + shasum 比对
exercises.html IDENTICAL bb35c27734cb
plan.html      IDENTICAL c44533854e83
archive.html   IDENTICAL d4468c61c543
✅ slimdown: 72 个动作 / 7 天 / 25 条安排

$ git diff --numstat b0f4b4f..HEAD -- demos/slimdown
56  17  demos/slimdown/exercises.html        # plan/archive 无条目 = 与 b0f4b4f 同字节

$ git merge-base --is-ancestor b0f4b4f origin/main && echo IN_ORIGIN   # IN_ORIGIN
```
