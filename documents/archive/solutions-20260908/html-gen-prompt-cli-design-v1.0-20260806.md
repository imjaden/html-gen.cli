# html-gen prompt CLI 挂载 — 设计文档

## 版本

v1.0 (2026-08-06)

## 背景与问题来源

参考 `pc prompt` / `pc prompt document-writing-guide` 的 CLI 挂载理念（全局 CLI 内嵌 `prompt` 子命令，读取项目 skills/ 目录，将技能库变成可查询的"prompt 供给站"，供跨项目 agent 直接调取规范），将 html-gen 相关 skills 及跨项目 prompt 挂载至 `html-gen prompt`。

待确认清单问答（用户回复 1A 2B 3A 4A）定稿：

| 项 | 确认 |
|:--|:--|
| 1 载体 | A=扩展 html-gen.py 加 prompt 子命令（与 pc 同理念，零新增注册） |
| 2 挂载范围 | B=补齐 html-gen-doc + html-gen-knowledge 一起挂载（技能库完整） |
| 3 引用目录 | A=统一 references/ |
| 4 跨项目 prompt 模板 | A=存为 html-gen-table/references/table-demo-prompt.md |

## 现状（已核实）

- `html-gen` 已全局注册（~/.local/bin/html-gen → html-gen.py），子命令 doc/slide/table/knowledge
- 项目 skills/ 现有：`skills/html-gen/SKILL.md`（总览 v2.3.0）、`skills/html-gen-table/SKILL.md`（A 型表格 v2.3.0）
- html-gen-doc（B 型文档）：无独立 SKILL.md，素材在 AGENTS.md（layout-doc.html 功能详解）
- html-gen-knowledge（C 型知识库）：ops profile 有成熟技能（software-development/html-gen-knowledge，含多 group 规则/Selenium 陷阱/内容规范）
- 上轮已产出"跨项目 table demo prompt"模板（对话内），未落盘
- pc 参考实现：personal-cinema.py `cmd_prompt`（L202-256）——无参列出 skills/ 各 skill（name+description+templates+用法）；带参输出 SKILL.md 全文 + templates 拼接；--brief 输出摘要

## 目标形态

```
html-gen prompt                          # 列出 skills/ 全部 skill（name/description/references/用法）
html-gen prompt <name>                   # 输出 SKILL.md 全文 + references/ 文件拼接
html-gen prompt <name> --brief           # 输出 description + 章节标题 + references 列表
```

挂载后 skills/ 目录：

```
skills/
├── html-gen/SKILL.md                    # 已有（总览，不变）
├── html-gen-table/SKILL.md              # 已有（A 型表格 v2.3.0，不变）
│   └── references/table-demo-prompt.md  # 新增：跨项目 prompt 模板（上轮产出）
├── html-gen-doc/SKILL.md                # 新增：B 型文档规范（自 AGENTS.md 提炼）
└── html-gen-knowledge/SKILL.md          # 新增：C 型知识库规范（自 ops profile 迁移整理）
```

## 设计决策 (D)

### D1 — CLI 扩展：prompt 子命令（1A）

**改动**：`html-gen.py` 新增 `prompt` 子命令（参考 personal-cinema.py cmd_prompt，约 45 行）：

- argparse：`sub.add_parser('prompt', help='输出项目 skills 的 prompt（html-gen prompt <skill>）')`；可选位置参数 `skill`、可选 `--brief`
- `cmd_prompt(args)`：
  - 无参：遍历 `SKILLS_DIR = Path(__file__).resolve().parent / 'skills'` 下各 `*/SKILL.md`，解析 frontmatter `description`，输出 name + description + references/ 子目录文件 + `用法: html-gen prompt <name>`
  - 带参：输出 SKILL.md 全文；拼接 `references/*.md`（若存在）
  - `--brief`：输出 description + `## 章节` 标题列表 + references 列表
  - skill 不存在：stderr 报错 + 列出可用列表，exit 1
- 注册到现有 subparsers，不破坏 doc/slide/table/knowledge

**路径自定位**：`Path(__file__).resolve().parent / 'skills'`（与模板定位同模式，项目内自包含）。

### D2 — skills 目录布局（2B/3A）

- 统一 `references/` 子目录命名（3A），支持列出与拼接
- 挂载清单：html-gen（已有）、html-gen-table（已有）+ reference、html-gen-doc（新建）、html-gen-knowledge（新建）

