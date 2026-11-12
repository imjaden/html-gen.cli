---
title: next-batch CL033/CL032/CL024 — review报告 v1.0
topic: next-batch-cl033-032-024
type: review
version: 1.0
date: 2026-11-12
author: hermes-v0.23.1(2026.9.24)
profile: review
tags: [review, html-gen, split-grid, baseline-gate, chromedriver]
loop: HTML-GEN-CL033
---

# next-batch CL033/CL032/CL024 — review报告 v1.0

> 日期: 2026-11-12 09:20 · 角色: review（1A 口径：独立复算，禁采信转述）
> 受审区间: `github/main..HEAD` 3 笔业务提交（**非** HEAD^..HEAD 单笔；按用户订正口径执行）
> - `70f714b` fix@table: splitGrid 行内 span:"full" 只吃剩余轨（HTML-GEN-CL033）— 13 文件
> - `4225011` chore@baseline: --verify 覆盖面扩到全量可重建产物（HTML-GEN-CL032）— 15 文件
> - `6bb5f6d` chore@tests: chromedriver 路径 env 化（HTML-GEN-CL024）— 36 文件
> 区间派生物（**不在受审集合**，只核未改代码）: `4e7574f` docs@handoff — `documents/handoff/handoff-html-gen.cli-ops.md` 单文件 +36/-36，零代码/零产物
> `loop:` 取主序 CL033；本批实跨三闭环（CL033/CL032/CL024），逐闭环证据见 §数据验证
> HEAD=`6bb5f6d` · `git status` 干净 · 3 笔合计 56 unique 文件（+627/-186）
> **结论: ⚠️ CONDITIONAL PASS — 80/100（B）· 1 🔴 0 / 4 🟡 / 6 🟢 · 阻塞项唯一 = HG-SEC-203（CL008 中文 subject）**

---

## 数据验证

| 验证项 | 方法 | 结果 |
|:--|:--|:--|
| 受审区间构成 | `git log --oneline origin/main..HEAD` + 逐笔 `git show --stat` | 4 笔：3 业务 + 1 handoff 派生；`rev-list --count origin/main..HEAD`=4 / `HEAD..origin/main`=0 ✅ 与订正口径一致 |
| 派生物未改代码 | `git show --stat 4e7574f` | 仅 `documents/handoff/handoff-html-gen.cli-ops.md`（36+/36-），无 `*.py`/`*.html`/`data/**` ✅ |
| 全量回归（权威 `-n 4`） | `/usr/bin/python3 -m pytest tests/ -q -n 4` ×3 | run1 **464 passed / 1 failed**（`test_templates.py::TestDocShowMd::test_doc_title_click_copy_path`）；run2/run3 **465 passed**（59.80s / 60.81s）⇒ 计数 465 成立，红点为偶发（见 HG-SEC-206） |
| 红点归属 | 单跑该用例 `-n 0` | 1 passed（0.49s）⇒ 非本批逻辑破坏；本批对该文件仅 `Service(CHROMEDRIVER)`→`chromedriver_service()` |
| 渲染基线门禁 | `scripts/baseline.py --check` | **基线一致 23/23** ✅（rc=0）；`data/_render-baseline.json` files=23 / verified=True / version=2 |
| 产物与模板同源 | `scripts/baseline.py --verify` | **15 件 current（sha 逐对相等）+ 5 件带理由 skip** ✅；skip 5 项与 `SKIP_PRODUCTS` 逐条对应 |
| 工作树 | `git status --short` | 空 ✅（复算前后两次均空） |
| 硬编码清面（CL024） | `git grep -c "script-miner/cache/chromedriver" 70f714b -- tests/` → 逐文件求和 | 修前 **31 文件 / 32 处**；HEAD `--include=*.py` 口径 **2 处**（`conftest.py:19` 缺省值 + `:3` docstring 示例）✅ |
| 调用点收敛 | `grep -c "from conftest import" / "chromedriver_service()"` | 31 文件导入 / **39 调用点** / **0 模块级调用**（全在 `setUpClass`/方法内 ⇒ SkipTest 语义正确） |
| 「64 个测试文件」可复算性 | 同上三口径（文件/路径出现/`Service(` 出现） | 31 / 32 / 35 —— **64 无任何口径支撑**（见 HG-SEC-204） |
| 文档自检判据复现 | 原文命令 `grep -rn "script-miner/cache/chromedriver" tests/ \| wc -l` | 实测 **5**（2 源码 + 3 `__pycache__/*.pyc` 二进制命中）≠ 文档写的 2（见 HG-SEC-204） |
| 变异测试 M1（CL033 主张） | 把 `else if (cells.length === 1)` 改恒真并跑 `test_split_grid` | **1 failed（test_10_mid_row_full_fills_remainder）/ 12 passed** ✅ 与 commit body 逐字吻合 |
| 变异测试 M2（口径订正主张） | 删 `var style = 'grid-row:'+…`（等价变异） | **13 passed** ✅ 证实「删 grid-row 是等价变异」，`test_01b` 注释与 `templates.md` 的订正措辞成立（未过度声明） |
| 产物 diff 越界面 | `git show 70f714b -- demos/*.html` 逐 hunk 分类 | 5 table demo + demos-index **仅 splitGrid JS 块**；CK033 无其它行 ✅ |
| CL032 重刷 9 页 diff 面 | `git show 4225011 -- demos/<doc>.html` 逐页 | doc 5 页 **仅 meta 字数/阅读时长行**（1,083→1,984 等，与 v3.4 汉字计数口径吻合）；knowledge 4 页 **仅 CL018 `_rxW` width JS 块** ✅ 与「diff 只含预期项」声明一致 |
| 门禁覆盖自证 | 读 `tests/test_baseline_gate.py:150-180`（test_08/09）+ 实跑 | test_08 断言 `demos/*.html ⊆ jobs ∪ SKIP` ∧ `jobs ⊆ SUBSET` ∧ jobs∩SKIP=∅；`SUBSET_LEN` 改为 `import baseline.SUBSET` 现取（不再写死 10）✅ |
| 测试计数三面 | `ls tests/test_*.py \| wc -l` / 逐文件 `grep -c '^    def test_'` | 46 文件 ✅；test_split_grid 13 / test_selenium_infra 3 / test_baseline_gate 9 / test_templates 18 ✅ 与 `documents/testing.md:27` 声明一致 |
| commit 规范工具面 | `hm check commit . --json` | status ok；**本批 3/3 命中 CJK warning**；`cjk_new`=157 / `cjk_legacy`=0 |
| 命名规范工具面 | `hm check naming .` | ✅ 通过（`templates.md`/`testing.md` 两条「非标准命名」为存量工作文件，非本批） |
| 双仓同步态 | `git rev-list --count` 双向 | 领先 4 / 落后 0 ⇒ 区间内 4 笔均未 push，reword 无需 force |

