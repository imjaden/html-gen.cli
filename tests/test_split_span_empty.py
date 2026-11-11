"""CL025 守卫: 分栏详情 ②空值不占格 / ③splitSpan 跨列权重 / ⑦三条几何判据。

来源: daily-checker 转交件 20261111-to-html-gen-layout-table-lessons（②③⑦）。
判据全部为行为断言（渲染后 DOM 实测），不看源码字面量。
"""
import json
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

ROOT = Path(__file__).resolve().parent.parent
GEN = ROOT / 'html-gen.py'
CHROMEDRIVER = '/Users/jadenli/CodeSpace/script-miner/cache/chromedriver/chromedriver'

COLS = [
    {'key': 'name', 'label': '名称', 'width': '120px'},
    {'key': 'emptyCol', 'label': '空列', 'width': '120px'},
    {'key': 'w2', 'label': '权重2', 'width': '120px', 'splitSpan': 2},
    {'key': 'full1', 'label': '整行', 'width': '120px', 'splitSpan': 'full'},
]
ROW = {'name': '行1', 'emptyCol': '', 'w2': 'W', 'full1': 'F'}


def render(extra_options=None, row=None):
    data = {
        'title': 'CL025 探针',
        'columns': COLS,
        'data': [row or ROW],
        'options': {'clickMode': 'split', 'pageSize': 10},
    }
    data['options'].update(extra_options or {})
    tmp = Path(tempfile.mkdtemp(prefix='cl025_'))
    dj = tmp / 'd.json'
    out = tmp / 'o.html'
    dj.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
    r = subprocess.run([sys.executable, str(GEN), 'table', '-d', str(dj), '-o', str(out)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return out


class TestSplitSpanAndEmpty(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        opts = Options()
        opts.add_argument('--headless=new')
        opts.add_argument('--no-sandbox')
        opts.add_argument('--disable-dev-shm-usage')
        cls.driver = webdriver.Chrome(service=Service(CHROMEDRIVER), options=opts)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def setUp(self):
        self.driver.set_window_size(1440, 900)

    def _open_split(self, path):
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

    def _items(self):
        return self.driver.execute_script("""
          var b=document.getElementById('splitPreviewBody');
          var out=[];
          Array.prototype.forEach.call(b.querySelectorAll('.kv-item'), function(el){
            var r=el.getBoundingClientRect();
            out.push({label:(el.querySelector('.kv-label')||{}).textContent||'',
                      x:Math.round(r.x), y:Math.round(r.y),
                      w:Math.round(r.width), h:Math.round(r.height),
                      top:Math.round(r.top)});
          });
          var list=b.querySelector('.kv-list');
          var lr=list?list.getBoundingClientRect():null;
          var br=b.getBoundingClientRect();
          return {items:out, listW: lr?Math.round(lr.width):0,
                  bodyW: Math.round(br.width), bodyClient: b.clientWidth,
                  bodyScroll: b.scrollWidth};
        """)

    # ② 空值不占格 -------------------------------------------------------
    def test_01_empty_cell_skipped_when_option_on(self):
        self._open_split(render({'hideEmptyCells': True}))
        r = self._items()
        labels = [i['label'] for i in r['items']]
        self.assertEqual(len(labels), 3, f'空值列应整格不渲染，实得 {labels}')
        self.assertNotIn('空列', labels)
        self.assertEqual(labels, ['名称', '权重2', '整行'])

    def test_02_default_keeps_backward_compat(self):
        self._open_split(render())          # 不传 hideEmptyCells = 既有行为
        r = self._items()
        self.assertEqual(len(r['items']), 4, '缺省必须保持全列渲染（向后兼容）')
        self.assertIn('空列', [i['label'] for i in r['items']])

    def test_03_empty_value_reordered_to_remaining_tracks(self):
        self._open_split(render({'hideEmptyCells': True}))
        r = self._items()
        by = {i['label']: i for i in r['items']}
        # 空列被移除后，权重2 与整行仍占据各自轨道（不被压成 0 宽）
        for lab in ('名称', '权重2', '整行'):
            self.assertGreater(by[lab]['w'], 40, f'{lab} 宽 {by[lab]["w"]}px 过窄')
        self.assertAlmostEqual(by['整行']['w'], r['listW'], delta=2,
                               msg='splitSpan="full" 必须占满整行')

    # ③ splitSpan 权重 -----------------------------------------------------
    def test_04_split_span_weight_doubles_width(self):
        self._open_split(render())
        r = self._items()
        by = {i['label']: i for i in r['items']}
        plain = by['名称']['w']
        self.assertGreater(by['权重2']['w'], plain * 1.4,
                           f'splitSpan=2 应显著宽于单轨 ({by["权重2"]["w"]} vs {plain})')
        self.assertAlmostEqual(by['整行']['w'], r['listW'], delta=2)

    def test_05_legacy_split_full_still_full_row(self):
        cols = [dict(c) for c in COLS]
        legacy = {'key': 'legacyFull', 'label': '旧整行', 'width': '120px', 'splitFull': True}
        row = dict(ROW, legacyFull='L')
        data_cols = cols[:2] + [legacy]
        tmp = Path(tempfile.mkdtemp(prefix='cl025_legacy_'))
        dj, out = tmp / 'd.json', tmp / 'o.html'
        dj.write_text(json.dumps({'title': 'legacy', 'columns': data_cols, 'data': [row],
                                  'options': {'clickMode': 'split', 'pageSize': 10}},
                                 ensure_ascii=False), encoding='utf-8')
        r0 = subprocess.run([sys.executable, str(GEN), 'table', '-d', str(dj), '-o', str(out)],
                            capture_output=True, text=True)
        self.assertEqual(r0.returncode, 0, r0.stderr)
        self._open_split(out)
        res = self._items()
        by = {i['label']: i for i in res['items']}
        self.assertAlmostEqual(by['旧整行']['w'], res['listW'], delta=2,
                               msg='旧 splitFull 必须仍等价 "full"（向后兼容）')

    # ⑦ 三条几何判据 -------------------------------------------------------
    # 注: 转交件的「每行宽 == 容器宽 ±2」针对其**显式行模型**（每行独立 grid）。
    # 本模板分栏详情是扁平 auto-fill 栅格（行边界由流隐式形成），等价判据改写为
    # 「行内不出界 + 行内不重叠 + 满行项（splitSpan=full）恰等于容器宽」（最后一条见 test_03/04）。
    def test_06_geometry_items_inside_container(self):
        self._open_split(render())
        r = self._items()
        self.assertGreater(len(r['items']), 0)
        body_left = self.driver.execute_script(
            "return Math.round(document.getElementById('splitPreviewBody')"
            ".getBoundingClientRect().left);")
        body_right = body_left + r['bodyW']
        for i in r['items']:
            self.assertGreaterEqual(i['x'], body_left - 1, f'{i["label"]} 左出界')
            self.assertLessEqual(i['x'] + i['w'], body_right + 1, f'{i["label"]} 右出界')
        # 同一视觉行内不得横向重叠
        rows = {}
        for i in r['items']:
            rows.setdefault(i['top'], []).append(i)
        for top, group in rows.items():
            group.sort(key=lambda g: g['x'])
            for a, b in zip(group, group[1:]):
                self.assertGreaterEqual(b['x'], a['x'] + a['w'] - 1,
                                        f'top={top} 行内 {a["label"]} 与 {b["label"]} 横向重叠')

    def test_07_geometry_adjacent_rows_not_same_top(self):
        self._open_split(render())
        r = self._items()
        tops = sorted({i['top'] for i in r['items']})
        self.assertGreaterEqual(len(tops), 2, '应至少形成 2 个视觉行')
        # 判据 2: 不同视觉行不得同处一条线 —— 任意两项 rect 不得同时横向与纵向重叠
        items = r['items']
        for a in range(len(items)):
            for b in range(a + 1, len(items)):
                i, j = items[a], items[b]
                xov = min(i['x'] + i['w'], j['x'] + j['w']) - max(i['x'], j['x'])
                yov = min(i['y'] + i['h'], j['y'] + j['h']) - max(i['y'], j['y'])
                self.assertFalse(xov > 1 and yov > 1,
                                 f'{i["label"]} 与 {j["label"]} 矩形重叠 (xov={xov}, yov={yov})')

    def test_08_geometry_no_horizontal_overflow_narrow(self):
        path = render()
        self.driver.set_window_size(900, 800)
        self._open_split(path)
        r = self._items()
        # 判据 3: 窄窗不横向溢出
        self.assertLessEqual(r['bodyScroll'], r['bodyClient'] + 1,
                             f'窄窗横向溢出 scrollWidth={r["bodyScroll"]} > clientWidth={r["bodyClient"]}')

    def test_09_all_empty_renders_no_nodes(self):
        row = {'name': '行1', 'emptyCol': '', 'w2': '', 'full1': ''}
        self._open_split(render({'hideEmptyCells': True}, row=row))
        r = self._items()
        # 除 name 外全空 ⇒ 只渲染名称一格，不产生空格子/空行
        self.assertEqual([i['label'] for i in r['items']], ['名称'])


if __name__ == '__main__':
    unittest.main()
