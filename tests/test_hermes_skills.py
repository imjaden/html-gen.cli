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

    # ── Skills Modal Detail Panel ──

    def test_07_modal_structured_fields(self):
        """Modal should show structured fields: 名称/分类/作者/描述."""
        btns = self.driver.find_elements(By.CSS_SELECTOR, '.action-btn')
        modal_btns = [b for b in btns if b.get_attribute('title') == '弹出框详情']
        self.assertTrue(len(modal_btns) > 0)
        modal_btns[0].click()
        time.sleep(0.3)

        panel = self.driver.find_element(By.ID, 'modalPanel')
        text = panel.text
        # Verify key fields present
        self.assertIn('名称', text, "Should show 名称 field")
        self.assertIn('分类', text, "Should show 分类 field")
        self.assertIn('描述', text, "Should show 描述 field")
        self.assertIn('路径', text, "Should show 路径 field")
        self.assertIn('文件数', text, "Should show 文件数 field")

        self.driver.find_element(By.CSS_SELECTOR, '.modal-close').click()
        time.sleep(0.15)

    def test_08_modal_tag_pills(self):
        """Modal should render 标签 and Profile as tag pills."""
        btns = self.driver.find_elements(By.CSS_SELECTOR, '.action-btn')
        modal_btns = [b for b in btns if b.get_attribute('title') == '弹出框详情']
        modal_btns[0].click()
        time.sleep(0.3)

        # Tag pills should be inline-block with border-radius
        pills = self.driver.find_elements(By.CSS_SELECTOR, '#modalPanel span[style*="border-radius:9999px"]')
        self.assertGreater(len(pills), 0, f"Should have tag pills, found {len(pills)}")

        self.driver.find_element(By.CSS_SELECTOR, '.modal-close').click()
        time.sleep(0.15)

    def test_09_modal_copy_path_no_error(self):
        """Copy path button should not throw JS error."""
        btns = self.driver.find_elements(By.CSS_SELECTOR, '.action-btn')
        modal_btns = [b for b in btns if b.get_attribute('title') == '弹出框详情']
        modal_btns[0].click()
        time.sleep(0.3)

        # Click the copy icon (📋 in the 路径 row)
        copy_btn = self.driver.execute_script("""
        var panel = document.getElementById('modalPanel');
        var spans = panel.querySelectorAll('span[title="拷贝路径"]');
        return spans.length > 0 ? true : false;
        """)
        self.assertTrue(copy_btn, "Should have copy path button")
        self.driver.execute_script(
            "var s = document.querySelector('#modalPanel span[title=\"拷贝路径\"]');"
            "if (s) s.click();"
        )
        time.sleep(0.3)

        errs = self._errors()
        self.assertEqual(len(errs), 0, f"Copy path should not throw JS error: {errs}")

        self.driver.find_element(By.CSS_SELECTOR, '.modal-close').click()
        time.sleep(0.15)

    def test_10_modal_version_badge(self):
        """Modal should show version as yellow badge."""
        btns = self.driver.find_elements(By.CSS_SELECTOR, '.action-btn')
        modal_btns = [b for b in btns if b.get_attribute('title') == '弹出框详情']
        modal_btns[0].click()
        time.sleep(0.3)

        # Version badge has fbbf24 (yellow) color
        badge = self.driver.execute_script("""
        var panel = document.getElementById('modalPanel');
        var spans = panel.querySelectorAll('span');
        for (var i = 0; i < spans.length; i++) {
            if (spans[i].textContent.trim() === '版本') {
                var next = spans[i].parentElement.querySelector('span[style*="fbbf24"]');
                return next ? next.textContent.trim() : null;
            }
        }
        return null;
        """)
        self.assertIsNotNone(badge, "Version badge should exist")
        self.assertNotEqual(badge, '', "Version badge should have text")

        self.driver.find_element(By.CSS_SELECTOR, '.modal-close').click()
        time.sleep(0.15)

    # ── Skills Split Panel ──

    def test_11_split_opens_with_content(self):
        """Split panel should open and attempt to load SKILL.md."""
        btns = self.driver.find_elements(By.CSS_SELECTOR, '.action-btn')
        split_btns = [b for b in btns if b.get_attribute('title') == '右侧展示详情']
        self.assertTrue(len(split_btns) > 0)
        split_btns[0].click()
        time.sleep(0.4)

        body = self.driver.find_element(By.ID, 'splitPreviewBody')
        self.assertTrue(len(body.text) > 0, "Split body should have content")

        self.driver.find_element(By.CSS_SELECTOR, '.sp-close').click()
        time.sleep(0.15)

    def test_12_split_nav_buttons(self):
        """Split panel should have ▲▼ navigation buttons."""
        btns = self.driver.find_elements(By.CSS_SELECTOR, '.action-btn')
        split_btns = [b for b in btns if b.get_attribute('title') == '右侧展示详情']
        split_btns[0].click()
        time.sleep(0.3)

        nav_btns = self.driver.find_elements(By.CSS_SELECTOR, '.sp-nav')
        self.assertEqual(len(nav_btns), 2, "Should have ▲▼ nav buttons")

        self.driver.find_element(By.CSS_SELECTOR, '.sp-close').click()
        time.sleep(0.15)

    # ── No JS errors after all interactions ──

    def test_13_no_js_errors_after_skills_modal_split(self):
        """No JS errors after opening modal + split in skills renderer."""
        # Open modal
        btns = self.driver.find_elements(By.CSS_SELECTOR, '.action-btn')
        modal_btns = [b for b in btns if b.get_attribute('title') == '弹出框详情']
        if modal_btns:
            modal_btns[0].click()
            time.sleep(0.2)
            # Try copy button
            self.driver.execute_script(
                "var s = document.querySelector('#modalPanel span[title=\"拷贝路径\"]');"
                "if (s) s.click();"
            )
            time.sleep(0.15)
            self.driver.find_element(By.CSS_SELECTOR, '.modal-close').click()
            time.sleep(0.1)

        # Open split
        btns2 = self.driver.find_elements(By.CSS_SELECTOR, '.action-btn')
        split_btns = [b for b in btns2 if b.get_attribute('title') == '右侧展示详情']
        if split_btns:
            split_btns[0].click()
            time.sleep(0.3)
            self.driver.find_element(By.CSS_SELECTOR, '.sp-close').click()
            time.sleep(0.1)

        errs = self._errors()
        self.assertEqual(len(errs), 0, f"JS errors after skills modal+split: {errs}")


if __name__ == '__main__':
    unittest.main()
