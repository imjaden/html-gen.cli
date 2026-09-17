
# html-gen CLI 规范

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

## 5. skills/ 与 profile 运行时 skill 的关系（2026-09-17 实测订正）

> ⚠️ 旧表述（「真源 = dev profile，编辑后 `cp -R` 覆盖项目副本」）**已作废** —— 与实测不符。

- 两侧是**命名相同的两套独立文档**（内容 / 版本 / 语言均不同）。实测: `html-gen-table` 仓内 209 行·中文·v2.4.0
  vs dev profile 544 行·英文·v4.0.0；`html-gen-doc` 68 行 vs 143 行；ops 侧 `html-gen-knowledge` 102 行（含「工作流 / 踩坑」段）。
  仓内副本被 `html-gen prompt` / `--site` 消费（生成 `prompts/`），profile 侧是 agent 运行时加载处。
- **同步纪律**（任何方向都必须先逐文件 diff 分类）:
  - 单向缺行（副本零独有行）= **陈旧** → 可定向 `cp`（改前 `tar` 备份 + 改后双侧 `sha256` 比对）
  - 含副本独有行 = **变体** → **禁止强行对齐**（会抹掉 profile 定制内容）
  - 副本无该文件 = 缺失 → **不新建**（除非确认该 profile 确实需要）
- 实测分布（2026-09-17）: 副本存在于 `dev` / `ops` / `summarizer` 三个 profile；`html-gen-slide/SKILL.md` 属陈旧（已同步），
  `html-gen-{table,doc}` 与 ops 的 `html-gen-knowledge` 属变体（不同步），`references/table-demo-prompt.md` 在 profile 侧不存在（不新建）；
  `~/.hermes/skills/`（default 运行时）无副本。
- ⇒ **本仓 `skills/**` 的改动不会自动传播到 profile（反之亦然）**；「两侧一致」不是不变式，勿按旧命令盲抄。

## 6. 审计入口

- `hm check cli <path>`（治理规范 CLI 规范条目）: 检查 --json 检出 +
  handle_{指令} 命名 + help/version 内置
- 本规范文件: `html-gen/skills/html-gen-cli-spec/SKILL.md`
