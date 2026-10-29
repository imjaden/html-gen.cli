# -*- coding: utf-8 -*-
"""Selenium + 生成器回归: A 型表格「默认状态」三项能力 (HTML-GEN-CL021)。

1. options.share=false   → 不渲染右上角分享按钮（模板 <!--SHARE_BUTTON--> 注入空串, 默认仍开启）
2. options.highlight     → 命中行常驻高亮 tr.hl-row（只高亮不筛选; 冻结列/右侧固定列背景同步覆盖）
3. options.defaultSort   → 加载即按该列排序（表头箭头点亮; 数值列按起始年 + 稳定序）

覆盖四张影视时间轴（daming / zhuyuanzhang / yongzheng / history）
+ 未配置页 countries-table 的默认行为回归（分享按钮仍在、无高亮、无强制排序）。
"""
import json
import subprocess
import sys
import time
import unittest
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

CHROMEDRIVER = '/Users/jadenli/CodeSpace/script-miner/cache/chromedriver/chromedriver'
PROJECT = Path(__file__).resolve().parent.parent
DRAMA = PROJECT / 'demos' / 'drama'

# 页 → 期望 (rows = 第 1 页可见行; hl = 第 1 页高亮行; period_key = 起止年份列标签;
#            first = 默认排序后首行该列文本; sorted = 是否应有默认排序)
PAGES = {
    'daming-timeline-table.html': {
        'rows': 24, 'hl': 8, 'hl_value': '嘉靖', 'period_key': '起止年份',
        'first': '1368—1398', 'sorted': True},
    'zhuyuanzhang-timeline-table.html': {
        'rows': 7, 'hl': 3, 'hl_value': '洪武', 'period_key': '起止年份',
        'first': '1328—1368', 'sorted': True},
    'yongzheng-timeline-table.html': {
        'rows': 15, 'hl': 9, 'hl_value': '雍正', 'period_key': '起止年份',
        'first': '1616—1626', 'sorted': True},
    'history-timeline-table.html': {
        'rows': 22, 'hl': 0, 'hl_value': '', 'period_key': '起止年代',
        'first': '约前3000—约前2070', 'sorted': False},
}

SHARE_PAYLOAD = {
    'title': '默认态能力测试',
    'columns': [
        {'key': 'era', 'label': '年号', 'width': '100px'},
        {'key': 'period', 'label': '起止年份', 'type': 'number', 'width': '120px'},
    ],
    'data': [
        {'era': '嘉靖', 'period': '1522—1566'},
        {'era': '洪武', 'period': '1368—1398'},
        {'era': '万历', 'period': '1573—1620'},
    ],
    'tabs': [],
}


def error_collector(driver):
    driver.execute_script(
        "window.__testErrors = [];"
        "window.onerror = function(m) { window.__testErrors.push(String(m)); };"
    )


def get_errors(driver):
    return driver.execute_script("return window.__testErrors;")


