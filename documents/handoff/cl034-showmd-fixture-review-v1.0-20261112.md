---
title: CL034 TestDocShowMd 夹具隔离 — review报告 v1.0
topic: cl034-showmd-fixture
type: review
version: 1.0
date: 2026-11-12
author: Security Reviewer (review profile)
profile: review
tags: [review, html-gen, test-hygiene, tmp-isolation, selenium, flaky]
loop: HTML-GEN-CL034
tracking: HG-SEC-219..224
---

# CL034 TestDocShowMd 夹具隔离 — review报告 v1.0

> 日期: 2026-11-12 11:10~11:25 · 闭环: **HTML-GEN-CL034**（上轮 HG-SEC-206 挂账项落地笔）· 角色: review（1A 口径：独立复算，禁采信转述）
> 受审区间: **单笔** `a79c2c8` fix@tests: isolate TestDocShowMd fixture from shared /tmp path (HTML-GEN-CL034) — 3 文件 +50/−9（`tests/test_templates.py` +26/−9、`scripts/probe-tmp-pollution.sh` 新增 27、`documents/testing.md` +4）
> 基线: `git status --short` 空 · ahead 1 / behind 0 · HEAD=`a79c2c8`
> **结论: ✅ PASS — 93/100（A−）· 0 🔴 / 2 🟡（建议修，非阻断）/ 5 🟢 record**

---

## ① 受审对象

| 项 | 内容 |
|:--|:--|
| 笔 | `a79c2c8`（不在 `github/main` 历史内，未 push） |
| 来源 | 上轮 PASS 报告 `documents/handoff/next-batch-cl033-032-024-review-v1.1-20261112.md` 的挂账项 **HG-SEC-206**（`test_doc_title_click_copy_path` 在 `-n 4` 下偶发红，明示「单独立项（mkdtemp + 等待策略）」） |
| 性质 | 既有债修复（零新功能、零用例增减、零产物/模板改动） |
| 改动面 | 夹具路径（`/tmp` 固定名 → `tempfile.mkdtemp`）+ 等待策略（3 处 `WebDriverWait` 收紧）+ 新增探针脚本 + testing.md 一条卫生约定 |

---

## ② 数据验证（本轮全部独立执行，非复述）

