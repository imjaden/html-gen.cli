"""Tests for html-gen: doc, slide, table, knowledge templates."""
import json, os, re, sys, time, unittest
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

PROJECT = Path(__file__).resolve().parent.parent
DEMOS = PROJECT / 'demos'
GEN = PROJECT / 'html-gen.py'
CHROMEDRIVER = '/Users/jadenli/CodeSpace/script-miner/cache/chromedriver/chromedriver'


def run_gen(*args):
    cmd = [sys.executable, str(GEN)] + list(args)
    r = os.system(' '.join(f"'{c}'" if ' ' in c else c for c in cmd))
    assert r == 0, f"gen failed: {' '.join(args)}"


class TestDoc(unittest.TestCase):
    """Doc mode — flat HTML, no slide code."""

    def test_gen_all_demos(self):
        for md_name, title in [
            ('html-gen-usage-guide-v1.0-20260707.md', '使用指南'),
            ('template-A-guide-v1.0-20260707.md', 'A 型'),
            ('template-B-guide-v1.0-20260707.md', 'B 型'),
            ('template-B-markdown-spec-v1.0-20260707.md', 'B 型规范'),
            ('template-C-guide-v1.0-20260707.md', 'C 型'),
        ]:
            out = Path('/tmp') / f'test-doc-{md_name.replace(".md", ".html")}'
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
        """meta 含 路径: 行, 且为脱敏文件名 (不含 /)."""
        tmp_md = Path('/tmp/test-meta-path.md')
        tmp_md.write_text('# 标题\n## S1\n内容')
        out = Path('/tmp/test-meta-path.html')
        run_gen('doc', '-i', str(tmp_md), '-o', str(out))
        html = out.read_text()
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


class TestSlide(unittest.TestCase):
    """Slide mode — standalone template, no doc/slide toggle."""

    def test_gen_slide(self):
        out = Path('/tmp/test-slide-demo.html')
        run_gen('slide', '-i', str(DEMOS / 'templates' / 'template-B-markdown-spec-v1.0-20260707.md'),
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
        out = Path('/tmp/test-slide-cover.html')
        run_gen('slide', '-i', str(DEMOS / 'templates' / 'template-B-guide-v1.0-20260707.md'),
                '--title', 'Cover Test', '-o', str(out))
        html = out.read_text()
        self.assertIn('slide-cover', html)
        self.assertIn('slide-cover-count', html)

    def test_perf_warning(self):
        out = Path('/tmp/test-slide-perf.html')
        src = DEMOS / 'templates' / 'template-B-guide-v1.0-20260707.md'
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
        tmp_md = Path('/tmp/test-meta-slide.md')
        tmp_md.write_text('# 标题\n## S1\n内容')
        out = Path('/tmp/test-meta-slide.html')
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


class TestBackwardCompat(unittest.TestCase):
    """Table and knowledge still work."""

    def test_table(self):
        out = Path('/tmp/test-table-compat.html')
        run_gen('table', '-d', str(PROJECT / 'data/_demos-data.json'), '--title', 'T', '-o', str(out))
        html = out.read_text()
        self.assertIn('data-table', html)

    def test_knowledge(self):
        out = Path('/tmp/test-kb-compat.html')
        run_gen('knowledge', '-d', str(PROJECT / 'data/_chaitin-kb-data.json'),
                '-g', str(PROJECT / 'data/_chaitin-groups.json'), '--title', 'K', '-o', str(out))
        html = out.read_text()
        self.assertIn('kw-wrapper', html)


class TestDocSlideFrontmatter(unittest.TestCase):
    """D5: frontmatter strip + sticky sidebar tests."""

    def test_doc_frontmatter_stripped(self):
        """D2+D3+D4: frontmatter stripped, fm title as <title>."""
        tmp_md = Path('/tmp/test-fm-doc.md')
        tmp_md.write_text('---\ntitle: TestDoc\n---\n# 正文标题\n## Section 1\n内容')
        out = Path('/tmp/test-fm-doc.html')
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
        tmp_md = Path('/tmp/test-fm-slide.md')
        tmp_md.write_text('---\ntitle: TestSlide\n---\n# 封面\n## Page 1\n内容')
        out = Path('/tmp/test-fm-slide.html')
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
        tmp_md = Path('/tmp/test-no-fm.md')
        tmp_md.write_text('# 无FM标题\n## Section\n内容')
        out = Path('/tmp/test-no-fm.html')
        run_gen('doc', '-i', str(tmp_md), '-o', str(out))
        html = out.read_text()
        self.assertIn('<title>无FM标题</title>', html, "Body # should be title")
        tmp_md.unlink(missing_ok=True)
        out.unlink(missing_ok=True)

    def test_sidebar_sticky(self):
        """D1: sidebar sticky survives scroll to bottom."""
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        import time

        tmp_md = Path('/tmp/test-sticky.md')
        lines = ['# Sticky Test']
        for i in range(50):
            lines.append(f'## Section {i}\n\nParagraph content for section {i}.\n')
        tmp_md.write_text('\n'.join(lines))
        out = Path('/tmp/test-sticky.html')
        run_gen('doc', '-i', str(tmp_md), '-o', str(out))

        opts = Options()
        opts.add_argument('--headless')
        opts.add_argument('--no-sandbox')
        opts.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(
            service=Service('/Users/jadenli/CodeSpace/script-miner/cache/chromedriver/chromedriver'),
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
    """Selenium: ?show-md=1 显隐 + 标题点击复制脱敏文件名."""

    @classmethod
    def setUpClass(cls):
        cls.tmp_md = Path('/tmp/test-show-md.md')
        cls.tmp_md.write_text('# ShowMD 测试\n## 章节\n正文内容。\n')
        cls.out = Path('/tmp/test-show-md.html')
        run_gen('doc', '-i', str(cls.tmp_md), '-o', str(cls.out))

        opts = Options()
        opts.add_argument('--headless')
        opts.add_argument('--no-sandbox')
        opts.add_argument('--disable-dev-shm-usage')
        cls.driver = webdriver.Chrome(
            service=Service(CHROMEDRIVER), options=opts)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        cls.tmp_md.unlink(missing_ok=True)
        cls.out.unlink(missing_ok=True)

    def _load(self, query=''):
        self.driver.get('file://' + str(self.out) + query)
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.doc-body')))
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
        """点击侧边栏标题 → toast 复制内容 = 脱敏文件名 (非 URL)."""
        self._load()
        el = self.driver.find_element(By.ID, 'sidebarTitle')
        self.driver.execute_script("arguments[0].click();", el)
        time.sleep(0.2)  # [speedup]
        toast = self.driver.execute_script(
            "var t = document.getElementById('docToast'); return t ? t.textContent : '';")
        self.assertIn('已复制: test-show-md.md', toast, f"应复制脱敏文件名, got: {toast}")
        self.assertNotIn('file://', toast, "不应复制完整 URL")
        self.assertEqual(self._errors(), [], f"JS errors: {self._errors()}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
