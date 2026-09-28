# html-gen 剪贴板回退统一设计 v1.2（canonical copyText）

> 日期: 2026-09-27（v1.2 补记 2026-09-28）
> 状态: 设计 v1.2 —— **决策已定稿 + [2/6] 评审 PASS 85/100·B（`4db7089`，0 阻塞）；[3/6] dev 待放行**
> 闭环: **HTML-GEN-CL015**（kind=independent；编号已就位，见 §9 F1）
> 来源: 跨仓转交件 `~/CodeSpace/script-miner/cache/handoff/prompt-dev-html-gen-doc-clipboard-fallback-20260927.md`
>       （2026-09-27 20:45 CST，源自 SCRIPT-MINER-CL042 全仓巡检 `efficiency/clipboard-fallback-check.py`）
> 前置: CL009/CL010/CL011/CL012/CL013/CL014 已闭环；SCRIPT-MINER-CL042 已交付（`ffd325f` + `2d69d2d`，对方本地未推）
> **与交接件的偏差**: 交接件只列 2 处（`layout-doc.html:315` / `layout-slide.html:590`）且验收要求
>   修改 script-miner 仓文件；**本设计按本仓实测把范围校正为 4 模板 8 处 + 78 个产物**，并把验收口径
>   改回「本仓可达」（§1.3 / T1）。偏离处均显式标注，供评审逐条裁定。
>   注: **T1 定稿 = 采用推荐**（改口径），即上述偏差已被用户认可为设计基线。
> 开放决策项: **无**（T1 + D1..D10 已于 2026-09-27 全部 pin，见 §0.2 / §0.3）
> 基线链: v1.0（`0c6acdb`，`docs@design`，设计初稿）→ v1.1（`dc14a38`，决策定稿）→ **v1.2（评审 findings 折入，本版；§0.4 为 [3/6] 唯一口径源）**

---

## 0. 变更摘要

### 0.1 本版要点（v1.0 立论；v1.1 = 决策定稿，内容不变）

