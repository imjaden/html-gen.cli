# html-gen Prompt 合集

> 在线阅读: html-gen 项目 9 个 skills prompt 全文（含 references）。
> 单篇获取: prompts/{skill}.md（纯 markdown）· prompts/{skill}.json（JSON 信封）· all.md（全量）。
> 重新生成: html-gen prompt --site（产物勿手改，由生成器产出）。


## github-issue-feedback

> Use when a static HTML data page needs a GitHub Issue feedback loop (reader submits data corrections → validated write-back to the data JSON → rebuild). Covers page-side ✏️ button, Issue Form, target config, sync script, security rules.

把「读者发现数据错误 → 提 Issue → 维护者一键写回数据 JSON → 重建静态页 → 回评」的闭环，
做成**配置驱动、可跨项目复制**的能力。已在 html-gen 的 countries 表案例落地（CL009 + CL010）。

## 何时使用

- 已有**静态 HTML 数据页**（由 `html-gen table` 生成）挂在 GitHub Pages，读者能看但不能改
- 数据源是**同源 JSON**，且页面有**可脚本化的重建命令**（一条命令能重新生成产物）
- 仓库有 GitHub 远端 + `gh` CLI 已认证，且你愿意让"数据纠错"走 Issue 流程而非直接提 PR
- 想要**白名单 + 类型校验 + 主键保护**的安全写回，而不是任人改数据文件

不适用：数据在数据库/API（应做后台表单）；页面非 html-gen 生成（无 ✏️ 按钮注入点）；
需要读者直接改文件（用 PR 流程更简单）。

## 能力总览

四件套，缺一不可：

| 层 | 产物 | 职责 |
|:---|:---|:---|
| 页面侧 | 分栏预览 header 的 `✏️` 按钮（layout-table） | 拼 GitHub Issue 新建 URL（预填 page/dataset/row/row_en/template，全量 URL 编码） |
| 表单侧 | `.github/ISSUE_TEMPLATE/data-fix-<case>.yml` | 结构化收集：字段（下拉 `标签｜key`）+ 建议值 + 来源 |
| 配置侧 | `scripts/feedback-targets.yaml` | 声明「哪些案例可被反馈、哪些字段可写、怎么重建」 |
| 脚本侧 | `<case>-issue-sync.py` | 拉 issue → 解析 → 校验链 → 写回 JSON → 重建 → 回评/关闭 → 本地提交 |

数据流：

```
读者点 ✏️ → GitHub Issue Form（预填上下文，人工填字段/值/来源）
   → gh issue list（按 label 拉取）
   → 校验链：page → dataset → 字段解析 → 主键硬保护 → editable 白名单
            → 非空 → 行唯一定位 → 类型 → 入库 XSS 防护 → 幂等 → 冲突取最新
   → 写回数据 JSON（indent=2，逐字往返）
   → 重建产物（html-gen table + 固化参数）
   → 回评（含本地短 sha）/ --close 关闭
   → 本地 git commit（显式 pathspec，只提交不推送）
```

**三个关键设计选择**（照抄即可，勿自行简化）：

1. **默认预览、显式落盘**：默认 `--dry-run` 零写盘；`--apply` 才写盘。一次 `--apply` 批量处理所有可执行 issue。
2. **提交只到本地**：`--apply` 自动 `git commit`（显式 pathspec），**不 push**——推送交由人工/review 通道。
3. **双层保护**：可写字段来自配置白名单，且主键/匹配键/受保护列在**代码层再拦一次**（配置误列也无效）。

## 快速接入（6 步 · 摘要）

```shell
# 1) 数据 JSON 顶层加案例自描述（或改用 CLI/env）
#    options.feedback = {repo, dataset, key, altKey, template}
# 2) 生成命令加 --feedback-repo（并把 corner/home/favicon 固化进重建参数）
html-gen table -d data/x.json -o demos/x.html --feedback-repo <owner/repo>
# 3) 复制 Issue Form 模板并按案例改下拉选项
cp .github/ISSUE_TEMPLATE/data-fix-countries.yml .github/ISSUE_TEMPLATE/data-fix-<case>.yml
# 4) 建 data-fix label + config.yml（关闭 blank issue）
# 5) 写 feedback-targets.yaml 的一个 target
# 6) 复制同步脚本并替换 docstring/HINT/prog 中的案例名
cp scripts/countries-issue-sync.py scripts/<case>-issue-sync.py
```

逐步骤的可复制片段 + 验证方法见 **`references/issue-feedback-adoption-prompt.md`**（可整体转交给其他项目的 agent）。

## CLI 契约

**页面侧（三级取值，CLI > env > JSON）**

| 入口 | 说明 |
|:---|:---|
| `html-gen table --feedback-repo <owner/repo>` | 仅 table 子命令；默认不注入（隐私） |
| env `HTML_GEN_FEEDBACK_REPO` | 兜底；显式传空串 `''` 禁用 env |
| 数据 JSON `options.feedback.{repo,dataset,key,altKey,template}` | 案例自描述；`repo` 为空 → 不渲染按钮 |

未配置 `repo` 时**不渲染 ✏️ 按钮**（既有页面零变更）。其余字段：`dataset`（表单数据集校验）、
`key`（行主键列，默认 `name`）、`altKey`（二次校验列，可空）、`template`（表单模板名，默认 `data-fix.yml`）。

**脚本侧（十态）**

```shell
python3 scripts/<case>-issue-sync.py --list          # 列待处理 issue（零写盘）
python3 scripts/<case>-issue-sync.py                 # 预览（默认 --dry-run，零写盘）
python3 scripts/<case>-issue-sync.py --apply         # 写回 + 重建 + 提交 + 回评
python3 scripts/<case>-issue-sync.py --apply --close # 追加关闭已处理 issue
python3 scripts/<case>-issue-sync.py --apply --no-commit   # 只写盘重建
python3 scripts/<case>-issue-sync.py --issue 12 --dry-run  # 只处理指定 issue
python3 scripts/<case>-issue-sync.py --issue 12 --field note --value-file body.txt --apply  # 人工裁决
python3 scripts/<case>-issue-sync.py --check-template      # 表单下拉 ↔ 配置一致性校验
python3 scripts/<case>-issue-sync.py --json                # 机器可读输出
python3 scripts/<case>-issue-sync.py --target <name> --config <path>  # 多 target / 自定义配置
```

退出码：`0` 正常；`1` 预检脏/预检失败/提交失败；`2` 参数错误或配置缺失。
字段级契约见 **`references/feedback-targets-schema.md`**。

## 安全红线（必读）

1. **白名单 + 硬保护双层**：可写字段必须在 `target.editable`；`key_field` / `alt_key` / `key_guard` / `protected`
   在代码层硬拦（配置误列也无效）。
2. **入库 XSS 防护**：string 字段建议值含 `<` 或 `>` → 拒绝（防止载荷经 Issue 入库后由页面 raw 渲染执行）。
3. **显式 pathspec**：`git add --` / `git commit -- <data> <html>`；**禁 `git add -A`**（并行会话 WIP 会被裹走）。
4. **写盘前预检**：目标文件有未提交改动 → 拒绝（`exit 1`），确保本次提交只含本次处置。
5. **失败不回滚**：提交失败时数据已写、产物已重建，脚本 exit 1 并在 issue 回评「提交失败，待维护者处理」。
6. **全链路 `shell=False`**：`gh` / `git` 调用一律列表参数，无字符串拼接。

## 运维

| 场景 | 做法 |
|:---|:---|
| 巡检待处理 | `--list`（每条附 `--issue N --dry-run` 引导行） |
| 同字段多条 issue | 冲突取最新（createdAt 大者，同则 issue 号大者），旧条目标注跳过原因 |
| 幂等 | 建议值与现值一致 → 跳过，不产生空提交 |
| 逃生口 | `--apply --no-commit`（只写盘重建，人工提交） |
| 人工裁决 | `--issue N --field KEY --value TEXT` / `--value-file PATH`（覆盖 issue 中的字段与值） |
| 表单漂移 | `--check-template` 校验下拉选项 ↔ `config.editable` ↔ 数据列标签一致 |
| 新案例 | 追加一份 target（无需改脚本），并在页面加 `options.feedback` |

## 本仓现状（html-gen.cli 参考实现）

| 项 | 位置 |
|:---|:---|
| 页面侧按钮 | `layout-table.html`（`FB_CFG` / `buildFeedbackUrl` / `renderSplitPreview` 的 `.sp-feedback`） |
| CLI 三级取值 | `html-gen.py`（`feedback_repo_args()` / table 子命令 `--feedback-repo`） |
| 表单模板 | `.github/ISSUE_TEMPLATE/data-fix-countries.yml`（84 行）+ `config.yml` |
| target 配置 | `scripts/feedback-targets.yaml`（countries） |
| 同步脚本 | `scripts/countries-issue-sync.py`（600 行） |
| 设计/评审 | `documents/solutions/countries-issue-feedback-design-v1.0..v1.4-*.md` + `documents/review/*issue-feedback*` |

## 复用差异点（其他项目接入时必改）

1. **脚本名与 docstring**：docstring 内案例名有 4 类形态（脚本名 ×9（L11-19 示例命令行）/ 表单模板名 / target 名 / 设计文档名）
2. **`HINT` 常量**（引导行打印用）与 **argparse `prog`**
3. **表单模板**：下拉选项 = 可写列的 `标签｜key`
4. **target 配置**：`data` / `html` / `key_field` / `editable` / `rebuild.args`
5. **重建参数**：`--github-url` / `--home-url` / `--favicon` / `--feedback-repo` 四项固化，防重建丢 corner/home

（`DEFAULT_CONFIG` 为通用路径，无需改；无 `DEFAULT_TARGET` 硬编码。）

## references 索引

| 文件 | 用途 |
|:---|:---|
| `references/issue-feedback-adoption-prompt.md` | 跨项目接入 prompt（6 步可复制片段 + 验收清单），可整体转交 |
| `references/feedback-targets-schema.md` | target 字段表 / 校验链顺序 / CLI 十态与退出码 / 安全红线 |
| `references/issue-form-template.md` | Issue Form yml 模板 + 机制约束（下拉不可 URL 预填等） |

---

## feedback-targets-schema

> 配置示例：`html-gen.cli/scripts/feedback-targets.yaml`（target `countries`）。
> 解析入口：`scripts/countries-issue-sync.py`（`load_target()` / `plan_issues()` / `guarded_fields()`）。
> 依赖：仅 PyYAML（**dev 依赖**；html-gen 运行时零依赖不受影响）。

## 1. target 字段表（19 项：16 具体字段 + 3 隐式机制）

| 字段 | 类型 | 必填 | 语义 | 缺省行为 |
|:---|:---|:---|:---|:---|
| `repo` | str | ✔ | `owner/repo`，`gh` 拉取与回评目标 | — |
| `label` | str | ✔ | 只处理带该 label 的 issue | — |
| `dataset` | str | ✔ | 数据集标识，须与 issue 表单「数据集」一致 | — |
| `template` | str | — | Issue Form 文件名（`--check-template` 校验用） | — |
| `page` | str | ✔ | 允许的页面（全路径或 basename 均可匹配） | — |
| `data` | str | ✔ | 数据 JSON 仓库相对路径（写回目标） | — |
| `html` | str | ✔ | 产物仓库相对路径（重建目标 + 提交范围） | — |
| `key_field` | str | ✔ | 行主键列（issue「行标识」→ 定位行） | — |
| `alt_key` | str | — | 匹配键列（issue「行英文标识」→ 二次校验） | 不校验 |
| `editable` | list | ✔ | **可写列白名单**（issue 字段解析依据） | 空 → 全部拒绝 |
| `protected` | list | — | 由其他脚本托管的列（拒绝写入） | 空 |
| `key_guard` | list | — | 硬保护列（主键/匹配键；配置误列也无效） | 取 `key_field`/`alt_key` |
| `commit.scope` | str | — | 提交消息 `data@<scope>: apply #N …` | 回退 `dataset` → `data` |
| `types` | map | — | 列 → `number`（数值解析 + 写 number） | 全按 string 写 |
| `parse_fields` | map | ✔ | issue body 段落标签 → 逻辑键（见 §3） | 解析失败即跳过 |
| `rebuild.args` | list | ✔ | 重建附加参数（corner/home/favicon/feedback 固化） | 空 → 产物丢参数 |
| `page`+`dataset` 组合 | — | ✔ | 双层定位：页面不匹配或数据集不匹配 → 跳过 | — |
| （隐式）`repo` 覆盖 | — | — | CLI `--repo` 可覆盖配置值 | — |
| （隐式）多 target | — | — | 单 target 自动选用；多 target 需 `--target` | — |

