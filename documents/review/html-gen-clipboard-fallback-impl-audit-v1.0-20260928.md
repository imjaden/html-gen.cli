# 剪贴板回退统一（canonical copyText）— 实现审计报告 v1.0

> 日期: 2026-09-28 · 闭环: **HTML-GEN-CL015 [5/6] 实现审计** · 角色: review（1A 口径：**独立复算，禁采信转述**）
> 被审（dev, 74 文件）: `b4afd4e`(canonical 块 + 8 调用点) → `d4f0ca9`(产物全量重生成) → `3d6bfff`(守卫 T1-T11) →
> `c5c4e02`(版本 3.4 + README) → `8e99f24`(features/skills 同步) → `bf61484`(用例命名 + 既存用例去假成功断言)
> 被审（ops）: `dfd5d71` [4/6] ops 核查回执（+2 文件: ops 报告 A / `TODO-handoff.md` M）
> 比对基线: `83c4e2c`（"零改动基线重生成 29 文件"，**不得**用更早 commit）
> 规格源（唯一口径）: `documents/solutions/html-gen-clipboard-fallback-design-v1.2-20260927.md`（§0.4 v1.2 补记 + §3 canonical 块规格 + §5 逐产物参数集 + §7 验收 A0–A4）
> 上轮评审: `documents/review/html-gen-clipboard-fallback-design-review-v1.1-20260927.md`（PASS 85/100·B · HG-SEC-187..201）
> ops 核查: `documents/review/html-gen-clipboard-fallback-ops-verify-v1.0-20260928.md`（18/18 PASS；**仅引用，不以其替代复算**）
> 锚点核验: `pwd && git rev-parse --show-toplevel` → `/Users/jadenli/CodeSpace/html-gen.cli` 两行一致 ✅ · HEAD=`dfd5d71` · `git status` 干净 · `ipconfig getifaddr en0`=`192.168.31.178`
> **结论: ✅ PASS —— 95/100（A）· 15 条 finding 全数处置或 N/A · 0 🔴 / 0 🟡 · 新增 5 🟢 record（全为文档/报告口径，0 代码回炉）**

---

## ① 结论要点表

