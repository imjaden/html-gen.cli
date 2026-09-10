# A 型表格 GitHub Issue 反馈通道设计 v1.2 (2026-09-10)

> v1.2 修订（实现审计后跟进，审计 PASS 95/A）：
>   ① 用户口径调整：表单/按钮文案「数据纠错」→「**数据反馈**」（issue title 前缀 `[数据反馈] `）
>   ② HG-SEC-119 修复：`--issue N` 改用 `gh issue view <N>` 直查（GitHub 搜索无 `in:number` 限定符，
>      原实现 `--search "<n> in:number"` 会静默退化为文本搜索）
>   ③ HG-SEC-120/121/122 折入（dry-run 零写盘自动化护栏、test_01 docstring 口径、恢复函数 staticmethod 化）
>   ④ HG-SEC-123 标注更正：`openSplitAt` 三处调用实为 pills / `onCellClick='split'` / **首列默认**
> v1.1 修订: 折入设计评审 HG-SEC-110..118（PASS 85/A，报告
>   documents/review/countries-issue-feedback-design-review-v1.0-20260910.md）：
>   ① repo 落 options.feedback（HG-SEC-111 根除 videos syncer 重建漂移）
>   ② gh 调用显式 list-form + shell=False（HG-SEC-110）
>   ③ body 解析边界（未知段并入上一字段，HG-SEC-115）
>   ④ rebuild.args 补 --favicon（HG-SEC-116）
>   ⑤ TC-01 断言口径修正（HG-SEC-112）+ 文档同步面补全（HG-SEC-113）
> 闭环: HTML-GEN-CL009 · 模式: 独立（不入调度队列）
> 探讨确认: A1 B1 C1 D1 E1 F1 G1 H1 I1 J1 K1 L1 M1 N1 + A0-1 A′1 O1 P1 Q1 + S1 T1 U1 V1（2026-09-10）
> 试点: demos/countries-table.html ← data/_countries-data.json（后续可复用至其他 A 型表格案例）
> 前置: HTML-GEN-CL002 / CL004 / CL006（table 模板 + videos 同步器 + rebuild 三参数）

## 1. 背景与需求

A 型表格案例（countries / provinces / drama 系列）数据为人工整理，读者发现错误时没有
反馈入口；维护者也无从收集结构化纠错。本闭环建立「页面 → GitHub Issue → 数据回写 →
产物重建」的最小闭环，以 countries-table 为试点，设计上支持后续案例复用。

需求（用户原文）：
1. 以 `demos/countries-table.html?split=0` 为例，添加反馈/编辑图标按钮，点击跳转 GitHub
   Issue 页面，自动填充该案例相关信息 + 手工填写；
2. 获取 issue 数据，更新至 `data/_countries-data.json`。

约束（实测确认）：
- **静态站无后端**：唯一提交通道 = 跳转 GitHub New Issue 页；解析/回写只能在本地脚本完成；
- **Issue Forms URL 预填只支持 `input` / `textarea`**（dropdown / checkboxes 不可预填，
  GitHub 官方 form schema `id` 条款 + 社区实证）→ 需预填的字段一律用 input/textarea；
- **GitHub 表单无只读字段**：预填字段仍可被人工修改 → 靠「请勿修改」文案 + 脚本白名单校验兜底；
- **labels 不受 URL 参数控制**（表单 `labels:` 声明 + 仓库需已存在该 label）；
- 项目约定：只 commit 不 push（push 走 review 通道）；运行时 html-gen 零依赖（脚本可用 PyYAML）。

## 2. 决策记录

