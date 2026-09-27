# 剪贴板回退统一设计 v1.1 — review 报告

> 日期: 2026-09-27
> Reviewer: Security Reviewer（review profile）
> Level: L2 (design-document-review)
> 闭环: HTML-GEN-CL015 [2/6]
> 评审基线: `documents/solutions/html-gen-clipboard-fallback-design-v1.1-20260927.md`（`dc14a38`，决策已定稿 T1+D1..D10）
> 结论: **✅ PASS（85/100）— 0 🔴 / 8 🟡（非阻断，折入 [3/6] dev）/ 7 🟢（record）**
> 方法: 全部判据**独立复算**（禁采信设计自报）—— 只读探针重跑、逐文件 `grep`/`git` 复算、scratch 内原样重生成 + 逐字节 diff、headless Chrome（项目自带 chromedriver）机制原型与真非 localhost origin 端到端实测

---

## 1. 结论摘要

设计的**核心机制成立且已实证**：canonical `copyText` 块（`isSecureContext` 前置 + `execCommand('copy')` 回退 + 返回值检查 + 失败可见反馈 + `onOk` 条件反馈）在 scratch 原型里对 4 个断言全部通过；设计的**问题定性**在真非 localhost origin（`http://192.168.31.178:8917`）上被端到端复现——剪贴板为空、复制实际失败，页面仍弹「已复制: usage-guide.md」（假成功）。

判据可复跑性整体成立：§9 事实卡 14 条中 11 条逐字成立、3 条为表述/枚举偏差（不影响结论）；§7 验收命令全部可复跑，只读探针零写他仓已实证。

扣分点集中在 **§5 重生成矩阵的「可复跑性」**：矩阵只给了「生成器 + 数据文件」，未记录各产物的**实际注入参数**（`--title` / `--subtitle` / `--welcome` / `--github-url` / `--home-url` / `--favicon`）。按矩阵原文执行会**退化用户可见内容**（knowledge 4/4 标题退化为「知识库」、10/25 doc 丢 GitHub corner、table 缺 title/corner/home）。进一步实测：43 个 demos 产物中 **22 个（51%）即使补齐参数仍与当前模板/样式基座存在 10–728 行差异**（历史陈旧产物），故「重生成后只差 canonical 块 + meta 时间戳」这一纪律前提与实测不符。这两项为 🟡 非阻断（设计自带的「先试跑 1 个 + 逐文件 diff」纪律会当场暴露，且修法明确），已给出可执行处置建议。

---

## 2. §9 事实卡 F1–F14 复算表（独立命令 + 原始输出）