## 2. 校验链顺序（逐条短路，任一失败即跳过该 issue）

| # | 阶段 | 规则 | 失败输出 |
|:--|:---|:---|:---|
| 1 | 页面匹配 | issue「页面」∈ {`target.page`, basename} | `page 不匹配（…）` |
| 2 | 数据集匹配 | issue「数据集」== `target.dataset` | `dataset 不匹配（…）` |
| 3 | 字段解析 | 下拉 `标签｜key` 取末段 → 裸 key 回退 → 未知拒绝；`--field` 可覆盖 | `字段值无法识别（… 不在可写列中）` |
| 4 | 硬保护 | ∈ `guarded_fields()`（`key_guard` ∪ `key_field` ∪ `alt_key` ∪ `protected`） | `字段 X 属受保护列…` |
| 5 | 白名单 | ∈ `target.editable` | `字段 X 不在可写白名单` |
| 6 | 建议值非空 | strip 后非空 | `建议值为空` |
| 7 | 行定位 | 主键列 + 匹配键列唯一定位；0 命中/多命中均拒绝 | `row=… 命中 N 行（歧义）` / 未命中 |
| 8 | 类型 | `types[field] == number` → `to_number()`（容忍 `1,234`）；解析失败拒绝 | `数值列 X 无法解析建议值` |
| 9 | 入库 XSS 防护 | string 字段含 `<` 或 `>` → 拒绝 | `建议值含 HTML 标签字符（< 或 >），安全策略拒绝` |
| 10 | 幂等 | 建议值 == 现值（`norm()` 归一化后） | `建议值与现值一致，无变化` |
| 11 | 冲突 | 同一 (行, 字段) 多条 → 取最新（`createdAt` 大者，同则 issue 号大者），其余标注跳过 | `X 与 #N 冲突，取最新` |

**行定位细节**：主键列命中唯一即通过；主键 0 命中（或未填）时用 `alt_key` 再试；
两者都歧义/都未命中 → 跳过。`key_guard` 保证主键**永不被写**。

## 3. `parse_fields` 映射

issue body 被解析为「`### 标签` → 值」字典（首段需以 `### ` 开头；同 id 多段自动合并）。
`parse_fields` 把表单 `id` 映射到 body 段落标签：

```yaml
parse_fields:
  page: 页面            # ↦ 表单 input id=page
  dataset: 数据集
  row: 行标识
  row_en: 行英文标识
  field: 字段            # ↦ dropdown id=field（值形如 标签｜key）
  current: 当前值        # 兼容 shim：旧版表单字段，仅解析不参与定位
  suggested: 建议值      # ↦ textarea id=suggested
  source: 来源
  note: 补充说明
```

新增表单字段时：在 `parse_fields` 加一行映射，并在 `plan_issues()` 消费（否则解析后无人使用）。

## 4. CLI 十态与退出码

| 命令 | 行为 | 写盘 | 提交 | 回评 |
|:---|:---|:---|:---|:---|
| `--list` | 列待处理 issue + 逐条引导行 | 否 | 否 | 否 |
| （默认）`--dry-run` | 预览将写入的 diff | 否 | 否 | 否 |
| `--apply` | 写回 + 重建 + 提交 + 回评 | ✔ | ✔ | ✔ |
| `--apply --close` | 同上 + 关闭 issue | ✔ | ✔ | ✔ + close |
| `--apply --no-commit` | 只写回 + 重建（跳预检） | ✔ | 否 | ✔ |
| `--issue N` | 只处理指定 issue | 依 mode | 依 mode | 依 mode |
| `--issue N --field KEY --value[-file]` | 人工裁决：覆盖字段与值 | 依 mode | 依 mode | 依 mode |
| `--check-template` | 表单下拉 ↔ 配置/数据列一致性 | 否 | 否 | 否 |
| `--json` | 机器可读 `{status,data,error}` | 依 mode | 依 mode | 依 mode |
| `--target/--config/--limit/--repo` | 目标选择与拉取范围 | — | — | — |

| 退出码 | 含义 |
|:---|:---|
| `0` | 正常（含「无可执行 issue」「幂等跳过」） |
| `1` | 写盘前预检脏、预检失败、提交失败（数据已写，不回滚） |
| `2` | 参数错误（`--field` 无 `--issue`）、配置缺失/无 targets |

## 5. 安全红线（逐条对应实现）

| # | 红线 | 实现 |
|:--|:---|:---|
| 1 | 白名单 + 硬保护双层 | `guarded_fields()` 先于 `editable` 检查；主键/匹配键/托管列在代码层拦截 |
| 2 | 入库 XSS 防护 | string 分支拒绝含 `<` / `>` 的建议值（防载荷经页面 raw 渲染执行） |
| 3 | 显式 pathspec | `git add --` / `git commit -- <data> <html>`；全脚本无 `git add -A` |
| 4 | 写盘前预检 | `git status --porcelain -- <data> <html>` 非空 → `exit 1`（在写盘之前） |
| 5 | 失败不回滚 | 提交失败时数据/产物保留，回评「提交失败，待维护者处理」，`exit 1` |
| 6 | `shell=False` 全链路 | `gh` / `git` 调用统一列表参数 + `subprocess.run(..., shell=False)` |

## 6. 回评与提交格式

- **回评**：`--apply` 成功后在该 issue 留言，含处置摘要 + 本地短 sha（`（待推送）`）；`--close` 追加关闭。
- **提交消息**：标题 `data@<scope>: apply #N <字段> 更新`；多 issue → `#N,#M`；body 逐条列 `- #N <行标签>.<字段>: 旧 → 新` + 产物路径。
- **提交范围**：仅 `target.data` + `target.html`（显式 pathspec）；无变化不产生空提交。

---

## issue-feedback-adoption-prompt

> 用法：把本文整体交给目标项目的 agent（或人），按步骤执行即可接入。
> 参考实现：`html-gen.cli` 的 countries 案例（`scripts/countries-issue-sync.py` + `scripts/feedback-targets.yaml`）。
> 前置知识：`github-issue-feedback` SKILL.md（能力总览/安全红线）。

## 0. 适用判定（不满足则不要接入）

| 前置 | 判定方法 |
|:---|:---|
| 页面由 `html-gen table` 生成 | 产物含 `data-table` 结构；能重新跑生成命令 |
| 数据源是同源 JSON | `data/<case>-data.json`（结构化格式：columns/data/options） |
| 有可脚本化的重建命令 | 一条命令重新生成产物（含 corner/home/favicon 参数固化） |
| 仓库在 GitHub + `gh` 已认证 | `gh auth status` 通过；`gh repo view <owner/repo>` 可用 |
| 有可挂 `label` 的权限 | 建 `data-fix` label（一次性） |

## 1. 交付物清单

| # | 文件 | 动作 |
|:---|:---|:---|
| 1 | `data/<case>-data.json` | 改：顶层加 `options.feedback` |
| 2 | 生成/重建命令 | 改：加 `--feedback-repo`（并固化 corner/home/favicon） |
| 3 | `.github/ISSUE_TEMPLATE/data-fix-<case>.yml` | 新增：表单模板（下拉选项 = 可写列） |
| 4 | `.github/ISSUE_TEMPLATE/config.yml` | 新增/改：关闭 blank issue |
| 5 | `scripts/feedback-targets.yaml` | 新增 target（多案例共用一份配置） |
| 6 | `scripts/<case>-issue-sync.py` | 复制 + 替换案例名（4 类形态 + HINT + prog） |
| 7 | GitHub label `data-fix` | 一次性创建 |

## 2. Step 1 — 数据 JSON 声明案例（页面侧开关）

在数据 JSON 顶层加：

```json
"options": {
  "feedback": {
    "repo": "owner/repo",
    "dataset": "countries",
    "key": "country_zh",
    "altKey": "country_en",
    "template": "data-fix-countries.yml"
  }
}
```

| 字段 | 必填 | 说明 |
|:---|:---|:---|
| `repo` | ✔ | `owner/repo`；空串或缺失 → **不渲染 ✏️ 按钮** |
| `dataset` | ✔ | 与 target `dataset` 一致，脚本据此拒绝跨数据集 issue |
| `key` | ✔ | 行主键列（预填 `row`，脚本用它唯一定位行） |
| `altKey` | — | 二次校验列（预填 `row_en`） |
| `template` | — | Issue Form 文件名；缺省 `data-fix.yml` |

**替代入口**（不改数据文件时）：`html-gen table --feedback-repo owner/repo`，或 env `HTML_GEN_FEEDBACK_REPO`。
优先级 **CLI > env > JSON**；显式空串禁用 env 兜底。

**验证**：重建产物 → 打开页面 → 点任意行打开分栏预览 → header 出现 ✏️ → 点击跳 GitHub 新建 issue，
URL 带 `template/page/dataset/row/row_en/title`（**不含** `field`：下拉不可 URL 预填）。

## 3. Step 2 — 生成命令与重建参数固化

```shell
python3 html-gen.py table -d data/<case>-data.json -o demos/<case>.html \
  --github-url https://github.com/<owner>/<repo> \
  --home-url https://<site-root>/ \
  --favicon https://<favicon-url> \
  --feedback-repo <owner>/<repo>
```

**为什么必须固化**：`--apply` 写回后会调生成命令重建产物；若重建命令漏参数，corner/home/feedback
会静默丢失（CL002 FIND-002 同类缺陷，实测复发过一次）。故把这四项写进
`feedback-targets.yaml` 的 `target.rebuild.args`，让脚本每次重建都带上。

## 4. Step 3 — Issue Form 模板

```shell
cp .github/ISSUE_TEMPLATE/data-fix-countries.yml .github/ISSUE_TEMPLATE/data-fix-<case>.yml
```

改三处：`title` 前缀、`page` 的 `placeholder`、`field` 下拉的选项列表。

下拉选项格式 **`标签｜key`**（全角竖线），每项对应一个可写列：

```yaml
  - type: dropdown
    id: field
    attributes:
      label: 字段
      multiple: false
      options:
        - 首都｜capital_zh
        - 备注｜note
```

**规则**：选项**不含**主键/匹配键（双层保护第一层）；不含由其他脚本托管的列（如 videos）。
细节与完整模板见 `references/issue-form-template.md`。

## 5. Step 4 — label 与 config.yml

```shell
gh label create data-fix --repo <owner>/<repo> --color FBCA04 \
  --description "案例数据纠错反馈（由页面 ✏️ 按钮发起）"
```

`.github/ISSUE_TEMPLATE/config.yml`（关闭 blank issue，引导走表单）：

```yaml
blank_issues_enabled: false
contact_links:
  - name: 数据纠错反馈
    url: https://github.com/<owner>/<repo>/issues/new?template=data-fix-<case>.yml
    about: 请通过表单提交数据纠错（页面上的 ✏️ 按钮会自动填写上下文）
```

## 6. Step 5 — target 配置

在 `scripts/feedback-targets.yaml` 的 `targets:` 下追加：

```yaml
  <case>:
    repo: <owner>/<repo>
    label: data-fix
    dataset: <case>                       # 与数据 JSON options.feedback.dataset 一致
    template: data-fix-<case>.yml
    page: demos/<case>.html               # 全路径或 basename 均可匹配
    data: data/<case>-data.json
    html: demos/<case>.html
    key_field: <key>                      # 主键列
    alt_key: <altKey>                     # 可空
    editable: [<key1>, <key2>, ...]       # 可写列白名单（不含主键/匹配键/托管列）
    protected: [videos]                   # 由其他脚本托管的列
    key_guard: [<key>, <altKey>]          # 硬保护（配置误列也无效）
    commit:
      scope: <case>                       # 提交消息 data@<scope>: apply #N …
    types:                                # 数值列（可解析校验 + 写入 number）
      area_km2: number
    parse_fields:                         # 表单 id → issue body 段落标签
      page: 页面
      dataset: 数据集
      row: 行标识
      row_en: 行英文标识
      field: 字段
      suggested: 建议值
      source: 来源
      note: 补充说明
    rebuild:
      args: [--github-url, https://github.com/<owner>/<repo>,
             --home-url, https://<site-root>/,
             --favicon, https://<favicon-url>,
             --feedback-repo, <owner>/<repo>]
```