---

## 合理性评估

| # | 判据 | 结论 |
|:--|:--|:--|
| REA-1 | CL033 修法是否消因而非消症 | ✅ 根因是「full 恒写 `1 / -1` 导致与同行兄弟格同占轨道」；改为「唯一格 → `1 / -1`；有兄弟格 → 吃剩余轨」直接消因，且不做隐式换行 ⇒ `--kv-cols`/几何判据语义不变，向后兼容面最小 |
| REA-2 | `take` 上界是否恒 ≥1、是否可能溢出栅格 | ✅ 由 `maxCols ≥ 本行 span 之和` 推得 `take ≥ 1`；且 `colIdx+take+tail ≤ maxCols+1` ⇒ 不产生隐式轨道。`Math.max(1,…)` 为兜底，未掩盖逻辑错误 |
| REA-3 | `skipEmpty` 与 full 的交互是否自洽 | ✅ 先按 `rowValueForCurrent` 过滤再算 tail；全行只剩 full ⇒ 按「唯一格」占满（`cells.length===1` 分支），与注释一致 |
| REA-4 | CL032 覆盖面判定是否闭环 | ✅ `jobs ∪ SKIP` 覆盖 `demos/*.html` 并就「既判定又跳过」反向断言 ⇒ 漏网页面会红；子集项数现取脚本常量，消除双源漂移 |
| REA-5 | SKIP 清单是否每条都有可审理由 | ✅ 5 条理由均可复核（demos-index 就地重建 / 两个手写落地页 / slide-demo 无 md 源 / the-price-you-choose 生成后 rx-patch 注入） |
| REA-6 | CL024 缺省值向后兼容是否成立 | ✅ `os.environ.get('CHROMEDRIVER') or DEFAULT`，缺省仍是历史现值；test_02 用子进程双跑（有/无 env）钉住两点 |
| REA-7 | 缺驱动降级为 skip 是否合理 | ⚠️ 方向合理（缺驱动 ≠ 代码坏），但**无 strict 开关** ⇒ 39 处几何断言可整体静默放水（HG-SEC-205） |

