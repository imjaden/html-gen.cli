---
title: html-gen CLI 手册
topic: html-gen
type: summary
version: 1.0
date: 2026-09-08
author: hermes-v0.20.6(2026.8.27)
profile: dev
provider: deepseek
model: deepseek-v4-flash
tags: [html-gen, cli, prompt, prompts-site, knowledge, table, json-output, handbook, summary]
---

# html-gen CLI v1.0

> html-gen 是一个零依赖 Python CLI：把 Markdown/JSON 注入 HTML 模板，生成自包含单文件页面。本文档是 CLI/命令/数据格式/输出规则/prompt 供给与在线阅读站点的主题手册，覆盖 2026-08-06~09-02 四条闭环演进（CL003 prompt/table-knowledge 输出契约、CL004 prompt 子命令、CL007/CL008 prompt 在线阅读站点 v1/v2）。
> 内容以 2026-09-08 当前实现为准（html-gen v3.3，2026-08-28；源码 html-gen.py、skills/、prompts/、features.md、README 实测互证）；设计决策编号均可在参考文档原文找到。

## 1. 功能定位

html-gen 的 CLI 面由两条线构成：

- **模板生成**：`doc` / `slide` / `table` / `knowledge` 四型模板（B 型文档 / D 型幻灯片 / A 型数据表格 / C 型知识库），从 Markdown 或结构化 JSON 生成单文件 HTML。
- **自描述 / agent 供给**：`prompt` 把项目 `skills/` 变成可查询的「prompt 供给站」（本地文本/JSON + GitHub Pages 在线阅读站点），`demo` 提供 demo 清单与详情，`help` 在运行时给出各数据格式精确规格。

`prompt --site` 另把 skills 沉淀为**跨项目可复用站点**（html-gen → http-server.cli 同构移植先例），是 CLI 面向 AI agent 的文档化出口。

## 2. CLI 命令总表（html-gen v3.3 / 2026-08-28 实测）

```
usage: html-gen.py [-h] [--version] [--quiet]
                   {help,version,doc,slide,table,knowledge,prompt,demo} ...
```

| 子命令 | 职责 | 关键参数 | 输入 → 输出 |
|:--|:--|:--|:--|
| `help` | 显示帮助（6 主题 doc/slide/table/knowledge/prompt/demo） | `[topic]` | 文本 |
| `version` | 显示版本 | — | 文本（`html-gen v3.3 (2026-08-28)`） |
| `doc` | Markdown → B 型文档 | `-i` 必填；`-o` 可选（缺省 md 派生 `.html`）；`--title/--subtitle/--metadata` | HTML |
| `slide` | Markdown → D 型幻灯片 | `-i` 必填；`-o` 可选（md 派生 `.slide.html`） | HTML |
| `table` | JSON → A 型数据表格 | `-d` 必填；`-o` 必填（CLI 或 JSON 顶层 `output` 二选一）；`--title/--subtitle` | HTML |
| `knowledge` | JSON → C 型知识库 | `-d`/`-g`；`-o` 必填（同 table 二选一）；`--title/--subtitle/--welcome` | HTML |
| `prompt` | 输出项目 skills / 生成在线阅读站点 | `[skill]`；`--brief/--json/--site/--dir` | 文本/JSON/站点 28 文件 |
| `demo` | demo 列表与详情 | `list\|<name>`；`--rebuild` | 文本/HTML |

全局参数：`-h/--help`、`--version`、`--quiet`（仅打印生成路径，抑制统计信息）。

通用隐私参数（doc/slide/table/knowledge 等共用）：`--github-url`、`--home-url`、`--favicon` —— 默认不注入（隐私意图）；**显式传空串 `''` 禁用 env 兜底**；env 分别为 `HTML_GEN_GITHUB_URL` / `HTML_GEN_HOME_URL` / `HTML_GEN_FAVICON`。站点生成内部对所有 Namespace 字段显式 pin（`github_url=''`、`home_url=站点根`），防止操作机 env 污染入库产物（HG-SEC-100）。

