"""Selenium test: layout-slide H3 toggle visibility."""
import os, sys, time, unittest
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

CHROMEDRIVER = '/Users/jadenli/CodeSpace/script-miner/cache/chromedriver/chromedriver'
PROJECT = Path(__file__).resolve().parent.parent
DEMO = PROJECT / 'demos' / 'templates' / 'template-D-slide-demo.html'


class TestH3Toggle(unittest.TestCase):

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
        time.sleep(0.15)  # [speedup]

        # Clear localStorage to prevent cross-test state
        self.driver.execute_script("localStorage.clear();")
        self.driver.get('file://' + str(DEMO))
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.slide-sidebar')))

    def test_01_h3_hidden_by_default(self):
        """toc-h3 items should be hidden on page load."""
        h3s = self.driver.find_elements(By.CSS_SELECTOR, '.toc-h3')
        self.assertGreater(len(h3s), 0, "No toc-h3 items found in demo")
        for h3 in h3s:
            self.assertEqual(h3.value_of_css_property('display'), 'none',
                             f"toc-h3 should be hidden: {h3.text[:30]}")

    def test_02_h3_toggle_visible(self):
        """Click H3 toggle → toc-h3 visible."""
        toggle = self.driver.find_element(By.ID, 'h3Toggle')
        self.assertEqual(toggle.text.strip(), 'H3')

        toggle.click()
        time.sleep(0.2)

        # Toggle should show "H3 ✓"
        self.assertIn('✓', toggle.text)

        # All toc-h3 should now be visible
        h3s = self.driver.find_elements(By.CSS_SELECTOR, '.toc-h3')
        for h3 in h3s:
            disp = h3.value_of_css_property('display')
            self.assertNotEqual(disp, 'none',
                                f"toc-h3 should be visible after toggle: {h3.text[:30]} (display={disp})")

    def test_03_h3_toggle_hidden_again(self):
        """Click H3 toggle twice → toc-h3 hidden again."""
        toggle = self.driver.find_element(By.ID, 'h3Toggle')
        toggle.click()  # show
        time.sleep(0.15)  # [speedup]

        toggle = self.driver.find_element(By.ID, 'h3Toggle')  # re-query
        toggle.click()  # hide
        time.sleep(0.15)  # [speedup]


        self.assertEqual(toggle.text.strip(), 'H3')

        h3s = self.driver.find_elements(By.CSS_SELECTOR, '.toc-h3')
        for h3 in h3s:
            self.assertEqual(h3.value_of_css_property('display'), 'none',
                             f"toc-h3 should be hidden again: {h3.text[:30]}")

    def test_04_no_js_errors(self):
        """No JS errors on page load or toggle."""
        self.driver.execute_script(
            "window.__testErrors = [];"
            "window.onerror = function(m) { window.__testErrors.push(m); };"
        )
        toggle = self.driver.find_element(By.ID, 'h3Toggle')
        toggle.click()
        time.sleep(0.15)
        toggle.click()
        time.sleep(0.15)
        errs = self.driver.execute_script("return window.__testErrors;")
        self.assertEqual(len(errs), 0, f"JS errors: {errs}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