| 项 | 决策 | 说明 |
|:---|:---|:---|
| A1 / A′1 | 按钮挂**分栏预览 header**；一期不加操作列 | 零列定义变更、不动数据 schema 与 localStorage 列宽缓存 |
| A0-1 | 接受修改共享模板 `layout-table.html` | 默认不传参 → 条件渲染为无 → 既有页面视觉零变更 |
| B1 | 单按钮「✏️ 纠错」 | 不做「编辑 / 反馈」双按钮 |
| C1 | Issue **Form**（`.github/ISSUE_TEMPLATE/data-fix.yml`）+ URL 预填 | 结构稳定、可加 label 与必填校验 |
| D1 | 预填 page / dataset / row / row_en / field / current | 用户填 suggested / source / note |
| E1 | join key = `country_zh`（195/195 唯一），`country_en` 作二次校验 | 无 ISO 码字段，不新增（E2 留二期） |
| F1 | 白名单写回 + 类型校验 + protected(videos) + 歧义拒绝 | dry-run 打印 before→after diff |
| G1 | 新增 `scripts/countries-issue-sync.py` | 与 `tool-table-videos-syncer.py` 风格一致，职责分离 |
| H1 | 先人工跑（dry-run → apply），跑顺后再评估 cron | 本期无自动化调度 |
| I1 | apply 后回评「旧→新」；`--close` 显式开关才关 issue | 默认只回评 |
| J1 | 需预填字段用 `input`（字段 key 列在 description 里） | 受 form schema 硬约束 |
| K1 | 新增 `--feedback-repo` + env `HTML_GEN_FEEDBACK_REPO`，默认不注入 | 隐私默认（同 `--github-url` 语义）；显式空串禁用 |
| L1 / Q1 | 一期只做 A 型表格 + countries-table 试点 | provinces / drama 二期 |
| M1 | 新增 `tests/test_issue_feedback.py` + 1 条 HG-SEC 登记 | Selenium 渲染条件 + 脚本解析/apply 单测 |
| N1 | 本地脚本路线（GitHub Actions 留二期） | gh CLI 已登录 `imjaden`（token 含 repo scope） |
| O1 | `openSplitAt(rowIdx, colKey)` 携带被点列 → 预填 `field` | 改动 3 处调用 + 1 个形参 |
| P1 | 创建 label `data-fix` + `config.yml`（关 blank issue） | label 不存在时表单 labels 会被静默忽略 |
| S1 | 同步脚本**配置驱动**（`scripts/feedback-targets.yaml`） | 一期只启用 countries 一份配置 |
| T1 | 一份通用 `data-fix.yml`（page/dataset 承载来源） | 全案例共用 |
| U1 | 二期接 provinces + drama；工具类页面（skills-list / demos-index）不开放 | — |
| V1 | 反馈配置独立文件，**不复用** `cache/data/_countries-data.videos.yaml` | 后者被 videos syncer 整体重写（`{'target','countries'}`），附加段必被覆盖 |

### 2.1 决策微调（实施期确定，记录备查）

- **`--feedback-labels` 不实现**：Issue Form 的 label 由模板 `labels:` 固定声明，URL 参数无法
  覆盖 → 无意义的开关不引入（K1 中的可选项取消）。
- **case 级配置放在数据 JSON 的 `options.feedback`**：`{"dataset","key","altKey","repo"}` 随数据文件走
  （复用即随案例自描述）→ 无需新增模板占位符（见 §4.2）。
- **repo 必须落 JSON（v1.1 / HG-SEC-111）**：`tool-table-videos-syncer.py` 是**独立重建路径**
  （每周同步视频后重建 countries-table.html），其 `resolve_rebuild_args` 只发
  `--github-url/--home-url/--favicon`，永不发 `--feedback-repo`。若 repo 只由 CLI/env 提供，
  该路径重建后反馈按钮会静默消失。落 JSON 后任何重建路径（videos / 手工 / 本脚本）都能拾取，
  从机制上根除漂移（countries 已是公开 demo，github-corner 已暴露同一仓库，无隐私回退）。

## 3. 数据契约

### 3.1 issue 表单字段（form id ↔ 中文 label ↔ 用途）

| id | label | 控件 | 预填 | 必填 | 说明 |
|:---|:---|:---|:---|:---|:---|
| page | 页面 | input | ✅ | ✅ | 如 `demos/countries-table.html`，脚本用其路由 target |
| dataset | 数据集 | input | ✅ | ✅ | 如 `countries`，与 config `dataset` 比对 |
| row | 行标识 | input | ✅ | ✅ | `country_zh` 值 |
| row_en | 行英文标识 | input | ✅ | ⬜ | `country_en`，二次校验（防改名歧义） |
| field | 字段 | input | ✅ | ✅ | 数据列 key，如 `pop_wan` |
| current | 当前值 | input | ✅ | ⬜ | 页面现值，仅供对照 |
| suggested | 建议值 | textarea | ⬜ | ✅ | 用户填写 |
| source | 来源 | input | ⬜ | ✅ | 权威出处链接/说明 |
| note | 补充说明 | textarea | ⬜ | ⬜ | 用户填写 |

