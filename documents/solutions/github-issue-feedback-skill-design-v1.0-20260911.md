# GitHub Issue 反馈通道 skill 沉淀设计 v1.0 (2026-09-11)

> 闭环: HTML-GEN-CL011 · 模式: 独立
> 决策（全量）: A2 B1 C1 D1 E1 F1 G1 H1
> 前置: CL009（反馈通道）已收官 [6/6]；CL010（入库 XSS 加固）实现已落地（审计/推送另计）
> 目标产物: `skills/github-issue-feedback/`（SKILL.md + references ×3）+ `html-gen prompt` 挂载

## 1. 背景与目标

### 1.1 现状
反馈闭环能力**已完整就绪**（CL009 + CL010），共四件套：

| 层 | 产物 | 位置 |
|:---|:---|:---|
| 页面侧 | 分栏预览 header ✏️ 按钮 → Issue Form；`--feedback-repo` / env `HTML_GEN_FEEDBACK_REPO` / `options.feedback.{repo,dataset,key,altKey,template}` 三级开关 | `layout-table.html`、`html-gen.py` |
| 表单侧 | 字段下拉（`标签｜key`）+ 值 textarea；`config.yml` 关闭 blank issue | `.github/ISSUE_TEMPLATE/data-fix-countries.yml` |
| 配置侧 | target 定义（repo/label/dataset/template/page/data/html/key_field/alt_key/editable/protected/key_guard/commit.scope/types/parse_fields/rebuild.args） | `scripts/feedback-targets.yaml` |
| 脚本侧 | 十态 CLI（`--list/--dry-run/--apply/--close/--no-commit/--issue/--field/--value/--value-file/--check-template/--json`）+ 校验链 + CL010 入库 `<`/`>` 拒绝 | `scripts/countries-issue-sync.py`（600 行，config 驱动） |

**缺口不是能力，是载体**：知识分散在 5 个版本的 `documents/solutions/countries-issue-feedback-design-v1.0..v1.4`、`documents/review/*` 4 份、ops profile reference 315 行、脚本 docstring 与源码注释中——其他项目 agent 无法「一条命令拿到完整接入规范」。

### 1.2 目标
1. **通用化**：把反馈闭环沉淀为可复制载体，其他项目（静态页 + 数据 JSON + 重建脚本形态）按一份 prompt 即可接入
2. **可挂载**：写入项目 `skills/`，通过 `html-gen prompt github-issue-feedback`（含 `--brief/--json`）与 `html-gen prompt --site`（prompts/ 在线阅读站点）对外供给

### 1.3 非目标（本轮边界）
- **不改脚本行为**（C1）：`countries-issue-sync.py` 保持现状，仅文档化「复制 + 改 3 处」接入路径
- **不改模板/渲染/CLI 参数语义**：零功能变更，仅新增 skill 与挂载注册
- **不写 ops profile**（F1）：`~/.hermes/profiles/ops/skills/.../issue-feedback-loop-design.md` 本轮不动，避免同知识两处维护
- **不做门户结构变更**（D1 决定复用既有 tab）

## 2. 决策定稿

| 项 | 决策 | 论证 |
|:---|:---|:---|
| A | **A2** 命名 `github-issue-feedback` | `html-gen prompt <name>` 已体现项目语境（同族先例 `pages-index` / `test-speed-optimization` 均不带 `html-gen-` 前缀）；skill 名不再重复 `html-gen`，跨项目复用语义更中性 |
| B | **B1** SKILL.md + 3 references | 「可复制」是本闭环核心价值 → 必须有可整体转交的接入 prompt（先例：`skills/html-gen-table/references/table-demo-prompt.md` 跨项目模板） |
| C | **C1** 脚本冻结仅文档化 | 脚本 600 行刚经 CL010 加固；改名会波及 `tests/test_issue_feedback.py`（37 用例引用脚本名）与文档面，风险不对称 → 另立闭环 |
| D | **D1** 门户归 `table` 组「指令 CLI」 | 能力当前 table 模板专属（✏️ 按钮 + `--feedback-repo` 均 table-only）；`cli` 组保留给跨模板工具（cli-spec / pages-index / test-speed） |
| E | **E1** references 全量进 prompt | `html-gen prompt <name>` 是 SKILL.md + references 全文拼接 → 单篇 ≤250 行硬约束（防一次输出撑爆上下文） |
| F | **F1** 仅项目 skills | 单一事实源；ops 侧 reference 属 profile 资产，收敛为指针另开动作 |
| G | **G1** 测试文档全量同步 | 计数断言/硬编码文案/门户产物构成对外契约，不同步即测试红或站点缺项 |
| H | **H1** 新立项 CL011 | CL010 已进入审计阶段，scope 为入库 XSS 加固；skill 沉淀是新交付物，混入会打断审计节奏与复盘粒度 |

## 3. skill 内容设计