| 面 | 判定 | 我的关键实测（独立复算） |
|:--|:--|:--|
| §3 canonical 块 | ✅ 逐字节合规 | 自建提取器（围栏块 + 标记锚点）取规格源与四模板：**唯一 sha256 `eb5431669eca36b4…` = 设计 §3 原文**，块内 27 行，四模板 100% 一致 |
| 块外越界调用 | ✅ 0 | 块内 `navigator.clipboard` 3（2 守卫 + 1 调用）/ `execCommand` 1；**块外 0 / 0**；`copyText(` 调用 3+2+2+1 = **8**（与 §4 矩阵逐条吻合） |
| 产物面（67 文件） | ✅ 0 未声明越界 | IN_BLOCK **216** · IN_SCRIPT **5**（**全部落在 D6 保护面 `demos/index.html`**，设计已声明）· IN_PROSE 10（正文/示例引用，判级口径一致）· 死代码 `fallbackCopyUrl`/`fallbackCopy(` 残留 **0** |
| 产品 vs 基线笔（188） | ✅ 仅脚本面 + 声明文档面 | 60 个产物逐行 diff 分类：**SCRIPT 2252 行** + 文档面 **11 行（声明项）** + **区间外未声明 0 行**；产物面新增文件 0（零结构改动）；`data/**` 零改动（间接：产物重生成 byte-IDENTICAL） |
| 4 个 drama strategy 表（188 例外） | ✅ 内容无损 | COLUMNS/DATA 区域与基线**逐行全等**；列集 daming 10 / history 11 / yongzheng 10 / zhuyuanzhang 10，**丢失 0**；JSON 源对 3 表确为旧口径（按 JSON 重生成丢 `derivative/homology/synonym/antonym` 4 列） |
| §0.4-A 参数集（187） | ✅ 可复跑 | 参数**只从产物自身回收**（禁凭记忆）重生成 **38/38 byte-IDENTICAL**（doc 25 + knowledge 4 + table 9）+ `demo --rebuild` **3/3 IDENTICAL**；`demos/index.html` 未被写（D6） |
| 全量回归 | ✅ 346 / 82 subtests / 0 failed | `-n 0` 权威单线程 137.11s；基线 `83c4e2c` **334 → 346**（Δ+12 = 新文件 12 用例，**既有用例数逐一不变**） |
| 真非 localhost 端到端 | ✅ 真复制实证 | `http://192.168.31.178:8931/table-actions-demo.html`：`isSecureContext=False`、`navigator.clipboard=undefined`；真实点击 → `已复制: document.pdf`、JS 错误 0；**有头 Chrome 下 `pbpaste` 回读 == `document.pdf`（真复制，哨兵法排除残值）** |
| 非假成功（失败可见） | ✅ | 干净页 + 无用户激活直调 `copyAction()` → **`复制失败`**（不静默、不假成功）；夹具 `execCommand→false` → `复制失败，请手动选中文本复制` |
| 上游只读探针 | ✅ OK 130 / WARN 0 / FAIL 0 | 独立复跑（内存改 REPO，零写盘）；基线副本同口径为 OK 104 / WARN 47 / FAIL 38（§0.4-B 声称一致） |
| 判据非恒真（反证） | ✅ 4 项 | ① 我的 A1/B2 扫描器指向基线副本 → 块缺失全红（块外调用 13 / `execCommand` 6；IN_BLOCK 0→216、IN_SCRIPT 286→0）② 变异测试 3 态全中（见 §2.6）③ 原用例「恒绿」端到端坐实（见 §2.7） |
| 测试削弱核查（E） | ✅ 无削弱 | `bf61484` 对既存用例仅 **+11/-2**（夹具 +1 方法改名 +1 docstring），**断言逐字未变**；判为 **无关**（非强化非削弱，详见 §3-E） |
| 文档面（193/194） | ✅ | 版本 `3.4`/`2026-09-27`；docstring 写死版本行**已删**（5 处→4 处）；`features.md` canonical 提及 **4 处**；skills 2 行已订正；`prompts` 重生成 **31 文件 = 22 IDENT + 9 仅 meta 时间戳**；`html-gen.py` diff **0 处**剪贴板键（契约段确未动） |
| 范围白名单 | ✅ | dev 74 文件全在声明面；保护面 `index.html` / `demos/index.html` / `AGENTS.md` / `data/**` **零改动** |

---

## ② 可复跑验证清单（命令 + 预期 + 断言）

> 全部脚本为本次审计**自建**（不复用 ops harness）；工件在
> `~/.hermes/profiles/review/cache/scratch/cl015-audit/`（`a1`…`b5` + `*.out` 原始输出）。
> `PY=/opt/homebrew/Caskroom/miniconda/base/envs/py3.12/bin/python3`

