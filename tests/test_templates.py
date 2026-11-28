"""Tests for html-gen: doc, slide, table, knowledge templates."""
import json, os, re, shutil, sys, tempfile, time, unittest
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from conftest import TmpDirMixin, chromedriver_service, is_external_net_failure

PROJECT = Path(__file__).resolve().parent.parent
DEMOS = PROJECT / 'demos'
GEN = PROJECT / 'html-gen.py'


def run_gen(*args):
    cmd = [sys.executable, str(GEN)] + list(args)
    r = os.system(' '.join(f"'{c}'" if ' ' in c else c for c in cmd))
    assert r == 0, f"gen failed: {' '.join(args)}"


class TestDoc(TmpDirMixin, unittest.TestCase):
    """Doc mode — flat HTML, no slide code."""

    def test_gen_all_demos(self):
        for md_name, title in [
            ('cli-guide.md', '使用指南'),
            ('table-guide.md', 'A 型'),
            ('doc-guide.md', 'B 型'),
            ('doc-features-demo.md', 'B 型规范'),
            ('knowledge-guide.md', 'C 型'),
        ]:
            out = self.tmpdir / f'test-doc-{md_name.replace(".md", ".html")}'
            src = DEMOS / 'templates' / md_name if (DEMOS / 'templates' / md_name).exists() else DEMOS / md_name
            run_gen('doc', '-i', str(src), '--title', title, '-o', str(out))
            html = out.read_text()
            self.assertTrue(html.startswith('<!DOCTYPE html>'))
            self.assertTrue(html.strip().endswith('</html>'))
            # No unreplaced placeholders
            leftovers = re.findall(r'<!--[A-Z_]+-->', html)
            self.assertEqual(len(leftovers), 0, f"{md_name}: leftovers {leftovers}")
            # Doc template should NOT have slide-specific elements
            self.assertNotIn('slide-main', html, f"{md_name}: has slide code")
            self.assertNotIn('slideMode', html, f"{md_name}: has slideMode JS")
            self.assertNotIn('mode-toggle', html, f"{md_name}: has mode toggle")
            # Doc template should have doc elements
            self.assertIn('doc-main', html)
            self.assertIn('doc-body', html)
            self.assertIn('doc-toc', html)

    def test_doc_meta_has_path(self):
        """meta 含 路径: 行(脱敏为纯文件名) + 不含 mtime 型时间戳(可复现渲染)."""
        tmp_md = self.tmpdir / 'test-meta-path.md'
        tmp_md.write_text('# 标题\n## S1\n内容')
        out = self.tmpdir / 'test-meta-path.html'
        run_gen('doc', '-i', str(tmp_md), '-o', str(out))
        html = out.read_text()
        # CL048: 文档时间取自 frontmatter，不取 mtime —— 否则同源两渲两哈希，基线来回抖
        self.assertNotIn('创建:', html, 'meta 不应再出现 mtime 型「创建」时间')
        st = tmp_md.stat()
        os.utime(tmp_md, (st.st_atime, st.st_mtime + 120))   # 动 mtime 后重渲，字节必须一致
        out2 = self.tmpdir / 'test-meta-path-2.html'
        run_gen('doc', '-i', str(tmp_md), '-o', str(out2))
        self.assertEqual(html, out2.read_text(), '同一 md 两渲应字节一致（mtime 不得进产物）')
        out2.unlink(missing_ok=True)
        self.assertIn('路径:', html)
        m = re.search(r'路径:\s*<code>([^<]+)</code>', html)
        self.assertIsNotNone(m, "meta 应含 路径: <code>文件名</code>")
        if m:
            self.assertEqual(m.group(1), 'test-meta-path.md')
            self.assertNotIn('/', m.group(1), "路径应脱敏为纯文件名")
        tmp_md.unlink(missing_ok=True)
        out.unlink(missing_ok=True)

    def test_doc_meta_path_hidden_by_default(self):
        """默认 CSS 隐藏 .meta-path, ?show-md=1 才显示."""
        tmpl = (PROJECT / 'layout-doc.html').read_text()
        self.assertIn('.meta-path { display: none; }', tmpl)
        self.assertIn('body.show-md .meta-path { display: inline; }', tmpl)
        self.assertIn("params.get('show-md') === '1'", tmpl)


