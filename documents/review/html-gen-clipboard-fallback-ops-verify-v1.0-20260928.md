# 剪贴板回退统一（canonical copyText）— ops 独立核查报告 v1.0

> 日期: 2026-09-28 · 闭环: **HTML-GEN-CL015 [4/6] ops 核查** · 角色: ops（交互式驱动会话）
> 被审对象: `b4afd4e`(canonical 块+8 调用点) → `d4f0ca9`(产物全量重生成) → `3d6bfff`(守卫 T1-T11) →
> `c5c4e02`(版本 3.4+README) → `8e99f24`(features/skills 同步) → `bf61484`(用例命名+既存用例去假成功断言)（dev 会话产出, 74 文件）
> 基线: `83c4e2c`（"零改动基线重生成"笔, 消除模板历史漂移后可比）
> 需求源: `documents/solutions/html-gen-clipboard-fallback-design-v1.2-20260927.md`（§0.4 v1.2 补记 = [3/6] 唯一口径源）
> 上轮依据: `documents/review/html-gen-clipboard-fallback-design-review-v1.1-20260927.md`（PASS 85/100·B；findings 187-201）
> 核查方式: **自建 harness 独立复跑**（`cache/closed-loop/HTML-GEN-CL015-verify.py`, 18 项；不复用 dev 的测试与其自报）
> **结论: PASS —— 18 项判据全绿（FAIL 0 / N-A 0），含真非 localhost 端到端「真复制」实证**

## 1. 结论要点

| 面 | 结果 | 关键实测 |
|:--|:--|:--|
| canonical 块（§3 规格） | ✅ | 四模板**各 3 次出现（2 守卫 + 1 调用）/ 块外 0**；块文本**逐字节一致**（唯一 sha 前缀 `e4adb3b7684b34c2`） |
| 调用点收敛（8 处） | ✅ | `copyText(` 分布 doc 3 / slide 2 / table 2 / knowledge 1 = **8**；块外 `navigator.clipboard`+`execCommand` 残留 **0** |
| table 对外名与死代码 | ✅ | `fallbackCopyUrl` 残留 **0**（死代码已清）；`window.copyAction`=1 / `window.shareLink`=1 保留 |
| D10 闸门正则 | ✅ | 含 basename 兜底正则（`/^(https?:\|\/\|~\/)/` 判定 + `[\w.\- ]+$`），防「路径整串被脱敏丢失」 |
| 产物面（56 产物） | ✅ | 与基线笔 diff：`<script>` 区间 2252 行 + 文档面 10 行（**声明项**）+ **区间外非 meta 非文档面 0 行** ⇒ 零数据层/零结构改动 |
| 只读探针 | ✅ | OK **130** / WARN **0** / FAIL **0**（基线笔实测为 OK 104 / WARN 47 / FAIL 38） |
| 四 drama strategy 表 | ✅ | 逐表列集与基线一致（10/10 无丢失）⇒ 手工同步未削内容 |
| 保护面 | ✅ | 根 `index.html` + `demos/index.html` 零改动（D6）；`data/**` 零改动；`AGENTS.md`（受保护）零改动 |
| 版本/文档面 | ✅ | `3.4`+`2026-09-27`；docstring 写死版本行已删（5 处→4 处）；版本字面量残留 0；`features.md` canonical 提及 4 处 |
| 守卫测试 | ✅ | `tests/test_clipboard_fallback.py` **12 用例**（T1–T11 + T5 的 A/B 负例 `test_05b`）+ secure 夹具 + SKIP 分支 |
| 全量回归 | ✅ | **346 passed / 82 subtests / 0 failed**（136.89s, `-n 0` 权威）；基线 334 → Δ+12 只增不减 |
| 端到端（A2/T5 验收） | ✅ | 真非 localhost `http://192.168.31.178` 下：`isSecureContext=False`、`navigator.clipboard=undefined`；真实点击复制 → `已复制: document.pdf`；**CDP 粘贴回读 == `document.pdf`（真复制）**；无用户激活的 JS 直调 → `复制失败`（**禁静默/禁假成功**） |
| 范围白名单 | ✅ | 74 文件全在声明范围（模板 4 + 产物 + 测试 + `html-gen.py` + README×2 + `features.md` + skills），白名单外 **0** |
| 判据非恒真 | ✅ | 同一 harness 指向基线 `83c4e2c` 副本 → **3 PASS / 7 FAIL**（TC1/2/4/5/6/13/14 全红） |

## 2. 可复跑验证清单（命令 + 预期 + 断言）