> label 文本**不带 emoji 与括号后缀**（render 后 body 段落标题为 `### 页面`），使解析可用
> 精确匹配；「请勿修改」提示放 `description` 与表单首部 markdown 块。

### 3.2 URL 预填参数（模板生成，全部 `encodeURIComponent`）

```
https://github.com/<repo>/issues/new
  ?template=data-fix.yml
  &title=[数据反馈] <dataset> · <row> · <field>
  &page=<location.pathname 去前导 />
  &dataset=<options.feedback.dataset>
  &row=<row[key]>
  &row_en=<row[altKey]>
  &field=<被点列 key，无则空>
  &current=<row[field]>
```

- `page` 取运行时 `location.pathname`（去前导 `/`），随部署路径自适应，无需注入；
- 空值参数一律不拼接（GitHub 对空参数无意义）；
- 单字段预填 URL ≈ 160 字符，远低于浏览器 ~8KB 上限（实测样本）。

## 4. 模板改动点（layout-table.html）

### 4.1 按钮渲染（`renderSplitPreview`，现 L1076-1110）

header 由 `▲ ▼ 标题 ✕` 变为 `▲ ▼ 标题 ✏️ ✕`（`✏️` 仅当反馈已启用时渲染）：

```js
var fb = FEEDBACK ? '<button class="sp-feedback" onclick="openFeedbackIssue()" title="反馈/纠错数据">✏️</button>' : '';
header.innerHTML = '<button class="sp-nav" …>▲</button><button class="sp-nav" …>▼</button> '
                 + title + fb + '<button class="sp-close" …>✕</button>';
```

CSS：`.sp-feedback` 复用 `.sp-nav` 视觉规格（深底、hover 反馈、36px 触达）。

### 4.2 配置来源（零新增占位符）

`OPTIONS` 已由 `inject()` 注入，新增子对象即可（`_SCRIPT_KEYS` 已含 `options`，`</` 转义现成）：

```js
const FB   = (OPTIONS && OPTIONS.feedback) || null;        // {repo, dataset, key, altKey}
const FEEDBACK = !!(FB && FB.repo);
```

- `options.feedback` 骨架来自数据 JSON（案例自描述）；
- `repo` 由 CLI `--feedback-repo` / env / JSON 三级取值后合并写入（§5）；
- 无 `feedback` 或 `repo` 为空 → `FEEDBACK=false` → 按钮不渲染（既有页面零变更）。

### 4.3 字段上下文（O1）

- `openSplitAt(idx)` → `openSplitAt(idx, colKey)`；调用点 3 处（v1.2 / HG-SEC-123 更正）：
  pills 格（`onCellClick='split'`）、普通格（`onCellClick === 'split'`）、**首列默认分栏**
  （`col === firstKeyCol`，非 onCellClick 分支）；
- `activateSplit(row, idx, colKey)` 记录 `splitField = colKey || ''`；
- URL 恢复（`?split=N`）与 ▲▼ 导航、行点击入口不传列 → `splitField=''` → `field` 参数省略；
- `closeSplit()` 清空 `splitField`。

### 4.4 链接构造与打开

```js
function buildFeedbackUrl(row) { … }   // 见 §3.2；返回 '' 表示不可用
window.openFeedbackIssue = function () {
  var u = buildFeedbackUrl(splitRow);
  if (u) window.open(u, '_blank', 'noopener,noreferrer');
};
```

安全：所有值经 `encodeURIComponent`；`open` 带 `noopener,noreferrer`；`repo` 经 `json.dumps`
注入，无法闭合 JS 字符串（防注入）。

## 5. CLI 参数矩阵（html-gen.py table）

