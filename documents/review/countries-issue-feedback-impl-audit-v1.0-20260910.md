# A 型表格 GitHub Issue 反馈通道 实现审计 v1.0（HTML-GEN-CL009）

> 日期: 2026-09-10 · 角色: review（只读审计，不改源码/模板/数据/测试/文档，仅写审计报告 + review-log + .review-level.yaml）
> 设计基线（权威）: documents/solutions/countries-issue-feedback-design-v1.1-20260910.md
> 设计评审: PASS 85/A（documents/review/countries-issue-feedback-design-review-v1.0-20260910.md，HG-SEC-110..118）
> ops 核查: PASS（documents/review/countries-issue-feedback-ops-verify-v1.0-20260910.md）
> 审计 commit 范围: 46ea35d（设计评审）→ c918522（设计 v1.1）→ 1e8b24d（实现）→ 8022fba（ops 核查）
> 结论: **PASS 95/A**（1 🟡 非阻断 + 5 🟢 记录，无 🔴）

## 1. 数据验证

| # | 项 | 方法 | 结果 |
|:-:|:---|:---|:---|
| 1 | 全量测试（权威串行） | `/usr/bin/python3 -m pytest tests/ -q -n 0` | ✅ **285 passed**（144.25s，1 warning 环境性 urllib3/OpenSSL） |
| 2 | 全量测试（并行） | `/usr/bin/python3 -m pytest tests/ -q -n 4` | ✅ **285 passed**（40.49s） |
| 3 | test_issue_feedback 单文件 | `pytest --collect-only` | ✅ 17 例（TestFeedbackRender 6 + TestIssueSyncScript 11） |
| 4 | 同步脚本 --list | 真实 gh 调用 | ✅ 「无待处理 issue（repo=imjaden/html-gen.cli, label=data-fix）」exit 0（测试 issue #1 已关闭） |
| 5 | 同步脚本 --dry-run | 真实 gh 调用 + `git status --short` | ✅ 零写盘，工作树干净 |
| 6 | 互斥组 / 退出码 | `--list --apply` / `--target nonexistent` / `--json` | ✅ 互斥冲突 exit 2；未知 target exit 2；`--json` 输出 `{"status":"ok",...}` exit 0 |
| 7 | 产物反馈按钮 | `grep -c spFeedbackBtn demos/countries-table.html` | ✅ 1（按钮定义在位） |
| 8 | 产物 issues/new + corner/home/favicon | grep 计数 | ✅ issues/new 1 / github-corner 5 / favicon.png 1 / home URL（html-gen.cli.jaden.tech）1 |
| 9 | OPTIONS.feedback 内联 | `grep -o 'feedback": {'` | ✅ `"feedback": {"dataset": "countries", ...}` 随 OPTIONS json.dumps 注入 |
| 10 | demos-index.html 无按钮 | `grep -c spFeedbackBtn` + `grep -c feedback data/_demos-data.json` | ✅ spFeedbackBtn 1（仅模板定义，非渲染）；_demos-data.json 无 feedback（0）→ 按钮不渲染 |
| 11 | gh 登录态 | `gh auth status` | ✅ imjaden，scopes 含 repo |
| 12 | 当前 open data-fix issues | `gh issue list --label data-fix --state open` | ✅ `[]`（#1 已 CLOSED） |

## 2. 设计落点逐条核对（§4/§5/§6/§7/§8 vs 实现 diff）

