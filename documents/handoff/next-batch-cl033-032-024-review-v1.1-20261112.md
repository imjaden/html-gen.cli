---
title: next-batch CL033/CL032/CL024 — review报告 v1.1（尾项复核 round-2）
topic: next-batch-cl033-032-024
type: review
version: 1.1
date: 2026-11-12
author: hermes-v0.23.1(2026.9.24)
profile: review
tags: [review, html-gen, recheck, split-grid, baseline-gate, chromedriver]
loop: HTML-GEN-CL033
---

# next-batch CL033/CL032/CL024 — review报告 v1.1（尾项复核 round-2）

> 日期: 2026-11-12 09:26~10:0x · 闭环: **HTML-GEN-CL033 尾项复核**（本批实跨 CL033/CL032/CL024）· 角色: review（1A 口径：独立复算，禁采信转述）
> 受审区间: `github/main..HEAD` **5 笔**（4 业务 + 1 上轮审计）· `rev-list --count`=6（第 6 笔 `4e7574f` 为零代码派生物，不计入）
> - `83f9488` fix@table: splitGrid inline span "full" fills remaining tracks only (HTML-GEN-CL033) — 13 文件
> - `d9d4ef3` chore@baseline: --verify covers all rebuildable products (HTML-GEN-CL032) — 15 文件
> - `f41c412` chore@tests: chromedriver path via CHROMEDRIVER env (HTML-GEN-CL024) — 36 文件
> - `5d122c9` audit@review: next-batch … review CONDITIONAL 80 (HG-SEC-203..212) — 3 文件（上轮报告）
> - `cc59515` fix@tests: review follow-ups HG-SEC-204/205/207/208/209/211/212 (HTML-GEN-CL033) — 9 文件（**本轮返工面**）
> 区间唯一文件 59 / +905 −193（`git diff --shortstat 4e7574f..HEAD`）· HEAD=`cc59515` · `git status` 空 · ahead 6 / behind 0
> **结论: ✅ PASS — 95/100（A）· 0 🔴 / 1 🟡（建议修，非阻断）/ 6 🟢 record** · 上轮唯一阻塞项 HG-SEC-203 已闭合

---

## ① errata：sha 位移（不是缺陷）

上轮报告与 `review-log.md` / `.review-level.yaml` 中引用的旧 sha 已被 CL008 reword 重写（`git reflog` 可见 `filter-branch: rewrite`）。
**内容零变化，已逐笔证明**（三口径同时成立 5/5，见 §② 前两行）：

| 旧 sha（分支历史已无） | 新 sha | 唯一变化 |
|:--|:--|:--|
| `70f714b` | `83f9488` | subject → 英文 |
| `4225011` | `d9d4ef3` | subject → 英文 |
| `6bb5f6d` | `f41c412` | subject → 英文 |
| `488bbac` | `5d122c9` | subject → 英文（上一轮审计笔） |
| `c40be23` | `cc59515` | subject → 英文（返工笔原文为中文） |

- 旧 sha 仍可解析（reflog + 分支 `backup-pre-reword-20261112`），**未 push 过 ⇒ 无 force、无对外历史改写**（`HEAD..github/main`=0）。
- 本报告及后续一律以新 sha 为准；上轮报告 `documents/handoff/next-batch-cl033-032-024-review-v1.0-20261112.md` 正文保持原样（append-only 审计留痕），erratum 由本文件承接。
- 遗留（🟢 建议）：本地 `refs/original/refs/heads/main` 与 `backup-pre-reword-20261112` 在推送后可删，避免 `push --all` 误带旧链。

---

## ② 数据验证（全部由本轮独立执行）