```bash
cd /Users/jadenli/CodeSpace/html-gen.cli
S=~/.hermes/profiles/review/cache/scratch/cl015-audit

# 1) canonical 块：规格源 vs 四模板逐字节 + 块内外计数          预期: sha 唯一 = eb5431669eca36b4 / 块外 0·0 / copyText 8
$PY $S/a1_canonical_block.py .

# 2) 产物面扫描（demos/**.html + prompts/**）                   预期: IN_BLOCK 216 / IN_SCRIPT 5(全为 demos/index.html) / 死代码 0
$PY $S/b2_product_scan.py .

# 3) 产物 vs 基线 83c4e2c 逐行 diff 分类                        预期: SCRIPT 2252 / 文档面 11 行 / 区间外未声明 0
$PY $S/a2_baseline_diff.py

# 4) 4 个 strategy 表注入载荷无损（锚点法）                     预期: 4/4 COLUMNS+DATA 逐行全等 / 丢列 0
$PY $S/a3_strategy_v4.py

# 5) §0.4-A 参数集全量重生成                                    预期: IDENTICAL 38 / DIFF 0 / ERR 0
$PY $S/a7_regen_all.py

# 6) 全量回归（权威单线程）                                     预期: 346 passed, 82 subtests
$PY -m pytest tests/ -q -n 0 | tail -2

# 7) 真非 localhost 端到端（需 http.server --bind 0.0.0.0, cwd=demos）
#    预期: isSecureContext=False / clipboard=undefined / toast='已复制: document.pdf'
$PY $S/b4_e2e.py
# 7b) 真复制实证（有头）+ headless 剪贴板隔离（含哨兵与剪贴板恢复）
#    预期: [headless] 哨兵仍在（隔离）; [headed] pbpaste == 'document.pdf'
$PY $S/b4b_clipboard_isolation.py

# 8) 变异测试（/tmp 副本，零污染 live 树）                      预期: BASE 绿 / M1·M2·M3 红且指名 / RESTORE 绿 / live 干净
$PY $S/b5_mutation.py

# 9) 测试削弱 A/B                                              预期: 基线×复制失败→'已复制'(假成功) / HEAD×复制失败→'复制失败'
$PY $S/e2_ab_probe.py

# 10) 上游只读探针                                              预期: OK 130 / WARN 0 / FAIL 0
$PY - <<'PY'
import importlib.util; from pathlib import Path
p = Path.home()/"CodeSpace/script-miner/efficiency/clipboard-fallback-check.py"
s = importlib.util.spec_from_file_location("c", p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
m.REPO = Path.cwd(); f = m.scan(None)
print(len(f), {lv: sum(1 for x in f if x['level']==lv) for lv in ('OK','WARN','FAIL')})
PY

# 11) 反证：判据指向基线副本                                     预期: 块缺失全红 / IN_BLOCK 0 / IN_SCRIPT 286
git archive 83c4e2c | tar -x -C /tmp/cl015-base-audit
$PY $S/a1_canonical_block.py /tmp/cl015-base-audit
$PY $S/b2_product_scan.py /tmp/cl015-base-audit

# 12) 版本/文档面                                              预期: v3.4 (2026-09-27) / docstring 版本行消失 / features 4 处
$PY html-gen.py version; sed -n '1,18p' html-gen.py; grep -c 'canonical\|copyText' features.md
```

---

## ③ 逐 finding 明细（HG-SEC-187..201，15 条）

> 判定口径：**已处置** = 补记/实现/测试/文档实测到位；**N-A** = 本批 git 交付面外；每条均附**我自己的**复算命令与实测输出，不写「ops 报告说已处置」。