### 分发与打包惯例

- 每个子命令一个 `cmd_*()` handler，`main()` dict 分发（`{'prompt': cmd_prompt, ...}`）。
- 已安装 CLI（~/.local/bin/html-gen）是 **exec 源文件 thin wrapper**，改根 `html-gen.py` 即时生效；`src/html_gen/` 打包源需重跑 `python3 scripts/build-package.py` 同步（gitignored 生成物，D7 惯例）。

## 3. 演进主线（四条闭环）

| 闭环 | 日期 | 内容 | 设计/评审 | 最终审计 |
|:--|:--|:--|:--|:--|
| CL004 | 2026-08-06~08 | `prompt` 子命令挂载 4 skills | 确认 1A 2B 3A 4A | verify PASS 100/A，89 passed（commit 8a3987b） |
| CL003 | 2026-08-29 | table/knowledge JSON 顶层 `output` 三态 | 三轮 75/B → 85/B → 100/A | 审计 PASS 100/A，235 passed（f6efacb 链） |
| CL007 | 2026-09-02 | `prompt --site` v1：B 型 doc 合集 18 文件 | 评审 PASS 85/A（HG-SEC-086..095） | 审计 PASS 100/A（HG-SEC-096..099，d4ec017） |
| CL008 | 2026-09-02 | `prompt --site` v2：C 型门户 28 文件 + 两级沉淀 | 评审 PASS 95/A（HG-SEC-100..105） | 审计 PASS 100/A（HG-SEC-106..108，479f053） |

CL 前置：CL004 → CL007 → CL008；CL003 独立并行。测试基线随演进 89 → 235 → 263 → 268（当前 `pytest --collect-only` 268 collected）。

## 4. prompt 子命令（本地供给）

```shell
html-gen prompt                      # 列出全部 skill（name + description 首行 + references/ 文件）
html-gen prompt <skill>              # skill 全文：SKILL.md + references/*.md 拼接
html-gen prompt <skill> --brief      # 摘要：description + 章节标题列表 + references 列表
html-gen prompt <skill> --json       # checkpoint 信封输出
```

- skill 不存在 → stderr 报错 + 列出可用表 + `exit 1`。
- `SKILLS_DIR = Path(__file__).resolve().parent/'skills'`（路径自定位，依赖文件位置）。
- skills/ 现挂载 8 篇（html-gen、html-gen-cli-spec、html-gen-doc、html-gen-knowledge、html-gen-slide、html-gen-table、pages-index、test-speed-optimization）+ references 3 个。
- `--json` 信封：`{status:"ok", error:"", data:...}`；无参 data 为 `[{name, description, references:[]}, ...]`；带参 data 含 `content`（含 frontmatter，与站点 JSON 不同）；不存在 → `{status:"error", error:"skill 'x' 不存在"}`。

## 5. prompt --site 在线阅读站点

```shell
html-gen prompt --site              # 生成 prompts/ 站点（默认输出仓库根 prompts/）
html-gen prompt --site --dir <path> # 输出目录覆盖（测试/临时预览；--dir '' 空串= cwd，慎用）
```

- `--site` 与 `[skill]`/`--brief`/`--json` **互斥** → stderr + exit 1。
- 生成流程：内存全量构建 → 任一读失败 fail-fast 零写盘 → 只删已知产物名（containment 语义）→ 写产物 → cmd_doc/cmd_knowledge 渲染门户 → 统计打印（`--quiet` 仅目录路径）。

### 5.1 v1 契约（CL007，18 文件）→ v2 继承

