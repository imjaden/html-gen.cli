"""Selenium test: layout-knowledge 侧栏搜索面板（CL047）、根页地图、主题、语言。

CL047 起搜索面从「侧栏过滤」改为「Spotlight 面板」：
- 入口 ⌘/Ctrl+K 与 🔍 按钮；**⌘F 不再拦截**（浏览器原生查找保留）
- 根页 = `#welcomePanel`（含菜单地图 `#kwMap`），点 `.sidebar-title` 回根页
"""
import json
import re
import time
import unittest
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from conftest import chromedriver_service

PROJECT = Path(__file__).resolve().parent.parent
DEMO = PROJECT / 'demos' / 'chaitin.html'
DEMO_DESC = PROJECT / 'demos' / 'cloudwise.html'   # 有 desc 的数据源


def _items_of(html_path):
    """从产物里抠出 ITEMS（html-gen 用 json.dumps 注入 ⇒ 可直接 json.loads）。"""
    s = Path(html_path).read_text(encoding='utf-8')
    m = re.search(r'const ITEMS\s*=\s*(\[.*?\]);', s, re.S)
    return json.loads(m.group(1)) if m else []


def _groups_of(html_path):
    s = Path(html_path).read_text(encoding='utf-8')
    m = re.search(r'const GROUPS = (\[.*?\]);', s, re.S)
    if not m:
        raise AssertionError(f'{html_path} 里找不到 GROUPS 注入')
    return json.loads(m.group(1))


