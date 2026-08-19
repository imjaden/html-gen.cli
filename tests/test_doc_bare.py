"""Selenium test: layout-doc bare mode — 默认展示，?sidebar=0 / ?toolbar=0 显式隐藏."""
import time, unittest
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

CHROMEDRIVER = '/Users/jadenli/CodeSpace/script-miner/cache/chromedriver/chromedriver'
PROJECT = Path(__file__).resolve().parent.parent
DEMO = PROJECT / 'demos' / 'templates' / 'template-B-guide-v1.0-20260707.html'


class TestDocBare(unittest.TestCase):

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
        time.sleep(0.6)
        self.driver.execute_script(
            "window.__testErrors = [];"
            "window.onerror = function(m) { window.__testErrors.push(String(m)); };"
        )

    def _errors(self):
        return self.driver.execute_script("return window.__testErrors;")

    def _sidebar_display(self):
        return self.driver.execute_script(
            "return getComputedStyle(document.getElementById('sidebar')).display;")

    def _toolbar_display(self):
        return self.driver.execute_script(
            "return getComputedStyle(document.getElementById('topToolbar')).display;")

    # ── 默认展示（无参）──

    def test_01_no_param_both_visible(self):
        self._load()
        self.assertEqual(self._sidebar_display(), 'flex', "sidebar 默认应展示")
        self.assertEqual(self._toolbar_display(), 'flex', "toolbar 默认应展示")
        self.assertEqual(self._errors(), [], f"JS errors: {self._errors()}")

    # ── sidebar=0 显式隐藏侧边栏 ──

    def test_02_sidebar_zero_hidden(self):
        self._load('?sidebar=0')
        self.assertEqual(self._sidebar_display(), 'none', "sidebar=0 应隐藏侧边栏")
        self.assertEqual(self._toolbar_display(), 'flex', "toolbar 保持展示")

    # ── toolbar=0 显式隐藏工具栏 ──

    def test_03_toolbar_zero_hidden(self):
        self._load('?toolbar=0')
        self.assertEqual(self._sidebar_display(), 'flex', "sidebar 保持展示")
        self.assertEqual(self._toolbar_display(), 'none', "toolbar=0 应隐藏工具栏")

    # ── 两者显式隐藏（knowledge 嵌入场景）──

    def test_04_both_zero_hidden(self):
        self._load('?sidebar=0&toolbar=0')
        self.assertEqual(self._sidebar_display(), 'none', "嵌入场景侧边栏隐藏")
        self.assertEqual(self._toolbar_display(), 'none', "嵌入场景工具栏隐藏")

    # ── 兼容：显式 1 仍展示 ──

    def test_05_explicit_one_visible(self):
        self._load('?sidebar=1&toolbar=1')
        self.assertEqual(self._sidebar_display(), 'flex', "sidebar=1 展示")
        self.assertEqual(self._toolbar_display(), 'flex', "toolbar=1 展示")

    # ── 默认展示下 collapsed 仍可用 ──

    def test_06_collapsed_works(self):
        self._load()
        self.driver.find_element(By.TAG_NAME, 'body').send_keys('[')
        time.sleep(0.3)
        sidebar = self.driver.find_element(By.ID, 'sidebar')
        classes = sidebar.get_attribute('class') or ''
        self.assertIn('collapsed', classes, "默认展示下侧边栏可折叠")
        self.assertEqual(self._sidebar_display(), 'flex', "collapsed 侧边栏仍 flex（48px）")


if __name__ == '__main__':
    unittest.main()