```bash
cd /Users/jadenli/CodeSpace/html-gen.cli
PY=/opt/homebrew/Caskroom/miniconda/base/envs/py3.12/bin/python3

# 1) 全量核查（18 项，含浏览器端到端与全量回归）        预期: 汇总 18 → PASS 18 / FAIL 0, EXIT=0
$PY cache/closed-loop/HTML-GEN-CL015-verify.py --with-pytest | tee cache/closed-loop/cl015-ops-check.txt
grep -E "^汇总|EXIT" cache/closed-loop/cl015-ops-check.txt

# 2) 仅端到端（真非 localhost + 剪贴板回读）           预期: PASS，A/B/C/D 四子项齐全
$PY cache/closed-loop/HTML-GEN-CL015-verify.py --only=17

# 3) 判据非恒真（基线副本反证）                        预期: 7 FAIL（TC1/2/4/5/6/13/14）
git worktree add -f /tmp/cl015-base 83c4e2c
CL015_REPO=/tmp/cl015-base $PY cache/closed-loop/HTML-GEN-CL015-verify.py --only=static

# 4) 只读探针（源面+产物面 违规调用扫描）              预期: OK 130 / WARN 0 / FAIL 0
$PY cache/closed-loop/cl015-probe.py

# 5) 全量回归（权威，单线程）                          预期: 346 passed, 82 subtests
$PY -m pytest tests/ -q -n 0 | tail -2

# 6) 端到端复现口径（真 LAN origin；ops 实测端口为临时端口）
#    python3 -m http.server <port> --bind 0.0.0.0  (cwd=demos) → http://<LAN IP>:<port>/table-actions-demo.html
#    点击「复制」动作 → toast「已复制: document.pdf」；同一浏览器 secure 页 Ctrl+V → 文本 = document.pdf
```

## 3. 18 项判据明细（harness 原文, 2026-09-28 12:20）

```
=== HTML-GEN-CL015 [4/6] ops 核查 ===  HEAD=bf61484 基线=83c4e2c

[TC1-块外零出现] PASS: layout-doc.html: 内 3 / 外 0; layout-slide.html: 内 3 / 外 0; layout-table.html: 内 3 / 外 0; layout-knowledge.html: 内 3 / 外 0
[TC2-块内3次(2守卫+1调用)] PASS: 同上
[TC3-四模板块逐字节一致] PASS: 唯一 sha 数 = 1 → 四文件同 'e4adb3b7684b34c2'
[TC4-调用点收敛] PASS: 块外残留 无; copyText 调用分布 {'layout-doc.html': 3, 'layout-slide.html': 2, 'layout-table.html': 2, 'layout-knowledge.html': 1} (合计 8, 期望 8)
[TC5-table对外名与死代码] PASS: fallbackCopyUrl 残留=0 / window.copyAction=1 / window.shareLink=1
[TC6-D10闸门正则兜底] PASS: 含 basename 兜底正则 = True
[TC7-只读探针(源+产物)] PASS: OK 130 / WARN 0 / FAIL 0（期望 0/0）
[TC8-产物diff仅脚本面] PASS: 56 个产物; <script> 区间改动行 2252; 文档面(声明项) 10 行; 区间外非 meta 非文档面行 0
[TC9-D6落地页未动] PASS: 根 index + demos/index: 零改动
[TC10-data未动] PASS: data/**: 零改动
[TC16-AGENTS未动] PASS: AGENTS.md（受保护）: 零改动
[TC11-4表列集无损] PASS: daming/history/yongzheng/zhuyuanzhang 基线列 10 / HEAD 10 / 丢失 []
[TC12-守卫测试面] PASS: 用例 12 条（T1–T11 + test_05b）; secure 夹具=True; SKIP 分支=True
[TC13-版本面] PASS: 常量 3.4/2026-09-27=True; docstring 写死版本行=已删; 版本字面量残留 0 处
[TC14-文档面/prompts一致] PASS: features.md canonical 提及 4 处（期望≥3）; prompt --site 语义差异 0; 仅 meta 时间戳差 9 文件（可解释, §5 纪律 1）
[TC15-范围白名单] PASS: 74 文件; 白名单外: 无
[TC17-真非localhost端到端] PASS: A isSecureContext=False clipboard=undefined; B 真实点击 → toast="已复制: document.pdf" JS错误=0; C 粘贴回读='document.pdf' 期望='document.pdf'; D JS直调 → toast="复制失败"（期望含「失败」）
[TC18-全量回归] PASS: rc=0; 346 passed, 82 subtests passed in 136.89s (0:02:16)

汇总: 18 项 → PASS 18 / FAIL 0 / N-A 0
```

