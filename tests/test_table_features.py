"""Selenium test: layout-table Phase 2-4 features."""
import os, sys, time, unittest
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
DEMO = PROJECT / 'demos' / 'table-features-demo.html'


def error_collector(driver):
    driver.execute_script(
        "window.__testErrors = [];"
        "window.onerror = function(m) { window.__testErrors.push(String(m)); };"
    )


def get_errors(driver):
    return driver.execute_script("return window.__testErrors;")


def open_settings(driver):
    btn = driver.find_element(By.ID, 'colToggleBtn')
    btn.click()
    time.sleep(0.2)


def select_click_mode(driver, mode):
    """Re-open settings and select click mode radio."""
    open_settings(driver)
    radios = driver.find_elements(By.NAME, 'clickMode')
    target = [r for r in radios if r.get_attribute('value') == mode]
    assert target, f"Click mode '{mode}' radio not found"
    driver.execute_script("arguments[0].click();", target[0])
    time.sleep(0.15)  # [speedup]

    # Close dropdown via JS (avoid body.click intercept by table rows)
    driver.execute_script("document.getElementById('colToggleDropdown').classList.remove('show');")
    time.sleep(0.2)


def select_density(driver, density):
    open_settings(driver)
    radios = driver.find_elements(By.NAME, 'density')
    target = [r for r in radios if r.get_attribute('value') == density]
    assert target, f"Density '{density}' radio not found"
    # Density inputs are display:none in horizontal layout; click the parent label
    driver.execute_script("arguments[0].click();", target[0])
    time.sleep(0.15)


