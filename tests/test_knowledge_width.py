"""回归测试: knowledge 条目级宽度 width=narrow|medium|wide（CL018 T2）。"""
import json
import subprocess
import tempfile
import time
import unittest
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

CHROMEDRIVER = '/Users/jadenli/CodeSpace/script-miner/cache/chromedriver/chromedriver'
GEN = Path(__file__).resolve().parent.parent / 'html-gen.py'


class TestKnowledgeWidth(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix='_tmp_kw_'))
        for name in ('a.html', 'b.html', 'c-overview.html'):
            (cls.tmp / name).write_text('<html><body><div id="docBody">x</div></body></html>',
                                        encoding='utf-8')
        data = [
            {'title': 'A', 'group': 'g1', 'section': 'SA', 'url': 'a.html', 'width': 'wide'},
            {'title': 'B', 'group': 'g2', 'section': 'SB', 'url': 'b.html'},
            {'title': 'C', 'group': 'g3', 'section': 'SC', 'url': 'c-overview.html'},
            {'title': 'D', 'group': 'g4', 'section': 'SD', 'url': 'a.html', 'width': 'narrow'},
        ]
        groups = [{'key': f'g{i}', 'label': f'G{i}'} for i in range(1, 5)]
        (cls.tmp / 'data.json').write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
        (cls.tmp / 'groups.json').write_text(json.dumps(groups, ensure_ascii=False), encoding='utf-8')
        cls.out = cls.tmp / 'kb.html'
        r = subprocess.run(['python3', str(GEN), 'knowledge', '-d', str(cls.tmp / 'data.json'),
                            '-g', str(cls.tmp / 'groups.json'), '-o', str(cls.out),
                            '--title', 'W', '--quiet'],
                           capture_output=True, text=True, timeout=60)
        assert r.returncode == 0, r.stderr

        opts = Options()
        opts.add_argument('--headless=new')
        opts.add_argument('--no-sandbox')
        opts.add_argument('--disable-dev-shm-usage')
        cls.driver = webdriver.Chrome(service=Service(CHROMEDRIVER), options=opts)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        import shutil
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def setUp(self):
        self.driver.set_window_size(1440, 900)
        self.driver.get('file://' + str(self.out))
        WebDriverWait(self.driver, 8).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.kw-tab')))
        time.sleep(0.3)
        self.driver.execute_script('localStorage.clear();')
        self.driver.get('file://' + str(self.out))
        WebDriverWait(self.driver, 8).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.kw-tab')))

    def _frame_src(self, group, section):
        self.driver.execute_script("selectSection(arguments[0], arguments[1]);", group, section)
        time.sleep(0.4)
        return self.driver.execute_script(
            "return document.getElementById('contentFrame').src;")

    def test_01_explicit_wide(self):
        self.assertIn('width=wide', self._frame_src('g1', 'SA'))

    def test_02_default_no_width(self):
        self.assertNotIn('width=', self._frame_src('g2', 'SB'))

    def test_03_overview_defaults_wide(self):
        self.assertIn('width=wide', self._frame_src('g3', 'SC'))

    def test_04_explicit_narrow(self):
        self.assertIn('width=narrow', self._frame_src('g4', 'SD'))

    def test_05_params_keep_sidebar_toolbar(self):
        src = self._frame_src('g1', 'SA')
        self.assertIn('sidebar=0', src)
        self.assertIn('toolbar=0', src)


if __name__ == '__main__':
    unittest.main()