| # | 设计断言 | 我的复算命令 | 实测 | 判定 |
|:--|:--|:--|:--|:--|
| F1 | 编号就位 6/6 + next-code CL016 + list ⏳ 待办 | `hm loop check .` / `hm loop next-code --json` / `hm loop list` | `6/6 通过`；`{"code":"HTML-GEN-CL016","system":"PROJ-CL"}`；list 显示 `HTML-GEN-CL015 [独立] ⏳ 待办` | ✅ 成立 |
| F2 | 本仓判级 OK 88 / WARN 47 / FAIL 38（调用点 173） | 只读探针（内存改 `REPO`，见 §7 A3-1） | `total 173`；`OK 88 / WARN 47 / FAIL 38`；FAIL 分布 = `layout-doc.html:424` + `layout-slide.html:590` + `src/html_gen/layout-{doc,slide}.html` 同两行 + 产物 34 处 | ✅ **逐字成立**（含 34 处分布） |
| F3 | 他仓基线 OK 81 / WARN 18 / FAIL 18（14 文件） | `cd ~/CodeSpace/script-miner && python3 efficiency/clipboard-fallback-check.py` | `合计: OK 81 / WARN 18 / FAIL 18`；FAIL 分布 14 文件，其中 `skills/` 7 + `tool-nav-manager/` 2 = 交接件 9 文件 | ✅ 成立 |
| F4 | 巡检脚本 `REPO` 硬编码、无 `--root` | `grep -n '^REPO' …`（+ 读全文确认无 `--root`） | `47:REPO = Path(__file__).resolve().parent.parent`；argparse 仅 `--json/--only/--self-test` | ✅ 成立 |
| F5 | 四模板 JS 在 IIFE 内、toast 为函数声明 | `grep -n '^(function\|function showToast\|function showKwToast\|window.showToast' layout-*.html` | doc `259:(function(){` + `320:function showToast`；slide `280:` + `345:`；table `341:` + `1438:` + `1444:window.showToast=showToast`；knowledge `227:` + `287:function showKwToast` | ✅ 成立（每文件另有第二个缩进 IIFE：doc:475 / slide:669 / knowledge:501，不影响结论） |
| F6 | 8 调用点行号 | `grep -n 'navigator\.clipboard' layout-*.html` | doc 315/424/453；slide 331/332/590；table 1248/1249/1277/1278；knowledge 282 —— 与 §4 矩阵 8 处逐条一致 | ✅ 成立 |
| F7 | 产物面规模 25/14/5/1 | `find demos -name '*.html'` + 标记分类 + `git ls-files` | demos 57 html = doc 25 + table 14 + knowledge 4 + slide 1 + `demos/index.html`（D6 不动）+ 11 chaitin 内容页（无剪贴板代码）；prompts 31 文件（含 kb 9）；`prompts/index.html` 属 knowledge 产物 | ✅ 成立（`prompts` 计数含 2 个 `_kb-*.json` 未枚举，见 HG-SEC-196） |
| F8 | `src/` 不进 commit | `git check-ignore -v src/html_gen/html-gen.py`; `git ls-files src/ \| wc -l` | `.gitignore:37:src/`；`0` | ✅ 成立 |
| F9 | 无 CHANGELOG | `ls *.md` | 现为 6 项（多 `TODO-handoff.md` —— 本版之后 `d5da78f` 产生）；「无 CHANGELOG」结论成立 | ✅ 成立（表述随批次新增文件轻微过期） |
| F10 | 版本同步面 5 处（含 `html-gen.py:17-18`） | `grep -rn '3\.3\|2026-08-28' --include=*.py --include=*.md` | 实测字面量点 **10 处**：`html-gen.py:12`（docstring `版本: 3.3(2026-08-28)`，**设计未列**）、`:17`、`:18` + `README.md:39` + `README.zh.md:39` + `tests/test_cli_version.py:20/26/32/38`（4 断言）+ `tests/test_demo_cmd.py:101` | ⚠️ **表述偏差**（漏 1 处，见 HG-SEC-193） |
| F11 | 本机非 localhost origin 可用 | `ipconfig getifaddr en0` | `192.168.31.178` | ✅ 成立 |
| F12 | `demo --rebuild` 只写 3 产物、`demos/index.html` 仅读入 | 读 `html-gen.py:1702-1778` + 副本内实跑 `demo --rebuild` 后 diff | 写 `_registry.json`(L1745) / `data/_demos-data.json`(L1770) / `demos-index.html`(L1771-1776)；`demos/index.html` 仅 `read_text`(L1716)；**副本实跑后三产物 byte-IDENTICAL、`demos/index.html` 未变** | ✅ 成立（前提「只读入不写出」实证为真） |
| F13 | `node --check` 可用 | `node --version` | `v26.0.0` | ✅ 成立 |
| F14 | 设计两笔提交可复核 | `git show --stat 0c6acdb dc14a38` | v1.0 `0c6acdb`（1 file, +389）；v1.1 `dc14a38`（1 file, +30/-15）；自指 hash 不入正文的处理合理 | ✅ 成立 |

**未核实项的一处实证补记（设计列「未核实」）**：headless Chrome `file://` 下 `document.execCommand('copy')` 真实返回值 = **`false`**（实测；同环境 `file://` 的 `isSecureContext = True`、`navigator.clipboard = [object Clipboard]`）。⇒ 设计采「spy 断言行可达」而非断言真实复制成功是**正确且必要**的取舍（否则 T5–T10 会因真实返回值恒 false 而不可写）。另：巡检脚本对「回退返回值 / 失败反馈」确实不判（`_classify()` 仅匹配标记串），设计的「判级盲区」定性 ✅ 成立。

---

## 3. §1.2 / §4 调用点矩阵逐条复算

`grep -n 'navigator\.clipboard' layout-*.html` + 逐行读源码：

| # | 位置 | 设计现状/判级 | 复核 | 判定 |
|:--|:--|:--|:--|:--|
| 1 | `layout-doc.html:315` | try/catch 吞错 + 无条件 toast；WARN | L315-316 逐字一致；真 LAN origin 实测「复制失败仍报已复制」 | ✅ |
| 2 | `layout-doc.html:424` | 裸 `writeText` + 无条件 `✓`；FAIL | 裸调用成立；**但「无条件 ✓」表述有偏差**（见下） | ⚠️ 部分 |
| 3 | `layout-doc.html:453` | `isSecureContext` 有、`execCommand` 返回值未查；OK（盲区） | L453-454 逐字一致，盲区成立 | ✅ |
| 4 | `layout-slide.html:331` | 同上（`fallbackCopy` 不查返回值）；OK（盲区） | L331-338 + `fallbackCopy` L340-346 一致 | ✅ |
| 5 | `layout-slide.html:590` | 裸调用 + 无条件 `✓`；FAIL | 一致 | ✅ |
| 6 | `layout-knowledge.html:282` | 同 #1（`showKwToast`）+ 闸门正则漏 basename；WARN | L275-283：`if (/^(https?:\|/\|~\/)/.test(target))` —— `[\w.\- ]+$` 缺失，D10 成立 | ✅ |
| 7 | `layout-table.html:1248` | 无 isSecure、`.then` 无 `.catch`；OK（盲区） | L1248-1256 一致 | ✅ |
| 8 | `layout-table.html:1277` | `shareLink` + `fallbackCopyUrl` 不查返回值；OK（盲区） | `shareLink` L1276-1284 + `fallbackCopyUrl` L1261-1270（`execCommand` 在 L1266）一致 | ✅ |

