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

    # ── 大明王朝1566 两表 ──

    def test_06_daming_timeline(self):
        self._load('daming-timeline-table.html')
        self.assertEqual(self._headers(),
                         ['序号', '年号', '皇帝', '庙号', '起止年份', '关键人物', '主要事件', '出处'],
                         f"大明时间轴表头: {self._headers()}")
        # 默认筛选嘉靖（总览 + 7 剧情事件 = 8 行）
        rows = self.driver.find_elements(By.CSS_SELECTOR, 'tbody tr')
        self.assertEqual(len(rows), 8, f"默认应筛选嘉靖 8 行: {len(rows)}")
        text = ' '.join(r.text for r in rows)
        self.assertIn('改稻为桑', text, "嘉靖拆分应含改稻为桑")
        self.assertIn('毁堤淹田', text, "嘉靖拆分应含毁堤淹田")
        self.assertIn('治安疏', text, "嘉靖拆分应含治安疏")
        # 清筛选 24 行（16 年号 + 嘉靖 8）
        self.driver.execute_script("clearQuickFilter();")
        time.sleep(0.6)
        self.assertEqual(len(self.driver.find_elements(By.CSS_SELECTOR, 'tbody tr')), 24,
                         "应 24 行（16 年号 + 嘉靖拆分 8）")
        # 嘉靖 split 详情（pills 格子整格点击）
        jia = self._row_by_text(1, '嘉靖')
        jtd = jia.find_elements(By.TAG_NAME, 'td')
        self.assertEqual(jtd[2].text, '朱厚熜', "嘉靖皇帝列应为姓名")
        self.assertEqual(jtd[3].text, '明世宗', "嘉靖庙号应为明世宗")
        self.driver.execute_script("arguments[0].click();", jtd[1])
        time.sleep(0.8)
        pv = self.driver.find_element(By.ID, 'splitPreviewBody').text
        self.assertIn('严嵩专权', pv, "嘉靖详情应含主要事件")
        self.assertIn('本剧主线', pv, "嘉靖出处应标本剧主线")

    def test_07_daming_strategy(self):
        self._load('daming-strategy-table.html')
        self.assertEqual(self._headers(),
                         ['序号', '计名', '分类', '别名', '衍生成语', '历史事件', '主要人物', '结局', '出处'],
                         f"大明计策表头: {self._headers()}")
        rows = self.driver.find_elements(By.CSS_SELECTOR, 'tbody tr')
        self.assertEqual(len(rows), 10, f"应 10 行（10 大事件）: {len(rows)}")
        first = rows[0].find_elements(By.TAG_NAME, 'td')
        self.assertEqual(first[0].text, '1', "序号应为 1")
        self.assertEqual(first[1].text, '借刀杀人', "首行应为借刀杀人（周云逸直谏）")
        self.assertIn('周云逸', first[5].text, "首行历史事件应含周云逸")
        self.assertEqual(first[2].find_elements(By.CSS_SELECTOR, '.cell-pill')[0].text, '敌战计',
                         "借刀杀人分类应为敌战计")
        # 李代桃僵行（毁堤淹田事件）split 详情
        lidao = self._row_by_text(1, '李代桃僵')
        self.assertIsNotNone(lidao, "应找到李代桃僵行")
        self.driver.execute_script("arguments[0].click();", lidao.find_elements(By.TAG_NAME, 'td')[1])
        time.sleep(0.8)
        pv = self.driver.find_element(By.ID, 'splitPreviewBody').text
        self.assertIn('毁堤淹田', pv, "详情应含毁堤淹田")
        self.assertIn('马宁远', pv, "详情应含马宁远")
        self.assertIn('叠加计策', pv, "详情应含叠加计策（趁火打劫/借刀杀人）")
        self.assertEqual(self._errors(), [], f"JS errors: {self._errors()}")


if __name__ == '__main__':
    unittest.main()
