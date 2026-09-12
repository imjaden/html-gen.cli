# GitHub Issue 反馈通道 skill 沉淀 — 实现审计报告 v1.0

> 闭环: HTML-GEN-CL011 · 步骤: [5/6] 实现审计
> 日期: 2026-09-12 · 执行: Security Reviewer
> 审计对象: commit `edd3e90`（dev）+ `8bbc575`（AGENTS.md 同步）+ `c7bbfa0`（ops 核查报告）
> 设计基线: `documents/solutions/github-issue-feedback-skill-design-v1.2-20260912.md`（评审 PASS 100/A，`f3be5d9`）
> 独立复验: 全部逐项亲自跑命令 / 读文件，未仅信 ops 报告

## 1. 结论

**CONDITIONAL PASS** —— 设计 §5 八项验收标准逐项独立复验全部命中，挂载副作用为零，测试 312 passed 零回归。
发现 **1 🟡 + 2 🟢**，均为交付物（skill 知识资产）的事实准确性/一致性缺陷，无安全漏洞、无破坏性 bug、无阻塞项。
🟡 为 SKILL.md 主文件校验链顺序与源码/自身 reference 三方不一致（可复用载体的事实准确即本闭环核心价值），建议 ops 一处三词重排后复审转 PASS。

## 2. 逐项验收（设计 §5 八项，独立复验）

| # | 验收标准 | 实测 | 证据 |
|:--|:--|:--|:--|
| 1 | skill 四文件 ≤250 行/篇 | ✅ | `wc -l`: SKILL.md 155 / adoption-prompt 203 / targets-schema 106 / form-template 136（合计 600） |
| 2 | prompt 四态正常 | ✅ | 列表含 `github-issue-feedback`+description+3 refs；全文 3 篇 references 拼接（`## {stem}`）；`--brief` 9 章节+refs；`--json` `status:ok`、data 键 `{content,name,references}`（3 refs） |
| 3 | `--site` 31 文件 + 门户 table 组条目 | ✅ | `find prompts -type f`=31（顶层 22 + kb/ 9）；`_kb-data.json`=27 条（skill×9+guide×6+case×12），新增条目 `{group:table, section:指令 CLI, badge:Prompt, url:kb/github-issue-feedback.html}`；index.html/all.md 含该条目 |
| 4 | 测试同步（L239/L252/L342 + 注释消息串） | ✅ | `EXPECTED_SKILLS` 9 项；硬断言 22/9/27（现 L240/L253/L343）；B 组注释/消息串 6 处同步（L5/L22/L105/L236/L180/L310/L371）；`test_prompt_cmd::test_06` 新增 |
| 5 | prompts/ 重生成 + 幂等 | ✅ | 独立 `--site --dir` 两次重生成，确定性集（22 顶层文件）与仓库提交版**逐字节一致**；`kb/*.html` 仅 doc meta 时间戳 2 行 diff（HG-SEC-086 既有 wildcard） |
| 6 | 文档面 §4.3 全表 | ✅ | AGENTS.md（L58 31 文件/L299+L326 312/L334 目录树+1）；features.md L25；skills/html-gen/SKILL.md（L63/L69/L70 + L313 v2.7.0 追加 + frontmatter 2.7.0）；html-gen-cli-spec L35；README 双源各 3 行；两 handbook 全行；历史行 L61/L62/L90/v2.5.0 未改写 |
| 7 | 全量 pytest 零回归 | ✅ | `python3 -m pytest tests/ -q -n 0` → **312 passed**（129.51s，1 个无关 urllib3/LibreSSL warning）；基线 311 + 1 新用例 |
| 8 | 设计 PASS + 实现审计 | ⏳→本报告 | 设计 PASS 100/A（`f3be5d9`）；本实现审计即第 8 项 |

## 3. 实现与设计 §4 逐条对照