| 来源 | 参数/变量 | 优先级 | 语义 |
|:---|:---|:---|:---|
| CLI | `--feedback-repo OWNER/REPO` | 1 | 显式空串 = 禁用（同 `--favicon`） |
| env | `HTML_GEN_FEEDBACK_REPO` | 2 | 未传 CLI 时兜底 |
| 数据 JSON | `options.feedback.repo` | 3 | 案例级默认 |
| — | 均无 | — | 不注入 → 按钮不渲染 |

- 仅 `table` 子命令新增（L1）；`doc/slide/knowledge` 不动；
- 合并结果写回 `options['feedback']['repo']` 后随 `OPTIONS` 注入；
- 帮助文案与 `--github-url/--home-url/--favicon` 同风格，`--quiet` 行为不变。

## 6. .github/ISSUE_TEMPLATE 规格

### 6.1 `data-fix.yml`（通用一份，T1）

```yaml
name: 数据纠错
description: 报告案例表格中的数据错误或过时信息（页面按钮会自动填写上下文）
title: "[数据纠错] "
labels: ["data-fix"]
body:
  - type: markdown
    attributes:
      value: |
        感谢反馈！**带「请勿修改」提示的字段由页面自动填充**，如被改动将导致本条被脚本跳过。
  - { type: input, id: page,    attributes: { label: 页面, description: 请勿修改, placeholder: demos/countries-table.html }, validations: { required: true } }
  - { type: input, id: dataset, attributes: { label: 数据集, description: 请勿修改 }, validations: { required: true } }
  - { type: input, id: row,     attributes: { label: 行标识, description: 请勿修改 }, validations: { required: true } }
  - { type: input, id: row_en,  attributes: { label: 行英文标识, description: 请勿修改（可选校验） }, validations: { required: false } }
  - { type: input, id: field,   attributes: { label: 字段, description: 请勿修改（数据列 key，如 pop_wan） }, validations: { required: true } }
  - { type: input, id: current, attributes: { label: 当前值, description: 请勿修改 }, validations: { required: false } }
  - { type: textarea, id: suggested, attributes: { label: 建议值 }, validations: { required: true } }
  - { type: input, id: source,  attributes: { label: 来源, description: 权威出处链接或说明 }, validations: { required: true } }
  - { type: textarea, id: note, attributes: { label: 补充说明 }, validations: { required: false } }
```

（实施时用展开式 YAML 书写，非 flow 风格。）

### 6.2 `config.yml`

```yaml
blank_issues_enabled: false
```

### 6.3 label

`gh label create data-fix --repo imjaden/html-gen.cli --color FBCA04 --description "案例数据纠错"`（幂等：已存在则跳过）。

## 7. 同步脚本规格（scripts/countries-issue-sync.py）

### 7.1 CLI

```
python3 scripts/countries-issue-sync.py [--config scripts/feedback-targets.yaml] [--target countries]
       [--list] [--dry-run] [--apply] [--close] [--issue N] [--repo OWNER/REPO] [--json]
```

- `--list` 只列待处理 issue（编号/标题/页面/行/字段/建议值）；
- `--dry-run` 默认，打印解析结果 + before→after diff，零写盘；
- `--apply` 写回 JSON + 重建 HTML + 回评 issue（`--close` 追加关闭）；
- `--issue N` 只处理指定 issue（便于实测；**v1.2 / HG-SEC-119**：以 `gh issue view <N> --json …` 直查，
  仅返回 open 且带目标 label 的 issue——GitHub 搜索语法无 `in:number` 限定符，禁止用 `--search` 近似）；
- `--limit N` 拉取上限（默认 100）；
- 三者互斥（同 syncer 风格：`--list/--dry-run/--apply` argparse mutually exclusive group）。

### 7.2 流程

1. 读 config（`yaml.safe_load`，RIG-001 同款安全约束）→ 取目标 target；
2. 拉 issue：`gh issue list --repo <repo> --label <label> --state open --limit 100 --json number,title,body,url,createdAt`；
   **gh 调用一律 list-form + `shell=False`**（HG-SEC-110），`--json` 结构化读取而非文本解析；
3. 解析 body：按 `### ` 首现序切段（HG-SEC-115）→ 标题精确匹配 config `parse_fields` 映射回 id；
   未知段并入上一字段值（值内偶发 `###` 行不视为新段），同名字段首次生效；
