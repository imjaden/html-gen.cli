"""CL030 守卫: 外链安全收口 —— 属性注入（SEC-4）与同类 window.open 面（SEC-5）。

来源: 复审 cache/logs/review-cl028.log §二 新发现。
判据全部为「DOM 属性实测」：注入成功与否不看源码，只看渲染出来的属性集与 window.open 实参。
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

INJECT_URL = 'https://ex.example/a/" data-pwn="1" onmouseover="window.__inj=1'
INJECT_QUOTE = "x' onmouseover='window.__quot=1"

COLS = [
    {'key': 'name', 'label': '名称', 'width': '140px'},
    {'key': 'video', 'label': '视频', 'type': 'videos', 'width': '220px'},
    {'key': 'link', 'label': '链接', 'width': '160px'},
    {'key': 'actions', 'label': '操作', 'type': 'actions', 'width': '100px', 'actions': [
        {'label': '打开', 'icon': '🔗', 'hrefKey': 'link'},
        {'label': '复制', 'icon': '📋', 'copyKey': 'name'},
    ]},
]


def render(rows, click_mode='modal'):
    data = {
        'title': 'CL030 注入探针',
        'columns': COLS,
        'data': rows,
        'options': {'clickMode': click_mode, 'pageSize': 10},
    }
    tmp = Path(tempfile.mkdtemp(prefix='cl030_'))
    dj, out = tmp / 'd.json', tmp / 'o.html'
    dj.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
    r = subprocess.run([sys.executable, str(GEN), 'table', '-d', str(dj), '-o', str(out)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return out


class TestLinkSafety(unittest.TestCase):

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

    def _open(self, path, split=False):
        self.driver.get('file://' + str(path))
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#tbody tr')))
        self.driver.execute_script('localStorage.clear();')
        self.driver.get('file://' + str(path))
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#tbody tr')))
        time.sleep(0.3)
        self.driver.execute_script("""
          window.__opened = [];
          window.open = function(u, t) { window.__opened.push([u, t]); return null; };
        """)

    # SEC-4: title 属性逃逸 -------------------------------------------------
    def test_01_video_title_cannot_escape_attribute(self):
        rows = [{'name': 'A', 'link': 'https://ok.example',
                 'video': [{'url': INJECT_URL, 'title': 't1'}]}]
        self._open(render(rows))
        pill = self.driver.find_element(By.CSS_SELECTOR, '#tbody tr td .video-pill')
        self.assertIsNone(pill.get_attribute('onmouseover'), '不得注入 onmouseover 事件属性')
        self.assertIsNone(pill.get_attribute('data-pwn'), '不得注入 data-pwn 属性')
        self.assertEqual(pill.get_attribute('title'), INJECT_URL,
                         'title 应完整还原为原始 URL（转义不能截断值）')
        # 分栏详情同一口径
        self.driver.execute_script("document.querySelector('#tbody tr td').click();")
        time.sleep(0.6)
        links = self.driver.find_elements(By.CSS_SELECTOR, '#splitPreviewBody a.video-split-link')
        if links:
            self.assertIsNone(links[0].get_attribute('onmouseover'))
            self.assertEqual(links[0].get_attribute('title'), INJECT_URL)

    def test_02_action_button_cannot_escape_attribute(self):
        # copyKey 把 name 值注入 onclick（单引号包裹）—— 含 ' 时必须不跳出属性
        rows = [{'name': INJECT_QUOTE, 'link': 'https://ok.example', 'video': []}]
        self._open(render(rows))
        btns = self.driver.find_elements(By.CSS_SELECTOR, '#tbody tr td .action-btn')
        self.assertGreaterEqual(len(btns), 2, '应渲染两个操作按钮')
        for b in btns:
            self.assertIsNone(b.get_attribute('onmouseover'),
                              f'按钮不得注入 onmouseover：{b.get_attribute("outerHTML")[:160]}')

    # SEC-5: 同类 window.open 面 -------------------------------------------
    def test_03_action_hrefkey_unsafe_has_no_click_surface(self):
        rows = [{'name': 'A', 'link': 'javascript:window.__act=1', 'video': []}]
        self._open(render(rows))
        btn = self.driver.find_elements(By.CSS_SELECTOR, '#tbody tr td .action-btn')[0]
        self.assertIsNone(btn.get_attribute('onclick'), '非法 hrefKey 不得带 onclick')
        self.assertIn('action-btn-disabled', btn.get_attribute('class'), '非法目标按钮应标禁用态')
        btn.click()
        time.sleep(0.2)
        self.assertEqual(self.driver.execute_script('return window.__opened;'), [],
                         '非法 hrefKey 点击不得调用 window.open')

    def test_04_action_hrefkey_safe_opens_target(self):
        rows = [{'name': 'A', 'link': 'https://ok.example/p?q=1', 'video': []}]
        self._open(render(rows))
        btn = self.driver.find_elements(By.CSS_SELECTOR, '#tbody tr td .action-btn')[0]
        self.assertIsNotNone(btn.get_attribute('onclick'), '合法目标必须可点')
        self.assertNotIn('action-btn-disabled', btn.get_attribute('class'))
        btn.click()
        time.sleep(0.2)
        self.assertEqual(self.driver.execute_script('return window.__opened;'),
                         [['https://ok.example/p?q=1', '_blank']])

    def test_05_tab_mode_row_url_unsafe_blocked(self):
        cols = [dict(c) for c in COLS]
        cols[0] = {'key': 'name', 'label': '名称', 'width': '140px', 'onClick': 'url'}
        data_rows = [
            {'name': '坏行', 'link': 'https://ok.example', 'video': [], 'url': 'javascript:window.__tab=1'},
            {'name': '好行', 'link': 'https://ok.example', 'video': [], 'url': 'https://ok.example/t'},
        ]
        path = render(data_rows, click_mode='tab')
        # 用自定义列重渲染
        data = {'title': 'CL030 tab', 'columns': cols, 'data': data_rows,
                'options': {'clickMode': 'tab', 'pageSize': 10}}
        tmp = Path(tempfile.mkdtemp(prefix='cl030tab_'))
        dj, out = tmp / 'd.json', tmp / 'o.html'
        dj.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
        r = subprocess.run([sys.executable, str(GEN), 'table', '-d', str(dj), '-o', str(out)],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self._open(out)
        # 注: 该列 onClick:'url' 会让单元格带 openSplitAt + stopPropagation，Selenium 点 td 打不到行事件
        # ⇒ 用 JS 直接在 <tr> 上派发 click，测的才是 row click 路径。
        self.driver.execute_script("document.querySelectorAll('#tbody tr')[0].click();")
        time.sleep(0.3)
        self.assertEqual(self.driver.execute_script('return window.__opened;'), [],
                         'row.url 为 javascript: 时点击行不得调用 window.open')
        self.driver.execute_script("document.querySelectorAll('#tbody tr')[1].click();")
        time.sleep(0.3)
        self.assertEqual(self.driver.execute_script('return window.__opened;'),
                         [['https://ok.example/t', '_blank']], '合法 row.url 应正常开新标签')


if __name__ == '__main__':
    unittest.main()