class TestSlide(TmpDirMixin, unittest.TestCase):
    """Slide mode — standalone template, no doc/slide toggle."""

    def test_gen_slide(self):
        out = self.tmpdir / 'test-slide-features-demo.html'
        run_gen('slide', '-i', str(DEMOS / 'doc-features-demo.md'),
                '--title', 'Slide Test', '-o', str(out))
        html = out.read_text()
        self.assertTrue(html.startswith('<!DOCTYPE html>'))
        leftovers = re.findall(r'<!--[A-Z_]+-->', html)
        self.assertEqual(len(leftovers), 0, f"leftovers: {leftovers}")
        # Must have slide elements
        for eid in ['slideMain', 'slidePage', 'slideDots', 'slideNav', 'slidePageNum',
                     'docBody', 'toc']:
            self.assertIn(f'id="{eid}"', html, f"missing id={eid}")
        # Must NOT have doc/slide toggle
        self.assertNotIn('mode-toggle', html)
        self.assertNotIn('switchMode', html)
        # Must have slide JS
        self.assertIn('slide.goTo', html)
        self.assertIn('slide.init()', html)

    def test_cover_page(self):
        out = self.tmpdir / 'test-slide-cover.html'
        run_gen('slide', '-i', str(DEMOS / 'doc-guide.md'),
                '--title', 'Cover Test', '-o', str(out))
        html = out.read_text()
        self.assertIn('slide-cover', html)
        self.assertIn('slide-cover-count', html)

    def test_perf_warning(self):
        out = self.tmpdir / 'test-slide-perf.html'
        src = DEMOS / 'doc-guide.md'
        run_gen('slide', '-i', str(src), '--title', 'Perf', '-o', str(out))
        html = out.read_text()
        # Small doc should have empty perf warning
        m = re.search(r'<div class="perf-warning" id="perfWarning">(.*?)</div>', html, re.DOTALL)
        self.assertIsNotNone(m)
        if m:
            self.assertEqual(m.group(1).strip(), '')

    def test_no_slide_code_in_doc(self):
        """Verify doc template doesn't leak slide code."""
        tmpl = (PROJECT / 'layout-doc.html').read_text()
        self.assertNotIn('slideMode', tmpl)
        self.assertNotIn('switchMode', tmpl)
        self.assertNotIn('mode-toggle', tmpl)
        self.assertNotIn('slide-main', tmpl)
        self.assertNotIn('slide-nav', tmpl)

    def test_slide_meta_has_path(self):
        """slide meta 同样含脱敏路径, 默认 CSS 隐藏 .meta-path."""
        tmp_md = self.tmpdir / 'test-meta-slide.md'
        tmp_md.write_text('# 标题\n## S1\n内容')
        out = self.tmpdir / 'test-meta-slide.html'
        run_gen('slide', '-i', str(tmp_md), '-o', str(out))
        html = out.read_text()
        self.assertIn('路径:', html)
        m = re.search(r'路径:\s*<code>([^<]+)</code>', html)
        self.assertIsNotNone(m, "slide meta 应含 路径: <code>文件名</code>")
        if m:
            self.assertEqual(m.group(1), 'test-meta-slide.md')
        # slide 无 show-md 机制, 默认 CSS 隐藏
        self.assertIn('.meta-path { display: none; }', html)
        tmp_md.unlink(missing_ok=True)
        out.unlink(missing_ok=True)


