"""Selenium test: countries-table.html — pills 标签筛选、tab 优先级、quickFilter 关闭、
定位 actions、国家列 split 详情（民族/信仰）、pageSize 50、tabs 计数."""
import time, unittest
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

CHROMEDRIVER = '/Users/jadenli/CodeSpace/script-miner/cache/chromedriver/chromedriver'
PROJECT = Path(__file__).resolve().parent.parent
DEMO = PROJECT / 'demos' / 'countries' / 'countries-table.html'


class TestCountriesTable(unittest.TestCase):

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
        self.driver.set_window_size(1400, 900)
        self.driver.get('file://' + str(DEMO))
        time.sleep(0.2)
        self.driver.execute_script("localStorage.clear();")
        self.driver.get('file://' + str(DEMO))
        time.sleep(0.8)
        self.driver.execute_script(
            "window.__testErrors = [];"
            "window.onerror = function(m) { window.__testErrors.push(String(m)); };"
        )

    def _errors(self):
        return self.driver.execute_script("return window.__testErrors;")

    def _search(self, name):
        inp = self.driver.find_element(By.ID, 'searchInput')
        inp.clear()
        inp.send_keys(name)
        time.sleep(0.4)

    def _row_for_country(self, name):
        self._search(name)
        # 精确匹配第一列（国家）文本，避免 ethnic_groups 里"XX族"误匹配
        rows = self.driver.find_elements(By.CSS_SELECTOR, 'tbody tr')
        for r in rows:
            tds = r.find_elements(By.TAG_NAME, 'td')
            if tds and tds[0].text == name:
                return r
        return None

    def _clear_search(self):
        self._search('')
        time.sleep(0.2)

    # ── 上轮功能回归 ──

    def test_01_region_pills_dundun_split(self):
        row = self._row_for_country('塞尔维亚')
        self.assertIsNotNone(row, "应能找到塞尔维亚行")
        pills = row.find_elements(By.CSS_SELECTOR, '.cell-pill')
        self.assertEqual([p.text for p in pills], ['欧洲', '南欧'],
                         "大洲列应按顿号切分为 欧洲/南欧 两个标签")

    def test_02_country_click_no_quickfilter(self):
        row = self._row_for_country('中国')
        self.assertIsNotNone(row)
        first_td = row.find_elements(By.TAG_NAME, 'td')[0]
        onclick = self.driver.execute_script("return arguments[0].getAttribute('onclick') || '';", first_td)
        self.assertNotIn('quickFilterBy', onclick, "国家列不应有快速筛选 onclick")
        # 点击国家列 → 进入 split 分栏（onCellClick:'split'）
        self.driver.execute_script("arguments[0].click();", first_td)
        time.sleep(0.4)
        wrapper = self.driver.find_element(By.CSS_SELECTOR, '.wrapper')
        self.assertIn('split-mode', (wrapper.get_attribute('class') or '').split(), "点击国家应进入分栏预览")

    def test_03_default_page_size_50(self):
        self._clear_search()
        rows = self.driver.find_elements(By.CSS_SELECTOR, 'tbody tr')
        self.assertEqual(len(rows), 50, "默认每页应展示 50 行")

    def test_04_tab_counts_correct(self):
        self._clear_search()
        tabs = self.driver.find_elements(By.CSS_SELECTOR, '.tab-btn')
        counts = {}
        for t in tabs:
            count = t.find_element(By.CSS_SELECTOR, '.count').text
            name = t.text[: -len(count)]
            counts[name] = int(count)
        self.assertEqual(counts.get('全部'), 195, f"全部计数: {counts}")
        self.assertEqual(counts.get('亚洲'), 48, f"亚洲计数: {counts}")
        self.assertEqual(counts.get('欧洲'), 44, f"欧洲计数: {counts}")
        self.assertEqual(counts.get('美洲'), 35, f"美洲计数: {counts}")
        self.assertEqual(counts.get('非洲'), 54, f"非洲计数: {counts}")
        self.assertEqual(counts.get('大洋洲'), 14, f"大洋洲计数: {counts}")

    # ── 新功能：标签筛选 ──

    def test_05_pill_click_filter_contains(self):
        # 克罗地亚（前 50 页内，region_tags=欧洲、南欧）点击「南欧」标签 → contains 筛选
        row = self.driver.find_element(By.XPATH, "//tr[.//td[1][text()='克罗地亚']]")
        pill = row.find_element(By.XPATH, ".//span[contains(@class,'cell-pill') and text()='南欧']")
        self.driver.execute_script("arguments[0].click();", pill)
        time.sleep(0.5)
        rows = self.driver.find_elements(By.CSS_SELECTOR, 'tbody tr')
        self.assertEqual(len(rows), 15, f"南欧标签筛选应 15 行, 实际 {len(rows)}")
        # filter pill 显示
        fp = self.driver.find_element(By.ID, 'quickFilterPill')
        self.assertIn('南欧', fp.text, "filter pill 应显示南欧")

    def test_06_tab_priority_and_pill_overlay(self):
        # tab=欧洲（44）→ 点击南欧标签 → 欧洲∩南欧 = 15
        self._clear_search()
        for t in self.driver.find_elements(By.CSS_SELECTOR, '.tab-btn'):
            if t.text.startswith('欧洲'):
                t.click()
                break
        time.sleep(0.4)
        rows = self.driver.find_elements(By.CSS_SELECTOR, 'tbody tr')
        self.assertEqual(len(rows), 44, "欧洲 tab 应 44 行")
        row = self.driver.find_element(By.XPATH, "//tr[.//td[1][text()='克罗地亚']]")
        pill = row.find_element(By.XPATH, ".//span[contains(@class,'cell-pill') and text()='南欧']")
        self.driver.execute_script("arguments[0].click();", pill)
        time.sleep(0.5)
        rows = self.driver.find_elements(By.CSS_SELECTOR, 'tbody tr')
        self.assertEqual(len(rows), 15, f"欧洲 tab + 南欧标签叠加应 15 行, 实际 {len(rows)}")
        # 仍处于欧洲 tab
        active = self.driver.find_elements(By.CSS_SELECTOR, '.tab-btn.active')
        self.assertEqual(len(active), 1)
        self.assertIn('欧洲', active[0].text)

    def test_07_other_cols_no_quickfilter(self):
        # 英文名/首都等列不应有快速筛选 onclick
        row = self._row_for_country('中国')
        self.assertIsNotNone(row)
        tds = row.find_elements(By.TAG_NAME, 'td')
        for idx in (1, 2, 4, 5):  # 英文名/首都/纬度/经度
            onclick = self.driver.execute_script(
                "return arguments[0].getAttribute('onclick') || '';", tds[idx])
            self.assertNotIn('quickFilterBy', onclick, f"列 {idx} 不应有快速筛选")
        self._clear_search()

    # ── 新功能：定位 actions ──

    def test_08_loc_actions_button(self):
        row = self._row_for_country('中国')
        self.assertIsNotNone(row)
        btn = row.find_element(By.CSS_SELECTOR, '.action-btn')
        self.assertEqual(btn.text, '🌍', "定位应为 🌍 图标按钮")
        onclick = self.driver.execute_script("return arguments[0].getAttribute('onclick') || '';", btn)
        self.assertIn('window.open', onclick, "定位按钮应 window.open 新页签")
        self.assertIn('earth.google.com', onclick, "应指向 Google Earth 链接")

    # ── 新功能：split 详情 + 民族/信仰 ──

    def test_09_split_detail_with_ethnic_religions(self):
        row = self._row_for_country('塞尔维亚')
        self.assertIsNotNone(row)
        first_td = row.find_elements(By.TAG_NAME, 'td')[0]
        self.driver.execute_script("arguments[0].click();", first_td)
        time.sleep(0.5)
        wrapper = self.driver.find_element(By.CSS_SELECTOR, '.wrapper')
        self.assertIn('split-mode', (wrapper.get_attribute('class') or '').split())
        body = self.driver.find_element(By.ID, 'splitPreviewBody')
        text = body.text
        self.assertIn('主要民族', text, "分栏详情应含主要民族字段")
        self.assertIn('主要信仰', text, "分栏详情应含主要信仰字段")
        self.assertIn('塞尔维亚族 83.3%', text, "应显示塞尔维亚民族占比")
        self.assertIn('东正教 84.6%', text, "应显示塞尔维亚信仰占比")

    # ── 新需求：千位符 / 搜索限定 / 亚洲标签修正 ──

    def test_11_thousands_format(self):
        # 面积/人口/GDP 千位符展示
        row = self._row_for_country('中国')
        self.assertIsNotNone(row)
        tds = row.find_elements(By.TAG_NAME, 'td')
        row_text = ' | '.join(td.text for td in tds)
        self.assertIn('9,562,910', row_text, "面积应千位符: 9,562,910")
        self.assertIn('140,898', row_text, "人口应千位符: 140,898")
        self.assertIn('187,296.7', row_text, "GDP 应千位符带小数: 187,296.7")

    def test_12_search_fields_limited(self):
        # 搜索只匹配 国家/英文名/首都/首都英文
        # 1) 首都英文可搜到
        self._search('Beijing')
        rows = self.driver.find_elements(By.CSS_SELECTOR, 'tbody tr')
        self.assertEqual(len(rows), 1, f"首都英文 Beijing 应筛出 1 行（中国）: {len(rows)}")
        self.assertIn('中国', rows[0].text)
        # 2) 面积数字（非搜索字段）搜不到
        self._search('9562910')
        rows = self.driver.find_elements(By.CSS_SELECTOR, 'tbody tr')
        self.assertEqual(len(rows), 0, f"面积数字不应命中搜索（限定 4 字段）: {len(rows)}")
        # 3) 英文名可搜
        self._search('China')
        rows = self.driver.find_elements(By.CSS_SELECTOR, 'tbody tr')
        self.assertEqual(len(rows), 1, "英文名 China 应筛出 1 行")
        self._clear_search()

    def test_13_iran_afghanistan_west_asia(self):
        # 伊朗/阿富汗 → 亚洲、西亚
        for name, expected in [('伊朗', ['亚洲', '西亚']), ('阿富汗', ['亚洲', '西亚'])]:
            row = self._row_for_country(name)
            self.assertIsNotNone(row)
            pills = row.find_elements(By.CSS_SELECTOR, '.cell-pill')
            self.assertEqual([p.text for p in pills], expected, f"{name} 标签应为 {expected}")

    def test_14_no_js_errors(self):
        self._clear_search()
        for _ in range(6):
            tabs = self.driver.find_elements(By.CSS_SELECTOR, '.tab-btn')
            if not tabs:
                break
            self.driver.execute_script("arguments[0].click();", tabs[0])
            time.sleep(0.2)
        self.assertEqual(self._errors(), [], f"JS 错误: {self._errors()}")


if __name__ == '__main__':
    unittest.main()