| # | 设计项 | 设计 § | 实现落点 | 核对 |
|:-:|:---|:---|:---|:---|
| 1 | FB_CFG/FB_REPO 门控（零新增占位符，OPTIONS.feedback.repo 驱动） | §4.2 | layout-table.html L357-360：`const FB_CFG=(OPTIONS&&OPTIONS.feedback)||null; const FB_REPO=(FB_CFG&&FB_CFG.repo)?String(FB_CFG.repo):''` | ✅ 命名 FB_CFG/FB_REPO（与设计 §4.2 伪码 FB/FEEDBACK 等价，纯命名差异） |
| 2 | 按钮渲染 `renderSplitPreview`（仅 FEEDBACK 时渲染 ✏️） | §4.1 | L1102-1104 `fbBtn` + `id="spFeedbackBtn"`，插于标题与 ✕ 之间 | ✅ ▲ ▼ 标题 ✏️ ✕ 顺序正确 |
| 3 | `.sp-feedback` CSS 复用 .sp-nav 视觉规格 | §4.1 | L182-183 新增，24px/36px 触达、深底 hover | ✅ |
| 4 | `openSplitAt(idx, colKey)` 三处调用携带列 key | §4.3 | pills L560-561 / onCellClick L597 / 首列默认 L603，均 `JSON.stringify(col.key).replace(/"/g,'&quot;')` | ✅ 3 处全覆盖（见 🟢 HG-SEC-123 标注） |
| 5 | `activateSplit(row,idx,colKey)` + `splitField` 生命周期 | §4.3 | L1048 `splitField=colKey||''`；打开/导航（`''`）/URL 恢复（不传列→`''`）/closeSplit 清空 | ✅ 四处生命周期完整 |
| 6 | `buildFeedbackUrl` 全量 encodeURIComponent、空值不拼、current 仅 field 存在时 | §3.2/§4.4 | L1086-1104 `add()` 统一 `encodeURIComponent(k)+'='+encodeURIComponent(v)`，空/undefined 跳过；`if(splitField) add('current',row[splitField])` | ✅ 逐条符合 |
| 7 | `window.open(..., 'noopener,noreferrer')` | §4.4 | L1108 `openFeedbackIssue` → `window.open(url,'_blank','noopener,noreferrer')` | ✅ |
| 8 | `repo` 经 json.dumps 注入（防闭合 JS 字符串） | §4.4 | cmd_table inject 走 `_SCRIPT_KEYS` 含 options → json.dumps | ✅ |
| 9 | CLI `--feedback-repo` 三级取值 CLI>env>JSON、空串禁用 | §5 | html-gen.py `feedback_repo_args()` L134-152 + argparse L893 | ✅ TC-03/TC-04 实测通过 |
| 10 | 仅 table 子命令新增 | §5 | argparse 仅 `t.add_argument` 增一处 | ✅ doc/slide/knowledge 不动 |
| 11 | data-fix.yml 9 字段（input/textarea 满足 URL 预填约束）+ labels + title | §6.1 | .github/ISSUE_TEMPLATE/data-fix.yml 74 行，9 字段、`labels:["data-fix"]`、`title:"[数据纠错] "` | ✅ |
| 12 | config.yml（关 blank issue） | §6.2 | `blank_issues_enabled: false` | ✅ |
| 13 | label data-fix 就位 | §6.3 | `gh label list`（ops 已核）→ #FBCA04「案例数据纠错」 | ✅ |
| 14 | 脚本 gh 调用 list-form + shell=False（HG-SEC-110） | §7.2 | `run()` 统一 `subprocess.run(cmd,shell=False)`；comment body 独立 argv 元素 | ✅ grep `shell=True`=0、`os.system`=0 |
| 15 | 六项校验 + 幂等 + 冲突取最新 | §7.2 | `plan_issues()`：page/dataset/protected/editable/suggested/行唯一/类型/幂等/冲突 | ✅ 全在（顺序略异，不影响正确性） |
| 16 | `protected:[videos]` | §7.2/§8 | feedback-targets.yaml L41；plan_issues 先查 protected 再查 editable | ✅ |
| 17 | JSON 往返逐字（indent=2 无尾换行） | §7.2 | `dump_rows()` `json.dumps(ensure_ascii=False,indent=2)` 无尾换行；test_19 断言 `not endswith('\n')` | ✅ |
| 18 | `[执行]` 打印 + rebuild 四参数 | §7.2/§8 | `rebuild()` L250 打印 `[执行]`；rebuild.args 含 github-url/home-url/favicon/feedback-repo 四参数 | ✅ |
| 19 | 退出码 0/1/2 | §7.4 | 互斥/未知 target/config 缺失=2；gh 失败=1；成功=0 | ✅ 实测 exit 2/0 |
| 20 | 一致性校验（options.feedback ↔ config） | §7.5 | `main()` L313-317 比对 dataset/key/altKey，`[警告]` 不阻断 | ✅ |
| 21 | feedback-targets.yaml schema 完整 | §8 | editable 17 列 + protected[videos] 1 = 18 列全覆盖；types 5 数值列；parse_fields 9 项 | ✅ |

