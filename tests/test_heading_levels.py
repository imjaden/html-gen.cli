"""Tests for h4-h6 heading rendering support."""
import subprocess, sys, time, unittest
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

PROJECT = Path(__file__).resolve().parent.parent
GEN = PROJECT / 'html-gen.py'
CHROMEDRIVER = '/Users/jadenli/CodeSpace/script-miner/cache/chromedriver/chromedriver'


def run_gen(*args):
    return subprocess.run([sys.executable, str(GEN)] + list(args),
                          capture_output=True, text=True, timeout=30)


class TestHeadingLevelsRegression(unittest.TestCase):
    """Regression tests for md_to_html h4-h6."""

    def test_md_to_html_h4_h5_h6(self):
        """md_to_html produces <h4>/<h5>/<h6> with ids."""
        import importlib.util
        spec = importlib.util.spec_from_file_location('html_gen', GEN)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        md = "#### 四级\n##### 五级\n###### 六级"
        out = mod.md_to_html(md)
        self.assertIn('<h4 id=', out)
        self.assertIn('<h5 id=', out)
        self.assertIn('<h6 id=', out)

    def test_md_to_html_no_leak(self):
        """#### xxx no longer produces <p>####."""
        import importlib.util
        spec = importlib.util.spec_from_file_location('html_gen', GEN)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        md = "#### 四级标题"
        out = mod.md_to_html(md)
        self.assertNotIn('<p>####', out)
        self.assertIn('<h4', out)

    def test_slug_anchor(self):
        """h4 title id matches slug()."""
        import importlib.util
        spec = importlib.util.spec_from_file_location('html_gen', GEN)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        md = "#### Hello World"
        out = mod.md_to_html(md)
        self.assertIn(f'id="{mod.slug("Hello World")}"', out)


class TestHeadingLevelsSelenium(unittest.TestCase):
    """Selenium tests for doc h4-h6 rendering."""

    @classmethod
    def setUpClass(cls):
        opts = Options()
        opts.add_argument('--headless')
        opts.add_argument('--no-sandbox')
        opts.add_argument('--disable-dev-shm-usage')
        svc = Service(CHROMEDRIVER)
        cls.driver = webdriver.Chrome(service=svc, options=opts)
        # Generate a doc with h4/h5/h6
        cls.tmp = Path('/tmp/test-h4-h6.md')
        cls.tmp.write_text(
            "# 主标题\n"
            "## 二级章节\n"
            "正文段落。\n"
            "### 三级小节\n"
            "#### 四级子节\n"
            "四级内容。\n"
            "##### 五级\n"
            "五级内容。\n"
            "###### 六级\n"
            "六级内容。\n"
        )
        cls.out = Path('/tmp/test-h4-h6.html')
        run_gen('doc', '-i', str(cls.tmp), '-o', str(cls.out))

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        cls.tmp.unlink(missing_ok=True)
        cls.out.unlink(missing_ok=True)

    def setUp(self):
        self.driver.get('file://' + str(self.out))
        time.sleep(0.5)
        self.driver.execute_script(
            "window.__testErrors = [];"
            "window.onerror = function(m) { window.__testErrors.push(String(m)); };"
        )

    def _errors(self):
        return self.driver.execute_script("return window.__testErrors;")

    def test_doc_h4_h5_render(self):
        """h4/h5 render with correct textContent, 0 JS errors."""
        h4 = self.driver.find_elements(By.CSS_SELECTOR, '.doc-body h4')
        self.assertEqual(len(h4), 1, "Should have 1 h4")
        self.assertIn('四级子节', h4[0].text)
        h5 = self.driver.find_elements(By.CSS_SELECTOR, '.doc-body h5')
        self.assertEqual(len(h5), 1, "Should have 1 h5")
        self.assertIn('五级', h5[0].text)
        h6 = self.driver.find_elements(By.CSS_SELECTOR, '.doc-body h6')
        self.assertEqual(len(h6), 1, "Should have 1 h6")
        self.assertIn('六级', h6[0].text)
        self.assertEqual(self._errors(), [], f"JS errors: {self._errors()}")

    def test_doc_toc_excludes_h4(self):
        """TOC links contain only h2/h3, not h4."""
        toc_links = self.driver.find_elements(By.CSS_SELECTOR, '.doc-toc a.toc-h4')
        self.assertEqual(len(toc_links), 0, "TOC should not contain h4")
        # h2/h3 in TOC
        h2_links = self.driver.find_elements(By.CSS_SELECTOR, '.doc-toc a.toc-h2')
        h3_links = self.driver.find_elements(By.CSS_SELECTOR, '.doc-toc a.toc-h3')
        self.assertGreaterEqual(len(h2_links), 1)
        self.assertGreaterEqual(len(h3_links), 1)

    def test_doc_h4_anchor_link(self):
        """h4 has .anchor-link child, TOC still only h2/h3."""
        h4 = self.driver.find_element(By.CSS_SELECTOR, '.doc-body h4')
        anchors = h4.find_elements(By.CSS_SELECTOR, '.anchor-link')
        self.assertGreaterEqual(len(anchors), 1, "h4 should have anchor-link")
        # No <p>#### leak
        body = self.driver.find_element(By.ID, 'docBody')
        self.assertNotIn('####', body.text)


if __name__ == '__main__':
    unittest.main()
