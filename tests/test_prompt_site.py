"""html-gen prompt --site 在线阅读站点生成测试 (HTML-GEN-CL007 / CL008 v2 C 型门户).

统一用 --dir 临时目录, 绝不触碰仓库 prompts/ (test_08 显式断言不变)。

v2 (CL008): 28 文件 = 顶层 20 (index/_kb-groups/_kb-data/all.md/16) + kb/ 8 detail;
index.html 由 B 型 doc 合集改为 C 型 knowledge 门户 (5 tab)。

"""
import json, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
GEN = PROJECT / 'html-gen.py'
SKILLS = PROJECT / 'skills'

EXPECTED_SKILLS = [
    'html-gen', 'html-gen-cli-spec', 'html-gen-doc', 'html-gen-knowledge',
    'html-gen-slide', 'html-gen-table', 'pages-index', 'test-speed-optimization',
]

# CL008 v2: 顶层 20 = index + all.md + _kb-groups/_kb-data json + 16 md/json
EXPECTED_TOP = (['index.html', 'all.md', '_kb-groups.json', '_kb-data.json']
                + [f'{s}.md' for s in EXPECTED_SKILLS]
                + [f'{s}.json' for s in EXPECTED_SKILLS])
EXPECTED_KB = [f'{s}.html' for s in EXPECTED_SKILLS]

# 门户 5 tab (label 断言; groups 定义见设计 §4.1)
EXPECTED_TAB_LABELS = ['A 表格', 'B 文档', 'C 知识库', 'D 幻灯片', '通用 CLI']

# html-gen-slide / html-gen-table 的 references (HG-SEC-089: 共 3 个)
REFS_BY_SKILL = {
    'html-gen-slide': ['selenium-h3-toggle-testing', 'slide-mode-null-guards'],
    'html-gen-table': ['table-demo-prompt'],
}
# references 原文的关键内容标记 (test_04 "原文出现在对应段"; 取 ref 正文中段, 避开被
# all.md 剥离的 ref 首行 `# 标题`)
REF_CONTENT_MARKS = {
    'selenium-h3-toggle-testing': 'H3 Toggle Visibility Test',
    'slide-mode-null-guards': 'buildDots',
    'table-demo-prompt': '自包含 HTML 数据表格页',
}

# kb detail 页正文关键标记 (test_12 抽样 html-gen / html-gen-table)
KB_DETAIL_MARKS = {
    'html-gen': '四型总览',
    'html-gen-table': '何时使用',
}


def run_site(*extra, timeout=120):
    """subprocess 运行 html-gen prompt --site [extra...]."""
    return subprocess.run([sys.executable, str(GEN), 'prompt', '--site'] + list(extra),
                          capture_output=True, text=True, timeout=timeout)


def make_dir():
    return Path(tempfile.mkdtemp(prefix='_tmp_prompt_site_'))


def strip_fm(text):
    """与 html-gen.py strip_frontmatter 同语义."""
    if text.startswith('---'):
        m = re.match(r'^---\n.*?\n---\n?', text, re.DOTALL)
        if m:
            return text[m.end():]
    return text


def refs_for(name):
    d = SKILLS / name / 'references'
    if not d.is_dir():
        return []
    return [p.stem for p in sorted(d.glob('*.md'))]


def fence_top_h1_count(text):
    """fence-aware: 顶层(围栏外) `# ` 行计数 (HG-SEC-087)."""
    lines = text.split('\n')
    cnt, in_code, fence_len = 0, False, 0
    for line in lines:
        m = re.match(r'^(```+)(.*)$', line)
        if m:
            ticks, rest = m.group(1), m.group(2).strip()
            num = len(ticks)
            if in_code:
                if num >= fence_len and not rest:
                    in_code, fence_len = False, 0
            else:
                in_code, fence_len = True, num
            continue
        if not in_code and line.startswith('# '):
            cnt += 1
    return cnt


