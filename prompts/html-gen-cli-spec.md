
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

| 子指令 | 用途 | 必填参数 | 可选参数 | 输出 |
|:-------|:-----|:---------|:---------|:-----|
| `help` | 显示帮助 | — | — | 文本 |
| `doc` | Markdown → B 型文档页 | `-i/--input` | `-o/--output` `--title` `--subtitle` `--metadata` | HTML 文件 |
| `slide` | Markdown → 幻灯片 | `-i/--input` | `-o/--output` `--title` `--subtitle` | HTML 文件 |
| `table` | JSON → A 型数据表格 | `-d/--data` | `--title` `-o/--output` | HTML 文件 |
| `knowledge` | JSON → C 型知识库 | `-d/--data` | `-g/--groups` `--title` `--subtitle` `--welcome` `-o/--output` | HTML 文件 |
| `prompt` | 输出项目 skills 内容 | — | `<skill>` `--brief` `--json` | 文本 / JSON |
| `demo` | demo 列表与详情 | — | `list\|<name>` `--json` `--all` `--open` `--rebuild` | 文本 / JSON |

## 3. 参数惯例（对齐 cli-args-reference.md）

| 功能 | 参数名 | 缩写 | 说明 |
|:-----|:-------|:-----|:-----|
| 输入文件 | `--input` | `-i` | doc/slide 必填 |
| 数据文件 | `--data` | `-d` | table/knowledge 必填 |
| 输出文件 | `--output` | `-o` | 必填（CLI `-o` 或 JSON 顶层 `output` 二选一；table/knowledge） |
| 标题 | `--title` | — | 页面标题 |
| 副标题 | `--subtitle` | — | 页面副标题 |
| 分组 | `--groups` | `-g` | knowledge 分组文件 |
| JSON 输出 | `--json` | — | checkpoint 信封（见 §4） |
| 摘要 | `--brief` | — | prompt 仅输出摘要 |
| 帮助 | `--help` | `-h` | argparse 内置 |

注: `--version` 未实现（版本硬编码在 docstring「版本: 3.1(2026-07-23)」,
2026-08-19 观察项, 后续可补 argparse `--version`）。

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