4. 逐条校验（六项，任一失败 → `[跳过] <issue> 原因` 且不写盘）：
   - `page` 匹配 target（全路径或 basename 均可）；
   - `dataset` == target.dataset；
   - `row` 唯一定位：`key_field` 精确 → 退化 `alt_key`；0 或 >1 命中 → 拒绝；
   - `field` ∈ `editable` 且 ∉ `protected`（videos 永远拒绝）；
   - 类型：`types[field]=='number'` → 可 `float()`；否则非空字符串；
   - `suggested` 非空；`suggested == current` → `[跳过] 无变化`（幂等）；
5. 冲突：同一 (row, field) 多条 issue → 只取最新一条，其余 `[冲突]` 提示跳过；
6. `--apply`：读 JSON → 改目标字段 → `json.dumps(ensure_ascii=False, indent=2)`（**无尾换行**，
   与现文件逐字一致，已有往返验证）→ 写回；
7. 重建：`subprocess.run([sys.executable, 'html-gen.py', 'table', '-d', data, '-o', html] + rebuild.args, shell=False)`，
   打印 `[执行] <完整命令>`（含 `--github-url/--home-url/--feedback-repo`）；
8. 回评：`gh issue comment <n> --body "<正文>"`；`--close` 追加 `gh issue close <n>`。
   **正文含用户可控数据（字段/旧值/新值/来源），必须作为独立 argv 元素传入（list-form + shell=False），
   禁 shell=True 与字符串拼接**（HG-SEC-110，与 RIG-002 同款）。

### 7.3 输出形态

```
[列表] 待处理 2 条
  #12 demos/countries-table.html · 伊朗 · pop_wan: 9157 → 9200 (来源: …)
  #13 demos/provinces-table.html · 广东 · … (跳过: page 不匹配)
[预览] 将更新 1 字段:
  - 伊朗.pop_wan: 9157 → 9200   (#12)
[预览] 跳过 1 条:
  - #13 page 不匹配（target=countries）
[预览] 将重建 demos/countries-table.html
[提示] 使用 --apply 执行
```

### 7.4 退出码

| 码 | 含义 |
|:---|:---|
| 0 | 成功（含无待处理 / 全部跳过） |
| 1 | 校验失败清单存在、gh 调用失败、JSON 写入失败、重建失败 |
| 2 | 参数错误（未知 target / config 缺失 / 互斥参数冲突） |

### 7.5 一致性校验

启动时比对数据 JSON `options.feedback`（dataset/key/altKey）与 config target，不一致 →
`[警告]`（不阻断），提示二者需同步（复用案例接入时的主要漂移点）。

## 8. 配置规格（scripts/feedback-targets.yaml）

```yaml
targets:
  countries:
    repo: imjaden/html-gen.cli
    label: data-fix
    dataset: countries
    page: demos/countries-table.html      # basename 亦可匹配
    data: data/_countries-data.json
    html: demos/countries-table.html
    key_field: country_zh
    alt_key: country_en
    editable: [country_zh, country_en, capital_zh, capital_en, capital_lat, capital_lon,
               region_tags, area_km2, pop_wan, gdp_yi, loc_url, ethnic_groups, religions,
               area_province, pop_province, gdp_province, note]
    protected: [videos]
    types: {capital_lat: number, capital_lon: number, area_km2: number,
            pop_wan: number, gdp_yi: number}
    parse_fields: {page: 页面, dataset: 数据集, row: 行标识, row_en: 行英文标识,
                   field: 字段, current: 当前值, suggested: 建议值,
                   source: 来源, note: 补充说明}
    rebuild:
      args: ["--github-url", "https://github.com/imjaden/html-gen.cli",
             "--home-url", "https://html-gen.cli.jaden.tech/",
             "--favicon", "https://www.jaden.tech/static/img/favicon.png",
             "--feedback-repo", "imjaden/html-gen.cli"]
```

`rebuild.args` 由 config 显式持有 → 从机制上杜绝「重建漏传参数丢失 corner/home」（CL002
FIND-002 同类缺陷，2026-09-10 又在手工重建中复发过一次）。

