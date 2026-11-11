"""CL026 守卫: 媒体列 —— type=image 缩略图/灯箱/协议白名单; videos 项 cover 封面外链。

来源: 用户 2026-11-09 提出「image 列类型」与「video 列支持封面 + 点击外链」两条需求，
路线取推荐项 (b): 新增 image 类型 + 扩展既有 videos 项 cover，不新增单数 video 类型。
判据全部为行为断言（渲染后 DOM / 点击事件实测）。
"""
import base64
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

SVG = ('<svg xmlns="http://www.w3.org/2000/svg" width="120" height="60">'
       '<rect width="120" height="60" fill="#4f46e5"/></svg>')
IMG = 'data:image/svg+xml;base64,' + base64.b64encode(SVG.encode()).decode()
COVER = ('data:image/svg+xml;base64,' +
         base64.b64encode(SVG.replace('#4f46e5', '#0ea5e9').encode()).decode())

COLS = [
    {'key': 'name', 'label': '名称', 'width': '120px'},
    {'key': 'pic', 'label': '图片', 'type': 'image', 'width': '140px'},
    {'key': 'video', 'label': '视频', 'type': 'videos', 'width': '200px'},
]
ROWS = [
    {'name': 'A 单图', 'pic': IMG,
     'video': [{'url': 'https://example.com/v1', 'title': '带封面', 'platform': 'bilibili', 'cover': COVER}]},
    {'name': 'B 对象图', 'pic': {'src': IMG, 'alt': '封面替代文本'},
     'video': [{'url': 'https://example.com/v2', 'title': '无封面', 'platform': 'youtube'}]},
]


