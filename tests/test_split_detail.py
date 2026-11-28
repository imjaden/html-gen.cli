"""回归测试: 表格分栏（demo 索引）—— 单列左表 / 详情链接可点 / 行高亮按 data-idx（CL018）。"""
import json
import subprocess
import tempfile
import time
import unittest
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from conftest import chromedriver_service

PROJECT = Path(__file__).resolve().parent.parent
GEN = PROJECT / 'html-gen.py'
INDEX = PROJECT / 'demos' / 'demos-index.html'


class TestSplitDetail(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        opts = Options()
        opts.add_argument('--headless=new')
        opts.add_argument('--no-sandbox')
        opts.add_argument('--disable-dev-shm-usage')
        cls.driver = webdriver.Chrome(service=chromedriver_service(), options=opts)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def setUp(self):
        self.driver.set_window_size(1440, 900)

    def _load(self, path):
        self.driver.get('file://' + str(path))
        WebDriverWait(self.driver, 8).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.data-table')))
        time.sleep(0.3)
        self.driver.execute_script('localStorage.clear();')
        self.driver.get('file://' + str(path))
        WebDriverWait(self.driver, 8).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#tbody tr')))

    # ── demo 索引页 ──

    def test_01_row_click_opens_split(self):
        self._load(INDEX)
        rows = self.driver.find_elements(By.CSS_SELECTOR, '#tbody tr')
        self.assertGreater(len(rows), 0)
        self.assertIn('clickable', rows[0].get_attribute('class'))
        rows[0].click()
        time.sleep(0.4)
        self.assertTrue(self.driver.execute_script('return !!window.splitActive'))

    def test_02_split_table_only_title_column(self):
        self._load(INDEX)
        self.driver.find_elements(By.CSS_SELECTOR, '#tbody tr')[0].click()
        time.sleep(0.4)
        ths = [t.text.strip() for t in self.driver.find_elements(By.CSS_SELECTOR, '#thead th')]
        # 序号是行号工具列（showIndex），数据列只保留标题
        self.assertEqual([t for t in ths if t != '序号'], ['标题'])

    def test_03_detail_link_clickable(self):
        self._load(INDEX)
        # 点「人选天选论」那行（标题含 renxuan 案例）
        for tr in self.driver.find_elements(By.CSS_SELECTOR, '#tbody tr'):
            if '人选天选论' in tr.text:
                tr.click()
                break
        time.sleep(0.4)
        body = self.driver.find_element(By.ID, 'splitPreviewBody')
        links = body.find_elements(By.CSS_SELECTOR, 'a')
        self.assertTrue(links, '详情面板应有可点击链接')
        self.assertTrue(any(l.get_attribute('href').endswith('the-price-you-choose.html') for l in links))
        # 不应出现被转义的字面 <a
        self.assertNotIn('<a ', body.text)
        # 标签仍成对渲染（标题/模板/文档链接 全字段）
        self.assertIn('文档链接', body.text)

    def test_04_active_row_highlight(self):
        self._load(INDEX)
        target = None
        for tr in self.driver.find_elements(By.CSS_SELECTOR, '#tbody tr'):
            if '人选天选论' in tr.text:
                target = tr
                break
        self.assertIsNotNone(target)
        expected_idx = target.get_attribute('data-idx')
        target.click()
        time.sleep(0.4)
        active = self.driver.find_elements(By.CSS_SELECTOR, '#tbody tr.split-active')
        self.assertEqual(len(active), 1)
        self.assertEqual(active[0].get_attribute('data-idx'), expected_idx)
        self.assertIn('人选天选论', active[0].text)

    # ── 跨页高亮（分页 ≥2 页）──

    def test_05_highlight_on_second_page(self):
        tmp = Path(tempfile.mkdtemp(prefix='_tmp_split_'))
        data = {
            'columns': [
                {'key': 'name', 'label': '名称', 'preview': True, 'width': '200px'},
                {'key': 'n', 'label': '值', 'type': 'number'},
            ],
            'data': [{'name': f'行{i:02d}', 'n': i} for i in range(31)],
            'options': {'pageSize': 10, 'clickMode': 'split'},
        }
        dfile = tmp / 'd.json'
        dfile.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
        out = tmp / 'out.html'
        r = subprocess.run(['python3', str(GEN), 'table', '-d', str(dfile), '-o', str(out), '--quiet'],
                           capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stderr)

        self._load(out)
        self.driver.execute_script('goPage(2);')
        time.sleep(0.4)
        rows = self.driver.find_elements(By.CSS_SELECTOR, '#tbody tr')
        self.assertEqual(rows[0].get_attribute('data-idx'), '10')
        rows[0].click()
        time.sleep(0.4)
        active = self.driver.find_elements(By.CSS_SELECTOR, '#tbody tr.split-active')
        self.assertEqual(len(active), 1)
        self.assertEqual(active[0].get_attribute('data-idx'), '10')
        self.assertIn('行10', active[0].text)

    # ── escape:false（HTML）列的「取文本」口径（CL048 守卫）──

    def test_06_html_column_split_header_is_plain_text(self):
        """标题列存 HTML 时，分栏标题必须是纯文本，不能露出 `<a href=...>` 原文。"""
        tmp = Path(tempfile.mkdtemp(prefix='_tmp_split_'))
        data = {
            'columns': [
                {'key': 'name', 'label': '名称', 'escape': False, 'preview': True, 'width': '220px'},
                {'key': 'note', 'label': '备注', 'escape': False},
            ],
            'data': [
                {'name': '<a href="a1.html" target="_blank" rel="noopener">★ 甲 案例</a>',
                 'note': '<b>粗</b>'},
                {'name': '<a href="a2.html" target="_blank" rel="noopener">乙 案例</a>',
                 'note': 'plain'},
            ],
            'options': {'clickMode': 'split'},
        }
        dfile = tmp / 'd.json'
        dfile.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
        out = tmp / 'out.html'
        r = subprocess.run(['python3', str(GEN), 'table', '-d', str(dfile), '-o', str(out), '--quiet'],
                           capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stderr)

        self._load(out)
        self.driver.find_elements(By.CSS_SELECTOR, '#tbody tr')[0].click()
        time.sleep(0.4)
        head = self.driver.find_element(By.CSS_SELECTOR, '#splitPreviewHeader').text
        self.assertIn('★ 甲 案例', head)
        self.assertNotIn('<', head, f'分栏标题露出标签: {head!r}')
        self.assertNotIn('href', head, f'分栏标题露出属性: {head!r}')

    def test_07_html_column_not_searchable_by_markup(self):
        """搜 `href` 不得命中任何行（HTML 列按纯文本参与搜索）。"""
        tmp = Path(tempfile.mkdtemp(prefix='_tmp_split_'))
        data = {
            'columns': [
                {'key': 'name', 'label': '名称', 'escape': False, 'preview': True, 'width': '220px'},
                {'key': 'note', 'label': '备注'},
            ],
            'data': [
                {'name': '<a href="a1.html">甲</a>', 'note': 'x'},
                {'name': '<a href="a2.html">乙</a>', 'note': 'y'},
            ],
            'options': {'clickMode': 'split'},
        }
        dfile = tmp / 'd.json'
        dfile.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
        out = tmp / 'out.html'
        r = subprocess.run(['python3', str(GEN), 'table', '-d', str(dfile), '-o', str(out), '--quiet'],
                           capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stderr)

        self._load(out)
        self.assertEqual(len(self.driver.find_elements(By.CSS_SELECTOR, '#tbody tr')), 2)
        self.driver.execute_script(
            "var i=document.getElementById('searchInput'); i.value='href';"
            "i.dispatchEvent(new Event('input',{bubbles:true}));")
        time.sleep(0.6)
        self.assertEqual(len(self.driver.find_elements(By.CSS_SELECTOR, '#tbody tr')), 0,
                         '搜 href 命中说明 HTML 列被当纯串匹配')
        self.driver.execute_script(
            "var i=document.getElementById('searchInput'); i.value='甲';"
            "i.dispatchEvent(new Event('input',{bubbles:true}));")
        time.sleep(0.6)
        self.assertEqual(len(self.driver.find_elements(By.CSS_SELECTOR, '#tbody tr')), 1,
                         'HTML 列的可见文本仍应可搜')


class TestHtmlColumnTextContract(unittest.TestCase):
    """CL048 静态守卫：escape:false 列存 HTML，所有取文本路径必须走 plainCellText/cellTextFor。"""

    def setUp(self):
        self.tpl = (PROJECT / 'layout-table.html').read_text(encoding='utf-8')

    def test_helper_exists(self):
        self.assertIn('function plainCellText(col, v)', self.tpl)

    def test_split_header_uses_plain_text(self):
        self.assertIn('escapeHtml(plainCellText(titleCol', self.tpl)

    def test_search_uses_cell_text_for(self):
        self.assertIn('cellTextFor(colByKey[k], row[k])', self.tpl)
        self.assertNotIn("String(row[k] || '').toLowerCase().indexOf(q)", self.tpl,
                         '搜索退回了裸 String()，HTML 列会被标记串命中')

    def test_csv_uses_cell_text_for(self):
        self.assertIn('var v = cellTextFor(c, row[c.key]);', self.tpl)


if __name__ == '__main__':
    unittest.main()