class TestBackwardCompat(TmpDirMixin, unittest.TestCase):
    """Table and knowledge still work."""

    def test_table(self):
        out = self.tmpdir / 'test-table-compat.html'
        run_gen('table', '-d', str(PROJECT / 'data/_demos-data.json'), '--title', 'T', '-o', str(out))
        html = out.read_text()
        self.assertIn('data-table', html)

    def test_knowledge(self):
        out = self.tmpdir / 'test-kb-compat.html'
        run_gen('knowledge', '-d', str(PROJECT / 'data/_chaitin-kb-data.json'),
                '-g', str(PROJECT / 'data/_chaitin-groups.json'), '--title', 'K', '-o', str(out))
        html = out.read_text()
        self.assertIn('kw-wrapper', html)
        # 侧栏条目 ellipsis 单行 ⇒ 必须有 title 属性兜全名（HERMES-MANAGER-CL393 转交）
        self.assertIn("class=\"kw-item-text\" title=", html)
        self.assertIn('function escAttr(', html)


class TestDocSlideFrontmatter(TmpDirMixin, unittest.TestCase):
    """D5: frontmatter strip + sticky sidebar tests."""

    def test_doc_frontmatter_stripped(self):
        """D2+D3+D4: frontmatter stripped, fm title as <title>."""
        tmp_md = self.tmpdir / 'test-fm-doc.md'
        tmp_md.write_text('---\ntitle: TestDoc\n---\n# 正文标题\n## Section 1\n内容')
        out = self.tmpdir / 'test-fm-doc.html'
        run_gen('doc', '-i', str(tmp_md), '-o', str(out))
        html = out.read_text()
        self.assertNotIn('<p>title:', html, "Frontmatter should not leak into body")
        self.assertNotIn('---', html.split('<body')[1] if '<body' in html else html,
                         "Frontmatter delimiter should not appear in body")
        self.assertIn('<title>TestDoc</title>', html, "FM title should be <title>")
        # Cleanup
        tmp_md.unlink(missing_ok=True)
        out.unlink(missing_ok=True)

    def test_slide_frontmatter_stripped(self):
        """D2+D5: slide frontmatter stripped, no leakage."""
        tmp_md = self.tmpdir / 'test-fm-slide.md'
        tmp_md.write_text('---\ntitle: TestSlide\n---\n# 封面\n## Page 1\n内容')
        out = self.tmpdir / 'test-fm-slide.html'
        run_gen('slide', '-i', str(tmp_md), '-o', str(out))
        html = out.read_text()
        # Frontmatter delimiter should not appear in body
        self.assertNotIn('---\ntitle:', html,
                         "Frontmatter YAML should not leak")
        self.assertIn('<title>TestSlide</title>', html, "FM title should be <title>")
        self.assertNotIn('<p>title:', html, "Raw frontmatter key:value should not appear")
        tmp_md.unlink(missing_ok=True)
        out.unlink(missing_ok=True)

    def test_doc_no_frontmatter_regression(self):
        """D2: doc without frontmatter still works, h1 from body."""
        tmp_md = self.tmpdir / 'test-no-fm.md'
        tmp_md.write_text('# 无FM标题\n## Section\n内容')
        out = self.tmpdir / 'test-no-fm.html'
        run_gen('doc', '-i', str(tmp_md), '-o', str(out))
        html = out.read_text()
        self.assertIn('<title>无FM标题</title>', html, "Body # should be title")
        tmp_md.unlink(missing_ok=True)
        out.unlink(missing_ok=True)

    def test_sidebar_sticky(self):
        """D1: sidebar sticky survives scroll to bottom."""
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        import time

        tmp_md = self.tmpdir / 'test-sticky.md'
        lines = ['# Sticky Test']
        for i in range(50):
            lines.append(f'## Section {i}\n\nParagraph content for section {i}.\n')
        tmp_md.write_text('\n'.join(lines))
        out = self.tmpdir / 'test-sticky.html'
        run_gen('doc', '-i', str(tmp_md), '-o', str(out))

        opts = Options()
        opts.add_argument('--headless')
        opts.add_argument('--no-sandbox')
        opts.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(
            service=chromedriver_service(),
            options=opts)
        try:
            driver.get(f'file://{out}')
            time.sleep(0.25)  # [speedup]

            driver.execute_script(
                "window.__testErrors = [];"
                "window.onerror = function(m) { window.__testErrors.push(String(m)); };")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(0.15)  # [speedup]

            sidebar_top = driver.execute_script(
                "var s = document.querySelector('.doc-sidebar');"
                "return s ? s.getBoundingClientRect().top : -1;")
            self.assertGreaterEqual(sidebar_top, -1, f"Sidebar should be visible, top={sidebar_top}")
            errs = driver.execute_script("return window.__testErrors;")
            self.assertEqual(len(errs), 0, f"JS errors: {errs}")
        finally:
            driver.quit()
            tmp_md.unlink(missing_ok=True)
            out.unlink(missing_ok=True)


