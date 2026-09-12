# GitHub Issue 反馈通道 skill 沉淀设计 v1.1 (2026-09-12)

> 闭环: HTML-GEN-CL011 · 模式: 独立
> 决策（全量，用户定稿）: A2 B1 C1 D1 E1 F1 G1 H1
> 基线: v1.0（2026-09-11）→ 本轮折入设计评审 CONDITIONAL PASS findings **HG-SEC-145..150**
> 评审报告: `documents/review/github-issue-feedback-skill-design-review-v1.0-20260911.md`（唯一结论源）
> 前置: CL009 ✅ [6/6]；CL010 实现已落地（`5f447fc`，审计/推送另计）

## 0. v1.0 → v1.1 变更摘要（全部为「改动面清单完备性」修正，决策层不变）

| Finding | 严重度 | v1.0 缺陷 | v1.1 修正 |
|:---|:---|:---|:---|
| HG-SEC-145 | 🟡 | §4.2 测试清单漏 3 处**硬断言**（第 9 个 skill 加入后必红 → §5.4 不可达） | §4.2 补列 L239（20→22）/ L252（8→9）/ L342（26→27）；§6 缓解扩为四处断言 |
| HG-SEC-146 | 🟡 | §4.1 计数注释清单不完整 + L1263 误分类 + 漏「顶层 20/16 md/json/kb 8」组 | §4.1 重排为**三组**（28 文件组 4 处 / ×8 组 5 处 / 顶层 20·16·kb8 组 3 处） |
| HG-SEC-147 | 🟢 | §4.3 指示改 `skills/html-gen/SKILL.md:314` 会**改写历史变更记录**（v2.5.0 行） | 改为**追加**新条目 v2.7.0；L63/L69（当前 spec）才做 28→31 / ×8→×9 |
| HG-SEC-148 | 🟢 | §4.3「features.md skills/能力段」**无此段**，落点悬空 | 指定落点：「### 主命令组 (html-gen CLI)」`--feedback-repo` 行（L24）后新增能力行 |
| HG-SEC-149 | 🟢 | C1「改 3 处」仅提脚本名，docstring 内 countries 有 **4 种形态** | §8 逐项枚举 4 类替换（脚本名×8 / 表单模板名 / target 名 / 设计文档名） |
| HG-SEC-150 | 🟢 | `feedback-targets-schema.md` ~130 行承载 20 字段 + 10 步链 + 10 态 CLI + 5 红线偏紧 | §3.1/§3.3 放宽至 **~200 行**（仍守 E1 ≤250）；总预算 ~700 行 |

评审已确认无误的锚点（无需改动，实施时直接引用）：`cmd_prompt` L928-1030 / `SKILL_TO_GROUP` 8 项 / `SITE_GROUPS` 5 tab / `_site_kb_items` / `cmd_prompt_site` / `n_total` 动态计算（9×3+4=31，L1264 无需改）/ `AGENTS.md:58` 既存漂移属实 / 反馈四件套 + CL010 `<`·`>` 拒绝（脚本 L262-264）。

## 1. 背景与目标

### 1.1 现状
反馈闭环能力**已完整就绪**（CL009 + CL010），共四件套：

| 层 | 产物 | 位置 |
|:---|:---|:---|
| 页面侧 | 分栏预览 header ✏️ 按钮 → Issue Form；`--feedback-repo` / env `HTML_GEN_FEEDBACK_REPO` / `options.feedback.{repo,dataset,key,altKey,template}` 三级开关 | `layout-table.html`、`html-gen.py` |
| 表单侧 | 字段下拉（`标签｜key`）+ 值 textarea；`config.yml` 关闭 blank issue | `.github/ISSUE_TEMPLATE/data-fix-countries.yml`（84 行） |
| 配置侧 | target 定义（repo/label/dataset/template/page/data/html/key_field/alt_key/editable/protected/key_guard/commit.scope/types/parse_fields/rebuild.args） | `scripts/feedback-targets.yaml` |
| 脚本侧 | 十态 CLI（`--list/--dry-run/--apply/--close/--no-commit/--issue/--field/--value/--value-file/--check-template/--json`）+ 校验链 + CL010 入库 `<`/`>` 拒绝（L262-264） | `scripts/countries-issue-sync.py`（600 行，config 驱动） |

