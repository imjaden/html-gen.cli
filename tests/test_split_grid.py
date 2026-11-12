"""CL031 守卫: 分栏详情声明式行布局（options.splitGrid）。

设计: documents/solutions/table-split-grid-design-v1.0-20261109.md §6 判据 1–8。
判据全部为 DOM 实测（坐标/节点数/类名），不看源码字面量。
"""
import json
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from conftest import chromedriver_service

ROOT = Path(__file__).resolve().parent.parent
GEN = ROOT / 'html-gen.py'

COLS = [
    {'key': 'a', 'label': 'A', 'width': '120px'},
    {'key': 'b', 'label': 'B', 'width': '120px'},
    {'key': 'c', 'label': 'C', 'width': '120px'},
    {'key': 'd', 'label': 'D', 'width': '120px'},
    {'key': 'e', 'label': 'E', 'width': '120px'},
    {'key': 'f', 'label': 'F', 'width': '120px'},
    {'key': 'hiddenOne', 'label': '隐藏', 'width': '120px'},
    {'key': 'emptyOne', 'label': '空', 'width': '120px'},
]
ROW = {'a': 'A1', 'b': 'B1', 'c': 'C1', 'd': 'D1', 'e': 'E1', 'f': 'F1',
       'hiddenOne': 'H1', 'emptyOne': ''}