**偏差（HG-SEC-197）**：
- §1.2 表把 doc:424 写作「无条件把锚点改成 `✓`」。实测该处**无 try/catch**，非安全上下文下 `navigator.clipboard.writeText` 同步抛 `TypeError` ⇒ `anchor.textContent='✓'` **根本不可达**，失败形态是「静默无反应」（设计 §1.4 的「无反应」描述正确）；「无条件 ✓」只发生在**安全上下文但 writeText reject** 的异步路径。两种上下文被写进同一句，建议拆写。
- §1.2 表把 table 第二处记作 `layout-table.html:1262,1277`：实际 `fallbackCopyUrl` 函数体在 L1261-1270、其**调用点仅 L1281**，L1277 是 `shareLink` 的存在性判断（已单列为第 8 行）。行号引用错位，不影响结论。

**「判级盲区」4 处**（doc:453 / slide:331 / table:1248 / table:1277-1278）经读探针源码 `_classify()` 确认：只匹配 `isSecureContext` / `execCommand('copy')` / `GM_setClipboard` / `ClipboardItem` 标记串，**不检查回退返回值与失败反馈** ⇒ 盲区定性 ✅ 成立，设计「比巡检口径更严」的自述为真。

---

## 4. §3 canonical 块规格 —— 机制原型实证（本批最关键项）

方法：scratch 副本（`cache/scratch/cl015/copy`，**仓库文件零改动**）内把 §3 块原文插入 `layout-doc.html` 的 IIFE 顶层，并按 §4 改写 2 个调用点（#1 标题点击、#2 锚点 `onOk`），用项目自带 headless Chrome 实跑。夹具即设计 §6 手法。

| 断言 | 实测 | 判定 |
|:--|:--|:--|
| 块外零 `navigator.clipboard`（块内 3 次） | 原型产物 `navigator.clipboard` 出现 6 次 = 块内 3 + 未改写的 2 调用点 3（原型只改 2/3 处，非守卫失败） | ✅ 规格自洽（`grep -o \| wc -l` 期望值与块内计数一致） |
| 非安全上下文必须走回退、不得依赖 `catch` | 夹具（`isSecureContext=false` + `clipboard=undefined`）→ 点击标题：`__execCalled=1`（回退被调用）+ toast `已复制: usage-guide.md` | ✅ **机制成立** |
| 失败路径可见反馈（禁假成功） | 真 LAN origin `/…` 无夹具：`isSecureContext=false`、`clipboard=undefined` → 点击标题 toast = `已复制: usage-guide.md`（**修前假成功端到端复现**）；canonical 块侧 `execCommand→false` 时 toast = `复制失败，请手动选中文本复制` | ✅ 修前红、修后绿 |
| D5 `onOk`：`✓` 仅在真成功出现 | 锚点（`a.anchor-link`）成功：spy>0 且文本变 `✓`；刻意 `execCommand→false`：文本保持 `¶` + toast `复制失败，请手动复制链接` | ✅ **D5 语义成立**（消灭锚点处假成功） |
| T5–T10 注入手法可行性 | `Object.defineProperty(window,'isSecureContext',{value:false,configurable:true})` 与 `Object.defineProperty(navigator,'clipboard',{value:undefined,…})` 均**不抛错**、生效；`document.execCommand` 实例覆写生效；`file://` 真环境 `isSecureContext=True` / `clipboard=[object Clipboard]`（夹具与真环境可区分） | ✅ 可行 |
| T11 前提 | `python3 -m http.server --bind 0.0.0.0 --directory <repo>` → `http://192.168.31.178:8917/demos/usage-guide.html`：`isSecureContext=false`、`navigator.clipboard=undefined` | ✅ 前提为真 |
| T11 SKIP 设计的必要性 | 复算期间本机 **8899 端口正被他人进程占用**（`lsof` 显示 PID 56788 非本会话），换 8917 才可跑 | ✅ SKIP 分支确有必要（非过度设计） |
| A/B 负例（修前必须转红） | 现行产物 + 夹具 → spy=0 且 toast 仍报「已复制」；真 LAN origin → 同样假成功 | ✅ 负例成立且可判 |