| # | 规格/依据 | 我的复算命令 | 实测输出 | 判定 |
|:--|:--|:--|:--|:--|
| **187** | §0.4-A 参数集（★ 缺项） | `$PY $S/a7_regen_all.py`（参数**只从产物自身回收**） | **IDENTICAL 38 / DIFF 0 / ERR 0**（doc 25 / knowledge 4 / table 9）+ `demo --rebuild` 3/3 IDENTICAL、`demos/index.html` 未变 | ✅ **已处置** |
| **188** | §0.4-A-A/B（例外 + 基线笔） | `$PY $S/a2_baseline_diff.py`；`$PY $S/a3_strategy_v4.py` | 60 产物：SCRIPT 2252 / 文档面 11 行 / **区间外未声明 0**；产物面新增 0；4 表 COLUMNS+DATA **逐行全等**、丢列 0 | ✅ **已处置**（例外成立且无损） |
| **189** | §0.4-C「189」 | `git diff 83c4e2c..HEAD -- demos/usage-guide.md`；上游只读探针 | md:274 已改为含 `document.execCommand('copy')` 字面量的判级可达表述；探针 **OK 130 / WARN 0 / FAIL 0**（含 `demos/usage-guide.html:961`） | ✅ **已处置** |
| **190** | §0.4-C「190」 | 读 `tests/test_clipboard_fallback.py` | `FIX_SECURE_REJECT`（`isSecureContext=true` + `writeText→Promise.reject`）存在，且被 `test_09` ① **实际使用**（非仅定义） | ✅ **已处置** |
| **191** | §0.4-C「191」 | 读 `tests/test_clipboard_fallback.py::test_03` + 块落点实测 | 四模板块均落主 `<script>` 内（L325/346/1418/293）、**toast 声明在块之前**且区间内无 `})();`；T3 含该三条解析链命中断言 | ✅ **已处置** |
| **192** | §0.4-C「192」 | `grep -n readonly` 块内；读测试 docstring / T11 SKIP 文案 | 保留 `ta.setAttribute('readonly','')`；测试文件 docstring 与 T11 SKIP 消息**双处登记**「移动 Safari 不在覆盖范围（HG-SEC-192）」 | ✅ **已处置**（未验证面如实保留） |
| **193** | §0.4-C「193」 | `$PY html-gen.py version`；`sed -n '1,18p' html-gen.py`；`git diff 83c4e2c..HEAD -- html-gen.py` | `html-gen v3.4 (2026-09-27)`；docstring `版本: 3.3(2026-08-28)` 行**已删**；diff 仅 +2/-4（常量 + docstring 行） | ✅ **已处置** |
| **194** | §0.4-C「194」 | `grep -c canonical features.md`；`grep skills/*/SKILL.md`；`$PY html-gen.py prompt --site --dir <scratch>` | features.md **4 处**（44/120/190 订正 + 191 新增）；skills doc:57 / table:140 已订正；prompts 重生成 **31 = 22 IDENT + 9 仅 meta 时间戳**；`html-gen.py` diff 剪贴板键 **0 处**（契约段未动） | ✅ **已处置** |
| **195** | §0.4-C「195/196」 | `git ls-files demos prompts data/_demos-data.json demos/_registry.json` | 产物面 **77 = 44 demos 产物 + 31 prompts + `_demos-data.json` + `_registry.json`**（`demos/*.html` 57 − 13 内容子页 = 44） | ✅ **已处置**（补记 78→77，§0.4 覆盖 §5 原文） |
| **196** | §0.4-C「195/196」 | `grep -l '"output"' data/*.json` | **0/8** 命中 ⇒ 与补记「8/8 无 `output`，table 一律显式 `-o`」一致；prompts 枚举含 `_kb-data.json` / `_kb-groups.json`（补记已列） | ✅ **已处置** |
| **197** | §0.4-C「197/198」 | `$PY $S/e2_ab_probe.py`（基线 × `isSecureContext=false` + `clipboard=undefined`） | 基线 `execCalled=0` 且 toast 仍 `已复制` ⇒ **非安全上下文下 `✓` 赋值确不可达**（同步 throw 被 catch），补记「拆写两句」的定性**与实测一致** | ✅ **已处置**（补记订正） |
| **198** | §0.4-C「197/198」 | `$PY $S/a1_canonical_block.py .` | 四模板 `navigator.clipboard` **恒为 3**（2 守卫 + 1 调用）⇒ 补记「块内 3 次」措辞成立 | ✅ **已处置** |
| **199** | §0.4-C「199」 | `git check-ignore -v src/html_gen/html-gen.py`；`git ls-files src/ \| wc -l`；`ls -la ~/.local/bin/html-gen` | `.gitignore:37:src/`；tracked **0**；已装 CLI 入口存在（2026-08-24，v3.3 期）⇒ **发版流程项，非本批 git 面** | **N-A**（本批交付面外） |
| **200** | §0.4-C「200」 | `hm loop next-code --json`；`grep -n CL016 html-gen.py` | 台账 `{"code":"HTML-GEN-CL016"}`；`html-gen.py:15/16/1234` 以 `CL016` 为**版本子命令内部编号** ⇒ 双语义**确实并存**，留档成立 | ✅ **已处置**（留档） |
| **201** | §0.4-C「201」+ §5-A doc 行 | `$PY $S/a7_regen_all.py`（25 doc 全量，含 `--subtitle` 回收） | 25/25 byte-IDENTICAL ⇒ `--subtitle` 已评估且可复跑；9 产物 favicon 位置差异经 `d4f0ca9` 全量重生成后**不再存在**（重生成零差异） | ✅ **已处置** |

**判定汇总：已处置 13 · N-A 1（199）· 部分处置 0 · 未处置 0。**（187–198、200、201 = 已处置；199 = N-A）

---

## ④ 新增项台账（HG-SEC-202 起）

> **「新增项 = 0」不成立 —— 新增 5 项，全部 🟢 record（文档/报告口径），0 🔴 / 0 🟡，无需代码回炉。**
> 5 项均**不改变** 15 条 finding 的判定与 [6/6] 的放行结论；归属见下表。

