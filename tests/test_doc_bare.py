"""Selenium test: layout-doc bare mode — sidebar/toolbar URL param control."""
import time, unittest
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

CHROMEDRIVER = '/Users/jadenli/CodeSpace/script-miner/cache/chromedriver/chromedriver'
PROJECT = Path(__file__).resolve().parent.parent
DEMO = PROJECT / 'demos' / 'template-B-guide-v1.0-20260707.html'


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
            "return getComputedStyle(document.getElementById('sidebar')).display;"
        )

    def _toolbar_display(self):
        return self.driver.execute_script(
            "return getComputedStyle(document.getElementById('topToolbar')).display;"
        )

    # ── Bare mode: no param → both hidden ──

    def test_01_no_param_both_hidden(self):
        self._load()
        self.assertEqual(self._sidebar_display(), 'none', "sidebar should be hidden by default")
        self.assertEqual(self._toolbar_display(), 'none', "toolbar should be hidden by default")
        self.assertEqual(self._errors(), [], f"JS errors: {self._errors()}")

    # ── sidebar=1 only ──

    def test_02_sidebar_only(self):
        self._load('?sidebar=1')
        self.assertEqual(self._sidebar_display(), 'flex', "sidebar should show with ?sidebar=1")
        self.assertEqual(self._toolbar_display(), 'none', "toolbar should stay hidden")

    # ── toolbar=1 only ──

    def test_03_toolbar_only(self):
        self._load('?toolbar=1')
        self.assertEqual(self._sidebar_display(), 'none', "sidebar should stay hidden")
        self.assertEqual(self._toolbar_display(), 'flex', "toolbar should show with ?toolbar=1")

    # ── both ──

    def test_04_both_visible(self):
        self._load('?sidebar=1&toolbar=1')
        self.assertEqual(self._sidebar_display(), 'flex', "sidebar should show")
        self.assertEqual(self._toolbar_display(), 'flex', "toolbar should show")

    # ── collapsed still works under show-sidebar (N5) ──

    def test_05_collapsed_under_sidebar(self):
        self._load('?sidebar=1')
        # Collapse via keyboard shortcut '['
        self.driver.find_element(By.TAG_NAME, 'body').send_keys('[')
        time.sleep(0.3)
        sidebar = self.driver.find_element(By.ID, 'sidebar')
        classes = sidebar.get_attribute('class') or ''
        self.assertIn('collapsed', classes, "sidebar should collapse under show-sidebar")
        # Still displayed (flex), just 48px
        self.assertEqual(self._sidebar_display(), 'flex', "collapsed sidebar still flex")


if __name__ == '__main__':
    unittest.main()
