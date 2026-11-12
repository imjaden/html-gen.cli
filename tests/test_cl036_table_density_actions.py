"""CL036: table 模板 —— 分享按钮落位（表头）+ 密度三档可读性 + 契约导出/严格模式/产物版本戳。

分两组：
- 静态/子进程组（快）：契约 JSON、--strict、未知键令牌、产物结构断言；
- Selenium 组（慢）：tabs 行折叠、密度入口恒在、切档改字号/写 URL。
夹具输出一律 tempfile.mkdtemp()（CL034 约定）。
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
GEN = PROJECT / 'html-gen.py'

PAYLOAD = {
    'columns': [{'key': 'name', 'label': '名称', 'width': '160px'},
                {'key': 'count', 'label': '数量', 'type': 'number', 'width': '100px'}],
    'data': [{'name': 'A', 'count': 1}, {'name': 'B', 'count': 2}],
}
PAYLOAD_TABS = dict(PAYLOAD, tabs=[{'key': 'all', 'label': '全部'}, {'key': 'a', 'label': 'A', 'match': 'name'}])


def run_gen(payload, out, *extra):
    src = out.with_suffix('.json')
    src.write_text(json.dumps(payload, ensure_ascii=False), encoding='utf-8')
    return subprocess.run([sys.executable, str(GEN), 'table', '-d', str(src), '-o', str(out), *extra],
                          capture_output=True, text=True)


class TestCl036ContractAndProduct(unittest.TestCase):
    """契约/CLI/产物结构（无浏览器）。"""

    @classmethod
    def setUpClass(cls):
        cls.tmpdir = Path(tempfile.mkdtemp(prefix='hg-cl036-'))
        cls.out = cls.tmpdir / 'p.html'
        r = run_gen(PAYLOAD_TABS, cls.out)
        assert r.returncode == 0, r.stderr
        cls.html = cls.out.read_text(encoding='utf-8')

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmpdir, ignore_errors=True)

    # ── 1. help --json 机器可读契约 (D9) ──
    def test_01_help_json_contract_exposes_density_and_stamps(self):
        r = subprocess.run([sys.executable, str(GEN), 'help', 'table', '--json'],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        d = json.loads(r.stdout)['data']
        opts = [e[0] for e in d['contract']['data']['options']]
        self.assertIn('density', opts, 'options 契约应含 density')
        self.assertIn('?density', [e[0] for e in d['contract']['url_state']])
        self.assertIn('table', d['template_stamps'])
        # 产物戳必须与契约导出的一致（跨仓 drift 比对的锚点）
        m = re.search(r'<meta name="generator" content="([^"]+)">', self.html)
        self.assertIsNotNone(m, '产物缺 generator 版本戳')
        stamp = m.group(1)
        self.assertEqual(stamp, d['template_stamps']['table'],
                         '产物 generator 戳应与 help --json 的 template_stamps.table 一致')

    # ── 2. --strict 升级为错误 (D10) ──
    def test_02_strict_rejects_unknown_keys(self):
        bad = dict(PAYLOAD, options={'nope': True})
        out = self.tmpdir / 'bad.html'
        loose = run_gen(bad, out)
        self.assertEqual(loose.returncode, 0, '宽松模式应仅告警不阻断')
        self.assertIn('WARN_UNKNOWN_KEY', loose.stderr, '未知键应有稳定机器令牌')
        self.assertIn('未知选项', loose.stderr, '人读文案应保留')
        self.assertNotIn('WARN_UNKNOWN_KEY', loose.stdout, '告警不得污染 stdout')
        strict = run_gen(bad, out, '--strict')
        self.assertEqual(strict.returncode, 2, '--strict 应 exit 2')

    # ── 3. options.density 是合法键（不得被未知键告警） ──
    def test_03_options_density_is_known_key(self):
        out = self.tmpdir / 'density.html'
        r = run_gen(dict(PAYLOAD, options={'density': 'comfortable'}), out)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn('WARN_UNKNOWN_KEY', r.stderr, f'density 应为已知键: {r.stderr!r}')
        self.assertIn('"density": "comfortable"', out.read_text(encoding='utf-8').replace("'", '"'))

    # ── 4. 产物结构：分享按钮在表头、tabs-actions 空、折叠规则与字号变量就位 ──
    def test_04_share_button_in_header_and_density_css(self):
        h = self.html
        self.assertLess(h.index('<div class="table-header">'), h.index('id="shareBtn"'),
                        'CL036: 分享按钮应在 .table-header 内')
        self.assertLess(h.index('id="shareBtn"'), h.index('<div class="flex-1">'),
                        'CL036: 分享按钮在统计 pill 之后、弹性占位之前')
        self.assertNotIn('id="shareBtn"', h[h.index('<div class="tabs-actions">'):h.index('<div class="table-main"')],
                         'tabs-actions 不得再承载分享按钮')
        self.assertIn('.tabs-row.no-tabs', h.replace(' ', ''), '缺 tabs 行折叠规则')
        # 跨仓硬约束: normalize_skeleton 用精确串定位, 该容器不得带额外属性
        self.assertIn('<div class="tabs-row">', h, 'tabs-row 开标签必须逐字为 <div class="tabs-row">')
        self.assertIn('--table-fs', h, '缺字号变量')
        for cls in ('.data-table.dense{--table-fs', '.data-table.comfortable{--table-fs'):
            self.assertIn(cls, h.replace(' ', ''), f'缺密度档变量: {cls}')
        self.assertIn('🔗', h, '分享图标应为 🔗')


class TestCl036Selenium(unittest.TestCase):
    """行为（Selenium headless）。"""

    @classmethod
    def setUpClass(cls):
        from conftest import chromedriver_service
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        cls.tmpdir = Path(tempfile.mkdtemp(prefix='hg-cl036-sel-'))
        cls.nomtab = cls.tmpdir / 'notabs.html'
        cls.tabs = cls.tmpdir / 'tabs.html'
        for payload, out in ((PAYLOAD, cls.nomtab), (PAYLOAD_TABS, cls.tabs)):
            r = run_gen(payload, out)
            assert r.returncode == 0, r.stderr
        opts = Options()
        opts.add_argument('--headless')
        opts.add_argument('--no-sandbox')
        opts.add_argument('--disable-dev-shm-usage')
        cls.driver = webdriver.Chrome(service=chromedriver_service(), options=opts)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        shutil.rmtree(cls.tmpdir, ignore_errors=True)

    def _wait_rows(self):
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.by import By
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#tbody tr')))

    def test_05_no_tabs_row_collapses(self):
        self.driver.get('file://' + str(self.nomtab))
        self._wait_rows()
        row = self.driver.find_element('css selector', '.tabs-row')
        self.assertIn('no-tabs', row.get_attribute('class'), '单视图页应折叠 tabs 行')
        self.assertEqual(row.value_of_css_property('display'), 'none')

    def test_06_density_entry_always_rendered_and_switches(self):
        from selenium.webdriver.common.by import By
        self.driver.get('file://' + str(self.tabs))
        self._wait_rows()
        self.driver.find_element('id', 'colToggleBtn').click()
        time.sleep(0.3)
        radios = [r.get_attribute('value') for r in self.driver.find_elements(By.NAME, 'density')]
        self.assertEqual(sorted(radios), ['comfortable', 'compact', 'default'],
                         'CL036: 密度入口必须恒在（原先单视图页整段不渲染）')
        td = self.driver.find_element(By.CSS_SELECTOR, '.data-table tbody td')
        base = float(td.value_of_css_property('font-size')[:-2])
        self.driver.execute_script("window.setDensity('comfortable')")
        time.sleep(0.3)
        comf = float(td.value_of_css_property('font-size')[:-2])
        self.assertGreater(comf, base, 'comfortable 应比 default 字号大')
        self.assertIn('density=comfortable', self.driver.current_url, '切档应写入 ?density=')
        self.assertIn('density=comfortable', self.driver.execute_script('return buildShareUrl();'),
                      '分享链接应带上密度')


if __name__ == '__main__':
    unittest.main()