class TestTableFeatures(unittest.TestCase):

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
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.data-table')))
        error_collector(self.driver)

    # ── Density ──

    def test_01_density_compact(self):
        select_density(self.driver, 'compact')
        table = self.driver.find_element(By.CSS_SELECTOR, '.data-table')
        self.assertIn('dense', (table.get_attribute('class') or ''))

    def test_02_density_comfortable(self):
        select_density(self.driver, 'comfortable')
        table = self.driver.find_element(By.CSS_SELECTOR, '.data-table')
        self.assertIn('comfortable', (table.get_attribute('class') or ''))

    # ── Click Modes ──

    def test_03_modal_panel(self):
        select_click_mode(self.driver, 'modal')
        # Use JS click to avoid Selenium click interception issues
        self.driver.execute_script(
            "var rows = document.querySelectorAll('.data-table tbody tr:not(.expand-row)');"
            "if (rows.length > 0) rows[0].click();"
        )
        time.sleep(0.25)

        overlay = self.driver.find_element(By.ID, 'modalOverlay')
        self.assertIn('active', (overlay.get_attribute('class') or '').split())

        # Close via close button
        close_btn = self.driver.find_element(By.CSS_SELECTOR, '.modal-close')
        close_btn.click()
        time.sleep(0.15)
        self.assertNotIn('active', (overlay.get_attribute('class') or '').split())

    def test_04_split_view(self):
        select_click_mode(self.driver, 'split')
        self.driver.execute_script(
            "var rows = document.querySelectorAll('.data-table tbody tr:not(.expand-row)');"
            "if (rows.length > 0) rows[0].click();"
        )
        time.sleep(0.25)

        wrapper = self.driver.find_element(By.CSS_SELECTOR, '.wrapper')
        self.assertIn('split-mode', (wrapper.get_attribute('class') or '').split())

        close_btn = self.driver.find_element(By.CSS_SELECTOR, '.sp-close')
        close_btn.click()
        time.sleep(0.15)
        self.assertNotIn('split-mode', (wrapper.get_attribute('class') or '').split())

    def test_05_expand_mode(self):
        select_click_mode(self.driver, 'expand')
        self.driver.execute_script(
            "var rows = document.querySelectorAll('.data-table tbody tr:not(.expand-row)');"
            "if (rows.length > 0) rows[0].click();"
        )
        time.sleep(0.25)

        expand_rows = self.driver.find_elements(By.CSS_SELECTOR, '.expand-row')
        self.assertEqual(len(expand_rows), 1)

        # Click again to collapse
        self.driver.execute_script(
            "var rows = document.querySelectorAll('.data-table tbody tr:not(.expand-row)');"
            "if (rows.length > 0) rows[0].click();"
        )
        time.sleep(0.15)
        expand_rows2 = self.driver.find_elements(By.CSS_SELECTOR, '.expand-row')
        self.assertEqual(len(expand_rows2), 0)

    # ── Quick Filter ──

    def test_06_quick_filter(self):
        """Click a column with quickFilter:true, filter pill appears."""
        cells = self.driver.find_elements(By.CSS_SELECTOR, '.clickable-cell')
        self.assertTrue(len(cells) > 0, "No clickable cells")

        # stars column (index 1) has quickFilter:true in _table-features-demo.json
        stars_idx = 1
        self.assertGreater(len(cells), stars_idx, "Not enough cells")
        cells[stars_idx].click()
        time.sleep(0.15)  # [speedup]


        pill = self.driver.find_element(By.ID, 'quickFilterPill')
        disp = pill.value_of_css_property('display')
        self.assertNotEqual(disp, 'none', f"Filter pill should be visible, got display={disp}")

        # Close via X button
        close_btn = pill.find_element(By.CSS_SELECTOR, '.fp-close')
        close_btn.click()
        time.sleep(0.15)

        disp2 = pill.value_of_css_property('display')
        self.assertEqual(disp2, 'none')

    # ── Keyboard Navigation ──

    def test_07_keyboard_nav(self):
        body = self.driver.find_element(By.TAG_NAME, 'body')
        body.click()
        time.sleep(0.1)

        body.send_keys(Keys.ARROW_DOWN)
        time.sleep(0.15)

        focused = self.driver.find_elements(By.CSS_SELECTOR, '.keyboard-focus')
        self.assertEqual(len(focused), 1)

        body.send_keys(Keys.ARROW_DOWN)
        time.sleep(0.1)
        focused2 = self.driver.find_elements(By.CSS_SELECTOR, '.keyboard-focus')
        self.assertEqual(len(focused2), 1)

    def test_06b_quickfilter_default_off(self):
        """Column without quickFilter:true should not trigger filter (D1 default-off)."""
        cells = self.driver.find_elements(By.CSS_SELECTOR, '.clickable-cell')
        # First cell (name) has NO quickFilter:true
        cells[0].click()
        time.sleep(0.15)  # [speedup]


        # Should have opened split (firstKeyCol default D3), not created filter pill
        wrapper = self.driver.find_element(By.CSS_SELECTOR, '.wrapper')
        self.assertIn('split-mode', (wrapper.get_attribute('class') or '').split(),
                      "First column click should open split (D3 firstKeyCol)")

        # Close split via JS (avoid stale element / overlay issues)
        self.driver.execute_script("if(window.closeSplit) closeSplit();")
        time.sleep(0.15)

    # ── Column Freeze ──

    def test_08_column_freeze(self):
        ths = self.driver.find_elements(By.CSS_SELECTOR, 'th.frozen-col')
        self.assertTrue(len(ths) > 0, "No frozen column headers")

        tds = self.driver.find_elements(By.CSS_SELECTOR, 'td.frozen-col')
        self.assertTrue(len(tds) > 0, "No frozen column cells")

    # ── Fullscreen ──

    def test_09_fullscreen(self):
        fs_btn = self.driver.find_element(By.ID, 'fsBtn')
        fs_btn.click()
        time.sleep(0.15)

        wrapper = self.driver.find_element(By.CSS_SELECTOR, '.wrapper')
        self.assertIn('fullscreen', (wrapper.get_attribute('class') or '').split())

        fs_btn.click()
        time.sleep(0.1)
        self.assertNotIn('fullscreen', (wrapper.get_attribute('class') or '').split())

    # ── No JS errors ──

    def test_10_no_js_errors(self):
        # Exercise features — re-open settings between mode switches
        for val in ['modal', 'split', 'expand', 'tab']:
            select_click_mode(self.driver, val)

        # Quick filter
        cells = self.driver.find_elements(By.CSS_SELECTOR, '.clickable-cell')
        if cells:
            cells[0].click()
            time.sleep(0.1)

        # Fullscreen
        fs_btn = self.driver.find_element(By.ID, 'fsBtn')
        fs_btn.click(); time.sleep(0.08)
        fs_btn.click(); time.sleep(0.08)

        # Density
        select_density(self.driver, 'compact')
        select_density(self.driver, 'default')

        errs = get_errors(self.driver)
        self.assertEqual(len(errs), 0, f"JS errors: {errs}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
