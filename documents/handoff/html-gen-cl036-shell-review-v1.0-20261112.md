---
title: HTML-GEN-CL036 table 模板壳变更（4 笔） — review报告 v1.0
topic: html-gen-cl036-shell
type: review
version: 1.0
date: 2026-11-12
author: Security Reviewer (review profile)
profile: review
tags: [review, html-gen, table-template, cross-repo, handoff, design-review]
loop: HTML-GEN-CL036
tracking: HG-SEC-226..232
---

[HTML-GEN-CL036] [2/6] 设计评审 @ 2026-11-12 18:09:42

# HTML-GEN-CL036 table 模板壳变更（4 笔） — review报告 v1.0

> 日期: 2026-11-12 · 闭环: **HTML-GEN-CL036** · 角色: review（1A 口径：独立复算，不采信转述）
> 受审区间: `github/main..HEAD` **4 笔**（订正口径，覆盖会话开场的「聚焦 HEAD 1 笔」）：`b0f4b4f` feat@demos(slimdown) / `8ab6754` docs@solutions(方案稿) / `af6994f` feat@table(主体) / `ece6b5d` docs@handoff(去件)
> 基线: `git status --short` 空 · ahead 4 / behind 0 · HEAD=`ece6b5d`
> **结论: ⚠️ CONDITIONAL PASS — 88/100 · 1 🔴 / 6 🟡 / 4 🟢**
> 🔴 只有 1 条且为**单行可修**（跨仓去件引用了失效 sha），代码与产物本身无缺陷。

---

## ① 复算判据（逐条独立重跑，命令可复跑）

| # | 主张 | 复跑命令 | 实测 | 判定 |
|:--|:--|:--|:--|:--|
| 1 | 472 passed / 47 文件 | `python3 -m pytest tests/ -q -n 4`（绝对路径 `/usr/bin/python3`） | `472 passed, 5 warnings in 65.67s`；`ls tests/test_*.py \| wc -l` = **47** | ✅ |
| 2 | 基线 23/23 | `python3 scripts/baseline.py --check` | `基线一致: 23/23` | ✅ |
| 3 | D11 产物戳 == `template_stamps.table` | `./html-gen.py help table --json` + `shasum -a 256 layout-table.html` | 契约 `html-gen v3.4+tpl204aeb64`；产物 `name="generator" content="html-gen v3.4+tpl204aeb64"`；模板 sha256 前 8 = `204aeb64` | ✅ 三向一致 |
| 4 | D10 宽松 rc0 + 令牌 | `table -d bad2.json`（`options.nope`） | rc 0，stderr `WARN_UNKNOWN_KEY 未知选项: nope (options)`，stdout 无令牌 | ✅ |
| 5 | D10 `--strict` exit 2 | 同上 `--strict` | rc **2** + `❌ --strict: 拒绝未知配置键 1 个` | ✅ |
| 6 | `--quiet` 不吞告警 | 同上 `--quiet` | rc 0，stderr 仍有 `WARN_UNKNOWN_KEY`（stdout 仅 `✅ 已生成`） | ✅ |
| 7 | 跨仓兼容（只读实调对方库） | 生成页 → `web_console_lib.normalize_skeleton()`（输出仅写 scratch） | 不抛错；`id="ratioBtn"/"colToggleBtn"` 已移入 `.tabs-row`、`.table-header` 内已无二者；`share` 仍在 header；`<div class="tabs-row">` 全文命中 **1** 次 | ✅ 硬约束成立 |
| 8 | S1 分享按钮落位 | 读 `layout-table.html:296-320` | `.table-header` 内顺序 `#statTotal` → `<!--HOME_LINK--><!--SHARE_BUTTON-->` → `.flex-1`；`html-gen.py:119-120` 为 `🔗` + `title/aria-label="拷贝含当前视图的分享链接"` | ✅ |
| 9 | S2 字号收口 | 读 CSS | `:root{--table-fs:0.82rem}`(`:104`) / `.dense 0.7rem`(`:162`) / `.comfortable 0.94rem`(`:165`)；`th`(`:107`)×0.88、`cell-pill`/`video-pill`(`:50,54`)×0.86、`stat-pill`(`:41`)×0.8 | ✅ |
| 10 | 安全面（区间 diff 静态扫） | `git diff github/main..HEAD -- '*.py' '*.sh' \| grep -E 'shell=True\|os.system\|eval\(\|exec\(\|pickle\|verify=False'` | **0 命中**；新增外链仅 favicon（19/19 demos 既有同款）；`?density=` 走白名单(`:1902`)、`q` 仅 `.value` 赋值(`:1898`) | ✅ 无新增攻击面 |