1. **问题定性**：`navigator.clipboard` 仅在安全上下文（https / localhost / file://）存在；`http://<局域网 IP
   或自定义域名>` 下它是 `undefined`，调用处直接抛 `TypeError`。写在 `try/catch` / `.catch()` 里的兜底
   **永不可达** ⇒ 静默失效；更有「catch 吞错 + 无条件提示已复制」= **假成功**。
2. **范围校正**（本仓同款巡检实测，§9 F2）：源面 **FAIL 2 / WARN 2**、产物面 **FAIL 38 / WARN 47**；
   交接件所列「9 文件」全部在 **script-miner 仓**（其自有 vendor 副本 + 手写页），与「只改本仓」边界冲突。
3. **修法**：四模板 **8 个调用点**全部收敛到**同一份 canonical `copyText` 块**（安全上下文前置判断 +
   `execCommand('copy')` 回退且**检查返回值** + 失败**可见反馈**），并把「块外零 `navigator.clipboard`」
   变成可断言的**不变量**（守卫测试 + 巡检双侧）。
4. **产物**：模板 JS 逐页内嵌 ⇒ 需重生成 **78 个 tracked 产物**（§5）；其中 `demos/slide-demo.html`
   无 md 源（手工同步）、`prompts/` 走 `prompt --site`。

### 0.2 决策定稿表（用户 2026-09-27 pin：T1 = 采用推荐；D1..D10 = 全采推荐）

> 定稿纪律：**已 pin 项即设计基线，[3/6] dev 按本表逐条落地**；另有偏离须在设计稿登记 ⚠️ 并说明理由，
> 不得静默更换（无澄清条款）。未采纳备选列仅作留痕。

| 编号 | 决策 | **定稿（pin）** | 未采纳备选 | 影响面 |
|:--|:--|:--|:--|:--|
| **T1** | 交接件验收条款（script-miner 巡检 `--only skills/ --only tool-nav-manager/` FAIL 归零）与「只改本仓」边界**冲突**（那 9 个文件全在他仓） | **改口径**：本仓侧以同款巡检（只读探针 / `--root`）验收；他仓 9 文件转交 script-miner（其 CL043 已登记）+ 回执 | 保持交接件原文（= 必须改他仓，越界） | 验收定义 |
| **D1** | 收敛范围 | **四模板 8 处全部收敛**（含当前判级 OK 的 4 处，换取「块外零出现」不变量） | 仅修 4 处不合格点 | 模板改写面 |
| **D2** | 共享方式 | **每模板内联同一 canonical 块 + 守卫测试逐字节比对**（模板保持自包含单文件） | 抽公共 JS 由 `html-gen.py` 注入（新机制：4 子命令 + 占位符协议） | 架构 |
| **D3** | toast 适配 | canonical 块内 `typeof showToast/showKwToast` **解析链**（保持四份块逐字节一致） | 每模板各写一行 `_toast` 别名（块不再逐字节一致，守卫需放宽） | 守卫强度 |
| **D4** | 失败反馈 | 统一 `failMsg` 默认「复制失败，请手动选中文本复制」；成功文案由调用点传入 | 各页自拟文案 | 文案 |
| **D5** | TOC 锚点 ✓ 语义 | 新增**可选第 4 参 `onOk`**：✓ 仅在**真成功**时出现（消灭锚点处的假成功） | 保留现状（点击即 ✓，与「禁止假成功」冲突） | canonical 签名 |
| **D6** | 落地页两处（`index.html` / `demos/index.html`） | **本批不动**（已合规：execCommand 回退 + 返回值检查；且双源同步成本高、交互语义不同） | 一并统一 | 双源同步 |
| **D7** | 版本号 | `3.3(2026-08-28)` → **`3.4(2026-09-27)`**（4 处常量 + 6 处断言同步） | 保持 3.3 至下次发版 | 发布面 |
| **D8** | 「changelog」落点 | 本仓**无 CHANGELOG 文件**（实测）；落 `features.md` 一行 + commit message | 新建 `CHANGELOG.md` | 文档面 |
| **D9** | 产物重生成范围 | **全量**（78 tracked 产物，§5 矩阵） | 仅重生成「有 FAIL/WARN」的产物（= 全部，结果相同） | 提交体积 |
| **D10** | `layout-knowledge.html` 标题复制**闸门正则**缺陷（`^(https?:\|/\|~/)` 不匹配脱敏 basename ⇒ 静默无反应；doc 侧已有 `[\w.\- ]+$` 兜底） | **纳入本批**（同函数、同批、低风险） | 折入另批 | 功能面 |

### 0.3 修订记录

| 版本 | 触发 | 处理 |
|:--|:--|:--|
| v1.0 → **v1.1** | 用户 2026-09-27 pin 回合：`1 采用推荐`（T1）+ `2 全采推荐`（D1..D10）+ `4 押后`（script-miner 转交回执） | ① T1 定稿为「改口径」，§1.3 三处偏差随之成为**设计基线**（不再是待裁定项）；② D1..D10 全部按推荐项定稿（§0.2 表头改「定稿（pin）」+ 新增定稿纪律条）；③ 状态行改「决策已定稿，待评审」；④ 开项清空；⑤ **内容零变更**（仅决策状态与修订记录）——[2/6] 评审基线 = 本版 `git rev` |
| v1.1 → **v1.2** | [2/6] 设计评审（review role，`4db7089`）**PASS 85/100·B**，0 🔴 / 8 🟡（187–194）/ 7 🟢（195–201）；用户 2026-09-28 回合 `2 全采推荐` 授权全自动落地 | ① 新增 **§0.4 补记**为 [3/6] 唯一口径源（§5 逐产物实测参数集 + 4 个 strategy 表例外 + 零改动基线实测 + 其余 10 条规格补记）；② 头部状态与基线链更新；③ **决策定稿表（§0.2）零变更**，不重开评审轮；④ §5 纪律 2 升格（补「参数最全的 1 个」试跑）|

### 0.4 v1.2 补记 —— [2/6] 评审 findings 187–201 折入（PASS 85/100 · `4db7089`）

> 触发：design-review v1.1 **PASS 85/100·B**（0 🔴 / 8 🟡 / 7 🟢）。**不重开评审轮**：🟡 187–194 折入 [3/6] 实施；
> 🟢 195–201 折入同批文档/计数笔；199 属发版流程（非本批 git 面）。
> **冲突条款：本节与 §1–§11 不一致时，一律以本节为准。**

#### A. §5「逐产物实测参数集」（answer HG-SEC-187；★ = v1.1 缺项，按原命令执行即回归）

| 生成器 | 实测命令 | 数 |
|:--|:--|:--|
| doc | `html-gen doc -i demos/<x>.md -o demos/<x>.html` + `[--subtitle "<sidebar sub>"]` + `[--github-url <corner href>]` | 25 |
| knowledge | `html-gen knowledge -d data/_<x>-kb-data.json -g data/_<x>-groups.json -o demos/<x>.html ★--title "<title>" [★--subtitle] [★--welcome] [--github-url]` | 4 |
| table | `html-gen table -d data/_<x>.json -o demos/<x>.html ★--title "<h1>" [--subtitle "<table-desc>"] [--github-url] [--home-url]` | 13 |
| demo | `html-gen demo --rebuild` | 3 |
| slide | **无 md 源** ⇒ 手工同步 canonical 块 | 1 |
| prompt | `html-gen prompt --site` | 31 |
| 打包 | `scripts/build-package.py`（`.gitignore:37` ⇒ 0 tracked） | 0 |

- **参数回收纪律**：参数**只能从产物自身回收**（`<title>` / `<h1>` / `.table-desc` / `div.sub` / `.w-sub` /
  `github-corner` href / `.home-link` href），禁凭记忆拼；`data/_*.json` 顶层 **8/8 无 `output`** ⇒
  table 一律显式 `-o`（订正 §5 括注与 table 行枚举，HG-SEC-196）。
- **表 → 数据源映射**：`demos/<x>-table.html` ← `data/_<x>-data.json`；
  `demos/drama/<stem>-table.html` ← `data/_drama-table-<stem>.json`；
  4 个 KB ← `data/_<x>-kb-data.json` + `data/_<x>-groups.json`。
- ⚠️ **例外（实测不可重生成，须手工同步）**：4 个 drama strategy 表
  （`daming/history/yongzheng/zhuyuanzhang-strategy-table.html`）—— 产物为 **11 列**结构
  （`衍生词/同源意象/近义词/反义词`），而 `data/_drama-table-*-strategy.json` 为**旧 7–8 字段**口径
  （`衍生成语`）；`8b0dcc6`（2026-08-24「rebuild strategy tables to 11-col structure」）**只改了产物、未改 JSON**。
  按 §5 重生成即**内容回归**（丢 4 列），实测使 `tests/test_history_tables.py::test_07_daming_strategy`
  与 `tests/test_drama_knowledge.py::test_18_yongzheng_group` 转红 ⇒ 这 4 表本批**保持现状 + 手工同步 canonical 块**
  （与 slide 同口径）；JSON 补列另立他批。
- **纪律 2 升格**：试跑对象 = 「每种生成器 1 个 + **参数最全的 1 个**」；A3 前**逐文件**跑只读探针并记录。

#### B. 零改动基线重生成（HG-SEC-188 处置①；已在 [3/6] 前单独成笔）

阶段一实测（`cache/closed-loop/cl015-baseline-regen.py`：scratch 生成 → 逐字节 diff，零写仓）：

| 面 | 实测 | 与评审比对 |
|:--|:--|:--|
| 42 产物（25 doc + 4 kb + 13 tbl） | **IDENTICAL 18 / favicon 位置 2 / STALE-DIFF 22** | 与评审 §5 分类**逐条一致**（独立复算） |
| `prompts/` 31 | IDENTICAL 22 / DIFF 9（各 2 行 = meta 创建/编辑日期） | 一致（元数据时间戳差异） |
| `demo --rebuild` 3 产物 | **byte-IDENTICAL** | 一致（featured 集稳定） |

- **STALE 差异性质**（抽样实证）：doc 缺 `.home-link` CSS 基座（10 行）；table/kb 缺 `--text-primary` 等
  CSS 变量基座（168–728 行）；favicon `<link>` 位置前移（2 行，字节长度不变）——**全部为样式/资源层，
  零数据层差异**（数据层差异仅出现在上面 4 个 exception 表）。
- 基线笔实收 **29 tracked**（20 demos + 9 prompts）；4 个 strategy 表按 A 例外**不入基线**。
- 只读探针复算（源面 + 产物面）：**OK 104 / WARN 47 / FAIL 38**；FAIL 分布与 §9 F2 **逐条一致**
  （`layout-doc.html:424` / `layout-slide.html:590` / 产物 34 处），OK 88→104 系产物收敛到现行模板所致 —— 
  即「基线笔不改变判级口径，只消除历史漂移」，[5/6] 审计据此可区分 canonical 改动与顺带漂移。

#### C. 其余规格补记

| finding | 本批规格（覆盖原文） |
|:--|:--|
| 191 | canonical 块插入锚点 = **主 IIFE 内、toast 函数声明之后**（或 IIFE 顶层），缩进 2 空格；T3 增「解析链命中」断言（防落点错致 toast 静默降级而静态守卫全绿） |
| 190 | §6 增第二套夹具 `secure` 变体（`isSecureContext=true` + `writeText` 返回 reject Promise），T9① 用之（原夹具固定 `false` ⇒ 该用例空转） |
| 192 | 本批**保留** `readonly`；显式登记「**移动 Safari 未验证面**」，T11 SKIP 说明中注明移动端不在覆盖范围 |
| 193 | 版本同步面补 `html-gen.py:12` docstring ⇒ 本批**删除写死的版本行**（根治：5 处 → 4 处，`__version__`/`__release_date__` 为唯一来源） |
| 194 | 文档同步面补：`skills/html-gen-doc/SKILL.md` `skills/html-gen-table/SKILL.md` 剪贴板表述 2 行（会流入 `prompts/`，改后须重跑 `prompt --site`）+ `features.md:44/120/190` 三行按 canonical 口径订正 + `html-gen help <type>` 契约段（实测无剪贴板键）**显式标注「本批不动」** |
| 195/196 | 产物数 **78 → 77**（`demos/demos-index.html` 在 table 行与 demo 行重复计 1）；prompts 枚举补 `_kb-data.json` / `_kb-groups.json`；table 行括注改「全部无 `output`，须显式 `-o`」 |
| 197/198 | §1.2 doc:424 拆写两句（非安全上下文 = **静默无反应**；「无条件 ✓」仅见于安全上下文 + `writeText` reject 异步路径）+ table 行号订正（函数体 1261-1270 / 调用点 1281）；§2.A 措辞统一为「**块内 3 次（2 守卫 + 1 调用）**」 |
| 189 | A3/T4「产物面 0 FAIL/0 WARN」在 `demos/usage-guide.html:961` 不可达（该处是 md 正文 prose）⇒ 改写 `demos/usage-guide.md:274` 为含 `document.execCommand('copy')` 字面量的表述（判级可达）+ 行号订正 |
| 199 | `src/html_gen/` 打包源未重建（已装 CLI 仍产旧代码）⇒ **发版流程**：发版前重跑 `build-package.py` + 重装；非本批 git 交付面 |
| 200 | `CL016` 编号双语义（`next-code` vs `html-gen.py` 版本子命令内注释）⇒ 留档；[3/6] 如需取号显式区分 |

---

## 1. 问题

### 1.1 触发事件

script-miner 在修本仓 `tool-nav-manager` 拷贝按钮时做全仓剪贴板巡检，首跑 **OK 81 / WARN 18 / FAIL 18（14 文件）**，
其中 **9 文件根因在仓外模板（html-gen.cli）** ⇒ 以交接件形式转来本仓。交接件原文要求
「统一成一个可复用的小函数，两处模板都改为调用它」+「完成后回一条已转交落地 + 巡检复跑结果」。

### 1.2 证据链（本仓实测，见 §9 事实卡）

| 类别 | 位置 | 现象 | 巡检判级 |
|:--|:--|:--|:--|
| 假成功 | `layout-doc.html:315` | `try { navigator.clipboard.writeText(t).catch(function(){}); } catch(e) {}` 之后**无条件** `showToast('已复制: ' + t)` | WARN |
| 假成功 | `layout-knowledge.html:282` | 同上模式（`showKwToast`），**交接件未列** | WARN |
| 裸调用 | `layout-doc.html:424` | TOC 锚点 `navigator.clipboard.writeText(url);` 无判断无回退，且**无条件**把锚点改成 `✓` | **FAIL** |
| 裸调用 | `layout-slide.html:590` | 同上（交接件所列第 2 处） | **FAIL** |
| 假成功（弱形态） | `layout-slide.html:331` | 有 `isSecureContext` + `fallbackCopy`，但 `fallbackCopy` **不检查返回值**，且两条路径都 `done()` | OK（判级盲区） |
| 假成功（弱形态） | `layout-doc.html:453` | 同上（`execCommand` 返回值未检查，`fallback()` 内无条件 `done()`） | OK（判级盲区） |
| 静默 | `layout-table.html:1248` | `if (navigator.clipboard)` 无 `isSecureContext`；`.then` **无 `.catch`** ⇒ 存在但 reject 时**无任何反馈** | OK（判级盲区） |
| 假成功 | `layout-table.html:1262,1277` | `fallbackCopyUrl` 不检查 `execCommand` 返回值，仍提示「已复制链接」 | OK（判级盲区） |

> 判级盲区 = 巡检脚本只看「所在函数块是否含 `isSecureContext` 或回退标记」，**不检查回退返回值与失败反馈**。
> 本设计把「失败可见反馈」一并纳入（§3），即比巡检口径更严。

### 1.3 交接件与本仓实测的**三处偏差**（核实结论）

| # | 交接件说法 | 实测 | 处置 |
|:--|:--|:--|:--|
| P1 | 受影响 2 处（doc:315 / slide:590） | 本仓**源面 4 处不合规**（doc:315 + doc:424 + slide:590 + knowledge:282），另 4 处为假成功弱形态（§1.2） | 范围校正为 8 处（D1） |
| P2 | 受影响产物「在 script-miner 仓中实测 9 个文件 10 处」 | 本仓**产物面 FAIL 38 / WARN 47**（`demos/**` + `prompts/**` + `src/**`），交接件**完全未计本仓产物**；其 9 文件全在他仓 | 本仓产物按 §5 重生成；他仓 9 文件转交（T1） |
| P3 | 验收：`cd ~/CodeSpace/script-miner && python3 efficiency/clipboard-fallback-check.py --only skills/ --only tool-nav-manager/` 预期 FAIL→OK | 该命令扫的是 **script-miner 仓**（`REPO = Path(__file__).resolve().parent.parent` 硬编码，§9 F4），其中 `tool-nav-manager-{changelog,features}.html` 是他仓**手写页**（非本仓产物），本批**不可能**改动 | 验收改口径（T1）：本仓只读探针 + 转交他仓 |

### 1.4 影响面

- **用户可见**：以 `http://<局域网 IP>:<域名>` 访问任一生成页（本仓 78 个产物 + 他仓 vendor 副本）时，
  ① 标题点击复制路径 **完全无反应**（`TypeError` 抛出后无 catch，doc 侧连 toast 都不出）；
  ② TOC 锚点复制 **无反应**；③ doc/slide/table 多处 **提示「已复制」但剪贴板为空**（假成功，最坏形态：
  用户以为已复制 → 粘贴出旧内容）。
- **本机 localhost 预览看不出问题**（localhost 属安全上下文）⇒ 回归测试必须打在**非 localhost origin**
  或**假不安全上下文**上（§6）。

---

## 2. 设计决策

### A. canonical 块：单一实现 + 块外零出现（D1/D2）

在四模板各自的 IIFE 内**内联同一份** `copyText`（带起止标记注释），并把**所有**调用点改为调用它。
收敛后每个模板仅剩 **1 个 `navigator.clipboard` 出现位置**（canonical 块内），于是：

- 巡检判级必然 OK（块内含 `isSecureContext` + `execCommand('copy')`）；
- 可写成硬不变量：**「文件内 `navigator.clipboard` 出现次数 == canonical 块内出现次数」**（守卫测试 T2）。

> 理由（对内联方案的取舍）：模板设计上必须**自包含单文件**（AGENTS.md「模板注入机制」：输出为自包含单文件、
> 无外部依赖）。抽公共 JS 需要新增一套注入机制（4 子命令 + 模板占位符 + 打包面），收益仅是「少 3 份副本」，
> 成本与回归面显著更大 ⇒ 取「副本 + 逐字节守卫」的既有样板（本仓 `style-guide.css` 内联即同思路）。

### B. toast 适配：解析链（D3）

canonical 块内按名字解析 toast 函数（`showToast` → `showKwToast` → `console`），使**四份块逐字节一致**：

- 四模板的 `showToast` / `showKwToast` 均为 **IIFE 内函数声明**（实测 `layout-{doc,slide,table,knowledge}.html`
  的 JS 全部包在 `(function() {` 内；`showToast`/`showKwToast` 为函数声明 ⇒ **提升**，调用点前后均可解析）。
- `layout-table.html:1444` 已有 `window.showToast = showToast;`，解析链同样命中。

### C. 失败反馈：禁止假成功（D4/D5）

- `fallback()` **必须检查** `document.execCommand('copy')` 的返回值：`ok ? done() : fail()`。
- 成功文案 `okMsg` 由调用点传入（保持各页现有文案：`'已复制: ' + target` / `'已复制链接'`）；
  `okMsg` 为空串/null 时**不弹成功 toast**（如锚点场景，改由 `onOk` 回调给 ✓ 反馈）。
- 失败文案统一默认「复制失败，请手动选中文本复制」。
- **`onOk`（D5，对交接件 snippet 的偏离）**：新增可选第 4 参 `onOk`，把「成功后的界面反馈」
  （TOC 锚点 `✓` 动画、代码块按钮 `已复制`）从「无条件执行」改为「真成功才执行」——这是交接件
  snippet 未覆盖、但同属假成功类的一处（本设计主动扩大）。

### D. 安全上下文判断必须在**调用之前**（核心机制）

```js
if (navigator.clipboard && navigator.clipboard.writeText && window.isSecureContext) { … } else { fallback(); }
```

`window.isSecureContext` 为 false 时**直接走回退**，不得依赖 `.catch()`（`TypeError` 在同步阶段抛出，
promise 链根本不存在）。三条件缺一不可：
`navigator.clipboard`（存在性）/ `navigator.clipboard.writeText`（API 完整性）/ `isSecureContext`（能力前提）。

### E. table 两处（copyAction / shareLink）

- `copyAction` 删除自带 else 分支与「无条件已复制」，改调 `copyText(text, '已复制: ' + text, '复制失败')`。
- `shareLink` 改调 `copyText(url, '已复制链接', '复制失败')`；`fallbackCopyUrl` **删除**（其唯一用途被
  canonical 块承接；保留会成为第二条未检查返回值的 execCommand 路径）。
- `window.copyAction` / `window.shareLink` 两个对外名字**保持不变**（模板内联 `onclick` 与测试依赖）。

### F. 落地页两处不动（D6）

`index.html` / `demos/index.html` 自带 `copyText(text, btn)`（另一签名）：含 `execCommand` 回退 + `ok` 检查，
巡检 OK，且其交互是「按钮文字 ✅」语义，与模板的 toast 语义不同 ⇒ 本批不动（双源同步零成本）。
**注意**：其函数名与本设计 canonical 块**同名不同签名**，仅命名巧合（canonical 块在 IIFE 内为局部，
落地页为全局），守卫测试**只扫 `layout-*.html`**，不扫落地页。

### G. 版本与文档（D7/D8）

- 版本 `3.3(2026-08-28)` → `3.4(2026-09-27)`；同步面 = `html-gen.py` 常量 ×2 + `README.md:39` +
  `README.zh.md:39` + `tests/test_cli_version.py`（4 处断言）+ `tests/test_demo_cmd.py:101`。
- 本仓**无 CHANGELOG 文件**（实测 `ls *.md` = AGENTS/features/README/README.zh/review-log）⇒
  「changelog」落 `features.md` 一行 + commit message，不新建文件。
- `AGENTS.md` 为**受保护指令文件**：落地须**分小步 patch 逐次审批** + 落地后 sha256 逐字节比对
  （测试计数 334 → 334+新增；模板段补「剪贴板回退 canonical」一行）。
- `demos/usage-guide.md:961` 现有「`navigator.clipboard` 在 `http://` 非安全上下文中不可用。v1.1+ 用
  `execCommand` 兜底。」的既有表述 ⇒ 订正为 canonical 块 + 失败反馈口径，并重生成 `usage-guide.html`。

### H. 产物重生成（D9）

模板 JS 逐页内嵌（`inject()` 把模板整体写入产物）⇒ 任一模板改动都要求对应产物**全量重生成**，
禁止手改产物（AGENTS.md「模板注入机制」+ 交接件要点 ④）。矩阵见 §5。

### I. 常驻守卫（防再犯）

新增 `tests/test_clipboard_fallback.py`：**静态不变量（T1..T4）+ 行为用例（T5..T10）+ 非 localhost
origin 端到端（T11）**。意义：把「非安全上下文静默失效」从「靠人工偶遇」变成**提交即拦**（对应
script-miner 侧 SCRIPT-MINER-CL044 的同类诉求，本仓先行落地）。

### J. 巡检复跑与跨仓转交（T1）

- **本仓侧**：用 script-miner 的巡检脚本做**只读探针**（`importlib` 载入后仅改内存 `REPO`，不落文件、
  不改他仓）⇒ 断言「根模板 + 全部产物 **0 FAIL / 0 WARN**」（§9 F2 即用此法取得基线）。
- **他仓侧**：9 文件（`skills/html-templates/layout-doc.html` + `skills/html-demos/*.html` ×6 +
  `tool-nav-manager/*.html` ×2）中，7 个是**本仓模板/产物的 vendor 副本**（本仓修完重新 vendor 即可），
  2 个是他仓**手写页**（须他仓自行修）⇒ 回执里明确转交，不在本批实现。
- **建议转交项（他仓）**：巡检脚本加 `--root <dir>` 参数，使「本仓自检」不必用内存探针（属
  SCRIPT-MINER-CL042/CL044 面）。

---

## 3. canonical 块规格（逐字节，四模板一致）

```js
  /* ═══════ html-gen:clipboard-copy v1 BEGIN —— canonical, 四模板逐字节一致, 守卫测试锁定 ═══════ */
  function copyText(text, okMsg, failMsg, onOk) {
    var _toast = (typeof showToast === 'function') ? showToast
      : (typeof showKwToast === 'function') ? showKwToast
      : function (m) { try { console.log('[html-gen] ' + m); } catch (e) {} };
    var done = function () { if (onOk) onOk(); if (okMsg) _toast(okMsg); };
    var fail = function () { _toast(failMsg || '复制失败，请手动选中文本复制'); };
    var fallback = function () {
      var ta = document.createElement('textarea');
      ta.value = text;
      ta.setAttribute('readonly', '');
      ta.style.cssText = 'position:fixed;top:-1000px;left:-1000px;opacity:0';
      document.body.appendChild(ta);
      ta.select();
      ta.setSelectionRange(0, text.length);
      var ok = false;
      try { ok = document.execCommand('copy'); } catch (e) { ok = false; }
      document.body.removeChild(ta);
      if (ok) { done(); } else { fail(); }
    };
    if (navigator.clipboard && navigator.clipboard.writeText && window.isSecureContext) {
      navigator.clipboard.writeText(text).then(done).catch(fallback);
    } else {
      fallback();                       /* 非安全上下文 ⇒ 直接回退, 不得依赖 catch */
    }
  }
  /* ═══════ html-gen:clipboard-copy v1 END ═══════ */
