# html-gen prompt 在线阅读站点设计 — review报告 v1.0

> 日期: 2026-09-02
> 文件: documents/solutions/html-gen-prompts-site-design-v1.0-20260902.md
> 项目路径: /Users/jadenli/CodeSpace/html-gen.cli
> 待 push commit: fe2ee22（docs@html-gen: prompt 在线阅读站点 设计 v1.0 · HTML-GEN-CL007，kind=independent）
> review维度: 合理性 / 严格性 / 安全性

## 数据验证

| # | 验证项 | 方法 | 结果 |
|:-:|:-------|:-----|:-----|
| 1 | 8 个 skill 子目录名与 E1 清单一致 | `ls skills/` | ✅ 8/8：html-gen / html-gen-cli-spec / html-gen-doc / html-gen-knowledge / html-gen-slide / html-gen-table / pages-index / test-speed-optimization |
| 2 | skills 合计 1185 行 / references 177 行 | `cat skills/*/SKILL.md \| wc -l` + `find skills -path '*/references/*'` | ✅ 1185 / 177，与 §3 行数一致 |
| 3 | references 文件数 | `find skills -path '*/references/*' -name '*.md'` | ❌ 漂移：实际 **3 个**（html-gen-slide×2 + html-gen-table×1），§3 写「4 个」 |
| 4 | 全部 SKILL.md 带 frontmatter | `head -1 skills/*/SKILL.md` | ✅ 8/8 均 `---` 开头 |
| 5 | 全部 references 无 frontmatter | `head -1` 各 references 文件 | ✅ 3/3 均 `# ` 开头（支撑「无 frontmatter 约定」） |
| 6 | `strip_frontmatter()` 存在 | read html-gen.py:252 | ✅ 返回 `(text, fm)`，`---` 开头才剥离 |
| 7 | `cmd_doc()` 可直调 | read html-gen.py:280-346 | ✅ `input/title/subtitle/output/quiet` 必填；`corner_args/favicon_args` 对 `github_url/home_url/favicon` 用 `getattr` 兜底，缺字段不崩 |
| 8 | cmd_doc meta 嵌入文件时间戳 | read html-gen.py:311-323 | ⚠️ `创建: {stat.st_ctime} · 编辑: {stat.st_mtime}`（分钟粒度）注入 index.html |
| 9 | `cmd_prompt` 全文/--json 拼接逻辑 | read html-gen.py:916-952 | ✅ 全文=`content_text`（含 frontmatter）+`\n---\n`+`## {stem}`；--json `content`=raw（含 frontmatter） |
| 10 | `HELP_PROMPT` 无 --site | read html-gen.py:713-727 | ⚠️ `html-gen help prompt` 用法块未含 `--site` |
| 11 | SKILL.md 正文含代码块内 `# ` 行 | `grep -n '^# '` | ⚠️ html-gen 7 处 / html-gen-table 3 处 / test-speed-optimization 2 处（均在 ``` 围栏内） |
| 12 | test_prompt_cmd.py 用例数 | read tests/test_prompt_cmd.py | ✅ 5 例（§7 说「5 例」一致） |
| 13 | 设计文档 frontmatter 惯例 | `head -8` 本设计 + 3 份兄弟设计 | ✅ 无 YAML frontmatter，但与 table-videos-syncer / favicon-urlstate / table-knowledge-json-output 兄弟文档同 header 式风格，符合项目惯例 |
| 14 | 文件命名规范 | 目检文件名 | ✅ `html-gen-prompts-site-design-v1.0-20260902.md`：topic 无点/无下划线，kebab-case，v1.0 与 H1 一致 |
| 15 | commit 格式 | `git log -1` | ✅ `docs@html-gen: ...`（type@scope: subject，与项目既有 `docs@html-gen` 惯例一致） |
| 16 | 9 决策完整性 | 读 §2 决策表 | ✅ A1 B3 C1 D1 E1 F1 G1 H1 I1 全部在表，与探讨记录一致 |

## 合理性评估

| # | 项 | 评级 | 说明 |
|:-:|:---|:----:|:-----|
| 1 | 需求覆盖 | ✅ | 在线阅读（C1 index.html 合集）+ curl md（B3 {skill}.md）+ curl json（B3 {skill}.json）+ 全量 all.md（G1）+ README 小节（F1）五项全覆盖 |
| 2 | 9 决策一致性 | ✅ | §2 决策表 → §4 产物/§5 CLI/§6 内容/§9 文档 逐节映射一致，无跨节矛盾 |
| 3 | 零依赖/零新模板 | ✅ | 复用 `cmd_doc` + layout-doc.html，纯标准库，符合约束 |
| 4 | frontmatter 剥离理由 | ✅ | §3 Jekyll 实证（SKILL.md→404 / SKILL.html→200，README.md→200 text/markdown）构成完整证据链，定论「站点产物一律剥离」成立 |
| 5 | 双形态差异文档化 | ✅ | §6.5 明确「CLI 直出含 frontmatter vs 站点产物剥离」，差异仅 frontmatter 一段，README 注明 |
| 6 | all.md 结构歧义 | 🟢 HG-SEC-092 | 段标题 `## {skill.name}` 与 skill 正文 h2 同级，TOC 扁平、skill 边界与内容标题不可区分（设计 §6.3 已 acknowledge「h2/h3 进 TOC」，非阻断） |
| 7 | 「同构」措辞 | 🟢 HG-SEC-093 | §6.2「信封与 CLI --json 同构」宜限定为「结构同构（键）」，content 值剥离 frontmatter 与 CLI 直出（raw 含 frontmatter）不同，§6.5 已澄清 |