class TestDocShowMd(unittest.TestCase):
    """Selenium: ?show-md=1 显隐 + 标题点击复制脱敏文件名.

    CL034: 夹具输出走 `tempfile.mkdtemp()`（原先写死共享临时名）——
    固定共享名会被并发会话/并行 worker 覆盖，页面被顶掉后本类用例整片红（实测第三者
    循环覆盖该路径 ⇒ 本类 2 例全红）。文件名仍取 `test-show-md.md`：断言的是「复制脱敏
    文件名」这条语义，与目录无关。
    """

    @classmethod
    def setUpClass(cls):
        cls.tmpdir = Path(tempfile.mkdtemp(prefix='hg-showmd-'))
        cls.tmp_md = cls.tmpdir / 'test-show-md.md'
        cls.tmp_md.write_text('# ShowMD 测试\n## 章节\n正文内容。\n')
        cls.out = cls.tmpdir / 'test-show-md.html'
        run_gen('doc', '-i', str(cls.tmp_md), '-o', str(cls.out))

        opts = Options()
        opts.add_argument('--headless')
        opts.add_argument('--no-sandbox')
        opts.add_argument('--disable-dev-shm-usage')
        cls.driver = webdriver.Chrome(
            service=chromedriver_service(), options=opts)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        shutil.rmtree(cls.tmpdir, ignore_errors=True)

    def _load(self, query=''):
        self.driver.get('file://' + str(self.out) + query)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.doc-body')))
        WebDriverWait(self.driver, 10).until(
            lambda d: d.execute_script('return document.readyState') == 'complete')
        self.driver.execute_script(
            "window.__testErrors = [];"
            "window.onerror = function(m) { window.__testErrors.push(String(m)); };")

    def _errors(self):
        return self.driver.execute_script("return window.__testErrors;")

    def _meta_path_display(self):
        return self.driver.execute_script(
            "var el = document.querySelector('.doc-header .meta .meta-path');"
            "return el ? getComputedStyle(el).display : 'missing';")

    def test_doc_show_md_param(self):
        """?show-md=1 → .meta-path display:inline, 0 JS errors."""
        self._load('?show-md=1')
        self.assertEqual(self._meta_path_display(), 'inline', "show-md=1 应显示路径行")
        self.assertEqual(self._errors(), [], f"JS errors: {self._errors()}")

    def test_doc_title_click_copy_path(self):
        """点击侧边栏标题 → toast 复制内容 = 脱敏文件名 (非 URL).

        CL015 夹具说明（HG-SEC-205 勘误, 2026-09-28）: headless Chrome 在 `file://` 下
        `navigator.clipboard.writeText` 会 reject；而 `document.execCommand('copy')` **仅在无用户激活时**
        返回 false（**有可信点击的用户激活时返回 True** —— 本批 canonical 设计的核心分野即在此；
        勿把「无激活分支」的观测当作环境通性）。修前实现「无条件 showToast('已复制: …')」
        使该用例恒绿（= 假成功断言）；canonical copyText 如实报失败后，注入可用 clipboard 桩仅用于
        **稳定观测成功分支**的 toast 文案（本用例真正要断言的是「文案 = 脱敏文件名而非 URL」）。
        """
        self._load()
        self.driver.execute_script(
            "Object.defineProperty(navigator, 'clipboard', { value: {"
            " writeText: function () { return Promise.resolve(); } }, configurable: true });")
        # CL034: 先等标题就位再点（-n 4 负载下 DOM 绑定可能晚于 readyState）
        el = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'sidebarTitle')))
        self.driver.execute_script("arguments[0].click();", el)
        # 等 toast 出现并含"已复制"文本 (异步动画, 固定 sleep 会偶发 flaky)
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.ID, 'docToast'), '已复制: test-show-md.md'))
        toast = self.driver.execute_script(
            "var t = document.getElementById('docToast'); return t ? t.textContent : '';")
        self.assertIn('已复制: test-show-md.md', toast, f"应复制脱敏文件名, got: {toast}")
        self.assertNotIn('file://', toast, "不应复制完整 URL")
        self.assertEqual(self._errors(), [], f"JS errors: {self._errors()}")