**缺口不是能力，是载体**：知识分散在 5 个版本的 `documents/solutions/countries-issue-feedback-design-v1.0..v1.4`、`documents/review/*`、ops profile reference 315 行、脚本 docstring 与源码注释中——其他项目 agent 无法「一条命令拿到完整接入规范」。

### 1.2 目标
1. **通用化**：沉淀为可复制载体，其他项目（静态页 + 数据 JSON + 重建脚本形态）按一份 prompt 即可接入
2. **可挂载**：写入项目 `skills/`，通过 `html-gen prompt github-issue-feedback`（含 `--brief/--json`）与 `html-gen prompt --site` 对外供给

### 1.3 非目标（本轮边界）
- **不改脚本行为**（C1）：`countries-issue-sync.py` 保持现状，仅文档化接入路径
- **不改模板/渲染/CLI 参数语义**：零功能变更，仅新增 skill 与挂载注册
- **不写 ops profile**（F1）：ops 侧 reference 本轮不动，避免同知识两处维护
- **不做门户结构变更**（D1）：复用既有 5 tab

## 2. 决策定稿

| 项 | 决策 | 论证 |
|:---|:---|:---|
| A | **A2** 命名 `github-issue-feedback` | `html-gen prompt <name>` 已体现项目语境（同族先例 `pages-index` / `test-speed-optimization` 均不带 `html-gen-` 前缀）；跨项目复用语义更中性 |
| B | **B1** SKILL.md + 3 references | 「可复制」是本闭环核心价值 → 必须有可整体转交的接入 prompt |
| C | **C1** 脚本冻结仅文档化 | 脚本 600 行刚经 CL010 加固；改名波及 `tests/test_issue_feedback.py`（37 用例引用脚本名）与文档面，风险不对称 |
| D | **D1** 门户归 `table` 组「指令 CLI」 | 能力当前 table 模板专属（✏️ 按钮 + `--feedback-repo` 均 table-only） |
| E | **E1** references 全量进 prompt | `html-gen prompt <name>` 是 SKILL.md + references 全文拼接 → **单篇 ≤250 行**硬约束 |
| F | **F1** 仅项目 skills | 单一事实源；ops 侧 reference 收敛为指针另开动作 |
| G | **G1** 测试文档全量同步 | 计数断言/硬编码文案/门户产物构成对外契约，不同步即测试红或站点缺项 |
| H | **H1** 新立项 CL011 | CL010 已进入审计阶段，混入会打断审计节奏与复盘粒度 |

## 3. skill 内容设计

### 3.1 目录结构（行数预算，HG-SEC-150 调整）
```
skills/github-issue-feedback/
├── SKILL.md                                   # ~180 行: 何时用 + 架构 + 快速接入 + 契约 + 红线 + 运维
└── references/
    ├── issue-feedback-adoption-prompt.md      # ~220 行: 跨项目落地 prompt（核心交付物）
    ├── feedback-targets-schema.md             # ~200 行: 字段表 + 校验链 + CLI 十态 + 安全红线（v1.1 由 130 放宽）
    └── issue-form-template.md                 # ~100 行: Issue Form yml 模板 + 约束 + label 约定
```
合计 ~700 行；每篇均 ≤250 行（E1）。超长内容按 §3.4 红线改指路设计文档。

### 3.2 SKILL.md 章节大纲
```
frontmatter: name/description/version 1.0.0/author ops/license MIT/metadata.hermes.tags/related_skills
## 何时使用            — 触发条件（页面需数据纠错入口 / 已有数据 JSON + 重建脚本 / 想接 GitHub 反馈闭环）
## 能力总览            — 四件套架构 + 数据流（读者 ✏️ → Issue Form → gh 拉取 → 校验链 → 写回 JSON → 重建 → 回评[/关闭] → 本地提交）
## 快速接入（6 步）    — 摘要级，详版指向 references/issue-feedback-adoption-prompt.md
## CLI 契约            — 页面侧三参数（--feedback-repo/env/options.feedback）+ 脚本十态速查
## 安全红线（必读）    — 白名单+主键双层保护 / 入库 XSS 拒绝 / 显式 pathspec / 写盘前预检 / 不回滚语义
## 运维               — --list 巡检 / 幂等 / 冲突取最新 / --no-commit 逃生口 / --close 语义
## 本仓现状            — countries 试点 + 设计文档索引（v1.0..v1.4 + 审计报告）+ 源码指路
## 复用差异点          — 其他项目接入需替换的位置（见 §8）
## references 索引
```