## 严格性评估

| # | 项 | 评级 | 说明 |
|:-:|:---|:----:|:-----|
| 1 | 幂等性 | 🟡 HG-SEC-086 | cmd_doc 将 all.md 的 `st_ctime/st_mtime`（分钟粒度）写入 index.html meta；两次生成若跨越分钟边界则 index.html 不同 → test_06 / 验收#6「diff 为空」**成为时间敏感的 flaky 断言** |
| 2 | h1 唯一性 | 🟡 HG-SEC-087 | 3 个 skill 正文含 ``` 围栏内 `# ` 注释行；test_04「唯一顶层 h1 计数==1」若用朴素 `^# ` 计数会误计，§6.3「删除首个 `# `」亦需 fence-aware |
| 3 | 清空输出目录 | 🟡 HG-SEC-088 | `--dir` 可指向任意目录，§5 步3「清空现有文件」无 containment；README「勿手改」是治理说明而非技术护栏 |
| 4 | 内存构建 fail-fast | ✅ | 步2 先内存全量构建、读失败即 exit 1 零写盘，先于步3 清空，避免半成品目录，顺序正确 |
| 5 | cmd_doc Namespace 构造 | ✅ | 只需 `input/output/title/subtitle/quiet`；github/home/favicon getattr 兜底，直调稳妥；`sys.exit(1)` 仅在 input 缺失触发（步4 已写 all.md，不会触发） |
| 6 | --dir 测试隔离 | ✅ | §7 统一 `--dir /tmp/...`，test_08 显式断言默认路径不写仓库，隔离充分 |
| 7 | references 文件数 | 🟢 HG-SEC-089 | §3「4 个」应为「3 个」（177 行正确），生成逻辑 glob 遍历不受影响，仅文档计数偏差 |
| 8 | test_02 覆盖缺口 | 🟢 HG-SEC-091 | 仅显式断言 html-gen-table + html-gen 的 references，html-gen-slide 的 2 个 references（selenium-h3-toggle-testing / slide-mode-null-guards）未点名，靠 test_04 泛化「references 原文出现」间接覆盖 |
| 9 | 帮助文本同步 | 🟢 HG-SEC-094 | §9 只列 README+AGENTS.md，遗漏 `HELP_PROMPT`（html-gen.py:713）；argparse `--help` 会自动列出 `--site`，README 在案，非阻断 |
| 10 | index.html env 交互 | 🟢 HG-SEC-090 | §5 未指定 favicon/github corner 的 env 兜底；cmd_doc 会注入 DEFAULT_FAVICON 且 `HTML_GEN_GITHUB_URL`/`HTML_GEN_HOME_URL` 若设则覆盖「不带」意图 |
| 11 | YAML 多行 description | 🟢 HG-SEC-095 | html-gen-slide 的 description 跨行，`_skill_desc` 只读首行 → all.md 段引述截断（继承既有 cmd_prompt 限制） |
| 12 | 验收清单可执行性 | ✅ | §8 十项均命令级可跑，curl 实测条目给出可判定 MIME 断言；#9 已把 .json MIME 不确定风险化 |

