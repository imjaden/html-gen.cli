"""html-gen prompt --site 在线阅读站点生成测试 (HTML-GEN-CL007).

统一用 --dir 临时目录, 绝不触碰仓库 prompts/ (test_08 显式断言不变)。
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

    # ── test_01 生成完整性: 18 文件 ──
    def test_01_site_generates_18_files(self):
        d = make_dir()
        try:
            r = self._run_ok(d)
            assert '18 文件' in r.stdout, f'统计行缺失: {r.stdout}'
            files = sorted(p.name for p in d.iterdir())
            expected = sorted(
                ['index.html', 'all.md']
                + [f'{s}.md' for s in EXPECTED_SKILLS]
                + [f'{s}.json' for s in EXPECTED_SKILLS])
            assert files == expected, f'文件清单不符: {files}'
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

    # ── test_05 index.html DOM 静态断言 ──
    def test_05_index_html_dom(self):
        d = make_dir()
        try:
            self._run_ok(d)
            html = (d / 'index.html').read_text(encoding='utf-8')
            # doc 模板关键元素
            assert 'doc-body' in html
            assert 'doc-sidebar' in html
            assert 'html-gen Prompt 合集' in html
            # HG-SEC-090: 无 github-corner 元素 (显式空串禁用; 正文 code fence 内
            # 文档化文本含转义 '&lt;a class="github-corner"', 须元素级断言)
            assert not re.search(r'<a[^>]*class="github-corner"', html)
            assert not re.search(r'<a[^>]*class="github-corner-hit"', html)
            # home 入口元素 + href 指向站点
            assert re.search(r'<a class="home-link" href="https://html-gen\.cli\.jaden\.tech/"',
                             html)
            # 内容已渲染 (skill 正文 h2 进入 doc TOC 内容)
            assert 'HTML 模板 CLI 生成器' in html or 'CLI 命令' in html
            assert '<!--TITLE-->' not in html and '<!--CONTENT-->' not in html
        finally:
            shutil.rmtree(d, ignore_errors=True)

    # ── test_06 幂等 (17 确定性文件 diff 为空) + containment ──
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
            deterministic = (['all.md'] + [f'{s}.md' for s in EXPECTED_SKILLS]
                             + [f'{s}.json' for s in EXPECTED_SKILLS])
            snap1 = {f: (d / f).read_bytes() for f in deterministic}
            idx1 = (d / 'index.html').read_text(encoding='utf-8')
            # 可能跨越分钟边界 → index.html 不参与字节 diff (HG-SEC-086)
            self._run_ok(d)
            for f in deterministic:
                assert (d / f).read_bytes() == snap1[f], f'{f} 幂等 diff 非空'
            idx2 = (d / 'index.html').read_text(encoding='utf-8')
            assert 'doc-body' in idx1 and 'doc-body' in idx2
            assert 'html-gen Prompt 合集' in idx1 and 'html-gen Prompt 合集' in idx2
            # containment: 无关文件保留且内容不变
            assert keep_txt.read_text(encoding='utf-8') == 'keep me'
            assert keep_md.read_text(encoding='utf-8') == '# 用户笔记\n不相关文件\n'
            assert (d / 'sub' / 'inner.txt').read_text(encoding='utf-8') == 'inner'
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
    # ── test_09 env-set pin (HG-SEC-097): 显式空串禁用 > env 兜底 ──
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

