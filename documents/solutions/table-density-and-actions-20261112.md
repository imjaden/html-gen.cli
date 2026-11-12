# table 模板：密度/字号 + 分享按钮落位 + 跨仓规范覆盖（方案 · 待指示实施）

- 日期：2026-11-12 · 编号：`HTML-GEN-CL036`（本批）· 状态：**方案已定稿，源码零改动**
- 触发：`http://jaden.local:8081/shortcuts/index.html` 目视两个问题（分享按钮独占一行 / 字号行高偏小），
  以及由此引出的「其他仓用 html-gen 模板为何覆盖不到规范」与「prompt 规范/说明文档是否要同步更新」
- 决策口径：用户「**全采推荐**」（D1–D8），实施待下一句指令

---

## 1. 实测事实（证据可复算）

### 1.1 页面归属链（决定改哪边）

```
hermes-manager/scripts/hm-shortcuts-page.py   (yaml 真值表 → payload)
  └── web_console_lib.gen_page()
        ├── run_html_gen()  →  shutil.which("html-gen")  →  ~/.local/bin/html-gen
        │                                                    └── 本仓 html-gen.py (v3.4)
        ├── 注入全局菜单 / 页脚
        └── normalize_skeleton()  →  把 .ratio-wrap / .col-toggle-wrap 从 .table-header
                                      移到 .tabs-row > .tabs-actions（hermes-manager 的 M11 设计）
```

⇒ **视觉壳 = 本仓 `layout-table.html`**（可改）；数据与生成器 = hermes-manager（跨仓只读，出转交件）。
`~/.local/bin/html-gen` 实测指向本仓 `html-gen.py`，改模板后对方重生成即继承。

### 1.2 分享按钮：不是"独占一行"，是 tabs 行退化 + 靠左

| 观测 | 实测值 | 位置 |
|---|---|---|
| `#tabsBar` 子节点数 | **0**（本页单视图，无 tab 条） | `layout-table.html:295` |
| `.table-tabs:empty` | `display:none` | `layout-table.html:13` |
| 分享按钮落点 | `x=16, y=61`（**左侧**，非右上） | 实测 getBoundingClientRect |
| 标题行落点 | `y=107`（与按钮之间空 10px margin） | `.tabs-row{margin-bottom:10px}` `:11` |
| `.tabs-actions` | `display:flex`，**无** `margin-left:auto` | `:14` |

根因：`.table-tabs{flex:1}` 只在有 tab 时把 `.tabs-actions` 顶到右边；tab 条为空 ⇒ `.tabs-actions` 退到行首，
整条 tabs 行只剩一个按钮 ⇒ 观感「独占一行且靠左」。

### 1.3 密度/字号：三档存在，但本页 UI 无入口

| 观测 | 实测值 |
|---|---|
| 当前 `td` | `font-size:12px` / `padding:7px 8px` / `line-height:19.2px` / **行高 35px** |
| 当前 `th` | `font-size:10.4px (0.65rem)` / `padding:6px 8px` |
| 当前 `.stat-pill` | `10.4px (0.65rem)` |
| `.data-table.dense` | `0.7rem` + `2px 8px` |
| `.data-table.comfortable` | `0.82rem` + `10px 12px` |
| 密度入口渲染条件 | `if (tabCount > 1 || density !== 'default')` `:1645` |
| 本页密度下拉 radio | **`[]`（一个都没有）** ← 单视图 + 默认密度 ⇒ 整段不渲染 |
| `localStorage['html-gen:table:density']` | `null`（未设 = default） |

⇒ 三档 CSS 齐全，但**用户在页面上点不到**；default 12px 在 6 列深色表上确实偏小。

### 1.4 其它现状（同一实测）

`table-layout:fixed`；`thead sticky` ✓；首列 `sticky` ✓；**无斑马纹**（行背景 `rgba(0,0,0,0)`）；
`td{white-space:nowrap}`；容器 `scrollWidth 1520 / clientWidth 716`（**横滚 2.1 倍**）；body 16px。
分享链接：`buildShareUrl() = syncUrlState() + location.href`，而 `syncUrlState()` 仅写 `tab / q / split`
⇒ **密度、排序、列可见性不随链接传递**。

---

## 2. 需求复述

- **R1** 分享/Home 按钮不再独占一行，落到「标题 + 统计」同域（`statTotal` 右侧）。
- **R2** 密度三档可用且**默认可读**；入口在每页都可见（不靠 localStorage 手改）。
- **R3** th / 行内 pill / video-pill / 统计 pill 字号随密度同比缩放（现 pill 固定 0.7rem，切档后失衡）。
- **R4** 分享链接能还原阅读视图（至少 `density`，可选 `sort` / 列可见性）。
- **R5** 模板是共享资产（本仓 6+ demo、hermes-manager 8 个 console 页、personal-cinema / script-miner 生成页）
  ⇒ 一次统一改 + 全量重刷 + 基线更新 + 跨仓转交，不做单页特供。