## ② 发现项

### 🔴 必须修复（1）

**HG-SEC-226 — 跨仓去件引用了「本批实际未落地」的失效 sha `b217461`**

`documents/handoff/20261112-to-hermes-manager-cl036-shell-change.md:10` 写「`html-gen` v3.4 模板，commit `b217461`」。
实测：`b217461` 是 `af6994f` 的 **amend 前草稿**（同 subject、同 18:01 时间戳），`git cat-file -t` 可查到对象但 **不在任何 ref 上**（`git branch -a --contains b217461` 空、`git log --all` 无命中、`git fsck` 归 unreachable），因此：
- hermes-manager 侧 `git show b217461` **必然失败**（该对象根本不进任何 clone）；
- 更严重：两笔 **tree 不同**（`git diff b217461 af6994f --stat` → 9 文件 +44/−35），草稿版 `layout-table.html` 恰是 **`<div class="tabs-row" id="tabsRow">`**——即本件 S1b 行明令禁止的写法（`af6994f` 才改成逐字 `<div class="tabs-row">` 并补了 `tests/test_cl036_table_density_actions.py:100` 断言）。
⇒ 文档与它自引的对象**自相矛盾**：读者按 sha 取到的树会让 `normalize_skeleton()` 抛 `RuntimeError`（`web_console_lib.py:862 _only_hit` 要求命中恰 1 次）。

**修复建议:** 改为引用 `af6994f`，并加一行事实注记「该笔尚未推送（本地 ahead 4），重生成前请先确认本仓已含此笔或由本仓推送后复取 sha」。若最终会 amend，则写「以 `git log -1 -- layout-table.html` 为准」，避免二次失效。

### 🟡 建议修复（6）

**HG-SEC-227 — 检查点 ① 的验收判据被过度概括，「单视图页」会读出假失败**

`:36-40` 断言「重生成后应满足：`.tabs-actions` 内只有 `▦`/`⚙` 两个控件，`.tabs-row` 因有子节点而**不折叠**」。
实测归属：`normalize_skeleton()` 只在 `gen_split()` 里调用（`web_console_lib.py:770`），而 shortcuts 页走 `gen_page()`（`web_console_lib.py:293-307`，**不调 normalize**，其 docstring 亦写明「console 三页改走 gen_split」）。shortcuts 页 `const TABS = [];`（`web/shortcuts/index.html:644`）⇒ 重生成后 `.tabs-actions` 为空、`.tabs-row` **会**折叠——而这正是本件 §4 视觉验收 1 想要的「不再有空白操作行」。
另 `:40` 的括注「syncTabsRow 只看 `.tabs-row` 是否存在 `.tabs-actions` 子节点」与实现不符：`layout-table.html:505-517` 判的是 `#tabsBar` 与 `.tabs-actions` **两者皆空**才折叠。

**修复建议:** 检查点 ① 拆成两条：「gen_split 三页（cron/memory/session）→ `.tabs-actions` 子节点 2、不折叠」「gen_page 页（shortcuts）→ `.tabs-actions` 空、`TABS=[]` 时折叠为 `display:none`」；括注改为「两者皆空才折叠」。

**HG-SEC-228 — 「8 个 console 页需重生成」范围不准；④ 的 drift 巡检会永久误报**