| 验证项 | 方法 | 结果 |
|:--|:--|:--|
| reword 未改内容 | `git rev-parse <old>^{tree}` vs `<new>^{tree}` | **5/5 IDENTICAL** ✅ |
| 同上（补丁面） | `git show <c> \| git patch-id --stable` | **5/5 SAME** ✅ |
| 同上（正文面） | `git log -1 --format=%B \| tail -n +2 \| md5` | **5/5 SAME** ⇒ 除 subject 外 body 逐字未变 ✅ |
| CL008（上轮唯一阻塞） | `git log --format=%s github/main..HEAD` + CJK 正则 | 区间 **6/6 subject 全英文，CJK 命中 0** ✅；`hm check commit . --json` → `cjk_new` **157 → 153**（余量全在区间外） |
| 全量回归（权威 `-n 4`） | `/usr/bin/python3 -m pytest tests/ -q -n 4` ×2 | **466 passed / 66.14s**；**466 passed / 70.76s** ⇒ 2/2 绿，计数 466 成立 ✅（206 债务本轮未复现，不因此销号） |
| 渲染基线门禁 | `scripts/baseline.py --check` | **基线一致 23/23**，rc=0 ✅ |
| 产物与模板同源 | `scripts/baseline.py --verify` | **15 current（sha 逐对相等）+ 5 带理由 skip**，rc=0 ✅ |
| 临时目录回收（212） | 同上 + `ls -d /tmp/baseline-verify-*` | verify 后 **0 残留** ✅；`--keep-temp` 实测**留下 1 个**（`TMPDIR` 生效位置随环境，见 215） |
| 204 ①「64 → 31」 | 三处 grep `\b64\b`（conftest/test_selenium_infra） | **0 处残留** ✅；修前真值独立复算：`git grep` @`4e7574f` → **31 文件 / 32 处路径 / 35 处 `Service(`** = 返工笔 body 声称值，逐字吻合 ✅ |
| 204 ②「判据补 `--include`」 | `grep -rn "/Users/" tests/ --include=*.py \| grep chromedriver \| wc -l` | **2**（≠ 文档声明的 0）⇒ 见 **HG-SEC-213**；两行均为判据自身（`test_selenium_infra.py:33` 注释、`:41` 判据行） |
| 硬编码清面终态 | `grep -rn "script-miner/cache/chromedriver" tests/` | **0 处**（连字面量都不再有：缺省值为 `expanduser` 分段拼）✅ |
| 207 缺省值不绑用户名 | 读 `conftest.py:18-22` + 子进程打印 | `os.path.join(expanduser('~'), 'CodeSpace','script-miner','cache','chromedriver','chromedriver')` ✅；skip 理由回显 `/Users/jadenli/…`（本机按 `~` 展开，非写死） |
| 205 缺驱动口径 | `CHROMEDRIVER=/nonexistent pytest tests/test_split_grid.py -n 0 -rs` | **13 skipped**，理由含实际路径 + `CHROMEDRIVER=<path>` 覆盖提示 ✅ |
| 205 strict 开关 | `CHROMEDRIVER=/nonexistent CHROMEDRIVER_REQUIRED=1 pytest tests/test_doc_width.py -n 0` | **4 errors（RuntimeError）+ 4 passed**，**不 skip** ✅ |
| 208 守卫判别力（变异 3 例） | 在 `tests/` 副本注入违规后跑 `test_selenium_infra.py` | M1 顶层追加 `/Users/.../chromedriver` ⇒ **test_01 红**；M2 `tests/sub/test_nested.py` 嵌套 ⇒ **红且点名 `sub/test_nested.py:1`**（证 `rglob` 真递归）；M5 docstring 内 ⇒ **红** ✅ |
| 208 豁免面（变异 2 例） | 同上 | M3 真实代码行 + `# noqa: user-path-guard` ⇒ **4 passed**；M4 `#` 开头注释行 ⇒ **4 passed** ⇒ 豁免仍无界（见 214） |
| 209 残留导入 | `grep -rn "chrome.service import Service" tests/` | 仅 `conftest.py:16` ✅；`grep -rn "Service(" tests/` 仅 `conftest.py:41` ✅ |
| 211 文档措辞 | 读 `layout-table.html:1457/1464/1496/1505` 对照 `templates.md` 新句 | `maxCols`=各行 span 之和最大值（`:1464`），写入容器 `--kv-cols`（`:1505`）⇒ 文档「以 `maxCols` 为基」成立 ✅ |
| 212 `--flag=value` 真生效 | `html-gen.py knowledge … --title=-dash-title` | rc=0，产物 `<title>-dash-title</title>` ✅；同值走两 token 形式 `--title -dash-title` ⇒ argparse usage 拒绝（还原了旧缺陷）✅ |
| 计数三面 | README/README.zh/testing.md/AGENTS.md + `ls tests/test_*.py` | README:137 / README.zh:135 → **466**；testing.md → **46 文件**、`test_selenium_infra 4`；AGENTS.md `:6`/`:44` 仍 **458 / 45**（受保护，见 210） |
| 各文件用例数 | `grep -c '    def test_'` | test_selenium_infra **4** / test_split_grid 13 / test_baseline_gate 9 / test_templates 18 ✅ 与 testing.md 声明一致 |
| 安全面（返工 diff） | `git diff 5d122c9..HEAD` 正则扫 `api_key\|secret\|password\|token\|shell=True\|os.system\|eval(\|exec(\|verify=False` | **0 命中** ✅；新增外链/`<script src=http>`/远程字体 **0** ✅ |
| 工作树 | `git status --short` | 空 ✅（复算前后两次；探针全部落在 scratch/与 `$TMPDIR`，已清） |