### 3.1 目录结构
```
skills/github-issue-feedback/
├── SKILL.md                                   # ~180 行: 何时用 + 架构 + 快速接入 + 契约 + 红线 + 运维
└── references/
    ├── issue-feedback-adoption-prompt.md      # ~220 行: 跨项目落地 prompt（核心交付物）
    ├── feedback-targets-schema.md             # ~130 行: 配置字段表 + 校验链 + CLI 十态 + 安全红线
    └── issue-form-template.md                 # ~100 行: Issue Form yml 模板 + 约束 + label 约定
```

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
## 复用差异点          — 其他项目接入需替换的 5 处
## references 索引
```

### 3.3 references 大纲

**① `issue-feedback-adoption-prompt.md`（核心交付物，跨项目可整体复制）**
- 适用判定（前置：静态 HTML 页 + 同源数据 JSON + 可重建的生成命令 + GitHub 仓库 + `gh` CLI 已认证）
- 6 步接入，每步含可复制片段 + 验证方法：
  1. 数据 JSON 加 `options.feedback.{repo,dataset,key,altKey,template}`
  2. 生成命令加 `--feedback-repo <owner/repo>`（及 `--github-url/--home-url/--favicon` 重建参数固化）
  3. 复制 Issue Form 模板并按案例改下拉选项
  4. 建 `data-fix` label + `config.yml`
  5. 写 `feedback-targets.yaml` target（字段表见 ②）
  6. 复制同步脚本并改 3 处（docstring / `HINT` / `argparse prog`）+ 默认配置路径
- 首次验收清单（`--check-template` → 页面按钮可见 → 造一条测试 issue → `--list` → `--dry-run` → `--apply --no-commit` → 视觉核对 → 回滚）

**② `feedback-targets-schema.md`**
- target 逐字段表（字段 / 类型 / 必填 / 语义 / 默认）
- 校验链顺序（page → dataset → 字段解析 → 主键硬保护 → editable 白名单 → 行唯一定位 → 类型 → 非空 → 入库 XSS 防护 → 幂等 → 冲突取最新）
- CLI 十态速查 + 退出码语义（0/1/2）
- 安全红线 5 条（显式 pathspec / 写盘前预检 / 失败不回滚 + exit 1 / 入库 `<`·`>` 拒绝 / `shell=False` 全链路）

**③ `issue-form-template.md`**
- Form yml 可复制模板（dropdown 字段 / textarea 值 / 只读说明段）
- 约束与机制原因：**下拉不可 URL 预填**（GitHub Issue Forms 限制）→ 页面不预填 field；主键/匹配键不进下拉（双层保护第一层）
- `config.yml` 关闭 blank issue 片段 + `data-fix` label 约定

### 3.4 内容红线
- **写**：可复制的命令/片段、字段契约、校验链、安全红线、验收方法、项目内指路
- **不写**：CL009/CL010 版本演进史（指向 `documents/solutions/`）、一次性 issue 处置记录（#1–#6）、本地绝对路径以外的环境私货
- **不复制脚本正文**（C1）：避免双份脚本漂移，改为「`cp scripts/countries-issue-sync.py` + 改 3 处」指引

## 4. 挂载改动面（精确清单）

### 4.1 代码
| 文件 | 位置 | 改动 |
|:---|:---|:---|
| `html-gen.py` | `SKILL_TO_GROUP`（L1046-1055） | 增 `'github-issue-feedback': ('table', '指令 CLI')` |
| `html-gen.py` | L793 / L911 / L1134 | 硬编码「28 文件」改「31 文件」 |
| `html-gen.py` | L1138 / L1207 / L1234 / L1263 | 注释「×8 / 8 个」改「×9 / 9 个」 |
| `html-gen.py` | L1264 / L1268-1269 | **无需改**：`n_total = len(skills)*3 + 4` 动态计算 |
| `html-gen.py` | L1296 | all.md 头部「项目 8 个 skills prompt」改「9 个」 |

### 4.2 测试
| 文件 | 位置 | 改动 |
|:---|:---|:---|
| `tests/test_prompt_site.py` | L5 docstring / L16-19 `EXPECTED_SKILLS` / L109「28 文件」/ L179「8 个 ## 段」/ L309「8 个 kb detail」 | 28→31、8→9、清单加项 |
| `tests/test_prompt_cmd.py` | L21-26 列表断言 | 可补 `github-issue-feedback` 断言（新增 1 用例或并入既有） |

### 4.3 文档
| 文件 | 位置 | 改动 |
|:---|:---|:---|
| `AGENTS.md` | L58 | **过期值修正**「18 文件」→「31 文件」（现存漂移，顺带修复） |
| `AGENTS.md` | 目录结构段（L327 附近） | skills 清单加 `github-issue-feedback/SKILL.md` |
| `features.md` | 能力表 | 补反馈通道 skill 沉淀条目（如无对应行则加在 skills/能力段） |
| `skills/html-gen/SKILL.md` | L63 / L69 / L314 | 28→31、×8→×9 |
| `skills/html-gen-cli-spec/SKILL.md` | L35 | 「站点 (28 文件)」→ 31 |
| `README.zh.md` | L84 | 「生成 `prompts/` 站点（28 文件）」→ 31 |
| `skills/github-issue-feedback/SKILL.md` | 新建 | 本闭环主产物 |

### 4.4 产物
`html-gen prompt --site` 重生成 `prompts/`：28 → **31 文件**（顶层 22 = index/all.md/_kb-*.json + 9 skill × md/json；`kb/` 9 detail）
- 新增：`prompts/github-issue-feedback.md` / `.json` / `kb/github-issue-feedback.html`
- 变更：`prompts/all.md`（多 1 段）、`prompts/index.html` + `_kb-data.json`（table 组多 1 条目）

## 5. 验收标准
1. `skills/github-issue-feedback/` 新建：SKILL.md + 3 references，单篇 ≤250 行（E1 约束）
2. `html-gen prompt`（列表）/ `html-gen prompt github-issue-feedback`（全文）/ `--brief` / `--json` 四态均正常
3. `html-gen prompt --site` 输出 **31 文件**，门户 table 组「指令 CLI」新增 1 条目，`kb/github-issue-feedback.html` 可访问
4. 测试同步：`tests/test_prompt_site.py` + `tests/test_prompt_cmd.py` 全绿
5. `prompts/` 重生成并提交（产物勿手改）
6. 文档面 6 处同步（含 `AGENTS.md:58` 过期值修正）
7. 全量 `python3 -m pytest tests/ -q -n 0` 零回归（基线 **311**）
8. 设计评审 PASS + 实现审计 PASS，review 通道 push `github`（ff-only，不推 gitee）

## 6. 风险与兼容

| 风险 | 影响 | 缓解 |
|:---|:---|:---|
| 计数硬编码遗漏 → 测试红/站点文案错 | 中 | §4 清单逐项核对 + 测试断言兜底（L109 断言统计行） |
| references 过长 → `html-gen prompt` 单次输出过大 | 中 | E1 单篇 ≤250 行预算；超长内容改指路设计文档 |
| skill 与 ops profile reference 双份漂移 | 中 | F1：本轮不写 ops；后续单独立动收敛为指针 |
| 门户 kb 条目缺 groups 映射 → 站点少项 | 低 | D1 显式注册 `SKILL_TO_GROUP`；测试 `EXPECTED_KB` 断言 |
| `prompts/` 重生成裹入无关 diff | 低 | 重生成后 `git status` 核对，仅提交 prompts/ 与 skill 相关文件 |

**兼容性**：纯增量（新增 skill + 注册 + 文案计数），无 API/参数/模板语义变更；既有 8 个 skill 的 prompt 输出与 kb 页不受影响（all.md/index.html 因新增条目而变更，属预期）。

## 7. 实施步骤（2/6 起）

```
[2/6] 设计评审（review role）—— 审本设计文档（决策完备性 / 改动面完整性 / 验收可执行性）
[3/6] dev 实现
      a. 编写 skills/github-issue-feedback/{SKILL.md, references ×3}（按 §3 大纲 + 行数预算）
      b. 挂载: html-gen.py SKILL_TO_GROUP + 3 处文案 28→31 + 4 处注释 ×8→×9 + all.md 头部
      c. 测试同步: test_prompt_site（4 处）+ test_prompt_cmd（列表断言）
      d. 文档同步: §4.3 六处（含 AGENTS.md:58 过期值）
      e. prompts/ 重生成 + 产物核对
