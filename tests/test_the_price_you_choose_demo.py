"""Selenium 回归：demos/the-price-you-choose.html（人选天选论 · The Price You Choose）。

来源见 data/_the-price-you-choose-source.json（upstream script-miner 57e191a，18 文件哈希）。
本页是成品拷贝 + 35 处前缀改写 + 版权声明 + canonical（demo --rebuild 注入）。
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
ENTRY = DEMOS / 'the-price-you-choose.html'
FRAME = 'contentFrame'


class _Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *args, **kwargs):
        pass


class TestThePriceYouChoose(unittest.TestCase):

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
        cls.driver = webdriver.Chrome(service=Service(CHROMEDRIVER), options=opts)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        cls.httpd.shutdown()

    def setUp(self):
        self.driver.set_window_size(1440, 900)
        self.driver.get(self.url('/the-price-you-choose.html'))
        WebDriverWait(self.driver, 8).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.kw-tab')))
        time.sleep(0.3)
        self.driver.execute_script('localStorage.clear();')
        self.driver.get(self.url('/the-price-you-choose.html'))
        WebDriverWait(self.driver, 8).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.kw-tab')))
        self.driver.execute_script(
            "window.__testErrors=[];window.onerror=function(m){window.__testErrors.push(String(m));};")

    def url(self, path):
        return f'http://127.0.0.1:{self.port}{path}'

    def _errors(self):
        errs = self.driver.execute_script('return window.__testErrors;') or []
        severe = [l['message'] for l in self.driver.get_log('browser') if l['level'] == 'SEVERE']
        return list(errs) + severe

    # ── 结构 ──

    def test_01_layout(self):
        tabs = [t.text.strip() for t in self.driver.find_elements(By.CSS_SELECTOR, '.kw-tab')]
        self.assertEqual(len(tabs), 3)
        self.assertIn('序', tabs[0])
        self.assertIn('1~4', tabs[1])
        self.assertIn('5~7', tabs[2])
        sub = self.driver.execute_script(
            "var s=document.querySelector('.kw-sidebar-header .sub');return s?s.textContent.trim():''")
        self.assertIn('9', sub)
        self.assertEqual(self.driver.execute_script(
            "return document.querySelectorAll('.rx-hl-row').length"), 0)
        self.assertEqual(self._errors(), [])

    def test_02_home_segments(self):
        title = self.driver.execute_script(
            "var e=document.querySelector('.rx-home-title');return e?e.textContent.trim():''")
        en = self.driver.execute_script(
            "var e=document.querySelector('.rx-home-en');return e?e.textContent.trim():''")
        self.assertEqual(title, '人选天选论')
        self.assertEqual(en, 'The Price You Choose')
        self.assertEqual(self.driver.execute_script("return document.querySelectorAll('a.rx-ch').length"), 8)
        self.assertEqual(self.driver.execute_script(
            "return document.querySelectorAll('a[data-rx-feat]').length"), 5)
        self.assertTrue(self.driver.execute_script("return !!document.getElementById('rxHomeBtn')"))
        self.assertEqual(self._errors(), [])

    # ── 亮点句文章页 ──

    def test_03_highlights_article(self):
        items = self.driver.find_elements(By.CSS_SELECTOR, '.kw-item')
        target = [i for i in items if '亮点句' in i.text][0]
        target.click()
        WebDriverWait(self.driver, 8).until(lambda d: d.execute_script(
            "var f=document.getElementById(arguments[0]);"
            "return !!(f && f.src && f.src.indexOf('highlights.html')!==-1);", FRAME))
        time.sleep(1.0)
        self.driver.switch_to.frame(self.driver.find_element(By.ID, FRAME))
        links = self.driver.execute_script(
            "return document.querySelectorAll('a[href*=\"#hl-chapter\"]').length")
        h2s = self.driver.execute_script("return document.querySelectorAll('h2').length")
        self.assertEqual(links, 45)
        self.assertEqual(h2s, 8)
        # 页尾来源行
        last = self.driver.execute_script(
            "var b=document.getElementById('docBody');"
            "var ps=b.querySelectorAll('p');return ps.length? ps[ps.length-1].textContent.trim():''")
        self.assertIn('来源', last)
        self.driver.switch_to.default_content()
        self.assertEqual(self._errors(), [])

    # ── 旧链接兼容（8 个 slug 桩）──

    def test_04_legacy_slug_redirect(self):
        self.driver.get(self.url('/the-price-you-choose/01-xu.html') +
                        '?width=wide&sidebar=0&toolbar=0&t=1#hl-01-xu-1')
        WebDriverWait(self.driver, 10).until(lambda d: 'chapter00.html' in d.current_url)
        time.sleep(0.8)
        self.assertIn('chapter00.html', self.driver.current_url)
        self.assertIn('人选天选论-序', self.driver.title)
        self.assertTrue(self.driver.execute_script(
            "return document.body.classList.contains('width-wide')"))
        self.assertTrue(self.driver.execute_script(
            "return !!document.getElementById('hl-chapter00-1')"))
        self.assertEqual(self._errors(), [])

    # ── 章节页：锚点 + 来源行位置 ──

    def test_05_chapter_anchor_and_source_tail(self):
        # 直接开正文页（KB 壳层已由 01/03/04 覆盖），验证锚点与来源行位置
        self.driver.get(self.url('/the-price-you-choose/chapter01.html') +
                        '?width=wide&sidebar=0&toolbar=0')
        WebDriverWait(self.driver, 10).until(lambda d: d.execute_script(
            "return !!document.getElementById('docBody')"))
        time.sleep(0.5)
        self.assertEqual(self.driver.execute_script(
            "return document.querySelectorAll('span.rx-hl').length"), 8)   # chapter01 = 8 段（含 2 处续行）
        self.assertEqual(self.driver.execute_script(
            "return document.querySelectorAll('[id^=\"hl-chapter01-\"]').length"), 8)
        last = self.driver.execute_script(
            "var b=document.getElementById('docBody');"
            "var ps=b.querySelectorAll('p');return ps.length? ps[ps.length-1].textContent.trim():''")
        self.assertIn('来源', last)
        # 来源行之后不应再有 h2 / 高亮 span
        tail_ok = self.driver.execute_script(
            "var b=document.getElementById('docBody');var ps=b.querySelectorAll('p');"
            "if(!ps.length) return false; var last=ps[ps.length-1];"
            "var after=b.innerHTML.split(last.outerHTML)[1]||'';"
            "return after.indexOf('<h2')===-1 && after.indexOf('rx-hl')===-1;")
        self.assertTrue(tail_ok)
        self.assertEqual(self._errors(), [])

    # ── 清单登记 ──

    def test_06_registered_in_demos_index(self):
        self.driver.get(self.url('/demos-index.html'))
        WebDriverWait(self.driver, 8).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.data-table')))
        time.sleep(0.6)
        hit = self.driver.execute_script(
            "return [...document.querySelectorAll('.data-table tbody tr')]"
            ".filter(r=>r.textContent.includes('人选天选论'))"
            ".map(r=>{var a=r.querySelector('a');return a?a.getAttribute('href'):''})")
        self.assertEqual(hit, ['the-price-you-choose.html'])

        reg = json.loads((DEMOS / '_registry.json').read_text(encoding='utf-8'))
        entry = [d for d in reg['demos'] if d['entry'] == 'the-price-you-choose.html']
        self.assertEqual(len(entry), 1)
        self.assertEqual(entry[0]['type'], 'knowledge')
        self.assertFalse(entry[0]['referenced'])
        subs = [d for d in reg['demos'] if d['entry'].startswith('the-price-you-choose/')]
        self.assertEqual(len(subs), 17)          # 9 内容页 + 8 旧 slug 桩
        self.assertTrue(all(d['referenced'] for d in subs))

    # ── 硬约束：版权声明 / canonical / 台账 ──

    def test_07_copyright_and_canonical(self):
        panel = self.driver.find_element(By.ID, 'welcomePanel').text
        self.assertIn('The Price You Choose', panel)
        self.assertIn('非出版本', panel)
        self.assertIn('姜蓝', panel)
        canon = self.driver.execute_script(
            "var l=document.querySelector('link[rel=canonical]');return l?l.getAttribute('href'):null")
        self.assertEqual(canon, 'https://html-gen.cli.jaden.tech/the-price-you-choose.html')

    def test_08_source_registry_matches_files(self):
        import hashlib
        reg = json.loads((PROJECT / 'data' / '_the-price-you-choose-source.json')
                         .read_text(encoding='utf-8'))
        self.assertEqual(reg['upstream_commit'], '57e191a')
        self.assertTrue(reg['source_index_sha256'].startswith('31fa7ac7'))
        for name, sha in reg['files'].items():
            f = DEMOS / 'the-price-you-choose' / name
            self.assertTrue(f.exists(), name)
            self.assertEqual(hashlib.sha256(f.read_bytes()).hexdigest(), sha, name)


if __name__ == '__main__':
    unittest.main()