## 3. 安全评估

| 面 | 核对 | 结论 |
|:---|:---|:---|
| URL 注入 | `buildFeedbackUrl` 所有值经 `add()` → `encodeURIComponent`；repo 经 json.dumps 注入（JSON 转义防 JS 字符串闭合），非 innerHTML | ✅ 无 XSS/注入面 |
| `window.open` | `noopener,noreferrer` | ✅ |
| gh 调用 | `run()` 统一 `shell=False` + list-form；comment body（含用户数据）独立 argv 元素；`--json` 结构化读取 | ✅ 无命令注入面 |
| 写回白名单绕过 | `field` 来自 issue body（用户可改），但经 protected→editable→类型→行唯一定位→幂等五层校验；videos 永远拒绝；data/html 路径来自 config（非用户输入） | ✅ 无绕过路径 |
| body 解析歧义 | 「空行+`### `」切段 + 未知段并入上一字段 + 同名字段首次生效；残值内含「空行+`### 已知label`」极端情形由人工 dry-run 兜底（设计已记录 HG-SEC-115） | 🟢 残面可接受 |
| 依赖 | 脚本仅标准库 + PyYAML（`yaml.safe_load`）；运行时 html-gen 零依赖不受影响 | ✅ |

**无 🔴/无凭据泄露**。安全面与设计评审结论一致，HG-SEC-110（shell=False）、HG-SEC-111（repo 落 JSON）、HG-SEC-116（rebuild.args 补 favicon）全部落定。

## 4. 测试与回归证据

- 285 tests 全绿（串行 144.25s / 并行 40.49s），268 → +17 与设计 §9「268→~279」一致（+17 因 TC 拆分多例，覆盖更充分）。
- 既有功能零回归：test_sync_videos 21 / test_templates 18 / test_index_landing 18 等 28 个既有文件全通过。
- TC-01 口径（HG-SEC-112）已收紧：test_01 断言「无 `"feedback"` 注入 + 无 spFeedbackBtn 渲染」，未断言 JS 源码无 issues/new（buildFeedbackUrl 常驻定义）——正确。
- HG-SEC-115 解析边界：test_12_stray_section_merged 断言未知段并入上一字段、段头文本保留。
- 真实端到端（ops 已核）：issue #1 创建 → dry-run（零写盘）→ apply → 回评 → --close；不丹 pop_wan 79→80 仅 1 字段变化；测试数据已 `git checkout` 回滚，工作树干净。

## 5. Findings

### 🟡 HG-SEC-119 — `--issue N` 使用无效 gh 搜索限定符 `in:number`

`gh_issue_list()`（scripts/countries-issue-sync.py:54）用 `--search f'{issue_no} in:number'` 定位指定 issue，但 GitHub 搜索语法**无 `in:number` 限定符**（`in:` 仅支持 title/body/comments）。实测 GitHub 静默忽略该限定符，查询退化为对数字的**文本搜索**：

- `gh issue list --search "pop_wan in:number"` ≡ `--search "pop_wan"`（均返回 #1，证明 `in:number` 被丢弃）；
- 后置过滤 `[i for i in issues if number==issue_no]`（L63）存在，但前置 `--search` 已把目标 issue 排除时无法补救。

**影响**：`--issue 42 --apply` 在 issue #42 的标题/正文不含数字「42」时，会静默返回「无待处理 issue」，维护者误以为无事可做。设计 §7.1 承诺「`--issue N` 只处理指定 issue」未达预期；且 ops 核查 §2 明确推荐「按 `--issue <n>` 直查」作为 gh 搜索索引延迟的对策，该对策本身即失效。

**修复建议**：改为 `gh issue view <N> --json number,title,body,url,createdAt` 直查（list-form + shell=False 不变），或去掉 `--search` 仅靠后置过滤（`--limit 100` 内）。非阻断（核心闭环 --list/--apply 不受影响，ops E2E 已证）。

### 🟢 HG-SEC-120 — 设计 §9 TC-08（dry-run 零写盘）无独立自动化测试