**S1–S7 可断言性**：S1/S2（标记成对 + sha256 集合）、S4（`if (ok)`）、S5（失败文案常量）、S7（函数头）均为纯文本断言，可实施；S3（`isSecureContext` 行号 < `writeText` 调用行号）在块内成立；S6 计数与 A3-2 期望值 3 一致（四模板现值 doc 4 / slide 3 / table 5 / knowledge 1 → 收敛后均 3）。

**遗留面**：① 插入锚点未规定（见 HG-SEC-191）；② `readonly` + `select()` 移动端（见 HG-SEC-192）；③ T9① 夹具缺 `isSecureContext=true`（见 HG-SEC-190）。

---

## 5. §5 重生成矩阵 78 数 —— 逐条复算（本报告扣分主项）

对 43 个 demos 产物（25 doc + 4 knowledge + 14 table）在 scratch 内**用真实 CLI 重生成**并逐字节 diff（`slide-demo.html` 无 md 源，`prompts/` 用 `--site` 单测，`demo --rebuild` 用副本单测）：

| 生成器 | 设计命令 | 实测结论 |
|:--|:--|:--|
| doc | `html-gen doc -i demos/<x>.md -o demos/<x>.html`（不带 `--title`，复现原 title） | md 源 **25/25 齐全** ✅；title 全部可由 md h1 复现 ✅；但 **10/25 需补 `--github-url`**（否则抹掉 GitHub corner），且其中 9 个产物 favicon link 位置与现行不同（陈旧） |
| knowledge | `html-gen knowledge -d … -g … -o …` | **4/4 缺 `--title`/`--subtitle`/`--welcome`**：按原文执行 → 标题退化为「知识库」、欢迎语退化为默认（用户可见回归）；`data/_<x>-kb-data.json` + `_<x>-groups.json` **4/4 齐全** ✅；补参后 cloudwise-business-analysis **byte-IDENTICAL** |
| table | `html-gen table -d data/_<x>.json`（顶层 `output` 已带；无则显式 `-o`） | **「顶层 `output` 已带」与实测不符**：8 个表数据 JSON 全部**无** `output`（须全部显式 `-o`）；且 **14/14 缺 `--title`**（如 provinces 现行 title「中国省份速查表」不可复现）+ 部分缺 `--github-url`/`--home-url`；countries-table 补 `--github-url + --home-url` 后 **byte-IDENTICAL**（反证参数集缺项） |
| demo | `html-gen demo --rebuild` | ✅ **3/3 产物 byte-IDENTICAL**（副本实跑），`demos/index.html` 未变、featured 15 集稳定 |
| slide | 无 md 源 ⇒ 手工同步 | ✅ 成立（`demos/slide-demo*` 仅 `.html`，全仓无生成脚本引用） |
| prompt | `html-gen prompt --site` | ✅ 22/31 byte-IDENTICAL；9 个 `kb/*.html` 各差 2 行 = doc 模板 meta 行（`创建/编辑` 取 md 文件 mtime，重生成后为当日）⇒ 「meta 时间戳」差异真实且可解释 |
| 打包 | `build-package.py` | `src/html_gen/**` 0 tracked ✅；但未重建则已装 CLI 仍产旧代码（见 HG-SEC-199） |

**陈旧产物实测（关键新证据）**：补齐「回收到的参数集」后逐文件分类 ——

- **IDENTICAL 18**（可复现，但参数集未记录于设计）
- **仅 favicon 位置差异 2**（`knowledge-guide` / `usage-guide`，2 行、字节长度不变）
- **STALE-DIFF 22**（差异 10–728 行，与当前模板/样式基座不一致）：doc 7（`chaitin/menu-design`、`markdown-spec`、`slide-guide`、4 个 drama overview，各 10 行：`.home-link` CSS 基座缺失 + favicon 顺序）、knowledge 3（`chaitin-business-analysis` 61 / `drama-knowledge` 61 / `knowledge-demo` 69 行）、table 12（`provinces`/`table-features`/`table-actions`/`hermes-profile-skills` 各 321 行含 `--text-primary` 等 CSS 变量基座缺失；8 个 drama 表 168–728 行）

⇒ **「重生成后逐文件只差 canonical 块 + meta 时间戳」这一纪律前提对 22/43（51%）不成立**。不阻断机制，但直接决定 [3/6]/[4/6] 的工作形态与 [5/6] 审计可判性（详见 HG-SEC-187/188）。

**78 数**：`doc 25 + knowledge 4 + table 14 + demo 3 + slide 1 + prompts 31 = 78`，但 `demos/demos-index.html` 同时出现在 **table 行（14）** 与 **demo 行（3）** ⇒ 去重后 **77 个 tracked 产物**（44 demos + 31 prompts + `data/_demos-data.json` + `demos/_registry.json`）。见 HG-SEC-195。