## 严格性评估

| # | 判据 | 结论 |
|:--|:--|:--|
| RIG-1 | 声明与实测是否逐条对齐 | ⚠️ 21 条声明中 19 条逐字可复现；2 条不成立：注释「64 个测试文件」（实测 31）、grep 自检判据「= 2」（实测 5）。二者均为本批**新写入的自证材料**，且与本批 commit body 自身（写 31）自相矛盾（HG-SEC-204） |
| RIG-2 | 用例是否真具备判别力（非恒真） | ✅ 独立变异复算：M1 精确点名 `test_10`（12 passed 保持），M2 全绿 ⇒ 用例集对「修法」敏感、对「等价变异」不误报 |
| RIG-3 | 「等价变异」口径订正是否诚实 | ✅ 主动把原「判别性用例」降级为「守结果不构成 M1 判别力」，并在 `templates.md` 补记；这比保留过度声明更严格 |
| RIG-4 | 测试削弱核查 | ✅ 本批对既有用例仅改 `Service(…)`→`chromedriver_service()` 与 import（-101/+174 中绝大多数为机械替换）；`test_templates.py` 断言逐字未变；`test_baseline_gate` 仅把写死的 `10` 换为 `SUBSET_LEN`（等强度） |
| RIG-5 | 新增守卫是否覆盖自身盲区 | ⚠️ `test_selenium_infra` test_01 只 `glob('*.py')` 顶层、按文件名整免 `conftest.py`，且自身靠字符串拼接规避扫描 ⇒ 自带一条「拼接即豁免」的后门范式（HG-SEC-208） |
| RIG-6 | 计数三面同步 | ✅ README.md:137 / README.zh.md:135 → 465；`documents/testing.md:27` → 46 文件 + 各文件数对齐；AGENTS.md:6/:44 仍 458/45（受保护文件待审批，HG-SEC-210） |
| RIG-7 | 全量回归可复现性 | ⚠️ 3 次复跑 1 次红（Selenium 时序 / 固定 `/tmp` 路径），ops 的「465 passed」为真但不是「恒真」（HG-SEC-206） |

## 安全性评估

| # | 面 | 结论 |
|:--|:--|:--|
| SEC-A | 子进程面（本批新增） | ✅ `scripts/baseline.py` 与 `tests/test_selenium_infra.py` 均 list-form + `capture_output`，`git diff github/main..HEAD -- '*.py'` 对 `shell=True|os.system|eval(|exec(|pickle|verify=False` **命中 0** |
| SEC-B | HTML/CSS 注入面（CL033 新代码） | ✅ `style` 串只拼接 `ri`/`colIdx`/`spanN`/`take` 四处数字；`spanN`/`take` 上游经 `normalizeSpan`（`Number.isInteger`）→ `plainSpan`（`Math.floor` + 上限 6），`take` 由 `Math.max(1, …)` 夹紧 ⇒ 不存在「数据 → CSS 值」字符串通道；`label` 走 `escapeHtml`、值走 `splitValueHtml`（`escape:false` 是既有列级显式豁免） |
| SEC-C | 凭据/密钥 | ✅ 区间 diff 无 token/key/password 形态新增；`DEFAULT_CHROMEDRIVER` 为本地路径，非凭据 |
| SEC-D | 供应链 / 零依赖铁律 | ✅ 无新增第三方包、无 CDN、无远程字体；重刷产物 diff 中 `<script src=http*>` / `<link href="http*>` / `<img src="http*>` 新增 **0**；`conftest.py` 仅用 `os`/`unittest`/`pathlib` + 既有 selenium |
| SEC-E | 信任边界变化（env 化） | ⚠️ `CHROMEDRIVER` 可指向任意可执行文件并被 `Service()` 启动 —— 本地测试运行器、无权限边界跨越，属常规做法；但「存在即用」（只判 `is_file()`）不校验可执行/版本，属 🟢 记录 |
| SEC-F | 门禁完整性（本批核心风险） | ⚠️ 缺驱动即 `SkipTest` ⇒ 39 处几何/交互断言可整体静默变绿；这是本批**唯一实质削弱门禁**的机制变化（HG-SEC-205） |
| SEC-G | 生成器契约面 | ✅ CL032 的 `--title/--subtitle/--welcome/--github-url` 全从产物 DOM 回收，argv 独立传参无 shell 面；值以 `-` 开头时 argparse 报「expected one argument」⇒ **fail-closed（红）而非静默放过**，方向安全 |