| 编号 | 严重度 | 描述（我的实测证据） | 复现命令 | 建议归属 |
|:--|:--|:--|:--|:--|
| **HG-SEC-202** | 🟢 record | **§0.4-A 例外表的「11 列」措辞与实测不符**：实为 `daming/yongzheng/zhuyuanzhang = 10 列`、`history = 11 列`；且 `history` 的**例外归因（「JSON 为旧 7–8 字段口径」）不成立** —— 其 JSON 列 11 / 产物列 11 已同步，按 JSON 重生成仍差 212 行是**样式基座漂移**（`.tabs-row/.tabs-actions/.home-link` 等 CL005 基座），非列集落后。**结论不受影响**（4 表按补记保持现状 + 手工同步 canonical 块，内容 0 丢失） | `$PY $S/a3_strategy_v4.py`（末段 JSON vs 产物列）；`$PY html-gen.py table -d data/_drama-table-history-strategy.json -o /tmp/h.html && diff /tmp/h.html demos/drama/history-strategy-table.html \| wc -l`（=212） | 已修正（2026-09-28 设计 §0.4-A 改写为分表列数 + 两表两因）；不阻断 |
| **HG-SEC-203** | 🟢 record | **ops 回执 TC11「4 表基线列 10 / HEAD 10」与实测不符**：实为 **history 11 / 11**（另 3 表 10/10 正确）。另 TC8 的「文档面（声明项）10 行」与我的分类计数口径不同：我的**非 `<script>` 逻辑改动行 = 20**（= 文案类 9：`usage-guide.md:274` + `usage-guide.html:961` + `prompts/{all.md×2, html-gen-doc.json, html-gen-doc.md, html-gen-table.md, kb/html-gen-doc.html, kb/html-gen-table.html}`；meta 类 11：`usage-guide.html` meta 1 + `prompts/html-gen-table.json` 1 + `prompts/kb/*.html` meta 9）。**两处均为计数/口径差，非结论差**：我独立复算同样得「零未声明改动」 | `$PY $S/a2_baseline_diff.py`（DOC-FACE 明细段 + OTHER 明细段） | 另批（ops 回执勘误）；不阻断 |
| **HG-SEC-204** | 🟢 record | **~~ops 回执~~ A4/T1「`git -C ../script-miner status --short` 空 ⇒ 零写他仓」与实测不符**（**ops 勘误 2026-09-28：该断言实为设计 §7 验收表 A4 条款原文（设计 v1.2 :386），ops 回执无此断言** ⇒ 来源标注应改「设计 §7 A4 条款」，非 ops 回执；详见 `documents/review/html-gen-clipboard-fallback-errata-analysis-v1.0-20260928.md` §二/§四）：复算时该命令输出 ` M efficiency/workflow-prompt.md`。经独立取证，**「探针只读」的判断本身成立**：① 该文件 mtime = `Sep 28 11:58`，早于 ops 核查（约 12:20）与本会话复算（12:49），非本批/本会话所致；② 探针脚本源码 `write_text\|open(...,'w')\|.write(\|shutil\|mkdir\|unlink\|rename` 命中 **0** 处。⇒ **条款措辞不可满足（已弃用并改判据），结论正确** | `git -C ~/CodeSpace/script-miner status --short`；`ls -la ~/CodeSpace/script-miner/efficiency/workflow-prompt.md`；`grep -n "write_text\|open(.*['\"]w\|\.write(\|shutil" ~/CodeSpace/script-miner/efficiency/clipboard-fallback-check.py` | 已修正（设计 §7 A4 条款改写 + 本行来源标注, 2026-09-28） |
| **HG-SEC-205** | 🟢 record | **`bf61484` 夹具 docstring 的环境前提与实测不符**：文称「headless Chrome 在 `file://` 下 `writeText` 抛 `NotAllowedError` **且 `execCommand('copy')` 返回 false**」。实测：`writeText` 确 reject ✅，但 `execCommand('copy')` 在**有用户激活**（Selenium 可信点击）的 headless `file://` 下**返回 True**；仅「干净页 + 无用户激活直调」才返回 false（→ `复制失败`）。⇒ 桩在本环境**不承重**（有桩/无桩均绿）。夹具**无害**、断言**未削弱**，仅注释需订正 | `$PY $S/e1_test_weakening.py`（E1/E2/E3）；`$PY $S/b4b_clipboard_isolation.py`（干净页直调 → `复制失败`） | 已修正（2026-09-28 tests docstring 环境前提订正）；不阻断 |
| **HG-SEC-206** | 🟢 record | **我自己的首轮判据出现过一次恒真/误报，已记录备查**（可复跑性纪律）：① 4 strategy 表初版按静态 `<table>` 解析（产物为 JS 注入 ⇒ 0 列 0 行「平凡 PASS」）→ 已改锚点法；② A7 全量重生成初版把 `countries-table.md` / `provinces-table.md` 等**数据源说明 md** 当 doc 源，与 table 产物**同名碰撞** ⇒ 误报 2 例 DIFF，核实 sha256 后为**逐字节相同**。两项均为 harness 侧缺陷，非被测物缺陷 | `$PY $S/a3_strategy_v4.py`；`shasum -a 256 demos/countries-table.html $S/regen-all/demos_countries-table.html` | 无需处置（本报告已自证并留档） |