实测 `web/*/index.html` 八页构成：`cron` / `memory` / `session` / `shortcuts` 各含 `.ratio-wrap`+`.flex-1`+`.tabs-actions`（= table 模板产物，**4 页**）；`knowledge` 为 knowledge 模板（无 `.ratio-wrap`/`.tabs-actions`）；`feishu`、`todo` 无 `--cobalt` 变量（非 html-gen 产物）；`1acl` 有 `.tabs-row`/`.tabs-actions` 但无 `.ratio-wrap`/`.flex-1`（**自建壳**，不在 `gen_page`/`gen_split` 链上）。
后果：(a) `:60` 的巡检定式 `grep -o 'content="html-gen v[^"]*"' web/*/index.html` 对 feishu/todo/knowledge/1acl **永远无戳**，把「该重生成」变成常态噪声；(b) 1acl 与本批同款视觉缺陷但未被点名（本件只点名 daily-checker 的 fork），重生成清单漏项。
另 §2 只给了 shortcuts 一个入口脚本名，实测另有 `scripts/web-console/{cron,memory,sessions}-web-refresh.py`。

**修复建议:** 受影响的 4 页 + 4 个入口脚本列全；§3 ④ 巡检式改为只扫这 4 页（或 `grep -L` 反向排除无戳页并注明原因）；§5 边界补一句 1acl 自建壳的处置。

**HG-SEC-229 — 去件缺 frontmatter，文件名不合 `{topic}-{type}-v{major}.{minor}-{yyyymmdd}`**

`documents/handoff/` 9 件中 **仅本件零 frontmatter**（同目录 `cl034-showmd-fixture-review-v1.0-20261112.md`、`next-batch-…-v1.1-20261112.md` 均含 title/topic/type/version/date/author；其余 5 件至少 title+date）。命名亦为 `20261112-to-hermes-manager-cl036-shell-change.md`，与 `skills-governance/document-frontmatter.md` §1「`{topic}-{type}-v{major}.{minor}-{yyyymmdd}.md`」不一致——无版本号导致后续变更只能新增文件、无法追踪版本。

**修复建议:** 补 frontmatter（`topic: html-gen-cl036-shell / type: handoff / version: 1.0 / date / author`），保留现文件名但补 `-v1.0-20261112` 后缀（若改档名须同步 `review-log`/回执引用）。

**HG-SEC-230 — `WARN_UNKNOWN_KEY` / `--strict` 的覆盖面被表述为「治静默漂移」，实际只覆盖 3 类键**

`html-gen.py:716-760` 校验范围仅：`columns[]` 属性名、`columns[].type` 取值、`options` 顶层键、`options.feedback` 子键（docstring 明示 `data[]` 行内字段不校验）。
实测顶层拼错**全静默**：`{"option":{"density":"compact"}}`（少一个 s）→ 宽松 rc 0 **无告警**、`--strict` 仍 **rc 0**（无令牌）。而 hermes-manager 的 payload 正是 `{title, subtitle, columns, data, tabs, options, output}` 这层最容易拼错。
检查点 ② 把它当作「键名拼错 100% 静默」的解，接收方会据此认为门禁已闭合。

**修复建议:** 去件补一行边界（「仅 `columns`/`options`/`options.feedback` 内的键受检，顶层 `options`↔`option`、`tabs`↔`tab` 一类拼写不在覆盖内」）；本仓另批考虑把顶层已知键集合纳入 `_contract_keys`（新增 1 个契约维度，非本批阻塞）。

**HG-SEC-231 — `b0f4b4f` 无闭环编号，跨仓/闭环追溯断链**

近 40 笔中 36 笔带 `CL{NNN}`；本批 `8ab6754`/`af6994f`/`ece6b5d` 均带 `HTML-GEN-CL036`，唯 `b0f4b4f feat@demos: add slimdown case with share link and PNG export` 无编号。该笔新增 17 文件 5,823 行（含新脚本 + 双数据源 + 三页产物），在 `hm loop artifacts` / draft 台账里查不到归属（`cache/draft/TODO-20261109.md:24` 只登记 CL036）。

**修复建议:** 后续同类批次补 `(HTML-GEN-CLnNN)` 后缀；本笔不改写历史，在 `review-log`/draft 补一行归属即可。

**HG-SEC-232 — AGENTS.md 计数权威仍为 466/46，与实测 472/47 及 README 自相矛盾（第 3 次延续）**

