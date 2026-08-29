# -*- coding: utf-8 -*-
"""Selenium test: layout-table URL 状态分享（HTML-GEN-CL004）— ?tab&q&split
replaceState 同步与初始化恢复（tab 白名单 / split 越界忽略 / q 仅 input.value）+ 🔗 拷贝按钮。

设计: documents/solutions/html-gen-favicon-urlstate-syncer-design-v1.0-20260829.md §6
HG-SEC-074: URL 读写统一 URLSearchParams（自动编解码）; HG-SEC-075: sort/quickFilter 变化 closeSplit;
HG-SEC-076: 恢复顺序 tab(buildTabs 前) → q(render 前) → split(render 后)。
"""
import json
import subprocess
import sys
import time
import unittest
from pathlib import Path
from urllib.parse import quote

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

CHROMEDRIVER = '/Users/jadenli/CodeSpace/script-miner/cache/chromedriver/chromedriver'
PROJECT = Path(__file__).resolve().parent.parent

PAYLOAD = {
    "title": "URL 状态测试",
    "columns": [
        {"key": "name", "label": "名称", "sortable": True},
        {"key": "group", "label": "分组", "sortable": True},
    ],
    "tabs": [
        {"key": "all", "label": "全部"},
        {"key": "a", "label": "A组", "field": "group"},
        {"key": "b", "label": "B组", "field": "group"},
    ],
    "data": [
        {"name": "阿法", "group": "a"},
        {"name": "阿贝", "group": "a"},
        {"name": "巴西", "group": "b"},
        {"name": "北京", "group": "b"},
        {"name": "成都", "group": "b"},
    ],
}


def error_collector(driver):
    driver.execute_script(
        "window.__testErrors = [];"
        "window.onerror = function(m) { window.__testErrors.push(String(m)); };"
    )


def get_errors(driver):
    return driver.execute_script("return window.__testErrors;")