```

**规格要点（守卫测试逐条断言）**

| # | 要点 | 断言方式 |
|:--|:--|:--|
| S1 | 起止标记存在且成对 | `grep -c 'clipboard-copy v1 BEGIN/END'` == 1/1 |
| S2 | 四模板块内文本 **sha256 相同** | 提取标记间文本 → sha256 → 集合大小 == 1 |
| S3 | `window.isSecureContext` 在调用**之前**判断 | 块内 `isSecureContext` 行号 < `writeText` 调用行号 |
| S4 | `execCommand('copy')` **返回值被检查** | 块内含 `if (ok)` |
| S5 | 失败路径产生**可见反馈** | 块内含 fail 文案常量 |
| S6 | **块外零 `navigator.clipboard`** | 文件内出现次数 == 块内出现次数（块内 3 次） |
| S7 | 签名固定 `(text, okMsg, failMsg, onOk)` | 块内函数头精确匹配 |

---

## 4. 调用点改写矩阵（8 处）

| # | 文件:行 | 现状 | 改法 | 判级 前→后 |
|:--|:--|:--|:--|:--|
| 1 | `layout-doc.html:315` | 标题点击：`try{…catch(noop)}` + 无条件 `showToast('已复制: '+t)` | `copyText(target, '已复制: ' + target)` | WARN → OK |
| 2 | `layout-doc.html:424` | TOC 锚点：裸 `writeText(url)` + 无条件 `✓` | `copyText(url, null, '复制失败，请手动复制链接', function(){ ✓ 动画 })` | **FAIL** → OK |
| 3 | `layout-doc.html:453` | 代码块按钮：内联 done/fallback（返回值未查） | `copyText(text, null, null, function(){ btn.textContent = '已复制'; … })` | OK（盲区）→ OK |
| 4 | `layout-slide.html:331` | 标题点击：isSecure + `fallbackCopy`（返回值未查） | `copyText(path, '已复制: ' + path)`；删 `fallbackCopy` | OK（盲区）→ OK |
| 5 | `layout-slide.html:590` | TOC 锚点：裸调用 + 无条件 `✓` | 同 #2（slide 版） | **FAIL** → OK |
| 6 | `layout-knowledge.html:282` | 标题点击：同 #1（`showKwToast`），**且闸门正则漏 basename** | 正则并入 doc 版 `[\w.\- ]+$`（D10）+ `copyText(target, '已复制: ' + target)` | WARN → OK |
| 7 | `layout-table.html:1248` | `copyAction`：无 isSecure、无 `.catch`、else 分支返回值未查 | `copyText(text, '已复制: ' + text, '复制失败')` | OK（盲区）→ OK |
| 8 | `layout-table.html:1277` | `shareLink` + `fallbackCopyUrl` | `copyText(url, '已复制链接', '复制失败')`；**删** `fallbackCopyUrl` | OK（盲区）→ OK |

**调用点签名用法约定**：`okMsg` 为空 → 不弹成功 toast（改为 `onOk` 承担界面反馈）；
`failMsg` 为空 ⇒ 用默认失败文案（**任何调用点都不得关闭失败反馈**）。

---

## 5. 产物重生成矩阵（78 tracked 文件）

| 生成器 | 命令 | 产物 | 数 |
|:--|:--|:--|:--|
| doc | `html-gen doc -i demos/<x>.md -o demos/<x>.html`（不带 `--title`，复现原 title） | 6 guide + 4 drama overview + 14 cloudwise + `chaitin/menu-design.html` | 25 |
| knowledge | `html-gen knowledge -d data/_<x>-kb-data.json -g data/_<x>-groups.json -o demos/<x>.html` | `chaitin-business-analysis` / `cloudwise-business-analysis` / `drama-knowledge` / `knowledge-demo` | 4 |
| table | `html-gen table -d data/_<x>.json`（顶层 `output` 已带；无则显式 `-o`） | countries / provinces / demos-index / table-features / table-actions / hermes-profile-skills + 8 drama 表 | 14 |
| demo | `html-gen demo --rebuild` | `data/_demos-data.json` + `demos/demos-index.html` + `demos/_registry.json` | 3 |
| slide | **无 md 源** ⇒ 手工同步 canonical 块（+ 校验 style-guide 变量基座仍在，单 `<style>` 块） | `demos/slide-demo.html` | 1 |
| prompt | `html-gen prompt --site` | `prompts/`（index + kb ×9 + skills md/json + all.md） | 31 |
| 打包 | `python3 scripts/build-package.py` | `src/html_gen/**`（`.gitignore:37` ⇒ **不进 commit**，发版用） | 0 tracked |

**纪律**

1. 重生成前先 `git status --short` 记基线；重生成后逐文件确认「**只差 canonical 块 + meta 时间戳**」，
   任何别的差异都要解释（防「顺带漂移」）。
2. 每个生成器先**试跑 1 个**并与旧产物 diff 确认零语义差异，再批量。
3. `demos/index.html` 是 `demo --rebuild` 的 **featured 数据源**（只读入、不写出，`html-gen.py:1702-1716`）
   ⇒ 本批不动它，故 `--rebuild` 后 `_registry.json` 的 featured 集保持稳定（重生成后抽查 diff）。

---

## 6. 测试影响与新增用例

新增 `tests/test_clipboard_fallback.py`（拟 ~11 用例）；现有断言仅**版本号 5 处**需同步（G 节）。

| # | 用例 | 层次 | 断言 |
|:--|:--|:--|:--|
| T1 | 四模板均含成对标记 + 四份块 sha256 集合 == 1 | 静态 | S1/S2 |
| T2 | 块外零 `navigator.clipboard`（四模板） | 静态 | S6 |
| T3 | 块内规格：`isSecureContext` 先行 / `if (ok)` / 失败文案 / 签名 | 静态 | S3/S4/S5/S7 |
| T4 | 产物面：`demos/**/*.html` + `prompts/**/*.html` 每个出现点都落在块内 | 静态 | 等价巡检口径（0 FAIL / 0 WARN） |
| T5 | doc 标题点击（假不安全上下文 + clipboard 删除 + `execCommand` spy→true） | Selenium | spy 被调用 + toast == `已复制: <脱敏路径>`；**A/B 负例**：修前 spy 未被调用且 toast 仍报「已复制」 |
| T6 | doc TOC 锚点：同上 + `✓` **仅在成功**出现；`execCommand`→false 时出现失败文案 | Selenium | 假成功消除（D5） |
| T7 | slide 标题 + TOC 锚点 | Selenium | 同 T5/T6 |
| T8 | knowledge 标题点击（`showKwToast` 解析链命中）+ 闸门正则含 basename（D10） | Selenium | 解析链 + 复制确实发生 |
| T9 | table `copyAction`：① clipboard **存在但 reject**（旧代码静默无反馈）② 假不安全上下文 | Selenium | 两路都出 toast（`已复制: …` 或失败文案），**不得静默** |
| T10 | 失败路径总闸：`execCommand`→false 时**必须**出现失败文案（反向断言「无假成功」） | Selenium | 任意模板 ×1 调用点 |
| T11 | **非 localhost origin 端到端**：`python3 -m http.server <port> --bind 0.0.0.0` + `http://192.168.31.178:<port>/…`（实测本机 LAN IP） | Selenium | `window.isSecureContext === false` 且点击后 `execCommand` 被真实调用；**无 LAN IP / 端口占用 ⇒ SKIP**（保他机/CI 可跑） |