---

## ⑤ 未验证面与降级登记（显式，不沉默略过）

| # | 面 | 状态 | 依据/说明 |
|:--|:--|:--|:--|
| U1 | **移动端 Safari（`readonly` + `select()`/`execCommand`）** | **未验证**（承接 192） | 环境无 iOS 真机/模拟器；T11 仅覆盖桌面 LAN。本批按 §0.4-C 保留 `readonly`，风险已知且低 |
| U2 | **headless 下「真复制」证伪/证实** | **降级说明** | 哨兵法实证：headless 与系统 pasteboard **未打通**（点击后 `pbpaste` 仍为哨兵 `CL015-SENTINEL-831532`）⇒ 凡以「headless 回读剪贴板」为据的**真复制**断言在本机不成立。**已改以有头 Chrome 实证替代并成功**（`pbpaste == document.pdf`）；ops 回执 TC17-C 的「CDP 粘贴回读」方法我**未能复现**（`clipboard.readText()` → `NotAllowedError`、`execCommand('paste')` → `false`），其结论我用更强方法独立取得（见 §①、§②/7b） |
| U3 | **`readText` 读取路径** | 不影响验收面 | 产品侧只用 `writeText`；读取仅测试用，headless 权限墙（U2 同源） |
| U4 | **`src/` 打包源未重建**（199） | **N-A** | 已装 CLI 仍产旧剪贴板代码；属发版流程（PyPI/重装），非本批 git 交付面 |
| U5 | **`prompts/kb/*.html` 的 meta 时间戳** | 可解释差异 | 22/31 byte-IDENTICAL，9 个 kb 页仅差 2 行（源 md mtime），非语义差。**⇒ 附带结论：doc 类产物的 byte-identity 依赖源 md mtime，fresh clone 后重生成会出现仅 meta 行差异**（本批 25 doc 在**当前工作树**下 100% 复现） |
| U6 | **`demos/index.html`（D6 保护面）自身 5 处脚本内 `navigator.clipboard`** | **声明内**，非本批缺陷 | 我的扫描 IN_SCRIPT=5 **全部**落于该文件（L365/376/380×2/381）；设计 §8-O5 已声明「落地页 `copyText` 同名不同签名，D6 不动」；该笔零改动已复核（`git diff 83c4e2c..HEAD -- demos/index.html` 空） |
| U7 | **`demos/chaitin/*.html`（13 内容子页）/ `slide-demo.html`** | 无生成器 | 前者无数据源与剪贴板代码（扫描目标出现点 0）；后者无 md 源（§0.4-A slide 行同口径） |

---

## ⑥ 文档面（只提建议，不代改）

1. **`features.md`**：本批已同步（canonical 4 处 + CL015 条目 L191）⇒ **无需再改**。
2. **`AGENTS.md`（受保护文件）**：仍**零改动**（TC16 守）。建议（属**建议面**，需审批后再动）：
   - 「CLI 子命令」段可补一句 canonical 口径：四模板 `copyText` 逐字节一致 + 块外零 `navigator.clipboard`，守卫见 `tests/test_clipboard_fallback.py`（T1–T11）；
   - 「测试治理」段的计数 `334 tests` 已过期 ⇒ 建议改 **346 tests（31 文件）**，并补 `test_clipboard_fallback.py`（12 用例）入枚举；
   - 该文件 docstring 内的**版本行若存在写死版本号**，按 193 同口径处理（本批已处理 `html-gen.py:12`）。