---

## 6. §6 测试计划 / §7 验收 —— 可实现性复算

| 项 | 实测 | 判定 |
|:--|:--|:--|
| T1–T4 静态不变量 | S1–S7 均为文本可断言；块内 3 次计数与 A3-2 一致 | ✅ 可实现（T4 例外见 HG-SEC-189） |
| T5–T10 夹具 | 注入手法实测可行（§4 表） | ✅ |
| T9① 「clipboard 存在但 reject」 | §6 夹具**固定** `isSecureContext=false` ⇒ canonical 块直接走 `else { fallback(); }`，**永不触达 `writeText().catch()` 路径**，该用例为空转；须加 `secure` 变体夹具（`isSecureContext=true` + `writeText` 返回 reject 的 Promise） | ⚠️ 需补（HG-SEC-190） |
| T10 反向断言（无假成功） | 修前红/修后绿已实证 | ✅ |
| T11 SKIP 分支 | 实测本机 8899 被他人进程占用 ⇒ SKIP 设计必要；且前提（LAN → 非安全上下文）为真 | ✅ 不构成 CI 硬失败 |
| A3-1 只读探针 | 独立复跑得同一组数（88/47/38）；`git -C ../script-miner status --short` **空**（零写他仓） | ✅ 可复跑 |
| A3-2 不变量计数 | 四模板当前 4/3/5/1 → 收敛后均 3，期望值 3 正确 | ✅ |
| A3-3 `node --check` + 全量 pytest | `node v26` 可用；`pytest --collect-only` = **334 tests**（与 AGENTS.md 一致） | ✅ |
| A4 巡检 `--self-test` | 脚本内嵌 5 例（FAIL/WARN/OK/OK/NOFINDING） | ✅ |

---

## 7. 安全事项（findings）

编号自 `HG-SEC-187` 起续号（全仓最大已用 186）。

### 🔴 阻塞项：0

### 🟡 非阻断（建议在 [3/6] dev 前折入设计补记 / 实施时落地，不重开评审轮）