---

## 3. 方案（已按 D1–D8 定稿）

### S1 按钮落位（`layout-table.html`，约 1 处 markup + 6 行 CSS/JS）

1. `<!--HOME_LINK--><!--SHARE_BUTTON-->` 从 `.tabs-actions` 移入 `.table-header`，紧随 `statTotal` pill、`.flex-1` 之前。
2. `#tabsBar` 无子节点时给 `.tabs-row` 挂 `no-tabs` 类（`buildTabs()` 末尾判定），CSS `.tabs-row.no-tabs{display:none}`。
3. 图标 `↗️` → `🔗`，补 `aria-label="拷贝含当前视图的分享链接"`；toast 沿用既有「已复制链接」。

**硬约束（跨仓）**：hermes-manager `normalize_skeleton()` 用 `_take_block` 抓 `.ratio-wrap` / `.col-toggle-wrap`，
抓不到即 `RuntimeError`（生成器 exit 2、保留旧壳）。⇒ 这两个块**必须留在 DOM 里**（可只 CSS 隐藏），
`.tabs-row` 也只许 `display:none` 不许删节点。

### S2 密度/字号体系（变量化，仿 `--kv-cols` 既有做法）

| 档位 | `--table-fs` | td padding | 近似行高 | th |
|---|---|---|---|---|
| dense（紧凑） | `0.7rem` (11.2px) | `2px 8px` | 22px | 不变 |
| **default（标准）** | `0.82rem` (13.1px) ← 由 12px 上调 | `8px 10px` | ~39px | `calc(--table-fs*0.88)` ≈ 11.5px |
| comfortable（舒适） | `0.94rem` (15px) ← 由 13.1px 上调 | `12px 14px` | ~48px | `calc(--table-fs*0.85)` ≈ 12.8px |

- `.cell-pill` / `.video-pill` / `.stat-pill` 改 `calc(var(--table-fs) * 0.9)`（当前硬编码 0.7rem / 0.65rem）。
- **去掉入口门控**（`:1645` 的 `tabCount > 1 || density !== 'default'`），密度段恒渲染。
- `?density=` 入 `syncUrlState()`（R4）；支持 `options.density` 作为页面默认档（见 §6 契约同步）。
- 可选：`d` 键循环密度 + toast「密度：舒适」。
- 代价：所有 table 产物重刷 + `baseline --update`；默认变大后 6 列页横滚 1520 → 约 1700px。

### S3 可读性延伸（本批只登记，不实施）

斑马纹开关 · hover 行高亮统一（现仅 `clickable-cell`）· `nowrap` 可切"允许换行" ·
长文本列 `max-width` + `title` tooltip · 列宽记忆。

---

## 4. 决策（D1–D8 已全采推荐）

| # | 决策 | 采用 |
|---|---|---|
| D1 | 按钮落位 | **A**：header 内 `statTotal` 右侧 + 无 tab 折叠 tabs-row |
| D2 | 图标/语义 | `🔗` + `aria-label`（提示"含当前视图"） |
| D3 | 字号档位 | **b**：三档整体上移（13.1 / 15 / 11.2） |
| D4 | 密度入口 | 去门控 + header 常驻三档切换 |
| D5 | 改动范围 | 改模板全量生效（demo 重刷 + 跨仓转交代重生成） |
| D6 | 分享链接 | `syncUrlState()` 增 `density` |
| D7 | 执行顺序 | 本仓模板 → 重刷/基线 → 转交 hermes-manager → 8081 目视验收 |
| D8 | 先定稿 | 本文件即定稿件 |

---

## 5. 分析一：为什么其他仓用 html-gen 模板时覆盖不到模板规范

> 结论先说：**契约只在本仓内闭环**，跨仓既拿不到机器可读的契约，也没有版本锚点，
> 唯一的对齐手段是"人读 help/skills"，而 `--quiet` 又把唯一的自动告警（未知键）吞掉了。

根因 8 条（每条带证据）：

**G1 契约三面同步只发生在仓内。**
`TEMPLATE_CONTRACT`（`html-gen.py:870`）+ `help <theme>` 键规范段 + `tests/test_help_contract.py`
互相钉死，但断言的是「本仓模板消费的键 ⊆ 契约」（`test_help_contract.py:238-268`）。
调用方传的 payload 不参与任何断言 ⇒ 契约再准也覆盖不到下游。