**测试注入手法（T5–T10 统一的「假不安全上下文」夹具）**

```js
Object.defineProperty(window, 'isSecureContext', { value: false });
Object.defineProperty(navigator, 'clipboard', { value: undefined });
window.__execCalled = 0;
document.execCommand = function () { window.__execCalled++; return true; };
```

> 未核实项：headless Chrome 在 `file://` 下 `execCommand('copy')` 的**真实返回值**未核实 ⇒ 统一用
> **spy 断言「行可达」**（确定性），真实复制由 T11 + 用户实机确认（A2）。

---

## 7. 验收清单（A0–A4 口径）

| 项 | 判据 | 复跑命令（可复制） |
|:--|:--|:--|
| **A0 编号就位** | `hm loop check .` 6/6 + draft 条目含 `状态:`/`闭环:` | `hm loop check .`（已实测 6/6，§9 F1） |
| **A1 事实卡** | §9 每条机制类断言附命令 + 原始输出 | §9 |
| **A2 端到端** | 真实使用路径：非 localhost origin 打开产物 → 点击 → 真复制（用户实机）+ T11 | `python3 -m http.server 8899 --bind 0.0.0.0` → `http://192.168.31.178:8899/demos/usage-guide.html` |
| **A3 出口判据** | 源面 0 FAIL/0 WARN + 产物面 0 FAIL/0 WARN + 全量 pytest 全绿 + 遗留项逐条归宿（§8） | 见下 |
| **A4 harness 自检** | 只读探针**不写他仓**（断言 `git -C ../script-miner status --short` 无新增）+ 巡检脚本 `--self-test` 5 例通过 | `python3 efficiency/clipboard-fallback-check.py --self-test` |