| 产物 | 说明 |
|:--|:--|
| `index.html` | 在线阅读页（v1 = B 型 doc 合集；v2 = C 型 knowledge 门户，URL 不变） |
| `{skill}.md` ×8 | 纯 markdown = strip_frontmatter(SKILL.md) 正文 + references 拼接（每 ref 前 `\n\n---\n\n## {stem}\n`） |
| `{skill}.json` ×8 | JSON 信封，与 CLI `--json` **结构同构**（键 status/error/data） |
| `all.md` | 全量合集：唯一顶层 h1 `# html-gen Prompt 合集` + 每 skill 一段（`## {skill.name}` 标题 + description 首行 + 正文删首个顶层 h1【fence-aware】） |

站点域 https://html-gen.cli.jaden.tech/prompts/（目录带尾斜杠返回 index.html 为 Pages 标准行为）。站点产物一律**剥离 YAML frontmatter**——带 frontmatter 的 .md 被 Jekyll 转换 404，无 frontmatter 原样服务（CL007 实证链）。

### 5.2 v2 门户（CL008，28 文件）

```
prompts/
├── index.html             C 型 knowledge 门户（5 tab 横向 = A表格/B文档/C知识库/D幻灯片/通用CLI）
├── _kb-groups.json        5 group 定义（_ 前缀：Jekyll 不发布，数据已内联 index.html）
├── _kb-data.json          26 条条目（skill×8 + guide×6 + case×12），字段含 kind/url/badge/section
├── kb/{skill}.html ×8     skill detail 页（cmd_doc 渲染 {skill}.md）
├── {skill}.md/.json ×16   保留，逐字不变（契约回归断言）
└── all.md                 保留，逐字不变
```

- 纵向 section：指令 CLI / 模板语法 / 使用案例；条目 = skill detail + guide 页 + 案例页（CASE_MAP：table 4 / doc 3 / knowledge 4 / slide 1；cli 组无案例维）。
- 注册表内置于 html-gen.py（SKILL_TO_GROUP / GUIDE_MAP / CASE_MAP），随 `--site` 生成 knowledge data；同 section 内按注册表顺序 append（layout-knowledge 侧栏按数据数组首现序渲染）。
- 门户 iframe 自动追加 `?sidebar=0&toolbar=0&t=`（layout-knowledge 模板层机制，doc 裸模式），零 JS 错误（审计维度 3 实证）。
- detail 页 title=skill 名、subtitle=None、Namespace 全字段 pin（github_url=''、home_url=''）。

### 5.3 维护约束

- 产物 commit 入库、勿手改；站点仅手动 `prompt --site` 生成 commit，无 cron/CI。
- **注册表漂移**：guide/demo 文件删改 → test_11 文件存在性断言兜底。
- skill 被删：known 清理集由当前 skills 计算，旧 {skill}.md/.json/kb/{skill}.html 会残留（git 跟踪 + 人工处理，HG-SEC-096）。

## 6. table/knowledge JSON 顶层 output（CL003 三态）

结构化数据 JSON 的**顶层 `output` 字段**可内嵌渲染目标（与 `--title`/`--subtitle` 平级），形成三态：

| CLI `-o` | JSON `output` | 结果 |
|:--|:--|:--|
| 显式传入 | 任意 | 用 CLI（最高优先级） |
| 未传（None） | 非空 | 用 JSON output |
| 未传 | 空/无 | stderr 中断 + `exit 1` |

```jsonc
// data 文件（结构化 dict 顶层）示例
{
  "columns": [...],
  "data": [...],
  "output": "demos/videos-table.html"   // 可选；与 CLI -o 二选一
}
```

- 中断文案（`--quiet` 下也打印，错误不静默）：
  `❌ 未指定输出文件: 请补充 -o <output.html>，或 JSON 顶层加 "output": "demos/xxx.html"`
- 中断必须位于写盘之前；简单数组格式（无元数据能力）CLI-only，同样触发中断。
- knowledge 结构化键 = `items`/`data`（与 table 的 `columns` 不同），`output` 取 dict 顶层；groups 文件不带 output。
- 路径基准 = 命令执行 cwd（与 -o 一致）；不校验 .html 后缀；不保护覆盖（与现状一致）。
- **历史坑**：旧版无 -o 时 table/knowledge 静默默认 `index.html`/`kb.html` → 覆盖错文件；argparse `default=` 两处是静默源根因位（HG-SEC-062），删除后三态才生效。doc/slide 不受影响（md 派生默认）。