**G2 唯一的自动告警被调用方吞掉。**
`warn_unknown_table_keys()`（`html-gen.py:692`）明确「仅写 stderr，不阻断、不改退出码」；
而 hermes-manager `run_html_gen()` 只在 `returncode != 0` 时才把 stderr 拼进异常（`web_console_lib.py:284-289`），
且命令行带 `--quiet`（`:281`）。⇒ **拼错键名 100% 静默**，页面照生成（少一列/少一个开关），无人知晓。

**G3 产物没有版本锚点。**
本仓 `demos/*.html` 中 `<meta name="generator">` = **0 个文件**（实测），也无 `html-gen vX.Y` 字样。
⇒ 无法回答「这页是哪个模板版本生成的」「模板升级后哪些页过期了」⇒ 不存在 drift 检测的可能。

**G4 下游直接 fork 模板源码，而不是调用 CLI。**
daily-checker 的 `index.html` 就是 `layout-table.html` 的移植件（来件自述 `index.html:12` / `:1374`），
因此自建了 370 行布局判据 + 305 行 `scripts/baseline.py`。
上游此后任何演进（CL033 的 `span:"full"`、CL034 的测试卫生、本批的密度变量）**结构化地覆盖不到它**。

**G5 调用方做骨架后处理，上游布局契约部分失效。**
hermes-manager `normalize_skeleton()` 会改写 DOM 位置（`.ratio-wrap` / `.col-toggle-wrap` → `.tabs-row`）。
它只在"抓不到锚点"时 fail-fast；锚点还在但语义变了（例如本批要把 share 搬进 header）它不会知情。

**G6 CLI 靠 PATH 定位，版本随环境漂移。**
`shutil.which("html-gen")`（`web_console_lib.py:272`）+ personal-cinema 还有硬编码 fallback
（`pc-gen-magnet-page.py` 的 `~/.local/bin/html-gen`）。同一份生成代码在别人机器上可能跑旧版模板。

**G7 跨仓测试是"软覆盖"。**
hermes-manager `_HAS_HTML_GEN = shutil.which("html-gen") is not None` + `skipif`
（`tests/test_web_console.py`、`tests/test_cl088_c4a_layout.py`）；script-miner 同款。
缺 CLI 即 skip ⇒ 绿是假绿，**与 CL034 刚修掉的 HG-SEC-219（探针 skip 假绿）同类问题**。

**G8 规范载体分散，且没有机器可读导出。**
`help <theme>`（人读文本）、`TEMPLATE_CONTRACT`（Python 内部常量）、`skills/*/SKILL.md`（喂 agent 的 prompt）、
`features.md`（本地存储键表）、`documents/*.md`（细则）。
实测 `density` 三档**只出现在** `features.md:228` 与一份归档设计稿里，
`help table` 键规范段、`TEMPLATE_CONTRACT`、`skills/html-gen-table/SKILL.md` **全都没有** ⇒
读 prompt 规范的下游 agent 根本不知道有密度这回事。

---

## 6. 分析二：prompt 规范与说明性文档的更新清单

