你以 dev role 在 html-gen.cli 项目实施 HTML-GEN-CL007（prompt 在线阅读站点），严格按设计文档执行。

【设计文档】
documents/solutions/html-gen-prompts-site-design-v1.0-20260902.md
（当前 HEAD 以 git log 为准；评审 PASS 85/A 折叠项 HG-SEC-086..095 已订正入设计文档）

【评审折叠项（须随实施落实，已入设计文档对应节）】
- HG-SEC-086：幂等断言限定 17 个确定性文件（8 md + 8 json + all.md）diff 为空；
  index.html 改结构/标题断言，不做字节 diff（cmd_doc meta 分钟粒度时间戳）
- HG-SEC-087：h1 删除/计数 fence-aware（3 个 skill 正文围栏内含 `# ` 注释行，
  实现复用 md_to_html 围栏解析语义）
- HG-SEC-088：清理只删已知产物名（index.html/all.md/8×{skill}.md/8×{skill}.json，
  共 18 个），其他文件保留（--dir 任意路径 containment）；测试含预置无关文件保留断言
- HG-SEC-090：cmd_doc 直调显式传 github_url=""（空串禁用防 env 覆盖）+ home_url 站点
- HG-SEC-091：test_02 显式断言 html-gen-slide 的 2 个 references
- HG-SEC-094：HELP_PROMPT（html-gen.py:713 起）同步补 --site

【需求摘要】
html-gen prompt 子命令扩展 --site：生成 prompts/ 目录（18 文件）供 GitHub Pages 原样服务，
平台可在线阅读（index.html，B 型 doc 渲染合集）+ curl 获取（每 skill .md 纯 markdown /
.json 信封 + all.md 全量）。产物一律剥离 frontmatter（Jekyll 实证依据见设计 §3/§6）。

【实施范围】
1. html-gen.py：
   - prompt 解析器加 --site / --dir 参数（html-gen.py:831-834 现有 prompt parser）
   - cmd_prompt 顶部 `if args.site:` 分支 → cmd_prompt_site(args)；互斥校验
     （--site 与 skill/--brief/--json 同传 → stderr + exit 1）
   - cmd_prompt_site：复用现有 skills 收集逻辑 + strip_frontmatter()（html-gen.py:252）
     + cmd_doc（html-gen.py:280，构造 Namespace 直调，传 title/home_url/quiet）
   - 实现要点：内存构建全部内容 → fail-fast → 清理已知产物名（18 个，无关文件保留）
     → 写 8 md + 8 json + all.md → cmd_doc 渲染 index.html（显式传 github_url="" 等，
     见折叠项 HG-SEC-090）→ 统计打印
   - 默认输出目录 = Path(__file__).resolve().parent / 'prompts'
2. tests/test_prompt_site.py 新增 8 用例（设计 §7：生成完整性/内容逐字一致/json 信封/
   all.md 结构/index DOM/幂等/互斥/默认目录隔离）——测试一律用 --dir 临时目录，绝不触碰仓库 prompts/
3. README.md + README.zh.md：prompt 命令段落后加「在线阅读 & curl 获取」小节
4. AGENTS.md：目录结构补 prompts/ 行；prompt 子命令段补 --site
5. 生成真实产物：`python3 html-gen.py prompt --site`（默认目录）→ 提交 prompts/ 18 文件

【提交规范】
- 单 commit：`feat@html-gen: prompt --site 在线阅读站点 (HTML-GEN-CL007)`
- 禁止：混入无关改动、触碰 cache/（gitignored）、git push、git checkout -- .
- prompts/ 产物与代码同 commit（产物由生成器得出，勿手改）

【完成后报告（必须附证据）】
1. git log --oneline -2 实际输出
2. git status --short 实际输出（应为干净或仅预期文件）
3. `python3 html-gen.py prompt --site --dir /tmp/prompts-verify` 实际输出 + 文件清单
4. 专项测试实际输出：python3 -m pytest tests/test_prompt_site.py tests/test_prompt_cmd.py -q
5. 全量测试：python3 -m pytest tests/ -q -n 4 实际输出（基线 255，预计 263）
6. 每个新增符号/函数的 grep 证据行（cmd_prompt_site / strip_frontmatter 调用等）

注：/usr/bin/python3 才是带 pytest 的解释器；后台 shell 会解析到 conda python（无 pytest），
测试必须前台显式 /usr/bin/python3 -m pytest 或本机 python3 验证。