### 3.3 references 大纲

**① `issue-feedback-adoption-prompt.md`（核心交付物，跨项目可整体复制）**
- 适用判定（前置：静态 HTML 页 + 同源数据 JSON + 可重建生成命令 + GitHub 仓库 + `gh` CLI 已认证）
- 6 步接入，每步含可复制片段 + 验证方法：
  1. 数据 JSON 加 `options.feedback.{repo,dataset,key,altKey,template}`
  2. 生成命令加 `--feedback-repo <owner/repo>`（及 `--github-url/--home-url/--favicon` 重建参数固化）
  3. 复制 Issue Form 模板并按案例改下拉选项
  4. 建 `data-fix` label + `config.yml`
  5. 写 `feedback-targets.yaml` target（字段表见 ②）
  6. 复制同步脚本并替换 **docstring 内 4 类 countries 形态**（HG-SEC-149，见 §8）+ `HINT`（L302）+ `argparse prog`（L432）
- 首次验收清单（`--check-template` → 页面按钮可见 → 造测试 issue → `--list` → `--dry-run` → `--apply --no-commit` → 视觉核对 → 回滚）

**② `feedback-targets-schema.md`（~200 行）**
- target 逐字段表（字段 / 类型 / 必填 / 语义 / 默认）—— 20 字段全枚举
- 校验链顺序（page → dataset → 字段解析 → 主键硬保护 → editable 白名单 → 行唯一定位 → 类型 → 非空 → 入库 XSS 防护 → 幂等 → 冲突取最新）
- CLI 十态速查 + 退出码语义（0/1/2）
- 安全红线 5 条（显式 pathspec / 写盘前预检 / 失败不回滚 + exit 1 / 入库 `<`·`>` 拒绝 / `shell=False` 全链路）

**③ `issue-form-template.md`（~100 行）**
- Form yml 可复制模板（dropdown 字段 / textarea 值 / 只读说明段）
- 约束与机制原因：**下拉不可 URL 预填**（GitHub Issue Forms 限制）→ 页面不预填 field；主键/匹配键不进下拉（双层保护第一层）
- `config.yml` 关闭 blank issue 片段 + `data-fix` label 约定

### 3.4 内容红线
- **写**：可复制的命令/片段、字段契约、校验链、安全红线、验收方法、项目内指路
- **不写**：CL009/CL010 版本演进史（指向 `documents/solutions/`）、一次性 issue 处置记录（#1–#6）、环境私货
- **不复制脚本正文**（C1）：避免双份脚本漂移，改为「`cp` + 替换 §8 清单」指引

## 4. 挂载改动面（精确清单，v1.1 修正）

### 4.1 代码（`html-gen.py`）—— 分三组（HG-SEC-146）

| 组 | 位置 | 现状 | 目标 |
|:---|:---|:---|:---|
| **A. 「28 文件」文案（4 处）** | L793（HELP_OVERVIEW） / L911（argparse help） / L1134（docstring） / **L1263（注释）** | 28 文件 | 31 文件 |
| **B. 「×8 / 8 个」文案（5 处）** | **L1134（docstring 内 ×8）** / L1138（渲染 8 个 kb） / L1207（kb/ 8 个 detail） / L1234（×8 注释） / L1296（all.md 头部「8 个 skills」） | ×8 / 8 个 | ×9 / 9 个 |
| **C. 产物构成注释（3 处，v1.1 新增）** | L1137（`顶层 20 + kb/ 8`） / L1202（`顶层 20 = … + 16 md/json`） / L1219（`写 16 md/json`） | 20 / 8 / 16 | 22 / 9 / 18 |
| — | L1046-1055 `SKILL_TO_GROUP` | 8 项 | +1 项：`'github-issue-feedback': ('table', '指令 CLI')` |
| — | L1264 / L1268-1269 | `n_total = len(skills)*3 + 4` | **无需改**（动态计算 9×3+4=31） |

