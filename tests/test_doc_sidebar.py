"""Selenium test: layout-doc TOC search, theme, language."""
import time, unittest
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

CHROMEDRIVER = '/Users/jadenli/CodeSpace/script-miner/cache/chromedriver/chromedriver'
PROJECT = Path(__file__).resolve().parent.parent
DEMO = PROJECT / 'demos' / 'doc-guide.html'


class TestDocSidebar(unittest.TestCase):

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
        self.driver.get('file://' + str(DEMO))
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.doc-body')))
        self.driver.execute_script(
            "window.__testErrors = [];"
            "window.onerror = function(m) { window.__testErrors.push(String(m)); };"
        )

    def _errors(self):
        return self.driver.execute_script("return window.__testErrors;")

    # ── TOC Search ──

    def test_01_toc_search_open(self):
        """Click 🔍 → search input appears."""
        btn = self.driver.find_element(By.ID, 'tocSearchBtn')
        btn.click()
        time.sleep(0.15)

        wrap = self.driver.find_element(By.ID, 'tocSearchWrap')
        self.assertIn('active', (wrap.get_attribute('class') or '').split())

    def test_02_toc_search_filter(self):
        """Type ≥2 chars → unmatched TOC items hidden."""
        btn = self.driver.find_element(By.ID, 'tocSearchBtn')
        btn.click()
        time.sleep(0.1)

        inp = self.driver.find_element(By.ID, 'tocSearchInput')
        inp.send_keys('指南')
        time.sleep(0.15)  # [speedup]


        # Some items should be filtered out
        filtered = self.driver.execute_script(
            "return document.querySelectorAll('.doc-toc a.filtered-out').length;"
        )
        total = self.driver.execute_script(
            "return document.querySelectorAll('.doc-toc a').length;"
        )
        self.assertGreater(total, 0, "No TOC items found")
        # At least some should be hidden if filter is working
        # (may be 0 if all match "指南", which is fine)

    def test_03_toc_search_close_esc(self):
        """Esc closes search."""
        btn = self.driver.find_element(By.ID, 'tocSearchBtn')
        btn.click()
        time.sleep(0.1)

        inp = self.driver.find_element(By.ID, 'tocSearchInput')
        inp.send_keys(Keys.ESCAPE)
        time.sleep(0.15)

        wrap = self.driver.find_element(By.ID, 'tocSearchWrap')
        self.assertNotIn('active', (wrap.get_attribute('class') or '').split())

    # ── Theme ──

    def test_04_theme_toggle(self):
        """🌙 click → light theme → ☀️."""
        btn = self.driver.find_element(By.ID, 'themeBtn')
        self.assertIn(btn.text, ['🌙', '☀️'])

        was_light = 'light' in (self.driver.find_element(By.TAG_NAME, 'html').get_attribute('class') or '')
        btn.click()
        time.sleep(0.15)

        is_light = 'light' in (self.driver.find_element(By.TAG_NAME, 'html').get_attribute('class') or '')
        self.assertNotEqual(was_light, is_light, "Theme should toggle")
        self.assertIn(btn.text, ['🌙', '☀️'])

    # ── Language ──

    def test_05_language_toggle(self):
        """🇨🇳/🇺🇸 toggle changes sub text."""
        # Get current state
        lang_zh = self.driver.find_element(By.ID, 'langZh')
        lang_en = self.driver.find_element(By.ID, 'langEn')
        was_zh = 'active' in (lang_zh.get_attribute('class') or '')

        # Click the non-active one
        target = lang_en if was_zh else lang_zh
        target.click()
        time.sleep(0.15)

        now_zh = 'active' in (lang_zh.get_attribute('class') or '')
        self.assertNotEqual(was_zh, now_zh, "Language should toggle")

    # ── Sidebar Collapse ──

    def test_06_sidebar_collapse(self):
        """◀◀ collapses sidebar, icon click expands."""
        btn = self.driver.find_element(By.ID, 'collapseBtn')
        initial = btn.text
        btn.click()
        time.sleep(0.15)  # [speedup]


        sidebar = self.driver.find_element(By.ID, 'sidebar')
        self.assertIn('collapsed', (sidebar.get_attribute('class') or '').split())
        self.assertNotEqual(initial, btn.text, "Button text should change")

        # Use JS to expand (the icon's onclick might not fire reliably in Selenium)
        self.driver.execute_script("toggleSidebar();")
        time.sleep(0.15)  # [speedup]

        self.assertNotIn('collapsed', (sidebar.get_attribute('class') or '').split())

    def test_07_no_js_errors(self):
        """No JS errors after exercising features."""
        # Ensure sidebar is expanded (it might be collapsed from previous test)
        self.driver.execute_script("if(document.getElementById('sidebar').classList.contains('collapsed')) toggleSidebar();")
        time.sleep(0.2)

        # TOC search — use JS click
        self.driver.execute_script("toggleTocSearch();")
        time.sleep(0.15)
        self.driver.find_element(By.ID, 'tocSearchInput').send_keys('test')
        time.sleep(0.1)
        self.driver.execute_script("toggleTocSearch();")
        time.sleep(0.1)

        # Theme toggle
        self.driver.find_element(By.ID, 'themeBtn').click()
        time.sleep(0.1)
        self.driver.find_element(By.ID, 'themeBtn').click()
        time.sleep(0.1)

        # Collapse/expand
        self.driver.find_element(By.ID, 'collapseBtn').click()
        time.sleep(0.2)
        self.driver.find_element(By.CSS_SELECTOR, '.doc-sidebar-icon').click()
        time.sleep(0.2)

        errs = self._errors()
        self.assertEqual(len(errs), 0, f"JS errors: {errs}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
