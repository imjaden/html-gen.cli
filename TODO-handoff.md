# 会话轮转入口 — html-gen.cli

> 新会话开场**只读本页**即可加载：① 已登记待执行编号 ② 当前澄清后的串行执行清单 ③ 指针与状态。
> **条目真值不在本页** —— 真值 = live draft（`cache/draft/TODO-<date>.md`）与 `hm loop list` / `hm loop status <编号>`。
> 本页 = 会话轮转入口页（hermes-manager 同构实践；当前为**手工维护版**，首次建立 2026-09-27）。
> 维护纪律：状态变化时**改本页对应格**，不复制真值（禁第二真值）。

---

## 一、已登记待执行（来源: `hm loop list`，本仓 1 条）

| 编号 | 标题 | 状态 | kind | prio | 方案文档 | 备注 |
|:--|:--|:--|:--|:--|:--|:--|
| **HTML-GEN-CL015** | html-gen 剪贴板回退统一 · 跨仓转交 SCRIPT-MINER-CL042 | READY（[1/6] 设计定稿 · [2/6] 评审 PASS 85/100 + push · [3/6] dev 落地 6 笔 · [4/6] ops 核查 18/18 PASS · **[5/6] 审计 PASS 95/100·A + 已 push** · [6/6] 复盘） | independent | P2 | `documents/solutions/html-gen-clipboard-fallback-design-v1.2-20260927.md` | 起点 `dc14a38`；基线笔 `83c4e2c`；dev 头 `bf61484`；审计头 `4a3c4a0`（= github/main）；findings 187-201 全闭合 + 新增 202-206 全 🟢 另批 errata |

> 取号核对：CL015 = 本仓新式序列 max(CL014) + 1；`hm loop next-code` 回 `HTML-GEN-CL016` ⇒ CL015 已绑定。

---

## 二、当前串行执行清单（2026-09-27 澄清定案 · 逐步放行）

| 步 | 内容 | 前置 | 状态 |
|:--|:--|:--|:--|
| T1 | 需求核实与澄清：交接件 3 处偏差（P1 范围少算 / P2 漏算本仓产物 / P3 验收条款越界）+ T1 验收口径裁定 | — | ✅ 已定案（用户 `1 采用推荐`） |
| T2 | 申请编号 + draft 登记（HTML-GEN-CL015；`hm loop check .` 6/6） | T1 | ✅ 已完成 |
| T3 | 设计方案 v1.0 / v1.1（含 commit：`0c6acdb` / `dc14a38`；决策定稿 T1+D1..D10） | T2 | ✅ 已完成 |
| T4 | **[2/6] 设计评审**（review role；**评审 PASS 后由该会话 push**，用户 2026-09-27 授权） | T3 | ✅ 已完成（**PASS 85/100 · B**，0 阻塞；`4db7089` + push github ff-only `5df590a..4db7089`） |
| T5 | **[3/6] dev 实施**：① 四模板 canonical `copyText` 块 + 8 调用点收敛 ② 产物全量重生成 ③ 版本 3.4 + README ④ `tests/test_clipboard_fallback.py`（T1–T11）⑤ features/skills 同步 ⑥ 折入评审 findings HG-SEC-187..194 | T4 ✅ | ✅ 已完成（dev 6 笔 `b4afd4e`→`bf61484`，74 文件，12m22s；基线笔 `83c4e2c`；AGENTS 本批零改动） |
| T6 | **[4/6] ops 核查**：只读探针复算 + A/B 负例成立 + 非 localhost origin 实机复制 | T5 ✅ | ✅ 已完成（**18/18 PASS**，FAIL 0 / N-A 0；报告 `documents/review/html-gen-clipboard-fallback-ops-verify-v1.0-20260928.md`；反证 3 PASS/7 FAIL） |
| T7 | **[5/6] 审计**（review role）：逐 finding 独立复算 + 「新增项 = 0」显式回答 | T6 ✅ | ✅ 已完成（**PASS 95/100·A**，15 条全闭合=已处置 13 / N-A 1 / 0 未闭合；新增 202-206 全 🟢；`4a3c4a0` + push github `69ec665..4a3c4a0` ff-only） |
| T8 | **[6/6] 复盘 + 收尾**：review-log + 给 script-miner 的转交回执（O2/O3） | T7 ✅ | ✅ 复盘完成（ops 报告 §8 勘误回填 + 入口页刷新 + 202-206 登记）；抄送 script-miner 回执 ⏸ 用户押后（`5 押后`） |
| T9 | 仓外（**本会话不做**）：script-miner CL043 手写页修复 + 7 个 vendor 副本重新拷贝 | 本批 [3/6] 落地 | ⏸ 用户押后（`4 押后`） |