字段级语义与校验链见 `references/feedback-targets-schema.md`。

## 7. Step 6 — 复制同步脚本并替换案例名

```shell
cp <html-gen.cli>/scripts/countries-issue-sync.py scripts/<case>-issue-sync.py
```

**替换清单（漏改会导致校验/引导失效）**：

| # | 位置 | 形态 | 不改的后果 |
|:---|:---|:---|:---|
| 1 | docstring 示例命令行 | `countries-issue-sync.py`（9 处，L11-19） | 文档误导 |
| 2 | docstring | 表单模板名 `data-fix-countries.yml` | `--check-template` 指错文件 |
| 3 | docstring | `--target countries` 示例 | 引导命令不可用 |
| 4 | docstring | 设计文档名引用 | 失效链接 |
| 5 | `HINT` 常量 | `python3 scripts/countries-issue-sync.py` | `--list` 引导行打印错命令 |
| 6 | argparse `prog=` | `countries-issue-sync.py` | `--help` 显示错名字 |

不改：`DEFAULT_CONFIG`（通用路径 `scripts/feedback-targets.yaml`）；脚本内**无** `DEFAULT_TARGET` 硬编码
（单 target 自动选用，多 target 需 `--target`）。

## 8. 首次验收清单（逐条可复跑）

```shell
# 1) 模板 ↔ 配置 ↔ 数据列 一致性
python3 scripts/<case>-issue-sync.py --check-template        # 期望：一致（N 项），exit 0
# 2) 页面按钮可见
python3 html-gen.py table -d data/<case>-data.json -o demos/<case>.html --feedback-repo <owner>/<repo>
#    浏览器打开 → 点行 → 分栏 header 有 ✏️ → 点击 URL 含 template/page/dataset/row
# 3) 造一条测试 issue（真实提交，稍后关闭）
python3 scripts/<case>-issue-sync.py --list                  # 期望：列出该 issue
python3 scripts/<case>-issue-sync.py                         # 期望：预览 diff，零写盘
python3 scripts/<case>-issue-sync.py --apply --no-commit     # 期望：写回 JSON + 重建 + 回评（不提交）
git diff -- data/<case>-data.json demos/<case>.html          # 期望：仅目标字段变化 + 产物重建
git checkout -- data/<case>-data.json demos/<case>.html      # 回滚测试改动
# 4) 全链路（确认无误后）
python3 scripts/<case>-issue-sync.py --apply --close         # 期望：写盘 + 重建 + 本地 commit + 回评 + 关闭
git log -1 --name-only                                       # 期望：仅 data 与 html 两个文件
```

## 9. 常见坑

| 坑 | 症状 | 处置 |
|:---|:---|:---|
| 下拉无法预填 | URL 带了 `field=` 但表单不生效 | GitHub Issue Forms 机制限制 → 页面不预填 field，由读者选择 |
| 字段值写成裸 key | `--check-template` 报不一致 | 下拉选项用 `标签｜key`（全角竖线），脚本取末段 |
| 主键被写 | 脚本直接跳过并给出原因 | `key_guard` 硬保护；确认没有把主键放进 `editable` |
| 重建丢 corner/home | 产物差异出现 corner 消失 | `rebuild.args` 固化四项参数 |
| 提交裹走无关文件 | `git show --name-only` 出现其他文件 | 脚本已用显式 pathspec；勿改成 `git add -A` |
| 数值列写入字符串 | 排序/格式化异常 | `types.<key>: number`，脚本用 `to_number()` 解析后写 number |
| 载荷入库后执行 | 页面弹窗/单元格执行脚本 | 入库 `<`/`>` 拒绝（脚本侧）+ 模板侧默认转义，两层都要 |

---

## issue-form-template

> 参考实现：`html-gen.cli/.github/ISSUE_TEMPLATE/data-fix-countries.yml`（84 行，可直接复制）
> 同目录 `config.yml` 关闭 blank issue（**参考实现当前仅 1 行 `blank_issues_enabled: false`**；
> §3 的 `contact_links` 为**增强可选项**，接入方可按需启用）。

## 1. 完整模板（复制后改 3 处）

```yaml
name: 数据反馈
description: 报告案例表格中的数据错误或过时信息（页面上的「✏️」按钮会自动填写上下文）
title: "[数据反馈] "
labels: ["data-fix"]
body:
  - type: markdown
    attributes:
      value: |
        感谢反馈！**标注「请勿修改」的字段由页面自动填充**，如被改动会导致本条被同步脚本跳过。
        请在「字段」下拉中选择要修改的列，并在「建议值」中填写新内容。
  - type: input
    id: page
    attributes:
      label: 页面
      description: 请勿修改（由页面自动填充）
      placeholder: demos/<case>.html        # ← 改 1/3
    validations:
      required: true
  - type: input
    id: dataset
    attributes:
      label: 数据集
      description: 请勿修改（由页面自动填充）
    validations:
      required: true
  - type: input
    id: row
    attributes:
      label: 行标识
      description: 请勿修改（主键，仅用于定位；脚本不会修改它）
    validations:
      required: true
  - type: input
    id: row_en
    attributes:
      label: 行英文标识
      description: 请勿修改（可选，用于二次校验）
    validations:
      required: false
  - type: dropdown
    id: field
    attributes:
      label: 字段
      description: 选择要修改的列（行标识/英文名/视频列不可修改）
      multiple: false
      options:                              # ← 改 2/3：标签｜key，与 editable 一一对应
        - <列标签>｜<key>
    validations:
      required: true
  - type: textarea
    id: suggested
    attributes:
      label: 建议值
      description: 该字段修正后的值（数值列请只填数字；长文本可直接粘贴，换行会原样保留）
    validations:
      required: true
  - type: input
    id: source
    attributes:
      label: 来源
      description: 权威出处链接或说明（用于核对）
    validations:
      required: true
  - type: textarea
    id: note
    attributes:
      label: 补充说明
      description: 可选，其他需要说明的信息
    validations:
      required: false
```

> 示例下拉（countries 案例，15 项）：
> `- 首都｜capital_zh` / `- 备注｜note` / `- 人口(万)｜pop_wan` …（**不含** `country_zh` / `country_en` / `videos`）

## 2. 机制约束（为什么这样设计）

| 约束 | 原因 |
|:---|:---|
| **`field` 用 dropdown 而非 input** | input 可被 URL 预填，会导致「点主键列 → 预填主键 → 主键被写」的真实事故（CL009 issue #2 驱动改版） |
| **dropdown 不可 URL 预填** | GitHub Issue Forms 机制限制：只有 input/textarea 支持 `?<id>=` 预填 → 页面**不预填** `field`，由读者选择 |
| **选项格式 `标签｜key`** | 人看标签、脚本取 key；全角竖线 `｜` 分隔（`v.split('｜')[-1]`） |
| **不含主键/匹配键** | 双层保护第一层；第二层在脚本 `guarded_fields()` 硬拦（配置误列也无效） |
| **不含托管列（videos）** | 该列由独立脚本（如 `tool-table-videos-syncer.py`）维护，issue 写入会与之冲突 |
| **`suggested` 用 textarea** | 多行长文本（备注/民族/信仰）需原样保留换行；`input` 会丢换行 |
| **上下文四字段标「请勿修改」** | `page`/`dataset` 进校验链、`row`/`row_en` 进行定位；被改动 → issue 被跳过（回评会给出原因） |

## 3. `config.yml`（关闭 blank issue）

```yaml
blank_issues_enabled: false
contact_links:
  - name: 数据纠错反馈
    url: https://github.com/<owner>/<repo>/issues/new?template=data-fix-<case>.yml
    about: 请通过表单提交数据纠错（页面上的 ✏️ 按钮会自动填写上下文）
```

## 4. label 约定

```shell
gh label create data-fix --repo <owner>/<repo> \
  --color FBCA04 --description "案例数据纠错反馈（由页面 ✏️ 按钮发起）"
```

- 表单 `labels: ["data-fix"]` 与 target `label: data-fix` **必须一致**（脚本按 label 拉取）
- 建议单 label 供多案例共用；若需分流可加 `<case>` label 并在 target 里改

## 5. 一致性校验

```shell
python3 scripts/<case>-issue-sync.py --check-template
```

校验三项：表单 dropdown 选项 ↔ `config.editable` ↔ 数据 JSON 列标签。
期望输出「一致（N 项）」，exit 0；不一致会逐项列出差异。**改完表单/配置/数据列后必跑。**

## 6. 页面侧预填参数（对应本文表单的 `id`）

| 页面参数 | 表单 id | 说明 |
|:---|:---|:---|
| `template` | — | 表单文件名（URL 参数 `?template=`） |
| `title` | — | `[数据反馈] <dataset> · <row>` |
| `page` | `page` | 当前页面路径（`location.pathname` 去前导 `/`） |
| `dataset` | `dataset` | `options.feedback.dataset` |
| `row` | `row` | `row[options.feedback.key]` |
| `row_en` | `row_en` | `row[options.feedback.altKey]`（可空） |

全部经 `encodeURIComponent` 拼接，无注入面；`field` / `current` 已不再预填（v1.3 起）。

## html-gen

> Use when asked to generate HTML from markdown or JSON using html-gen, create data table pages, knowledge bases, slide presentations, or document pages. Use when user references html-gen CLI or wants markdown converted to styled HTML.

## 概述

`html-gen` 是一个零依赖 Python CLI 工具，将 Markdown/JSON 数据注入 HTML 模板，输出自包含单文件 HTML。深色主题，4 种模板类型。

## 四型总览

| 类型 | 模板文件 | 命令 | 输入 | 输出场景 |
|:---|:---|:---|:---|:---|
| A 型 · 数据表格 | `layout-table.html` | `table` | JSON 数据 | 文件索引、项目列表、数据浏览 |
| B 型 · 文档阅读 | `layout-doc.html` | `doc` | Markdown | 分析报告、技术文档、长文阅读 |
| C 型 · 知识库 | `layout-knowledge.html` | `knowledge` | JSON 条目+类目 | 知识库、面试准备、项目 Wiki |
| D 型 · 幻灯片 | `layout-slide.html` | `slide` | Markdown | 课件演示、会议分享、分段阅读 |

> A 型表格的详细列配置、操作按钮、Tab 过滤等高级功能参见 `html-gen-table` skill。

## CLI 命令

```shell
# B 型 — Markdown → 文档
html-gen doc -i report.md -o report.html

> 默认隐藏侧边栏/工具栏（Bare 模式）；独立完整浏览加 `?sidebar=1&toolbar=1` [--title "标题"] [--subtitle "副标题"]（自动剥离 YAML frontmatter）

# D 型 — Markdown → 幻灯片
html-gen slide -i slides.md -o slides.html [--title "标题"] [--subtitle "副标题"]

# A 型 — JSON → 数据表格
html-gen table -d data.json [--title "标题"] [-o index.html]

# C 型 — JSON → 知识库
html-gen knowledge -d data.json [-g groups.json] [--title "标题"] [--welcome "欢迎语"] [-o kb.html]
```

输出均为自包含单文件 HTML（CSS 内联，零外部依赖）。

四渲染子命令通用参数：`--github-url <url>`（右上角 GitHub corner，默认不带）、`--home-url <url>`（demo 首页入口）、`--favicon <url>`（favicon 图标，默认注入 `DEFAULT_FAVICON`，显式空串禁用）、`--quiet`（仅打印路径）；环境变量兜底 `HTML_GEN_GITHUB_URL` / `HTML_GEN_HOME_URL` / `HTML_GEN_FAVICON`（CLI 参数优先）。

