# GitHub Issue 反馈通道 skill 沉淀 — ops 核查报告 v1.0

> 闭环: HTML-GEN-CL011 · 步骤: [4/6] ops 核查
> 日期: 2026-09-12 · 执行: ops（本会话）
> 核查对象: commit `edd3e90`（dev）+ `8bbc575`（AGENTS.md 同步）
> 设计基线: `documents/solutions/github-issue-feedback-skill-design-v1.2-20260912.md`（评审 PASS `f3be5d9`）

## 1. 核查结论

**通过** —— 设计 §5 八项验收标准逐项实测命中，无阻断偏差；工作树干净，可进 [5/6] 实现审计。
三项如实记录的非阻断说明见 §4。

## 2. 逐项核对（设计 §5 验收标准）

| # | 验收标准 | 实测 | 证据 |
|:--|:--|:--|:--|
| 1 | skill 四文件、每篇 ≤250 行 | ✅ | `wc -l`: SKILL.md 155 / adoption-prompt 203 / targets-schema 106 / form-template 136（合计 600） |
| 2 | prompt 四态正常 | ✅ | 列表含 `github-issue-feedback` + description + 3 refs；全文 = SKILL.md + references 拼接；`--brief` 输出 9 章节 + refs；`--json` `status:ok`，data 键 `{content,name,references}`（3 refs） |
| 3 | `prompt --site` 31 文件 + 门户 table 组新增条目 | ✅ | 生成统计行 `9 skills (31 文件: 门户 + kb×9 + md/json×18 + all.md)`；`find prompts -type f` = **31**（顶层 22 + kb/ 9）；`_kb-data.json` = **27 条**，新增条目 `{title: github-issue-feedback, group: table, section: 指令 CLI, badge: Prompt, url: kb/github-issue-feedback.html}`；`prompts/index.html` 含该条目 |
| 4 | 测试同步（含 L239/L252/L342 + 注释消息串）全绿 | ✅ | `pytest -n 0` → **312 passed**；三处硬断言现状值 22 / 9 / 27；注释与消息串 6 处同步（L5/L21/L104/L235-236/L179/L309/L370） |
| 5 | `prompts/` 重生成并提交 | ✅ | 已随 dev 提交（新增 3 文件 + 变更 all.md/index.html/_kb-data.json/18 md·json）；重生成后幂等：确定性集（22 文件）**零 diff**；`kb/*.html` 仅 doc meta 时间戳行变化（HG-SEC-086 既有 wildcard，已还原提交版本） |
| 6 | 文档面同步（§4.3 全表） | ✅ | AGENTS.md（L58 18→31 / L299 311→312 且文件数 31→30 修正 / L326 288→312 / 目录树 +1 行）；features.md（主命令组 +1 行、测试计数 312）；skills/html-gen/SKILL.md（L63/L69/L70 + 变更记录追加 v2.7.0 + frontmatter 2.4.0→2.7.0）；skills/html-gen-cli-spec/SKILL.md L35；README.md + README.zh.md 各 3 行；html-gen-cli-handbook 16 行（含 P15 与 2 条待办闭环）；pages-content-handbook L32 |
| 7 | 全量 pytest 零回归 | ✅ | `python3 -m pytest tests/ -q -n 0` → **312 passed**（127.11s）；基线 311 + 新增 1 用例（`test_prompt_cmd::test_06_prompt_feedback_skill_references`） |
| 8 | 设计评审 PASS（+ 实现审计待 [5/6]） | ✅/⏳ | 设计评审 PASS 100/A（`f3be5d9`，三轮：CONDITIONAL 90 → CONDITIONAL 95 → PASS）；实现审计 [5/6] 待执行 |

## 3. 独立核查（非仅信 dev 自述）

| 项 | 方法 | 结果 |
|:--|:--|:--|
| 计数文案穷举 | 全仓 grep `28 文件\|28 files\|×8\|×16\|8 skills\|8 篇\|26 条\|顶层 20\|16 md/json\|kb/ 8\|268 collected\|288 tests\|18 文件` | 残留 9 处**全部为合法历史归属行或评审记录**：`html-gen-cli-handbook` L61/L62/L90（CL007/CL008 历史行）、L262（P15 闭环说明）、`skills/html-gen/SKILL.md:315`（v2.5.0 变更记录）、`skills/github-issue-feedback/SKILL.md:141`（描述脚本 docstring 的 ×8 形态）、`engineering-testing-handbook:75`（sleep 映射数字，无关）、`.review-level.yaml`（评审 tracking 文本）。**现行状态断言零残留**。 |
| 门户可达性 | `_kb-data.json` 条目 → `kb/github-issue-feedback.html` 存在 | ✅ 文件在 31 文件清单内 |
| 幂等性 | 重跑 `prompt --site` 后 `git status prompts/` | ✅ 确定性集零 diff（kb/ 时间戳 wildcard 已还原） |
| 语法/健康 | `python3 -m py_compile html-gen.py` | ✅ OK |

## 4. 偏差与说明（如实记录，均非阻断）

| # | 项 | 说明 | 处置 |
|:--|:--|:--|:--|
| D1 | **AGENTS.md 写入需交互审批** | 该文件为受保护 agent-instruction 文件：dev 期间两次自动审批超时被拦（未绕过）；用户显式批准后 5 处 patch 落盘并单独提交 `8bbc575` | 已闭环；后续闭环建议提前在 dev 步申请授权 |
| D2 | **`kb/*.html` 重生成出现时间戳 diff** | 9 个 kb detail 页各 1 行 doc meta 时间戳变化（HG-SEC-086 既有 wildcard：kb 页排除于确定性集） | 已 `git checkout` 还原提交版本；设计 §4.4 已声明该 wildcard |
| D3 | **步骤 usage 记账为 0** | `hm loop sync/step-done` 按 commit 时间 + session title 匹配会话；评审跑在 **review profile** 库、本会话 title 为 `HTML-GEN-CL010-ongoing` → 均未命中，steps 1–3 的 token/cost 记 0 | 留待人工决定是否回填（当前会话真实累计 in 866K / out 57K / $0.041，含 CL010+CL011 全过程，无法按闭环拆分） |
| D4 | handbook §3 演进主线 CL011 行 | 设计 §4.3 标为可选（评审/审计列待 [5/6] 回填） | 未做；可在 [5/6] 后一行补齐或 [6/6] 复盘时处理 |

## 5. 产物与环境事实

| 项 | 值 |
|:--|:--|
| dev commit | `edd3e90`（32 文件，3697+/79−） |
| AGENTS.md commit | `8bbc575`（4+/3−） |
| 新增 skill | `skills/github-issue-feedback/`（4 文件，600 行） |
| prompts/ 规模 | 31 文件（顶层 22 + kb/ 9） |
| 测试 | 312 passed（`-n 0`，试运行 127–129s） |
| 工作树 | 干净（仅评审 profile 的 review-log/.review-level 待 [5/6] 由 review 处置） |
| 未推送 | 9 commit（CL010 `5f447fc` + CL011 设计链 4 + 评审 `f3be5d9` + dev `edd3e90` + AGENTS.md `8bbc575` + 本报告） |