**批内提交计划（拟 7 笔，见设计稿 §10）**：**实际 11 笔**已落地（`f7fcf82` 设计 v1.2 / `ee2c39f` D7 云智慧索引旁支
/ `83c4e2c` 零改动基线笔 / dev 6 笔 `b4afd4e`→`bf61484` / `dfd5d71` ops 回执 / `4a3c4a0` 审计件），
每笔 `git add` **显式 pathspec**；push 由 review 审计 PASS 后 ff-only 执行（`origin`/gitee 不推、不 force）。

---

## 三、未定案观察项（无编号；随批处置或另立批）

| # | 诉求 | 出处 | 状态 |
|:--|:--|:--|:--|
| O2 | script-miner 9 文件：7 个本仓模板/产物 vendor 副本（重新 vendor）+ 2 个他仓手写页（他仓自修） | 设计稿 §8 O2 | 转交，用户**押后** |
| O3 | 巡检脚本缺 `--root` 参数 ⇒ 本仓自检只能用内存探针 | 设计稿 §8 O3 | 转交建议（他仓 CL042/CL044 面） |
| O4 | 本仓巡检未接入提交门禁 | 设计稿 §8 O4 | 本批以 `tests/test_clipboard_fallback.py` T1–T4 常驻守卫承接 |
| O5 | 落地页 `index.html` / `demos/index.html` 的 `copyText` 与 canonical 块**同名不同签名** | 设计稿 §8 O5 | D6 定稿: 本批不动，另批可选 |
| O6 | `demos/usage-guide.md` 既有表述「v1.1+ 用 execCommand 兜底」 | 设计稿 §8 O6 | 本批订正 + 重生成 |
| O7 | 他仓 vendor 副本缺源 commit 注释（版本可追溯性） | 设计稿 §8 O7 | 记录（他仓决定） |
| O8 | `AGENTS.md:352` 索引路径 patch **待落**（受保护文件写入被拦 = 审批超时未获同意, 未重试未绕道）；补丁已备 `cache/handoff/agents-md-index-path-20260928.patch`（`git apply --check` 通过）；sha256 `6d6a324276205e74…` → 预期 `2658f832135f4592…` | 本会话 [6/6] 收尾 | ⏸ 待用户套用（`git apply` 或交互式审批） |
| **HG-SEC-202..206** | [5/6] 审计**新增 5 项 🟢 record**（全为文档/报告/注释口径，0 代码回炉）：202 设计 §0.4-A「4 表 11 列」措辞+history 例外归因；203 ops 回执 TC11/TC8 计数口径；204 设计 §7 A4「status 空」条款措辞（**审计归因写作 ops 回执，ops 侧勘误已改归设计 §7 A4**）；205 `bf61484` 夹具 docstring 注释；206 审计侧 harness 自证 | 审计报告 §④ | 另批 errata（不阻断；ops §8 已回填 E1–E3） |

---

## 四、指针与状态

- 待办真值: `cache/draft/TODO-20260927.md` · 队列视图: `hm loop list` · 单号状态: `hm loop status HTML-GEN-CL015`
- 设计稿: `documents/solutions/html-gen-clipboard-fallback-design-v1.2-20260927.md`（§0.2 决策定稿表 / §0.4 **v1.2 补记 = [3/6] 唯一口径源** / §5 逐产物参数集 / §9 事实卡 F1–F14）
- 产物基线笔: `83c4e2c`（"零改动基线重生成 29 文件"，消除模板历史漂移 22 陈旧 + 2 favicon）⇒ [4/6] 起 diff 可比
- ops 核查: `documents/review/html-gen-clipboard-fallback-ops-verify-v1.0-20260928.md`（**18/18 PASS**；harness
  `cache/closed-loop/HTML-GEN-CL015-verify.py`，输出存档 `cache/closed-loop/cl015-ops-check.txt`，
  反证存档 `cache/closed-loop/cl015-harness-reverse.log`）
- 评审记录: `documents/review/html-gen-clipboard-fallback-design-review-v1.1-20260927.md`（**PASS 85/100 · B**，0 阻塞，
  findings HG-SEC-187..201 = 8 🟡 折入 [3/6] + 7 🟢 折入文档笔）+ `review-log.md` / `.review-level.yaml` 同步
  （同笔 commit `4db7089`，已 push）
- 跨仓来源件: `~/CodeSpace/script-miner/cache/handoff/prompt-dev-html-gen-doc-clipboard-fallback-20260927.md`（只读）
- 派发留档（`cache/**` gitignored）: `cache/review-prep/prompt-html-gen-cl015-design-review-20260927.md`
  + `cache/review-prep/dispatch-html-gen-cl015-design-review-20260927.sh` + `cache/closed-loop/cl015-design-review-dispatch.log`
