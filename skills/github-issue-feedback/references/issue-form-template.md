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