| 编号 | 严重度 | 描述（证据） | 处置建议 |
|:--|:--|:--|:--|
| **HG-SEC-187** | 🟡 非阻断 | **§5 重生成矩阵命令集不完整、按原文执行会产出回归产物**。实测：knowledge 4/4 缺 `--title/--subtitle/--welcome`（执行后标题退化为「知识库」、欢迎语变默认）；10/25 doc 缺 `--github-url`（抹掉 GitHub corner）；14/14 table 缺 `--title`（如 provinces 丢「中国省份速查表」）+ 部分缺 `--github-url`/`--home-url`。反证：`countries-table` 补 `--github-url + --home-url` 后 byte-IDENTICAL；`cloudwise-business-analysis` 补 `--title + --welcome` 后 byte-IDENTICAL | §5 增「逐产物**实测参数集**」表（本报告 §5 已回收并可复算），并把纪律 2「先试跑 1 个」明确为「先试跑**每种生成器 1 个 + 参数最全的 1 个**」 |
| **HG-SEC-188** | 🟡 非阻断 | **§5 纪律 1 前提（「只差 canonical 块 + meta 时间戳」）对 22/43 产物不成立**：补齐参数后仍有 10–728 行差异（`.home-link` CSS 基座、`--text-primary` 等样式变量、模板特性历史漂移），仅 18 个 byte-IDENTICAL、2 个仅 favicon 顺序差 2 行 | ① [3/6] 先做一次**零改动基线重生成**（当前模板 × 当前数据）并单独成笔，把历史漂移与 canonical 改动分离；② 或明确「本批接受历史漂移并入同一笔」并在提交消息/审计报告中登记差异白名单（否则 [5/6] 无法区分 canonical 改动与顺带漂移） |
| **HG-SEC-189** | 🟡 非阻断 | **A3/T4「产物面 0 FAIL / 0 WARN」在 `demos/usage-guide.html:961` 不可达**：该处是 md **正文 prose** 提及（源在 `demos/usage-guide.md:274`，非 §G 所写「md:961」），探针按花括号启发式判 **FAIL**（`blocklen=34709`，不含 `isSecureContext`/`execCommand('copy')`）。§G 只说「订正表述」未给出**判级可达**的写法 | 改写该行为含 `document.execCommand('copy')` 字面量的表述（例：「…在 `http://` 等非安全上下文下不可用，须先 `window.isSecureContext` 前置判断，回退用 `document.execCommand('copy')`」）；行号改为 `demos/usage-guide.md:274`；并把「A3 前逐文件跑探针」写入 §5 纪律 |
| **HG-SEC-190** | 🟡 非阻断 | **T9① 夹具与用例目标不自洽**：§6 夹具固定 `isSecureContext=false`，此时 canonical 块走 `else` 分支，`navigator.clipboard.writeText(...).catch(...)` **永不被执行** ⇒ 「clipboard 存在但 reject」用例空转（不会因修复缺失而转红） | §6 增第二套夹具 `secure` 变体（`isSecureContext=true` + `navigator.clipboard={writeText:()=>Promise.reject(...)}`），T9① 用之；同理若需覆盖「安全上下文成功路径」亦须用它 |
| **HG-SEC-191** | 🟡 非阻断 | **canonical 块插入锚点未定义**（§2.A 仅说「IIFE 内」）。若落点错（如落在 IIFE 外的脚本顶层 / 第二个 IIFE 内），`typeof showToast` 解析链降级为 `console.log` 兜底——**功能静默降级但静态守卫 T1–T3 全绿**（只查块文本与出现次数） | §3 补一行规格：「插入锚点 = 主 IIFE 内、toast 函数声明之后（或 IIFE 顶层），缩进 2 空格」；并让 T3 增加「解析链命中」断言（如块内 `showToast` 名字在块所在作用域已被声明，或由 T5/T8 行为断言兜住） |
| **HG-SEC-192** | 🟡 非阻断 | **canonical 块新增 `readonly`，移动端兼容未验证**：现行三处回退实现均**无** `readonly`；iOS Safari 对 `readonly` textarea 的 `select()`/`execCommand('copy')` 有已知不生效的报告（常见 workaround：`readOnly=false` 临时置位或 `contentEditable`）。T11 只覆盖桌面 LAN，A2 亦为桌面 | ① 显式登记为「未验证面（移动 Safari）」；② 或去掉 `readonly`、或补 `ta.focus()` + 兼容分支；③ T11 的 SKIP 说明中注明移动端不在覆盖范围（避免被读成「已端到端验证」） |
| **HG-SEC-193** | 🟡 非阻断 | **D8/G 的版本同步面漏 1 处**：`html-gen.py:12` 模块 docstring `版本: 3.3(2026-08-28)` 未列入（D7「4 处常量」实为 5：`html-gen.py:12/17/18` + `README.md:39` + `README.zh.md:39`）。该 docstring 行不参与 `help`/`version` 输出（banner 取自 `__version__`/`__release_date__`，已实测），故为源内自述漂移 | G 节同步面补 `html-gen.py:12`；或删去 docstring 中重复的版本行（改为不写死），根治 |
| **HG-SEC-194** | 🟡 非阻断 | **文档同步面不完整**：① `skills/html-gen-doc/SKILL.md:57`「标题点击复制路径 / 代码复制 (clipboard + fallback)」与 `skills/html-gen-table/SKILL.md:140`「clipboard + execCommand fallback」为剪贴板行为描述面（且这两份 SKILL.md 会流入 `prompts/`，重生成后与源码不一致）；② `features.md:44/120/190` 三行描述的是旧形态（`clipboard API try/catch fallback`、`copyAction() clipboard fallback`），D8 仅「新增一行」未订正既有三行；③ `html-gen help <type>` 契约段（`TEMPLATE_CONTRACT`）实测无剪贴板键（仅 `copyKey`/「复制」动作标签，与本机制无关）⇒ 应**显式写明「不动」**而非沉默略过 | §G/§10 补：skills 两行 + features.md 三行按 canonical 口径订正；§10 第 7 笔显式列 `skills/**/SKILL.md`（若改则需重跑 `prompt --site`）；help 契约段标注「本批不动（无剪贴板键）」 |

### 🟢 记录（record，非阻断）

