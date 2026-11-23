"""slimdown 方案页 v1.3 回归：数据契约（按星期 / 按主题）+ 视图切换与点击态记忆。

数据来源：scripts/slimdown-import-v13.py（两份参考页 → data/_slimdown-plan.json + 动作库 append）。
页面：demos/slimdown/plan.html（scripts/build-slimdown.py 由 _src/{plan.tpl,plan.css,state.js,shot.js,plan.js} 生成）。
"""
import json
import threading
import time
import unittest
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from conftest import chromedriver_service

PROJECT = Path(__file__).resolve().parent.parent
DATA = PROJECT / 'data'
DEMOS = PROJECT / 'demos'
PAGE = DEMOS / 'slimdown' / 'plan.html'


class _Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *args, **kwargs):
        pass


class TestSlimdownData(unittest.TestCase):
    """数据契约：不启浏览器，改坏数据先在这里红。"""

    @classmethod
    def setUpClass(cls):
        cls.plan = json.loads((DATA / '_slimdown-plan.json').read_text(encoding='utf-8'))
        cls.ex = json.loads((DATA / '_slimdown-exercises.json').read_text(encoding='utf-8'))
        cls.html = PAGE.read_text(encoding='utf-8')

    def test_01_presets(self):
        ids = [p['id'] for p in self.plan['presets']]
        self.assertEqual(ids, ['home', 'strength'])
        self.assertEqual(self.plan['defaultPreset'], 'home')
        home = [p for p in self.plan['presets'] if p['id'] == 'home'][0]
        self.assertEqual(len(home['days']), 7)

    def test_02_home_week_shape(self):
        home = [p for p in self.plan['presets'] if p['id'] == 'home'][0]
        items = sum(len(d.get('items') or []) for d in home['days'])
        self.assertEqual(items, 52)                      # 参考页七天共 52 条
        rest = [d for d in home['days'] if d.get('rest')]
        self.assertEqual(len(rest), 1)
        self.assertEqual(rest[0]['key'], 'sun')
        self.assertEqual(len(rest[0]['recover']), 5)
        for d in home['days']:
            if d.get('rest'):
                continue
            self.assertEqual(d['setsHint'], '3–5')       # v1.3 是全天统一建议组数
            self.assertGreaterEqual(len(d['items']), 8)

    def test_03_items_carry_muscle_and_reps(self):
        home = [p for p in self.plan['presets'] if p['id'] == 'home'][0]
        for d in home['days']:
            for it in d.get('items') or []:
                self.assertTrue(it['id'].startswith('ex'))
                self.assertTrue(it['reps'])
                self.assertTrue(it['muscle'])
                self.assertNotIn('sets', it)             # v1.3 不给动作级组数

    def test_04_strength_preset_kept(self):
        st = [p for p in self.plan['presets'] if p['id'] == 'strength'][0]
        self.assertEqual(len(st['days']), 7)
        self.assertEqual(sum(len(d['items']) for d in st['days']), 25)   # 旧七日原样保留
        self.assertTrue(all('sets' in it for d in st['days'] for it in d['items']))

    def test_05_themes(self):
        th = self.plan['themes']
        self.assertEqual(len(th), 4)
        self.assertEqual([len(t['items']) for t in th], [8, 13, 12, 8])
        for t in th:
            self.assertTrue(t['video']['url'].startswith('https://www.douyin.com/video/'))
            for it in t['items']:
                self.assertTrue(it['cn'] and it['en'] and it['m'])

    def test_06_exercise_library_appended(self):
        rows = self.ex['data']
        self.assertEqual(len(rows), 80)
        self.assertEqual([r['id'] for r in rows], ['ex%02d' % i for i in range(1, 81)])
        new = [r for r in rows if r['theme'] == '居家自重']
        self.assertEqual(len(new), 8)
        self.assertIn('80 个动作 · 11 个主题', self.ex['subtitle'])
        self.assertIn('居家自重', [t['label'] for t in self.ex['tabs']])

    def test_07_page_snapshot_matches_data(self):
        # 断言串一律小写短串 + assertTrue(msg)，失败时不把整个 HTML 倒进日志
        self.assertTrue(self.plan['version'] in self.html, '改了数据没重建')
        for marker in ('id="viewSeg"', 'id="themeRow"', 'id="shotHost"',
                       'slimdown:ui:v2', 'SB.shot', '"setsHint":"3–5"', 'theme-card'):
            self.assertTrue(marker in self.html, marker)
        for t in self.plan['themes']:
            self.assertTrue(t['video']['url'] in self.html, t['video']['url'])
        self.assertTrue('{{' not in self.html, '占位符未替换')