---

## 安全事项

🟡 **HG-SEC-203 — 3/3 commit subject 含中文，违反 CL008 新笔硬约束（本批唯一阻塞项）**

`hm check commit . --json` → `cjk_new`=157 / `cjk_legacy`=0，本批 `70f714b`/`4225011`/`6bb5f6d` 全部命中。
治理裁定链：`skills-governance/git-commit-template.md` L22 + `hermes-skills-governance-handbook` §5（存量/新笔以 **2026-08-27** 为界，本批 2026-11-12 属新笔）+ `hm-loop-handbook` §9.3「违反 → 审计 CONDITIONAL」。
先例同判：`documents/archive/reviews-20260830/loop-status-taskboard-impl-audit-v1.0-20260827.md`（4 笔中文 subject → 1 🟡 -5 → CONDITIONAL PASS 95，reword 后尾项复核）。
**修复建议:** 3 笔均未 push（`HEAD..origin/main`=0），`git rebase -i 4e7574f` reword 为英文 subject，无需 force：
`fix@table: splitGrid inline span:"full" fills remaining tracks only (HTML-GEN-CL033)` /
`chore@baseline: --verify covers all rebuildable products (HTML-GEN-CL032)` /
`chore@tests: chromedriver path via CHROMEDRIVER env (HTML-GEN-CL024)`（编号/缩写/`--flag` 原样保留）。
**系统面附注（另批决策）:** 157 笔 `cjk_new` 说明历史评审对该判据**系统性漏检**（近 200 笔窗口内 0 次记 CONDITIONAL）。其中已 push 者受「不改写已推历史」红线约束不可 reword ⇒ 需治理裁定二选一：① 对 `<某日` 已推笔登记豁免；② 只前向执行。

🟡 **HG-SEC-204 — 本批新增的「自证材料」有 2 处与实测不符（自相矛盾）**

① `tests/conftest.py:4` 与 `:10`、`tests/test_selenium_infra.py:6` 写「64 个测试文件」/「64 个文件各自抛 WebDriverException」；实测修前 **31 文件 / 32 处路径 / 35 处 `Service(`**，且本批 commit body 自己写的是「31 个测试文件」—— 同一批内两种数字。
② `documents/testing.md:28`（CL024 新增段）与 commit body 的复算判据 `grep -rn "script-miner/cache/chromedriver" tests/ | wc -l == 2` 实测 **5**（缺 `--include=*.py`，`tests/__pycache__/*.pyc` 3 个二进制命中；`hm check pycache` 报 48 项陈旧 pyc 属环境常态）。
**修复建议:** ① 三处 `64` → `31`（或删数字只留「跨 31 个测试文件」）；② 判据补 `--include=*.py` 并注明「期望 2（均在 conftest.py）」。二者均为注释/文档，零行为影响，可与 203 的 reword 同批落地。

🟡 **HG-SEC-205 — 缺 chromedriver 即静默 skip，门禁可无声放水（无 strict 开关）**

`conftest.py:31-37` 在二进制缺失时抛 `unittest.SkipTest`，覆盖 **39 处** selenium 断言（几何坐标/交互/剪贴板等本仓核心判据）。当前无任何「缺驱动必须红」的开关，也无 CI 侧 `skipped==0` 断言 ⇒ 换机/CI 未装驱动时全量仍显示「passed」。
**修复建议:** 增 `CHROMEDRIVER_REQUIRED=1`（缺失时抛 `RuntimeError` 而非 SkipTest），并在 `documents/testing.md` 的权威命令旁注明「CI 必须置 1」；或不引入开关，改在 CI 里断言 `-rs` 输出无 `SKIP ... chromedriver`。

🟡 **HG-SEC-206 — `test_doc_title_click_copy_path` 在 `-n 4` 下偶发红（既有债，本批暴露）**