```bash
# A3-1 源面 + 产物面（只读探针: 仅改内存 REPO, 零写盘）
cd ~/CodeSpace/html-gen.cli && python3 - <<'PY'
import importlib.util; from pathlib import Path
p = Path.home()/"CodeSpace/script-miner/efficiency/clipboard-fallback-check.py"
s = importlib.util.spec_from_file_location("c", p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
m.REPO = Path.cwd(); f = m.scan(None)
print({lv: sum(1 for x in f if x['level']==lv) for lv in ('OK','WARN','FAIL')})   # 期望 {'OK': N, 'WARN': 0, 'FAIL': 0}
PY
# A3-2 不变量（canonical 块内 navigator.clipboard 出现 3 次: 守卫行 2 + 实调用 1）
for f in layout-doc.html layout-slide.html layout-table.html layout-knowledge.html; do
  echo "$f: $(grep -o 'navigator\.clipboard' $f | wc -l) (期望 3)"; done
# A3-3 语法 + 全量回归
node --check <(python3 - <<'PY'
import re,sys; h=open('layout-doc.html',encoding='utf-8').read()
sys.stdout.write(re.search(r'<script>(.*?)</script>', h, re.S).group(1))
PY
) && python3 -m pytest tests/ -q -n 4
```

---

## 8. 观察项与跨仓转交

