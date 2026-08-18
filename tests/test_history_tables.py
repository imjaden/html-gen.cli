"""Selenium test: 中国历史两表 — 36计(序号/pills筛选/split整行) + 时间轴(12列/历任皇帝split)."""
import time, unittest
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

CHROMEDRIVER = '/Users/jadenli/CodeSpace/script-miner/cache/chromedriver/chromedriver'
PROJECT = Path(__file__).resolve().parent.parent


class TestHistoryTables(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        opts = Options()
        opts.add_argument('--headless')
        opts.add_argument('--no-sandbox')
        opts.add_argument('--disable-dev-shm-usage')
        cls.driver = webdriver.Chrome(service=Service(CHROMEDRIVER), options=opts)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def setUp(self):
        self.driver.set_window_size(1400, 900)
        self.driver.execute_script(
            "window.__testErrors = [];"
            "window.onerror = function(m) { window.__testErrors.push(String(m)); };"
        )

    def _errors(self):
        return self.driver.execute_script("return window.__testErrors;")

    def _load(self, page):
        self.driver.get('file://' + str(PROJECT / 'demos/drama' / page))
        time.sleep(0.9)
        self.driver.execute_script(
            "window.__testErrors = [];"
            "window.onerror = function(m) { window.__testErrors.push(String(m)); };"
        )

    def _headers(self):
        return [th.text for th in self.driver.find_elements(By.CSS_SELECTOR, 'thead th')]

    def _row_by_text(self, col_idx, text):
        for r in self.driver.find_elements(By.CSS_SELECTOR, 'tbody tr'):
            tds = r.find_elements(By.TAG_NAME, 'td')
            if len(tds) > col_idx and tds[col_idx].text == text:
                return r
        return None

    # ── 36计 ──

    def test_01_strategy_headers_and_index(self):
        self._load('history-strategy-table.html')
        self.assertEqual(self._headers(),
                         ['序号', '计名', '分类', '别名', '衍生成语', '人物', '兵法'],
                         f"36计表头: {self._headers()}")
        first = self.driver.find_elements(By.CSS_SELECTOR, 'tbody tr')[0]
        tds = first.find_elements(By.TAG_NAME, 'td')
        self.assertEqual(tds[0].text, '1', "序号应为 1")
        self.assertEqual(tds[1].text, '瞒天过海')
        self.assertIn('备周则意怠', tds[6].text, "兵法列应展示原文")

    def test_02_strategy_pill_filter(self):
        self._load('history-strategy-table.html')
        row = self._row_by_text(1, '瞒天过海')
        pills = row.find_elements(By.CSS_SELECTOR, '.cell-pill')
        self.assertEqual([p.text for p in pills], ['胜战计'], f"分类 pills: {[p.text for p in pills]}")
        self.driver.execute_script("arguments[0].click();", pills[0])
        time.sleep(0.6)
        n = len(self.driver.find_elements(By.CSS_SELECTOR, 'tbody tr'))
        self.assertEqual(n, 6, f"胜战计应 6 行: {n}")

    def test_03_strategy_split_full(self):
        self._load('history-strategy-table.html')
        row = self._row_by_text(1, '瞒天过海')
        self.driver.execute_script("arguments[0].click();", row.find_elements(By.TAG_NAME, 'td')[1])
        time.sleep(0.8)
        pv = self.driver.find_element(By.ID, 'splitPreviewBody').text
        self.assertIn('【原文】', pv, "详情应含原文")
        self.assertIn('【白话】', pv, "详情应含白话")
        self.assertIn('历史案例', pv, "详情应含历史案例")
        self.assertIn('来源', pv, "详情应含来源")
        self.assertEqual(self._errors(), [], f"JS errors: {self._errors()}")

    # ── 时间轴 ──

    def test_04_timeline_headers_and_index(self):
        self._load('history-timeline-table.html')
        self.assertEqual(self._headers(),
                         ['序号', '分期', '朝代', '起止年代', '建立者', '开国年号', '皇帝数量',
                          '都城', '民族', '治世/盛世', '制度/大事', '同时期西方大事'],
                         f"时间轴表头: {self._headers()}")
        self.assertEqual(self._row_by_text(0, '1').find_elements(By.TAG_NAME, 'td')[1].text, '史前',
                         "首行应分期=史前")

    def test_05_timeline_split_emperors(self):
        self._load('history-timeline-table.html')
        tang = self._row_by_text(2, '唐')
        self.assertIsNotNone(tang, "应找到唐行")
        self.driver.execute_script("arguments[0].click();", tang.find_elements(By.TAG_NAME, 'td')[2])
        time.sleep(0.8)
        pv = self.driver.find_element(By.ID, 'splitPreviewBody').text
        self.assertIn('历任皇帝', pv, "详情应含历任皇帝")
        self.assertIn('唐太宗李世民', pv, "历任皇帝应含唐太宗")
        self.assertIn('贞观之治', pv, "历任皇帝应含贞观之治")
        self.assertIn('同时期西方大事', pv, "详情应含西方大事")
        self.assertIn('查理曼', pv, "西方大事应含查理曼")
        self.assertEqual(self._errors(), [], f"JS errors: {self._errors()}")


if __name__ == '__main__':
    unittest.main()
