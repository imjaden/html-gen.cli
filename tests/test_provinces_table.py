"""Selenium test: provinces-table.html — 中国省份速查表（34 省级行政区 + 国家双向关联）。

覆盖 T1-T10（参照 test_countries_table 模式）：
  T1 表头 11 列 + 序号列（含 width）
  T2 region_tags pills 标签渲染
  T3 关联国家列 pills 2-3 标签
  T4 区域 tab 过滤（七大区域）
  T5 面积/人口/GDP 数值排序
  T6 搜索（简称/省会，searchFields 限定）
  T7 34 行数据完整（含港澳台）
  T8 港澳台 region_tags=华南 + note 口径说明
  T9 无 JS 错误（全 tab × 列遍历）
  T10 生成物 COLUMNS/DATA 与 JSON 逐字段一致（含 width）

国家表补充断言（TestCountriesBackfill）：
  - 韩国行 gdp_province 含"广东"（反向回填）
  - 柬埔寨 area_province 含"广东"（面积归一化命中，杜绝 0-命中）
  - 省份表广东 gdp_country 含 韩国/西班牙（GDP 归一化 ×7.08 对照）
"""
import json, re, time, unittest
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

CHROMEDRIVER = '/Users/jadenli/CodeSpace/script-miner/cache/chromedriver/chromedriver'
PROJECT = Path(__file__).resolve().parent.parent
DEMO = PROJECT / 'demos' / 'provinces-table.html'
COUNTRIES_DEMO = PROJECT / 'demos' / 'countries-table.html'
DATA_JSON = PROJECT / 'data' / '_provinces-data.json'


