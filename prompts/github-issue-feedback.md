
# GitHub Issue 反馈通道（数据纠错闭环）

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
# feedback-targets.yaml 字段契约与校验链

> 配置示例：`html-gen.cli/scripts/feedback-targets.yaml`（target `countries`）。
> 解析入口：`scripts/countries-issue-sync.py`（`load_target()` / `plan_issues()` / `guarded_fields()`）。
> 依赖：仅 PyYAML（**dev 依赖**；html-gen 运行时零依赖不受影响）。

## 1. target 字段表（20 项）

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
# 跨项目接入 Prompt：GitHub Issue 数据反馈闭环

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
# Issue Form 模板与约束

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