| 编号 | 描述 | 处置 |
|:--|:--|:--|
| **HG-SEC-195** | **78 数重复计 1**：`demos/demos-index.html` 同时计入 §5 table 行（14）与 demo 行（3）⇒ 去重后 **77** 个 tracked 产物（44 demos + 31 prompts + `_demos-data.json` + `_registry.json`） | §5 标题与 D9、§10 第 4 笔提交消息的「78 文件」改 77（或不写数） |
| **HG-SEC-196** | §5 prompts 行枚举漏 `prompts/_kb-data.json`、`prompts/_kb-groups.json`（总数 31 正确）；table 行括注「顶层 `output` 已带」与实测不符（**8/8 表数据 JSON 均无 `output`**，须全部显式 `-o`；`data/_demos-data.json` 无 output 亦为 AGENTS.md 既定事实） | 括注改为「全部无 `output`，须显式 `-o`」并补枚举 2 文件 |
| **HG-SEC-197** | ① §1.2 doc:424「无条件把锚点改成 `✓`」把两种上下文混写：非安全上下文下 `✓` 赋值**不可达**（同步抛 TypeError，无 try/catch），实为「静默无反应」；「无条件 ✓」只见于「安全上下文 + writeText reject」异步路径。② §1.2 表 table 第二处行号 `1262,1277` 错位（函数体 1261-1270、调用点 1281） | 拆写两句 + 行号订正；结论（FAIL/盲区定性）不变 |
| **HG-SEC-198** | §2.A 写「收敛后每个模板仅剩 **1 个 `navigator.clipboard` 出现位置**」，与 S6 / A3-2 的「**块内 3 次**」措辞不一致（位置 vs 次数） | 统一为「块内 3 次出现（2 次守卫判断 + 1 次调用）」 |
| **HG-SEC-199** | `src/html_gen/`（gitignored 打包源，`.gitignore:37`）未在 §10 提交计划中重建；实测 `~/.local/bin/html-gen` 已安装（`html-gen v3.3 (2026-08-28)`）⇒ 根模板修好后，**已装 CLI 仍会生成旧剪贴板代码**（HG-SEC-069 同族，非本批 git 交付问题） | 发版前重跑 `python3 scripts/build-package.py` + 按安装方式重装；建议 §5 打包行补「发版前必须同步」（不产生提交） |
| **HG-SEC-200** | `CL016` **编号双语义**：`hm loop next-code` 返回 `HTML-GEN-CL016`（台账下一号），而仓库内 `html-gen.py:17-18` 注释与 AGENTS.md 已把「CL016」用作**版本子命令的内部编号**（`ddb168e feat@cli: version constants + version subcommand (CL016)`） | 留档；[3/6] 若触发 `hm loop` 自动取号，建议显式说明两者不同体系（避免撞名混淆） |
| **HG-SEC-201** | §5 doc 行「不带 `--title`，复现原 title」实测成立（25/25 的 `<title>` 与 md h1 一致），但 `--subtitle` 未评估；`demos/chaitin/menu-design.html` 等 9 个产物的 favicon link **位置**与当前模板注入位不一致（2 行、字节长度不变） | 记入 HG-SEC-188 的差异白名单；重生成后按「允许差异清单」核对 |

---

## 8. 维度评估

| 维度 | 评估 | 依据 |
|:--|:--|:--|
| **机制成立性** | ✅ 强 | canonical 块 scratch 原型 4/4 断言通过；回退可达、失败可见、D5 `onOk` 条件反馈均实证；`typeof` 解析链在四模板（含 table `window.showToast` 命中）可成立 |
| **问题定性准确性** | ✅ 强 | 真非 localhost origin（LAN IP + http.server）端到端复现假成功；`file://` 属安全上下文（`isSecureContext=True`）与设计前提一致 |
| **判据可复跑性** | ⚠️ 中（§5 除外） | 事实卡 11/14 逐字成立；A3/A4 全部可复跑且只读探针零写他仓；但 §5 命令集缺参（187）、纪律前提与实测不符（188） |
| **覆盖完整性（§1.2/§1.3）** | ✅ 好 | 8 调用点无漏；自查全仓 `execCommand('copy')` 未见清单外**模板/产物**调用面；`prompts/kb/pages-index.html:550/551` 为 skill 文档的示例代码（探针判 OK，不需改动）；`data-copy` 属性入口仅存在于根 `index.html`/`demos/index.html`（D6 不动，已合规） |
| **安全面** | ✅ 好 | `ta.value = text` 非 `innerHTML` ⇒ 任意文本（含 `<script>`/`</textarea>`）不解析、不可执行；`ta.style.cssText` 为常量；`readonly` 为唯一新引入行为（192）；toast 走 `textContent`（doc/slide/knowledge/table 四模板均已实测为 `textContent`，无 XSS 注入面） |
| **风险面（顺带漂移）** | ⚠️ 中 | §5 三条纪律**只能检测、不足以兜住**：需先做基线对齐或登记差异白名单（188）；`demo --rebuild` 的 featured 集稳定性前提已实证为真（`demos/index.html` 只读入不写出） |
| **跨仓边界** | ✅ 清晰 | P1/P2/P3 三处偏差登记理由站得住（F2/F3/F4 复算一致）；T1 改口径后 §7 验收**只读探针零写他仓**已实证（`git -C ../script-miner status --short` 空） |

---

## 9. 评分

| 项 | 分值 | 得分 |
|:--|:--|:--|
| 机制成立性（canonical 块 + 回退 + 反馈 + D5） | 30 | 30 |
| 问题定性与范围校正（8 调用点 / 34+ 产物 / 三处偏差） | 20 | 20 |
| 判据可复跑性（§7 验收 + §9 事实卡） | 20 | 16 |
| 覆盖完整性（§1.2/§1.3/文档面/遗漏面） | 15 | 11 |
| 风险与纪律充分性（顺带漂移、meta 时间戳、featured 稳定性） | 15 | 8 |
| **合计** | **100** | **85** |

