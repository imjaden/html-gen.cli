# GitHub Issue 反馈通道 skill 沉淀设计 v1.2 (2026-09-12)

> 闭环: HTML-GEN-CL011 · 模式: 独立
> 决策（全量，用户定稿）: A2 B1 C1 D1 E1 F1 G1 H1
> 基线链: v1.0（`3f7e0ad`）→ v1.1（`b2bf584`，折入 HG-SEC-145..150）→ **v1.2（折入 HG-SEC-151..153 + 附注）**
> 评审报告: `documents/review/github-issue-feedback-skill-design-review-v1.0-20260911.md`（CONDITIONAL PASS 90/A）、`…-v1.1-20260912.md`（CONDITIONAL PASS 95/A）
> 前置: CL009 ✅ [6/6]；CL010 实现已落地（`5f447fc`，审计/推送另计）

## 0. v1.1 → v1.2 变更摘要

| Finding | 严重度 | v1.1 缺陷 | v1.2 修正 |
|:---|:---|:---|:---|
| HG-SEC-151 | 🟡 | §4.3 漏 README 文案：`README.zh.md` L95/L96（×8 / 8 skills）+ 英文 `README.md` 整体未列（L84/L95/L96） | §4.3 新增「README 双源」组（6 行：两文件 × L84/L95/L96） |
| HG-SEC-152 | 🟢 | handbook（`documents/html-gen-cli-handbook-v1.0-20260908.md`）现行状态计数未覆盖，且未声明冻结 | **折入 §4.3**（非冻结）——依据先例：CL009 曾于同一 feat commit（`1b1ac53`）同步更新该 handbook L48；本轮列为 15 行清单 |
| HG-SEC-153 | 🟢 | 未说明 `skills/html-gen/SKILL.md` frontmatter 现为 `2.4.0`（落后变更记录 v2.6.0 两版） | §4.3 附注现状与目标（`2.4.0 → 2.7.0`） |
| 附注（🟢） | — | `tests/test_prompt_site.py` 注释/消息串计数未枚举（L21/L104/L235-236/L370） | §4.2 增列「注释与消息串」组（不红测试，但同步以免漂移） |
| 本次自查补漏 | — | v1.1 漏 `skills/html-gen/SKILL.md:70`（`×16`）与 `pages-content-handbook:32`（测试计数 268） | §4.3 一并列入 |

**范围判定规则（防无限轮次，本轮起生效）**

| 类别 | 判定 | 处置 |
|:---|:---|:---|
| **现行状态断言** | 描述「当前」产物/计数/挂载量的文案（如 `prompt --site` 28 文件、skills 8 篇、`pytest` 268） | **纳入本轮同步** |
| **历史归属行** | 带闭环归属的历史记录（`§3 演进主线` CL007/CL008 行、`### 5.1 v1 契约（CL007，18 文件）`、`skills/html-gen/SKILL.md` 变更记录旧版本行） | **不改写**；如需体现新闭环则**追加**新行 |
| **归档快照** | `documents/archive/*`、`documents/review/*`（历史报告）、`cache/` | **不触碰** |

## 1. 背景与目标（同 v1.0/v1.1，摘要）

反馈闭环能力已就绪（CL009 + CL010）：页面侧 ✏️ 按钮（`--feedback-repo`/env/`options.feedback`）+ Issue Form（`.github/ISSUE_TEMPLATE/data-fix-countries.yml`，84 行）+ 配置（`scripts/feedback-targets.yaml`）+ 脚本（`scripts/countries-issue-sync.py`，600 行，十态 CLI + 校验链 + 入库 `<`·`>` 拒绝 L262-264）。

**缺口是载体**：知识分散在 5 版设计文档 + ops reference + 源码注释，其他项目无法一条命令接入。

**目标**：① 通用化（可复制接入 prompt）② 挂载 `html-gen prompt`（列表/全文/--brief/--json）与 `html-gen prompt --site`。

**非目标**：不改脚本行为（C1）；不改模板/渲染/CLI 语义；不写 ops profile（F1）；不做门户结构变更（D1）。

## 2. 决策定稿