### 4.2 测试（v1.1 补 3 处硬断言，HG-SEC-145）

| 文件 | 位置 | 现状 | 目标 |
|:---|:---|:---|:---|
| `tests/test_prompt_site.py` | L5 docstring | 「28 文件 = 顶层 20 + kb/ 8」 | 「31 文件 = 顶层 22 + kb/ 9」 |
| | L16-19 `EXPECTED_SKILLS` | 8 项 | +`github-issue-feedback`（L22-24 `EXPECTED_TOP` / L25 `EXPECTED_KB` 由列表派生，自动跟随） |
| | L109 | `assert '28 文件' in r.stdout` | `'31 文件'` |
| | L179 | 「8 个 ## {skill.name} 段标题」断言 | 9 个 |
| | **L239** | `assert len(deterministic) == 20` | **22** |
| | **L252** | `assert len(list((d/'kb').glob('*.html'))) == 8` | **9** |
| | L309 | 「8 个 kb/{skill}.html detail」断言 | 9 个 |
| | **L342** | `assert len(items) == 26` | **27**（9 skill + 6 guide + 12 case） |
| `tests/test_prompt_cmd.py` | L21-26 列表断言 | 4 项抽样 | 补 `github-issue-feedback`（新增 1 用例或并入既有） |

### 4.3 文档（v1.1 修正落点，HG-SEC-147/148）

| 文件 | 位置 | 改动 |
|:---|:---|:---|
| `AGENTS.md` | L58 | **既存漂移修正**「18 文件」→「31 文件」（实测现状 28） |
| `AGENTS.md` | 目录结构段（L327 附近） | skills 清单加 `github-issue-feedback/SKILL.md` |
| `features.md` | **「### 主命令组 (html-gen CLI)」L24 `html-gen table --feedback-repo` 行之后新增一行** | `html-gen prompt github-issue-feedback — GitHub Issue 反馈通道接入规范 skill ✅ — skills/github-issue-feedback/SKILL.md`（**不新造段**：features.md 无 skills/能力段） |
| `skills/html-gen/SKILL.md` | L63 / L69（**当前 spec 正文**） | 28→31 / ×8→×9 |
| `skills/html-gen/SKILL.md` | **L314 区域「## 变更记录」** | **追加**新条目 `- v2.7.0 (2026-09-12): prompt --site 28→31 文件（新增 github-issue-feedback skill 挂载）`；**不得改写 v2.5.0 历史行**；同步 frontmatter `version: 2.7.0` |
| `skills/html-gen-cli-spec/SKILL.md` | L35 | 「站点 (28 文件)」→ 31 |
| `README.zh.md` | L84 | 「生成 `prompts/` 站点（28 文件）」→ 31 |
| `skills/github-issue-feedback/SKILL.md` | 新建 | 本闭环主产物 |

### 4.4 产物
`html-gen prompt --site` 重生成 `prompts/`：28 → **31 文件**
- 顶层 **22** = index.html + all.md + _kb-groups/_kb-data json + **18**（9 skill × md/json）
- `kb/` **9** detail
- 新增：`prompts/github-issue-feedback.md` / `.json` / `kb/github-issue-feedback.html`
- 变更：`prompts/all.md`（多 1 段）、`prompts/index.html` + `_kb-data.json`（table 组多 1 条目）

## 5. 验收标准
1. `skills/github-issue-feedback/` 新建：SKILL.md + 3 references，**每篇 ≤250 行**
2. `html-gen prompt`（列表）/ `html-gen prompt github-issue-feedback`（全文）/ `--brief` / `--json` 四态正常
3. `html-gen prompt --site` 输出 **31 文件**（顶层 22 + kb/ 9），门户 table 组「指令 CLI」新增 1 条目
4. 测试同步：`tests/test_prompt_site.py`（含 **L239 L252 L342** 三处硬断言）+ `tests/test_prompt_cmd.py` 全绿
5. `prompts/` 重生成并提交（产物勿手改）
6. 文档面 7 处同步（§4.3 全表；含 `AGENTS.md:58` 漂移修正、L314 **追加**语义）
7. 全量 `python3 -m pytest tests/ -q -n 0` 零回归（基线 **311**；新增用例后计数更新至上浮值）
8. 设计评审 PASS + 实现审计 PASS，review 通道 push `github`（ff-only，不推 gitee）