| 验证项 | 方法 | 结果 |
|:--|:--|:--|
| 探针（病人判据 1） | `bash scripts/probe-tmp-pollution.sh 3` | round1/2/3 各 **2 passed**，`TOTAL_FAILS=0`，rc=0 ✅（0.68/0.57/0.53s） |
| **A/B 反证（独立重建，病人口径的加强版）** | `git worktree add --detach <scratch>/ab-prefix 8c46b71` + 拷入探针 ⇒ 修前夹具（`Path('/tmp/test-show-md.{md,html}')`） | round1/2/3 **各 2 failed**（11.56/11.30/11.44s），`TOTAL_FAILS=3`，rc=1 ⇒ 修前 3/3 复现（病人仅报 2 轮） |
| **对照实验（新做，病人未做）** | 同一修前 worktree，**不起污染进程**单跑 | `2 passed`（0.58s） ⇒ 红了必须归因于「第三者覆盖」，不是旧代码自身坏 ✅ |
| 夹具落点 | `python3 -c "tempfile.mkdtemp(prefix='hg-showmd-')"` | `/var/folders/.../T/hg-showmd-bfvpyeq_` ⇒ 走 `TMPDIR`，与 `/tmp` **不同目录树**（探针物理上碰不到，隔离强于「换个名字」） ✅ |
| 单文件回归 | `pytest tests/test_templates.py -q -n 0` | **18 passed**（2.73s） ✅ |
| 全量回归（权威 `-n 4`） | `/usr/bin/python3 -m pytest tests/ -q -n 4` ×3 | **466 passed / 60.72s**、**466 / 60.49s**、**466 / 61.75s** ⇒ 3/3 绿 ✅ |
| 加压 | `-n 8` | **466 passed / 51.44s** ✅ |
| 渲染基线门禁 | `python3 scripts/baseline.py --check` | **基线一致 23/23**，rc=0 ✅（与 body「零产物/零模板改动」一致） |
| 计数（零变化） | `ls tests/test_*.py \| wc -l` + `grep -rhoE '^\s+def test_'` + `git show a79c2c8 \| grep -cE '^\+ *def test_'` | **46 文件 / 466 用例 / 新增 test 方法 0** ⇒ 「不新增用例」为事实，「466/46」与 AGENTS.md:6/:44 逐字一致 ✅ |
| 残留清理 | `ls -d /tmp/hg-showmd-*`、`ls /tmp/test-show-md.*` | 探针前后均 **0** ✅ |
| 临时目录回收（正常 / 异常路径） | 第 1 轮 `-n 4`×3 + `-n 8` 后查 `TMPDIR/hg-showmd-*`；再以 `CHROMEDRIVER=/nonexistent` 触发 setUpClass 早退 | 正常路径 **0 残留**（4 轮全量后仍 0）✅；缺驱动路径 **每次 +1**（2→3 实测）⇒ 见 HG-SEC-221 |
| **探针判别力缺口（新发现）** | `CHROMEDRIVER=/nonexistent bash scripts/probe-tmp-pollution.sh 1` | `2 skipped` 却 **rc=0 / TOTAL_FAILS=0** ⇒ **假绿**（见 HG-SEC-219） |
| 等待策略事实 | `grep reruns/rerunfailures` pytest.ini·requirements-dev·pyproject；`grep time.sleep` 该文件 | 无 `--reruns`、无新依赖；`time.sleep` 仅剩 `:228/:234`（`[speedup]` 计时用途，**非本笔引入**） ✅ |
| 安全面 | 区间 diff 正则 `shell=True\|os.system\|eval(\|exec(\|pickle\|verify=False\|api_key\|secret\|password\|token` | **0 命中** ✅；新增外链/CDN/远程字体/`<script src`：**0** ✅；零第三方依赖（bash + stdlib） ✅ |
| 精度复核（病人「25 处」） | `grep -ro "/tmp/" tests/ --include=*.py \| wc -l` | **25 次命中**（`test_templates.py` 18、`test_doc_width.py` 2、`test_selenium_infra.py` 2、`test_heading_levels.py` 2、`test_issue_feedback.py` 1）⇒ 总数成立；「19 处在本文件」= 18 处代码 + 本笔新增 docstring 中的 1 处字面提及 ✅（口径差异已核，非缺陷） |

---

## ③ 病人主张逐条裁决

| # | 主张 | 裁决 | 依据 |
|:--|:--|:--|:--|
| 1 | 根因 = 夹具写死共享 `/tmp/test-show-md.{md,html}`，第三者一写即把页面顶掉 ⇒ 整片红（非纯时序玄学） | **✅ 成立（强于原报）** | 修前 worktree + 污染进程：3/3 轮 2 failed；同 worktree 无污染进程：2 passed ⇒ 因果链闭合；失败时延 ≈11.4s = `.doc-body` 5s + toast 5s 双超时，与「页面被替换成 `<p>polluted</p>`」一致 |
| 2 | 修法 = `mkdtemp` 独占目录 + `rmtree`；点击前 `WebDriverWait(10)` 等 `#sidebarTitle`；`_load` 加 `readyState === 'complete'`；toast 5s→10s（仍 `WebDriverWait`，无 sleep、无 `--reruns`） | **✅ 逐字吻合** | `tests/test_templates.py:259-263, 273-275, 277-283, 315-318`；grep 无 reruns/sleep 增量 |
| 3 | 判别力 = 新探针 + A/B（修前 `TOTAL_FAILS=2`，修后 0） | **✅ 成立，但有边界** | 我方 A/B 独立重建：修前 **3/3 红**、修后 **3/3 绿** ⇒ 判别力真实存在。**边界**：① 缺驱动时探针 rc=0 假绿（219）；② 判别力锚定在 `/tmp/test-show-md.html` 这一具体历史路径 —— 若未来回归成 `Path(tempfile.gettempdir())/'test-show-md.html'`（固定名但不在 `/tmp`），探针仍是绿（见 219 修复建议） |

---

## ④ 发现项

### 🔴 必须修复

无。核心修法经独立 A/B 反证坐实，全量 4 轮（含 `-n 8`）零红，无安全面新增风险。

