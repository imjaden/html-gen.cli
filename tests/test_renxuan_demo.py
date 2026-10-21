"""Selenium 回归：demos/renxuan.html（人选天选论 · 在线阅读）案例完整性与跳转。

该页是 script-miner 交付的成品拷贝（来源见 data/_renxuan-source.json），
正文 8 页位于 demos/renxuan/，由 demo --rebuild 通过 data/_renxuan-kb-data.json
标记为 referenced 子页（不出现在独立案例清单）。
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
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

CHROMEDRIVER = '/Users/jadenli/CodeSpace/script-miner/cache/chromedriver/chromedriver'
PROJECT = Path(__file__).resolve().parent.parent
DEMOS = PROJECT / 'demos'
PAGE = DEMOS / 'renxuan.html'
FRAME = 'contentFrame'


class _Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *args, **kwargs):  # 静音 http.server 访问日志
        pass


class TestRenxuanDemo(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # iframe 内锚点断言需同源 → 用本地 http（file:// 下跨文件 iframe 不可读）
        handler = partial(_Quiet, directory=str(DEMOS))
        cls.httpd = ThreadingHTTPServer(('127.0.0.1', 0), handler)
        cls.port = cls.httpd.server_address[1]
        threading.Thread(target=cls.httpd.serve_forever, daemon=True).start()

        opts = Options()
        opts.add_argument('--headless=new')
        opts.add_argument('--no-sandbox')
        opts.add_argument('--disable-dev-shm-usage')
        opts.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
        cls.driver = webdriver.Chrome(service=Service(CHROMEDRIVER), options=opts)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        cls.httpd.shutdown()

    def setUp(self):
        self.driver.set_window_size(1440, 900)
        self.driver.get(f'http://127.0.0.1:{self.port}/renxuan.html')
        WebDriverWait(self.driver, 8).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.kw-tab')))
        time.sleep(0.4)
        self.driver.execute_script('localStorage.clear();')
        self.driver.execute_script(
            "window.__testErrors = [];"
            "window.onerror = function(m) { window.__testErrors.push(String(m)); };")

    def _errors(self):
        errs = self.driver.execute_script('return window.__testErrors;') or []
        severe = [l['message'] for l in self.driver.get_log('browser') if l['level'] == 'SEVERE']
        return list(errs) + severe

    def _tab(self, needle):
        self.driver.execute_script(
            "var t=[...document.querySelectorAll('.kw-tab')]"
            ".find(e=>e.textContent.indexOf(arguments[0])!==-1);t.click();", needle)
        time.sleep(0.6)

    # ── 结构 ──

    def test_01_layout(self):
        tabs = self.driver.execute_script("return document.querySelectorAll('.kw-tab').length")
        sub = self.driver.execute_script(
            "var s=document.querySelector('.kw-sidebar-header .sub');"
            "return s? s.textContent.trim():''")
        self.assertEqual(tabs, 4)
        self.assertIn('16', sub)
        self.assertEqual(self._errors(), [])

    def test_02_highlight_rows_45(self):
        self._tab('亮点句')
        titles = self.driver.execute_script(
            "return [...document.querySelectorAll('.kw-section-title')]"
            ".map(e=>e.textContent.trim())")
        self.assertEqual(len(titles), 8)
        per = []
        for t in titles:
            self.driver.execute_script("selectSection('highlights', arguments[0]);", t)
            time.sleep(0.35)
            per.append(self.driver.execute_script(
                "return document.querySelectorAll('.rx-hl-row').length"))
        self.assertEqual(per, [6, 6, 5, 5, 5, 5, 6, 7])
        self.assertEqual(sum(per), 45)
        self.assertEqual(self._errors(), [])

    # ── 跳转 ──

    def test_03_highlight_jump_to_anchor(self):
        self._tab('亮点句')
        first = self.driver.execute_script(
            "var t=[...document.querySelectorAll('.kw-section-title')][0];"
            "selectSection('highlights', t.textContent.trim());"
            "var a=document.querySelector('.rx-hl-row a');"
            "var h=a? a.getAttribute('href'):null; if(a) a.click(); return h;")
        self.assertIsNotNone(first)
        frag = first.split('#')[1]
        WebDriverWait(self.driver, 8).until(lambda d: d.execute_script(
            "var f=document.getElementById(arguments[0]);"
            "return !!(f && f.src && f.src.indexOf('.html')>0);", FRAME))
        time.sleep(1.0)
        src = self.driver.execute_script(
            "return document.getElementById(arguments[0]).src;", FRAME)
        self.assertIn('renxuan/', src)
        self.assertIn('#' + frag, src)

        self.driver.switch_to.frame(self.driver.find_element(By.ID, FRAME))
        self.assertTrue(self.driver.execute_script(
            "return !!document.getElementById(arguments[0])", frag))
        self.assertEqual(self.driver.execute_script(
            "return document.querySelectorAll('span.rx-hl').length"), 6)
        self.driver.switch_to.default_content()
        self.assertEqual(self._errors(), [])

    def test_04_chapter_body_renders(self):
        self._tab('人之路')
        sec = self.driver.find_element(By.CSS_SELECTOR, '.kw-section-title')
        self.driver.execute_script("selectSection('renzhilu', arguments[0].textContent.trim());", sec)
        time.sleep(1.2)
        src = self.driver.execute_script(
            "return document.getElementById(arguments[0]).src;", FRAME)
        self.assertIn('renxuan/02-heliu-shijie.html', src)
        self.driver.switch_to.frame(self.driver.find_element(By.ID, FRAME))
        length = self.driver.execute_script(
            "var b=document.getElementById('docBody');"
            "return b? b.innerText.replace(/\\s+/g,' ').trim().length:0")
        self.assertGreater(length, 1000)
        self.driver.switch_to.default_content()
        self.assertEqual(self._errors(), [])

    # ── 清单登记 ──

    def test_05_registered_in_demos_index(self):
        self.driver.get(f'http://127.0.0.1:{self.port}/demos-index.html')
        WebDriverWait(self.driver, 8).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.data-table')))
        time.sleep(0.6)
        hit = self.driver.execute_script(
            "return [...document.querySelectorAll('.data-table tbody tr')]"
            ".filter(r=>r.textContent.includes('人选天选论'))"
            ".map(r=>{var a=r.querySelector('a');"
            "return a? a.getAttribute('href'):''})")
        self.assertEqual(hit, ['renxuan.html'])

        reg = json.loads((DEMOS / '_registry.json').read_text(encoding='utf-8'))
        entry = [d for d in reg['demos'] if d['entry'] == 'renxuan.html']
        self.assertEqual(len(entry), 1)
        self.assertEqual(entry[0]['type'], 'knowledge')
        self.assertFalse(entry[0]['referenced'])
        subs = [d for d in reg['demos'] if d['entry'].startswith('renxuan/')]
        self.assertEqual(len(subs), 8)
        self.assertTrue(all(d['referenced'] for d in subs))
        self.assertEqual(self._errors(), [])

    # ── 源件完整性 ──

    def test_08_copyright_notice(self):
        """硬约束：demo 页保留来源与「连载版、非出版本」声明。"""
        panel = self.driver.find_element(By.ID, 'welcomePanel').text
        self.assertIn('连载版', panel)
        self.assertIn('非出版本', panel)
        self.assertIn('姜蓝', panel)
        self.assertIn('guohen.com', panel)
        self.assertEqual(self._errors(), [])

    def test_06_source_registry_matches_files(self):
        import hashlib
        reg = json.loads((PROJECT / 'data' / '_renxuan-source.json').read_text(encoding='utf-8'))
        self.assertTrue(reg['source_index_sha256'].startswith('d4c030ff'))
        for name, sha in reg['files'].items():
            f = DEMOS / 'renxuan' / name
            self.assertTrue(f.exists(), name)
            self.assertEqual(hashlib.sha256(f.read_bytes()).hexdigest(), sha, name)


if __name__ == '__main__':
    unittest.main()
