"""Selenium test: drama-knowledge.html — 以剧读史影视历史知识库 (v2: section-as-menu)."""
import time, unittest
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

CHROMEDRIVER = '/Users/jadenli/CodeSpace/script-miner/cache/chromedriver/chromedriver'
PROJECT = Path(__file__).resolve().parent.parent
DEMO = PROJECT / 'demos' / 'drama-knowledge.html'


class TestDramaKnowledge(unittest.TestCase):

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
        time.sleep(0.2)
        self.driver.execute_script("localStorage.clear();")
        self.driver.get('file://' + str(DEMO))
        time.sleep(0.6)
        self.driver.execute_script(
            "window.__testErrors = [];"
            "window.onerror = function(m) { window.__testErrors.push(String(m)); };"
        )

    def _errors(self):
        return self.driver.execute_script("return window.__testErrors;")

    def _tab_labels(self):
        return [t.text.split('\n')[-1].strip() for t in self.driver.find_elements(By.CSS_SELECTOR, '.kw-tab')]

    def _section_titles(self):
        return [s.text for s in self.driver.find_elements(By.CSS_SELECTOR, '.kw-section-title')]

    def _iframe_src(self):
        src = self.driver.find_element(By.ID, 'contentFrame').get_attribute('src') or ''
        return src.split('?')[0]

    # ── T1: Tab order ──

    def test_01_tabs_render_order(self):
        labels = self._tab_labels()
        self.assertEqual(labels, ['中国历史', '大明王朝1566'],
                         f"Tabs: {labels}")

    # ── T2: Section rendering (3 sections, no kw-item rows) ──

    def test_02_sections_render_as_menu(self):
        """D2: 中国历史 group: 3 sections, 0 items (single-item sections skipped)."""
        sections = self._section_titles()
        self.assertEqual(sections, ['概述', '时间轴', '36计策'],
                         f"Sections: {sections}")
        items = self.driver.find_elements(By.CSS_SELECTOR, '.kw-item')
        self.assertEqual(len(items), 0, "Single-item sections should not render kw-item rows")

    # ── T3: Section click opens iframe ──

    def test_03_section_click_timeline_history(self):
        """Click 中国历史 时间轴 section → iframe src = history-timeline-table.html."""
        sections = self.driver.find_elements(By.CSS_SELECTOR, '.kw-section-title')
        # 时间轴 is the 2nd section
        sections[1].click()
        time.sleep(0.3)
        src = self._iframe_src()
        self.assertTrue(src.endswith('drama/history-timeline-table.html'),
                        f"Expected timeline, got: {src}")

    def test_04_section_click_overview_daming(self):
        """Click 大明 概述 section → iframe src = daming-overview.html."""
        self.driver.find_elements(By.CSS_SELECTOR, '.kw-tab')[1].click()
        time.sleep(0.3)
        sections = self.driver.find_elements(By.CSS_SELECTOR, '.kw-section-title')
        sections[0].click()  # 概述
        time.sleep(0.3)
        src = self._iframe_src()
        self.assertTrue(src.endswith('drama/daming-overview.html'),
                        f"Expected overview, got: {src}")

    def test_05_section_click_strategy_daming(self):
        """Click 大明 36计策 section → iframe src = daming-strategy-table.html."""
        self.driver.find_elements(By.CSS_SELECTOR, '.kw-tab')[1].click()
        time.sleep(0.3)
        sections = self.driver.find_elements(By.CSS_SELECTOR, '.kw-section-title')
        sections[2].click()  # 36计策
        time.sleep(0.3)
        src = self._iframe_src()
        self.assertTrue(src.endswith('drama/daming-strategy-table.html'),
                        f"Expected strategy, got: {src}")

    # ── T4: Title 重复不串组 ──

    def test_06_title_duplicate_no_cross_group(self):
        """'概述' in 中国历史 != '概述' in 大明 (K1: selectItem by group+title)."""
        # Click 中国历史 概述
        sections = self.driver.find_elements(By.CSS_SELECTOR, '.kw-section-title')
        sections[0].click()
        time.sleep(0.3)
        self.assertTrue(self._iframe_src().endswith('drama/history-overview.html'))
        # Switch to 大明, click 概述
        self.driver.find_elements(By.CSS_SELECTOR, '.kw-tab')[1].click()
        time.sleep(0.3)
        sections2 = self.driver.find_elements(By.CSS_SELECTOR, '.kw-section-title')
        sections2[0].click()
        time.sleep(0.3)
        self.assertTrue(self._iframe_src().endswith('drama/daming-overview.html'),
                        "Cross-group title should not collide")

    # ── T5: State restore ──

    def test_07_restore_state(self):
        """Refresh restores group + section."""
        self.driver.find_elements(By.CSS_SELECTOR, '.kw-tab')[1].click()
        time.sleep(0.3)
        self.driver.find_elements(By.CSS_SELECTOR, '.kw-section-title')[1].click()  # 时间轴
        time.sleep(0.3)
        self.driver.get('file://' + str(DEMO))
        time.sleep(0.6)
        active = self.driver.find_elements(By.CSS_SELECTOR, '.kw-tab.active')
        self.assertEqual(len(active), 1)
        self.assertEqual(active[0].text.split('\n')[-1].strip(), '大明王朝1566',
                         "Should restore group")
        self.assertTrue(self._iframe_src().endswith('drama/daming-timeline-table.html'),
                        "Should restore section URL")

    # ── T6: Table content pages ──

    def test_08_daming_timeline_tabs(self):
        """大明时间轴 table 应有 2 tabs (年号总览 + 剧情节点)."""
        self.driver.find_elements(By.CSS_SELECTOR, '.kw-tab')[1].click()
        time.sleep(0.3)
        self.driver.find_elements(By.CSS_SELECTOR, '.kw-section-title')[1].click()
        time.sleep(0.5)
        # Switch to iframe content
        frame = self.driver.find_element(By.ID, 'contentFrame')
        self.driver.switch_to.frame(frame)
        tabs = self.driver.find_elements(By.CSS_SELECTOR, '.tab-btn')
        self.assertGreaterEqual(len(tabs), 2, f"Should have ≥2 tabs, got {len(tabs)}")
        self.driver.switch_to.default_content()

    # ── T7: JS errors ──

    def test_09_no_js_errors(self):
        """Exercise all sections → no JS errors."""
        for tab_idx in [0, 1]:
            self.driver.find_elements(By.CSS_SELECTOR, '.kw-tab')[tab_idx].click()
            time.sleep(0.3)
            sections = self.driver.find_elements(By.CSS_SELECTOR, '.kw-section-title')
            for si in range(len(sections)):
                sections = self.driver.find_elements(By.CSS_SELECTOR, '.kw-section-title')
                sections[si].click()
                time.sleep(0.15)
        self.assertEqual(self._errors(), [], f"JS errors: {self._errors()}")


if __name__ == '__main__':
    unittest.main()