## 7. 用法示例

```shell
# 模板生成快速开始
html-gen doc   -i report.md  -o report.html
html-gen slide -i slides.md  -o slides.html
html-gen table -d data.json  -o index.html
html-gen knowledge -d data.json -o kb.html

# 数据文件内嵌输出目标（批量循环免逐个 -o）
html-gen table -d data/_videos-table.json          # JSON output 决定路径
html-gen knowledge -d data/_drama-kb-data.json -g data/_drama-groups.json

# prompt 本地供给
html-gen prompt                          # 列 skills
html-gen prompt html-gen-table --brief   # 摘要
html-gen prompt html-gen --json          # JSON 信封

# prompt 在线阅读站点
html-gen prompt --site                   # 生成 prompts/（28 文件）
html-gen prompt --site --dir /tmp/pg     # 隔离目录预览

# 机器获取（GitHub Pages，curl）
curl https://html-gen.cli.jaden.tech/prompts/html-gen.md      # 单 skill markdown
curl https://html-gen.cli.jaden.tech/prompts/html-gen.json    # 单 skill JSON 信封
curl https://html-gen.cli.jaden.tech/prompts/all.md           # 全量合集
```

## 8. 关键决策（原文编号）

### 8.1 prompt CLI 挂载（CL004，solutions/html-gen-prompt-cli-design-v1.0-20260806.md）

| 编号 | 决策 |
|:--|:--|
| 1A | 载体 = 扩展 html-gen.py 加 prompt 子命令（零新增注册，与 pc 同理念） |
| 2B | 挂载范围 = html-gen-doc + html-gen-knowledge 一起补齐挂载（技能库完整） |
| 3A | 引用目录统一 references/ |
| 4A | 跨项目 prompt 模板存为 html-gen-table/references/table-demo-prompt.md |
| D1 | argparse + cmd_prompt；可选 `[skill]` + `--brief`；不存在 → stderr 列可用表 + exit 1；SKILLS_DIR 路径自定位 |
| D2 | skills 目录布局统一 references/；挂载 4 skill |
| D3 | html-gen-doc/SKILL.md 新建（源 = AGENTS.md 详解 + 总览 skill 的 CLI/md 语法） |
| D4 | html-gen-knowledge/SKILL.md 新建（沿用 ops profile 成熟版） |
| D5 | 新增 table-demo-prompt.md → `html-gen prompt table` 输出 A 型表格规范 + 可执行 prompt |
| D6 | tests/test_prompt_cmd.py 5 用例（列/全文/带 reference/不存在 exit1/--brief） |
| D7 | 文档同步（AGENTS.md CLI 表 + skills/ 挂载清单） |

### 8.2 站点 v1（CL007，solutions/html-gen-prompts-site-design-v1.0-20260902.md）

| 编号 | 决策 |
|:--|:--|
| A1 | 落地形态：生成 prompts/ 静态目录并 commit；不新增 .nojekyll |
| B3 | curl 格式：每 skill .md + .json（md 纯 markdown；json 与 CLI 信封同构） |
| C1 | 在线阅读：B 型 doc 模板渲染合集页（零新模板） |
| D1 | 生成机制：prompt 子命令扩展 `--site`（对齐 demo --rebuild） |
| E1 | 覆盖全部 8 skills + references |
| F1 | README 加「在线阅读 & curl 获取」小节（中英双份） |
| G1 | 合集形态：index.html 合集页 + 发布 all.md 供一次 curl 全量 |
| H1 | v1 不做每 skill .html（后被 CL008 H1 推翻） |
| I1 | 触发时机：仅手动生成 commit，无 cron/CI |
| （派生） | 站点产物一律剥离 YAML frontmatter |