| # | 观察项 | 归宿 |
|:--|:--|:--|
| O1 | 交接件验收条款（script-miner 巡检 FAIL 归零）须改口径 | 本批（T1，回执说明） |
| O2 | script-miner 9 文件：7 个 vendor 副本（本仓修完重新 vendor）+ 2 个他仓手写页 | **转交** script-miner（其 CL043 已登记；回执列清单） |
| O3 | 巡检脚本缺 `--root` 参数 ⇒ 本仓自检只能用内存探针 | **转交** script-miner（CL042/CL044 面，建议项） |
| O4 | 本仓巡检未接入提交门禁（本次靠跨仓巡检才发现） | 本批以 `tests/test_clipboard_fallback.py` T1–T4 常驻守卫承接（等价效果，零外部依赖） |
| O5 | 落地页 `index.html` / `demos/index.html` 的 `copyText` 与 canonical 块**同名不同签名** | 记录（D6 不动）；若评审要求归一，另开批（双源 + 交互语义变更） |
| O6 | `usage-guide.md` 既有表述「v1.1+ 用 execCommand 兜底」 | 本批订正 + 重生成（G 节） |
| O7 | 他仓 vendor 副本的**版本可追溯性**（其 `layout-doc.html` 与本源行号已不同） | 记录：vendor 时带源 commit 注释（建议，他仓决定） |