`AGENTS.md:6`（期望 466 passed）、`AGENTS.md:44`（466 tests / 46 文件）未随本批更新；`README.md:137`、`README.zh.md:135` 已写 472 并注「权威计数见 AGENTS.md」⇒ **被指向的权威值反而是错的**。实测 472 / 47 文件。
历史同款：HG-SEC-210（458/45 受保护未落）、更早 208 轮同项——这是连续第 3 批「受保护文件审批未落」。
按来件说明**不计入本批缺陷**，此处仅按事实登记为待审批项（见 ③）。

### 🟢 记录（4）

- **HG-SEC-233** `src/html_gen/` 是本机 gitignored 的打包镜像（`.gitignore:37`、`pyproject.toml:27 package-dir`），内容停在 CL030 前（`grep -c 'no-tabs\|stamp_generator\|WARN_UNKNOWN_KEY' src/html_gen/html-gen.py` = 0）。当前 PATH `~/.local/bin/html-gen` 直接 exec 仓根 `html-gen.py`（实测），故无现网影响；但 `pip install .` 会发布旧壳。建议在 `documents/directory-layout.md` 的「双源漂移」段补一句「`src/` 为本地打包镜像，发版前须重同步」。
- **HG-SEC-234** `no-tabs` 折叠是**纯客户端**行为（`layout-table.html:505`），JS 执行前存在一帧空行（CLS 位移），视觉验收「无 JS 错误」不覆盖该帧；影响极小，记录备查。
- **HG-SEC-235** `cmd_table` 的 `open(data_path)`（`html-gen.py:773`）未带 `encoding='utf-8'`，`LC_ALL=C` 下 CJK payload 有 `UnicodeDecodeError` 面（CL012 既有代码，非本批引入）。
- **HG-SEC-236** 三页 slimdown 产物含 `href="https://www.jaden.tech/static/img/favicon.png"` 外链；实测 `demos/*.html` **19/19** 同款（仓内既有约定），不构成 AGENTS.md「自包含单文件」的新违例。`scripts/build-slimdown.py` 仅 stdlib（argparse/json/re/subprocess/sys/pathlib）+ 列表式 `subprocess.run`（无 shell、无注入面），零依赖达标。

## ③ 待审批 / 待确认（不阻塞结论）

1. **AGENTS.md 计数（HG-SEC-232）**：需审批后落 `:6` → 472 passed、`:44` → 472 tests（47 文件）。推荐：下批随任意代码笔一并提交，避免第 4 次延续。
2. **本批是否先修 HG-SEC-226 再推送**：当前 `github/main..HEAD` = 4 笔未推送，去件已引失效 sha。推荐：改 sha（1 行）+ 本报告一起本地提交，推送由「推送」口令放行（沿用本仓前两轮处置）。

## ④ 附录：维度评估

| 维度 | 评分 | 备注 |
|:--|:--|:--|
| 合理性 | 88 | 壳变更方向正确（分享入表头 / 字号变量化 / 去密度门控 / 机器契约三件），且用对方 `normalize_skeleton()` 做了实调兼容验证；扣分在验收判据与范围清单的概括化。 |
| 严格性 | 85 | 复算判据 10/10 可跑通、三向戳一致；扣分在引用失效 sha、`--strict` 覆盖面表述过宽、`b0f4b4f` 无闭环号。 |
| 安全性 | 96 | 区间 diff 零危险模式、零新依赖、`?density=` 白名单、`q` 无 innerHTML 汇；扣分为文档级溯源缺陷（HG-SEC-226）而非运行时漏洞。 |

**综合 88/100 → CONDITIONAL PASS**（1 🔴 单行可修 + 6 🟡 文档级，代码/产物零缺陷）。

## ⑤ 处理

- 本次仅产出报告 + `review-log.md` + `.review-level.yaml` 回顾，本地 path-scoped 提交（`audit@review`），**未推送**。
- HG-SEC-226 修复后建议同批推送；HG-SEC-227/228/230 均为去件定向修订（同一文件，一次改完）。
- HG-SEC-230 的顶层键覆盖扩展、HG-SEC-233 的 `src/` 同步纪律属另批立项，不阻塞本批。