3. `documents/solutions/html-gen-clipboard-fallback-design-v1.2-20260927.md`：建议按 **HG-SEC-202** 出 errata（11 列 → 分表列数；history 例外归因改为「样式基座漂移」）。
4. `documents/review/html-gen-clipboard-fallback-ops-verify-v1.0-20260928.md`：建议按 **HG-SEC-203/204** 出勘误行（TC11 列数；A4「status 空」→ 改为「探针源码零写操作 + mtime 取证」）。
5. **`README.md` / `README.zh.md`**：本批已随 `c5c4e02` 同步 3.4（`grep 3\.3` 无残留），**无需再改**。

---

## ⑦ 评分与结论

| 维度 | 权重 | 得分 | 依据 |
|:--|--:|--:|:--|
| 逐 finding 独立复算（15 条证据强度） | 30 | 29 | 13 条已处置 + 1 N-A；每条钉到源码行/产物/命令输出；199 的 N-A 定性有 grep + ls 双证据 |
| 自建判据独立复算（A1/A2/A5/A7/B2/B3/B4） | 30 | 30 | 块字节级、产物面零越界、产物 41 项 byte-IDENTICAL、346 回归、真 LAN 端到端 + **有头真复制实证** |
| 判据非恒真与测试削弱核查 | 15 | 15 | 4 项反证（扫描器指向基线全红 / 变异 3 态 / 基线假成功 A/B / T4 主判据指名） |
| 基线口径纪律（188 可判性） | 15 | 14 | 未声明改动 0；扣 1 分因 `history` 例外归因需 errata（202）方能使「按 JSON 重生成即回归」的表述完全自洽 |
| 遗留登记与降级诚实性 | 10 | 7 | U1–U7 全登记；扣分因 ops 回执 2 处证据行不实（203/204）需另批勘误，审计侧无法就地闭合 |
| **合计** | **100** | **95** | **A（PASS）** |

- **结论：✅ PASS 95/100（A）** —— 15 条 finding 全数处置或 N-A（已处置 13 / N-A 1 / 部分 0 / 未处置 0）；机制、产物面、守卫、端到端四层均经**独立复算**成立；0 🔴 / 0 🟡 未闭合项。
- **新增项：5（HG-SEC-202..206）全部 🟢 record**，全部为文档/报告/注释口径，**无需代码回炉**；建议归属「另批 errata/勘误」。
- **放行依据**：canonical 块与规格**逐字节一致**且块外零越界；产物面与基线 diff **零未声明改动**；全量产物重生成 **41/41 byte-IDENTICAL**；回归 **346/346**；真非 localhost origin 下 **真复制经有头浏览器 + OS 剪贴板回读实证**，失败路径**不静默不假成功**；4 个声明例外表**内容 0 丢失**。
- **报告**: `documents/review/html-gen-clipboard-fallback-impl-audit-v1.0-20260928.md`

### 附：本报告使用的自建工件（仓库零改动；`git status` 复算前后均干净）

```
~/.hermes/profiles/review/cache/scratch/cl015-audit/
├── a1_canonical_block.py      + a1.out
├── a2_baseline_diff.py        + a2.out / a2b.out
├── a3_strategy_tables.py / a3_strategy_tables_v2.py / a3_strategy_v3.py / a3_strategy_v4.py  + a3*.out
├── a5_regen.py                + a5.out
├── a7_regen_all.py            + a7.out
├── b2_product_scan.py         + b2.out
├── b3_pytest.out              （346 passed, 82 subtests, 137.11s）
├── b4_e2e.py / b4b_clipboard_isolation.py  + b4.out / b4b.out
├── b5_mutation.py             + b5.out
├── e1_test_weakening.py / e2_ab_probe.py   + e1.out / e2.out
├── clipboard-backup.txt       （剪贴板哨兵测试前备份，测后已恢复 == 备份）
├── regen/ regen-all/ prompts.regen/        （/tmp 外的重生成产物与基线页副本）
/tmp/cl015-base-audit/         （83c4e2c 基线副本：反证用）
/tmp/cl015-mutation/           （HEAD 副本：变异测试用；还原后复绿）
```