### 8.3 站点 v2（CL008，solutions/html-gen-prompts-site-v2-design-v1.0-20260902.md，14 条目）

| 编号 | 决策 |
|:--|:--|
| A1 | 两级沉淀：html-gen skills 补 --site；另建跨项目通用 skill（cli-prompts-site） |
| B1+B3 | 通用 skill 内容：通用生成骨架 + html-gen 参考实现 + hs 移植清单 + 测试/验收要点 |
| C1 | hs 落地通道：本次只沉淀 + 打印转交 prompt（hs 项目自闭环） |
| D1 | 门户形态：/prompts/ 改 C 型 knowledge（layout-knowledge） |
| E1+E2 | {skill}.md/.json + all.md 逐字保留；门户仍 /prompts/（index.html 换 knowledge 产物） |
| F1 | 横向 tab：5 group（A 表格/B 文档/C 知识库/D 幻灯片/通用 CLI） |
| G1 | 纵向 section：指令 CLI / 模板语法 / 使用案例 |
| G1a-1 | 案例数量：每模板 2-4 个（按可用素材） |
| G1b-1 | 通用 tab 不设语法/案例维 |
| H1 | 每 skill 生成 doc detail 页 kb/{skill}.html（推翻 v1 H1） |
| I1 | 生成器内置注册表映射表（skill→group/section + guide/demo 注册表） |
| J1 | 沉淀与改造合一 CL（HTML-GEN-CL008） |
| K-1 | 产物布局：prompts/kb/{skill}.html ×8 + _kb-groups.json + _kb-data.json |
| L-1 | 通用 skill 命名 cli-prompts-site（Hermes devops 类） |

### 8.4 table/knowledge output 三态（CL003，solutions/table-knowledge-json-output-design-v1.2-20260829.md）

| 编号 | 决策 |
|:--|:--|
| 1A | 字段命名：JSON 顶层 `output`，与 CLI --output 同名、与 title/subtitle 平级 |
| 2A | 路径基准：相对命令执行 cwd；不写绝对路径 |
| 3 | 无输出中断：CLI 无 -o 且 JSON 无 output → 提示 + exit 1（废除静默默认） |
| 4A | 覆盖保护：不保护；.html 后缀不校验 |
| 5 | 批量配套：文档补场景说明 + 循环示例；不加 --all 参数 |
| 6 | 退出码 exit 1（对齐「数据文件不存在」语义） |
| 7 | knowledge 只认 data 文件的 output（groups 文件不带） |
| 8 | 后缀校验：不校验 .html 后缀 |
| 9 | `-o` 描述改「必填（CLI 或 JSON output 二选一）」 |

## 9. 已知坑