| 项 | 决策 | 论证 |
|:---|:---|:---|
| A | **A2** `github-issue-feedback` | `html-gen prompt <name>` 已体现项目语境（先例 `pages-index`/`test-speed-optimization` 无前缀） |
| B | **B1** SKILL.md + 3 references | 可复制载体是本闭环核心 |
| C | **C1** 脚本冻结仅文档化 | 脚本刚经 CL010 加固；改名波及 37 用例 + 文档面 |
| D | **D1** `table` 组「指令 CLI」 | 能力当前 table 专属 |
| E | **E1** references 全量进 prompt，单篇 ≤250 行 | `cmd_prompt` 为全文拼接 |
| F | **F1** 仅项目 skills | 单一事实源 |
| G | **G1** 测试文档全量同步 | 计数/文案是对外契约 |
| H | **H1** 独立立项 CL011 | 与 CL010 审计解耦 |

## 3. skill 内容设计

### 3.1 目录结构与行数预算
```
skills/github-issue-feedback/
├── SKILL.md                                   # ~180 行
└── references/
    ├── issue-feedback-adoption-prompt.md      # ~220 行（核心交付物）
    ├── feedback-targets-schema.md             # ~200 行（20 字段 + 校验链 + 十态 CLI + 5 红线）
    └── issue-form-template.md                 # ~100 行
```
合计 ~700 行；每篇 ≤250 行（E1）。

### 3.2 SKILL.md 章节大纲
```
frontmatter: name/description/version 1.0.0/author ops/license MIT/metadata.hermes.tags/related_skills
## 何时使用 / ## 能力总览 / ## 快速接入（6 步）/ ## CLI 契约
## 安全红线（必读）/ ## 运维 / ## 本仓现状 / ## 复用差异点 / ## references 索引
```

### 3.3 references 大纲
1. **`issue-feedback-adoption-prompt.md`**：适用判定 + 6 步接入（每步可复制片段 + 验证法）+ 首次验收清单；第 6 步含 docstring 4 类 countries 形态替换（见 §8）
2. **`feedback-targets-schema.md`**：target 20 字段表 + 校验链顺序（page→dataset→字段解析→主键硬保护→editable 白名单→非空→行唯一定位→类型→入库 XSS 防护→幂等→冲突取最新）+ CLI 十态与退出码 + 安全红线 5 条
3. **`issue-form-template.md`**：Form yml 模板（dropdown/textarea）+ 机制约束（下拉不可 URL 预填 → 页面不预填 field；主键/匹配键不进下拉）+ `config.yml` + label 约定

### 3.4 内容红线
写可复制片段/字段契约/校验链/安全红线/验收法/指路；不写版本演进史与一次性 issue 处置记录；不复制脚本正文（C1）。

> **勘误（2026-09-12，实现审计 HG-SEC-155）**：§3.3 第 2 项原写校验链「行定位 → 类型 → 非空」（笔误，三轮设计评审以设计自述为据未对照源码核销）。正确顺序为 **非空 → 行唯一定位 → 类型**（源码 `scripts/countries-issue-sync.py` `plan_issues()` L245-259；`references/feedback-targets-schema.md` §2 行序正确）。实现已按正确序落盘。

## 4. 挂载改动面（精确清单）

### 4.1 代码（`html-gen.py`）

| 组 | 位置 | 现状 | 目标 |
|:---|:---|:---|:---|
| A「28 文件」文案（4） | L793 / L911 / L1134 / L1263 | 28 文件 | 31 文件 |
| B「×8 / 8 个」文案（5） | L1134(×8) / L1138 / L1207 / L1234 / L1296 | ×8 / 8 个 | ×9 / 9 个 |
| C 产物构成注释（3） | L1137（`顶层 20 + kb/ 8`） / L1202（`顶层 20 = … + 16 md/json`） / L1219（`写 16 md/json`） | 20 / 8 / 16 | 22 / 9 / 18 |
| 注册表 | L1046-1055 `SKILL_TO_GROUP` | 8 项 | +1：`'github-issue-feedback': ('table', '指令 CLI')` |
| 无需改 | L1264 / L1268-1269 | `n_total = len(skills)*3 + 4` | 动态 → 31 |

### 4.2 测试

**A. 断言（会红，必须改）**

| 文件 | 位置 | 现状 | 目标 |
|:---|:---|:---|:---|
| `tests/test_prompt_site.py` | L16-19 `EXPECTED_SKILLS` | 8 项 | +`github-issue-feedback`（L22-24 `EXPECTED_TOP` / L25 `EXPECTED_KB` 派生自动跟随） |
| | L109 | `'28 文件'` | `'31 文件'` |
| | **L239** | `len(deterministic) == 20` | **22** |
| | **L252** | `len(kb/*.html) == 8` | **9** |
| | **L342** | `len(items) == 26` | **27**（9 skill + 6 guide + 12 case） |
| `tests/test_prompt_cmd.py` | L21-26 列表断言 | 4 项抽样 | 补 `github-issue-feedback` 断言（新增 1 用例或并入既有） |