class TestPromptSite:
    """prompt --site subprocess 测试 — 每用例独立临时目录."""

    def _run_ok(self, d):
        r = run_site('--dir', str(d))
        assert r.returncode == 0, f'exit={r.returncode}\nstderr={r.stderr}'
        return r

    # ── test_01 生成完整性: 28 文件 (顶层 20 + kb/ 8) ──
    def test_01_site_generates_28_files(self):
        d = make_dir()
        try:
            r = self._run_ok(d)
            assert '28 文件' in r.stdout, f'统计行缺失: {r.stdout}'
            top_files = sorted(p.name for p in d.iterdir() if p.is_file())
            assert top_files == sorted(EXPECTED_TOP), f'顶层文件清单不符: {top_files}'
            kb = d / 'kb'
            assert kb.is_dir(), 'kb/ 子目录缺失'
            kb_files = sorted(p.name for p in kb.iterdir())
            assert kb_files == sorted(EXPECTED_KB), f'kb/ 文件清单不符: {kb_files}'
        finally:
            shutil.rmtree(d, ignore_errors=True)

    # ── test_02 内容逐字一致: {skill}.md 正文段 == strip(SKILL.md) ──
    def test_02_skill_md_equals_stripped_skill(self):
        d = make_dir()
        try:
            self._run_ok(d)
            for name in EXPECTED_SKILLS:
                body = strip_fm((SKILLS / name / 'SKILL.md').read_text(encoding='utf-8'))
                refs = refs_for(name)
                # §6.1: 每 reference 前 \n\n---\n\n## {stem}\n + reference 原文
                expected = body + ''.join(
                    f'\n\n---\n\n## {stem}\n'
                    f'{(SKILLS / name / "references" / f"{stem}.md").read_text(encoding="utf-8")}'
                    for stem in refs)
                got = (d / f'{name}.md').read_text(encoding='utf-8')
                assert got == expected, f'{name}.md 与 strip(SKILL.md)+refs 不一致'
            # HG-SEC-091: html-gen-slide 的 2 个 references 显式断言
            slide = (d / 'html-gen-slide.md').read_text(encoding='utf-8')
            assert '## selenium-h3-toggle-testing' in slide
            assert '## slide-mode-null-guards' in slide
            assert 'H3 Toggle Visibility Test' in slide
            # html-gen 无 references → 无 ref 段
            plain = (d / 'html-gen.md').read_text(encoding='utf-8')
            assert plain == strip_fm((SKILLS / 'html-gen' / 'SKILL.md').read_text(encoding='utf-8'))
            assert '## ' + 'table-demo-prompt' not in plain
        finally:
            shutil.rmtree(d, ignore_errors=True)

    # ── test_03 JSON 信封 ──
    def test_03_skill_json_envelope(self):
        d = make_dir()
        try:
            self._run_ok(d)
            for name in EXPECTED_SKILLS:
                doc = json.loads((d / f'{name}.json').read_text(encoding='utf-8'))
                assert set(doc) == {'status', 'error', 'data'}, f'{name}.json 信封键'
                assert doc['status'] == 'ok'
                assert doc['error'] == ''
                data = doc['data']
                assert set(data) == {'name', 'content', 'references'}
                assert data['name'] == name
                body = strip_fm((SKILLS / name / 'SKILL.md').read_text(encoding='utf-8'))
                # content == 同 skill .md 正文段 (strip 后逐字一致)
                assert data['content'] == body
                assert (d / f'{name}.md').read_text(encoding='utf-8').startswith(data['content'])
                expected_refs = refs_for(name)
                assert sorted(data['references']) == expected_refs
                for stem in expected_refs:
                    raw = (SKILLS / name / 'references' / f'{stem}.md').read_text(encoding='utf-8')
                    assert data['references'][stem] == raw
        finally:
            shutil.rmtree(d, ignore_errors=True)

    # ── test_04 all.md 结构 (唯一顶层 h1 fence-aware) ──
    def test_04_all_md_structure(self):
        d = make_dir()
        try:
            self._run_ok(d)
            text = (d / 'all.md').read_text(encoding='utf-8')
            assert not text.startswith('---'), '不以 --- 开头'
            assert text.startswith('# html-gen Prompt 合集'), '首行唯一顶层 h1'
            # 8 个 ## {skill.name} 段标题 (各恰好一次)
            for name in EXPECTED_SKILLS:
                assert re.search(rf'^## {re.escape(name)}$', text, re.M), f'缺段标题 ## {name}'
                assert len(re.findall(rf'^## {re.escape(name)}$', text, re.M)) == 1
            # 唯一顶层 h1: fence-aware 计数 == 1 (HG-SEC-087)
            assert fence_top_h1_count(text) == 1, 'fence-aware 顶层 h1 计数应 == 1'
            # references 段标题 + 原文出现在对应段
            for stem, mark in REF_CONTENT_MARKS.items():
                assert re.search(rf'^## {re.escape(stem)}$', text, re.M), f'缺 ref 段 {stem}'
                assert mark in text, f'references 原文缺失: {stem}'
            # all.md 头部说明引用块
            assert '重新生成: html-gen prompt --site' in text
        finally:
            shutil.rmtree(d, ignore_errors=True)

    # ── test_05 index.html 门户 DOM (CL008: C 型 knowledge, 5 tab) ──
    def test_05_index_html_knowledge_portal_dom(self):
        d = make_dir()
        try:
            self._run_ok(d)
            html = (d / 'index.html').read_text(encoding='utf-8')
            # layout-knowledge 模板关键元素
            assert 'id="kwTabBar"' in html
            assert 'id="kwSidebar"' in html
            assert 'id="kwSectionsContainer"' in html
            # 5 tab 标签 (groups JSON 注入 GROUPS; kw-tab 渲染于 JS, 此处断言 JSON 标签文本)
            for label in EXPECTED_TAB_LABELS:
                assert label in html, f'门户缺 tab 标签: {label}'
            assert 'html-gen Prompt 站点' in html
            # HG-SEC-090: 无 github-corner 元素 (显式空串禁用)
            assert not re.search(r'<a[^>]*class="github-corner"', html)
            assert not re.search(r'<a[^>]*class="github-corner-hit"', html)
            # home 入口元素 + href 指向站点
            assert re.search(r'<a class="home-link" href="https://html-gen\.cli\.jaden\.tech/"',
                             html)
            # 无未替换占位符
            assert '<!--TITLE-->' not in html and '<!--GROUPS-->' not in html
            assert '<!--ITEMS-->' not in html and '<!--WELCOME_TEXT-->' not in html
            # 非 B 型 doc (v1 断言撤销): 门户无 doc-body 内容区
            assert 'doc-body' not in html
        finally:
            shutil.rmtree(d, ignore_errors=True)

    # ── test_06 幂等 (确定性 20 文件 byte-identical) + containment ──
    def test_06_idempotent_and_containment(self):
        d = make_dir()
        try:
            # 预置无关文件 (HG-SEC-088: 清理只删已知产物名)
            keep_txt = d / 'keep-me.txt'
            keep_txt.write_text('keep me', encoding='utf-8')
            keep_md = d / 'notes.md'
            keep_md.write_text('# 用户笔记\n不相关文件\n', encoding='utf-8')
            (d / 'sub').mkdir()
            (d / 'sub' / 'inner.txt').write_text('inner', encoding='utf-8')

            self._run_ok(d)
            # CL008: 确定性集 20 = 16 md/json + all.md + _kb json + index.html
            # (knowledge 门户无 doc meta 分钟粒度 → index.html 参与字节 diff;
            #  kb/*.html 为 doc 渲染含 doc meta → 排除, HG-SEC-086 同类)
            deterministic = sorted(EXPECTED_TOP)
            assert len(deterministic) == 20, f'确定性集应 20: {len(deterministic)}'
            snap1 = {f: (d / f).read_bytes() for f in deterministic}
            self._run_ok(d)
            for f in deterministic:
                assert (d / f).read_bytes() == snap1[f], f'{f} 幂等 diff 非空'
            # containment: 无关文件保留且内容不变 (含 kb/ 内无关文件)
            assert keep_txt.read_text(encoding='utf-8') == 'keep me'
            assert keep_md.read_text(encoding='utf-8') == '# 用户笔记\n不相关文件\n'
            assert (d / 'sub' / 'inner.txt').read_text(encoding='utf-8') == 'inner'
            kb_keep = d / 'kb' / 'keep-notes.md'
            kb_keep.write_text('kb unrelated', encoding='utf-8')
            self._run_ok(d)
            assert kb_keep.read_text(encoding='utf-8') == 'kb unrelated'
            assert len(list((d / 'kb').glob('*.html'))) == 8
        finally:
            shutil.rmtree(d, ignore_errors=True)

    # ── test_07 互斥: --site 与 skill/--brief/--json ──
    def test_07_site_exclusive(self):
        combos = [
            ['html-gen'],
            ['html-gen', '--brief'],
            ['--brief'],
            ['--json'],
            ['html-gen', '--json'],
        ]
        for extra in combos:
            r = run_site(*extra)
            assert r.returncode == 1, f'--site {extra} 应 exit 1 (got {r.returncode})'
            assert '互斥' in r.stderr, f'--site {extra} stderr 缺互斥提示: {r.stderr}'

    # ── test_08 默认目录 (仓库 prompts/) 不被测试触碰 ──
    def test_08_default_dir_untouched(self):
        repo_prompts = PROJECT / 'prompts'
        before = None
        if repo_prompts.exists():
            before = {p.name: p.read_bytes() for p in sorted(repo_prompts.iterdir())
                      if p.is_file()}
        d = make_dir()
        try:
            self._run_ok(d)
            # --dir 生成后, 仓库默认 prompts/ 应保持原状 (不存在或逐字节不变)
            if before is None:
                assert not repo_prompts.exists(), '测试不应创建仓库 prompts/'
            else:
                after = {p.name: p.read_bytes() for p in sorted(repo_prompts.iterdir())
                         if p.is_file()}
                assert after == before, '测试不应改动仓库 prompts/'
        finally:
            shutil.rmtree(d, ignore_errors=True)

    # ── test_09 env-set pin (HG-SEC-097): 显式空串禁用 > env 兜底; 含 kb 页扩展 ──
    def test_09_env_set_cannot_override_disabled(self):
        d = make_dir()
        try:
            env = dict(os.environ)
            env['HTML_GEN_GITHUB_URL'] = 'https://github.com/evil/example'
            env['HTML_GEN_HOME_URL'] = 'https://evil.example/'
            r = subprocess.run(
                [sys.executable, str(GEN), 'prompt', '--site', '--dir', str(d)],
                capture_output=True, text=True, timeout=120, env=env)
            assert r.returncode == 0, f'exit={r.returncode} stderr={r.stderr}'
            html = (d / 'index.html').read_text(encoding='utf-8')
            # github corner 仍禁用 (github_url='' 显式禁用优先于 env)
            assert not re.search(r'<a[^>]*class="github-corner"', html)
            assert 'github.com/evil' not in html
            # home 仍指向站点 (home_url 显式传站点, 不受 env 污染)
            assert 'evil.example' not in html
            assert re.search(
                r'<a class="home-link" href="https://html-gen\.cli\.jaden\.tech/"', html)
            # HG-SEC-100 扩展: 8 个 kb/{skill}.html detail 页同样零 github-corner / 零 env 污染
            for name in EXPECTED_SKILLS:
                kh = (d / 'kb' / f'{name}.html').read_text(encoding='utf-8')
                assert not re.search(r'<a[^>]*class="github-corner"', kh), f'{name} 页 corner'
                assert not re.search(r'<a[^>]*class="github-corner-hit"', kh), f'{name} 页 hit'
                assert 'github.com/evil' not in kh, f'{name} 页 env 污染'
                assert 'evil.example' not in kh, f'{name} 页 env 污染'
                # detail 页 home_url='' → 无 home 入口
                assert '<a class="home-link"' not in kh, f'{name} 页不应有 home 入口'
        finally:
            shutil.rmtree(d, ignore_errors=True)

    # ── test_10 --dir 守卫 (HG-SEC-098): 空串 / 仓库根 拒绝 ──
    def test_10_dir_guard(self):
        # 空串 --dir '' → exit 1
        r = run_site('--dir', '')
        assert r.returncode == 1, f'--dir 空串应 exit 1 (got {r.returncode})'
        assert '--dir' in r.stderr
        # 仓库根 (index.html/all.md 同名产物在 known 清理集) → exit 1
        r2 = subprocess.run(
            [sys.executable, str(GEN), 'prompt', '--site', '--dir', str(PROJECT)],
            capture_output=True, text=True, timeout=120)
        assert r2.returncode == 1, f'--dir 仓库根应 exit 1 (got {r2.returncode})'
        assert '仓库根' in r2.stderr
        # 仓库 prompts/ 未被上述误操作触碰
        assert (PROJECT / 'prompts').is_dir()

    # ── test_11 _kb-data.json schema + url 存在性 (CL008 §8) ──
    def test_11_kb_data_schema(self):
        d = make_dir()
        try:
            self._run_ok(d)
            items = json.loads((d / '_kb-data.json').read_text(encoding='utf-8'))
            assert isinstance(items, list) and len(items) == 26
            groups = json.loads((d / '_kb-groups.json').read_text(encoding='utf-8'))
            group_keys = {g['key'] for g in groups}
            assert len(groups) == 5 and group_keys == {'table', 'doc', 'knowledge',
                                                       'slide', 'cli'}
            skills_seen = []
            for it in items:
                assert set(it) == {'title', 'group', 'section', 'badge', 'desc',
                                   'url', 'kind'}, f"条目字段: {it['title']}"
                assert it['kind'] in ('skill', 'guide', 'case')
                assert it['group'] in group_keys, f"group 越界: {it['title']}"
                assert it['section'] and it['url']
                if it['kind'] == 'skill':
                    skills_seen.append(it['title'])
                    assert it['badge'] == 'Prompt'
                    assert it['url'] == f"kb/{it['title']}.html"
                    assert it['title'] in EXPECTED_SKILLS
                elif it['kind'] == 'guide':
                    assert it['badge'] == '指南'
                else:
                    assert it['badge'] == '案例'
                # url 存在性: kb/ detail 相对生成目录; ../demos/ 相对仓库 demos/ (防注册表漂移)
                if it['kind'] == 'skill':
                    assert (d / it['url']).is_file(), f"detail 缺失: {it['url']}"
                else:
                    rel = it['url'][len('../demos/'):]
                    assert (PROJECT / 'demos' / rel).is_file(), \
                        f"demos 文件缺失(注册表漂移?): {it['url']}"
            assert sorted(skills_seen) == sorted(EXPECTED_SKILLS), '8 skill 条目不齐'
            # HG-SEC-102: 同组 section 首现顺序 = 指令 CLI → 模板语法 → 使用案例
            # (cli 组: 指令 CLI → 页面规范 → 测试规范)
            expect_order = {
                'table': ['指令 CLI', '模板语法', '使用案例'],
                'doc': ['指令 CLI', '模板语法', '使用案例'],
                'knowledge': ['指令 CLI', '模板语法', '使用案例'],
                'slide': ['指令 CLI', '模板语法', '使用案例'],
                'cli': ['指令 CLI', '页面规范', '测试规范'],
            }
            for g in group_keys:
                seen = []
                for it in items:
                    if it['group'] == g and it['section'] not in seen:
                        seen.append(it['section'])
                assert seen == expect_order[g], f"{g} 组 section 顺序: {seen}"
        finally:
            shutil.rmtree(d, ignore_errors=True)

    # ── test_12 kb/{skill}.html detail 页 (CL008 §8) ──
    def test_12_kb_detail_pages(self):
        d = make_dir()
        try:
            self._run_ok(d)
            for name in EXPECTED_SKILLS:
                kh = (d / 'kb' / f'{name}.html').read_text(encoding='utf-8')
                assert 'doc-body' in kh, f'{name} detail 非 doc 渲染'
                assert f'<title>{name}</title>' in kh, f'{name} detail title != skill 名'
                # 无未替换占位符
                assert '<!--TITLE-->' not in kh and '<!--CONTENT-->' not in kh
            # 正文关键标记抽样 (与 {skill}.md 同源, cmd_doc 渲染后文本保留)
            for name, mark in KB_DETAIL_MARKS.items():
                kh = (d / 'kb' / f'{name}.html').read_text(encoding='utf-8')
                assert mark in kh, f'{name} detail 正文缺关键标记: {mark}'
                md_text = (d / f'{name}.md').read_text(encoding='utf-8')
                assert mark in md_text, f'{name}.md 源缺标记(契约同源): {mark}'
        finally:
            shutil.rmtree(d, ignore_errors=True)

    # ── test_13 契约回归显式声明 (CL008 §8: CL007 契约逐字不变) ──
    def test_13_contract_unchanged(self):
        d = make_dir()
        try:
            self._run_ok(d)
            # {skill}.md == strip(SKILL.md) + refs (抽样 html-gen/html-gen-table 全等;
            # 全量循环在 test_02/03)
            for name in ('html-gen', 'html-gen-table'):
                body = strip_fm((SKILLS / name / 'SKILL.md').read_text(encoding='utf-8'))
                expected = body + ''.join(
                    f'\n\n---\n\n## {stem}\n'
                    f'{(SKILLS / name / "references" / f"{stem}.md").read_text(encoding="utf-8")}'
                    for stem in refs_for(name))
                got = (d / f'{name}.md').read_text(encoding='utf-8')
                assert got == expected, f'契约漂移: {name}.md'
            # json 信封不变 (全量: status/error/data 键集)
            for name in EXPECTED_SKILLS:
                doc = json.loads((d / f'{name}.json').read_text(encoding='utf-8'))
                assert set(doc) == {'status', 'error', 'data'}
                assert doc['status'] == 'ok' and doc['error'] == ''
                assert set(doc['data']) == {'name', 'content', 'references'}
            # all.md 唯一顶层 h1 (fence-aware) 不变
            text = (d / 'all.md').read_text(encoding='utf-8')
            assert fence_top_h1_count(text) == 1
            assert text.startswith('# html-gen Prompt 合集')
        finally:
            shutil.rmtree(d, ignore_errors=True)
