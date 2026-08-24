"""Tests for doc-body content width levels (?width=narrow|medium|wide)."""
import subprocess, sys, time, unittest
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

PROJECT = Path(__file__).resolve().parent.parent
GEN = PROJECT / 'html-gen.py'
CHROMEDRIVER = '/Users/jadenli/CodeSpace/script-miner/cache/chromedriver/chromedriver'
DEMO = PROJECT / 'demos' / 'doc-guide.html'

TMP_MD = Path('/tmp/test-doc-width.md')
TMP_HTML = Path('/tmp/test-doc-width.html')


def run_gen(*args):
    return subprocess.run([sys.executable, str(GEN)] + list(args),
                          capture_output=True, text=True, timeout=30)


class TestDocWidthRegression(unittest.TestCase):
    """纯 Python 回归：模板 CSS 规则 + 无持久化."""

    @classmethod
    def setUpClass(cls):
        TMP_MD.write_text("# 宽度测试\n## 章节\n正文内容测试。\n")
        run_gen('doc', '-i', str(TMP_MD), '-o', str(TMP_HTML))
        cls.html = TMP_HTML.read_text()

    @classmethod
    def tearDownClass(cls):
        TMP_MD.unlink(missing_ok=True)
        TMP_HTML.unlink(missing_ok=True)

    def test_width_narrow_css(self):
        self.assertIn('body.width-narrow .doc-body { max-width: 720px; }', self.html)

    def test_width_wide_css(self):
        self.assertIn('body.width-wide .doc-body { max-width: 1280px; }', self.html)

    def test_width_default_960(self):
        # 默认 .doc-body max-width 960px
        self.assertIn('.doc-body { padding: 0 80px; max-width: 960px;', self.html)

    def test_width_no_persist(self):
        # 宽度不持久化：无 doc_width 相关 localStorage 键
        self.assertNotIn('doc_width', self.html)
        self.assertNotIn('html-gen:doc_width', self.html)
        self.assertNotIn("localStorage.setItem('html-gen:width", self.html)


class TestDocWidthSelenium(unittest.TestCase):
    """Selenium：?width= 三态计算宽度."""

    @classmethod
    def setUpClass(cls):
        opts = Options()
        opts.add_argument('--headless')
        opts.add_argument('--no-sandbox')
        opts.add_argument('--disable-dev-shm-usage')
        svc = Service(CHROMEDRIVER)
        cls.driver = webdriver.Chrome(service=svc, options=opts)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def setUp(self):
        self.driver.set_window_size(1280, 800)

    def _load(self, query=''):
        self.driver.get('file://' + str(DEMO) + query)
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.doc-body')))
        self.driver.execute_script(
            "window.__testErrors = [];"
            "window.onerror = function(m) { window.__testErrors.push(String(m)); };"
        )

    def _errors(self):
        return self.driver.execute_script("return window.__testErrors;")

    def _max_width(self):
        return self.driver.execute_script(
            "return getComputedStyle(document.querySelector('.doc-body')).maxWidth;"
        )

    def test_width_default_960(self):
        self._load()
        self.assertEqual(self._max_width(), '960px', "默认应为 960px")

    def test_width_narrow(self):
        self._load('?width=narrow')
        self.assertEqual(self._max_width(), '720px', "narrow 应为 720px")
        self.assertEqual(self._errors(), [], f"JS errors: {self._errors()}")

    def test_width_wide(self):
        self._load('?width=wide')
        self.assertEqual(self._max_width(), '1280px', "wide 应为 1280px")
        self.assertEqual(self._errors(), [], f"JS errors: {self._errors()}")

    def test_width_embed(self):
        """嵌入降级 (?sidebar=0&toolbar=0) + wide 组合."""
        self._load('?sidebar=0&toolbar=0&width=wide')
        mw = self._max_width()
        self.assertEqual(mw, '1280px', f"embed+wide 应为 1280px, got {mw}")
        self.assertEqual(self._errors(), [], f"JS errors: {self._errors()}")


if __name__ == '__main__':
    unittest.main()
