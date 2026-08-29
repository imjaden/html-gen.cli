# table/knowledge JSON 顶层 output 字段设计 v1.0

- 日期: 2026-08-29
- 状态: 已确认（探讨决策 1A2A3A4A5 + 1A2A3A + 1A2A 全部闭合）
- 类别: 功能解决方案（CLI 行为变更）

## 1. 背景与需求

html-gen `table` / `knowledge` 子命令的输出目标目前只能通过 CLI `-o/--output` 指定；
table 无 `-o` 时静默落 `index.html`、knowledge 静默落 `kb.html`（历史坑：不带 -o 覆盖错文件）。

结构化 JSON 已支持顶层 `title` / `subtitle` 元数据（优先级 CLI > JSON > 默认，html-gen.py:420-428），
但输出目标无法内嵌。批量渲染/脚本化场景（多数据文件循环）需为每个文件单独传 `-o`，易出错。

需求：
1. table/knowledge 结构化 JSON 支持顶层 `output` 字段指定渲染目标 html
2. CLI `-o` 显式传参优先级最高（覆盖 JSON）
3. 无 `-o` 且无 JSON `output` 时打印友好提示并中断（替代静默默认值，防覆盖错文件）
4. 批量渲染场景文档化（循环示例 + 适用场景），不加 `--all` 批量参数

## 2. 决策汇总（9 项，全部确认）

| # | 决策 | 内容 |
|:--|:--|:--|
| 1A | 字段命名 | JSON 顶层 `output`，与 CLI `--output` 同名，与 title/subtitle 平级 |
| 2A | 路径基准 | 相对命令执行 cwd（与 `-o` 行为一致）；不写绝对路径（机器/目录相关） |
| 3 | 无输出中断 | CLI 无 `-o` 且 JSON 无 output → 友好提示 + exit 1 中断（不再静默 index.html/kb.html） |
| 4A | 覆盖保护 | 不保护（与现状一致），output 指向非 .html 后缀也不校验 |
| 5 | 批量配套 | 文档补充场景说明 + 循环示例；不加 `--all` 参数 |
| 6 | 退出码 | exit 1（对齐"数据文件不存在"语义） |
| 7 | 多文件源 | knowledge 只认 data 文件的 output（groups 文件不带） |
| 8 | 后缀校验 | 不校验 .html 后缀（与 4A 一致） |
| 9 | 文档表述 | `-o` 描述改"必填（CLI 或 JSON output 二选一）" |

## 3. 设计细节

### 3.1 字段形态

```json
{
  "title": "项目速查表",
  "subtitle": "共 N 条记录",
  "output": "demos/xxx.html",
  "columns": [...],
  "data": [...]
}
```

- 仅结构化格式（dict 顶层）支持；简单数组格式无元数据能力，CLI-only（同样触发中断提示）
- `output` 为空串 / None 视为未提供（无清空语义，走中断提示）

### 3.2 优先级三态矩阵

| CLI -o | JSON output | 结果 |
|:--|:--|:--|
| 显式传入 | 任意 | 用 CLI（最高优先级，与 title/subtitle 一致） |
| 未传 | 非空 | 用 JSON output |
| 未传 | 空/无 | 打印提示 + exit 1 中断 |

### 3.3 中断行为

- 文案（stderr，`--quiet` 下也打印——错误信息不静默）：
  `❌ 未指定输出文件: 请补充 -o <output.html>，或 JSON 顶层加 "output": "demos/xxx.html"`
- exit 1，与"数据文件不存在"（html-gen.py:397-399）同语义

### 3.4 实现位置

- cmd_table（html-gen.py:441 `out = args.output or 'index.html'`）→ 三态解析：
  1. `args.output` 非空 → 用之
  2. 结构化 JSON 且 `raw.get('output')` 非空 → 用之
  3. 否则打印提示 + exit 1
- cmd_knowledge（html-gen.py:484 `out = args.output or 'kb.html'`）→ 同三态
- 结构化 JSON 分支（L411-421）加 `json_output = raw.get('output')`，简单数组分支 `json_output = None`

### 3.5 向后兼容

- 行为变更点（有意）：`html-gen table -d x.json`（无 -o 且 JSON 无 output）从"静默写 index.html"改为"中断"——防覆盖错文件
- cmd_demo --rebuild（html-gen.py:988 直调 cmd_table，`output=str(DEMOS_DIR/'demos-index.html')`）已传 output，零影响
- doc/slide 不受影响（md 派生默认：`md.with_suffix('.html')`，html-gen.py:313/384）

## 4. 影响面分析

- 代码：html-gen.py 两处（cmd_table L441 / cmd_knowledge L484）+ 两处 JSON 解析分支
- 测试：grep 排查 tests/ 中不带 -o 的 table/knowledge 子进程调用（cmd_demo rebuild 已带 output 不受影响）
- 文档同步清单：
  - AGENTS.md：CLI 子命令节 `-o` 可选性描述 + 数据格式节补 output 字段说明
  - html-gen.py HELP 文本：help table / help knowledge 的 JSON 数据格式说明补 output 字段 + `-o` 表述
  - demos/table-guide.html + demos/knowledge-guide.html（md 源 → doc 重新生成）
  - README.md / README.zh.md：Commands 节 `-o` 描述
  - skills/html-gen-table/SKILL.md + html-gen-knowledge/SKILL.md：数据格式节补 output
- 无模板（layout-*.html）改动

## 5. 测试计划

新增用例（新建 tests/test_json_output.py，Selenium 不需要——纯 CLI 行为，subprocess 断言）：

| 用例 | 断言 |
|:--|:--|
| CLI -o 覆盖 JSON output | 指定 CLI 路径生成，JSON output 路径不生成 |
| 无 CLI -o + JSON output 生效 | 生成到 JSON output 路径，文件存在且内容含标题 |
| 两者皆无 | exit 1 + stderr 含提示文案 |
| JSON output 空串 | 视为未提供 → exit 1 中断 |
| --quiet + 两者皆无 | exit 1，stderr 仍打印错误 |
| knowledge 三态 | CLI 覆盖 / JSON 生效 / 皆无中断 |
| knowledge groups 带 output | 被忽略（仍走 data 文件解析/中断） |
| 简单数组无 -o | exit 1 中断（CLI-only 语义） |
| doc/slide 不受影响 | 无 -o 时默认 md 派生路径照常生成 |

回归：全量 `python3 -m pytest tests/ -q -n 4`

## 6. 待办清单（dev 实施依据）

- D1: cmd_table 三态解析（html-gen.py:441 区域 + L409-421 加 json_output）
- D2: cmd_knowledge 三态解析（html-gen.py:484 区域）
- D3: 中断文案统一（两处共用，stderr + exit 1）
- D4: tests/test_json_output.py 新用例（上表全量）
- D5: 文档同步（AGENTS.md / HELP / guides / README / skills）
- D6: 全量回归通过

## 7. 验证清单（ops 核查用）

1. `html-gen table -d data/_countries-data.json -o /tmp/t.html`（CLI 覆盖；该数据无 output → 用 CLI）
2. 构造临时 JSON 带 output → 无 -o 生成到 output 路径
3. 无 -o 且 JSON 无 output → exit 1 + 提示文案
4. `html-gen knowledge` 三态同上
5. `html-gen demo --rebuild` 正常（demos-index.html 生成，不触发中断）
6. 全量 pytest 通过