class TestKnowledgeSidebar(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        opts = Options()
        opts.add_argument('--headless')
        opts.add_argument('--no-sandbox')
        opts.add_argument('--disable-dev-shm-usage')
        svc = chromedriver_service()
        cls.driver = webdriver.Chrome(service=svc, options=opts)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def setUp(self):
        self.driver.set_window_size(1280, 800)
        # Clear localStorage to prevent cross-test state pollution
        self.driver.get('file://' + str(DEMO))
        time.sleep(0.2)
        self.driver.execute_script("localStorage.clear();")
        # Reload clean
        self.driver.get('file://' + str(DEMO))
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.kw-tab')))
        self.driver.execute_script(
            "window.__testErrors = [];"
            "window.onerror = function(m) { window.__testErrors.push(String(m)); };"
        )

    # ── helpers ──

    def _errors(self):
        return self.driver.execute_script("return window.__testErrors;")

    def _spot_active(self):
        return self.driver.execute_script(
            "return document.getElementById('kwSpotOverlay').classList.contains('active');")

    def _key(self, key, **mods):
        parts = ['key:%s' % json.dumps(key)] + [f'{k}:true' for k in mods]
        parts += ['bubbles:true', 'cancelable:true']
        js = ("var ev = new KeyboardEvent('keydown', {%s});"
              "document.dispatchEvent(ev); return ev.defaultPrevented;" % ', '.join(parts))
        return self.driver.execute_script(js)

    def _type(self, text):
        inp = self.driver.find_element(By.ID, 'kwSpotInput')
        inp.clear()
        inp.send_keys(text)
        time.sleep(0.3)   # 面板 120ms debounce

    # ── Search panel（CL047：Spotlight 同构） ──

    def test_01_spot_open(self):
        self.driver.execute_script("toggleKwSpot();")
        time.sleep(0.15)
        self.assertTrue(self._spot_active(), 'toggleKwSpot 应激活搜索面板')

    def test_02_spot_filter(self):
        self.driver.execute_script("toggleKwSpot();")
        time.sleep(0.1)
        self._type('画像')
        hits = self.driver.find_elements(By.CSS_SELECTOR, '.kw-spot-item')
        self.assertGreater(len(hits), 0, '搜索条目名应至少有 1 条命中')
        self.assertGreater(len(self.driver.find_elements(By.CSS_SELECTOR, '.kw-spot-results mark.kw-mark')), 0,
                          '命中片段应有 <mark> 高亮')

    def test_03_spot_close_esc(self):
        self.driver.execute_script("toggleKwSpot();")
        time.sleep(0.1)
        self._key('Escape')
        time.sleep(0.15)
        self.assertFalse(self._spot_active(), 'Escape 应关闭面板')

    # ── Theme ──

    def test_04_theme_toggle(self):
        btn = self.driver.find_element(By.ID, 'kwThemeBtn')
        was_light = 'light' in (self.driver.find_element(By.TAG_NAME, 'html').get_attribute('class') or '')
        btn.click()
        time.sleep(0.15)
        is_light = 'light' in (self.driver.find_element(By.TAG_NAME, 'html').get_attribute('class') or '')
        self.assertNotEqual(was_light, is_light, "Theme should toggle")

    # ── Language ──

    def test_05_language_toggle(self):
        zh = self.driver.find_element(By.ID, 'kwLangZh')
        en = self.driver.find_element(By.ID, 'kwLangEn')
        was_zh = 'active' in (zh.get_attribute('class') or '')
        (en if was_zh else zh).click()
        time.sleep(0.15)
        now_zh = 'active' in (zh.get_attribute('class') or '')
        self.assertNotEqual(was_zh, now_zh)

    # ── Sidebar Collapse ──

    def test_06_sidebar_collapse(self):
        self.driver.execute_script("toggleSidebar();")
        time.sleep(0.15)
        sb = self.driver.find_element(By.ID, 'kwSidebar')
        self.assertIn('collapsed', (sb.get_attribute('class') or '').split())
        self.driver.execute_script("toggleSidebar();")
        time.sleep(0.15)
        self.assertNotIn('collapsed', (sb.get_attribute('class') or '').split())

    # ── Tab Switch ──

    def test_07_tab_switch(self):
        tabs = self.driver.find_elements(By.CSS_SELECTOR, '.kw-tab')
        self.assertGreater(len(tabs), 0, "Should have tabs")
        if len(tabs) > 1:
            tabs[1].click()
            time.sleep(0.15)
            self.assertIn('active', (tabs[1].get_attribute('class') or '').split())
            # CL047: 切页签回根页（不再自动选首条）
            self.assertTrue(self.driver.execute_script(
                "return document.getElementById('welcomePanel').classList.contains('active');"),
                '切页签应回到根页')

    # ── No JS errors ──

    def test_08_no_js_errors(self):
        self.driver.execute_script("toggleKwSpot();")
        time.sleep(0.1)
        self._type('test')
        self.driver.execute_script("toggleKwSpot();kwGoRoot();")
        time.sleep(0.1)
        self.driver.execute_script("toggleKwTheme();toggleSidebar();")
        time.sleep(0.2)
        self.driver.execute_script("toggleSidebar();")
        time.sleep(0.2)
        errs = self._errors()
        self.assertEqual(len(errs), 0, f"JS errors: {errs}")

    # ── CL047: ⌘F 归还原生 / ⌘K 打开面板 ──

    def test_09_cmdf_not_intercepted(self):
        prevented = self.driver.execute_script(
            "var ev = new KeyboardEvent('keydown', {key:'f', metaKey:true, bubbles:true, cancelable:true});"
            "document.dispatchEvent(ev); return ev.defaultPrevented;")
        self.assertFalse(prevented, '⌘F 不得被拦截（浏览器原生查找要保留）')
        self.assertFalse(self._spot_active(), '⌘F 不应打开搜索面板')

    def test_10_cmdk_opens_idempotent_and_esc(self):
        prevented = self._key('k', metaKey=True)
        time.sleep(0.2)
        self.assertTrue(prevented, '⌘K 应 preventDefault（避免浏览器默认行为）')
        self.assertTrue(self._spot_active(), '⌘K 应打开搜索面板')
        self.assertEqual(self.driver.execute_script("return document.activeElement.id"),
                         'kwSpotInput', '焦点应落在 #kwSpotInput')
        self.driver.execute_script("toggleKwSpot();")      # 显式关（不依赖幂等语义）
        time.sleep(0.1)
        self.driver.execute_script("toggleKwSpot();")      # 再开
        time.sleep(0.1)
        self.assertTrue(self._spot_active(), 'toggle 两次后应仍为打开态')
        self._key('Escape')
        time.sleep(0.15)
        self.assertFalse(self._spot_active(), 'Escape 应关闭面板')

    def test_11_narrow_panel_fits(self):
        self.driver.set_window_size(756, 413)
        self.driver.get('file://' + str(DEMO))
        time.sleep(0.3)
        self.driver.execute_script("toggleKwSpot();")
        time.sleep(0.2)
        self.assertTrue(self._spot_active(), '窄屏 ⌘K/toggle 也应打开面板')
        box = self.driver.execute_script(
            "var r = document.querySelector('.kw-spot-modal').getBoundingClientRect();"
            "return {w: r.width, vw: window.innerWidth};")
        self.assertLessEqual(box['w'], box['vw'], '面板宽度不得超过视口')
        self.driver.set_window_size(1280, 800)

    # ── CL047: 根页返回 ──

    def test_12_root_return_via_title(self):
        items = self.driver.find_elements(By.CSS_SELECTOR, '.kw-item')
        self.assertGreater(len(items), 0, '侧栏应有条目')
        items[0].click()
        time.sleep(0.3)
        self.assertFalse(self.driver.execute_script(
            "return document.getElementById('welcomePanel').classList.contains('active');"),
            '点条目后根页应隐藏')
        self.assertIn('item=', self.driver.execute_script("return location.search;"),
                      'URL 应带 item 参数')
        self.driver.find_element(By.CSS_SELECTOR, '.kw-sidebar-header .sidebar-title').click()
        time.sleep(0.3)
        self.assertTrue(self.driver.execute_script(
            "return document.getElementById('welcomePanel').classList.contains('active');"),
            '点标题应回到根页')
        self.assertNotIn('item=', self.driver.execute_script("return location.search;"),
                         'URL 的 item 参数应被清掉')
        self.assertIsNone(self.driver.execute_script("return localStorage.getItem('html-gen:kw_item');"),
                          'localStorage 的 item 记忆应被清掉')

    # ── CL047: 根页菜单地图 ──

    def test_13_root_map_table(self):
        items = _items_of(DEMO)
        groups = _groups_of(DEMO)
        cols = len(self.driver.find_elements(By.CSS_SELECTOR, '#kwMap thead th'))
        self.assertEqual(cols, len(groups) + 1, '地图表列数应 = 类目数 + 行表头列')
        map_items = self.driver.find_elements(By.CSS_SELECTOR, '#kwMap .kw-map-item')
        self.assertEqual(len(map_items), len(items), '格内条目总数应等于数据条目数')
        map_items[0].click()
        time.sleep(0.3)
        self.assertFalse(self.driver.execute_script(
            "return document.getElementById('welcomePanel').classList.contains('active');"),
            '点地图条目后应离开根页')
        self.assertIn('item=', self.driver.execute_script("return location.search;"))

    # ── CL047: 搜索面 = 标题/副标题/描述/分组，不含 url/正文 ──

    def test_14_url_not_searched(self):
        self.driver.execute_script("toggleKwSpot();")
        time.sleep(0.1)
        self._type('company-profile')     # 只出现在 item.url 里
        self.assertEqual(len(self.driver.find_elements(By.CSS_SELECTOR, '.kw-spot-item')), 0,
                         'url/正文不在搜索面内，应 0 命中')
        self.assertEqual(len(self.driver.find_elements(By.CSS_SELECTOR, '.kw-spot-empty')), 1,
                         '无匹配应显示空态')

    def test_15_desc_searched(self):
        items = _items_of(DEMO_DESC)
        titles = [i.get('title', '') for i in items]
        probe = None
        for it in items:
            d = it.get('desc') or ''
            for i in range(len(d) - 3):
                cand = d[i:i + 3]
                if cand.strip() == cand and not any(cand in t for t in titles) and '\\' not in cand:
                    probe = cand
                    break
            if probe:
                break
        self.assertIsNotNone(probe, 'cloudwise 数据里应能找到只在 desc 出现的 3 字片段')
        self.driver.get('file://' + str(DEMO_DESC))
        time.sleep(0.3)
        self.driver.execute_script("toggleKwSpot();")
        time.sleep(0.1)
        self._type(probe)
        self.assertGreater(len(self.driver.find_elements(By.CSS_SELECTOR, '.kw-spot-item')), 0,
                           f'desc 命中失败（probe={probe!r}）：描述应参与搜索')


if __name__ == '__main__':
    unittest.main(verbosity=2)