---

## ③ 返工面逐项复核（上轮 7 项 + 2 项挂账）

| Finding | 上轮 | 本轮判定 | 我的实测依据 |
|:--|:--|:--|:--|
| **HG-SEC-203** 3/3 CJK subject | 🟡 阻塞 | ✅ **closed** | 区间 6/6 英文；5 组 tree/patch-id/body-md5 三口径 5/5 相同 ⇒ 仅 subject 变 |
| **HG-SEC-204** 自证材料与实测不符 ① | 🟡 | ✅ **closed** | 三处 `64` 清零；31/32/35 三值独立复算与 body 逐字吻合 |
| **HG-SEC-204** ② grep 判据 | 🟡 | 🟡 **部分闭合 → 转 HG-SEC-213** | 判据换了形式（`--include=*.py` 正确解决 `.pyc` 3 个假命中），但新判据的期望值 **0 与实测 2 不符**（判据自身两行） |
| **HG-SEC-205** 缺驱动静默 skip | 🟡 | ✅ **closed（含残留 216）** | `CHROMEDRIVER_REQUIRED=1` → RuntimeError，test_04 守；默认仍 skip 且理由带路径（与设计一致） |
| **HG-SEC-206** `-n 4` 偶发红 | 🟡 | ⏸ **按既有债挂账（未在本笔修，双方已约定单独立项）** | 本轮 2 次全量 2/2 绿；不因此销号 |
| **HG-SEC-207** 缺省值绑用户名 | 🟢 | ✅ **closed** | `expanduser` 分段拼；test_02 oracle 改为按 `~` 现算（且断言 env 覆盖优先） |
| **HG-SEC-208** 守卫面窄 + 拼接豁免 | 🟢 | ✅ **closed（含残留 214）** | `rglob` + 取消按名豁免（conftest 同受约束）+ `noqa` 显式标注；变异 M1/M2/M5 红、M3/M4 豁免 |
| **HG-SEC-209** 残留 `Service` 导入 | 🟢 | ✅ **closed** | `test_templates.py` 该局部导入已删；全仓 `chrome.service import Service` 仅 conftest |
| **HG-SEC-210** AGENTS.md 计数 | 🟢 待审批 | ⏸ **仍开（受保护文件，未绕过）** | `:6` 458 / `:44` 458·45，实测 466/46 ⇒ 偏差由上轮 7 扩到 **8**；README 仍指向它作权威 |
| **HG-SEC-211** 「剩余轨」基准未点明 | 🟢 | ✅ **closed** | templates.md 新句 + 代码 `:1464/:1505` 三处对齐 |
| **HG-SEC-212** verify 临时目录 / argv 前缀 | 🟢 | ✅ **closed（含残留 215/217）** | 实测 0 残留 + `--keep-temp` 保留 1；`--title=-dash-title` 生效、两 token 形式被拒 |

---

## ④ 合理性评估

| # | 判据 | 结论 |
|:--|:--|:--|
| REA-1 | 修复是否对准根因而非自证数字 | ✅ 204 的三处 `64` 是**叙述性自证**，直接删数字改为可复算的「31 文件」；207 把「env 可覆盖但缺省仍绑用户名」改成真正去耦合（分段 + `~`），换机可跑而非降级 skip |
| REA-2 | 205 的 strict 开关是否「缺驱动即红」而非换个名字静默 | ✅ 语义在 `chromedriver_service()` 单点分支（`REQUIRED` 为真 ⇒ RuntimeError），39 处调用点无需改动即受控；test_04 从子进程侧验证「不 skip 而是错」 |
| REA-3 | 208 的豁免范式是否从「拼接绕检」升级为可审 | ✅ 拼接已删，改为同行 `noqa: user-path-guard` 标注 ⇒ **可 grep 可枚举**；且 conftest 不再整免。残留：豁免无数量上界（214） |
| REA-4 | 212 的清理是否可能删错东西 | ✅ 只删本次 `mkdtemp` 出来的唯一目录（`ignore_errors`），不 glob 全量；未 push 前实测 `/tmp` 与 `$TMPDIR` 双位置均回到 0 |
| REA-5 | `--title=` 形式是否会改变渲染语义 | ✅ 实测同一值两种传法产出一致（`-dash-title` 字面进 `<title>`）；`test_baseline_gate` 的断言从 `in '--title'` 改为 `startswith('--title=')`，**等强度**（仍要求存在且带值） |