3 次全量复跑 1 次红（run1），单独 `-n 0` 恒绿。用例本身：固定 `/tmp/test-show-md.{md,html}` + 5s `WebDriverWait` 等 toast 文案（`tests/test_templates.py:254-257, 300-316`）。本批对该文件只换了 Service 来源，**不是引入方**；但「465 passed」的可复现性由此打折。
**修复建议:** 单独立项：输出路径改 `tempfile.mkdtemp()`（消除跨会话/多仓 `/tmp` 撞名），toast 等待前先等 `.doc-toast` 容器就位并放宽超时；若为 CI，加 `--reruns 1 --reruns-delay 1`。

🟢 **HG-SEC-207 — `DEFAULT_CHROMEDRIVER` 仍硬编码本机用户名绝对路径**

`tests/conftest.py:19` = `/Users/jadenli/CodeSpace/script-miner/cache/chromedriver/chromedriver`。CL024 的目标是去机器耦合，实际做到「env 可覆盖」但缺省值仍绑死用户名（他人机器上表现为 skip 而非可跑）。
建议：`os.path.join(os.path.expanduser('~'), 'CodeSpace/script-miner/cache/chromedriver/chromedriver')`；同步改 `tests/test_selenium_infra.py:18` 的 `DEFAULT` 期望值（现为拼接常量，改动面 2 行）。

🟢 **HG-SEC-208 — test_01 守卫扫描面为顶层非递归，且自带「拼接即豁免」范式**

`test_selenium_infra.py:24` `TESTS.glob('*.py')` 只覆盖 `tests/` 顶层；`conftest.py` 按文件名整免（其缺省值另由 test_02 钉住，尚可接受），但「字符串拼接规避扫描」一旦被后续笔效仿即失效。
建议：`TESTS.rglob('*.py')`；豁免改为「只允许 conftest.py 出现该路径且恰好 1 次」。

🟢 **HG-SEC-209 — `tests/test_templates.py:209` 遗留未使用的 `Service` 局部导入**

commit body 称「顺带清掉因此不再使用的 `Service` 导入」，实际 `test_sidebar_sticky` 内仍有一行 `from selenium.webdriver.chrome.service import Service`，而该函数已改用 `chromedriver_service()`。零行为影响；建议删除以与声明一致（`grep -rn "chrome.service import Service" tests/` 应仅剩 `conftest.py:16`）。

🟢 **HG-SEC-210 — AGENTS.md 计数停在 458 / 45，且 README 反向把它指为权威（待补审批）**

`AGENTS.md:6`（期望 458 passed）/ `:44`（458 tests，45 文件）与实测 465/46 不符；`README.md:137` / `README.zh.md:135` 均写「465 tests, see AGENTS.md for the authoritative count」⇒ 权威指针指向旧值。AGENTS.md 为受保护指令文件，本会话两次审批超时未获同意，按红线**未绕过**（不属本批缺陷，按用户口径仅记 🟢）。
建议：审批放行后一次改 `:6` 465 / `:44` 465 tests（46 文件），并复跑 `wc -c AGENTS.md` ≤ 4,000B。

🟢 **HG-SEC-211 — splitGrid `take` 的「剩余轨」以跨行 `maxCols` 计，文档措辞未点明**

`layout-table.html:1496` `take = maxCols - colIdx + 1 - tail`，`maxCols` 是**全行 span 之和的最大值**（同文件 :1457-1465）。故「行 2 = [[a],[b,full]]」时 full 会填到 `maxCols` 而非「本行 span 之和」。行为上是「填满整行」，与视觉预期相符；但 `documents/templates.md:57` 写「只吃本行剩余轨」，未点明基准是 `maxCols`，二次维护时易误判。
建议：该句补「（剩余轨 = 到 `--kv-cols`/`maxCols` 为止；`maxCols` 取各行 span 之和的最大值）」。

🟢 **HG-SEC-212 — `--verify` 临时目录不清理 / 回收值以独立 argv 传参**

`scripts/baseline.py:229` `mkdtemp(prefix='baseline-verify-')` 全程无 `shutil.rmtree` ⇒ 每次 verify 遗留 15 个 HTML（当前 /tmp 已有多次副本）；`build_jobs` 把回收标题以 `['--title', value]` 传参，值以 `-` 开头会被 argparse 拒绝（fail-closed，非静默，方向安全）。
建议：`--verify` 收尾 `shutil.rmtree(tmpdir, ignore_errors=True)`（保留 `--keep-temp` 供排查）；argv 改 `f'--title={value}'` 形式彻底消除前缀歧义。

---

## 评分