class TestProvincesTable(unittest.TestCase):

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
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.data-table')))
        self.driver.execute_script(
            "window.__testErrors = [];"
            "window.onerror = function(m) { window.__testErrors.push(String(m)); };"
        )

    def _errors(self):
        return self.driver.execute_script("return window.__testErrors;")

    def _search(self, text):
        inp = self.driver.find_element(By.ID, 'searchInput')
        inp.clear()
        inp.send_keys(text)
        time.sleep(0.4)

    def _clear_search(self):
        self._search('')

    def _row_for_province(self, name):
        """搜索并按第 1 数据列（跳过序号列）精确匹配省份行，避免 pills 内文本误匹配。"""
        self._search(name)
        rows = self.driver.find_elements(By.CSS_SELECTOR, 'tbody tr')
        for r in rows:
            tds = r.find_elements(By.TAG_NAME, 'td')
            if len(tds) > 1 and tds[1].text == name:
                return r
        return None

    def _cell_texts(self, row):
        return [td.text for td in row.find_elements(By.TAG_NAME, 'td')]

    # ── T1 表头 11 列 + 序号列 ──

    def test_01_header_11_columns_plus_index(self):
        self._clear_search()
        ths = self.driver.find_elements(By.CSS_SELECTOR, '.data-table thead th')
        # 序号列 + 11 数据列
        self.assertEqual(len(ths), 12, f"表头应为 序号+11 列, 实际 {len(ths)}")
        self.assertEqual(ths[0].text, '序号', "第 1 列应为序号列")
        labels = [t.text for t in ths[1:]]
        # 注: 模板 text-transform:uppercase 使 km² 渲染为 KM²（数据 JSON 仍为小写 km²）
        self.assertEqual(labels, [
            '省份名称', '简称', '省会/首府', '区域', '面积(万KM²)', '人口(万)',
            'GDP(亿元)', '面积相近国家', '人口相近国家', 'GDP相近国家', '备注',
        ], f"表头标签不符: {labels}")
        # Cinema 模型：显式 width 断言（关键列抽查；style 格式为 "width: 110px;"）
        widths = [t.get_attribute('style') for t in ths]
        self.assertIn('width: 110px', widths[1], f"省份列 width: {widths[1]}")
        self.assertIn('width: 60px', widths[2], f"简称列 width: {widths[2]}")
        self.assertIn('width: 170px', widths[8], f"面积相近国家列 width: {widths[8]}")
        self.assertIn('width: 200px', widths[11], f"备注列 width: {widths[11]}")

    # ── T2 region_tags pills ──

    def test_02_region_tags_pills(self):
        row = self._row_for_province('北京')
        self.assertIsNotNone(row, "应能找到北京行")
        tds = row.find_elements(By.TAG_NAME, 'td')
        region_td = tds[4]  # 序号(0) + 省份(1) + 简称(2) + 省会(3) + 区域(4)
        pills = region_td.find_elements(By.CSS_SELECTOR, '.cell-pill')
        self.assertEqual([p.text for p in pills], ['华北'], "北京区域标签应为 华北")

    # ── T3 关联国家列 pills 2-3 标签 ──

    def test_03_country_pills_2_3(self):
        row = self._row_for_province('广东')
        self.assertIsNotNone(row, "应能找到广东行")
        tds = row.find_elements(By.TAG_NAME, 'td')
        for idx, dim in ((8, '面积'), (9, '人口'), (10, 'GDP')):
            pills = tds[idx].find_elements(By.CSS_SELECTOR, '.cell-pill')
            self.assertGreaterEqual(len(pills), 2, f"广东{dim}相近国家应 ≥2 标签, 实际 {len(pills)}")
            self.assertLessEqual(len(pills), 3, f"广东{dim}相近国家应 ≤3 标签, 实际 {len(pills)}")
        # 广东实测命中（设计 §四:6 验收基准）
        gd_area = [p.text for p in tds[8].find_elements(By.CSS_SELECTOR, '.cell-pill')]
        gd_gdp = [p.text for p in tds[10].find_elements(By.CSS_SELECTOR, '.cell-pill')]
        self.assertEqual(gd_area, ['柬埔寨', '乌拉圭', '叙利亚'], f"广东面积相近: {gd_area}")
        self.assertEqual(gd_gdp, ['韩国', '西班牙', '墨西哥'], f"广东GDP相近: {gd_gdp}")

    # ── T4 区域 tab 过滤 ──

    def test_04_region_tab_filter(self):
        self._clear_search()
        tabs = self.driver.find_elements(By.CSS_SELECTOR, '.tab-btn')
        counts = {}
        for t in tabs:
            cnt = t.find_element(By.CSS_SELECTOR, '.count').text
            counts[t.text[:-len(cnt)]] = int(cnt)
        self.assertEqual(counts.get('全部'), 34, f"全部计数: {counts}")
        for region, n in [('华北', 5), ('东北', 3), ('华东', 7), ('华中', 3),
                          ('华南', 6), ('西南', 5), ('西北', 5)]:
            self.assertEqual(counts.get(region), n, f"{region}计数: {counts}")
        # 点击华南 tab → 6 行（含港澳台）
        for t in tabs:
            if t.text.startswith('华南'):
                t.click()
                break
        time.sleep(0.4)
        rows = self.driver.find_elements(By.CSS_SELECTOR, 'tbody tr')
        self.assertEqual(len(rows), 6, f"华南 tab 应 6 行, 实际 {len(rows)}")
        names = [r.find_elements(By.TAG_NAME, 'td')[1].text for r in rows]
        self.assertIn('广东', names, f"华南应含广东: {names}")
        self.assertIn('香港', names, f"华南应含香港: {names}")

    # ── T5 数值排序 ──

    def _click_th(self, label):
        ths = self.driver.find_elements(By.CSS_SELECTOR, '.data-table thead th')
        for t in ths:
            if t.text == label:
                t.click()
                time.sleep(0.4)
                return
        self.fail(f"未找到表头: {label}")

    def _first_row_name(self):
        rows = self.driver.find_elements(By.CSS_SELECTOR, 'tbody tr')
        tds = rows[0].find_elements(By.TAG_NAME, 'td')
        return tds[1].text  # 序号列后第 1 列 = 省份

    def test_05_numeric_sort(self):
        self._clear_search()
        # 面积升序 → 澳门 (0.0033 最小)
        self._click_th('面积(万KM²)')
        self.assertEqual(self._first_row_name(), '澳门', f"面积升序首行应为澳门: {self._first_row_name()}")
        # 面积降序 → 新疆 (166.49 最大)
        self._click_th('面积(万KM²)')
        self.assertEqual(self._first_row_name(), '新疆', f"面积降序首行应为新疆: {self._first_row_name()}")
        # 人口升序 → 澳门 (68 最小)
        self._click_th('人口(万)')
        self.assertEqual(self._first_row_name(), '澳门', f"人口升序首行应为澳门: {self._first_row_name()}")
        # GDP 降序 → 广东 (135673 最大)
        self._click_th('GDP(亿元)')
        self._click_th('GDP(亿元)')
        self.assertEqual(self._first_row_name(), '广东', f"GDP降序首行应为广东: {self._first_row_name()}")

    # ── T6 搜索（简称/省会，searchFields 限定）──

    def test_06_search_abbr_capital(self):
        # 简称搜索
        self._search('粤')
        rows = self.driver.find_elements(By.CSS_SELECTOR, 'tbody tr')
        self.assertEqual(len(rows), 1, f"搜「粤」应 1 行（广东）: {len(rows)}")
        self.assertIn('广东', rows[0].text)
        # 省会搜索
        self._search('广州')
        rows = self.driver.find_elements(By.CSS_SELECTOR, 'tbody tr')
        self.assertEqual(len(rows), 1, f"搜「广州」应 1 行（广东）: {len(rows)}")
        self.assertIn('广东', rows[0].text)
        # 非搜索字段（面积数字）不命中 → searchFields 限定生效
        self._search('12601')
        rows = self.driver.find_elements(By.CSS_SELECTOR, 'tbody tr')
        self.assertEqual(len(rows), 0, f"面积数字不应命中搜索: {len(rows)}")
        self._clear_search()

    # ── T7 34 行数据完整（含港澳台）──

    def test_07_34_rows_incl_hmt(self):
        # 全部 tab 计数 34
        self._clear_search()
        tabs = self.driver.find_elements(By.CSS_SELECTOR, '.tab-btn')
        all_count = int(tabs[0].find_element(By.CSS_SELECTOR, '.count').text)
        self.assertEqual(all_count, 34, f"全部 tab 应 34 行, 实际 {all_count}")
        # 港澳台各自可搜到
        for name in ('香港', '澳门', '台湾'):
            row = self._row_for_province(name)
            self.assertIsNotNone(row, f"应能找到 {name}")
        self._clear_search()

    # ── T8 港澳台 region_tags=华南 + note ──

    def test_08_hmt_south_china(self):
        for name in ('香港', '澳门', '台湾'):
            row = self._row_for_province(name)
            self.assertIsNotNone(row, f"应能找到 {name}")
            tds = row.find_elements(By.TAG_NAME, 'td')
            pills = tds[4].find_elements(By.CSS_SELECTOR, '.cell-pill')
            self.assertEqual([p.text for p in pills], ['华南'], f"{name} 区域应归华南")
            self.assertIn('特别行政区', tds[11].text, f"{name} note 应含口径说明")
        self._clear_search()

    # ── T9 无 JS 错误（全 tab × 列遍历）──

    def test_09_no_js_errors(self):
        self._clear_search()
        # 遍历全部 tab
        for _ in range(8):
            tabs = self.driver.find_elements(By.CSS_SELECTOR, '.tab-btn')
            if not tabs:
                break
            self.driver.execute_script("arguments[0].click();", tabs[0])
            time.sleep(0.2)
        # 遍历全部列头排序（sortBy 会重建 thead，每列点击前重新查询）
        idx = 1
        for _ in range(11):
            ths = self.driver.find_elements(By.CSS_SELECTOR, '.data-table thead th')
            if idx >= len(ths):
                idx = 1
            self.driver.execute_script("arguments[0].click();", ths[idx])
            idx += 1
            time.sleep(0.15)
        # 翻页到第 2 页
        try:
            pg = self.driver.find_element(By.CSS_SELECTOR, '.page-btn.next')
            self.driver.execute_script("arguments[0].click();", pg)
            time.sleep(0.3)
        except Exception:
            pass
        self.assertEqual(self._errors(), [], f"JS 错误: {self._errors()}")

    # ── T10 生成物与 JSON 逐字段一致 ──

    def _extract_injected(self, html, var):
        m = re.search(r'const\s+' + var + r'\s*=\s*(\[[\s\S]*?\]|\{[\s\S]*?\});', html)
        self.assertIsNotNone(m, f"HTML 中未找到 const {var}")
        return json.loads(m.group(1))

    def test_10_generated_matches_json(self):
        html = DEMO.read_text(encoding='utf-8')
        cfg = json.loads(DATA_JSON.read_text(encoding='utf-8'))
        cols = self._extract_injected(html, 'COLUMNS')
        data = self._extract_injected(html, 'DATA')
        # COLUMNS 逐字段一致（含 width）
        self.assertEqual(len(cols), len(cfg['columns']), "COLUMNS 列数应一致")
        for got, want in zip(cols, cfg['columns']):
            self.assertEqual(got, want, f"COLUMNS 列 {want.get('key')} 不一致")
        # DATA 逐字段一致
        self.assertEqual(len(data), len(cfg['data']), "DATA 行数应一致 (34)")
        for got, want in zip(data, cfg['data']):
            self.assertEqual(got, want, f"DATA 行 {want['province']} 不一致")
        # TABS / OPTIONS 一致
        tabs = self._extract_injected(html, 'TABS')
        self.assertEqual(tabs, cfg['tabs'], "TABS 不一致")
        opts = self._extract_injected(html, 'OPTIONS')
        self.assertEqual(opts, cfg['options'], "OPTIONS 不一致")