### 🟡 建议修复

**HG-SEC-219 — 探针在「用例被跳过」时假绿，判别力被 skip 通道旁路**

`scripts/probe-tmp-pollution.sh:19-20` 只以 `rc` 判红。实测 `CHROMEDRIVER=/nonexistent bash scripts/probe-tmp-pollution.sh 1` ⇒ `2 skipped, 16 deselected`，却输出 `TOTAL_FAILS=0` 且 rc=0。
即：缺 chromedriver 的机器 / CI 上，本笔赖以立论的判别力载体**恒绿**，与被上一轮判为 🟡 并于 CL024 修掉的 HG-SEC-205（「缺驱动静默 skip，39 处断言整体变绿」）属同一类缺陷的新落点 —— 该机制已有现成开关，探针未接。

**修复建议（一行级）**：`scripts/probe-tmp-pollution.sh:19` 的 pytest 调用前置 `CHROMEDRIVER_REQUIRED=1`，并把判据从「rc==0」升级为「rc==0 **且** 输出含 `2 passed`」（`grep -q '2 passed' /tmp/probe-tmp-pollution-$i.log`）。顺带让判别力脱离具体路径：断言 `TestDocShowMd` 的夹具目录 ≠ `dirname ${POLLUTED_PATH}` 可从 `-s` 输出取，或至少在脚本注释里写明「本探针只证 `/tmp` 固定名已解耦」。

**HG-SEC-220 — testing.md 新规「一律 mkdtemp / 禁写固定 /tmp」与仓内现实自相矛盾，且 commit body 未披露存量**

`documents/testing.md:26-29` 写「夹具输出**一律** `tempfile.mkdtemp()`，禁写固定 `/tmp/<name>`」，实测成立的反例有 **25 处 / 5 文件**（见 ② 精度复核），其中 18 处就在本次被修改的同一文件其它类（`:54-216`）；同时**新探针自己**在 `/tmp/test-show-md.html` 上写删（`scripts/probe-tmp-pollution.sh:15,25`）。
本笔的修法本身没错，问题在规则文本：一条「一律」级铁律落地当天即有 25 处自违例、外加探针这个「故意违例者」，未标注存量与豁免口径 ⇒ 下一位读者按字面 grep 会得到 25 红（与本仓历史上第三次「自证口径与实测不符」同型：HG-SEC-204②/213）。

**修复建议（一行级）**：该条末尾补一句 ——「存量：`tests/` 现有 25 处固定 `/tmp` 名（另批立项清理，勿以此条判红）；`scripts/probe-tmp-pollution.sh` 属故意制造坏环境的探针，豁免本条」。README/testing.md 的用例计数口径无需改动。

### 🟢 记录