- 推送面: 远端 `github`（`imjaden/html-gen.cli`）为发布面；`origin` = gitee（本批**不推**）；push 一律 ff-only、不 force
- 项目规范: `AGENTS.md`（受保护指令文件：落地须分小步 patch 逐次审批 + sha256 逐字节比对）·
  `features.md`（能力清单）· `review-log.md` + `.review-level.yaml`（审计链与 findings 台账）
- **本仓无** `skills-governance/loop-batch-gates.md` / `documents/1A-closed-loop-protocol-*.md`（实测不存在，
  那些是 hermes-manager 的规范文件）⇒ 本仓 1A 口径以设计稿 §7 验收清单（A0–A4）+ `hm loop check .` 为准

---

## 五、历史

- 2026-09-28 **[5/6] 审计 PASS 95/100·A**（review role，`4a3c4a0`）→ **已 push github `69ec665..4a3c4a0`**（推后
  `ls-remote == 本地 HEAD`；`origin`/gitee 仍 `7821427`；未 force）→ **[6/6] 复盘**（本笔）。
  15 条 finding 全闭合（已处置 13 / N-A 199 / 部分 0 / 未处置 0）；新增 202-206 全 🟢 record（另批 errata）。
  审计增值实证（独立于 ops）：块 sha256 `eb5431669eca36b4…` **== 设计 §3 原文逐字节**（与 ops 的 `e4adb3b7…`
  数值相异系提取边界口径不同：ops 取「BEGIN/END 标记**之间**文本」，审计口径见其报告；两侧各自自证
  「四模板块唯一值 / == 原文」，判定一致）；
  参数回收重生成 **38/38 byte-IDENTICAL** + `demo --rebuild` 3/3；变异测试 3 态（M3 指名
  `demos/usage-guide.html:1253 脚本内裸调用`）；**有头 Chrome + `pbpaste` 回读 == `document.pdf`（真复制实证，
  且证 headless 与系统 pasteboard 隔离——ops 的 headless CDP 回读法未被复现，方法差异已双方登记）**；
  基线 × 复制彻底失败仍 toast `已复制` ⇒ 坐实原用例「恒绿=假成功断言」。
  审计对 ops 回执 2 处口径/归因提出勘误（203/204）⇒ ops §8 已回填 E1–E3（其中 E3 = **审计归因有误**：
  `status 空` 条款真实来源是设计 §7 A4 行，非 ops 回执；grep 实证）。
- 2026-09-28 [3/6] dev 落地（`b4afd4e`→`bf61484` 6 笔，74 文件）→ [4/6] ops 核查 **18/18 PASS**。
  关键实测：四模板 canonical 块逐字节一致（sha `e4adb3b7…`）/ 块外 0 / 调用点 8；
  产物 56 个 `<script>` 区间 2252 行 + 文档面 10 行为唯一差异（零数据层）；
  只读探针 OK 130 / WARN 0 / FAIL 0（基线笔时 104/47/38）；全量回归 346 passed；
  真非 localhost（`192.168.31.178`）端到端：`isSecureContext=False` + 真实点击 → `已复制: document.pdf`
  + **CDP 粘贴回读 = `document.pdf`（真复制实证）** + 无激活 JS 直调 → `复制失败`（禁假成功）。
  反证：同一 harness 指向基线笔 = 3 PASS / 7 FAIL（判据非恒真）。
  例外登记：4 个 drama strategy 表不可重生成（JSON 列集落后产物）⇒ 手工同步；`AGENTS.md` 受保护未获审批
  ⇒ 本批零改动；移动端 Safari `readonly`+`select()` 仍未验证（D4 登记）。
- 2026-09-27 [2/6] 评审 **PASS 85/100 · B**（0 阻塞）→ `4db7089` 已 push（`5df590a..4db7089`，ff-only，
  未推 gitee，未 force）。评审增值实证：canonical 块原型实跑（headless Chrome 4/4 断言）+
  **真非 localhost origin 端到端**（`http://192.168.31.178:8917/demos/usage-guide.html`，修前实机坐实假成功）。
  折入项：HG-SEC-187..194 → [3/6] dev；195..201 → 同批文档笔；199 → 发版流程（非本批提交面）。
- 本页**首次建立**（2026-09-27）：CL015 批的会话轮转入口。此前本仓无 TODO-handoff.md，交接靠
  `cache/handoff/` 与 `documents/handoff/` 快照；如需追溯更早批次的执行明细，见
  `git log --oneline`、`cache/closed-loop/2026*` 步骤 JSON 与 `review-log.md`。
- 已完成编号（--done）: HTML-GEN-CL001 ~ CL014 ✅（清单 `hm loop list --done`；审计链见 `review-log.md` 与 `.review-level.yaml`）。