```
Base: 100
🔴 HIGH   × 0  →  -0
🟡 MEDIUM × 4  → -20   (203 CL008 中文 subject / 204 自证材料与实测不符 / 205 缺驱动静默 skip / 206 全量偶发红)
🟢 LOW    × 6  →  -0   (207..212 record only)
得分: 80 / 100 → Rating: B
```

| 维度 | 权重 | 得分 | 依据 |
|:--|--:|--:|:--|
| 合理性 | 35% | 33 | 三笔修法均消因、向后兼容面最小；扣分因「skip 无 strict 开关」使 CL024 的降级策略缺护栏 |
| 严格性 | 40% | 33 | 声明 19/21 逐字可复现、变异 M1/M2 独立点名、等价变异口径主动订正；扣分因本批新写注释 2 处数字与自己的 commit body 矛盾 + 3 次复跑 1 次红 |
| 可维护性 | 20% | 18 | 单点收敛（conftest / 作业表 / 子集常量现取）显著降低双源漂移；扣分因 test_01 非递归 + 拼接豁免范式 + verify 临时目录无回收 |
| 跨 profile | 5% | 5 | review/ops/dev 事实链一次性可复算（命令全给），无「只有作者能跑」的判据 |

---

## 结论

⚠️ **CONDITIONAL PASS — 80/100（B）**

**判定依据（两条独立成立）:**
1. **CL008 强制项**：本批 3/3 属「新笔」（≥2026-08-27）且 subject 含中文，按 handbook §5 + `hm-loop-handbook` §9.3「违反 → 审计 CONDITIONAL」，不计分也必须记 CONDITIONAL。
2. **B 档**（70–84）：4 🟡 × -5 = 80。

**功能/技术面实质结论（全部经独立复算，无一条采信转述）:**
- CL033 修法**成立且消因**：`1 / -1` 恒写 → 「唯一格占满 / 有兄弟格吃剩余轨」，不做隐式换行；变异 M1 精确点名 `test_10`（12 例保持绿），M2 证实「删 grid-row 是等价变异」的口径订正未过度声明；产物 6 件 diff 仅 JS 块，`--kv-cols`/几何判据语义未变。
- CL032 覆盖面**真扩容**：`--verify` 15 件 sha 逐对相等 + 5 件带理由 skip；`--check` 23/23；test_08/09 把「漏网页」与「回收标题缺失」变成红；重刷 9 页 diff 仅元信息/CL018 JS 块（并实证了 9 页此前确有模板漂移 —— 该门禁缺口是真实存在的）。
- CL024 **清面彻底**：31 文件/32 处 → 2 处（均在 conftest），39 调用点 0 模块级，缺驱动降级为 SkipTest 带路径与 env 提示；代价是门禁可静默放水（205 已登记修复路径）。

**处置建议（按序）:**
1. **必须**：reword 3 笔 subject 为英文（未 push，`rebase -i` 无 force），完成后触发**尾项复核**（笔数从 4 变 4，hash 全变）。
2. **建议同批**：204（64 → 31；grep 判据补 `--include=*.py`）、209（删残留 import）—— 都是一行级改动，与 reword 同一次 rebase 顺手完成最省事。
3. **另批**：205（strict 开关）、206（偶发红用例加固）、207/208/210/211/212。
4. **治理面**：`cjk_new`=157 需一次裁定（豁免登记 or 前向执行），否则每轮评审都要重复记同一个 CONDITIONAL。

**未 push、未改任何代码；本报告与 review-log / .review-level.yaml 已本地提交，等复审放行后再 push。**

---

## 待确认清单

| □ | 项 | 类别 |
|:-:|:--|:--|
| ☐ | 3 笔 subject reword 为英文（203）— 阻塞放行 | 治理 🟡 |
| ☐ | `64` → `31`（3 处）+ grep 判据补 `--include=*.py`（204） | 严格性 🟡 |
| ☐ | 是否加 `CHROMEDRIVER_REQUIRED=1` 严格开关（205） | 安全性 🟡 |
| ☐ | 偶发红用例单独立项 or 本批随手加固（206） | 严格性 🟡 |
| ☐ | `DEFAULT_CHROMEDRIVER` 改 `expanduser` 组合（207） | 安全性 🟢 |
| ☐ | `cjk_new`=157 的系统性裁定：豁免登记 vs 前向执行 | 治理（跨批） |
| ☐ | AGENTS.md `:6`/`:44` 计数 465/46 补审批（210） | 治理 🟢（受保护文件） |