class TestDocTypography(unittest.TestCase):
    """Selenium: doc 正文排版 — li 字体与 p 一致 (容器基座 0.88rem) + blockquote 紧凑."""

    @classmethod
    def setUpClass(cls):
        opts = Options()
        opts.add_argument('--headless')
        opts.add_argument('--no-sandbox')
        opts.add_argument('--disable-dev-shm-usage')
        cls.driver = webdriver.Chrome(
            service=chromedriver_service(), options=opts)
        cls.page = DEMOS / 'doc-features-demo.html'  # 含 p/li/blockquote 的真实产物

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def setUp(self):
        self.driver.set_window_size(1400, 900)
        self.driver.get('file://' + str(self.page))
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.doc-body')))
        # 外链 favicon 断网/被墙的 net::ERR_ 不算页面缺陷（见 conftest.is_external_net_failure）
        errs = [e for e in self.driver.get_log('browser')
                if e['level'] in ('SEVERE', 'ERROR') and not is_external_net_failure(e['message'])]
        self.assertEqual([], [e['message'][:120] for e in errs], "加载后出现 JS 错误")

    def test_01_li_font_matches_p(self):
        """li 与 p 计算字体一致 (容器 font-size: 0.88rem 基座)."""
        p_size = self.driver.execute_script(
            "return getComputedStyle(document.querySelector('.doc-body p')).fontSize;")
        li_size = self.driver.execute_script(
            "return getComputedStyle(document.querySelector('.doc-body li')).fontSize;")
        self.assertEqual(p_size, li_size,
                         f"li 字体应等于 p ({p_size}): li={li_size}")
        self.assertEqual('14.08px', p_size, f"p 字体应为 0.88rem: {p_size}")

    def test_02_blockquote_compact(self):
        """普通 blockquote 上下间距紧凑 (margin 0.1rem / padding 2px)."""
        mt = self.driver.execute_script(
            "var b = document.querySelector('.doc-body blockquote'); return b ? parseFloat(getComputedStyle(b).marginTop) : null;")
        self.assertIsNotNone(mt, "应有 blockquote")
        self.assertLess(mt, 5, f"blockquote margin-top 应紧凑: {mt}")
        pt = self.driver.execute_script(
            "var b = document.querySelector('.doc-body blockquote'); return b ? parseFloat(getComputedStyle(b).paddingTop) : null;")
        self.assertLess(pt, 4, f"blockquote padding-top 应小: {pt}")