- **HG-SEC-221** 清理顺序脆弱（**本轮实测复现，非推测**）：`tearDownClass` 先 `cls.driver.quit()` 再 `rmtree`（`:273-275`），`quit()` 抛异常则临时目录不回收；`setUpClass` 内 `mkdtemp` 之后任一步失败（`run_gen` / `Options` / `webdriver.Chrome`）时 **`tearDownClass` 根本不执行** ⇒ `hg-showmd-*` 泄漏。证据：`CHROMEDRIVER=/nonexistent` 跑 2 次 ⇒ `TMPDIR` 下 2 个残留（各 38,728B html + 42B md，`drwx------`）；复现 1 次 ⇒ +1（2→3）；同环境**正常**跑一次 ⇒ ±0（3→3），且全量 4 轮（含 `-n 8`）后仍为 0 ⇒ 泄漏只在「跳过后 / 早退」路径，正常路径不漏。建议 `cls.addClassCleanup(shutil.rmtree, cls.tmpdir, ignore_errors=True)` 紧跟 `mkdtemp`（py3.8+ 可用，与本仓 py3.9 基线相容），`tearDownClass` 只留 `driver.quit()`。
- **HG-SEC-222** `cls.tmp_md.write_text('# ShowMD 测试…')`（`:261`）未指定 `encoding='utf-8'`，内容为 CJK 字面量；`LC_ALL=C` / `PYTHONUTF8=0` 环境下 `open()` 默认编码为 ASCII ⇒ `UnicodeEncodeError`，用例整片 error（跨平台 CI 脆点）。建议补 `encoding='utf-8'`。
- **HG-SEC-223** 探针自身卫生（developer-local，低风险）：① `:15` `printf … > /tmp/test-show-md.html` 与 `:25` `rm -f` 都是**共享可预测路径**的写/删（CWE-377/59 形态：本机他人预置同名符号链接时会被跟随截断）；② 仅 `set -u`（`:9`），无 `set -e`/`trap`，中断时残留污染进程（上限 4s，影响有限）；③ `kill "$poll"`（`:21`）只杀子 shell，`sleep` 子进程可能成活；④ **实测残留** `/tmp/probe-tmp-pollution-{1,2,3}.log` 共 3 个不回收（探针只在 `:25` 清 html，未清自身日志）—— 与 220 的「探针豁免」应一并写明。建议：起手 `[ -L /tmp/test-show-md.html ] && rm -f`，日志改 `mktemp -d` 或收尾一并 `rm -f /tmp/probe-tmp-pollution-*.log`。
- **HG-SEC-224** CL034 无登记：`hm loop artifacts HTML-GEN-CL034` ⇒ ①报告 ②review-log ③.review-level 全 ❌、④步骤 JSON 0/6。其中 ①②③ 由**本报告提交**自动补齐（落点按 G-2 走 `documents/handoff/`）；④ 属 hermes-manager 侧（跨仓只读，按 AGENTS.md 出转交件）。建议：小修类批若沿用 1A，另仓 draft 登一条 `HTML-GEN-CL034`，否则在收尾时显式裁定「不适用」。
- **HG-SEC-225** 等待阈值 5s→10s（`:279,320`；新增等待在 `:281`/`:316`）是放松而非收紧：headless 本地页面实测整类 0.53~0.68s，10s 余量 15 倍以上，理论上可掩盖真实性能回归。当前取值可接受（原 5s 在 `-n 4` 负载下被证实不足），但若后续再有 flaky，应优先查「为什么慢」而不是继续加阈值。

---

## ⑤ 三规范检查

### 5.1 评审规范（1A 口径 / 治理 §6）

| 项 | 判定 | 依据 |
|:--|:--|:--|
| 独立复算、不采信转述 | ✅ | 全部判据本轮重跑；A/B 用独立 worktree 重建（非 `git stash`），并补对照实验 |
| 根因经反证而非「跑绿即过」 | ✅ | 修前 3/3 红 + 无污染对照 2 passed ⇒ 归因唯一 |
| 严重度分级 + 每项给修法 + 优先级 | ✅ | 0 🔴 / 2 🟡（219 → 220 顺序）/ 5 🟢，均带 `path:line` |
| 不放过模糊点 | ✅ | 病人「25 处」口径差异、「19 处本文件」、「判别力是否绑定具体路径」三处已逐项核并标明边界 |
| 报告落点与命名（G-2） | ✅ | `documents/handoff/cl034-showmd-fixture-review-v1.0-20261112.md`（`documents/reviews/` 自 2026-11-08 起只存档） |
| review-log / .review-level 回写 | ✅ | 本笔同步 append（含 Tracking ID 与 open/closed 状态） |
| 已知边界按事实记账、不越权判 FAIL | ✅ | 零新增用例、25 处存量、探针故意写 `/tmp` 三项均按要求记为事实/另批，未计入阻断 |

### 5.2 commit 规范

| 项 | 判定 | 依据 |
|:--|:--|:--|
| 格式 `type@scope: subject` | ✅ | `fix@tests:`；`fix` 属 1A §D 白名单（`feat@/fix@/test@/refactor@`），亦在 `hm check commit` 近 200 笔实测类型集内（fix×17） |
| type 恰当 | ✅ | 修既有 flaky（测试缺陷修复），非 `test@`（未增删用例）、非 `chore@` |
| scope 恰当 | ✅ | 主改动 `tests/`；附带 `scripts/` 探针与 `documents/testing.md` 属同一病因闭环 |
| subject 全英文（CL008） | ✅ | CJK 0 命中；`hm check commit . --json` 对本笔无 error/warning（`cjk_new`=153 与上轮持平，全在区间外） |
| 编号标记 | ✅ | 尾部 `(HTML-GEN-CL034)` 与前序 200 笔同格式 |
| body | ✅ | 问题/修法/A/B 实证/验收四段齐全，复算命令可执行 |
| subject 长度 | 🟢 | 79 字符（超 72 惯例）；前序 `cc59515` 82 字符已有先例，非新偏差，不单独计 finding |
| path-scoped 提交纪律 | ✅ | `git show --stat` 仅 3 个预期文件，无夹带 |

