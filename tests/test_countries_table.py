"""Selenium test: countries-table.html — pills 顿号、quickFilter 关闭、pageSize 50、tabs 计数."""
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

    def _row_for_country(self, name):
        # 通过搜索定位（pageSize 50 内需先搜到）
        inp = self.driver.find_element(By.ID, 'searchInput')
        inp.clear()
        inp.send_keys(name)
        time.sleep(0.4)
        rows = self.driver.find_elements(By.CSS_SELECTOR, 'tbody tr')
        for r in rows:
            if name in r.text:
                return r
        return None

    def test_01_region_pills_dundun_split(self):
        row = self._row_for_country('塞尔维亚')
        self.assertIsNotNone(row, "应能找到塞尔维亚行")
        pills = row.find_elements(By.CSS_SELECTOR, '.cell-pill')
        self.assertEqual([p.text for p in pills], ['欧洲', '南欧'],
                         "大洲列应按顿号切分为 欧洲/南欧 两个标签")

    def test_02_country_click_no_quickfilter(self):
        # 国家列单元格不应带 quickFilterBy onclick
        row = self._row_for_country('中国')
        self.assertIsNotNone(row)
        first_td = row.find_elements(By.TAG_NAME, 'td')[0]  # 第 1 列=国家（无行选择时）
        onclick = self.driver.execute_script("return arguments[0].getAttribute('onclick') || '';", first_td)
        self.assertNotIn('quickFilterBy', onclick, "国家列不应有快速筛选 onclick")
        # 点击国家单元格，不出现 filter pill（execute_script 避免 stale）
        self.driver.execute_script("arguments[0].click();", first_td)
        time.sleep(0.3)
        pill = self.driver.find_element(By.ID, 'quickFilterPill')
        self.assertNotIn('block', pill.get_attribute('style') or '', "点击国家不应触发快速筛选")

    def test_03_default_page_size_50(self):
        rows = self.driver.find_elements(By.CSS_SELECTOR, 'tbody tr')
        self.assertEqual(len(rows), 50, "默认每页应展示 50 行")

    def test_04_tab_counts_correct(self):
        tabs = self.driver.find_elements(By.CSS_SELECTOR, '.tab-btn')
        counts = {}
        for t in tabs:
            count = t.find_element(By.CSS_SELECTOR, '.count').text
            name = t.text[: -len(count)]  # label 与 count 无分隔（如 "亚洲48"）
            counts[name] = int(count)
        self.assertEqual(counts.get('全部'), 195, f"全部计数: {counts}")
        self.assertEqual(counts.get('亚洲'), 48, f"亚洲计数: {counts}")
        self.assertEqual(counts.get('欧洲'), 44, f"欧洲计数: {counts}")
        self.assertEqual(counts.get('美洲'), 35, f"美洲计数: {counts}")
        self.assertEqual(counts.get('非洲'), 54, f"非洲计数: {counts}")
        self.assertEqual(counts.get('大洋洲'), 14, f"大洋洲计数: {counts}")

    def test_05_tab_switch_filters(self):
        # 切到亚洲 tab → 行数 48（分页 50 上限内全部显示）
        for t in self.driver.find_elements(By.CSS_SELECTOR, '.tab-btn'):
            if t.text.startswith('亚洲'):
                t.click()
                break
        time.sleep(0.4)
        rows = self.driver.find_elements(By.CSS_SELECTOR, 'tbody tr')
        self.assertEqual(len(rows), 48, "亚洲 tab 应显示 48 行")

    def test_06_no_js_errors(self):
        # 触发渲染全路径（每次重新获取 tabs 避免 stale）
        for _ in range(6):
            tabs = self.driver.find_elements(By.CSS_SELECTOR, '.tab-btn')
            if not tabs:
                break
            self.driver.execute_script("arguments[0].click();", tabs[0])
            time.sleep(0.2)
        self.assertEqual(self._errors(), [], f"JS 错误: {self._errors()}")


if __name__ == '__main__':
    unittest.main()