class TestUrlState(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        opts = Options()
        opts.add_argument('--headless')
        opts.add_argument('--no-sandbox')
        opts.add_argument('--disable-dev-shm-usage')
        svc = Service(CHROMEDRIVER)
        cls.driver = webdriver.Chrome(service=svc, options=opts)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def setUp(self):
        self.driver.set_window_size(1280, 800)
        # 先加载一页清掉 localStorage（列可见性等状态跨用例隔离）
        self.driver.get('file://' + str(PROJECT / 'demos' / 'countries-table.html'))
        self.driver.execute_script("localStorage.clear();")
        self._tmp_files = []

    def tearDown(self):
        for p in self._tmp_files:
            p.unlink(missing_ok=True)

    def _gen_page(self, url_suffix=''):
        """用 html-gen.py table 生成临时 URL 状态测试页并加载（唯一文件名防 file:// 缓存）。"""
        stamp = str(int(time.time() * 1000))
        src = PROJECT / 'tests' / f'_tmp_urlstate_{stamp}.json'
        out = PROJECT / 'tests' / f'_tmp_urlstate_{stamp}.html'
        self._tmp_files += [src, out]
        src.write_text(json.dumps(PAYLOAD, ensure_ascii=False), encoding='utf-8')
        cmd = [sys.executable, str(PROJECT / 'html-gen.py'), 'table',
               '-d', str(src), '-o', str(out)]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            self.fail(f"html-gen.py 生成失败 ({proc.returncode}): stderr={proc.stderr!r}")
        self.driver.get('file://' + str(out) + url_suffix)
        # 可能无匹配（空状态）→ 等 #tbody tr 或 #emptyState 任一出现
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, '#tbody tr, #emptyState')))
        error_collector(self.driver)
        return out

    def _active_tab_text(self):
        """激活 tab 的 label（firstChild 文本节点, 排除 count span）。"""
        return self.driver.execute_script(
            "var el=document.querySelector('.tab-btn.active');"
            "return el ? el.firstChild.textContent : null;")

    def _search_value(self):
        return self.driver.find_element(By.ID, 'searchInput').get_attribute('value')

    def _split_active_text(self):
        """split-active 行首列文本（排除 group 列）。"""
        return self.driver.execute_script(
            "var r=document.querySelector('tbody tr.split-active');"
            "return r ? r.querySelector('td').textContent : null;")

    # ── test_01 URL 携带 ?tab&q&split 打开 → 恢复 ──
    def test_01_restore_tab_q_split(self):
        """?tab=b&q=巴&split=0 打开 → B组 激活、搜索已应用（巴）、分栏高亮巴西。"""
        self._gen_page('?tab=b&q=' + quote('巴') + '&split=0')
        self.assertEqual(self._active_tab_text(), 'B组')
        self.assertEqual(self._search_value(), '巴')
        # 搜索已应用：filtered = [巴西, 北京]（group=b 且含 巴）；split=0 → 巴西
        self.assertEqual(self._split_active_text(), '巴西')
        self.assertEqual(self.driver.execute_script("return window.splitIdx;"), 0)
        self.assertEqual(get_errors(self.driver), [])

    # ── test_02 无效 tab / split 越界 → 忽略恢复, 无 JS 错误 ──
    def test_02_invalid_tab_split_ignored(self):
        """无效 tab（白名单外）+ split 越界 → 忽略；q 无匹配 → 空状态；无 JS 错误。"""
        self._gen_page('?tab=zzz&q=' + quote('不存在的词') + '&split=999')
        # tab 忽略 → 默认第一个 tab（全部）
        self.assertEqual(self._active_tab_text(), '全部')
        # q 赋值但无匹配 → 空状态显示
        self.assertEqual(self._search_value(), '不存在的词')
        empty = self.driver.find_element(By.ID, 'emptyState')
        self.assertEqual(empty.value_of_css_property('display'), 'block')
        # split 越界忽略 → 无分栏
        self.assertIsNone(self._split_active_text())
        self.assertFalse(self.driver.execute_script("return window.splitActive;"))
        self.assertEqual(get_errors(self.driver), [])

    # ── test_03 状态变化 → location.search 同步 ──
    def test_03_state_changes_sync_url(self):
        """切 tab/搜索/开关分栏/导航 → replaceState 同步；默认值剔除。"""
        self._gen_page()

        def search_str():
            return self.driver.execute_script("return location.search;")

        # 初始：无参数
        self.assertEqual(search_str(), '')
        # 切 tab → tab=a
        self.driver.execute_script("switchTab('a');")
        self.assertEqual(search_str(), '?tab=a')
        # 搜索输入（300ms debounce）→ q 同步
        inp = self.driver.find_element(By.ID, 'searchInput')
        inp.send_keys('阿')
        time.sleep(0.4)
        self.assertEqual(search_str(), '?tab=a&q=' + quote('阿'))
        # 打开分栏 → split 同步
        self.driver.execute_script("openSplitAt(0);")
        self.assertEqual(search_str(), '?tab=a&q=' + quote('阿') + '&split=0')
        # 分栏导航 → split=1
        self.driver.execute_script("splitNav(1);")
        self.assertIn('&split=1', search_str())
        # 关闭分栏 → 剔除 split 参数
        self.driver.execute_script("closeSplit();")
        self.assertEqual(search_str(), '?tab=a&q=' + quote('阿'))
        # 清空搜索 → 剔除 q（clear 后显式触发 input 事件, 模拟真实输入）
        inp.clear()
        self.driver.execute_script(
            "document.getElementById('searchInput').dispatchEvent(new Event('input'));")
        time.sleep(0.4)
        self.assertEqual(search_str(), '?tab=a')
        # 切回默认 tab → 剔除 tab, URL 纯净
        self.driver.execute_script("switchTab('all');")
        self.assertEqual(search_str(), '')
        self.assertEqual(get_errors(self.driver), [])

    # ── test_04 sort / quickFilter 变化 → closeSplit（HG-SEC-075）──
    def test_04_sort_quickfilter_close_split(self):
        """分栏打开后 sortBy / quickFilterBy → closeSplit + URL 剔除 split。"""
        self._gen_page()
        self.driver.execute_script("openSplitAt(0);")
        self.assertIn('split=0', self.driver.execute_script("return location.search;"))
        # sortBy → closeSplit
        self.driver.execute_script("sortBy('name', null);")
        self.assertFalse(self.driver.execute_script("return window.splitActive;"))
        self.assertNotIn('split', self.driver.execute_script("return location.search;"))
        # 重新开分栏后 quickFilterBy → closeSplit
        self.driver.execute_script("openSplitAt(0);")
        self.assertIn('split=0', self.driver.execute_script("return location.search;"))
        self.driver.execute_script("quickFilterBy('group', 'a', 'exact');")
        self.assertFalse(self.driver.execute_script("return window.splitActive;"))
        self.assertNotIn('split', self.driver.execute_script("return location.search;"))
        self.assertEqual(get_errors(self.driver), [])

    # ── test_05 拷贝按钮 → execCommand fallback + toast ──
    def test_05_share_button_fallback_copy(self):
        """🔗 点击 → clipboard 不可用走 execCommand fallback → toast「已复制链接」。"""
        self._gen_page()
        # 制造可分享状态：tab=a + split=0
        self.driver.execute_script("switchTab('a'); openSplitAt(0);")
        # 禁用 clipboard API → 确定走 fallback 分支
        self.driver.execute_script(
            "Object.defineProperty(navigator, 'clipboard', {value: undefined, configurable: true});")
        self.driver.find_element(By.ID, 'shareBtn').click()
        time.sleep(0.4)
        toast = self.driver.find_element(By.ID, 'toast')
        self.assertEqual(toast.text, '已复制链接')
        # buildShareUrl 规范化：剔除默认/空参数, 含当前非默认状态
        url = self.driver.execute_script("return buildShareUrl();")
        self.assertIn('tab=a', url)
        self.assertIn('split=0', url)
        self.assertEqual(get_errors(self.driver), [])

    # ── test_06 分享/Home 按钮位于 tabs 行居右 (CL005) ──
    def test_06_share_home_buttons_in_tabs_actions(self):
        """shareBtn 位于 .tabs-actions（tabs 行居右）且图标 ↗; --home-url 注入的 home-link 同容器。"""
        self._gen_page()
        btn = self.driver.find_element(By.ID, 'shareBtn')
        parent = btn.find_element(By.XPATH, '..')
        self.assertIn('tabs-actions', parent.get_attribute('class'))
        self.assertIn('↗', btn.text)
        # --home-url 生成页: home-link 与 shareBtn 同容器（tabs 行居右）
        stamp = str(int(time.time() * 1000))
        src = PROJECT / 'tests' / f'_tmp_cl005home_{stamp}.json'
        out = PROJECT / 'tests' / f'_tmp_cl005home_{stamp}.html'
        self._tmp_files += [src, out]
        src.write_text(json.dumps(PAYLOAD, ensure_ascii=False), encoding='utf-8')
        proc = subprocess.run([sys.executable, str(PROJECT / 'html-gen.py'), 'table',
                               '-d', str(src), '-o', str(out),
                               '--home-url', 'https://example.com/'],
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.driver.get('file://' + str(out))
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#tbody tr, #emptyState')))
        error_collector(self.driver)
        home = self.driver.find_element(By.CSS_SELECTOR, '.home-link')
        self.assertIn('tabs-actions', home.find_element(By.XPATH, '..').get_attribute('class'))
        self.assertEqual(get_errors(self.driver), [])


if __name__ == '__main__':
    unittest.main()