**table 专属**：`--feedback-repo <owner/repo>`（GitHub Issue 反馈通道开关；默认不注入，显式空串禁用，env `HTML_GEN_FEEDBACK_REPO`，CLI > env > JSON `options.feedback.repo`）。启用后分栏预览 header 出 ✏️ 按钮 → 跳转 GitHub Issue Form（v1.3 起字段为**下拉选择**，主键/匹配键/视频列不可选）；表单模板名由 `options.feedback.template` 指定。脚本 `python3 scripts/countries-issue-sync.py`（`scripts/feedback-targets.yaml`）校验写回：`--list`（每条附 `--issue N --dry-run` 引导）/ `--dry-run` / `--apply`（默认自动 `git commit`，显式 pathspec 仅数据+产物，`--no-commit` 关闭，只提交不推送；回评带本地短 sha）；`--issue N --field KEY --value TEXT|--value-file PATH`（人工裁决）；`--check-template`（模板 ↔ config 一致性校验）。设计: documents/solutions/countries-issue-feedback-design-v1.4-20260911.md。

## prompt — 项目 skills 输出

skills/ 每子目录一个 skill（含 SKILL.md），可拼接 references/*.md：

```shell
html-gen prompt                    # 列出全部 skill (名称 + 摘要)
html-gen prompt <skill>            # 输出该 skill 摘要 + 章节
html-gen prompt <skill> --brief    # 仅摘要
html-gen prompt <skill> --json     # JSON 信封 {status,data,error}
html-gen prompt --site             # 生成 prompts/ 在线阅读站点 (31 文件)
html-gen prompt --site --dir <path> # 站点输出目录覆盖 (默认 仓库根/prompts/)
```

`--site` 产物（勿手改，由生成器产出；一律剥离 YAML frontmatter）：
- `prompts/index.html` — C 型 knowledge 门户（5 tab：A 表格 / B 文档 / C 知识库 / D 幻灯片 / 通用 CLI；纵向 = 指令 CLI / 模板语法 / 使用案例；guide/case 以 iframe 加载 demos/ 页）
- `prompts/kb/{skill}.html` ×9 — 每 skill 的 doc detail 页
- `prompts/{skill}.md` / `.json` ×18 + `prompts/all.md` — curl 契约文件
- `prompts/_kb-groups.json` / `_kb-data.json` — 门户运行时数据（Jekyll `_` 前缀不发布，已内联 index.html）

curl 契约 URL（GitHub Pages 域）：
```shell
curl -s https://html-gen.cli.jaden.tech/prompts/              # 门户
curl -s https://html-gen.cli.jaden.tech/prompts/kb/html-gen.html
curl -s https://html-gen.cli.jaden.tech/prompts/html-gen.md    # 单 skill 纯 md
curl -s https://html-gen.cli.jaden.tech/prompts/html-gen.json  # JSON 信封
curl -s https://html-gen.cli.jaden.tech/prompts/all.md         # 全量合集
```

`--site` 与 `skill` / `--brief` / `--json` 互斥。

## 支持的 Markdown 语法

`md_to_html()` 内置渲染器支持以下语法子集。**AI 生成 Markdown 时必须遵守此规范**：

### 块级元素

| 语法 | 写法 | 说明 |
|:---|:---|:---|
| h1 标题 | `# 标题` | 全文档唯一 |
| h2 标题 | `## 标题` | 自动加入 TOC、slide 分页边界 |
| h3 标题 | `### 标题` | 自动加入 TOC |
| 无序列表 | `- 列表项` | 连续自动合并为 `<ul>` |
| 有序列表 | `1. 列表项` | 连续自动合并为 `<ol>` |
| 表格 | `\| A \| B \|` + `\|:---\|:---\|` | 第二行为对齐分隔行 |
| 围栏代码块 | ` ```lang ` … ` ``` ` | 支持变长 fence 嵌套 |
| 引用 | `> 文字` | 单行模式 |
| 分隔线 | `---` | 连续 3+ 短横 |
| Callout 提示框 | `> **Note:** 内容` | 支持 Note/Tip/Warning/Danger/Caution + 中文对应词 |

### 行内元素

| 语法 | 写法 | 说明 |
|:---|:---|:---|
| 加粗 | `**文字**` | 全局有效，表格内也支持 |
| 斜体 | `*文字*` | `**` 优先匹配 |
| 行内代码 | `` `code` `` | 在 `<pre><code>` 内无效 |
| 链接 | `[文字](url)` | 自动 `target="_blank"` |
| 图片 | `不解析` | 用纯 HTML `<img>` 代替 |

### 不支持

- 缩进子列表（平铺即可）
- 图片 Markdown 语法 `![alt](url)`
- HTML 标签（会被转义）
- Emoji 短码 `:smile:`（直接用 Unicode Emoji）

### Callout 关键词对照

```
> **Note:** ...     > **注意**：...
> **Tip:** ...      > **提示**：...
> **Warning:** ...  > **警告**：...
> **Danger:** ...   > **危险**：...
> **Caution:** ...  > **注意**：...
```

## B 型 · 文档阅读 (doc)

**输入**: Markdown 文件  
**输出**: 侧边栏 TOC + 内容区 HTML 文档

自动功能：
- 从 h2/h3 生成侧边栏目录，点击平滑滚动
- 滚动时自动高亮当前章节
- 代码块悬停复制按钮 + CSS 行号
- h2/h3 悬浮 ¶ 锚点链接，点击复制 `#id`
- 顶部阅读进度条
- 图片点击灯箱放大
- 外链自动归档到文档底部
- 文件元信息（路径/创建时间/字数/阅读时长）

**用法**:
```shell
html-gen doc -i report.md -o report.html

> 默认隐藏侧边栏/工具栏（Bare 模式）；独立完整浏览加 `?sidebar=1&toolbar=1` --title "标题" --subtitle "副标题"
```

## D 型 · 幻灯片 (slide)

**输入**: Markdown 文件（每个 `##` 为一页）  
**输出**: h2 分页幻灯片 + 底部圆点导航

自动功能：
- 封面页（h1 标题 + 副标题 + 元信息 + 节数统计）
- h2 自动分页，每个二级标题独立一页
- 键盘翻页：← → Space Home End
- 底部圆点导航（已读/当前/未读三色）
- 右上角页码 n/N（3s 渐隐）
- F 键全屏演示
- localStorage 进度保存
- 侧边栏 TOC（h3 默认隐藏，可通过 H3 开关显示）
- >50 h2 时显示性能警告

**用法**:
```shell
html-gen slide -i slides.md -o slides.html --title "标题" --subtitle "副标题"
```

## A 型 · 数据表格 (table)

**输入**: JSON 数据（简单数组 或 结构化对象）  
**输出**: 可搜索/排序/分页的交互表格

### 简单格式

```json
[{"名称": "项目A", "数量": 10}, {"名称": "项目B", "数量": 20}]
```

列名自动从首条 key 推导。

### 结构化格式

```json
{
  "columns": [
    {"key": "name", "label": "名称", "sortable": true, "locale": "zh"},
    {"key": "stars", "label": "Stars", "type": "number"},
    {"key": "actions", "label": "操作", "type": "actions", "actions": [
      {"icon": "📋", "label": "复制", "copyKey": "name"},
      {"icon": "🔗", "label": "打开", "hrefKey": "url"},
      {"icon": "👁️", "label": "详情", "desc": "查看详细信息"}
    ]}
  ],
  "data": [
    {"name": "project-a", "stars": 120, "url": "https://github.com/..."}
  ],
  "tabs": [
    {"key": "all", "label": "全部"},
    {"key": "Python", "label": "🐍 Python", "field": "lang"}
  ],
  "options": {"pageSize": 30, "exportCSV": true, "rowSelect": true}
}
```

列类型: `string`(默认) / `number` / `actions`。详见 `html-gen-table` skill。

## C 型 · 知识库 (knowledge)

**输入**: JSON 条目 + 可选类目分组  
**输出**: 顶部标签栏 + 左侧章节 + 右侧内容区

### 数据格式

```json
[
  {
    "title": "条目名称",
    "group": "所属类目",
    "section": "子分类",
    "badge": "标记",
    "desc": "<p>HTML 内容（内联渲染）</p>",
    "url": "detail.html"
  }
]
```

- `title`(必填): 条目名称
- `group`(必填): 所属类目，对应顶部 Tab
- `section`(可选): 子分类，侧栏分组
- `badge`(可选): 标记文本
- `desc`: 内联 HTML 内容（与 url 二选一）
- `url`: 外部 HTML 路径（iframe 加载，与 desc 二选一）

### 类目分组（可选）

```json
[
  {"key": "Agent 框架", "label": "🤖 Agent 框架", "icon": "🤖"},
  {"key": "HTML 工具", "label": "🌐 HTML 工具", "icon": "🌐"}
]
```

不提供 groups 时，从条目的 `group` 字段自动推导。

### 用法

```shell
# 自动推导类目
html-gen knowledge -d data.json --title "知识库" -o kb.html

# 指定类目
html-gen knowledge -d data.json -g groups.json --title "知识库" --welcome "从上方类目选择" -o kb.html
```

## AI 工作流程

当用户要求生成 HTML 页面时：

1. **确定类型**: 根据用户需求选择 A/B/C/D 型
2. **准备数据**: 
   - B/D 型: 按规范编写 Markdown 文件
   - A/C 型: 按 schema 编写 JSON 数据文件
3. **生成**: 执行对应 CLI 命令
4. **交付**: 输出 `.html` 文件路径

### 典型场景

**场景 1: 将笔记转为文档**
```shell
html-gen doc -i notes.md -o notes.html --title "学习笔记"
```

**场景 2: 生成课件幻灯片**
```shell
html-gen slide -i lecture.md -o lecture.html --title "第3讲" --subtitle "课件"
```

**场景 3: 生成项目索引页**
```json
// data.json
[{"name": "repo-a", "stars": 120, "lang": "Python"}]
```
```shell
html-gen table -d data.json --title "项目列表" -o index.html
```

## 常见问题

### Q: Markdown 中的 `<script>` 会被执行吗？
不会。`_md_escape()` 转义 `&` `<` `>`，安全。

### Q: 生成的 HTML 为什么没有图片？
Markdown 图片语法 `![alt](url)` 不解析。用 `<img src="...">` 代替。

### Q: 列表缩进子项没渲染？
不支持缩进子列表，改为平铺写法。

## 验证清单

- [ ] Markdown 语法符合上述规范（无缩进子列表、无 `![img]`）
- [ ] JSON 数据格式正确（A/C 型）
- [ ] CLI 命令执行成功，输出 `✅ 已生成: xxx.html`
- [ ] 生成的 HTML 在浏览器中正常渲染
- [ ] 链接、表格、代码块显示正确


## 变更记录
- v2.7.0 (2026-09-12): prompt --site 28→31 文件（新增 github-issue-feedback skill 挂载: 跨项目 Issue 数据反馈闭环规范）
- v2.6.0 (2026-09-10): table 专属 `--feedback-repo`（GitHub Issue 反馈通道 + scripts/countries-issue-sync.py 数据反馈闭环）
- v2.5.0 (2026-09-02): prompt 子命令段补 `--site`（prompts/ 在线阅读站点 28 文件: C 型 knowledge 门户 5 tab + kb/{skill}.html detail + curl 契约）
- v2.4.0 (2026-08-29): 新增 favicon 默认注入（--favicon 覆盖/空串禁用）+ --github-url/--home-url/--quiet 通用参数说明
- v2.3.0 (2026-08-06): 新增 frontmatter 自动剥离; 修复 doc/slide 侧边栏 sticky 失效
- v2.2.0 (2026-08-06): 新增 quickFilter/freeze 列属性、datetime/pills 列类型、clickModes 选项

## html-gen-cli-spec

> html-gen CLI 参数惯例、子指令表、--json 统一信封（checkpoint 协议）与 skills 同步约定。开发/审计 html-gen CLI 时参考。

> 本文档定义 html-gen 项目的 CLI 规范（对齐 hermes-manager 治理规范
> 「CLI 规范」条目 + cli-args-reference.md 统一 JSON 信封）。
> 2026-08-19 定稿（决策: 1B 2A 3B 4A 5C 6A 7A）。

## 1. 入口与命名

- 入口: `html-gen.py`（argparse 子指令分发, `main()` 内 `add_subparsers`）
- 辅助脚本: `company-report.py`（独立入口, 不并入 html-gen 主 CLI）
- Handler 命名: `cmd_{指令}`（如 `cmd_doc` / `cmd_slide` / `cmd_table` /
  `cmd_knowledge` / `cmd_prompt` / `cmd_demo` / `cmd_help`）
  —— 为 hermes-manager `handle_{指令}` 惯例的项目变体（cmd_ 前缀,
  语义等价, 2026-08-19 决策保留不改）
- 分发: `{'help': cmd_help, ...}[args.command](args)`（dict 映射）

## 2. 子指令表

| 子指令 | 用途 | 输出 |
|:-------|:-----|:-----|
| `help` | 显示帮助 | 文本 |
| `doc` | Markdown → B 型文档页 | HTML 文件 |
| `slide` | Markdown → 幻灯片 | HTML 文件 |
| `table` | JSON → A 型数据表格 | HTML 文件 |
| `knowledge` | JSON → C 型知识库 | HTML 文件 |
| `prompt` | 输出项目 skills 内容 / 生成 prompts/ 在线阅读站点 | 文本 / JSON / 站点 (31 文件) |
| `demo` | demo 列表与详情 | 文本 / JSON |

> **参数（必填 / 可选 / 默认 / env 兜底）不在本文档枚举** —— 单一事实源是
> `html-gen help <type>` 的「CLI 参数」段（实现: `html-gen.py` 的 `TEMPLATE_CONTRACT[type]['cli']`，
> 由 `tests/test_help_contract.py` 对 argparse 实测提取做双向守卫）。复制到本文档即漂移。

## 3. 参数惯例（对齐 cli-args-reference.md）

- 长形 flag 是键（如 `--data` / `--output` / `--input` / `--groups`），短形仅为别名：
  `-d` / `-o` / `-i` / `-g`（短形不计入契约 `cli` 键集）。
- 逐模板长形 flag 清单、默认值、`HTML_GEN_*` env 兜底与「显式空串禁用」约定:
  `html-gen help doc|slide|table|knowledge` 的「CLI 参数」段。
- `--json` / `--brief` / `--site` / `--dir`（prompt）与 `--json` / `--all` / `--open` /
  `--rebuild`（demo）属**手写帮助主题**（描述 CLI 子命令而非数据契约），见 `html-gen help prompt|demo`。

## 4. --json 统一信封（checkpoint 协议）

`prompt` / `demo` 子指令的 `--json` 输出统一使用 checkpoint 信封:

```json
{"status": "ok", "error": "", "data": ...}        // 成功
{"status": "error", "data": null, "error": "..."} // 失败
```

字段:
- `status`: `"ok"` / `"error"`（必填, 仅两值）
- `data`: 成功时结果; no-match 返回 `[]` 非 `null`
- `error`: 失败消息; 成功为 `""`

各子指令 data 结构:
- `prompt`（无 skill）: `[{"name", "description", "references": []}, ...]`
- `prompt <skill>`: `{"name", "content", "references": {stem: content}}`
- `prompt <不存在>`: `{"status": "error", "error": "skill 'x' 不存在"}`
- `demo list`: `[{name, entry, type, featured, stale, ...}, ...]`
- `demo <name>`: 单 demo 对象

约定:
1. 错误走信封, 不 print 污染 stdout（人类提示走 stderr）
2. no-match 返回 `[]` 非 `null`
3. doc/slide/table/knowledge 输出 HTML 文件, 无 --json

## 5. skills/ 同步约定

- **真源**: `~/.hermes/profiles/dev/skills/software-development/html-gen*/`
  （skill_manage 写入位置, agent 会话加载处）
- **项目副本**: `html-gen/skills/`（已 git 提交）
- **同步**: 编辑 dev profile skill 后必须拷贝项目副本:
  ```bash
  cp -R ~/.hermes/profiles/dev/skills/software-development/html-gen*/ ~/CodeSpace/html-gen/skills/
  cd ~/CodeSpace/html-gen && git add skills/ && git commit -m "docs@skills: sync html-gen 项目副本"
  ```
- 拷贝整目录时清掉 `__pycache__/`
- 2026-08-19 当前项目副本: html-gen / html-gen-doc / html-gen-knowledge /
  html-gen-table / html-gen-slide / test-speed-optimization

## 6. 审计入口

- `hm check cli <path>`（治理规范 CLI 规范条目）: 检查 --json 检出 +
  handle_{指令} 命名 + help/version 内置
- 本规范文件: `html-gen/skills/html-gen-cli-spec/SKILL.md`

## html-gen-doc

> html-gen B 型文档模板规范。使用 html-gen doc 命令将 Markdown 转为自包含 HTML 文档页时参考。

## 概述
B 型文档模板从 Markdown 生成完整的文档页面。自动剥离 YAML frontmatter，提供侧边栏 TOC 导航、实时高亮、搜索等功能。

## 何时使用
- 需要将 Markdown 文档转为可分享的自包含 HTML 页面
- 需要带侧边栏导航的长文档（报告/手册/指南）
- 需要幻灯片模式（doc/slide 双模式）

## CLI 用法

```
html-gen doc -i report.md -o report.html [--title "标题"] [--subtitle "副标题"]
```

> 逐 flag 清单、默认值与 env 兜底见 **`html-gen help doc`** 的「CLI 参数」段
> （单一事实源: `html-gen.py` 的 `TEMPLATE_CONTRACT['doc']`）。

自动剥离 YAML frontmatter。标题优先级: `--title` > fm title > body h1 > stem。

## URL 状态

Bare 模式（默认隐藏侧边栏/工具栏，URL 参数可显式展示）与正文宽度三级
（窄/中/宽，默认 960px）的参数键与取值口径见 **`html-gen help doc`** 的「URL 状态」段
（`?sidebar` / `?toolbar` / `?width`）。

## Markdown 语法规范

> 完整语法子集（块级 / 行内 / Callout / 不支持项）见 **`html-gen help doc`** 的语法说明段。

- h1-h3: 自动加 id 锚点
- **加粗** / *斜体* / `代码` / [链接](url)
- 围栏代码块 (变长 fence 嵌套)
- 表格 (pipe table)
- 无序/有序列表
- Callout: `> **Note/Warning/Tip/Danger/注意/警告/提示/危险**: 内容`
- 分隔线 `---` / 引用 `> 文字`
- 不解析图片 (安全限制)

## 文档页特性
- 侧边栏 TOC (h2/h3 自动生成) + 实时高亮当前章节
- TOC 搜索 (🔍 按钮, 150ms debounce, ≥2 字符)
- 折叠/展开侧边栏 (48px, `[` 快捷键)
- 侧边栏宽度拖拽 (200-400px, localStorage)
- H3 子项开关 / 中英双语 / 🌙☀️ 主题切换
- 标题点击复制路径 / 代码复制 (clipboard + fallback)
- 行号 / Callout 提示框 / 阅读进度条 / 图片灯箱

## 验证清单
- [ ] `html-gen doc` 命令执行成功
- [ ] 侧边栏 TOC 与正文 h2/h3 对应
- [ ] 搜索过滤正常
- [ ] 折叠/展开/拖拽功能正常
- [ ] 代码复制功能正常

## 变更记录
- v1.0.0 (2026-08-08): 首次提炼自 AGENTS.md

## html-gen-knowledge

> html-gen C 型知识库模板规范。使用 html-gen knowledge 命令生成分 tab 侧栏的知识库页面时参考。

## 概述
C 型知识库通过顶部 tab 分组、左侧 section-as-menu 的导航结构，以 iframe 或内联 HTML 展示内容。专为多主题知识索引场景设计。

## 何时使用
- 多主题知识索引（如以剧读史、技术文档索引）
- 需要 tab 切换 + 侧栏导航的知识库
- section 与 item 一对一时可跳过 item 行直接点击 section 标题

## CLI 用法

```
html-gen knowledge -d data.json [-g groups.json] [--title "标题"] [--welcome "欢迎语"] [-o kb.html]
```

> 逐 flag 清单、默认值（`--title` 默认「知识库」、`--welcome` 默认欢迎文案）与输出目标三态
> 见 **`html-gen help knowledge`** 的「CLI 参数」段。

## 数据格式

条目 schema（item 7 键: title / group / section / badge / desc / url / icon，含必填与
`url`|`desc` 二选一语义）与数据源三态（数组 / `{items|data}` / 顶层 `output`）见
**`html-gen help knowledge`** 的「item 条目键」「数据源与输出目标」段。示例：

```json
[
  {"title": "条目名称", "group": "所属类目", "section": "子分类",
   "url": "detail.html", "desc": "<p>内联 HTML</p>", "badge": "标记"}
]
```

- title 与 section 同名时自动跳过 item 行 (K2 rule)
- 输出目标: 结构化 dict 顶层可带 `"output"`（仅 data 文件识别，groups 文件忽略）；
  优先级 CLI `-o` > JSON `output` > 均无中断 (exit 1)

## groups 格式

类目键（key / label / icon）见 `html-gen help knowledge` 的「groups 类目键」段。示例：

```json
[{"key": "类目key", "label": "显示名", "icon": "🏛️"}]
```

## 模板特性
- 顶部横向标签栏 (按 group 分组)
- 左侧 section-as-menu (section 标题可点击跳转)
- selectItem 双参数 (group, title) 支持跨组同名
- 侧边栏搜索 (150ms debounce, ≥2 字符过滤)
- 折叠/展开侧边栏 (`[` 快捷键, localStorage)
- 双内容模式 (iframe / 内联 HTML)
- 空状态欢迎面板
- localStorage 状态恢复 (group + item)

## 注意事项
- iframe 内容必须与知识库页面同源
- 单条 section (title===section && count===1) 自动跳过 kw-item 渲染
- Selenium headless 测试: iframe 内元素需 `driver.switch_to.frame()` 切换

## 变更记录
- v1.0.0 (2026-08-08): 首次提炼自 drama 知识库实施经验 + AGENTS.md

## html-gen-slide

> Use when generating slide-style presentation HTML from Markdown with

## 概述

`layout-slide.html` 是 html-gen 的独立幻灯片模板 — 将 Markdown 文件按 h2 标题分页，渲染为可逐页演示的 HTML。支持封面页、圆点导航、键盘翻页、全屏模式、localStorage 进度保存和性能警告。

> 文档平铺阅读使用 `html-gen doc` 命令（`layout-doc.html`）。详见 `html-gen-doc` skill。

## 何时使用

- 将 Markdown 课件/讲稿渲染为逐页幻灯片
- 需要键盘翻页演示的长文档
- 会议记录/课程笔记的分段回顾
- 演讲时配合全屏模式 `F` 键

## CLI 用法

```shell
html-gen slide -i lecture.md -o lecture.slide.html --title "课件标题" --subtitle "副标题"
```

> 逐 flag 清单、默认值与 env 兜底见 **`html-gen help slide`** 的「CLI 参数」段
> （单一事实源: `html-gen.py` 的 `TEMPLATE_CONTRACT['slide']`；slide 无 `--metadata`）。

## URL 状态

**slide 无 URL 状态** —— 不使用 URL 查询参数，阅读位置只由 localStorage 记忆
（`html-gen help slide` 的「URL 状态」段如实写明此点）。交互能力总览同样见
`html-gen help slide` 的「交互行为」段（8 项）。

## 分页规则

- **封面页**（Page 1）：h1 标题 + 副标题 + 元信息 + 节数统计
- **内容页**（Page 2+）：每个 `##` h2 为一页，包含标题及其后续内容直到下一个 h2

## Phase 3/4 — TOC 搜索 + 侧边栏宽度拖拽 (v1.1)

### TOC 搜索

侧边栏底部 🔍 按钮 → 切换 TOC 顶部搜索输入框 `.slide-toc-search`：
- 150ms 防抖，输入 ≥2 字符触发过滤
- 不匹配条目 `.filtered-out` (display:none)
- Enter → 跳转到第一个匹配项 + 关闭搜索
- Esc → 关闭搜索，清除过滤
- 点击搜索框外部 → 自动关闭
- 激活时 🔍 按钮变 `var(--cobalt-400)` 高亮

### 侧边栏宽度拖拽

侧边栏右边缘拖拽调整宽度：
- `.slide-sidebar-resize`: 8px handle，hover/active 时 cobalt 高亮
- 拖拽范围 200–400px
- 实时更新 `sb.style.width` 和 `sb.style.minWidth`
- localStorage 持久化 key: `html-gen:slide:sidebar-width`

### 侧边栏底部工具栏

- 🔍 — TOC 搜索开关
- ◀◀ / ▶▶ — 折叠/展开侧边栏 (48px collapsed)
- `[` 快捷键仅在非 input/textarea 聚焦时触发

## 导航操作

| 操作 | 行为 |
|:---|:---|
| `←` / `→` | 上/下一页 |
| `↑` / `↓` | 上/下一页 |
| `Space` | 下一页 |
| `Shift+Space` | 上一页 |
| `Home` | 首页（封面） |
| `End` | 末页 |
| `F` | 全屏演示切换 |
| 底部圆点点击 | 跳转对应页 |
| 侧边栏 TOC 点击 | 跳转对应 h2 页 |

## 进度系统

- 底部圆点导航：未访问(暗灰) / 已访问(灰) / 当前(蓝)
- 页码浮层 `N / M` 右上角显示，3s 无操作渐隐
- localStorage 进度保存（key: `layoutslide_page`），下次打开自动恢复

## 性能提示

当 Markdown 含 >50 个 h2 时，封面页顶部显示黄色警告条：

```
⚠️ 本文档共 N 节，幻灯片模式下可能加载较慢
```

## 侧边栏 H3 开关（v2.2+）

侧边栏头部包含 H3 子标题开关，默认隐藏 `.toc-h3` 项：

- 开关位于 sub 行右侧，显示 `H3`（关闭）/ `H3 ✓`（打开）
- `.toc-h3` 默认 `display: none`
- 点击开关切换所有 `.toc-h3` 的显示状态

### CSS 优先级（重要）

`.slide-toc a { display: block; }` 优先级高于 `.toc-h3 { display: none; }`。

**正确写法**:
```css
.toc-h3 { display: none; }
.toc-h3.show { display: block; }
/* 必须用更高优先级覆盖 .slide-toc a */
.slide-toc .toc-h3 { display: none; }
.slide-toc .toc-h3.show { display: block; }
```

## 侧边栏头部显示（v2.2+）

- **logo**: 文档标题超过 30 字自动截断 + `…`
- **sub**: 显示副标题（如 `Slide 演示`） + 节数统计（`共 N 节`），如无副标题则仅显示节数

```javascript
// logo 截断
var txt = logoEl.textContent.replace(/^🎞️\s*/, '');
if (txt.length > 30) txt = txt.substring(0, 30) + '…';
logoEl.textContent = '🎞️ ' + txt;

// sub 节数
var base = subEl.textContent.trim();
subEl.textContent = (base ? base + ' · ' : '') + '共 ' + (pages.length - 1) + ' 节';
```

## 安全实现

### DOM 渲染

- 页面内容使用 `cloneNode(true)` 深拷贝 DOM 子树，不经过字符串序列化
- 禁止 `innerHTML` 直接注入用户内容
- 侧边栏标题使用 `textContent` 设置

### Null Guard（关键规范）

**所有 `getElementById()` 调用必须添加 null guard。** 即使 HTML 结构正确，生成的模板在不同浏览器/环境可能出现元素不存在的情况。

```javascript
// ✅ 正确 — null guard
var el = document.getElementById('slideDots');
if (!el) return;
el.innerHTML = '';

// ❌ 错误 — 直接访问 null 属性导致 TypeError
document.getElementById('slideDots').innerHTML = '';
```

受影响的方法：`buildDots`、`_updateDots`、`_showPageNum`、`enter`、`exit`、`_syncToc`、`renderPage`、TOC click handler。

详见 `references/slide-mode-null-guards.md`。

### localStorage

```javascript
// ✅ 正确 — parseInt + 边界校验
try {
  var n = parseInt(localStorage.getItem('layoutslide_page'), 10);
  if (isNaN(n) || n < 0 || n >= this.pages.length) n = 0;
  this.currentPage = n;
} catch(e) { this.currentPage = 0; }
```

### XSS 防护

- 所有 `<!--KEY-->` 注入值自动转义 `</` → `<\/`（防止 script 标签闭合）
- Markdown 纯文本 `<` `>` `&` 自动转义（`_md_escape` 在 `inline_format` 前调用）

## 与 doc 模板的区别

| | `layout-doc.html` | `layout-slide.html` |
|:---|:---|:---|
| 命令 | `html-gen doc` | `html-gen slide` |
| 渲染模式 | 平铺连续滚动 | h2 逐页分页 |
| TOC 点击 | 滚动到锚点 | 跳转到对应页 |
| 进度条 | 顶部 2px 线 | 底部圆点 |
| 页码 | 无 | 右上角 `N / M` |
| 全屏 | 无 | `F` 键 |
| 代码复制 | ✅ | ❌ |
| 代码行号 | ✅ | ❌ |
| 图片灯箱 | ✅ | ❌ |
| 输出后缀 | `.html` | `.slide.html` |

## 常见问题

### 键盘翻页不响应
确保未聚焦在 input/textarea 元素中。模板会跳过表单元素内的键盘事件。

### 页面内容为空
检查 Markdown 的 h2 标题是否被正确解析。`## Title` 必须有空格。

### localStorage 恢复失败
所有 localStorage 操作包裹 `try/catch`，失败时回退到封面页（page 0）。

### 切换全屏后布局错乱
按 `F` 或 `Esc` 退出全屏。全屏使用 `Element.requestFullscreen()` 标准 API。

## 验证清单

- [ ] 运行 `html-gen slide -i input.md -o output.html` 正常生成
- [ ] 封面页显示 h1 标题、副标题、元信息、节数
- [ ] 所有 h2 正确分页，内容无丢失
- [ ] 键盘 ← → Space Home End 翻页正常
- [ ] 底部圆点导航正常，当前/已访问状态正确
- [ ] `F` 全屏进入/退出正常
- [ ] >50 h2 时性能警告显示
- [ ] 浏览器 Console 无 TypeError（所有 DOM null guard 生效）

---

## selenium-h3-toggle-testing

## H3 Toggle Visibility Test

Test `.toc-h3` hidden by default and toggleable via the H3 switch:

```python
class TestH3Toggle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        opts = Options()
        opts.add_argument('--headless')
        opts.add_argument('--no-sandbox')
        svc = Service(CHROMEDRIVER_PATH)
        cls.driver = webdriver.Chrome(service=svc, options=opts)

    def setUp(self):
        # CRITICAL: headless Chrome defaults to 800×600 which triggers
        # @media (max-width: 768px) → sidebar hidden → elements not interactable
        self.driver.set_window_size(1280, 800)
        self.driver.get('file://' + str(DEMO_HTML))

    def test_h3_hidden_by_default(self):
        h3s = self.driver.find_elements(By.CSS_SELECTOR, '.toc-h3')
        for h3 in h3s:
            self.assertEqual(h3.value_of_css_property('display'), 'none')

    def test_h3_toggle_visible(self):
        toggle = self.driver.find_element(By.ID, 'h3Toggle')
        toggle.click()
        h3s = self.driver.find_elements(By.CSS_SELECTOR, '.toc-h3')
        for h3 in h3s:
            self.assertNotEqual(h3.value_of_css_property('display'), 'none')

    def test_h3_toggle_hidden_again(self):
        toggle = self.driver.find_element(By.ID, 'h3Toggle')
        toggle.click(); time.sleep(0.15)  # show
        toggle.click(); time.sleep(0.15)  # hide
        h3s = self.driver.find_elements(By.CSS_SELECTOR, '.toc-h3')
        for h3 in h3s:
            self.assertEqual(h3.value_of_css_property('display'), 'none')
```

## CSS Specificity Debugging

When `display: none` doesn't work despite correct CSS:

1. Check if a higher-specificity rule overrides it (e.g. `.slide-toc a { display: block }` beats `.toc-h3 { display: none }`)
2. Use DevTools → Computed Styles to see which rule wins
3. Fix: match or exceed specificity (e.g. `.slide-toc .toc-h3 { display: none }`)

---

## slide-mode-null-guards

## 问题背景

2026-07-13，`layout-doc.html` 合并 doc/slide 模式时，在浏览器 Console 出现以下错误：

```
Uncaught TypeError: Cannot set properties of null (setting 'innerHTML')
    at Object.buildDots (template-B-markdown-spec-v1.0-20260707.html:1219:22)

Uncaught TypeError: Cannot read properties of null (reading 'classList')
    at Object.enter (template-B-markdown-spec-v1.0-20260707.html:1131:43)

Uncaught TypeError: Cannot read properties of null (reading 'scrollIntoView')
    at HTMLAnchorElement.<anonymous> (template-B-markdown-spec-v1.0-20260707.html:993:53)
```

## 根因

`document.getElementById()` 返回 `null` 时，直接访问 `.classList`、`.style`、`.innerHTML` 等属性导致 `TypeError`。即使在 HTML 中元素确实存在，不同浏览器/环境/解析顺序可能导致临时不可用。

## 解决方案

所有 `getElementById()` 调用必须添加 null guard：

```javascript
// buildDots
var dots = document.getElementById('slideDots');
if (!dots) return;
dots.innerHTML = '';

// _updateDots
var dotsEl = document.getElementById('slideDots');
if (!dotsEl) return;
var dots = dotsEl.children;

// _showPageNum
var el = document.getElementById('slidePageNum');
if (!el) return;

// _syncToc / slideNavTitle
var titleEl = document.getElementById('slideNavTitle');
if (titleEl) titleEl.textContent = ...;

// enter
var dm = document.getElementById('docMain');
var sm = document.getElementById('slideMain');
var sn = document.getElementById('slideNav');
if (!dm || !sm || !sn) return;

// exit
var sm = document.getElementById('slideMain');
if (sm) sm.classList.remove('active');

// TOC click
var target = document.getElementById(this.dataset.target);
if (target) target.scrollIntoView({ behavior: 'smooth' });

// perfWarning
var pw = document.getElementById('perfWarning');
if (pw && pw.textContent.trim()) pw.style.display = 'block';
```

## 影响范围

以下方法/位置必须添加 null guard：

| 位置 | 元素 | 风险 |
|:---|:---|:---|
| `buildDots()` | `slideDots` | innerHTML |
| `_updateDots()` | `slideDots`, `slideNavTitle` | children, textContent |
| `_showPageNum()` | `slidePageNum` | textContent, classList |
| `enter()` | `docMain`, `slideMain`, `slideNav` | style.display, classList |
| `exit()` | `slideMain`, `slideNav`, `docMain`, `perfWarning` | classList, style.display |
| TOC click handler | `this.dataset.target` | scrollIntoView |

## 测试验证

结构测试即可覆盖（无需 Selenium）：

```python
def test_null_guards_in_template(self):
    tmpl = (PROJECT / 'layout-slide.html').read_text()
    for pattern, desc in [
        (r'if\s*\(!?\s*dots?\s*\)\s*return', 'buildDots'),
        (r'if\s*\(!?\s*el\s*\)\s*return', '_showPageNum'),
        (r'if\s*\(!dm\s*\|\|\s*!sm\s*\|\|\s*!sn\s*\)\s*return', 'enter'),
        (r'if\s*\(target\s*\)\s*target\.scrollIntoView', 'TOC'),
    ]:
        self.assertIsNotNone(re.search(pattern, tmpl), f"Missing: {desc}")
```

## html-gen-table

> Use when building data table HTML pages with html-gen. Covers column config, actions, tabs, sorting, CSV export, and row selection for the A-type layout-table template.

## 概述

`layout-table.html` 是 html-gen 的 A 型模板 — 将 JSON 数据渲染为可交互的数据表格。支持搜索、排序、分页、Tab 分类过滤、操作列按钮、行选择、CSV 导出、列可见性控制和列宽拖拽。生成自包含单文件 HTML，零外部依赖。

## 何时使用

- 将 JSON 数据列表渲染为可交互 HTML 表格
- 文件索引、项目管理、数据浏览等列表展示场景
- 需要搜索/排序/分页的只读数据展示
- 演示操作按钮功能（使用 `desc` 模式）

## CLI 用法

```shell
# 简单数组格式（向后兼容）
html-gen table -d data.json --title "数据表格" -o index.html

# 结构化格式（推荐）
html-gen table -d data.json --title "项目列表" -o projects.html
```

## 数据格式

### 简单格式（JSON 数组）

```json
[{"名称": "项目A", "数量": 10}, {"名称": "项目B", "数量": 20}]
```

列名自动从第一条记录的 key 推导，所有列默认可排序。

### 结构化格式（推荐）

```json
{
  "columns": [
    {"key": "name", "label": "名称", "sortable": true, "locale": "zh"},
    {"key": "count", "label": "数量", "type": "number", "sortable": true},
    {"key": "actions", "label": "操作", "type": "actions", "actions": [...]}
  ],
  "data": [...],
  "output": "demos/xxx.html",   // 渲染目标 (无 CLI -o 时生效; 均无 → 中断 exit 1)
  "tabs": [
    {"key": "all", "label": "全部"},
    {"key": "Python", "label": "🐍 Python", "field": "lang"}
  ],
  "options": {"pageSize": 30, "exportCSV": true, "rowSelect": true}
}
```

## 列配置 (COLUMNS)

> **键规范单一事实源**: 列属性（22 键）、列类型（6 类）及其取值/默认值的完整定义只在
> **`html-gen help table`** 的「列属性」「列类型」段（实现: `html-gen.py` 的
> `TEMPLATE_CONTRACT['table']`，由 `tests/test_help_contract.py` 对 `layout-table.html`
> 实测消费做双向守卫）。本篇不再维护键表 —— 复制即漂移（CL013 起因: 「默认收起」列属性
> 长期未被任何面向人的文档收录，下游据旧文档把正确写法判成「臆造属性」）。

### 用法要点（键名与取值以 `html-gen help table` 为准）

- **列宽** `width` 仅作初始值：列宽拖拽会记忆到 localStorage（`html-gen:table:col-widths`），
  刷新后覆盖配置；改配置后需清 localStorage 或重新拖拽才生效。
- **两种「隐藏」语义不同**：一种**永不可见**（表格/筛选/分栏详情全部排除），另一种是
  **默认收起**且 ⚙️ 面板可开启、分栏详情仍全列渲染 —— 语义与键名对照见 help（此差异是 CL013 的直接动因）。
- **点击筛选默认关**：单元格点击筛选必须显式开启；标签列（pills）的标签点击筛选默认开、可关。
- **HTML 转义默认开启**（CL010 起）：只有显式关闭才豁免，不要把它当成 opt-in。
- **分栏模式列集**：任一列标记为「分栏可见」时，分栏表只显示这些列；也可用选项显式指定分栏列集。
- **数字列**务必设 `type: "number"`（JSON 注入后数字可能变字符串，否则按文本排序）。
- **中文排序**设 `locale: "zh"`（走 `localeCompare(text, 'zh')`）。

### 操作按钮 (actions)

操作按钮列（`type: "actions"`）的按钮子键与优先级（`copyKey` > `hrefKey` > `handler`/`desc`）
见 `html-gen help table` 的「actions[] 操作按钮子键」段。示例：

```json
{
  "icon": "📋",        // Emoji 图标
  "label": "复制",     // title 提示文本
  "copyKey": "name",   // 模式1: 复制字段值到剪贴板
  "hrefKey": "url",    // 模式2: 新标签页打开 URL
  "desc": "复制名称"   // 模式3: 点击弹 Toast 展示描述（演示用）
}
```

只生效第一个匹配的模式；`handler` 为自定义 JS 函数名（模板调 `window.{handler}(event, row)`）。

## Tab 分类过滤 (TABS)

Tab 键（`key` / `label` / `field` / `match` / `contains` / `value`）、匹配语义与默认字段见
`html-gen help table` 的「Tab 属性」段。示例：

```json
[
  {"key": "all", "label": "全部"},
  {"key": "Python", "label": "🐍 Python", "field": "lang"},
  {"key": "工具", "label": "🔧 工具", "field": "group"}
]
```

- 第一个 Tab 的 key 用于「全部」；`contains: true` 走逗号/顿号分隔的包含匹配；Tab 计数 = 匹配行数。
- Tab 选择自动保存到 localStorage。

## 单元格点击行为（默认）

点击行为优先级链（从高到低）：
1. 列上的显式单元格点击行为（分栏 / 弹窗）
2. 列上的点击筛选开关（显式 true）
3. **第 1 列（首个有 key 的数据列）→ 默认打开分栏预览**（展示该行元信息）
4. 其余列 → 无操作

即：普通单元格默认无筛选；需要按值筛选的列显式开启；标签列默认可点筛选。

## 全局选项 (OPTIONS)

13 个 options 顶层键（含 `searchFields` / `showIndex` / `defaultFilter` / `feedback` /
`clickMode` 单数兼容别名）及其默认值见 `html-gen help table` 的「选项」段；
`options.feedback` 子键（5 项）见「options.feedback 子键」段。

## URL 状态分享 (🔗)

URL 状态键（`?tab` / `?q` / `?split`）的取值口径见 `html-gen help table` 的「URL 状态」段。
行为：

- 状态变化用 `history.replaceState` 静默同步（不产生历史记录），默认参数（空值）自动剔除
- **tabs 行居右按钮区 `.tabs-actions`**（CL005）：↗ 分享按钮拷贝规范化 URL（clipboard + execCommand fallback，headless 兼容）；🏠 home 入口（`--home-url` 注入，与 share 同容器 36px 圆角深底，font-size 1rem 图标同尺寸）
- 排序 / 快速过滤触发时自动 closeSplit（下标语义失效保护）
- 加载时按 tab → q → split 顺序恢复（HG-SEC-076）

## 操作按钮 Emoji 参考

| 类别 | Emoji |
|:---|:---|
| 查看/导航 | 👁️ 查看 · 🔗 打开 · 👀 预览 · 📍 定位 |
| 编辑/修改 | ✏️ 编辑 · 📝 重命名 · 📁 移动 · 📌 置顶 · ⭐ 收藏 |
| 操作/执行 | ▶️ 播放 · ⬇️ 下载 · 🚀 运行 · 🧬 克隆 |
| 复制/分享 | 📋 复制 · 📎 链接 · 💻 命令 · 🗂️ 路径 · 📤 分享 |
| 删除/清理 | 🗑️ 删除 · 📥 归档 · 🧹 清理 |
| 信息/诊断 | ℹ️ 元信息 · 📄 日志 · 📊 状态 · 🕐 历史 · 🔍 Diff |

## 常见场景

### 文件管理器

```json
{"actions": [
  {"icon": "👁️", "label": "预览", "desc": "预览文件内容"},
  {"icon": "📋", "label": "复制路径", "copyKey": "path"},
  {"icon": "🗑️", "label": "删除", "desc": "永久删除（需确认）"}
]}
```

### CRUD 管理

```json
{"actions": [
  {"icon": "👁️", "label": "查看", "desc": "查看详细信息"},
  {"icon": "✏️", "label": "编辑", "desc": "修改记录内容"},
  {"icon": "🔗", "label": "打开", "hrefKey": "url"},
  {"icon": "🗑️", "label": "删除", "desc": "永久删除（需二次确认）"}
]}
```

## 常见问题

### Q: 操作按钮点击没反应？
检查 `col.type` 是否设为 `"actions"`，actions 数组中每个按钮必须至少配置 `copyKey`、`hrefKey` 或 `desc` 之一。

### Q: 数字列排序不正确？
设置 `col.type: "number"`。JSON 注入后数字可能变字符串，`type: "number"` 确保使用 `parseFloat` 比较。

### Q: 中文排序混乱？
设置 `col.locale: "zh"` 使用 `localeCompare(text, 'zh')`。

### Q: Tab 切换后分页错误？
每次切换 Tab 自动重置到第 1 页。Tab 状态保存在 localStorage key `htmlgen_tab`。

## 验证清单

- [ ] 数据 JSON 格式正确（简单数组或结构化对象）
- [ ] 列 key 与数据字段名一致
- [ ] `type: "actions"` 列配置了 actions 数组
- [ ] Tab 的 field 与数据字段匹配
- [ ] 运行 `html-gen table -d data.json -o output.html` 正常生成
- [ ] 生成的 HTML 在浏览器中表格正常渲染
- [ ] 排序、搜索、分页功能正常
- [ ] 操作按钮点击有响应（copyKey 复制 / hrefKey 跳转 / desc Toast）


## 变更记录
- v2.5.0 (2026-08-29): 分享/Home 按钮统一放 tabs 行居右 `.tabs-actions`（↗ 图标 + home-link 流式同容器 36px，CL005）
- v2.4.0 (2026-08-29): 新增 URL 状态分享（?tab&q&split replaceState 同步/恢复 + 🔗 拷贝按钮）
- v2.3.0 (2026-08-06): quickFilter 默认关（显式 true 启用）+ pillFilter/onCellClick/preview 列属性; tabs value/contains 匹配; pills 顿号分隔; 第 1 列默认分栏
- v2.2.0 (2026-08-06): 新增 quickFilter/freeze 列属性、datetime/pills 列类型、clickModes 选项; 兼容单数 clickMode
- v2.1.0: 列冻结、右侧固定列、分栏列过滤增强、单元格点击分栏、自定义模态框渲染器、SKILL.md 加载

---

## table-demo-prompt

## 任务

使用 `html-gen table` 命令将 JSON 数据转为自包含 HTML 数据表格页。

## 数据规范

四个顶层分区: `columns`（列定义）/ `data`（数据行, 别名 `rows`）/ `tabs`（标签页）/ `options`（选项）。
**键名、取值与默认值一律以 `html-gen help table` 的键规范段为准**（单一事实源: `html-gen.py` 的
`TEMPLATE_CONTRACT['table']`）。下列仅为写法示例 —— 示例可含键名, 规范以 help 为准:

```
columns: [{key, label, type, width, preview, onCellClick}]
data:    [{<字段名>: <值>}]
tabs:    [{key, label, field}]
options: {pageSize, exportCSV, search, columnsSplit}
```

## 列类型

文本(默认) / 数值 / 日期 / 标签 / 视频 / 操作按钮 六类; 取值名与排序口径见
`html-gen help table` 的「列类型」段。

## 默认行为须知

- 标签点击筛选默认开、单元格快速筛选默认关（两者均可在列属性覆盖, 键名与默认值见 help「列属性」段）
- 第 1 列默认分栏预览（无显式单元格点击配置时）

## 生成命令

```bash
html-gen table -d data.json --title "标题" -o index.html
```

## 质量要求

- 所有数据列显式设列宽（Cinema 宽度模型要求; 默认值见 help「列属性」段）
- 操作列表取 `actions`、标签列表取 `pills`（列类型取值见 help）

## pages-index

> Use when building or optimizing a GitHub Pages project landing/index page. Hero + product-matrix layout, light theme, copy buttons, dynamic two-screen hero, github-corner theming, dual-source sync.

## 概述

沉淀自 html-gen.cli 落地页两轮迭代（2026-08-24，review 审计 PASS 100/A）。适用于"一仓多产物"项目（如 CLI 工具 + 多模板/多 demo）的 pages index 页。深色主题 + 浅色可切换，中文优先，零依赖单文件。

## 骨架（hero + 产物矩阵）

```
<body>
  <button class="theme-btn" id="themeBtn" aria-pressed="false">🌙</button>   ← 固定右上角 right:88px 避让 corner
  <a class="github-corner">…SVG…</a>
  <section class="hero">       ← 动态两屏（见下）
    h1 渐变标题(前置品牌圆标 img.hero-logo) + tagline + badges 徽章行 + scroll-hint
    hero-blocks 2 卡:
      卡1: ⚡ 安装 & 快速开始（合并, 每条 code-block 行内复制 + block-title "复制全部"）
      卡2: 🆚 竞品对比（转置表格: 行=维度, 列=工具, 自家列全 ✓ 高亮 .win）
  </section>
  <section class="templates">  ← 产物矩阵: 每产物一张卡
    tpl-head: icon(四色 ia/ib/ic/id) + 名称 + guide 链接 + 文件行数
    tpl-body: scenarios pills + features 列表 + cli-box(带复制) + demos 列表
  </section>
  <footer class="site-footer">GitHub(favicon) · Gitee(favicon) · MIT</footer>
</body>
```

断点: 4 列 → `@media (max-width:1500px)` 2 列 → `@media (max-width:1100px)` 1 列。

hero 卖点分层: title(品牌) → tagline(一句话定位) → badges(3-4 短徽章: ⚡ 零依赖 · 🌙 深色主题 · 🇨🇳 中文优先 · 📦 单文件) → blocks(安装/对比)。tagline 已承载卖点时可跳过 badges（避免重复）。

竞品对比卡（转置模式）: 340px 卡片内放不下"工具×维度"正排表，转置为"维度×工具"（6 行维度 × 4 列工具），自家列 `th.hl` + `td.win` 高亮，✓/— 符号，11px 紧凑样式。对比是"为什么选我"最直接说服工具（http-server 实证）。

## 主题系统

- style-guide.css `:root` 定义语义色变量: `--text-primary/--text-body/--text-secondary/--text-muted/--text-faint/--border-strong/--border-soft/--code-bg/--code-text/--code-cmd/--hero-title-from`；`:root.light` 覆盖全套
- 页面所有硬编码色一律 var() 引用（含 inline style），否则浅色下对比度失败（WCAG AA 4.5:1）
- 主题按钮: `document.documentElement.classList.toggle('light')` + localStorage key 规范 `html-gen:<page>_theme`（模板页用 doc_theme/kw_theme/layoutslide_theme，落地页用 index_theme 隔离）
- `aria-pressed` 随状态同步
- 陷阱: style-guide.css 的 `:root.light a { color: var(--cobalt-600) }` 特异性 (0,1,1) 会覆盖 `.github-corner` (0,1,0)，浅色下 corner 变 indigo——必须加 `:root.light .github-corner { color: var(--gh-octocat); }` (0,2,0) 且 hover 同样覆盖

## github-corner 浅色配色

- 变量: `:root { --gh-corner-fill: rgba(0,0,0,0.41); --gh-octocat: var(--text-secondary); }` / `:root.light { --gh-corner-fill: rgba(0,0,0,0.75); --gh-octocat: #ffffff; }`
- SVG: 三角 `fill="var(--gh-corner-fill)"`，octocat `fill="currentColor"` + `.github-corner { color: var(--gh-octocat); }`
- 浅色 = 深三角 + 白猫（经典 GitHub 形态）；深色 hover 也须保持 `var(--gh-octocat)`（加 `.github-corner:hover` 保护）
- 两种模式: 无工具栏页 = 全图标可点（pointer-events auto）；有工具栏页 = 穿透 `pointer-events:none` + hit 区（36px）

## 动态两屏 hero

目标: 首屏底部看到第二屏标题 + scroll-hint 固定视口底部。

```js
function updateHeroHeight() {
  var hero = document.querySelector('.hero');
  if (hero) hero.style.minHeight = (window.innerHeight - 55) + 'px';  // 55≈第二屏标题露出高度，按需微调（-55~-110）
}
updateHeroHeight();
window.addEventListener('resize', updateHeroHeight);
```

- `.scroll-hint`: `position:fixed; bottom:24px; left:50%; translateX(-50%)` + `.hide { opacity:0; visibility:hidden }`，scrollY>8 淡出、回顶恢复
- CSS 保留 `min-height:80vh` 作无 JS fallback

## 复制按钮

```js
function copyText(text, btn) {
  var orig = btn ? btn.textContent : '';
  var done = function() { if (btn) { btn.classList.add('ok'); btn.textContent = '✅';
    setTimeout(function() { btn.classList.remove('ok'); btn.textContent = orig; }, 1500); } };
  var fallback = function() {
    var ta = document.createElement('textarea');
    ta.value = text; ta.style.position = 'fixed'; ta.style.left = '-9999px';
    document.body.appendChild(ta); ta.select();
    var ok = false;
    try { ok = document.execCommand('copy'); } catch(e) {}
    document.body.removeChild(ta);
    if (ok) done();   // 必须检查返回值，失败不标记 ✅
  };
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(text).then(done).catch(fallback);
  } else { fallback(); }
}
```

- 按钮 `data-copy` 存原文（不含 `$` prompt），恢复用保存的 orig（勿硬编码 📋，会丢"复制"标签）
- headless Chrome 兼容: clipboard API 不可用时走 execCommand
- **行内复制模式**（首屏快速开始区价值最高）: `.code-block` 改 flex + `margin-left:auto` 的 copy-btn；block-title 可留"复制全部"（data-copy 用 `&#10;` 连接多条命令）。层级: 块级"复制全部" + 行级精准复制

## 双源同步 + 防漂移测试

根 index.html 与 demos/index.html 为独立副本时: 功能特性必须同步，保留各自差异（corner 模式/链接前缀/hero 有无）。防漂移测试断言两文件关键功能特征一致:

```python
features = ['id="themeBtn"', 'html-gen:index_theme', 'class="site-footer"',
            'class="copy-btn"', 'max-width: 1500px', '--gh-octocat', 'rel="noopener"',
            'html-gen table -d data.json', ...]
missing_root = [f for f in features if f not in root]   # 同样查 demos
```

## Footer favicon 图标化

平台链接前置 14px favicon: `<img class="favicon" src="https://github.com/favicon.ico" alt="">` + 文本。样式 `.favicon { width:14px; height:14px; vertical-align:-2px; margin-right:5px; }`。前提: 逐个 `curl -sL -o /dev/null -w "%{http_code}" <url>` 验证 200（部分平台 favicon 带 hash 易 404，如 PyPI）。

## 测试规范

- 沿用项目模式: headless Chrome + `window.__testErrors` JS 错误检查 + `WebDriverWait` 主元素
- 覆盖: hero 动态高度（`offsetHeight ≈ innerHeight-110 ±6`）、scroll-hint fixed+淡出、主题切换+localStorage 持久化、复制按钮数量+data-copy 非空、footer 链接、light 白猫（`rgb(255,255,255)`）、双源一致性
- 全量: `python3 -m pytest tests/ -q -n 4`

## Pitfalls

1. `:root.light a` 全局规则覆盖 corner/按钮颜色（特异性陷阱）——高特异性覆盖必须显式加
2. inline style 硬编码色不随主题——所有颜色走变量
3. `test_02_hero_100vh` 类断言随 hero 高度设计变更必须同步（80vh→动态两屏→断言 ≥0.75 或精确 vh−110）
4. 行数/文件数等元信息漂移（AGENTS.md vs 页面 tpl-file）——review 会抓（HG-SEC-036）
5. 双源只改一处导致防漂移测试红——同步时保留差异点，同步功能点

## test-speed-optimization

> html-gen Selenium 测试套件提速。测试执行慢时用 xdist 并行 + sleep 调低 + WebDriverWait 三方案优化。

## 何时使用

- 全量 Selenium 测试执行慢（>100s），需要提速
- 需要定位耗时瓶颈（sleep 分布 / --durations）
- 需要并行化测试（xdist）或调低固定 sleep

## 耗时分析方法论

1. **sleep 分布统计**：扫描 tests/*.py 统计 `time.sleep(X)` 分布，定位大值 sleep
   ```python
   import re
   from pathlib import Path
   for f in sorted(Path('tests').glob('test_*.py')):
       sleeps = re.findall(r'time\.sleep\(([\d.]+)\)', f.read_text())
       # 按值聚合计次
   ```
2. **--durations 定位**：`pytest tests/ -q --durations=10` 看最慢的 10 个用例
3. **区分 sleep 类型**：
   - setUp 页面加载 wait（`get()` 后的大 sleep）→ 用 WebDriverWait（D'）
   - 交互 wait（点击后的小 sleep）→ 调低映射（D）
   - localStorage 上下文 wait（clear 前的 sleep）→ 保持或微调

## 三方案

### 方案 C — pytest-xdist 并行（最大收益，零逻辑风险）

```ini
# pytest.ini
[pytest]
addopts = -n 4
```

```bash
python3 -m pytest tests/ -q -n 4     # 并行, ~4x 提速
python3 -m pytest tests/ -q -n 0     # 定向调试, 关闭并行
```

依赖：`pytest-xdist>=3.8.0`（requirements-dev.txt 或 AGENTS.md 显式声明）。

### 方案 D' — setUp sleep → WebDriverWait（最稳健）

```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

WebDriverWait(self.driver, 5).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, '<主元素>'))
)
```

主元素按页面类型：table → `.data-table`；knowledge → `.kw-tab`；doc → `.doc-body`；slide → `.slide-sidebar`。超时兜底 5s。

### 方案 D — 交互 sleep 调低映射（机械）

映射表（大值减半，小值不动）：

| 原值 | 新值 |
|:---|:---|
| 0.3 | 0.15 |
| 0.4 | 0.2 |
| 0.5 | 0.25 |
| 0.6 | 0.3 |
| 0.8 | 0.4 |
| 0.9 | 0.45 |

`0.08 / 0.1 / 0.15 / 0.2 / 0.25` 保持不变。

辅助脚本：`scripts/speedup_sleeps.py`（--dry-run / --apply / --restore）。

## 验证流程（防 flaky）

1. D' + D 改完 → 单线程连跑 2 次：`pytest tests/ -q -n 0`
2. 加并行：`pytest tests/ -q -n 4`
3. 抽样 flaky（各 3 次）：`test_table_features.py` / `test_drama_knowledge.py`
4. 任何文件失败 → 从 .bak 回退该文件（`cp test_x.py.bak test_x.py`）

## 坑

1. **副本测试文件 PROJECT 绝对路径**：不同环境 chromedriver/项目路径不同，副本文件须修正 `PROJECT`、`CHROMEDRIVER` 绝对路径。
2. **stale element**：split 面板/详情加载类交互需较慢 wait，sleep 减半可能触发 `StaleElementReferenceException`，该文件回退。
3. **WebDriverWait 注入需补 import**：若原文件未 `from selenium.webdriver.common.by import By`，注入 WebDriverWait 时必须一并补 By/WebDriverWait/EC 三个 import，否则 `NameError`。
4. **并行共享路径**：所有测试写 /tmp 须文件名唯一（不跨文件冲突），不得写 demos/ 或项目目录；xdist 下各 worker 独立进程。
5. **幂等**：speedup_sleeps.py 用 `# [speedup]` 标记已改行，二次 --apply 不重复改。注意：被回退的文件（cp .bak 还原）无标记，--dry-run 会再次列出该文件——属预期，勿二次 --apply（否则重新引入 flaky）。
6. **toast/异步文本等待**（2026-08-21 实测）：点击后 `time.sleep(0.2)` 再读 toast textContent 会偶发 flaky（单线程慢时 0.2s 内 toast 未更新）。改 `WebDriverWait.until(EC.text_to_be_present_in_element((By.ID, 'docToast'), '已复制: xxx'))`。规律：**凡是断言"点击后产生的异步文本/DOM"一律用 WebDriverWait，不用固定 sleep**。
7. **测试收集边界**（2026-08-19 实测核实）：pytest.ini `testpaths = tests` 已限定收集范围——根目录直接 `python -m pytest`（无参数）只收集 tests/ 的 141 用例，正常无崩溃；scripts/ 下辅助脚本（company-report.py 等）不被收集。约定：① 全量/定向统一显式 `pytest tests/`（意图明确）；② scripts/ 下脚本避免 `test_` 前缀命名（若移除 testpaths 或 `pytest scripts/` 会按文件名误收集）；③ 早前"scripts/test_profile.py 顶层 sys.exit(1) 导致 xdist 崩溃"的 pitfall 已不适用（该文件不存在、pytest.ini 为 `-n 4` 非 `-n auto`、testpaths 已防）。

## 验证清单

- [ ] 单线程 `pytest tests/ -q -n 0`：全绿，连跑 2 次无 flaky
- [ ] 并行 `pytest tests/ -q -n 4`：全绿，~25-30s
- [ ] speedup_sleeps.py --dry-run / --apply 幂等验证
- [ ] 无测试写共享路径（并行安全）