def render(rows=None, cols=None, extra_options=None):
    data = {
        'title': 'CL026 媒体列探针',
        'columns': cols or COLS,
        'data': rows or ROWS,
        'options': {'clickMode': 'split', 'pageSize': 20},
    }
    data['options'].update(extra_options or {})
    tmp = Path(tempfile.mkdtemp(prefix='cl026_'))
    dj, out = tmp / 'd.json', tmp / 'o.html'
    dj.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
    r = subprocess.run([sys.executable, str(GEN), 'table', '-d', str(dj), '-o', str(out)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return out


class TestMediaColumns(unittest.TestCase):

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

    def _load(self, path, density=None):
        self.driver.get('file://' + str(path))
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#tbody tr')))
        self.driver.execute_script('localStorage.clear();')
        if density:
            self.driver.execute_script(
                "localStorage.setItem('html-gen:table:density', arguments[0]);", density)
        self.driver.get('file://' + str(path))
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#tbody tr')))
        time.sleep(0.3)

    # image 列 ------------------------------------------------------------
    def test_01_image_cell_renders_thumbnail(self):
        self._load(render())
        imgs = self.driver.find_elements(By.CSS_SELECTOR, '#tbody tr td.cell-media img.cell-thumb')
        self.assertEqual(len(imgs), 2, f'两行都应有缩略图，实得 {len(imgs)}')
        nat = self.driver.execute_script('return [arguments[0].naturalWidth, arguments[0].naturalHeight];', imgs[0])
        self.assertEqual(nat, [120, 60], f'缩略图应真实加载（naturalWidth 120x60），实得 {nat}')
        h = self.driver.execute_script('return Math.round(arguments[0].getBoundingClientRect().height);', imgs[0])
        self.assertEqual(h, 22, f'默认密度缩略图高应 22px（不撑行），实得 {h}')

    def test_02_image_object_form_uses_alt(self):
        self._load(render())
        imgs = self.driver.find_elements(By.CSS_SELECTOR, '#tbody tr td.cell-media img.cell-thumb')
        self.assertEqual(imgs[1].get_attribute('alt'), '封面替代文本')

    def test_03_unsafe_protocol_rejected(self):
        rows = [dict(ROWS[0], pic='javascript:alert(1)')]
        self._load(render(rows=rows))
        imgs = self.driver.find_elements(By.CSS_SELECTOR, '#tbody tr td.cell-media img')
        self.assertEqual(len(imgs), 0, 'javascript: 伪协议不得渲染为 <img>')

    def test_04_click_thumbnail_opens_lightbox(self):
        self._load(render())
        thumb = self.driver.find_element(By.CSS_SELECTOR, '#tbody tr td.cell-media img.cell-thumb')
        thumb.click()
        time.sleep(0.2)
        self.assertTrue(self.driver.execute_script(
            "return document.getElementById('lightbox').classList.contains('active');"), '点击缩略图应开灯箱')
        self.assertTrue(self.driver.execute_script(
            "return document.getElementById('lightboxImg').getAttribute('src');").startswith('data:image/svg'))
        self.driver.execute_script('window.closeLightbox();')
        time.sleep(0.15)
        self.assertFalse(self.driver.execute_script(
            "return document.getElementById('lightbox').classList.contains('active');"), '关闭后灯箱应隐藏')

    def test_05_dense_density_shrinks_thumbnail(self):
        self._load(render(), density='compact')
        h = self.driver.execute_script(
            "return Math.round(document.querySelector('#tbody tr td.cell-media img.cell-thumb')"
            ".getBoundingClientRect().height);")
        self.assertEqual(h, 18, f'紧凑密度缩略图高应 18px，实得 {h}')

    def test_06_image_in_split_detail_shows_large_image(self):
        self._load(render())
        self.driver.find_element(By.CSS_SELECTOR, '#tbody tr td:nth-child(1)').click()
        time.sleep(0.6)
        imgs = self.driver.find_elements(By.CSS_SELECTOR, '#splitPreviewBody img.kv-img')
        self.assertEqual(len(imgs), 1, '分栏详情应出大图')
        imgs[0].click()
        time.sleep(0.2)
        self.assertTrue(self.driver.execute_script(
            "return document.getElementById('lightbox').classList.contains('active');"), '分栏大图点击应开灯箱')

    # videos 列 cover ------------------------------------------------------
    def test_07_video_cover_in_cell_and_click_opens_url(self):
        self._load(render())
        covers = self.driver.find_elements(By.CSS_SELECTOR, '#tbody tr td img.video-cover-thumb')
        self.assertEqual(len(covers), 1, '仅带 cover 的视频出封面缩略图')
        # 拦截 window.open，验证点击封面外链到该视频
        self.driver.execute_script("""
          window.__opened = [];
          window.open = function(u, t) { window.__opened.push([u, t]); return null; };
        """)
        covers[0].click()
        time.sleep(0.2)
        opened = self.driver.execute_script('return window.__opened;')
        self.assertEqual(opened, [['https://example.com/v1', '_blank']],
                         f'封面点击应外链到视频地址，实得 {opened}')

    def test_08_videos_without_cover_keep_pills(self):
        self._load(render())
        pills = self.driver.find_elements(By.CSS_SELECTOR, '#tbody tr td .video-pill')
        self.assertGreaterEqual(len(pills), 2, '无 cover 的视频仍渲染 pill（向后兼容）')
        covers = self.driver.find_elements(By.CSS_SELECTOR, '#tbody tr td img.video-cover-thumb')
        self.assertEqual(len(covers), 1, '仅 1 行有 cover')

    def test_09_video_cover_in_split_detail(self):
        self._load(render())
        self.driver.find_element(By.CSS_SELECTOR, '#tbody tr td:nth-child(1)').click()
        time.sleep(0.6)
        covers = self.driver.find_elements(By.CSS_SELECTOR, '#splitPreviewBody img.kv-video-cover')
        self.assertEqual(len(covers), 1, '分栏详情应渲染视频封面')
        self.driver.execute_script("""
          window.__opened = [];
          window.open = function(u, t) { window.__opened.push([u, t]); return null; };
        """)
        covers[0].click()
        time.sleep(0.2)
        opened = self.driver.execute_script('return window.__opened;')
        self.assertEqual(opened, [['https://example.com/v1', '_blank']])

    # 消费面 ---------------------------------------------------------------
    def test_10_image_column_excluded_from_search(self):
        self._load(render())
        # 'svg+xml' 只出现在 image 列的 data URI 里：若 image 参与搜索应命中 2 行，
        # 排除后（与 videos 同口径）应 0 行 —— 这才是「已排除」的判别性证据。
        self.driver.find_element(By.CSS_SELECTOR, '#searchInput').send_keys('svg+xml')
        time.sleep(0.5)
        after = len(self.driver.find_elements(By.CSS_SELECTOR, '#tbody tr'))
        self.assertEqual(after, 0,
                         'image 列不参与默认搜索：仅图片 URL 含的关键词不应命中任何行')

    def test_11_sort_by_image_column_orders_by_media_text(self):
        # CL028 (评审 FR-2): 原断言（行数不变 + 无 [object Object]）零判别力 ——
        # String(对象) 排序既不抛错也不丢行，把 isMedia 分支整段置死照样绿。
        # 改为「媒体文本序 ≠ String() 序」的判别性断言：alt AAA 必须排在 ZZZ 之前。
        rows = [
            {'name': '行B', 'pic': {'src': IMG, 'alt': 'ZZZ'}, 'video': []},
            {'name': '行A', 'pic': {'src': IMG, 'alt': 'AAA'}, 'video': []},
        ]
        self._load(render(rows=rows))
        first_before = self.driver.find_element(By.CSS_SELECTOR, '#tbody tr td:nth-child(1)').text
        self.assertEqual(first_before, '行B', '数据序：行B 在前（若反过来本用例不成立）')
        self.driver.execute_script("""
          var ths = document.querySelectorAll('.data-table thead th');
          for (var i = 0; i < ths.length; i++) { if (ths[i].textContent.trim() === '图片') { ths[i].click(); break; } }
        """)
        time.sleep(0.4)
        cells = self.driver.execute_script(
            "return Array.prototype.map.call(document.querySelectorAll('#tbody tr td:nth-child(1)'),"
            " function(td){ return td.textContent.trim(); });")
        self.assertEqual(cells[0], '行A',
                         f'按 image 列升序应按 alt 文本（AAA<ZZZ）排序，实得顺序 {cells}')

    def test_12_unsafe_video_url_has_no_click_surface(self):
        # CL028 (评审 SEC-1): video.url 非 http(s) ⇒ 不允许出现可点击外链面
        rows = [{'name': 'A', 'pic': IMG,
                 'video': [{'url': 'javascript:window.__viaOpen=1', 'title': '坏目标', 'cover': COVER}]}]
        self._load(render(rows=rows))
        self.driver.execute_script("""
          window.__opened = [];
          window.open = function(u, t) { window.__opened.push([u, t]); return null; };
        """)
        pills = self.driver.find_elements(By.CSS_SELECTOR, '#tbody tr td .video-pill')
        self.assertEqual(len(pills), 1, '目标非法时仍应显示 pill 文案（只是不可点）')
        self.assertFalse(pills[0].get_attribute('onclick'), '非法目标不得带 onclick')
        covers = self.driver.find_elements(By.CSS_SELECTOR, '#tbody tr td img.video-cover-thumb')
        for c in covers:
            self.assertFalse(c.get_attribute('onclick'), '非法目标下封面不得带 onclick')
            c.click()
        time.sleep(0.2)
        self.assertEqual(self.driver.execute_script('return window.__opened;'), [],
                         '非法目标点击不得调用 window.open')
        # 分栏详情同口径
        self.driver.find_element(By.CSS_SELECTOR, '#tbody tr td:nth-child(1)').click()
        time.sleep(0.6)
        links = self.driver.find_elements(By.CSS_SELECTOR, '#splitPreviewBody a.video-split-link')
        self.assertEqual(len(links), 0, '分栏详情不得渲染非法目标的 <a>')
        self.assertEqual(self.driver.execute_script('return window.__opened;'), [])

    def test_13_unsafe_cover_protocol_rejected(self):
        # CL028 (评审 FR-4/SEC-3): cover 也走白名单，javascript: 不得渲染为 <img>
        rows = [{'name': 'A', 'pic': IMG,
                 'video': [{'url': 'https://example.com/v1', 'title': '有坏封面',
                            'cover': 'javascript:window.__viaCover=1'}]}]
        self._load(render(rows=rows))
        self.assertEqual(len(self.driver.find_elements(By.CSS_SELECTOR, '#tbody tr td img.video-cover-thumb')), 0,
                         'cover 为伪协议时不得渲染封面图')
        self.driver.find_element(By.CSS_SELECTOR, '#tbody tr td:nth-child(1)').click()
        time.sleep(0.6)
        self.assertEqual(len(self.driver.find_elements(By.CSS_SELECTOR, '#splitPreviewBody img.kv-video-cover')), 0,
                         '分栏详情同样不得渲染非法封面')

    def test_14_non_whitelisted_data_subtype_rejected(self):
        # CL028 (评审 SEC-2): data: 收窄到 png/jpeg/gif/webp/svg+xml —— 其它子类型不渲染
        cols = [dict(c) for c in COLS]
        rows = [{'name': 'A', 'pic': 'data:image/bmp;base64,AAAA', 'video': []},
                {'name': 'B', 'pic': 'data:image/png;base64,iVBORw0KGgo=', 'video': []}]
        self._load(render(rows=rows, cols=cols))
        imgs = self.driver.find_elements(By.CSS_SELECTOR, '#tbody tr td.cell-media img.cell-thumb')
        self.assertEqual(len(imgs), 1, 'data:image/bmp 不在白名单 ⇒ 只应有 png 那一行的图')
        self.assertIn('image/png', imgs[0].get_attribute('src'))


if __name__ == '__main__':
    unittest.main()