### 5.3 命名规范

| 项 | 判定 | 依据 |
|:--|:--|:--|
| 新文件 `scripts/probe-tmp-pollution.sh` | ✅ | kebab-case + 用途式命名，与 `scripts/` 现有 `baseline.py` / `tool-table-videos-syncer.py` 同风格；`100755` + shebang 齐备 |
| 扩展名 | 🟢 | `scripts/` 下**首个** `.sh`（其余全是 `.py`）；本探针本质是「起后台进程 + 跑 pytest」，bash 更贴切，但若后续要入 `hm tool scan`/统一入口，需评估改 `.py` |
| 临时目录前缀 `hg-showmd-` | ✅ | 仓名前缀 + 用途，与 `baseline-verify-*` 同构，无碰撞 |
| 文档/类/方法命名 | ✅ | `TestDocShowMd`、`_load`、`test_doc_*` 均未改名；testing.md 新条目沿用既有 `- **加粗结论**（编号）：…` 体例 |
| 报告与结论编号 | ✅ | 报告按 `{topic}-review-v{major}.{minor}-{yyyymmdd}.md`；finding 续号 **HG-SEC-219**（218 已被上轮占用，无重号） |
| 引用一致性 | ✅ | testing.md 引用路径 `bash scripts/probe-tmp-pollution.sh` 与实体逐字一致 |
| 跨仓登记 | 🟢 | CL034 本仓无 draft 条目（见 224） |

---

## ⑥ 维度评估与评分

| 维度 | 评分 | 依据 |
|:--|:--|:--|
| 合理性 | 96 | 根因经「污染 3/3 红 + 无污染对照绿」闭环，不是修到绿为止；修法（独占目录）方向正确且比换名更强 |
| 严格性 | 88 | 判别力真实存在，但探针 skip 通道假绿（219）、规则文本无存量口径（220）；等待阈值放松缺少「何时不该再加」的边界 |
| 安全性 | 95 | 区间 0 注入/0 外部资源/0 新依赖；新增的共享 `/tmp` 写删与清理顺序属低风险卫生项（221/223） |
| 可维护性 | 92 | `path:line` 级注释与 docstring 归因清晰；编码/清理顺序两处脆点（221/222）与 `.sh` 惯例分叉（5.3） |
| **总分** | **93 / 100（A−）** | 判据：PASS ≥ 90 / CONDITIONAL 75–89 / FAIL < 75 |

---

## ⑦ 结论与处理

- **✅ PASS（93/100）** —— HG-SEC-206 **closed**（病因消除，A/B 独立复现修前 3/3 红、修后 3/3 绿 + 对照实验归因唯一）。
- **候选放行**：本笔为单一 fix，未 push（ahead 1）；两枚 🟡 均建议（非阻断）——建议 `219` 一行修后与本笔一并推送，或按「只处理被审的笔」先放行本笔、219/220 另笔。
- **未 push**：本报告 + `review-log.md` + `.review-level.yaml` 仅本地 `audit@review` 提交（沿用本仓前两轮处置：push 由「推送」口令放行）。
- **另批（不阻塞本笔）**：220 的 25 处存量清理立项；221/222/223 一行级卫生修；224 跨仓 draft 登记。

---

## 参考

- 上轮报告：`documents/handoff/next-batch-cl033-032-024-review-v1.1-20261112.md`（HG-SEC-206 立项处）
- 受审笔：`git show a79c2c8`
- 复算脚本：`bash scripts/probe-tmp-pollution.sh 3`；A/B 复建方式：`git worktree add --detach <scratch>/ab-prefix a79c2c8^`