**B. 注释与消息串（不红测试，同步以防漂移，v1.2 新增）**

| 位置 | 现状 | 目标 |
|:---|:---|:---|
| L5 docstring | `28 文件 = 顶层 20 (…/16) + kb/ 8 detail` | `31 文件 = 顶层 22 (…/18) + kb/ 9 detail` |
| L21 注释 | `顶层 20 = … + 16 md/json` | `22 = … + 18 md/json` |
| L104 注释 | `test_01 生成完整性: 28 文件 (顶层 20 + kb/ 8)` | `31 文件 (顶层 22 + kb/ 9)` |
| L235-236 注释 | `确定性集 20 = 16 md/json + …` | `22 = 18 md/json + …` |
| L179 / L309 消息串 | 「8 个」 | 「9 个」 |
| L370 消息串 | `'8 skill 条目不齐'` | `'9 skill 条目不齐'` |

### 4.3 文档

| 文件 | 位置 | 现状 → 目标 |
|:---|:---|:---|
| `AGENTS.md` | L58 | 「18 文件」（**既存漂移**，实测现状 28）→ 「31 文件」 |
| `AGENTS.md` | 目录结构段（L327 附近） | skills 清单 + `github-issue-feedback/SKILL.md` |
| `features.md` | 「### 主命令组 (html-gen CLI)」L24 `--feedback-repo` 行**之后**新增一行 | `html-gen prompt github-issue-feedback — GitHub Issue 反馈通道接入规范 skill ✅ — skills/github-issue-feedback/SKILL.md`（**不新造段**） |
| `skills/html-gen/SKILL.md` | L63 / L69 / **L70**（当前 spec 正文） | 28→31 / ×8→×9 / **×16→×18** |
| `skills/html-gen/SKILL.md` | **L314 区域「## 变更记录」** | **追加** `- v2.7.0 (2026-09-12): prompt --site 28→31 文件（新增 github-issue-feedback skill 挂载）`；**不改写 v2.5.0 历史行** |
| `skills/html-gen/SKILL.md` | frontmatter | `version: 2.4.0`（现状，落后变更记录 v2.6.0 两版）→ `2.7.0` |
| `skills/html-gen-cli-spec/SKILL.md` | L35 | 「站点 (28 文件)」→ 31 |
| **`README.md`（英文）** | L84 / L95 / L96 | `28 files`→31 / `(×8)`→(×9) / `All 8 skills`→`All 9 skills` |
| **`README.zh.md`** | L84 / L95 / L96 | 「28 文件」→31 / 「（×8）」→（×9）/ 「8 skills 全量」→「9 skills 全量」 |
| **`documents/html-gen-cli-handbook-v1.0-20260908.md`（HG-SEC-152）** | L43 | `文本/JSON/站点 28 文件` → 31 |
| | L64 | 测试基线 `268` → `311` |
| | L77 | 「skills/ 现挂载 8 篇（…）+ references 3 个」→ **9 篇**（+`github-issue-feedback`）+ references **6 个** |
| | L95 / L96 | `{skill}.md ×8` / `{skill}.json ×8` → ×9 |
| | L101 | `### 5.2 v2 门户（CL008，28 文件）` → 「（CL008 起，**现 31 文件**）」（归属保留，仅计数） |
| | L107 | `_kb-data.json 26 条条目（skill×8 + guide×6 + case×12）` → **27 条（skill×9 …）** |
| | L108 | `kb/{skill}.html ×8` → ×9 |
| | L109 | `{skill}.md/.json ×16` → **×18** |
| | L169 | `html-gen prompt --site # 生成 prompts/（28 文件）` → 31 |
| | L204 | `覆盖全部 8 skills + references` → 9 |
| | L227 | `prompts/kb/{skill}.html ×8` → ×9 |
| | L262 / L266 | 遗留项 P15「AGENTS.md prompt 段仍『18 文件』、测试计数 247 vs 268」→ 标记**已闭环（CL011：18→31、计数 311）** |
| | L273 | 「skills/（html-gen-cli-spec 等 8 篇）」→ 9 篇 |
| | **不改写** | L61（CL007 行）/ L62（CL008 行）/ L90（`### 5.1 v1 契约（CL007，18 文件）`）——历史归属；可选：§3 演进主线**追加** CL011 行（评审/审计列于 [5/6] 后回填） |
| **`documents/pages-content-handbook-v1.0-20260908.md`** | L32 | 「现仓 268 collected」→ 311 |
| `skills/github-issue-feedback/SKILL.md` + references ×3 | 新建 | 本闭环主产物 |

