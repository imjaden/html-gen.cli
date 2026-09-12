---
name: github-issue-feedback
description: Use when a static HTML data page needs a GitHub Issue feedback loop (reader submits data corrections → validated write-back to the data JSON → rebuild). Covers page-side ✏️ button, Issue Form, target config, sync script, security rules.
version: 1.0.0
author: ops
license: MIT
metadata:
  hermes:
    tags: [github-issue, feedback-loop, data-fix, static-site, html-gen, form, write-back]
    related_skills: [html-gen, html-gen-table, github]
---

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
            → 行唯一定位 → 类型 → 非空 → 入库 XSS 防护 → 幂等 → 冲突取最新
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

1. **脚本名与 docstring**：docstring 内案例名有 4 类形态（脚本名 ×8 / 表单模板名 / target 名 / 设计文档名）
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