### D3 — html-gen-doc/SKILL.md 新建

**内容来源**：AGENTS.md「layout-doc.html（B 型文档）」功能详解 + html-gen 总览 skill 的 CLI/md 语法 + frontmatter 剥离。

**结构**（对齐 html-gen-table 风格）：
- frontmatter：name/description/version(v1.0.0)/author/license/metadata.related_skills
- 概述 / 何时使用 / CLI 用法 / Markdown 语法规范（md_to_html 子集）/ 文档页特性（侧边栏 TOC、搜索、折叠、拖拽、主题、代码复制、Callout、进度条、灯箱）/ 验证清单 / 变更记录

### D4 — html-gen-knowledge/SKILL.md 新建

**内容来源**：ops profile `software-development/html-gen-knowledge/SKILL.md`（成熟，含工作流、多 group 规则、section-as-menu、Selenium 陷阱、内容规范）。

**处理**：整理 frontmatter（name/description/version v1.0.0/author/license），正文基本沿用（其内容即 html-gen 知识库构建规范，已含 AGENTS.md 未写的操作经验）。

### D5 — table-demo-prompt reference（4A）

**新增**：`skills/html-gen-table/references/table-demo-prompt.md`，内容 = 上轮产出的跨项目 prompt 模板全文（任务/背景/数据规范/列配置/tabs/options/生成命令/默认行为须知/质量要求）。

**效果**：`html-gen prompt table` 输出 A 型表格规范 + 跨项目可执行 prompt，另一个项目 agent 直接可用。

### D6 — 测试

- 新增回归测试 `tests/test_prompt_cmd.py`（subprocess 或直接调用 cmd_prompt 捕获 stdout）：
  - 无参：输出包含 html-gen-table、html-gen-doc、html-gen-knowledge、html-gen
  - `prompt html-gen-table`：输出含 "v2.3.0" 与 references/table-demo-prompt.md 内容
  - `prompt html-gen-doc`：输出含 B 型文档关键章节
  - `prompt html-gen-knowledge`：输出含 知识库构建
  - `prompt 不存在`：exit 1 + 可用列表
- 全量回归（现有 84 用例不涉及 CLI 子命令列表，预期无破坏）

### D7 — 文档同步

- `AGENTS.md`：CLI 子命令表加 `prompt`；目录结构补 skills/ 挂载清单（4 skill）
- `skills/html-gen/SKILL.md`：总览补 `html-gen prompt` 说明（可选，作为 CLI 命令之一）

## 改动文件清单

| 文件 | 改动 |
|:--|:--|
| html-gen.py | 新增 prompt 子命令 + cmd_prompt（D1） |
| skills/html-gen-table/references/table-demo-prompt.md | 新增（D5） |
| skills/html-gen-doc/SKILL.md | 新增（D3） |
| skills/html-gen-knowledge/SKILL.md | 新增（D4） |
| tests/test_prompt_cmd.py | 新增（D6） |
| AGENTS.md | CLI 表 + 目录结构同步（D7） |

## 测试规划

- test_prompt_cmd.py 5 用例（D6）
- 全量 84 + 5 = 89 通过

## 风险与兼容

- **零破坏**：prompt 为新增子命令，现有 doc/slide/table/knowledge 与生成逻辑不受影响
- **路径依赖**：SKILLS_DIR 依赖 `Path(__file__).parent`——html-gen.py 移动则路径变化（与模板定位同约束，可接受）
- **skill 内容提炼**：html-gen-doc 为首次提炼，可能遗漏细节——以 AGENTS.md 为准，后续使用中迭代（skill 维护原则）
- **profile 技能重复**：html-gen-knowledge 同时存在于 ops profile 与项目 skills/——项目内为事实源，profile 副本保留（跨项目复用场景）

## 待办清单（dev 阶段）

- [ ] D1 html-gen.py prompt 子命令实现
- [ ] D3 skills/html-gen-doc/SKILL.md 新建
- [ ] D4 skills/html-gen-knowledge/SKILL.md 迁移整理
- [ ] D5 skills/html-gen-table/references/table-demo-prompt.md 新增
- [ ] D6 tests/test_prompt_cmd.py 新建 + 全量回归
- [ ] D7 AGENTS.md 同步
- [ ] git commit（不 push）