class TestCountriesBackfill(unittest.TestCase):
    """国家表 3 列反向回填 + 单位归一化对照（杜绝 0-命中错误模式）。"""

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
        self.driver.get('file://' + str(COUNTRIES_DEMO))
        time.sleep(0.2)
        self.driver.execute_script("localStorage.clear();")
        self.driver.get('file://' + str(COUNTRIES_DEMO))
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.data-table')))
        self.driver.execute_script(
            "window.__testErrors = [];"
            "window.onerror = function(m) { window.__testErrors.push(String(m)); };"
        )

    def _search(self, text):
        inp = self.driver.find_element(By.ID, 'searchInput')
        inp.clear()
        inp.send_keys(text)
        time.sleep(0.4)

    def _clear_search(self):
        self._search('')

    def _row_for_country(self, name):
        self._search(name)
        rows = self.driver.find_elements(By.CSS_SELECTOR, 'tbody tr')
        for r in rows:
            tds = r.find_elements(By.TAG_NAME, 'td')
            if tds and tds[0].text == name:
                return r
        return None

    def _col_idx(self, label):
        """按表头文本定位列索引（不依赖固定列数/倒数第 N 列）."""
        ths = self.driver.find_elements(By.CSS_SELECTOR, 'thead th')
        for i, th in enumerate(ths):
            if th.text == label:
                return i
        return None

    def test_11_korea_gdp_province_contains_gd(self):
        # 广东 GDP 命中韩国 → 韩国行反向 gdp_province 含"广东"
        row = self._row_for_country('韩国')
        self.assertIsNotNone(row, "应能找到韩国行")
        tds = row.find_elements(By.TAG_NAME, 'td')
        gdp_col = self._col_idx('GDP相近省份')
        assert gdp_col is not None, "表头应含 GDP相近省份 列"
        pills = [p.text for p in tds[gdp_col].find_elements(By.CSS_SELECTOR, '.cell-pill')]
        self.assertIn('广东', pills, f"韩国 gdp_province 应含广东: {pills}")
        self._clear_search()

    def test_12_cambodia_area_province_contains_gd(self):
        # 面积归一化对照：广东 17.97 万km² ↔ 柬埔寨 18.10（area_km2=181035 → 18.10）
        # area_province 列默认 initialHidden → 先通过设置面板显示
        self.driver.execute_script("toggleCol('area_province', true);")
        time.sleep(0.3)
        row = self._row_for_country('柬埔寨')
        self.assertIsNotNone(row, "应能找到柬埔寨行")
        tds = row.find_elements(By.TAG_NAME, 'td')
        area_col = self._col_idx('面积相近省份')
        assert area_col is not None, "表头应含 面积相近省份 列"
        pills = [p.text for p in tds[area_col].find_elements(By.CSS_SELECTOR, '.cell-pill')]
        self.assertIn('广东', pills, f"柬埔寨 area_province 应含广东: {pills}")
        self._clear_search()

    def test_13_countries_html_has_3_new_columns(self):
        # 国家表重生成物含 3 个新列（表头 label 断言）
        html = COUNTRIES_DEMO.read_text(encoding='utf-8')
        self.assertIn('面积相近省份', html, "国家表应含面积相近省份列")
        self.assertIn('人口相近省份', html, "国家表应含人口相近省份列")
        self.assertIn('GDP相近省份', html, "国家表应含GDP相近省份列")


if __name__ == '__main__':
    unittest.main()