### 4.4 产物
`html-gen prompt --site` 重生成 `prompts/`：28 → **31 文件**
- 顶层 **22** = index.html + all.md + _kb-groups/_kb-data json + **18**（9 skill × md/json）
- `kb/` **9** detail
- 新增：`prompts/github-issue-feedback.md` / `.json` / `kb/github-issue-feedback.html`
- 变更：`prompts/all.md`（+1 段）、`prompts/index.html` + `_kb-data.json`（table 组 +1 条目）

## 5. 验收标准
1. `skills/github-issue-feedback/` 新建：SKILL.md + 3 references，每篇 ≤250 行
2. `html-gen prompt`（列表/全文/--brief/--json）四态正常
3. `html-gen prompt --site` 输出 **31 文件**（顶层 22 + kb/ 9），门户 table 组新增 1 条目
4. 测试同步：§4.2 A 组断言 + B 组注释/消息串全绿（含 L239/L252/L342）
5. `prompts/` 重生成并提交
6. 文档面同步：§4.3 全表（AGENTS.md×2 / features.md / skills 2 篇 / README 双源 6 行 / 两 handbook 共 16 行）
7. 全量 `python3 -m pytest tests/ -q -n 0` 零回归（基线 **311**；新增用例后计数上浮）
8. 设计评审 PASS + 实现审计 PASS，review 通道 push `github`（ff-only，不推 gitee）

## 6. 风险与兼容

| 风险 | 影响 | 缓解 |
|:---|:---|:---|
| 计数文案/断言遗漏 | 中 | §4 全表（本轮已全仓 grep 穷举）+ 四处测试兜底 L109/L239/L252/L342 |
| references 过长 | 中 | ≤250 行/篇；超长改指路 |
| skill 与 ops profile reference 双份漂移 | 中 | F1 本轮不写 ops |
| handbook 同步面大（16 行）易漏 | 中 | §4.3 逐行清单 + 本轮范围判定规则（历史行不改写） |
| `prompts/` 重生成裹入无关 diff | 低 | 重生成后 `git status` 核对 |
| 改写变更记录历史 | 低 | HG-SEC-147：只**追加**新条目 |

**兼容性**：纯增量，无 API/参数/模板语义变更；既有 8 skill 的 prompt 输出不变（`all.md`/`index.html` 因新增条目而变，属预期）。

## 7. 实施步骤（2/6 起）

```
[2/6] 设计评审 v1.0 → CONDITIONAL PASS（145..150）→ v1.1 → 复审 CONDITIONAL PASS（151..153）→ 本 v1.2 → 复审至 PASS
[3/6] dev: a. skill 四文件 → b. §4.1 挂载 → c. §4.2 测试 → d. §4.3 文档（16+ 行）→ e. prompts/ 重生成
[4/6] ops 核查：四态 prompt + 31 文件清单 + 门户条目 + 全量 pytest
[5/6] 实现审计：逐条对照 §5
[6/6] 复盘
```

## 8. 跨项目复用指引（C1/HG-SEC-149）

```
1) cp scripts/countries-issue-sync.py <project>/scripts/<case>-issue-sync.py
2) 替换 docstring 4 类 countries 形态:
   a. 脚本名 ×8（示例命令行）  b. 表单模板名 data-fix-countries.yml（L5）
   c. target 名 countries（L19）  d. 设计文档名（L25）
   另改 HINT（L302）+ argparse prog（L432）；DEFAULT_CONFIG（L40）为通用路径, 无 DEFAULT_TARGET, 无需改
   漏改 b/c → 破 --check-template
3) cp scripts/feedback-targets.yaml → 写本项目 target
4) cp .github/ISSUE_TEMPLATE/data-fix-countries.yml → 改下拉选项（列标签｜key）
5) 生成命令加 --feedback-repo（或 JSON options.feedback）
6) 造测试 issue → --check-template → --list → --dry-run → --apply --no-commit → 视觉核对
```
**前提**：页面由 `html-gen table` 生成；数据为同源 JSON；有可脚本化重建命令；仓库有 `gh` 权限。
**候选项目**（非本轮）：llm-radar、www.jaden.tech、http-server.cli 看板。
