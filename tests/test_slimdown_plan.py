"""slimdown 方案页 v1.3 回归：数据契约（按星期 / 按主题）+ 视图切换与点击态记忆。

数据来源：scripts/slimdown-import-v13.py（两份参考页 → data/_slimdown-plan.json + 动作库 append）。
页面：demos/slimdown/index.html（scripts/build-slimdown.py 由 _src/{plan.tpl,plan.css,state.js,shot.js,plan.js} 生成；
plan.html 为旧链接跳转桩）。
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
from conftest import chromedriver_service, is_external_net_failure

PROJECT = Path(__file__).resolve().parent.parent
DATA = PROJECT / 'data'
DEMOS = PROJECT / 'demos'
PAGE = DEMOS / 'slimdown' / 'index.html'


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
        # v1.4：力量版预设已移除，只剩 home
        ids = [p['id'] for p in self.plan['presets']]
        self.assertEqual(ids, ['home'])
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

    def test_04_redirect_stub_keeps_old_links(self):
        stub = (DEMOS / 'slimdown' / 'plan.html').read_text(encoding='utf-8')
        self.assertIn('slimdown:redirect auto', stub)          # 带标记，别名清理不误删
        self.assertIn("location.replace('index.html' + location.search + location.hash)", stub)
        self.assertIn('noindex', stub)                         # 跳转桩不抢 canonical
        self.assertIn('已迁目录首页', stub)                      # registry 行的标题口径

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
        for marker in ('id="viewSeg"', 'id="themeRow"', 'id="shotHost"', 'id="shotList"',
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
        return f'http://127.0.0.1:{self.port}/slimdown/index.html'

    def js(self, code):
        return self.driver.execute_script('return ' + code)

    def to_week(self):
        """v1.5 起默认视图是主题，周视图相关用例先切过去。"""
        self.js("document.querySelector('#viewSeg button[data-view=week]').click()")
        time.sleep(0.3)

    def errors(self):
        errs = self.js('window.__testErrors') or []
        severe = [l['message'] for l in self.driver.get_log('browser')
                  if l['level'] == 'SEVERE' and not is_external_net_failure(l['message'])]
        return list(errs) + severe

    def ui_state(self):
        raw = self.js("localStorage.getItem('slimdown:ui:v2')")
        return json.loads(raw) if raw else {}

    # ── 结构 ──
    def test_10_week_view(self):
        self.to_week()
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
        # v1.5：标签序「主题、星期」，默认主题
        self.assertEqual([b.text.strip() for b in
                          self.driver.find_elements(By.CSS_SELECTOR, '#viewSeg button')],
                         ['主题', '星期'])
        self.assertFalse(self.js("document.getElementById('themeRow').hidden"))   # 默认主题
        self.assertTrue(self.js("document.getElementById('weekRow').hidden"))
        self.assertEqual(len(self.driver.find_elements(By.CSS_SELECTOR, '#themeRow .theme-card')), 4)
        self.assertIsNone(self.js("document.getElementById('presetPick')"))   # 下拉已移除
        self.assertTrue(self.js("document.getElementById('fabEdit').hidden"))
        self.to_week()
        self.assertEqual(len(self.driver.find_elements(By.CSS_SELECTOR, '#weekRow .day-card')), 7)
        self.assertFalse(self.js("document.getElementById('fabEdit').hidden"))
        self.assertEqual(self.js("document.querySelectorAll('.video-link').length"), 4)
        self.assertEqual(self.ui_state()['view'], 'week')      # to_week 之后应落记忆
        self.assertEqual(self.errors(), [])

    def test_12_reload_keeps_view_and_skin(self):
        self.to_week()                                   # 切星期后再验证记忆
        self.js("(function(){var s=document.getElementById('themeSel');s.value='indigo';"
                "s.dispatchEvent(new Event('change'));})()")
        time.sleep(0.3)
        self.driver.refresh()
        WebDriverWait(self.driver, 8).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#weekRow .day-card')))
        time.sleep(0.3)
        self.assertEqual(self.js("document.documentElement.getAttribute('data-view')"), 'week')
        self.assertFalse(self.js("document.getElementById('weekRow').hidden"))
        self.assertEqual(self.js("document.documentElement.getAttribute('data-theme')"), 'indigo')
        self.assertEqual(self.js("document.getElementById('themeSel').value"), 'indigo')
        self.assertEqual(self.errors(), [])

    def test_13_checkin_persists(self):
        self.to_week()
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
        self.to_week()
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

    def test_15_theme_panel_shot_list(self):
        # v1.4：左列表 + 右预览 + 单张下载；合并长图/逐张已撤
        self.js("document.querySelector('#viewSeg button[data-view=theme]').click()")
        time.sleep(0.2)
        self.js("document.getElementById('fabShot').click()")
        time.sleep(0.4)
        self.assertIn('主题跟练', self.js("document.getElementById('panelTitle').textContent"))
        self.assertEqual(self.js("document.querySelectorAll('#shotList li').length"), 4)
        self.assertEqual(self.js("document.querySelectorAll('#previewHost .card').length"), 1)
        self.assertTrue(self.js("document.querySelector('#shotList li').classList.contains('on')"))
        self.assertTrue(self.js("document.getElementById('btnSavePlan').disabled"))
        self.assertTrue(self.js("document.getElementById('btnShare').disabled"))
        self.assertFalse(self.js("document.getElementById('btnDownloadImg').disabled"))
        self.assertIsNone(self.js("document.getElementById('btnDownloadEach')"))  # 逐张按钮已删
        # 选第 3 套 → 预览换卡
        self.js("document.querySelectorAll('#shotList li')[2].click()")
        time.sleep(0.3)
        self.assertIn('Tabata', self.js("document.querySelector('#previewHost .card h2').textContent"))
        self.assertEqual(self.ui_state()['shotTheme'], 2)

    def test_16_week_shot_list_and_memory(self):
        self.to_week()
        self.js("document.getElementById('fabEdit').click()")
        time.sleep(0.3)
        self.js("document.querySelector('#panelSeg button[data-view=prev]').click()")
        time.sleep(0.3)
        self.assertEqual(self.js("document.querySelectorAll('#shotList li').length"), 8)   # 本周速览 + 七天
        self.js("document.querySelectorAll('#shotList li')[0].click()")
        time.sleep(0.3)
        self.assertIn('7-DAY', self.js("document.querySelector('#previewHost .card .k').textContent"))
        self.assertEqual(self.ui_state()['shotWeek'], 'week')
        self.js("document.getElementById('panelClose').click()")
        self.driver.refresh()
        WebDriverWait(self.driver, 8).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#weekRow .day-card')))
        time.sleep(0.3)
        self.assertEqual(self.ui_state()['shotWeek'], 'week')

    def test_17_panel_and_masthead_metrics(self):
        # v1.4：面板 90vw×90vh；masthead 减半（175px → 目标 ≤100px @1440）
        self.driver.set_window_size(1440, 900)
        self.driver.refresh()
        WebDriverWait(self.driver, 8).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#weekRow .day-card')))
        time.sleep(0.3)
        mh = self.js("Math.round(document.querySelector('.masthead').getBoundingClientRect().height)")
        self.assertLessEqual(mh, 60)                     # v1.5：标题一行
        self.to_week()
        self.js("document.getElementById('fabEdit').click()")
        time.sleep(0.3)
        size = self.js("JSON.stringify((function(){var p=document.querySelector('.panel').getBoundingClientRect();"
                       "var h=document.querySelector('.p-head').getBoundingClientRect();"
                       "var f=document.querySelector('.p-foot').getBoundingClientRect();"
                       "return {w:Math.round(p.width), h:Math.round(p.height), vw:innerWidth, vh:innerHeight,"
                       " head:Math.round(h.height), foot:Math.round(f.height)};})())")
        import json as _json
        sz = _json.loads(size)
        self.assertAlmostEqual(sz['w'] / sz['vw'], 0.9, delta=0.02)
        self.assertAlmostEqual(sz['h'] / sz['vh'], 1.0, delta=0.02)   # v1.5：面板 100vh
        self.assertLessEqual(sz['head'], 40)             # p-head 减半
        self.assertLessEqual(sz['foot'], 40)             # p-foot 减半
        self.assertEqual(self.errors(), [])

    def test_18_shared_link_forces_week_view(self):
        # 记忆是主题，但带 #p= 的分享链接必须落星期视图；恢复后回主题
        self.driver.refresh()
        WebDriverWait(self.driver, 8).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#themeRow .theme-card')))
        self.js("location.hash = 'p=v3|home|1=!!73*~99%20次|2=!!'")
        self.driver.refresh()                                # 页面级刷新，避免脚本内 reload 竞态
        WebDriverWait(self.driver, 8).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#sharedBar:not([hidden])')))
        time.sleep(0.3)
        self.assertFalse(self.js("document.getElementById('weekRow').hidden"))
        self.assertFalse(self.js("document.getElementById('sharedBar').hidden"))
        self.js("document.getElementById('btnUnshare').click()")
        time.sleep(0.3)
        self.assertFalse(self.js("document.getElementById('themeRow').hidden"))
        self.assertEqual(self.errors(), [])

    def test_19_mobile_fullwidth_and_readonly(self):
        # v1.6：手机端单卡满宽（左右切换）+ 隐藏编辑/下载图片；主题改名落地
        self.driver.set_window_size(390, 844)
        self.driver.refresh()
        WebDriverWait(self.driver, 8).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#weekRow .day-card')))
        time.sleep(0.3)
        self.to_week()                                   # 默认视图是主题，先切到星期再量
        vw = self.js("innerWidth")
        w = self.js("Math.round(document.querySelector('#weekRow .day-card').getBoundingClientRect().width)")
        self.assertGreaterEqual(w / vw, 0.9)                          # 星期卡满宽
        self.assertEqual(self.js("getComputedStyle(document.getElementById('fabEdit')).display"), 'none')
        self.assertEqual(self.js("document.getElementById('fabShot').title"), '预览方案')
        self.js("document.getElementById('fabShot').click()")
        time.sleep(0.4)
        self.assertEqual(self.js("getComputedStyle(document.getElementById('btnDownloadImg')).display"), 'none')
        self.assertTrue(self.js("!!document.querySelector('#previewHost .card')"))    # 预览仍可用
        self.js("document.getElementById('panelClose').click()")
        self.js("document.querySelector('#viewSeg button[data-view=theme]').click()")
        time.sleep(0.3)
        tw = self.js("Math.round(document.querySelector('#themeRow .theme-card').getBoundingClientRect().width)")
        self.assertGreaterEqual(tw / vw, 0.9)                          # 主题卡满宽
        self.assertIn('八段锦 · 养生跟练', self.js("document.getElementById('themeRow').textContent"))
        self.assertNotIn('懒人版八段锦', self.driver.page_source)
        self.assertEqual(self.errors(), [])


if __name__ == '__main__':
    unittest.main()