评级 **B（PASS）**：无阻塞项；🟡 均为「实施时落地 / 折入补记」级，不改变 T1+D1..D10 的机制与决策。

---

## 10. 结论与处置

- **结论：✅ PASS 85/100**（0 🔴 / 8 🟡 非阻断 / 7 🟢 record）
- **PASS 依据**：核心机制经 scratch 原型与真 origin 端到端实证；决策 T1+D1..D10 无需重裁；未发现第 4/5 处漏列调用面；验收命令可复跑且零写他仓。
- **处置建议（不重开评审轮，[3/6] dev 前折入）**：
  1. §5 补「逐产物实测参数集」表（187）+ 差异白名单/基线对齐步骤（188）；
  2. `usage-guide.md:274` 改写为判级可达写法 + 行号订正（189）；
  3. §6 补 `secure` 变体夹具（190）+ §3 补插入锚点规格（191）+ §3 登记移动端未验证（192）；
  4. G 节补 `html-gen.py:12`（193）+ skills/features 文档面（194）；
  5. 🟢 195–201 随笔订正/留档。
- **待处置编号归属**：HG-SEC-187..194 → 归属 [3/6] dev（折入实施）；HG-SEC-195..201 → 归属同批笔 4/6/7（文档与计数订正）；HG-SEC-199 → 归属发版流程（非本批提交面）。
- **报告**: `documents/review/html-gen-clipboard-fallback-design-review-v1.1-20260927.md`

---

## 附录 A：本报告复算命令（可复制）

```bash
# A-1 本仓判级基线（只读探针，内存改 REPO，零写盘）
cd ~/CodeSpace/html-gen.cli && python3 - <<'PY'
import importlib.util; from pathlib import Path
p = Path.home()/"CodeSpace/script-miner/efficiency/clipboard-fallback-check.py"
s = importlib.util.spec_from_file_location("c", p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
m.REPO = Path.cwd(); f = m.scan(None)
print(len(f), {lv: sum(1 for x in f if x['level']==lv) for lv in ('OK','WARN','FAIL')})
PY
# A-2 他仓零写断言
git -C ~/CodeSpace/script-miner status --short          # 期望：空
# A-3 调用点与块外出现次数
grep -n 'navigator\.clipboard' layout-*.html
for f in layout-doc.html layout-slide.html layout-table.html layout-knowledge.html; do
  echo "$f: $(grep -o 'navigator\.clipboard' $f | wc -l)"; done
# A-4 版本同步面（实测 10 处字面量点）
grep -rn '3\.3\|2026-08-28' --include=*.py --include=*.md . | grep -v '^\./cache/' | grep -v '^\./prompts/'
# A-5 全量回归 + 收集数
python3 -m pytest tests/ -q --collect-only | tail -1        # 334 tests
python3 -m pytest tests/ -q -n 4
# A-6 重生成可复现性抽查（scratch 输出，不动仓库文件）
python3 html-gen.py doc  -i demos/usage-guide.md  -o /tmp/x.html --github-url https://github.com/imjaden/html-gen.cli --home-url https://html-gen.cli.jaden.tech/
python3 html-gen.py table -d data/_countries-data.json -o /tmp/y.html --github-url https://github.com/imjaden/html-gen.cli --home-url https://html-gen.cli.jaden.tech/   # 期望 byte-IDENTICAL
python3 html-gen.py knowledge -d data/_cloudwise-kb-data.json -g data/_cloudwise-groups.json -o /tmp/z.html --title '云智慧 · 商业分析' --welcome '从上方类目选择，浏览公司概况、产品体系、经营分析与生态合作。'   # 期望 byte-IDENTICAL
# A-7 非安全上下文端到端（T11 前提；注意 8899 可能被占用）
python3 -m http.server 8917 --bind 0.0.0.0 --directory ~/CodeSpace/html-gen.cli   # 另开终端
# 浏览器打开 http://192.168.31.178:8917/demos/usage-guide.html → 控制台 window.isSecureContext === false
```

## 附录 B：本报告使用的 scratch 副本（仓库零改动）

- `~/.hermes/profiles/review/cache/scratch/cl015/{doc,kb,tbl}`：重生成输出
- `~/.hermes/profiles/review/cache/scratch/cl015/copy/`：仓库最小副本（用于 `demo --rebuild` 与 canonical 块原型）
- `~/.hermes/profiles/review/cache/scratch/cl015/proto_test.py`：机制原型 + Selenium 断言脚本
- 复核：`git status --short` 空；`git -C ~/CodeSpace/script-miner status --short` 空