> `html-gen prompt <skill>` 直接读 `skills/<skill>/SKILL.md`（`html-gen.py:1547`），
> `prompt --site` 再生成 `prompts/`（23 顶层 + `kb/` 9）⇒ **改 skills/*.md 即改 prompt 输出，但站点产物必须重生成**。

| # | 文件/载体 | 现状 | 本批需改 | 触发条件 | 判据 |
|---|---|---|---|---|---|
| 1 | `html-gen.py: TEMPLATE_CONTRACT['table']` | 无 `density` 键 | `options` 增 `density`（取值 `default/compact/comfortable`，默认 `default`） | 采纳 `options.density` | `test_help_contract` 通过 |
| 2 | `html-gen help table` 键规范段 | 无密度、无字号 | 增 `options.density` 说明 + 三档语义 + `?density=` | 同上 | `help table` 与契约逐字一致（既有断言） |
| 3 | `tests/test_help_contract.py` | 三面同步断言 | 新键自动纳入（`_assert_dim('options')`），另加「模板实际消费 `--table-fs` 三档」断言 | 同上 | 全绿 |
| 4 | `skills/html-gen-table/SKILL.md` | `:140` 写「分享按钮在 `.tabs-actions`」 | 改位置（`.table-header` 内 `statTotal` 右侧）+ 增密度三档/字号变量/`?density=` | S1+S2 | `html-gen prompt html-gen-table` 输出含新段 |
| 5 | `skills/html-gen-cli-spec/SKILL.md` | 无密度 | 若 `density` 入 `options` 则加键；若另加 `--density` CLI 参数则同步参数表 | 同上 | 同上 |
| 6 | `prompts/`（23 文件 + `kb/` 9） | 旧内容 | `html-gen prompt --site` 重生成（产物勿手改） | 4/5 改完 | 文件数 32 稳定 + 内容含新段 |
| 7 | `documents/templates.md` | 有 `splitGrid`/`full` 口径 | 增「密度三档 + `--table-fs` + 按钮落位 + `tabs-row.no-tabs`」 | S1+S2 | 与模板实现逐条对应 |
| 8 | `documents/cli-reference.md` | 参数表 | 若加 `--density` 参数则同步三层说明 | 仅当新增 CLI 参数 | help/文档一致 |
| 9 | `documents/testing.md` | 有基线/卫生约定 | 增「`tabs-row` 折叠」「密度入口恒在」「字号变量生效」三条渲染判据 | S1+S2 | 新断言落 `tests/` |
| 10 | `features.md:228` | 已有 `html-gen:table:density` 键 | 补「入口不再门控 + 默认档字号变更」 | S2 | 与实现一致 |
| 11 | `AGENTS.md` `:6`/`:44` | 466/46 | 新增断言后 +N（预估 +4 ⇒ 470） | 测试数变化 | **受保护文件需审批** |
| 12 | `README.md` / `README.zh.md` | 466 | 同上 | 同上 | 与 AGENTS 一致 |
| 13 | `data/_render-baseline.json` | 23 项 | 重刷后 `--update`（所有 table 产物字节必变） | S1+S2 | `--check` 23/23 |

---

## 7. 下一步行动计划（待指示，不执行）

- **P1** ✅ 本文件落盘（`documents/solutions/table-density-and-actions-20261112.md`）。
- **P2** 改 `layout-table.html`：S1 + S2；补 4 条渲染断言（header 内含 share、无 tab 时 `tabs-row` 隐藏、
  密度入口恒在、`--table-fs` 三档生效）；同步 §6 的 1–10 项。
- **P3** `python3 html-gen.py demo --rebuild` 全量重刷 → `scripts/baseline.py --update` → `pytest -q -n 4`（预期 466+4=470）；
  同步 README/README.zh/**AGENTS（需审批）**。
- **P4** 出转交件给 hermes-manager：① 重生成 8 个 console 页的命令；② `normalize_skeleton` 锚点兼容检查点
  （`.ratio-wrap`/`.col-toggle-wrap` 仍在 DOM）；③ 建议其 `run_html_gen` 改为 stderr 非空即记日志（治 G2）。
- **P5** 视觉验收：8081 三档密度截图对比 + 窄屏（756px）与 1280px 两档宽度检查。

---

## 8. 由本次分析衍生、尚未决策的 3 条（附推荐）

- **D9 契约机器可读化**：新增 `html-gen help table --json`（或 `--contract` 输出 JSON）。
  **推荐做**——这是 G1/G8 的治本点：下游生成器可在生成前比对「本机 CLI 版本 + 契约键」，
  拼错键从"静默"变"启动即报"。
- **D10 未知键严格模式**：CLI 加 `--strict`（默认仍宽松，保持向后兼容），`--quiet` 不再吞 stderr 警告。
  **推荐做**——一行开关换掉 G2 的静默面。
- **D11 产物版本戳**：产物注入 `<meta name="generator" content="html-gen v3.4 (+模板 sha 短码)">`。
  **推荐做**，但代价是全部产物重刷 + 基线重写；可与 P3 合并成一次成本。
  （D9+D10+D11 合起来才构成"跨仓 drift 可检测"的最小闭环。）

---

## 9. 复跑命令（证据复算）

```bash
# 页面侧（8081 正在跑；headless 浏览器控制台量测也可）
curl -s http://jaden.local:8081/shortcuts/index.html | grep -n "share-link\|statTotal\|tabsBar"
# 模板侧
grep -n "tabs-actions\|table-tabs:empty" ~/CodeSpace/html-gen.cli/layout-table.html
grep -n "data-table td {\|\.dense td\|\.comfortable td" ~/CodeSpace/html-gen.cli/layout-table.html
grep -n "tabCount > 1 || density" ~/CodeSpace/html-gen.cli/layout-table.html
# 覆盖不到的证据
grep -c 'name="generator"' ~/CodeSpace/html-gen.cli/demos/*.html | grep -v ':0' | wc -l    # ⇒ 0
grep -rn "density" ~/CodeSpace/html-gen.cli/skills/ | wc -l                                 # ⇒ 0
grep -rn "warn_unknown\|stderr" ~/CodeSpace/hermes-manager/scripts/web-console/web_console_lib.py
grep -rn "_HAS_HTML_GEN\|skipif" ~/CodeSpace/hermes-manager/tests/test_web_console.py | head -3
sed -n '12p;1374p' ~/CodeSpace/daily-checker/index.html     # fork 证据
```

## 10. 边界

- 本轮**不动任何源码/模板/产物**；只落方案。
- hermes-manager / daily-checker / script-miner / personal-cinema 一律只读，改动走转交件。
- `AGENTS.md` 属受保护文件：P3 的计数同步需单独审批。