---

## 9. 事实卡（A1：机制类断言 = 实测命令 + 原始输出）

| # | 断言 | 命令 | 实测结果 |
|:--|:--|:--|:--|
| F1 | 编号已就位且绑定生效 | `hm loop check .` / `hm loop next-code --json` | `6/6 通过`；`next-code` → `{"status":"ok","code":"HTML-GEN-CL016","system":"PROJ-CL"}`（回 CL016 ⇒ CL015 已绑定）；`hm loop list` 显示 `HTML-GEN-CL015 [独立] ⏳ 待办` |
| F2 | 本仓判级基线：根模板 + 产物 | 只读探针（§7 A3-1 同款，内存改 `REPO`） | **OK 88 / WARN 47 / FAIL 38**（调用点 173）；FAIL 分布 = `layout-doc.html:424`、`layout-slide.html:590`、`src/html_gen/layout-{doc,slide}.html` 同两行 + 产物 34 处 |
| F3 | script-miner 基线（只读） | `cd ~/CodeSpace/script-miner && python3 efficiency/clipboard-fallback-check.py` | `OK 81 / WARN 18 / FAIL 18`（14 文件）；其中 `skills/`（7 文件）+ `tool-nav-manager/`（2 文件）= 交接件所列 9 文件 |
| F4 | 巡检脚本 `REPO` 硬编码、无 `--root` | `grep -n '^REPO' ~/CodeSpace/script-miner/efficiency/clipboard-fallback-check.py` | `47:REPO = Path(__file__).resolve().parent.parent`（写死为脚本所在仓 ⇒ 跨仓自检只能改内存变量） |
| F5 | 四模板 JS 均在 IIFE 内、toast 为函数声明 | `grep -n '^(function\|function showToast\|function showKwToast' layout-*.html` | doc `259:(function(){` + `320:function showToast`；slide `280:` + `345:`；table `341:` + `1438:` + `1444:window.showToast=showToast`；knowledge `227:` + `287:function showKwToast` |
| F6 | 调用点现状（8 处） | `grep -n 'navigator.clipboard' layout-*.html` | doc 315/424/453；slide 331/590；table 1248/1249/1277/1278；knowledge 282（详见 §1.2） |
| F7 | 产物面规模 | `grep -rl 'sidebarTitle' demos/` 等 | doc 派生 25（demos）+ 9（`prompts/kb`）；table 14；knowledge 5（4 demos + `prompts/index.html`）；slide 1（`slide-demo.html`） |
| F8 | `src/` 不进 commit | `git check-ignore -v src/html_gen/html-gen.py` | `.gitignore:37:src/`；`git ls-files src/` = 0 |
| F9 | 无 CHANGELOG 文件 | `ls *.md` | AGENTS.md / features.md / README.md / README.zh.md / review-log.md（无 CHANGELOG） |
| F10 | 版本号同步面 | `grep -rn '3\.3' --include=*.py --include=*.md` | `html-gen.py:17-18` + `README.md:39` + `README.zh.md:39` + `tests/test_cli_version.py`（4 断言）+ `tests/test_demo_cmd.py:101` |
| F11 | 本机非 localhost origin 可用 | `ipconfig getifaddr en0` | `192.168.31.178`（T11 可用） |
| F12 | 重生成覆盖面锚点 | `grep -n 'rebuild' -A 60 html-gen.py` | `demo --rebuild` 只写 `_registry.json` + `data/_demos-data.json` + `demos-index.html`；`demos/index.html` 仅**读入**作 featured 源 |
| F13 | `node --check` 可用 | `node --version` | `v26.0.0` |
| F14 | 设计两笔提交可复核 | `git log --oneline -- documents/solutions/html-gen-clipboard-fallback-design-v1.1-20260927.md` | v1.0 = `0c6acdb`（1 file, +389）；v1.1 = **本版自身提交**（hash 取该命令首行 —— 自指 hash 不写入正文，避免 amend 循环） |

