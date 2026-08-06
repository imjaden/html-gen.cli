"""Selenium test: drama-knowledge.html — 以剧读史影视历史知识库."""
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
        # tab 文本含 icon（如 "📜\n大明王朝1566"），取末行纯 label
        return [t.text.split('\n')[-1].strip() for t in self.driver.find_elements(By.CSS_SELECTOR, '.kw-tab')]

    def _section_titles(self):
        return [s.text for s in self.driver.find_elements(By.CSS_SELECTOR, '.kw-section-title')]

    def _item_titles(self):
        return [i.text for i in self.driver.find_elements(By.CSS_SELECTOR, '.kw-item .kw-item-text')]

    # ── Tabs ──

    def test_01_tabs_render_order(self):
        labels = self._tab_labels()
        self.assertEqual(labels, ['中国历史', '大明王朝1566'], "Tab 顺序应为 中国历史 → 大明王朝1566")

    def test_02_default_group_history(self):
        # 默认选中第一个 group：中国历史（总览索引层）
        active = self.driver.find_elements(By.CSS_SELECTOR, '.kw-tab.active')
        self.assertEqual(len(active), 1)
        self.assertEqual(active[0].text.split('\n')[-1].strip(), '中国历史')
        self.assertEqual(len(self._item_titles()), 8, "中国历史 Tab 应有 8 条")
        self.assertEqual(self._section_titles(), ['朝代脉络', '代表影视剧', '观剧指南'])

    # ── Switch to 大明王朝1566 ──

    def test_03_switch_to_daming(self):
        tabs = self.driver.find_elements(By.CSS_SELECTOR, '.kw-tab')
        tabs[1].click()
        time.sleep(0.4)
        self.assertEqual(self._section_titles(), ['概述', '时间轴', '36计策'], "section 顺序应为 概述→时间轴→36计策")
        items = self._item_titles()
        self.assertEqual(len(items), 16, "大明王朝1566 Tab 应有 16 条")
        self.assertEqual(items[0], '一剧看懂大明1566')
        # 时间轴 7 条 + 36计策 6 条
        timeline = [t for t in items if t in ('改稻为桑国策出台', '毁堤淹田九县', '海瑞赴任淳安',
                                              '审通倭案', '严嵩倒台', '海瑞上治安疏', '嘉靖驾崩·海瑞出狱')]
        self.assertEqual(len(timeline), 7, "时间轴应有 7 条")

    # ── Content modes ──

    def test_04_desc_inline(self):
        self.driver.find_elements(By.CSS_SELECTOR, '.kw-tab')[1].click()
        time.sleep(0.3)
        self.driver.find_element(By.CSS_SELECTOR, '.kw-item').click()  # 一剧看懂大明1566
        time.sleep(0.3)
        body = self.driver.find_element(By.ID, 'kwBody')
        self.assertEqual(body.value_of_css_property('display'), 'block')
        self.assertIn('改稻为桑', body.text)
        frame = self.driver.find_element(By.ID, 'contentFrame')
        self.assertEqual(frame.value_of_css_property('display'), 'none', "desc 条目不应显示 iframe")

    def test_05_timeline_url(self):
        self.driver.find_elements(By.CSS_SELECTOR, '.kw-tab')[1].click()
        time.sleep(0.3)
        # 时间轴第一条：改稻为桑国策出台
        self.driver.find_element(By.XPATH, "//div[contains(@class,'kw-item')][.//span[text()='改稻为桑国策出台']]").click()
        time.sleep(0.3)
        src = (self.driver.find_element(By.ID, 'contentFrame').get_attribute('src') or '').split('?')[0]
        self.assertTrue(src.endswith('drama/daming-timeline-01.html'), f"iframe src 错误: {src}")
        body = self.driver.find_element(By.ID, 'kwBody')
        self.assertEqual(body.value_of_css_property('display'), 'none', "url 条目不应显示内联 body")

    def test_06_strategy_url(self):
        self.driver.find_elements(By.CSS_SELECTOR, '.kw-tab')[1].click()
        time.sleep(0.3)
        self.driver.find_element(By.XPATH, "//div[contains(@class,'kw-item')][.//span[text()='李代桃僵·毁堤淹田']]").click()
        time.sleep(0.3)
        src = (self.driver.find_element(By.ID, 'contentFrame').get_attribute('src') or '').split('?')[0]
        self.assertTrue(src.endswith('drama/daming-strategy-01.html'), f"iframe src 错误: {src}")

    def test_07_badge_rendered(self):
        self.driver.find_elements(By.CSS_SELECTOR, '.kw-tab')[1].click()
        time.sleep(0.3)
        badges = [b.text for b in self.driver.find_elements(By.CSS_SELECTOR, '.kw-item-badge')]
        self.assertIn('关键事件', badges)
        self.assertIn('计谋', badges)

    # ── State restore ──

    def test_08_restore_state(self):
        tabs = self.driver.find_elements(By.CSS_SELECTOR, '.kw-tab')
        tabs[1].click()
        time.sleep(0.3)
        self.driver.find_element(By.XPATH, "//div[contains(@class,'kw-item')][.//span[text()='严嵩倒台']]").click()
        time.sleep(0.3)
        # 刷新后应恢复 group + item
        self.driver.get('file://' + str(DEMO))
        time.sleep(0.6)
        active = self.driver.find_elements(By.CSS_SELECTOR, '.kw-tab.active')
        self.assertEqual(len(active), 1)
        self.assertEqual(active[0].text.split('\n')[-1].strip(), '大明王朝1566', "刷新后应恢复上次 group")
        active_item = self.driver.find_elements(By.CSS_SELECTOR, '.kw-item.active .kw-item-text')
        self.assertEqual(len(active_item), 1)
        self.assertEqual(active_item[0].text, '严嵩倒台', "刷新后应恢复上次 item")

    # ── JS errors ──

    def test_09_no_js_errors(self):
        self.driver.find_elements(By.CSS_SELECTOR, '.kw-tab')[1].click()
        time.sleep(0.3)
        for item in self._item_titles():
            try:
                self.driver.find_element(By.XPATH, f"//div[contains(@class,'kw-item')][.//span[text()='{item}']]").click()
                time.sleep(0.1)
            except Exception:
                pass
        self.assertEqual(self._errors(), [], f"JS 错误: {self._errors()}")


if __name__ == '__main__':
    unittest.main()
