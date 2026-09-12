# feedback-targets.yaml 字段契约与校验链

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