## 4. 判据非恒真 + harness 自检

**反证**（同一 harness, 只把 `CL015_REPO` 指向基线笔副本 `83c4e2c`）: `3 PASS / 7 FAIL`
—— TC1/TC2（块标记缺失）、TC4（块外残留 4 文件 + copyText 合计 0）、TC5（`fallbackCopyUrl` 残留 3）、
TC6（无 basename 兜底正则）、TC13（仍是 3.3）、TC14（`features.md` 0 处）全红；
TC3/TC8/TC15 在基线因「无差异/无文件」平凡通过，**已识别为恒真项**（判据有效性不依赖之）。

**harness 自检记录（3 轮误判 → 改判据后复跑，非改被测物）**:

| 轮 | 误判项 | 根因（判据侧） | 修正 |
|:--|:--|:--|:--|
| 1 | TC8/TC11/TC13/TC14/TC15 | 分类器按关键词判「脚本面」漏 D10 正则行；TC11 硬编码 4 列（history 表本就无）；TC13 把 `§3.3`/`83.3%` 当版本残留；TC14 不容忍 meta 时间戳；白名单漏 `layout-*.html` | 改按 `<script>` 区间行号判；TC11 改逐表与基线列集比对；TC13 收窄版本字面量正则；TC14 容忍 meta 差并区分语义差；白名单补四模板 |
| 2 | TC8（1 行） | 同一次改动的**删除侧**未对称归类（旧文案行不含新关键词） | 判据补 `clipboard/fallback/canonical` 通用词，两侧对称 |
| 3 | TC17-C（`ERR:NotAllowedError`） | headless 下 `navigator.clipboard.readText()` 权限墙（harness 侧限制, 非产品缺陷） | 改走 CDP editing command `paste` 注入聚焦 textarea 回读，得 `document.pdf` 实证 |

## 5. 未验证面与降级登记（显式, 不沉默略过）

- **移动端 Safari `readonly` + `select()`**（评审 192 / 决策 D4）: 环境无 iOS 真机/模拟器 ⇒ **仍未验证**；本批保留 `readonly`（兼容性优先），风险已知且低。
- **`readText` 类读取路径**: headless 权限墙（见 §4 轮 3）；产品侧不依赖读取（仅 `writeText`），不影响验收面。
- **`src/` 打包源未重建**（评审 199）: 属发版流程（PyPI/装 CLI 仍产旧代码），**非本批 git 交付面**。
- **PWA/离线/自定义 origin**: 未涉及，无判据。

## 6. 被派方自报面核实（采信 / 不采信）

- 采信（本核查已复算）: 6 笔提交序列、74 文件范围、346 tests、版本 3.4、`prompts` 语义一致、四表内容无损。
- **测试削弱核查**（重点）: `bf61484` 动了既存用例 `tests/test_templates.py::TestDocShowMd::test_doc_title_click_copy_path`
  —— 实测为**强化而非削弱**：仅新增 `navigator.clipboard.writeText` 可用桩 + 文档化夹具说明（11 insertions / 2 deletions，其中 1 为方法改名），
  断言目标（toast 文案 = 脱敏文件名而非 URL）保持不变。原用例在旧实现下因「无条件 showToast」而**恒绿 = 假成功断言**，
  本次修正后该用例才真实观测成功分支。**本批无任何「改红为绿」的断言删除/放宽**。
- 不采信: dev 自报的 NEW-1…NEW-5（features/AGENTS 建议）与对 4 篇 author 空条目的判断 —— 属建议面，未纳入本核查判据；
  `AGENTS.md` 建议**未落地**（受保护文件审批超时, 见 §7）。

## 7. 遗留待处置（转 [5/6]/[6/6]）

1. `AGENTS.md` 索引路径 1 行 patch —— **受保护文件未获审批**（07 轮写入被拦），本批刻意零改动（TC16 已守）。
2. 云智慧系 4 篇 `author` 空条目（索引面）—— 上游 script-miner 数据面，本批仅登记证据不代做。
3. 4 个 drama strategy 表 JSON 列集落后产物（`8b0dcc6` 只改产物侧）—— 另批修，本批按 v1.2 §0.4-A 例外手工同步 canonical 块。
4. 推送面: 本批 `github` 远端 FF-only 推送待放行（`origin`/gitee 不推）；dev 5 笔 + ops 笔未推。
