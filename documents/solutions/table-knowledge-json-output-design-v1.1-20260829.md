# table/knowledge JSON 顶层 output 字段设计 v1.1

- 日期: 2026-08-29
- 状态: 已确认（探讨决策 1A2A3A4A5 + 1A2A3A + 1A2A 全部闭合）；v1.1 按 review 意见修订（HG-SEC-062..066）
- 类别: 功能解决方案（CLI 行为变更）

## 0. 修订记录（v1.0 → v1.1）

| 意见 | 严重度 | 处理 |
|:--|:--:|:--|
| HG-SEC-062 / RIG-1 | 🔴 | ✅ 已修：§3.4/D1/D2 增 argparse `default=` 删除点（html-gen.py:768/779）；§4 代码改动点更正为「两处 cmd + 两处 argparse default + 两处 JSON 解析分支」 |
| HG-SEC-063 / RIG-2 | 🟡 | ✅ 已修：§4 D5 文档同步清单增 `demos/usage-guide.md`（usage-guide.html 重新生成）；§3.5 补 `_demos-data.json` 手工调用行为变更提示 |
| HG-SEC-064 / RIG-3 | 🟡 | ✅ 已修：§3.4/D2 增 cmd_knowledge json_output 提取位置（L475 raw 最终化后，结构化键 items/data） |
| HG-SEC-065 / OBS-1 | 🟢 | ✅ 已修：§3.2 矩阵行 1 表述改「CLI `-o` 非空」，与 §3.1 空串语义对齐 |
| HG-SEC-066 / OBS-2 | 🟢 | ✅ 已修：§5 测试表补「knowledge `-g` groups.json + data 文件带 output 生效」组合用例 |

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
- knowledge 结构化键为 `items`/`data`（与 table 的 `columns` 不同），output 同样取 dict 顶层

### 3.2 优先级三态矩阵

| CLI -o | JSON output | 结果 |
|:--|:--|:--|
| CLI `-o` 非空（显式传入） | 任意 | 用 CLI（最高优先级，与 title/subtitle 一致） |
| 未传（argparse 缺省 None） | 非空 | 用 JSON output |
| 未传 | 空/无 | 打印提示 + exit 1 中断 |

注：CLI `-o` 空串（`-o ""`）视为未传（truthiness 判断），与 §3.1「output 空串/None 视为未提供」语义一致；
与 title（`is not None`，空串被 honored）措辞区分——output 无清空语义，空串即退化输入。

### 3.3 中断行为

- 文案（stderr，`--quiet` 下也打印——错误信息不静默）：
  `❌ 未指定输出文件: 请补充 -o <output.html>，或 JSON 顶层加 "output": "demos/xxx.html"`
- exit 1，与"数据文件不存在"（html-gen.py:397-399）同语义
- **中断必须位于写盘之前**：三态解析计算出 `out` 后、`Path(out).write_text` 之前执行 exit（当前代码结构天然满足，实施时勿改成"先写再判断"）

### 3.4 实现位置

改动点共 6 处（含 review 修正）：

1. **argparse 删除默认值（根因位，必改）**：
   - html-gen.py:768 `t.add_argument('-o', '--output', default='index.html')` → 删 `default='index.html'`（argparse 缺省为 None）
   - html-gen.py:779 `k.add_argument('-o', '--output', default='kb.html')` → 删 `default='kb.html'`
   - 不删这两个 default，`args.output` 恒为真值，三态步骤 2/3 永不触发（HG-SEC-062）
2. **cmd_table（html-gen.py:441 `out = args.output or 'index.html'`）→ 三态解析**：
   - `args.output` 非空 → 用之
   - 结构化 JSON 且 `raw.get('output')` 非空 → 用之
   - 否则打印提示 + exit 1
   - 结构化 JSON 分支（L411-421）加 `json_output = raw.get('output')`，简单数组分支 `json_output = None`
3. **cmd_knowledge（html-gen.py:484 `out = args.output or 'kb.html'`）→ 同三态**：
   - `json_output` 提取位置：在 L475 raw 最终化后（`items = raw if isinstance(raw, list) else (raw.get('items') or raw.get('data') or raw)` 之后）
     `json_output = raw.get('output') if isinstance(raw, dict) else None`；简单数组 `json_output = None`
   - knowledge 结构化键为 `items`/`data`（非 table 的 `columns`），output 取 dict 顶层即可

### 3.5 向后兼容