[4/6] ops 核查 —— 四态 prompt 实测 + 31 文件清单核对 + 门户 kb 可达 + 全量 pytest
[5/6] 实现审计（review role）—— 逐条对照 §5 验收标准
[6/6] 复盘
```

## 8. 跨项目复用指引（本闭环交付目标）

其他项目接入路径（skill ② 详述）：
```
1) cp <html-gen.cli>/scripts/countries-issue-sync.py <project>/scripts/<case>-issue-sync.py
2) 改 3 处: docstring 示例 / HINT 常量 / argparse prog（替换脚本名）
3) cp <html-gen.cli>/scripts/feedback-targets.yaml → 写本项目 target（data/html/key_field/editable/rebuild.args）
4) cp .github/ISSUE_TEMPLATE/data-fix-countries.yml → 改下拉选项（列标签｜key）
5) 页面生成命令加 --feedback-repo（或数据 JSON options.feedback）
6) 造测试 issue → --check-template → --list → --dry-run → --apply --no-commit → 视觉核对
```
**复用前提（写进 skill 的适用判定）**：页面由 `html-gen table` 生成（✏️ 按钮依赖 layout-table）；数据为同源 JSON；有可脚本化的重建命令；仓库有 `gh` 权限。

**候选项目**（非本轮范围，供后续评估）：llm-radar 数据看板、www.jaden.tech 卡片页、http-server.cli 看板类页面。
