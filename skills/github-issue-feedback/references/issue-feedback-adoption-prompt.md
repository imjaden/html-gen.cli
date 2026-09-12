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