- 行为变更点（有意）：`html-gen table -d x.json`（无 -o 且 JSON 无 output）从"静默写 index.html"改为"中断"——防覆盖错文件
- **`data/_demos-data.json` 是无 output 的结构化 JSON**：此后**手工** `html-gen table -d data/_demos-data.json`（不带 -o）将从"静默写 index.html"变为"中断"——需求 3 的预期行为变更，D5 文档（usage-guide / AGENTS.md 批量场景说明）顺带提一句，避免误判为 bug
- cmd_demo --rebuild（html-gen.py:988 直调 cmd_table，`output=str(DEMOS_DIR/'demos-index.html')`）已传 output，零影响
- doc/slide 不受影响（md 派生默认：`md.with_suffix('.html')`，html-gen.py:313/384）
- output 指向不存在的父目录时 `Path(out).write_text` 抛 FileNotFoundError（Python traceback）——`-o` 既有行为，非本次引入，不在本次范围（后续可选增强）

## 4. 影响面分析

- 代码：6 处——两处 cmd（L441/L484）+ **两处 argparse default（L768/L779）** + 两处 JSON 解析分支（table L409-421 / knowledge L473-475）
- 测试：已实测排查 tests/ 全部 table/knowledge 子进程调用（test_templates / test_render_summary / test_corner_privacy / test_initial_hidden_split / test_videos / test_table_features `_gen_table_page`）均显式传 `-o`，**零测试依赖静默默认值**；test_demos_index.py:97/99 的「table -d data.json」仅为页面展示字符串非真实调用（页面示例可保留，若要同步需连断言一起改）
- 文档同步清单（D5）：
  - AGENTS.md：CLI 子命令节 `-o` 可选性描述 + 数据格式节补 output 字段说明 + 批量场景说明（含 _demos-data.json 行为变更提示）
  - html-gen.py HELP 文本：help table / help knowledge 的 JSON 数据格式说明补 output 字段 + `-o` 表述
  - demos/table-guide.html + demos/knowledge-guide.html（md 源 → doc 重新生成）
  - **demos/usage-guide.md → usage-guide.html（重新生成）**：table 节（:126 现写「默认 index.html」）改「必填（CLI `-o` 或 JSON `output` 二选一）」；knowledge 节（:186）同理；doc 节（:60）不受影响（md 派生默认保留）
  - README.md / README.zh.md：Commands 节 `-o` 描述
  - skills/html-gen-table/SKILL.md + html-gen-knowledge/SKILL.md：数据格式节补 output
- 无模板（layout-*.html）改动

## 5. 测试计划

新增用例（新建 tests/test_json_output.py，纯 CLI 行为，subprocess 断言）：

| 用例 | 断言 |
|:--|:--|
| CLI -o 覆盖 JSON output | 指定 CLI 路径生成，JSON output 路径不生成 |
| 无 CLI -o + JSON output 生效 | 生成到 JSON output 路径，文件存在且内容含标题 |
| 两者皆无 | exit 1 + stderr 含提示文案 |
| JSON output 空串 | 视为未提供 → exit 1 中断 |
| CLI -o 空串 | 视为未传 → JSON output 生效 / 皆无则中断 |
| --quiet + 两者皆无 | exit 1，stderr 仍打印错误 |
| knowledge 三态 | CLI 覆盖 / JSON 生效 / 皆无中断 |
| knowledge -g groups.json + data 带 output | 用 data 的 output（决策 7 完整语义） |
| knowledge groups 带 output（data 无） | 被忽略 → 中断提示 |
| 简单数组无 -o | exit 1 中断（CLI-only 语义） |
| doc/slide 不受影响 | 无 -o 时默认 md 派生路径照常生成 |

回归：全量 `python3 -m pytest tests/ -q -n 4`

## 6. 待办清单（dev 实施依据）

- D1: cmd_table 三态解析 + **argparse L768 删 `default='index.html'`**（html-gen.py:441 区域 + L409-421 加 json_output）
- D2: cmd_knowledge 三态解析 + **argparse L779 删 `default='kb.html'`** + **L475 raw 最终化后提取 json_output（isinstance(raw, dict) 判断，结构化键 items/data）**
- D3: 中断文案统一（两处共用，stderr + exit 1，写盘前）
- D4: tests/test_json_output.py 新用例（上表全量）
- D5: 文档同步（AGENTS.md / HELP / guides 含 **usage-guide.md** / README / skills）
- D6: 全量回归通过

## 7. 验证清单（ops 核查用）

1. `html-gen table -d data/_countries-data.json -o /tmp/t.html`（CLI 覆盖；该数据无 output → 用 CLI）
2. 构造临时 JSON 带 output → 无 -o 生成到 output 路径
3. 无 -o 且 JSON 无 output → exit 1 + 提示文案
4. `html-gen knowledge` 三态同上（含 -g 组合）
5. `html-gen demo --rebuild` 正常（demos-index.html 生成，不触发中断）
6. `html-gen table -d data/_demos-data.json`（手工无 -o）→ 中断提示（预期行为变更）
7. 全量 pytest 通过