test_issue_feedback.py 17 例未含显式「dry-run 零写盘」断言。该行为由 (a) 代码结构保证（`main()` L347-351 `if not args.apply: ... return 0` 在写盘前返回）+ (b) ops E2E 实测（`git status` 干净）双重覆盖，功能正确，仅缺自动化回归护栏。

### 🟢 HG-SEC-121 — test_01 docstring 口径残留

test_01 docstring 仍写「产物无 issues/new」，但实际断言已按 HG-SEC-112 收紧为「无 `"feedback"` 注入 + 无 spFeedbackBtn 渲染」（不断言 issues/new）。docstring 与实际断言不一致（纯文档层面，不影响测试正确性）。

### 🟢 HG-SEC-122 — test 文件 `orig_parse` 跨 module 实例

test_issue_feedback.py:407 `orig_parse = _load_sync_module().parse_issue_body` 二次加载产生新函数对象，与 setUpClass 的 `cls.mod.parse_issue_body` 非同源对象；test_16/test_18 的 finally 恢复用跨实例函数。因同源同义，功能等价，属测试卫生瑕疵（建议改为 `cls.mod.parse_issue_body` 一次性捕获）。

### 🟢 HG-SEC-123 — 设计 §4.3 对 L594 分支标注不准

设计 §4.3 枚举 openSplitAt 调用点为「L552（pills）、L588/L594（onCellClick）」，但 L594 实为「首列默认分栏」分支（`col === firstKeyCol`，非 onCellClick）。实现正确覆盖 3 处（pills / onCellClick / 首列默认），首列默认携带列 key 符合 O1「携带被点列」意图。设计标注轻微不准，实现无偏差。

### 🟢 HG-SEC-124 — demos-index.html 连带重建 + `--limit` 超设计 §7.1

① `demos/demos-index.html`（+60/-12）为共享模板 layout-table.html 改动后的连带重建，未在设计 §10 文档同步面显式列出；属 HG-SEC-114「视觉/行为零变更，非 byte-identical」正常表现（_demos-data.json 无 feedback → 按钮不渲染），非越界。② 脚本新增 `--limit` flag（默认 100）超出设计 §7.1 CLI 清单（`--repo` 已在清单内），benign。

## 6. 遗留项判定

| 遗留项 | 判定 |
|:---|:---|
| HG-SEC-118（URL `?title=` 覆盖表单固定 title） | ✅ 正确记录为「需登录态实测」，不阻断：ops 核查 §2 已注明「本机浏览器无 GitHub 会话未能实测」；设计 §13 已声明「若不可覆盖，title 恒为 `[数据纠错] `，功能与解析不受影响（正文段落才是数据来源）」 |
| gh 搜索索引延迟（创建后 ~2s 才可查到） | ✅ 正确记录为「脚本行为正确（空列表→退出 0），自动化首次查询可能扑空」，不阻断；对策「按 --issue 直查」因 HG-SEC-119 而需修正 |

## 7. 评分与结论

| 扣分项 | 严重度 | 分值 |
|:---|:---|:---|
| HG-SEC-119 --issue 无效 gh 搜索限定符 | 🟡 | -5 |
| HG-SEC-120..124（5 项） | 🟢 | 0（记录） |

得分: 100 - 5 = **95 / 100 → A**

**PASS（95/A）** — 设计 → 实现 → 真实数据落点全程可复现：模板门控/列上下文/URL 构造/三级取值/Issue Form/脚本六校验+幂等+冲突/protected/JSON 往返逐字/rebuild 四参数/退出码三态逐条核对命中；285 tests 全绿（串行+并行）；安全面 URL 全编码 + noopener + json.dumps + 白名单/类型/protected/行唯一五层兜底，无 🔴 无凭据泄露；HG-SEC-110..116 全部落定，HG-SEC-117（skillSplit 缺省 `''` 优雅降级）与 HG-SEC-118（title 待实测）正确记录不阻断。唯一 🟡 HG-SEC-119（`--issue` 便捷 flag 静默失效）非阻断，建议 follow-up 修复（`gh issue view` 直查）。核心反馈闭环（--list/--dry-run/--apply/--close）经 ops 真实 issue E2E 验证，功能完整。