| 段 | 设计目标 | 实测 | 结果 |
|:--|:--|:--|:--|
| §4.1 代码 A 组（28→31 ×4） | L793/L911/L1134/L1263 | 四处置换为 31 文件 | ✅ |
| §4.1 代码 B 组（×8→×9 ×5） | L1134/L1138/L1207/L1234/L1296 | 五处置换为 ×9/9 个 | ✅ |
| §4.1 代码 C 组（产物构成注释 ×3） | L1137/L1202/L1219 | 20→22 / 8→9 / 16→18 | ✅ |
| §4.1 注册表 SKILL_TO_GROUP | +1 项 | L1053 `'github-issue-feedback': ('table','指令 CLI')`（D1 归 table 组） | ✅ |
| §4.2 A 组断言 | EXPECTED_SKILLS/L109/L239/L252/L342 + test_prompt_cmd | 9 项/31 文件/22/9/27 + test_06 | ✅ |
| §4.2 B 组注释/消息串 | 6 处 | L5/L21/L104/L235-236/L179/L309/L370 全同步 | ✅ |
| §4.3 文档 | 全表（AGENTS×2/features/skills×2/README 双源/handbook×2） | 逐行 grep 命中，历史行未改写 | ✅ |
| §4.4 产物结构 | 22/18/9 + 统计行 | `n_total = len(skills)*3+4`=31；统计行 `9 skills (31 文件: 门户 + kb×9 + md/json×18 + all.md)` | ✅ |
| §8 复用指引 | 6 步 + 4 类形态 | 与脚本 docstring/HINT/prog/DEFAULT_CONFIG 逐条对照一致（见 §4 质量审计） | ✅ |

## 4. 交付物质量审计（本闭环重点）

### 4.1 事实准确性（逐条对照源码）

| 声明 | 源码实测 | 结果 |
|:--|:--|:--|
| `--feedback-repo` 仅 table / 三级取值 | `html-gen.py` L893 + `feedback_repo_args()` L135-150（CLI>env>JSON，空串禁用） | ✅ |
| `options.feedback` 五字段 repo/dataset/key/altKey/template | `layout-table.html` L357 注释 + `buildFeedbackUrl()` L1087-1107（key 默认 name/altKey 空/template 默认 data-fix.yml） | ✅ |
| 校验链 11 步顺序 | `plan_issues()` L227-283 | 🟡 **见 HG-SEC-155**（SKILL.md 主文件顺序错） |
| CLI 十态 | argparse L448-452 + docstring 用法 9 行 | ✅ 十态齐全 |
| 退出码 0/1/2 | `die()` code=2 缺省；1=拉取失败/预检脏/提交失败/重建失败；0=正常 | ✅ |
| HINT/prog/DEFAULT_CONFIG | L302 `HINT` / L432 `prog='countries-issue-sync.py'` / L40 `DEFAULT_CONFIG`（通用路径）；无 `DEFAULT_TARGET` | ✅ |
| docstring 4 类 countries 形态 | 脚本名×9（L11-19）/ 表单模板名（L5）/ target 名（L19）/ 设计文档名（L25） | 🟢 **见 HG-SEC-156**（×8 vs 9） |
| rebuild.args 四项 | `feedback-targets.yaml` L62-71（--github-url/--home-url/--favicon/--feedback-repo） | ✅ |

### 4.2 可执行性（adoption-prompt 6 步 + 验收清单）

6 步（数据 JSON 声明 → 重建命令固化 → Issue Form → label/config → target 配置 → 复制脚本替换）无缺步、无自相矛盾；Step 6 替换清单 6 项与源码对应（漏改后果标注准确）。验收清单 4 段可复跑（--check-template / 页面按钮 / --list→--dry-run→--apply --no-commit / --apply --close）。占位符规范（`<owner>/<repo>`/`<case>`），无环境私货。✅

### 4.3 安全红线一致性（skill 声明 6 条 vs 脚本现状）