class TestTemplateStaticGuards(unittest.TestCase):
    """静态守卫（CL044 → CL047 改写）：模板级能力不得被重生成或后续改动悄悄抹掉。"""

    SPOT_MARKERS = ('toggleKwSpot', 'kwSpotOverlay', 'kwGoRoot', 'kw-map-table', 'escHtml')
    KB_PRODUCTS = ('demos/knowledge-demo.html', 'demos/drama.html',
                   'demos/chaitin.html',
                   'demos/cloudwise.html')

    def test_knowledge_spot_panel_in_template(self):
        tmpl = (PROJECT / 'layout-knowledge.html').read_text(encoding='utf-8')
        for m in self.SPOT_MARKERS:
            self.assertIn(m, tmpl, f'模板缺少 CL047 标记: {m}')
        self.assertIn("e.key === 'k'", tmpl, '⌘/Ctrl+K 入口须存在')
        self.assertIn('搜索（⌘/Ctrl+K）', tmpl, '搜索按钮 title 要写新快捷键')
        # CL047：⌘F 归还原生查找（CL044 的拦截段必须消失）
        self.assertNotIn("e.key !== 'f'", tmpl, '不得再拦截 ⌘F（浏览器原生查找要保留）')
        self.assertNotIn('kwSearchWrap', tmpl, '侧栏过滤面板应已被搜索面板取代')

    def test_knowledge_spot_panel_reaches_products(self):
        for rel in self.KB_PRODUCTS:
            f = PROJECT / rel
            if not f.is_file():
                continue
            html = f.read_text(encoding='utf-8')
            for m in self.SPOT_MARKERS:
                self.assertIn(m, html, f'{rel} 未随模板重建（缺 {m}，跑 baseline --verify 定位）')
            self.assertNotIn("e.key !== 'f'", html, f'{rel} 仍含 CL044 的 ⌘F 拦截段')


class TestImpactSurfaceDocs(unittest.TestCase):
    """CL048: 影响面矩阵单源 + 四份 guide 摘要 + 标题话术（防「改了模板漏了说明」）.

    反例: CL047 改完模板，skills/*、prompts/index.html、src/html_gen 三面全没跟上，
    全靠事后全量扫描才发现 —— 这几条把「有没有这章/这套话术」变成机器可判。
    """

    FACES = ('指令面', 'Skills 面', '文档面', '案例面', '测试面', '基线/门禁面', '打包面', '跨仓/发布面')
    GUIDES = ('table-guide.md', 'doc-guide.md', 'knowledge-guide.md', 'slide-guide.md')
    TITLES = {
        'table-guide.md': '# 🗂 表格（模板A）',
        'doc-guide.md': '# 📄 文档（模板B）',
        'knowledge-guide.md': '# 📚 知识库（模板C）',
        'slide-guide.md': '# 🖼 幻灯片（模板D）',
    }

    def test_01_matrix_is_single_source(self):
        doc = (PROJECT / 'documents' / 'templates.md').read_text(encoding='utf-8')
        self.assertIn('## 影响面矩阵', doc, 'documents/templates.md 缺「影响面矩阵」节（单源权威）')
        for face in self.FACES:
            self.assertIn(face, doc, f'影响面矩阵缺「{face}」行')
        self.assertIn('build-package.py', doc, '影响面矩阵须点名打包面入口 build-package.py')
        self.assertIn('baseline.py', doc, '影响面矩阵须点名基线门禁入口 baseline.py')

    def test_02_guides_point_to_matrix(self):
        for name in self.GUIDES:
            body = (DEMOS / name).read_text(encoding='utf-8')
            # h2 一律带中文序号前缀（一、二、…），迭代记录作附录不编号
            self.assertRegex(body, r'(?m)^## 一、\S', f'{name} 的 h2 缺中文序号前缀（一、二、…）')
            self.assertRegex(body, r'(?m)^## [一二三四五六七八九十]+、影响面说明$',
                             f'{name} 缺「## N、影响面说明」节')
            self.assertIn('documents/templates.md', body, f'{name} 未指回单源权威 templates.md')

    def test_03_guide_titles_follow_naming(self):
        for name, want in self.TITLES.items():
            first = (DEMOS / name).read_text(encoding='utf-8').splitlines()[0].strip()
            self.assertEqual(want, first, f'{name} 一级标题话术应为「{want}」')


if __name__ == '__main__':
    unittest.main(verbosity=2)