## ⑤ 严格性评估

| # | 判据 | 结论 |
|:--|:--|:--|
| RIG-1 | 声称值是否逐条可复现 | ⚠️ 24 条声称中 22 条逐字可复现；2 条不成立：① testing.md/body 的 `… \| wc -l == 0` 实测 **2**（213，**同类缺陷第 3 次**：上轮 204 ① 数字不符 → 本轮 ①修好、②换了形式但仍不符）；②「顺手清掉 135 个历史遗留目录」为仓外一次性手动操作，不可复算（结果面 `/tmp`=0 与声明一致，217） |
| RIG-2 | 新守卫是否具备真判别力（非恒真） | ✅ 变异 3 红 2 豁免，**逐例点名**（`test_01`）；嵌套目录也红 ⇒ `rglob` 不是装饰性改动 |
| RIG-3 | 是否借修 finding 顺手削弱既有断言 | ✅ 本笔 9 文件全为 `tests/` + docs + `scripts/baseline.py`；唯一断言改动是 `--title` 形式（等强度）；**无一处断言被删或放宽**（`git diff 5d122c9..HEAD -- tests/` 逐 hunk 核） |
| RIG-4 | 挂账项是否诚实登记而非静默跳过 | ✅ 206 在 commit body 明写「未在本笔修」并给出成因（固定 `/tmp` + toast 等待）与归属（单独立项），与上轮裁定一致 |
| RIG-5 | 计数三面是否同步 | ✅ README/README.zh/testing.md 已同步 466/46/`infra 4`；AGENTS.md 例外有审批阻塞背书（210） |
| RIG-6 | 全量可复现性 | ✅ 2/2 全绿（66.14s / 70.76s），无 flaky；但 206 债务仍在 ⇒ 不能宣称「恒真」 |

## ⑥ 安全性评估

| # | 面 | 结论 |
|:--|:--|:--|
| SEC-A | 门禁完整性（本批核心） | ✅ 205 修复后「缺驱动」不再默认静默：默认 skip 有显式理由（路径 + 覆盖方式），`CHROMEDRIVER_REQUIRED=1` 下变红。**残留**：仓内无 CI（`.github` 仅 `ISSUE_TEMPLATE`）⇒ 开关无自动落点（216） |
| SEC-B | 路径/信任边界 | ✅ 缺省值改 `~` 展开后不再泄漏本机用户名到测试源码（`/Users/` 命中仅剩判据自身 2 行）；`CHROMEDRIVER` 仍可指向任意可执行文件——本地测试运行器、无权限跨越（沿用上轮 SEC-E，不升级） |
| SEC-C | 子进程面（新增 `shutil`） | ✅ 仅 `shutil.rmtree(本次 mkdtemp)`，无 glob、无用户输入拼接；`build_jobs` 仍 list-form argv，无 `shell=True` |
| SEC-D | 注入面（`--flag=value`） | ✅ 值来自产物 DOM 回收，argv 直传不经 shell；`=` 形式消除 `-` 前缀歧义且**不引入**解析歧义（argparse 按首个 `=` 切分） |
| SEC-E | 凭据 / 供应链 / 零依赖 | ✅ 返工 diff 无 token/key/password；无新增第三方包、无 CDN/远程字体；产物零改动（本笔不触产物） |
| SEC-F | 审计面自身（自证数字） | ⚠️ 本轮唯一实质问题：**自证判据本身不成立**（213）——判据若不成立，门禁的「可复算性」就打折；建议把该判据落成用例（现在 `test_01` 已是其实体），文档只引用用例名，杜绝第三次漂移 |

---

