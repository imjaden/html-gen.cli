────────────────────────────────────────
验证 prompt — html-gen prompt CLI 挂载
────────────────────────────────────────

对 html-gen 项目 ~/CodeSpace/html-gen 验证 prompt 子命令 (D1) / skills 挂载 (D3-D5) 实现。

聚焦:
- documents/solutions/html-gen-prompt-cli-design-v1.0-20260806.md (设计方案)
- Review: PASS (100/A)
- 本 session commit: 8a3987b (dev 实现)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
检查项
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

D1 · prompt 子命令
  □ argparse 注册: sub.add_parser('prompt', help='...')
  □ 参数: skill (nargs='?') + --brief (store_true)
  □ main() 分发: {'prompt': cmd_prompt}
  □ cmd_prompt() 函数定义
  □ 无参: 列出所有 skill (desc + references + 用法)
  □ 带参不存在: 报错 + 可用列表
  □ 带参 --brief: description + 章节标题 + references
  □ 带参全文: SKILL.md 全文 + references 拼接

D3 · skills/html-gen-doc/SKILL.md
  □ YAML frontmatter (name/description/version/author)
  □ 概述 / 何时使用 / CLI 用法 / Markdown 语法 / 特性 / 验证清单 / 变更记录

D4 · skills/html-gen-knowledge/SKILL.md
  □ YAML frontmatter
  □ 数据格式 (title/group/section/url/desc) / groups 格式
  □ K2 rule: title=section → skip kw-item
  □ Selenium iframe 陷阱说明

D5 · references/table-demo-prompt.md
  □ 数据规范 (columns/data/tabs/options)
  □ 列类型 (string/number/datetime/pills/actions)
  □ 默认行为 (quickFilter 关/pillFilter 开/firstKeyCol 分栏)
  □ 生成命令 + 质量要求

D6 · 测试 test_prompt_cmd.py
  □ test_01: html-gen prompt → 4 skills 列出
  □ test_02: html-gen prompt html-gen-table → v2.3.0 + reference
  □ test_03: html-gen prompt html-gen-doc → B 型文档内容
  □ test_04: html-gen prompt 不存在 → non-zero exit
  □ test_05: html-gen prompt html-gen --brief → 章节标题

D7 · AGENTS.md 同步
  □ CLI 子命令表: prompt 行
  □ 目录树: skills/ 挂载清单 (html-gen/html-gen-table/html-gen-doc/html-gen-knowledge)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
手动验证
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  html-gen prompt                      → 列出 4 个 skill (desc + references + 用法)
  html-gen prompt html-gen-table       → 全文 + reference splice (table-demo-prompt.md)
  html-gen prompt html-gen --brief     → 摘要 (desc + 章节列表)
  html-gen prompt 不存在               → 报错 + 可用列表

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
产出
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 按治理规范逐项验证（实现是否与设计一致）
2. 报告验证结果（功能/测试/质量）
3. 若 PASS → 提示切 review role 做最终审计

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
关键路径
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  html-gen.py:L599-603            argparse + dispatch
  html-gen.py:L606-660            cmd_prompt() 函数
  skills/html-gen-doc/SKILL.md    B 型文档规范
  skills/html-gen-knowledge/SKILL.md  C 型知识库规范
  skills/html-gen-table/references/table-demo-prompt.md  跨项目模板
  tests/test_prompt_cmd.py        5 tests
  AGENTS.md                       CLI 表 + 目录树

  全量: pytest tests/ -q → 89 passed
────────────────────────────────────────