class TestSlimdownPage(unittest.TestCase):
    """真页面：视图切换 / 刷新保持 / 打卡 / 面板可用性。"""

    @classmethod
    def setUpClass(cls):
        handler = partial(_Quiet, directory=str(DEMOS))
        cls.httpd = ThreadingHTTPServer(('127.0.0.1', 0), handler)
        cls.port = cls.httpd.server_address[1]
        threading.Thread(target=cls.httpd.serve_forever, daemon=True).start()
        opts = Options()
        opts.add_argument('--headless=new')
        opts.add_argument('--no-sandbox')
        opts.add_argument('--disable-dev-shm-usage')
        opts.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
        cls.driver = webdriver.Chrome(service=chromedriver_service(), options=opts)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        cls.httpd.shutdown()

    def setUp(self):
        self.driver.set_window_size(1440, 900)
        self.driver.get(self.url())
        self.driver.execute_script('localStorage.clear();')
        self.driver.get(self.url())
        WebDriverWait(self.driver, 8).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#weekRow .day-card')))
        time.sleep(0.3)
        self.driver.execute_script(
            'window.__testErrors=[];window.onerror=function(m){window.__testErrors.push(String(m));};')

    # ── helpers ──
    def url(self):
        return f'http://127.0.0.1:{self.port}/slimdown/plan.html'

    def js(self, code):
        return self.driver.execute_script('return ' + code)

    def errors(self):
        errs = self.js('window.__testErrors') or []
        severe = [l['message'] for l in self.driver.get_log('browser') if l['level'] == 'SEVERE']
        return list(errs) + severe

    def ui_state(self):
        raw = self.js("localStorage.getItem('slimdown:ui:v2')")
        return json.loads(raw) if raw else {}

    # ── 结构 ──
    def test_10_week_view(self):
        cards = self.driver.find_elements(By.CSS_SELECTOR, '#weekRow .day-card')
        self.assertEqual(len(cards), 7)
        rows = self.js("[].map.call(document.querySelectorAll('#weekRow .day-card'),"
                       "function(c){return c.querySelectorAll('.d-list li').length;})")
        self.assertEqual(rows, [9, 9, 8, 9, 8, 9, 0])       # 周日是恢复日
        self.assertEqual(self.js("document.querySelectorAll('.r-list li').length"), 5)
        self.assertEqual(self.js("document.querySelectorAll('.today-chip').length"), 1)
        self.assertIn('建议 3–5 组', self.js(
            "document.querySelector('#weekRow .day-card .d-chip').textContent"))
        self.assertEqual(self.errors(), [])

    def test_11_theme_view_switch(self):
        self.js("document.querySelector('#viewSeg button[data-view=theme]').click()")
        time.sleep(0.3)
        self.assertEqual(len(self.driver.find_elements(By.CSS_SELECTOR, '#themeRow .theme-card')), 4)
        self.assertTrue(self.js("document.getElementById('weekRow').hidden"))
        self.assertTrue(self.js("document.getElementById('presetPick').hidden"))
        self.assertTrue(self.js("document.getElementById('fabEdit').hidden"))
        self.assertEqual(self.js("document.querySelectorAll('.video-link').length"), 4)
        self.assertEqual(self.ui_state()['view'], 'theme')
        self.assertEqual(self.errors(), [])

    def test_12_reload_keeps_view_and_skin(self):
        self.js("document.querySelector('#viewSeg button[data-view=theme]').click()")
        self.js("(function(){var s=document.getElementById('themeSel');s.value='indigo';"
                "s.dispatchEvent(new Event('change'));})()")
        time.sleep(0.3)
        self.driver.refresh()
        WebDriverWait(self.driver, 8).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#themeRow .theme-card')))
        time.sleep(0.3)
        self.assertEqual(self.js("document.documentElement.getAttribute('data-view')"), 'theme')
        self.assertFalse(self.js("document.getElementById('themeRow').hidden"))
        self.assertEqual(self.js("document.documentElement.getAttribute('data-theme')"), 'indigo')
        self.assertEqual(self.js("document.getElementById('themeSel').value"), 'indigo')
        self.assertEqual(self.errors(), [])

    def test_13_checkin_persists(self):
        self.js("document.querySelector('#weekRow .day-card[data-day=wed] .chk').click()")
        time.sleep(0.2)
        self.assertEqual(self.js(
            "document.querySelector('#weekRow .day-card[data-day=wed]').classList.contains('done')"), True)
        self.assertFalse(self.js("document.getElementById('panelMask').classList.contains('open')"))
        self.driver.refresh()
        WebDriverWait(self.driver, 8).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#weekRow .day-card')))
        time.sleep(0.3)
        self.assertEqual(self.js(
            "document.querySelector('#weekRow .day-card[data-day=wed]').classList.contains('done')"), True)
        self.assertEqual(self.js(
            "document.querySelector('#weekRow .day-card[data-day=wed] .chk').getAttribute('aria-pressed')"),
            'true')

    def test_14_day_panel_and_day_memory(self):
        self.js("document.querySelector('#weekRow .day-card[data-day=thu]').click()")
        time.sleep(0.3)
        self.assertTrue(self.js("document.getElementById('panelMask').classList.contains('open')"))
        self.assertIn('周四', self.js("document.getElementById('panelTitle').textContent"))
        self.assertEqual(self.js("document.querySelectorAll('#planList .plan-row').length"), 9)
        self.assertEqual(self.ui_state()['day'], 'thu')
        self.js("document.getElementById('panelClose').click()")
        self.driver.refresh()
        WebDriverWait(self.driver, 8).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#weekRow .day-card')))
        time.sleep(0.3)
        self.assertEqual(self.ui_state()['day'], 'thu')

    def test_15_theme_panel_export_gates(self):
        self.js("document.querySelector('#viewSeg button[data-view=theme]').click()")
        time.sleep(0.2)
        self.js("document.getElementById('fabShot').click()")
        time.sleep(0.4)
        self.assertIn('主题跟练', self.js("document.getElementById('panelTitle').textContent"))
        self.assertEqual(self.js("document.querySelectorAll('#previewHost .card').length"), 4)
        self.assertTrue(self.js("document.getElementById('btnSavePlan').disabled"))
        self.assertTrue(self.js("document.getElementById('btnShare').disabled"))
        self.assertFalse(self.js("document.getElementById('btnDownloadImg').disabled"))
        self.assertFalse(self.js("document.getElementById('btnDownloadEach').hidden"))

    def test_16_preset_switch(self):
        self.js("(function(){var s=document.getElementById('presetSel');s.value='strength';"
                "s.dispatchEvent(new Event('change'));})()")
        time.sleep(0.3)
        self.assertEqual(self.js("document.querySelectorAll('#weekRow .day-card .d-list li').length"), 25)
        self.assertIn('下肢 A', self.js("document.querySelector('#weekRow .day-card .b-tag').textContent"))
        self.assertEqual(self.ui_state()['preset'], 'strength')
        self.driver.refresh()
        WebDriverWait(self.driver, 8).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#weekRow .day-card')))
        time.sleep(0.3)
        self.assertEqual(self.ui_state()['preset'], 'strength')
        self.assertEqual(self.errors(), [])


if __name__ == '__main__':
    unittest.main()
