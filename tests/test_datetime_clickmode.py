"""Selenium test: datetime sorting + clickMode singular compatibility."""
import json, time, unittest
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

CHROMEDRIVER = '/Users/jadenli/CodeSpace/script-miner/cache/chromedriver/chromedriver'
PROJECT = Path(__file__).resolve().parent.parent
TMPL = PROJECT / 'layout-table.html'
STYLE = PROJECT / 'style-guide.css'
DEMO = PROJECT / 'demos' / '_test_datetime_clickmode.html'


def generate_html(data, options=None):
    """Generate a test HTML using the table template."""
    tmpl = TMPL.read_text(encoding='utf-8')
    css = STYLE.read_text(encoding='utf-8') if STYLE.exists() else ''
    tmpl = tmpl.replace('<link rel="stylesheet" href="style-guide.css">', f'<style>\n{css}\n</style>')
    columns = [
        {"key": "name", "label": "Name", "sortable": True},
        {"key": "date", "label": "Date", "sortable": True, "type": "datetime"},
        {"key": "count", "label": "Count", "sortable": True, "type": "number"},
    ]
    opts = options or {}
    # Escape </script>
    cols_str = json.dumps(columns, ensure_ascii=False).replace('</', '<\\/')
    data_str = json.dumps(data, ensure_ascii=False).replace('</', '<\\/')
    tabs_str = json.dumps([], ensure_ascii=False).replace('</', '<\\/')
    opts_str = json.dumps(opts, ensure_ascii=False).replace('</', '<\\/')
    html = tmpl.replace('<!--COLUMNS-->', cols_str)
    html = html.replace('<!--DATA-->', data_str)
    html = html.replace('<!--TABS-->', tabs_str)
    html = html.replace('<!--OPTIONS-->', opts_str)
    DEMO.write_text(html, encoding='utf-8')
    return DEMO


class TestDatetimeClickmode(unittest.TestCase):

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

    def _load(self, data, options=None):
        generate_html(data, options)
        self.driver.get('file://' + str(DEMO))
        time.sleep(0.3)
        try: self.driver.execute_script("localStorage.clear();") 
        except: pass
        self.driver.get('file://' + str(DEMO))
        time.sleep(0.8)
        self.driver.execute_script(
            "window.__testErrors = [];"
            "window.onerror = function(m) { window.__testErrors.push(String(m)); };"
        )

    def _errors(self):
        return self.driver.execute_script("return window.__testErrors;")

    def _get_cell_texts(self, col_idx):
        """Get the text content of all tds in column col_idx."""
        return self.driver.execute_script(f"""
        var tds = document.querySelectorAll('tbody tr td:nth-child({col_idx + 1})');
        var result = [];
        for (var i = 0; i < tds.length; i++) result.push(tds[i].textContent.trim());
        return result;
        """)

    # ── Test 1: datetime_ordering ──

    def test_01_datetime_ordering(self):
        """Sort datetime column: correct order, empty values last."""
        data = [
            {"name": "C", "date": "2026-02-01", "count": 3},
            {"name": "A", "date": "2025-12-01", "count": 1},
            {"name": "B", "date": "2026-01-15", "count": 2},
            {"name": "E", "date": "", "count": 0},
            {"name": "D", "date": "2026-2-1", "count": 4},  # non-padded month
        ]
        self._load(data)

        # Click Date column header (index 1) — ascend
        ths = self.driver.find_elements(By.CSS_SELECTOR, 'th.sortable')
        date_th = [t for t in ths if t.text.strip().upper() == 'DATE']
        self.assertTrue(len(date_th) > 0, "Date column header not found")
        date_th[0].click()
        time.sleep(0.3)

        dates = self._get_cell_texts(1)
        non_empty = [d for d in dates if d]
        self.assertEqual(non_empty, ['2025-12-01', '2026-01-15', '2026-2-1', '2026-02-01'],
                         f"Date ascending order wrong: {non_empty}")
        self.assertEqual(dates[0], '', "Empty date should sort first (epoch 0)")

        # Click again for descending — re-query to avoid stale element
        ths2 = self.driver.find_elements(By.CSS_SELECTOR, 'th.sortable')
        date_th2 = [t for t in ths2 if t.text.strip().upper() == 'DATE']
        date_th2[0].click()
        time.sleep(0.3)
        dates_desc = self._get_cell_texts(1)
        non_empty_desc = [d for d in dates_desc if d]
        self.assertEqual(non_empty_desc, ['2026-02-01', '2026-2-1', '2026-01-15', '2025-12-01'],
                         f"Date descending order wrong: {non_empty_desc}")

        errs = self._errors()
        self.assertEqual(len(errs), 0, f"JS errors: {errs}")

    # ── Test 2: clickmode_singular ──

    def test_02_clickmode_singular(self):
        """options.clickMode (singular) should work like clickModes=['split']."""
        data = [{"name": "X", "date": "2026-01-01", "count": 1}]
        self._load(data, {"clickMode": "split"})

        # Open settings
        btn = self.driver.find_element(By.ID, 'colToggleBtn')
        btn.click()
        time.sleep(0.3)

        # Check that split is the active click mode
        radios = self.driver.find_elements(By.NAME, 'clickMode')
        split_radio = [r for r in radios if r.get_attribute('value') == 'split']
        self.assertTrue(len(split_radio) > 0, "Split radio should exist")
        self.assertTrue(split_radio[0].is_selected(), "Split should be selected (singular clickMode)")

        # Close settings
        self.driver.find_element(By.TAG_NAME, 'body').click()
        time.sleep(0.15)

        errs = self._errors()
        self.assertEqual(len(errs), 0, f"JS errors: {errs}")

    # ── Test 3: clickmodes_plural_priority ──

    def test_03_clickmodes_plural_priority(self):
        """Plural clickModes should take priority over singular clickMode."""
        data = [{"name": "X", "date": "2026-01-01", "count": 1}]
        self._load(data, {"clickMode": "tab", "clickModes": ["modal", "split"]})

        # Open settings
        btn = self.driver.find_element(By.ID, 'colToggleBtn')
        btn.click()
        time.sleep(0.3)

        # Modal should be visible, tab should NOT (plural overrides singular)
        radios = self.driver.find_elements(By.NAME, 'clickMode')
        radio_vals = [r.get_attribute('value') for r in radios]
        self.assertIn('modal', radio_vals, "Modal should be in plural clickModes")
        self.assertIn('split', radio_vals, "Split should be in plural clickModes")
        self.assertNotIn('tab', radio_vals, "Tab should NOT be present (plural overrides singular)")

        # Close settings
        self.driver.find_element(By.TAG_NAME, 'body').click()
        time.sleep(0.15)

        errs = self._errors()
        self.assertEqual(len(errs), 0, f"JS errors: {errs}")


if __name__ == '__main__':
    unittest.main()