class TestTableDefaultState(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        opts = Options()
        opts.add_argument('--headless')
        opts.add_argument('--no-sandbox')
        opts.add_argument('--disable-dev-shm-usage')
        cls.driver = webdriver.Chrome(service=Service(CHROMEDRIVER), options=opts)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def setUp(self):
        self.driver.set_window_size(1440, 900)
        self._tmp_files = []

    def tearDown(self):
        for p in self._tmp_files:
            p.unlink(missing_ok=True)

    # ── helpers ──────────────────────────────────────────────────────────

    def _load(self, path):
        """加载页面并清 localStorage 后重载（列可见性/宽度跨用例隔离）。"""
        self.driver.get('file://' + str(path))
        WebDriverWait(self.driver, 8).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#tbody tr')))
        self.driver.execute_script('localStorage.clear();')
        self.driver.get('file://' + str(path))
        WebDriverWait(self.driver, 8).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#tbody tr')))
        error_collector(self.driver)

    def _load_drama(self, name):
        self._load(DRAMA / name)

    def _headers(self):
        return [th.text.strip() for th in
                self.driver.find_elements(By.CSS_SELECTOR, 'thead th')]

    def _col_index(self, label):
        """表头文本 → 单元格下标（thead 含序号列, 与 td 一一对齐）。"""
        heads = self._headers()
        self.assertIn(label, heads, f'表头缺少 {label}: {heads}')
        return heads.index(label)

    def _rows(self):
        return self.driver.find_elements(By.CSS_SELECTOR, 'tbody tr')

    def _hl_rows(self):
        return self.driver.find_elements(By.CSS_SELECTOR, 'tbody tr.hl-row')

    def _cell(self, row, idx):
        return row.find_elements(By.TAG_NAME, 'td')[idx].text.strip()

    def _gen_page(self, payload):
        stamp = str(int(time.time() * 1000))
        src = PROJECT / 'tests' / f'_tmp_defstate_{stamp}.json'
        out = PROJECT / 'tests' / f'_tmp_defstate_{stamp}.html'
        self._tmp_files += [src, out]
        src.write_text(json.dumps(payload, ensure_ascii=False), encoding='utf-8')
        proc = subprocess.run(
            [sys.executable, str(PROJECT / 'html-gen.py'), 'table',
             '-d', str(src), '-o', str(out)],
            capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0,
                         f'html-gen.py 生成失败: {proc.stderr!r}')
        return out, proc

    # ── 1) options.share ────────────────────────────────────────────────

    def test_01_share_default_on(self):
        """缺省不配 share → 按钮保留（既有页面零回归）。"""
        payload = dict(SHARE_PAYLOAD)
        out, proc = self._gen_page(payload)
        self.assertNotIn('未知选项', proc.stderr, f'新增键不应告警: {proc.stderr!r}')
        self.assertIn('id="shareBtn"', out.read_text(encoding='utf-8'),
                      '缺省应渲染分享按钮')

    def test_02_share_false_hides_button(self):
        """options.share=false → 产物不含按钮节点（占位符注入空串）。"""
        payload = dict(SHARE_PAYLOAD, options={'share': False})
        out, proc = self._gen_page(payload)
        self.assertNotIn('未知选项', proc.stderr, f'新增键不应告警: {proc.stderr!r}')
        self.assertNotIn('id="shareBtn"', out.read_text(encoding='utf-8'),
                         'share=false 应不渲染分享按钮')

    def test_03_share_hidden_on_all_timeline_pages(self):
        """四张时间轴页均隐藏分享按钮（含 home-link 容器不为空时也不报错）。"""
        for name in PAGES:
            with self.subTest(page=name):
                self._load_drama(name)
                self.assertFalse(self.driver.find_elements(By.ID, 'shareBtn'),
                                 f'{name}: 分享按钮应已隐藏')
                self.assertEqual(get_errors(self.driver), [])

    # ── 2) options.highlight ───────────────────────────────────────────

    def test_04_rows_and_highlight_counts(self):
        """默认不再筛选年号：全量行数 = 数据行数；高亮行数按 options.highlight。"""
        for name, exp in PAGES.items():
            with self.subTest(page=name):
                self._load_drama(name)
                rows, hl = self._rows(), self._hl_rows()
                self.assertEqual(len(rows), exp['rows'],
                                 f'{name}: 可见行数应 {exp["rows"]}: {len(rows)}')
                self.assertEqual(len(hl), exp['hl'],
                                 f'{name}: 高亮行数应 {exp["hl"]}: {len(hl)}')
                if exp['hl']:
                    self.assertTrue(all(exp['hl_value'] in r.text for r in hl),
                                    f'{name}: 高亮行应全为 {exp["hl_value"]}')
                self.assertEqual(get_errors(self.driver), [])

    def test_05_no_default_filter_pill(self):
        """移除 defaultFilter 后：无 quickFilter 筛选态（statFilteredPill 隐藏）。"""
        for name in PAGES:
            with self.subTest(page=name):
                self._load_drama(name)
                shown = self.driver.execute_script(
                    "var p=document.getElementById('statFilteredPill');"
                    "return p ? getComputedStyle(p).display : 'none';")
                self.assertEqual(shown, 'none', f'{name}: 不应有默认筛选态')

    def test_06_highlight_covers_frozen_column(self):
        """冻结列是不透明背景 → 高亮必须同步覆盖 td.frozen-col（否则年号列不着色）。"""
        self._load_drama('yongzheng-timeline-table.html')
        bg_hl = self.driver.execute_script(
            "var t=document.querySelector('tbody tr.hl-row td.frozen-col');"
            "return t ? getComputedStyle(t).backgroundColor : '';")
        bg_plain = self.driver.execute_script(
            "var r=document.querySelector('tbody tr:not(.hl-row) td.frozen-col');"
            "return r ? getComputedStyle(r).backgroundColor : '';")
        self.assertNotEqual(bg_hl, '', '高亮行应有冻结列单元格')
        self.assertNotEqual(bg_plain, '', '普通行应有冻结列单元格')
        self.assertNotEqual(bg_hl, bg_plain, '高亮行冻结列背景应与普通行不同')

    def test_07_highlight_survives_search(self):
        """高亮由数据派生：搜索过滤后命中行仍保持高亮。"""
        self._load_drama('yongzheng-timeline-table.html')
        before = len(self._hl_rows())
        self.assertGreater(before, 0)
        self.driver.find_element(By.ID, 'searchInput').send_keys('青海')
        time.sleep(0.6)
        rows = self._rows()
        self.assertEqual(len(rows), 1, f'搜索应命中 1 行: {len(rows)}')
        self.assertTrue(rows[0].get_attribute('class').find('hl-row') >= 0,
                        '搜索过滤后命中行仍应高亮')

    def test_08_highlight_coexists_with_split_active(self):
        """高亮 class 与分栏高亮 class 并存（不复用 split-active，互不清除）。"""
        self._load_drama('daming-timeline-table.html')
        total = len(self._hl_rows())
        self.assertGreater(total, 0)
        self.driver.execute_script(
            "var r=document.querySelector('tbody tr.hl-row td.cell-pills'); r.click();")
        time.sleep(0.6)
        act = self.driver.find_elements(By.CSS_SELECTOR, 'tbody tr.split-active')
        self.assertEqual(len(act), 1, '应有一行 split-active')
        self.assertIn('hl-row', act[0].get_attribute('class') or '',
                      'split-active 行应同时保留 hl-row')
        self.assertEqual(len(self._hl_rows()), total, '分栏不应清掉常驻高亮')

    # ── 3) options.defaultSort ─────────────────────────────────────────

    def test_09_default_sort_ascending(self):
        """默认按起止年份升序：首行为最早年份 + 表头箭头点亮；未配置页保持数据原序。"""
        for name, exp in PAGES.items():
            with self.subTest(page=name):
                self._load_drama(name)
                idx = self._col_index(exp['period_key'])
                first = self._cell(self._rows()[0], idx)
                self.assertEqual(first, exp['first'],
                                 f'{name}: 首行 {exp["period_key"]} 应 {exp["first"]}: {first}')
                th_cls = self.driver.execute_script(
                    "var ths=[...document.querySelectorAll('thead th')];"
                    "var t=ths[arguments[0]]; return t ? t.className : '';", idx)
                if exp['sorted']:
                    self.assertIn('sort-asc', th_cls,
                                  f'{name}: 默认排序列表头应有 sort-asc: {th_cls}')
                else:
                    self.assertNotIn('sort-asc', th_cls,
                                     f'{name}: 未配置默认排序不应点亮箭头: {th_cls}')

    def test_10_legacy_page_unaffected(self):
        """未配置默认态的既有表页（countries）：分享按钮仍在、无 hl-row、无默认排序。"""
        self._load(PROJECT / 'demos' / 'countries-table.html')
        self.assertTrue(self.driver.find_elements(By.ID, 'shareBtn'),
                        'countries 表分享按钮应仍在')
        self.assertEqual(len(self._hl_rows()), 0, 'countries 表不应有常驻高亮')
        self.assertEqual(self.driver.find_elements(By.CSS_SELECTOR, 'thead th.sort-asc'),
                         [], 'countries 表不应有默认排序箭头')
        self.assertEqual(get_errors(self.driver), [])


if __name__ == '__main__':
    unittest.main()