## ⑦ 安全事项

🟡 **HG-SEC-213 — 新复算判据的期望值仍与实测不符（204 的同类缺陷，第 3 次）**

`documents/testing.md:22-23` 与 `cc59515` body 的验收行均写：`grep -rn "/Users/" tests/ --include=*.py | grep chromedriver | wc -l` **== 0**；实测 **2**：
`tests/test_selenium_infra.py:33`（注释里写了「`/Users/` 与 chromedriver 同行」）+ `:41`（判据代码本身，末带 `# noqa: user-path-guard`）。判据扫到了自己 —— 与上轮 204 ② 同型（当时是 `__pycache__/*.pyc` 3 个假命中，本次是判据自身 2 行）。
**影响**：零行为影响，但这是仓内权威测试文档给出的复算命令；照抄必得 2，读者无法区分「文档错」与「仓库坏」。
**修复建议（任选，一行级）**：① 判据改为「**0 处非标注命中**」：`grep -rn "/Users/" tests/ --include=*.py | grep chromedriver | grep -v 'noqa: user-path-guard' | grep -v ':33:' | wc -l` == 0（并把 `:33` 注释措辞改成不含 `/Users/` 与 `chromedriver` 双 token，例如「用户绝对路径」）；或 ② 直接写「!= 2 即红」不好读，改写成「== 2（均为 `test_selenium_infra.py` 判据自身，已 `noqa` 标注）」。**根治**：文档只写「由 `tests/test_selenium_infra.py::test_01_*` 守卫」，不再复制命令与数字（双源漂移的成因）。

🟢 **HG-SEC-214 — 守卫的豁免仍无上界（`noqa` 标注可被真实代码借走）**

变异实测：`X = '/Users/someone/y/chromedriver'  # noqa: user-path-guard` ⇒ **4 passed**（未命中）；`#` 开头的注释行整行豁免 ⇒ 同样通过。相对上轮「拼接即豁免」已是进步（可 grep、可枚举），但没有任何断言限制豁免数量/位置 ⇒ 后续笔可无痕豁免真实告警。
**建议**：加一条断言「`noqa: user-path-guard` 的**允许集合**恰为 `{test_selenium_infra.py:41}`」（比对 `(relpath, lineno)` 集合），或至少断言计数 == 1。
**证据**：`M3/M4` 变异 4 passed；`grep -rn "noqa: user-path-guard" tests/*.py` → 2 行（`:34` 说明、`:41` 判据）。

🟢 **HG-SEC-215 — `--keep-temp` 不打印目录；清理无 `try/finally`**

`scripts/baseline.py:235-236` 只在正常返回路径 `rmtree`；`--keep-temp` 时既不删除**也不输出 tmpdir**（实测 `--verify --keep-temp` 输出中 `baseline-verify-` 出现 **0 次**），而 `mkdtemp` 落点随 `TMPDIR`（本机为 `/var/folders/...`，非 `/tmp`）⇒ 想排查的人找不到目录。
**建议**：`if keep_temp: print(f'临时目录: {tmpdir}')`；把 `for` 循环与 `rmtree` 包进 `try/finally`（`build_jobs` 内 `read_text` 抛错时不至泄漏）。

🟢 **HG-SEC-216 — `CHROMEDRIVER_REQUIRED` 解析大小写不全 + 无自动落点**

`conftest.py:22` `not in ('', '0', 'false', 'False')` ⇒ `CHROMEDRIVER_REQUIRED=FALSE` / `NO` 会被当成「必须」。另：仓内无 CI（`.github/` 仅 `ISSUE_TEMPLATE`），`testing.md` 的「CI 必须置 1」目前是纸面规约，无任何自动检查会红。
**建议**：`os.environ.get('CHROMEDRIVER_REQUIRED','').lower() in ('','0','false','no')` 取反；`testing.md` 补一条可直接复制的本地严格跑法 `CHROMEDRIVER_REQUIRED=1 python3 -m pytest tests/ -q -n 4`。

🟢 **HG-SEC-217 — 「清理 135 个历史遗留目录」为仓外不可复算操作**