## 6. 风险与兼容

| 风险 | 影响 | 缓解 |
|:---|:---|:---|
| 计数硬编码/断言遗漏 → 测试红或站点文案错 | 中 | §4.1 三组 + §4.2 逐行清单；**测试兜底四处断言 L109 / L239 / L252 / L342**（v1.1 扩） |
| references 过长 → `html-gen prompt` 单次输出过大 | 中 | E1 ≤250 行/篇；总 ~700 行；超长改指路设计文档 |
| skill 与 ops profile reference 双份漂移 | 中 | F1：本轮不写 ops；后续单独立动收敛为指针 |
| 门户 kb 条目缺 groups 映射 → 站点少项 | 低 | D1 显式注册 + `EXPECTED_KB` 断言 |
| `prompts/` 重生成裹入无关 diff | 低 | 重生成后 `git status` 核对，仅提交相关文件 |
| 改写 `skills/html-gen/SKILL.md` 变更记录历史 | 低 | HG-SEC-147 已修正语义：**只追加** v2.7.0 条目 |

**兼容性**：纯增量（新增 skill + 注册 + 文案计数），无 API/参数/模板语义变更；既有 8 个 skill 的 prompt 输出与 kb 页不受影响（`all.md`/`index.html` 因新增条目而变更，属预期）。

## 7. 实施步骤（2/6 起）

```
[2/6] 设计评审 → CONDITIONAL PASS（HG-SEC-145..150）→ 本 v1.1 修正 → 复审（re-review）至 PASS
[3/6] dev 实现
      a. 写 skills/github-issue-feedback/{SKILL.md, references ×3}（§3 大纲 + 行数预算）
      b. 挂载: SKILL_TO_GROUP +1 / §4.1 三组文案 / §4.4 产物构成注释
      c. 测试同步: §4.2（test_prompt_site 8 处 + test_prompt_cmd）
      d. 文档同步: §4.3（7 处，含 AGENTS.md:58 漂移 + L314 追加语义）
      e. prompts/ 重生成 + 产物核对（22 顶层 + 9 kb）
[4/6] ops 核查 —— 四态 prompt 实测 + 31 文件清单核对 + 门户 kb 可达 + 全量 pytest
[5/6] 实现审计（review role）—— 逐条对照 §5 八项验收标准
[6/6] 复盘
```

## 8. 跨项目复用指引（C1/HG-SEC-149 修正）

```
1) cp <html-gen.cli>/scripts/countries-issue-sync.py <project>/scripts/<case>-issue-sync.py
2) 替换 docstring 内 4 类 countries 形态（HG-SEC-149 实测枚举）:
   a. 脚本名 ×8 处（示例命令行）
   b. 表单模板名 data-fix-countries.yml（L5）
   c. target 名 countries（L19 --target countries 示例）
   d. 设计文档名 countries-issue-feedback-design-v1.4（L25）
   再改 HINT 常量（L302）+ argparse prog（L432）
   —— DEFAULT_CONFIG（L40）为通用路径, 无 DEFAULT_TARGET, 无需改
   漏改 b/c 会破 --check-template（模板 dropdown ↔ config.editable 校验）
3) cp <html-gen.cli>/scripts/feedback-targets.yaml → 写本项目 target（data/html/key_field/editable/rebuild.args）
4) cp .github/ISSUE_TEMPLATE/data-fix-countries.yml → 改下拉选项（列标签｜key）
5) 页面生成命令加 --feedback-repo（或数据 JSON options.feedback）
6) 造测试 issue → --check-template → --list → --dry-run → --apply --no-commit → 视觉核对
```
**复用前提（写进 skill 适用判定）**：页面由 `html-gen table` 生成（✏️ 按钮依赖 layout-table）；数据为同源 JSON；有可脚本化的重建命令；仓库有 `gh` 权限。

**候选项目**（非本轮范围）：llm-radar 数据看板、www.jaden.tech 卡片页、http-server.cli 看板类页面。