## 9. 测试计划（tests/test_issue_feedback.py）

| 用例 | 断言 |
|:---|:---|
| TC-01 默认不渲染 | 未配置反馈（无 `options.feedback`）→ 产物未注入 `options.feedback`、分栏 header 无 `#spFeedbackBtn`。**断言口径（v1.1 / HG-SEC-112）：不断言 JS 源码无 `issues/new` 字面量**（`buildFeedbackUrl` 常驻定义，仅在 `FB_REPO` 为空时返回 `''`） |
| TC-02 传参渲染 | 传 `--feedback-repo` + JSON `options.feedback` → 分栏 header 有按钮；URL 含 `template=data-fix.yml&page=…&dataset=countries&row=…&field=…&current=…` 且编码正确 |
| TC-03 空串禁用 | `--feedback-repo ""` → 不渲染（显式禁用语义） |
| TC-04 env 兜底 | `HTML_GEN_FEEDBACK_REPO` 生效；CLI 覆盖 env |
| TC-05 列上下文 | 点 `col.onCellClick='split'` 的单元格 → URL `field` = 该列 key；行点击/URL 恢复 → 无 `field` 参数 |
| TC-06 body 解析 | fixture issue body → 9 字段全解析（含空 `row_en`/`note`） |
| TC-07 校验拒绝 | page 不匹配 / dataset 不匹配 / 字段不在白名单 / videos 保护 / 行 0 命中 / 行多命中 / 数值不可解析 → 各自 `[跳过]` 且零写盘 |
| TC-08 dry-run 零写盘 | 打印 diff，JSON 与 HTML 内容/mtime 不变 |
| TC-09 apply 写回 | 临时副本 JSON 目标字段更新；其余字段与**格式逐字不变**（round-trip 断言）；`[执行]` 含三参数（mock subprocess） |
| TC-10 幂等 | `suggested == current` → `[跳过] 无变化` |
| TC-11 冲突 | 同 (row, field) 两条 issue → 只取最新，另一条 `[冲突]` |
| TC-12 解析边界（HG-SEC-115） | 值内含 `### 来源` 行 → 不产生错位段；未知段并入上一字段 |
| TC-13 dry-run 零写盘（HG-SEC-120） | 默认模式：数据文件内容不变、不触发重建与回评 |
| TC-14 `--issue` 直查（HG-SEC-119） | 断言调用 `gh issue view`（非 `--search`）；非 open / 缺 label 不返回 |

预计 268 → ~279 tests。

## 10. 文档同步面

| 文件 | 变更 |
|:---|:---|
| `AGENTS.md` | CLI 子命令表加 `--feedback-repo`；目录结构加 `.github/`、`scripts/feedback-targets.yaml`、`scripts/countries-issue-sync.py`；测试数 |
| `README.md` / `README.zh.md` | table 参数清单补 `--feedback-repo` |
| `skills/html-gen/SKILL.md` | 参数 + 反馈通道用法；随后 `html-gen prompt --site` 重生成 `prompts/*` |
| `documents/table-template-handbook-v1.0-20260908.md` | 新增「反馈通道」章节（契约 + 脚本 + 复用） |
| `documents/html-gen-cli-handbook-v1.0-20260908.md` | L48 隐私/通用参数枚举补 `--feedback-repo`（table-only，HG-SEC-113） |
| `features.md` | CLI 参数计数 15 → 16（HG-SEC-113） |
| `.github/ISSUE_TEMPLATE/*` | 新增（§6） |
| `features.md` | 若有 CLI 参数清单则同步 |
| `review-log.md` / `.review-level.yaml` | HG-SEC 登记（ops 回填） |

## 11. 验收清单