commit body 记「顺手清掉 135 个历史遗留目录」。实测当前 `/tmp` 与 `$TMPDIR` 的 `baseline-verify-*` 均 0（结果面与声明一致），但该批量清理无脚本/无日志，属一次性手动操作，他人无法重放，也无法审计删除范围（若曾用 `/tmp/baseline-verify-*` glob，理论上可删到其他并发会话正在排查的目录）。
**建议**：如后续仍需批量清理，落成显式参数（如 `--clean-legacy-temp`，只删 mtime 早于 N 天）或在 `testing.md` 记一行手工命令；本次不追溯。

🟢 **HG-SEC-218 — 仓内并存两套 argv 约定，存在静默取错的远端风险**

`baseline.py` 现统一 `--flag=value`；而 `tests/test_sync_videos.py:40-41` 的假 `html-gen` 桩按 `args.index('--github-url') + 1` 取值。若将来 `scripts/sync-videos.py` 也改用 `=` 形式（合理演进），该桩会**静默取到 `None`/错值而不断言失败**。
**建议**：桩内同时支持两式（`next((a.split('=',1)[1] for a in args if a.startswith('--github-url=')), None)`），或在桩上注明「调用方必须用两 token 形式」。

**挂账（本轮不处置，双方已约定）**

- **HG-SEC-206**（🟡 既有债）：`test_doc_title_click_copy_path` 在 `-n 4` 下偶发红（固定 `/tmp/test-show-md.*` + 5s toast 等待）。本轮 2 次全量未复现；单独立项（`mkdtemp` + 先等容器再等文案）。
- **HG-SEC-210**（🟢 受保护文件）：`AGENTS.md:6` 458 / `:44` 458·45，实测 466/46；三次审批超时未获同意，按红线未绕过。**偏差已由上轮 7 扩到 8**，建议放行后一次性改为 466 / `466 tests（46 文件）` 并复跑 `wc -c AGENTS.md` ≤ 4,000B。

---

## ⑧ Commit 规范检查

| 口径 | 结论 | 证据 |
|:--|:--|:--|
| 格式 `{type}@{scope}: {subject}` | ✅ 5/5 合规 | `fix@table` / `chore@baseline` / `chore@tests` / `audit@review` / `fix@tests` —— type、scope 全小写 |
| **CL008 subject 全英文** | ✅ **5/5 合规（上轮阻塞项闭合）** | 区间 CJK 命中 0；`hm check commit . --json` 对区间零告警（`cjk_new` 153 全在区间外存量） |
| 编号保留原样 | ✅ | `(HTML-GEN-CL033)` / `(HTML-GEN-CL032)` / `(HTML-GEN-CL024)` / `(HG-SEC-203..212)` 原样 |
| body 质量 | ✅ | 返工笔逐条对号（204/205/207/208/209/211/212 + 明确「206 未修」+ 验收数字），可逐条复算；本报告 §② 即按其声明逐项验 |
| path-scoped / 无夹带 | ✅ | `cc59515` 恰 9 文件，全部本批必要面；`git status` 空；`audit` 笔 3 文件（报告 + review-log + `.review-level.yaml`） |
| 治理口径小差异（🟢 记录） | ⚠️ | `skills-governance/git-commit-template.md:29` 的 bugfix type 写作 `fixed`，本仓与 `hm check` 实际用 `fix`（该模板 L55 亦承认闭环内另有 `fix@` 判据）—— 建议治理侧统一措辞，免后续审计各执一词 |

## ⑨ 命名规范检查

| 面 | 结论 | 证据 |
|:--|:--|:--|
| `hm check naming .` | ✅ **通过** | 仅 `documents/templates.md` / `documents/testing.md` 两条「有 frontmatter 但非标准命名」—— Style B 工作文件（固定名无版本），**存量**，非本批引入 |
| 测试文件命名 | ✅ | 本批新增/改动均 `tests/test_{feature}.py`；`conftest.py` 为 pytest 约定 |
| 脚本命名 | ✅ | `scripts/baseline.py`（`{purpose}.ext`，未新增脚本） |
| 文档命名 | ✅ | 本报告 `next-batch-cl033-032-024-review-v1.1-20261112.md` = `{topic}-review-v{major}.{minor}-{yyyymmdd}.md`，topic 与 v1.0 同源、版本 +0.1 |
| Review-log | ✅ | Style B `review-log.md` 固定名，本轮 append |

---

## ⑩ 评分