def render(split_grid=None, extra_options=None, row=None, cols=None):
    data = {
        'title': 'CL031 探针',
        'columns': cols or COLS,
        'data': [row or ROW],
        'options': {'clickMode': 'split', 'pageSize': 10, 'exportCSV': True},
    }
    if split_grid is not None:
        data['options']['splitGrid'] = split_grid
    data['options'].update(extra_options or {})
    tmp = Path(tempfile.mkdtemp(prefix='cl031_'))
    dj, out = tmp / 'd.json', tmp / 'o.html'
    dj.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
    r = subprocess.run([sys.executable, str(GEN), 'table', '-d', str(dj), '-o', str(out)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return out


class TestSplitGrid(unittest.TestCase):

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

    def _open(self, path):
        self.driver.get('file://' + str(path))
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#tbody tr')))
        self.driver.execute_script('localStorage.clear();')
        self.driver.get('file://' + str(path))
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#tbody tr')))
        time.sleep(0.3)
        self.driver.find_element(By.CSS_SELECTOR, '#tbody tr td:nth-child(1)').click()
        time.sleep(0.6)

    def _cells(self):
        return self.driver.execute_script("""
          var b = document.getElementById('splitPreviewBody');
          var g = b.querySelector('.kv-grid');
          var items = b.querySelectorAll('.kv-item');
          var out = [];
          Array.prototype.forEach.call(items, function (el) {
            var r = el.getBoundingClientRect();
            out.push({label: (el.querySelector('.kv-label')||{}).textContent || '',
                      x: Math.round(r.x), y: Math.round(r.y), top: Math.round(r.top),
                      w: Math.round(r.width), h: Math.round(r.height),
                      row: el.style.gridRow, col: el.style.gridColumn});
          });
          var body = b.getBoundingClientRect();
          var gr = g ? g.getBoundingClientRect() : {width: 0, left: 0};
          return {items: out, hasGrid: !!g, gridW: Math.round(gr.width), gridLeft: Math.round(gr.left),
                  cols: g ? getComputedStyle(g).getPropertyValue('--kv-cols').trim() : '',
                  bodyW: Math.round(body.width), bodyLeft: Math.round(body.left),
                  bodyClient: b.clientWidth, bodyScroll: b.scrollWidth,
                  listNodes: b.querySelectorAll('.kv-list').length};
        """)

    # 判据 1: 显式行 ------------------------------------------------------
    def test_01_explicit_rows(self):
        self._open(render({'grid': [['a', 'b'], ['c'], ['d', 'e', 'f']]}))
        r = self._cells()
        self.assertTrue(r['hasGrid'], '应渲染 .kv-grid 容器')
        tops = sorted({i['top'] for i in r['items']})
        self.assertEqual(len(tops), 3, f'应形成 3 个视觉行，实得 top 集合 {tops}')
        by = {i['label']: i for i in r['items']}
        # 行首起排：每行从第 1 轨开始 ⇒ c 独占第 2 行第 1 轨
        self.assertNotEqual(by['C']['top'], by['A']['top'],
                            'c 不得与第 1 行同 top（否则被流顶到第 1 行第 3 列 —— 对端 ④ 现象）')
        self.assertNotEqual(by['C']['top'], by['D']['top'], 'c 不得与第 3 行同 top')
        self.assertLessEqual(abs(by['C']['x'] - by['A']['x']), 1,
                             f'c 应在第 1 轨（c.x={by["C"]["x"]}, A.x={by["A"]["x"]}）')
        self.assertLessEqual(abs(by['F']['x'] - (by['E']['x'] + (by['E']['x'] - by['D']['x']))), 2,
                             f'f 应在第 3 轨（D/E/F 同行依次排开，f.x={by["F"]["x"]}）')

    def test_01b_short_row_does_not_absorb_next_row(self):
        # 守「短行不吸收下一行」的结果：[[a],[b,c]] ⇒ b/c 同处第 2 行、c 不回填第 1 行空列。
        # 注意：本用例不构成 M1（删掉逐格 grid-row）的判别力 —— 行首恒落第 1 轨，
        # 上一行已占 col 1 ⇒ CSS Grid 稀疏自动流必然换行，结果与显式坐标一致（M1 为等价变异）。
        self._open(render({'grid': [['a'], ['b', 'c']]}))
        r = self._cells()
        by = {i['label']: i for i in r['items']}
        self.assertEqual(by['B']['top'], by['C']['top'], 'b/c 应同处第 2 行')
        self.assertNotEqual(by['A']['top'], by['B']['top'], 'b 不得被顶到第 1 行')
        self.assertNotEqual(by['A']['top'], by['C']['top'],
                            'c 不得被自动流塞回第 1 行空列（显式行边界失效的典型症状）')

    # 判据 2: 权重与整行 ---------------------------------------------------
    def test_02_span_and_full(self):
        self._open(render({'grid': [['a', {'key': 'b', 'span': 2}], [{'key': 'c', 'span': 'full'}]]}))
        r = self._cells()
        by = {i['label']: i for i in r['items']}
        self.assertGreaterEqual(by['B']['w'], by['A']['w'] * 1.8,
                                f'span:2 应≈两倍单轨（B={by["B"]["w"]}, A={by["A"]["w"]}）')
        self.assertLessEqual(abs(by['C']['w'] - r['gridW']), 2,
                             f'full 应≈栅格宽（C={by["C"]["w"]}, grid={r["gridW"]}）')

    # 判据 3: catch-all 与零空轨 ------------------------------------------
    def test_03_catch_all_expansion(self):
        self._open(render({'grid': [['a'], ['*']], 'hide': ['hiddenOne', 'emptyOne']}))
        r = self._cells()
        labels = [i['label'] for i in r['items']]
        self.assertEqual(labels[:1], ['A'])
        self.assertEqual(sorted(labels[1:]), ['B', 'C', 'D', 'E', 'F'], f'catch-all 应展开剩余 5 列: {labels}')
        tops = sorted({i['top'] for i in r['items']})
        self.assertEqual(len(tops), 2, 'A 一行 + catch-all 一行')

    def test_04_catch_all_empty_renders_no_track(self):
        # 所有列都被显式引用或 hide ⇒ 展开集为空 ⇒ 该行零节点、不留空轨
        self._open(render({'grid': [['a', 'b'], ['c', 'd'], ['e', 'f'], ['*']],
                           'hide': ['hiddenOne', 'emptyOne']}))
        r = self._cells()
        tops = sorted({i['top'] for i in r['items']})
        self.assertEqual(len(tops), 3, f'catch-all 空集不得产生第 4 行，实得 {len(tops)} 行')
        self.assertEqual(len(r['items']), 6, '不得产生空格子节点')

    def test_04b_empty_catch_all_row_in_middle_leaves_no_gap(self):
        # 空 catch-all 行夹在中间：不得留下一条空轨（否则后续行被推下去）
        # 除 a/b 外全部 hide ⇒ catch-all 展开集为空（夹在中间的空行）
        self._open(render({'grid': [['a'], ['*'], ['b']],
                           'hide': ['c', 'd', 'e', 'f', 'hiddenOne', 'emptyOne']}))
        r = self._cells()
        by = {i['label']: i for i in r['items']}
        gap_expected = by['B']['top'] - by['A']['top']
        one_row = by['B']['h'] + 6            # 行高 + gap(6px)
        self.assertLessEqual(abs(gap_expected - one_row), 4,
                             f'空 catch-all 行不得留空轨（A→B 间距={gap_expected}，单行≈{one_row}）')

    # 判据 4: hide 不占位但数据仍在 ---------------------------------------
    def test_05_hide_keeps_data_elsewhere(self):
        self._open(render({'grid': [['a', 'hiddenOne'], ['*']], 'hide': ['hiddenOne']}))
        r = self._cells()
        self.assertNotIn('隐藏', [i['label'] for i in r['items']], 'hide 清单里的列不得出现在详情')
        # 表格侧仍渲染该列
        heads = self.driver.execute_script(
            "return Array.prototype.map.call(document.querySelectorAll('.data-table thead th'),"
            " function(th){ return th.textContent.trim(); });")
        self.assertIn('隐藏', heads, 'hide 只作用于 splitGrid，表格列集不变')
        self.assertIn('H1', self.driver.find_element(By.CSS_SELECTOR, '#tbody tr').text,
                      '数据仍在表格里')

    # 判据 5: 几何 ---------------------------------------------------------
    def test_06_geometry(self):
        self._open(render({'grid': [['a', 'b'], ['c'], ['d', 'e', 'f']]}))
        r = self._cells()
        left, right = r['bodyLeft'], r['bodyLeft'] + r['bodyW']
        for i in r['items']:
            self.assertGreaterEqual(i['x'], left - 1, f'{i["label"]} 左出界')
            self.assertLessEqual(i['x'] + i['w'], right + 1, f'{i["label"]} 右出界')
        # 同 top 的格不得横向重叠
        rows = {}
        for i in r['items']:
            rows.setdefault(i['top'], []).append(i)
        for top, group in rows.items():
            group.sort(key=lambda g: g['x'])
            for a, b in zip(group, group[1:]):
                self.assertGreaterEqual(b['x'], a['x'] + a['w'] - 1, f'top={top} 横向重叠')
        # 窄窗不横向溢出
        self.driver.set_window_size(900, 800)
        time.sleep(0.3)
        r2 = self._cells()
        self.assertLessEqual(r2['bodyScroll'], r2['bodyClient'] + 1,
                             f'窄窗横向溢出 scroll={r2["bodyScroll"]} client={r2["bodyClient"]}')

    # 判据 6: 向后兼容（不写 splitGrid ⇒ 仍是扁平 kv-list） -----------------
    def test_07_backward_compat_flat_list(self):
        self._open(render(None))
        r = self._cells()
        self.assertFalse(r['hasGrid'], '不写 splitGrid 时不得出现 .kv-grid')
        self.assertEqual(r['listNodes'], 1, '不写 splitGrid 时应仍用 .kv-list 扁平容器')

    # 判据 3 附带: skipEmpty 时空值格零节点 ---------------------------------
    def test_09_skip_empty_in_grid(self):
        grid = {'grid': [['a', 'emptyOne'], ['b']], 'skipEmpty': True}
        self._open(render(grid))
        r = self._cells()
        labels = [i['label'] for i in r['items']]
        self.assertNotIn('空', labels, 'skipEmpty=true 时空值列不得占格')
        self.assertIn('A', labels)
        # 关掉 skipEmpty ⇒ 空值格照常渲染（一格一节点，值区为空）
        self._open(render({'grid': [['a', 'emptyOne'], ['b']], 'skipEmpty': False}))
        labels2 = [i['label'] for i in self._cells()['items']]
        self.assertIn('空', labels2, 'skipEmpty=false 时空值列仍占格（向后兼容 hideEmptyCells 缺省 false）')

    # 判据 7 (CL033): 行内 full 只吃剩余轨，不盖兄弟格 ---------------------
    def test_10_mid_row_full_fills_remainder(self):
        # 修前 full 恒写 1 / -1 ⇒ 与同行兄弟格重叠且无提示
        self._open(render({'grid': [['a', {'key': 'b', 'span': 'full'}]]}))
        r = self._cells()
        by = {i['label']: i for i in r['items']}
        gap = 6   # .kv-grid 的 gap
        self.assertEqual(by['A']['top'], by['B']['top'], 'a/b 应同行（full 不得隐式换行）')
        self.assertGreater(by['B']['x'], by['A']['x'], 'full 应排在 a 之后')
        self.assertGreaterEqual(by['B']['x'], by['A']['x'] + by['A']['w'],
                                f'b 盖住 a：a 右边界={by["A"]["x"] + by["A"]["w"]}, b.x={by["B"]["x"]}')
        expect = r['gridW'] - by['A']['w'] - gap
        self.assertLessEqual(abs(by['B']['w'] - expect), 3,
                             f'full 应填满剩余轨：B={by["B"]["w"]}, 期望≈{expect}（grid={r["gridW"]}）')
        # 行首 full 且其后仍有兄弟格：同样不得重叠，也不得靠隐式新增轨道绕过
        self._open(render({'grid': [[{'key': 'a', 'span': 'full'}, 'b']]}))
        r2 = self._cells()
        by2 = {i['label']: i for i in r2['items']}
        self.assertEqual(by2['A']['top'], by2['B']['top'], 'a/b 应同行')
        self.assertGreaterEqual(by2['B']['x'], by2['A']['x'] + by2['A']['w'],
                                f'行首 full 也不得盖住 b：a.w={by2["A"]["w"]}, b.x={by2["B"]["x"]}')
        self.assertLessEqual(by2['B']['x'] + by2['B']['w'], r2['gridLeft'] + r2['gridW'] + 1,
                             'b 不得溢出栅格（隐式新增轨道）')

    # 判据 7 防回归: 独占一行的 full 仍占满整行 ----------------------------
    def test_11_full_alone_still_spans_all(self):
        self._open(render({'grid': [['a', 'b'], [{'key': 'c', 'span': 'full'}]]}))
        r = self._cells()
        by = {i['label']: i for i in r['items']}
        self.assertLessEqual(abs(by['C']['w'] - r['gridW']), 2,
                             f'唯一格 full 应≈栅格宽（C={by["C"]["w"]}, grid={r["gridW"]}）')

    # 边界: 未知 key / 非法 grid 不崩 ---------------------------------------
    def test_08_unknown_key_and_bad_grid_are_safe(self):
        self._open(render({'grid': [['nope', 'a'], 'not-a-line', ['b']]}))
        r = self._cells()
        labels = [i['label'] for i in r['items']]
        self.assertIn('A', labels)
        self.assertIn('B', labels)
        self.assertNotIn('NOPE', labels)
        errs = self.driver.execute_script('return window.__testErrors || [];')
        self.assertEqual(errs, [], f'不得产生 JS 错误: {errs}')


if __name__ == '__main__':
    unittest.main()
