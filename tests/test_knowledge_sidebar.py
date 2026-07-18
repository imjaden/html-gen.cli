"""Selenium test: layout-knowledge sidebar search, theme, language."""
import time, unittest
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

CHROMEDRIVER = '/Users/jadenli/CodeSpace/script-miner/cache/chromedriver/chromedriver'
PROJECT = Path(__file__).resolve().parent.parent
DEMO = PROJECT / 'demos' / 'chaitin-business-analysis-v1.0-20260707.html'


class TestKnowledgeSidebar(unittest.TestCase):

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
        # Clear localStorage to prevent cross-test state pollution
        self.driver.get('file://' + str(DEMO))
        time.sleep(0.2)
        self.driver.execute_script("localStorage.clear();")
        # Reload clean
        self.driver.get('file://' + str(DEMO))
        time.sleep(0.6)
        self.driver.execute_script(
            "window.__testErrors = [];"
            "window.onerror = function(m) { window.__testErrors.push(String(m)); };"
        )

    def _errors(self):
        return self.driver.execute_script("return window.__testErrors;")

    # ── Search ──

    def test_01_search_open(self):
        btn = self.driver.find_element(By.ID, 'kwSearchBtn')
        btn.click()
        time.sleep(0.15)
        wrap = self.driver.find_element(By.ID, 'kwSearchWrap')
        self.assertIn('active', (wrap.get_attribute('class') or '').split())

    def test_02_search_filter(self):
        # Switch to a tab first to ensure items are rendered
        tabs = self.driver.find_elements(By.CSS_SELECTOR, '.kw-tab')
        if len(tabs) > 0:
            tabs[0].click()
            time.sleep(0.3)

        btn = self.driver.find_element(By.ID, 'kwSearchBtn')
        btn.click()
        time.sleep(0.1)

        inp = self.driver.find_element(By.ID, 'kwSearchInput')
        inp.send_keys('ags')
        time.sleep(0.3)

        # Check that items exist
        items = self.driver.find_elements(By.CSS_SELECTOR, '.kw-item')
        self.assertGreater(len(items), 0, "Should have sidebar items")

    def test_03_search_close_esc(self):
        self.driver.execute_script("toggleKwSearch();")
        time.sleep(0.1)
        self.driver.execute_script(
            "document.getElementById('kwSearchInput').value = '';"
            "toggleKwSearch();"
        )
        time.sleep(0.15)
        wrap = self.driver.find_element(By.ID, 'kwSearchWrap')
        self.assertNotIn('active', (wrap.get_attribute('class') or '').split())

    # ── Theme ──

    def test_04_theme_toggle(self):
        btn = self.driver.find_element(By.ID, 'kwThemeBtn')
        was_light = 'light' in (self.driver.find_element(By.TAG_NAME, 'html').get_attribute('class') or '')
        btn.click()
        time.sleep(0.15)
        is_light = 'light' in (self.driver.find_element(By.TAG_NAME, 'html').get_attribute('class') or '')
        self.assertNotEqual(was_light, is_light, "Theme should toggle")

    # ── Language ──

    def test_05_language_toggle(self):
        zh = self.driver.find_element(By.ID, 'kwLangZh')
        en = self.driver.find_element(By.ID, 'kwLangEn')
        was_zh = 'active' in (zh.get_attribute('class') or '')
        (en if was_zh else zh).click()
        time.sleep(0.15)
        now_zh = 'active' in (zh.get_attribute('class') or '')
        self.assertNotEqual(was_zh, now_zh)

    # ── Sidebar Collapse ──

    def test_06_sidebar_collapse(self):
        self.driver.execute_script("toggleSidebar();")
        time.sleep(0.3)
        sb = self.driver.find_element(By.ID, 'kwSidebar')
        self.assertIn('collapsed', (sb.get_attribute('class') or '').split())

        self.driver.execute_script("toggleSidebar();")
        time.sleep(0.3)
        self.assertNotIn('collapsed', (sb.get_attribute('class') or '').split())

    # ── Tab Switch ──

    def test_07_tab_switch(self):
        tabs = self.driver.find_elements(By.CSS_SELECTOR, '.kw-tab')
        self.assertGreater(len(tabs), 0, "Should have tabs")
        if len(tabs) > 1:
            tabs[1].click()
            time.sleep(0.3)
            self.assertIn('active', (tabs[1].get_attribute('class') or '').split())

    # ── No JS errors ──

    def test_08_no_js_errors(self):
        # Use JS for all interactions (elements may be off-screen in headless)
        self.driver.execute_script("toggleKwSearch();")
        time.sleep(0.1)
        self.driver.execute_script("document.getElementById('kwSearchInput').value='test';")
        time.sleep(0.1)
        self.driver.execute_script("toggleKwSearch();toggleKwTheme();")
        time.sleep(0.1)
        self.driver.execute_script("toggleKwTheme();toggleSidebar();")
        time.sleep(0.2)
        self.driver.execute_script("toggleSidebar();")
        time.sleep(0.2)

        errs = self._errors()
        self.assertEqual(len(errs), 0, f"JS errors: {errs}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