```
Base: 100
🔴 HIGH   × 0  →  -0
🟡 MEDIUM × 1  →  -5    (213 新复算判据期望值仍不符实测)
🟢 LOW    × 6  →  -0    (214/215/216/217/218 record + 210 受保护文件挂账)
得分: 95 / 100 → Rating: A
```

| 维度 | 权重 | 得分 | 依据 |
|:--|--:|--:|:--|
| 合理性 | 35% | 34 | 7 项返工全部对上根因（数字→可复算、缺省→去耦合、豁免→可枚举、清理→只删自有目录）；扣 1 因 strict 开关无落点（纸面规约） |
| 严格性 | 40% | 37 | 22/24 声称逐字可复现、变异 3 红 2 豁免逐例点名、断言零削弱、挂账诚实；扣 3 因「自证数字不符」同类缺陷第 3 次复发（213） |
| 可维护性 | 20% | 19 | 单点收敛（conftest 单分支 / 判据单文件 / 作业表单源）延续；扣 1 因 `--keep-temp` 不可发现 + 无 try/finally（215） |
| 跨 profile | 5% | 5 | 全部判据给出可复制命令与期望值，review/ops/dev 三方均可独立复算 |

## ⑪ 结论

✅ **PASS — 95/100（A）**

**判定依据**
1. **上轮唯一阻塞项（HG-SEC-203 · CL008）已闭合**：区间 6/6 subject 全英文，且三口径（tree / patch-id / body-md5）证明 reword 只动了 subject 行 —— 内容零变化、未 push、无 force。
2. **7 项返工实质落地**：204①/205/207/208/209/211/212 全部经独立复算闭合（含 3 例变异证明守卫非恒真、2 例探针证明 skip/error/argv 三处行为真的换了）；204② 换了形式但期望值仍错 ⇒ 转 213（🟡 建议修，非阻断）。
3. **挂账如实**：206（偶发红）与 210（AGENTS.md 计数，受保护文件待审批）均在本笔声明里明确「未修」并给出归属，未以「已修复」搪塞。

**处置建议（按序）**
1. **建议修（一行/两行，任选 213 的 ① 或 ②）**：testing.md 判据期望值 → 与实测对齐，或改为只引用 `test_selenium_infra.py::test_01_*`（避免第三次复制命令）。
2. **另批**：214（豁免集合上界）/ 215（keep-temp 打印 + try/finally）/ 216（大小写 + 严格跑法入文档）/ 217（清理若需常态化则成文）/ 218（桩兼容两式）。
3. **仍需审批**：210 —— 放行后一次改 `AGENTS.md:6`/`:44` 为 466 / 466·46 文件。
4. **治理面（跨批）**：`cjk_new`=153 的历史存量仍需一次裁定（豁免登记 or 仅前向执行），否则每轮都要记同一句话。

**推送状态**：本轮**未 push**（`git rev-list --count github/main..HEAD` = 6，本轮审计笔提交后 = 7）。放行条件建议：213 一行修完成后一并推送（含本报告笔）。若要跳过 213 直接推，回「推送」即可。

---

## ⑫ 待确认清单

| □ | 项 | 类别 | 推荐 |
|:-:|:--|:--|:--|
| ☐ | 213：testing.md 判据期望值 0→实测 2（或改为只引用用例） | 严格性 🟡 | **改判据为「0 处非标注命中」+ 措辞去双 token**（根治：不再复制数字） |
| ☐ | 214：是否给 `noqa` 豁免加上界断言 | 安全性 🟢 | 加 `(relpath, lineno)` 集合断言 == `{test_selenium_infra.py:41}` |
| ☐ | 215：`--keep-temp` 是否打印目录 + `try/finally` | 可维护性 🟢 | 两行都加 |
| ☐ | 216：`CHROMEDRIVER_REQUIRED` 是否 `.lower()` + 严格跑法入 testing.md | 安全性 🟢 | 建议加（无 CI 时这是唯一可执行护栏） |
| ☐ | 206：偶发红用例何时单独立项 | 严格性 🟡（既有债） | 与本批解耦，独立小批（`mkdtemp` + 等待策略） |
| ☐ | 210：AGENTS.md `:6`/`:44` → 466/46 审批 | 治理 🟢（受保护文件） | 放行后一次改 + 复跑 `wc -c` ≤ 4,000B |
| ☐ | `cjk_new`=153 存量裁定（豁免 vs 前向） | 治理（跨批） | 前向执行 + 登记豁免边界日期 |
