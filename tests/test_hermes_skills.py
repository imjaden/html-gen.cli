"""Selenium test: hermes-profile-skills — 3 action buttons + profile tabs."""
import time, unittest
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

CHROMEDRIVER = '/Users/jadenli/CodeSpace/script-miner/cache/chromedriver/chromedriver'
PROJECT = Path(__file__).resolve().parent.parent
DEMO = PROJECT / 'demos' / 'hermes-profile-skills-list.html'


class TestHermesSkills(unittest.TestCase):

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
        time.sleep(0.3)
        self.driver.execute_script("localStorage.clear();")
        self.driver.get('file://' + str(DEMO))
        time.sleep(0.8)
        self.driver.execute_script(
            "window.__testErrors = [];"
            "window.onerror = function(m) { window.__testErrors.push(String(m)); };"
        )

    def _errors(self):
        return self.driver.execute_script("return window.__testErrors;")

    # ── Profile Tabs ──

    def test_01_profile_tabs_exist(self):
        tabs = self.driver.find_elements(By.CSS_SELECTOR, '.tab-btn')
        self.assertGreaterEqual(len(tabs), 5, f"Expected ≥5 tabs, got {len(tabs)}")

    def test_02_profile_tab_switch(self):
        tabs = self.driver.find_elements(By.CSS_SELECTOR, '.tab-btn')
        if len(tabs) > 1:
            tabs[1].click()
            time.sleep(0.3)
            # Re-query after DOM update
            tabs = self.driver.find_elements(By.CSS_SELECTOR, '.tab-btn')
            self.assertIn('active', (tabs[1].get_attribute('class') or '').split())

    # ── Action Buttons ──

    def test_03_modal_button(self):
        """Click 📋 button → modal opens with skill data."""
        btns = self.driver.find_elements(By.CSS_SELECTOR, '.action-btn')
        # Find the modal button (📋)
        modal_btns = [b for b in btns if b.get_attribute('title') == '弹出框详情']
        self.assertTrue(len(modal_btns) > 0, "No modal action buttons found")
        modal_btns[0].click()
        time.sleep(0.3)

        overlay = self.driver.find_element(By.ID, 'modalOverlay')
        self.assertIn('active', (overlay.get_attribute('class') or '').split(),
                      "Modal should be active")

        # Verify content has skill name
        panel = self.driver.find_element(By.ID, 'modalPanel')
        self.assertIn('Skill', panel.text, f"Modal should show skill data, got: {panel.text[:100]}")

        # Close modal
        self.driver.find_element(By.CSS_SELECTOR, '.modal-close').click()
        time.sleep(0.15)
        self.assertNotIn('active', (overlay.get_attribute('class') or '').split())

    def test_04_split_button(self):
        """Click 📑 button → split view opens with skill data."""
        btns = self.driver.find_elements(By.CSS_SELECTOR, '.action-btn')
        split_btns = [b for b in btns if b.get_attribute('title') == '右侧展示详情']
        self.assertTrue(len(split_btns) > 0, "No split action buttons found")
        split_btns[0].click()
        time.sleep(0.4)

        wrapper = self.driver.find_element(By.CSS_SELECTOR, '.wrapper')
        self.assertIn('split-mode', (wrapper.get_attribute('class') or '').split(),
                      "Wrapper should have split-mode")

        # Verify preview has content
        header = self.driver.find_element(By.ID, 'splitPreviewHeader')
        self.assertTrue(len(header.text) > 0, "Split preview header should have text")

        # Close split
        self.driver.find_element(By.CSS_SELECTOR, '.sp-close').click()
        time.sleep(0.15)
        self.assertNotIn('split-mode', (wrapper.get_attribute('class') or '').split())

    def test_05_url_button(self):
        """🔗 button should exist and have a valid onclick."""
        btns = self.driver.find_elements(By.CSS_SELECTOR, '.action-btn')
        url_btns = [b for b in btns if b.get_attribute('title') == '新标签页打开']
        self.assertTrue(len(url_btns) > 0, "No URL action buttons found")
        # Verify onclick is well-formed (no broken attributes)
        onclick = url_btns[0].get_attribute('onclick')
        self.assertIn('window.open', onclick or '', "URL button should have window.open")
        self.assertIn('noopener', onclick or '', "Should have noopener for security")

    # ── No JS errors ──

    def test_06_no_js_errors(self):
        """No JS errors after exercising all features."""
        # Switch tab
        tabs = self.driver.find_elements(By.CSS_SELECTOR, '.tab-btn')
        if len(tabs) > 1:
            tabs[1].click()
            time.sleep(0.3)

        # Click modal button
        btns = self.driver.find_elements(By.CSS_SELECTOR, '.action-btn')
        modal_btns = [b for b in btns if b.get_attribute('title') == '弹出框详情']
        if modal_btns:
            modal_btns[0].click()
            time.sleep(0.2)
            self.driver.find_element(By.CSS_SELECTOR, '.modal-close').click()
            time.sleep(0.1)

        # Click split button
        split_btns = [b for b in btns if b.get_attribute('title') == '右侧展示详情']
        if split_btns:
            split_btns[0].click()
            time.sleep(0.2)
            self.driver.find_element(By.CSS_SELECTOR, '.sp-close').click()
            time.sleep(0.1)

        # Click URL button (should not error — opens new tab)
        btns2 = self.driver.find_elements(By.CSS_SELECTOR, '.action-btn')
        url_btns = [b for b in btns2 if b.get_attribute('title') == '新标签页打开']
        if url_btns:
            url_btns[0].click()
            time.sleep(0.1)

        errs = self._errors()
        self.assertEqual(len(errs), 0, f"JS errors: {errs}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