- [ ] 模板条件渲染：未传参零变更，传参出按钮，空串禁用
- [ ] 列上下文：`openSplitAt(idx, colKey)` 三处调用 + `splitField` 生命周期（打开/导航/URL 恢复/关闭）
- [ ] CLI 三级取值（CLI > env > JSON）与 `--quiet` 兼容
- [ ] `.github/ISSUE_TEMPLATE/data-fix.yml` + `config.yml` + label `data-fix` 就位
- [ ] 脚本四态（`--list/--dry-run/--apply/--close`）+ 六类校验 + 冲突/幂等
- [ ] JSON 往返逐字（indent=2 无尾换行）；videos 列不可写
- [ ] 重建命令含 `--github-url/--home-url/--feedback-repo` 三参数并打印 `[执行]`
- [ ] countries-table 重建后：按钮在位 + corner/home 保持在位（防回归）
- [ ] `tests/test_issue_feedback.py` 全通过；全量 pytest 零回归
- [ ] 端到端实测：真实提交 1 条测试 issue → dry-run → apply → 回评（`--close`）→ 数据/产物 diff 仅目标字段
- [ ] 设计评审 + 实现审计 PASS（review 子会话）

## 12. 复用指引（U1 / T1 / S1 / V1）

| 层 | 复用成本 |
|:---|:---|
| 模板按钮 / URL 构造 / CLI 参数 | **零改动**：任意 `html-gen table` 页面重建时加 `--feedback-repo` 即得 |
| 数据 JSON | 加 `options.feedback`（dataset/key/altKey）一行；join key 随案例声明 |
| 配置 | `scripts/feedback-targets.yaml` 增一份 target（data/html/key_field/editable/protected/types/rebuild.args） |
| issue 表单 | 共用 `data-fix.yml`；`page`/`dataset` 字段承载来源，脚本按 dataset 路由 |
| 已知 join key | countries=`country_zh`、provinces=`province`、drama 系列=`strategy`/`era`（实测） |
| 不适用 | `doc / knowledge / slide` 模板无「数据行」概念，不在复用范围（L1） |
| 禁用 | 不要复用 `cache/data/_countries-data.videos.yaml` 存放本配置（会被 videos syncer 整体重写） |

## 13. 风险与边界

- **表单预填字段可被篡改** → 白名单 + 类型 + 行唯一定位三重校验；不通过只跳过不写盘；
- **误报/滥报污染数据** → 全流程人工触发（H1），`--apply` 前必有 dry-run diff 供审；
- **同字段并发反馈** → 冲突规则（取最新）+ 回评留痕，避免静默互覆；
- **videos 列双写风险** → `protected: [videos]`，视频变更仍走 `tool-table-videos-syncer.py`；
- **重建参数漂移**（corner/home 丢失类）→ `rebuild.args` 固化在 config 并由脚本打印 `[执行]` 核验；
- **URL 长度**：单字段约 160 字符，安全；
- **gh 依赖**：脚本需本机 `gh` 已登录（当前 `imjaden`，token 含 repo scope）；未登录 → exit 1 并提示。
- **口径澄清（HG-SEC-114）**：「既有页面零变更」指**视觉/行为零变更**，非产物字节级一致——新增的
  `FB_CFG/FB_REPO/buildFeedbackUrl/openFeedbackIssue` 常驻于生成 HTML；未配置 repo 时按钮不渲染。
- **activateSplit 形参覆盖（HG-SEC-117）**：`skillSplit`（layout-table.html:883/885）未传列 key，
  缺省 `''` 优雅降级；skills-list 属 U1 排除范围，不影响 countries 试点。
- **title 预填待实测（HG-SEC-118）**：URL `?title=` 能否覆盖表单 YAML 固定 `title` 存在版本差异，
  实施期以真实 issue 实测确认；若不可覆盖，则 title 恒为 `[数据纠错] `（功能不受影响）。

## 14. 修订记录

- v1.0 (2026-09-10)：HTML-GEN-CL009 首版，A1…V1 全量决策落地 + 试点方案 + 复用指引
- v1.1 (2026-09-10)：折入设计评审 HG-SEC-110..118（PASS 85/A）——repo 落 JSON（跨重建漂移根治）、
  gh list-form 显式、body 解析边界、rebuild.args 补 --favicon、TC-01 口径、文档同步面补全
- v1.2 (2026-09-10)：审计后跟进（实现审计 PASS 95/A）——文案「数据纠错」→「数据反馈」、
  `--issue` 改 `gh issue view` 直查（HG-SEC-119）、dry-run/测试卫生三项 🟢 折入、§4.3 调用点标注更正