| 红线 | 脚本现状 | 结果 |
|:--|:--|:--|
| 白名单+硬保护双层 | `guarded_fields()` L210-215 先于 editable L242 | ✅ |
| 入库 XSS（`<`/`>` 拒绝） | L262-265 string 分支 | ✅ |
| 显式 pathspec（禁 -A） | L328 `git add --` + L332 `git commit -- <paths>`；全脚本无 `git add -A` | ✅ |
| 写盘前预检 | L534-539 `git_dirty` 非空 exit 1 | ✅ |
| 失败不回滚 | 提交失败 L585 回评「待维护者处理」+ return 1，无回滚 | ✅ |
| 全链路 shell=False | `run()` L51 `subprocess.run(..., shell=False)` | ✅ |

### 4.4 内容红线

- 无版本演进史（仅一句「已在 countries 案例落地 (CL009+CL010)」背景引用）；无一次性 issue 处置记录（issue #2 引用仅作机制约束论据）；未复制脚本正文（C1，仅指路 + 替换清单）。✅
- 无环境私货：参考实现路径均为 html-gen.cli 本仓相对/公开 URL，采用占位符。✅

### 4.5 合规（PII/令牌/私密路径）

grep 全四文件 `imjaden|jaden|@email|/Users/|/home/|ghp_|gho_|token|password|api_key|secret|PRIVATE KEY` —— 零命中；无真实邮箱、token、内网地址、绝对路径。✅

## 5. 挂载副作用核查

- 既有 8 skill prompt 输出：确定性集（22 顶层文件，含 8 skill md/json）逐字节一致 → 零回归。✅
- `all.md`/`index.html`/`_kb-data.json` 仅因新增条目变化（预期）。✅
- `SKILL_TO_GROUP` 归组符合 D1（table 组「指令 CLI」），门户 5 tab/3 section 结构不变。✅
- `_site_kb_items` 计数 27 = 9 skill + 6 guide + 12 case 正确。✅

## 6. 发现项

| # | 严重度 | 位置 | 描述 | 处置建议 |
|:--|:--|:--|:--|:--|
| HG-SEC-155 | 🟡 | `skills/github-issue-feedback/SKILL.md` L44-45 | 数据流图校验链顺序与源码不符：写「行唯一定位 → 类型 → 非空」，源码 `plan_issues()`（L245-259）实际为「非空 → 行唯一定位 → 类型」。`references/feedback-targets-schema.md` §2 顺序正确（#6 非空/#7 行定位/#8 类型），故为主 SKILL.md 与自身 reference + 源码三方不一致。根因：设计 §3.3 L72 同序错误被三轮评审以「设计自述」为据而未对照源码核销 | 重排 L45 三词为「非空 → 行唯一定位 → 类型」；设计 §3.3 L72 同句作 docs errata 一并订正（可选） |
| HG-SEC-156 | 🟢 | `SKILL.md` L141 | 「脚本名 ×8」与 docstring 实际 9 处示例命令行（L11-19）不符；`references/issue-feedback-adoption-prompt.md` L164 用「约 8 处」更准确 | 将「×8」改「约 9 处」或「×9」，与 adoption-prompt 措辞对齐 |
| HG-SEC-157 | 🟢 | `references/issue-form-template.md` §3 + `adoption-prompt.md` §5 | config.yml 模板含 `contact_links` 重定向段，但 html-gen.cli 实际 `.github/ISSUE_TEMPLATE/config.yml` 仅 `blank_issues_enabled: false` 单行；且 issue-form-template.md L4 声称「把读者引导到表单」与实际不符 | 二选一：给参考实现 config.yml 补 contact_links 段，或在 skill 内标注「模板为增强版，参考实现实际仅单行」 |

> 非 finding 观察（无需修）：设计 §4.3 两处 handbook 计数目标写「311」，实现落地为「312」（新增 1 用例后实际），与设计 §5 项 7「新增用例后计数上浮」一致，属设计规划值与实际的正常收敛。

## 7. 处理

- ⏳ CONDITIONAL PASS → 写报告 + review-log + .review-level.yaml，**不 commit / 不 push**（待 ops 折入 HG-SEC-155..157 后复审）
- HG-SEC-155 为唯一 🟡，修复 = 一处三词重排（非阻塞，但属交付物事实准确性，应交 ops 修正）
- 报告: `documents/review/github-issue-feedback-skill-impl-audit-v1.0-20260912.md`