## 安全事项

- **无注入路径**：prompts/ 产物内容源为项目受控的 skills/*/SKILL.md，无外部输入进入 HTML/SQL/命令上下文；渲染走既有 `md_to_html`（安全转义）。✅
- **无凭据/无第三方依赖**：零新依赖、无 API key、无 CDN。✅

🟡 HG-SEC-088 — 清空输出目录缺乏 containment（误删风险）

`html-gen prompt --site --dir <path>` 步3「清空输出目录现有文件」把用户可控的 `<path>` 当作可全清目录。默认路径（仓库 prompts/，目录专用 + git 跟踪）安全，但 `--dir` 是面向用户/脚本的自由参数，误传 `--dir ~` 或含他人物件的目录会成批删除无关文件。README「勿手改」是文档约束，非技术护栏。

修复建议：将「清空」收敛为「只删除已知产物名」——`index.html`、`all.md`、`*.md`、`*.json`（或按 `{skill}.md/.json` 白名单），而非 `rm -rf *`/全目录删除；可选再加一道：目录非空且含非预期文件时 warn/abort。保留「skill 被删则旧产物不残留」的幂等语义（旧产物均在白名单内）。

🟡 HG-SEC-086 — index.html 时间戳致幂等 flaky（见严格性评估）

cmd_doc 将 all.md 的 `st_ctime/st_mtime`（`%Y-%m-%d %H:%M` 分钟粒度）注入 index.html meta。两次生成落在同一分钟则 diff 为空、跨分钟则非空 → test_06 / 验收#6 的「diff 为空」随时间漂移。

修复建议：幂等断言范围限定 17 个确定性文件（8 .md + 8 .json + all.md），index.html 单独断言「结构/标题/正文」而非字节 diff；或生成时 `os.utime(all.md, 固定时间戳)` 归一化 meta 源，或给 cmd_doc 传固定 metadata。推荐前者（改动最小、语义清晰）。

## 评分

| 扣分项 | 严重度 | 分值 |
|:-------|:------:|:----:|
| HG-SEC-086 幂等 flaky | 🟡 | -5 |
| HG-SEC-087 h1 fence-aware 未 pin | 🟡 | -5 |
| HG-SEC-088 清空目录无 containment | 🟡 | -5 |
| HG-SEC-089..095（7 项） | 🟢 | 0（记录） |

得分: 100 - 15 = **85 / 100 → A**

## 结论

**PASS（85/A，通过）** — 设计架构正确，三项 🟡 修正项均为非阻断实现细节（幂等断言口径 / fence-aware h1 / 清空 containment），折叠进 dev 实施即可，不阻塞开工。无 🔴 阻断项。评审通过后由 dev role 按设计文档实施，三项 🟡 以 D-item 编号折入对应实现步。

## 待确认清单

| □ | 项 | 类别 |
|:-:|:---|:-----|
| □ | HG-SEC-088 清空目录收敛为「只删已知产物名」 | 安全性 🟡 |
| □ | HG-SEC-086 幂等断言限定 17 文件（index.html 改结构断言） | 严格性 🟡 |
| □ | HG-SEC-087 明确 h1 删除/计数 fence-aware（复用 md_to_html 围栏逻辑） | 严格性 🟡 |
| □ | HG-SEC-089 §3「4 个 references」→「3 个」 | 数据 🟢 |
| □ | HG-SEC-090 §5 补 index.html favicon/github env 交互说明 | 严格性 🟢 |
| □ | HG-SEC-091 test_02 补 html-gen-slide 的 2 个 references 显式断言 | 测试 🟢 |
| □ | HG-SEC-094 §9 补 HELP_PROMPT 同步 --site | 文档 🟢 |
| □ | HG-SEC-093 §6.2「同构」限定为「结构同构」 | 文档 🟢 |
| □ | HG-SEC-095 §6.3 注明 YAML 多行 description 截断（html-gen-slide） | 文档 🟢 |
| □ | HG-SEC-092 记录 all.md TOC 扁平歧义（可选：段标题升 h1） | 结构 🟢 |