**未核实（禁止据此写验收断言）**：巡检脚本对「回退返回值 / 失败反馈」不判（仅机制推断，未行级核实）；
headless Chrome `file://` 下 `execCommand('copy')` 真实返回值；`hs` 是否默认绑定 `0.0.0.0`（故 T11 用
`python3 -m http.server`）；他仓 vendor 重新拷贝的可行性。

---

## 10. 提交计划（拟 7 笔，串行；第 1、2 笔今日已完成）

| 序 | commit（subject 前缀带完整编号） | 内容 |
|:--|:--|:--|
| 1 | `docs@design: 剪贴板回退统一设计 v1.0 (HTML-GEN-CL015)` | 设计初稿 —— **已完成** `0c6acdb` |
| 2 | `docs@design: 剪贴板回退统一设计 v1.1 — 决策定稿 T1+D1..D10 (HTML-GEN-CL015)` | 本版（`git mv` v1.0→v1.1，决策定稿） —— **已完成**（见 §9 F14） |
| 3 | `feat@templates: canonical copyText 块 + 8 调用点收敛 (HTML-GEN-CL015)` | 四模板（`layout-{doc,slide,table,knowledge}.html`） |
| 4 | `sync@demos: 模板产物全量重生成 78 文件 (HTML-GEN-CL015)` | §5 矩阵（doc 25 / knowledge 4 / table 14 / demo 3 / slide-demo 1 / prompts 31） |
| 5 | `test@templates: 剪贴板回退守卫 T1-T11 + 版本断言同步 (HTML-GEN-CL015)` | 新增 `tests/test_clipboard_fallback.py` + 5 处版本断言 |
| 6 | `feat@cli: 版本 3.4 (2026-09-27) + README 同步 (HTML-GEN-CL015)` | `html-gen.py` 常量 + 两 README |
| 7 | `docs@html-gen: features/AGENTS 同步 + review-log (HTML-GEN-CL015)` | `features.md` + `AGENTS.md`（**受保护：分小步 patch 逐次审批 + sha256 比对**）+ 评审记录 |

> 纪律：每笔 `git add` **显式 pathspec**（防夹带并行 WIP）；`cache/**` 整树 gitignore ⇒ draft 回写/步骤产物
> 不产生提交需求；**只 commit 不 push**（推送待用户放行）。

---

## 11. 下一步（今日范围外，等指示）

1. **[2/6] 设计评审**（review role）：以 **v1.1** 为基线（§0.3），重点核 §1.3 三处偏差（已 pin 为设计基线）
   与 §9 事实卡的可复算性；决策项已定稿 ⇒ 评审聚焦**机制/判据/遗漏面**，不再裁定选项。
2. 评审 PASS/条件通过后按 §10 第 3~7 笔推进 [3/6] dev → [4/6] ops 核查 → [5/6] 审计 → [6/6] 复盘。
3. 用户 `4 押后` 项（script-miner 转交回执 O2/O3）：转交件**暂缓发出**，待本批 [3/6] 落地后重提。