| # | 坑 | 说明/出处 |
|:--|:--|:--|
| P1 | Jekyll 对 frontmatter 的 .md 返回 404 | 站点产物必须剥离 frontmatter；无 frontmatter 原样服务（CL007 实证） |
| P2 | doc 渲染注入分钟粒度时间戳 meta | st_ctime/st_mtime → 跨分钟生成字节不同；幂等断言限确定性文件集，index/kb 类页改结构断言（HG-SEC-086/103） |
| P3 | h1 计数/删除必须 fence-aware | 3 个 skill 正文围栏内含 `# ` 注释行，朴素 `^# ` 误计；实现 `_fence_top_h1_indices`（HG-SEC-087） |
| P4 | --dir 清理只删已知产物名 | 勿 rm -rf（containment，HG-SEC-088）；`--dir ''` 空串 → cwd 且仓库根 index.html 在 known 集（HG-SEC-098，守卫未落实待核） |
| P5 | github_url 显式空串禁用 env | or 链回退会重开隐私泄露面（HG-SEC-090/097）；站点生成 Namespace 全字段 pin |
| P6 | table/knowledge 无 -o 不再静默 | 静默默认已废除；无 -o 且 JSON 无 output 必中断 exit 1（CL003）；`data/_demos-data.json` 手工调用将中断 = 预期行为变更 |
| P7 | argparse default 是静默双源 | 改输出语义须同时删 argparse `default=`（HG-SEC-062 教训） |
| P8 | knowledge url 优先于 desc | C 型条目带 url → desc 不在门户 UI 渲染（注册表元数据语义，HG-SEC-101）；iframe 自动裸模式 `?sidebar=0&toolbar=0&t=` |
| P9 | `_kb-*.json` 下划线前缀不发布 | Pages 404 预期，数据已内联 index.html，勿误作外部数据源（HG-SEC-105） |
| P10 | 注册表漂移 | 条目文件删改 → test_11 Path 存在性断言兜底 |
| P11 | section 排序依赖首现序 | layout-knowledge 按数据数组 section 首现序渲染（HG-SEC-102） |
| P12 | YAML 多行 description 截断 | `_skill_desc` 只取首行语义，摘要截断记录不修（HG-SEC-095） |
| P13 | output 父目录不存在 | Path.write_text FileNotFoundError traceback（-o 既有行为，P2 可选增强） |
| P14 | 已装 CLI 与 src/ 打包源双份 | 改根 html-gen.py 即时生效；src/ 需 build-package.py 同步（D7） |
| P15 | AGENTS.md 文本滞后 | prompt 段仍「18 文件」、测试计数 247 vs 实测 268（HG-SEC-106 未闭环，遗留） |

## 10. 待办 / 遗留

- AGENTS.md prompt 段 18→28、目录树 prompts/ 行、测试计数 247→268（HG-SEC-106，未闭环）。
- push 后 curl 实测：.md/.json MIME、门户/kb detail 200、契约回归（验收项，用户 push 后执行）。
- HG-SEC-097 env-set 回归测试、HG-SEC-098 --dir 空串守卫：可选未落实。
- skills/html-gen frontmatter 2.4.0 vs 变更记录 v2.5.0 版本口径待核。

## 11. 参考文档

- 保留原位：features.md（功能清单）、skills/（html-gen-cli-spec 等 8 篇）、prompts/（生成产物）、review-log.md / .review-level.yaml（历史记录，不追改）。
- 本族过程文档（18 份）待归档 → `documents/archive/{solutions,root,review}-20260908/`（以执行批次实际日期为准）：

| 素材 | 原位路径 | 归档桶 |
|:--|:--|:--|
| prompt CLI 设计 v1.0（CL004） | documents/solutions/html-gen-prompt-cli-design-v1.0-20260806.md | solutions |
| prompt CLI 验证项 | documents/verify-prompt-prompt-cli-20260808.md | root |
| 站点 v1 设计（CL007） | documents/solutions/html-gen-prompts-site-design-v1.0-20260902.md | solutions |
| 站点 v1 设计评审 / 实现审计 / process prompt ×3 | documents/review/html-gen-prompts-site-{design-review-v1.0,impl-audit-v1.0,design-review-prompt,dev-impl-prompt,impl-audit-prompt}-20260902.md | review |
| 站点 v2 设计（CL008） | documents/solutions/html-gen-prompts-site-v2-design-v1.0-20260902.md | solutions |
| 站点 v2 设计评审 / 实现审计 / process prompt ×2 | documents/review/html-gen-prompts-site-v2-{design-review-v1.0,impl-audit-v1.0,dev-impl-prompt,impl-audit-prompt}-20260902.md | review |
| table/knowledge output 设计 v1.2（CL003） | documents/solutions/table-knowledge-json-output-design-v1.2-20260829.md | solutions |
| output 设计评审 v1.0/v1.1/v1.2 + 实现审计 | documents/review/table-knowledge-json-output-{design-review-v1.0,design-review-v1.1,design-review-v1.2,impl-audit-v1.0}-20260829.md | review |
