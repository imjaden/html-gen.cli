"""Selenium test: stickyRight + column width constraints."""
import time, unittest
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

CHROMEDRIVER = '/Users/jadenli/CodeSpace/script-miner/cache/chromedriver/chromedriver'
PROJECT = Path(__file__).resolve().parent.parent
DEMO = PROJECT / 'demos' / 'hermes-profile-skills-list.html'


class TestStickyAndWidth(unittest.TestCase):

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
        self.driver.set_window_size(1024, 600)
        self.driver.get('file://' + str(DEMO))
        time.sleep(0.8)
        self.driver.execute_script(
            "window.__testErrors = [];"
            "window.onerror = function(m) { window.__testErrors.push(String(m)); };"
        )

    # ── stickyRight ──

    def test_01_sticky_right_th(self):
        """操作列表头应有 sticky-right 类且 position:sticky."""
        th = self.driver.find_elements(By.CSS_SELECTOR, 'th.sticky-right')
        self.assertEqual(len(th), 1, "Should have exactly 1 sticky-right th")

        pos = th[0].value_of_css_property('position')
        self.assertEqual(pos, 'sticky', f"Expected sticky, got {pos}")

        right = th[0].value_of_css_property('right')
        self.assertEqual(right, '0px', f"Expected right:0px, got {right}")

    def test_02_sticky_right_td(self):
        """操作列单元格应有 sticky-right 类."""
        tds = self.driver.find_elements(By.CSS_SELECTOR, 'td.sticky-right')
        self.assertGreater(len(tds), 0, "Should have sticky-right td cells")

    def test_03_sticky_stays_visible_on_scroll(self):
        """横滚后操作列仍固定在视口右侧."""
        # Scroll the table horizontally
        wrap = self.driver.find_element(By.CSS_SELECTOR, '.table-wrap')
        self.driver.execute_script("arguments[0].scrollLeft = 400;", wrap)
        time.sleep(0.3)

        info = self.driver.execute_script("""
        var td = document.querySelector('td.sticky-right');
        if (!td) return {error: 'no td'};
        var r = td.getBoundingClientRect();
        var wrap = document.querySelector('.table-wrap').getBoundingClientRect();
        return {
            tdRight: Math.round(r.right),
            wrapRight: Math.round(wrap.right),
            isAtEdge: Math.abs(r.right - wrap.right) <= 8
        };
        """)
        self.assertTrue(info.get('isAtEdge'), 
            f"sticky td should be at wrap edge: td={info.get('tdRight')}, wrap={info.get('wrapRight')}")

    # ── Column Width ──

    def test_04_profiles_column_truncated(self):
        """PROFILES 列超出内容应被省略符截断."""
        result = self.driver.execute_script("""
        var ths = document.querySelectorAll('th');
        var profilesIdx = -1;
        for (var i = 0; i < ths.length; i++) {
            if (ths[i].textContent.trim() === 'Profiles') { profilesIdx = i; break; }
        }
        if (profilesIdx < 0) return 'no profiles column';
        var tds = document.querySelectorAll('td.clickable-cell');
        // Find the first profiles cell (after header offset)
        var profilesCell = null;
        for (var i = profilesIdx; i < tds.length; i += 6) { // 6 columns
            if (tds[i]) { profilesCell = tds[i]; break; }
        }
        if (!profilesCell) return 'no profiles cell';
        var style = window.getComputedStyle(profilesCell);
        return {
            width: style.width,
            overflow: style.overflow,
            textOverflow: style.textOverflow,
            whiteSpace: style.whiteSpace,
            scrollWidth: profilesCell.scrollWidth,
            clientWidth: profilesCell.clientWidth,
            isTruncated: profilesCell.scrollWidth > profilesCell.clientWidth
        };
        """)
        self.assertEqual(result['overflow'], 'hidden', "Should have overflow:hidden")
        self.assertIn('ellipsis', result.get('textOverflow', ''),
                      f"Should have text-overflow:ellipsis, got {result.get('textOverflow')}")

    def test_05_description_column_width(self):
        """描述列应受 width 约束."""
        result = self.driver.execute_script("""
        var ths = document.querySelectorAll('th');
        var style = null;
        for (var i = 0; i < ths.length; i++) {
            if (ths[i].textContent.trim() === '描述') {
                style = ths[i].style.width || window.getComputedStyle(ths[i]).width;
                break;
            }
        }
        return style;
        """)
        self.assertTrue(result and 'px' in str(result),
                       f"描述列应有固定宽度，实际: {result}")

    # ── No JS errors ──

    def test_06_no_js_errors(self):
        """全功能演练零 JS 错误."""
        # Scroll
        wrap = self.driver.find_element(By.CSS_SELECTOR, '.table-wrap')
        self.driver.execute_script("arguments[0].scrollLeft = 200;", wrap)
        time.sleep(0.1)
        self.driver.execute_script("arguments[0].scrollLeft = 0;", wrap)
        time.sleep(0.1)

        # Open settings
        self.driver.find_element(By.ID, 'colToggleBtn').click()
        time.sleep(0.15)
        self.driver.find_element(By.TAG_NAME, 'body').click()
        time.sleep(0.1)

        errs = self.driver.execute_script("return window.__testErrors;")
        self.assertEqual(len(errs), 0, f"JS errors: {errs}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
