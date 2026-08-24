"""回归测试: demos/index.html（模板展示首页）— 主题切换 / 复制按钮 / footer / 双源一致性.

页面: PROJECT/demos/index.html (模板展示首页, 与根 index.html 双源同步).
双源一致性: 根 index.html 与 demos/index.html 为独立副本, 关键功能特征须保持一致 (D14-14B).
"""
import time, unittest
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

CHROMEDRIVER = '/Users/jadenli/CodeSpace/script-miner/cache/chromedriver/chromedriver'
PROJECT = Path(__file__).resolve().parent.parent
DEMOS_INDEX = PROJECT / 'demos' / 'index.html'
ROOT_INDEX = PROJECT / 'index.html'


class TestDemosIndex(unittest.TestCase):

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
        self.driver.set_window_size(1400, 900)
        self.driver.get('file://' + str(DEMOS_INDEX))
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.template-grid')))
        self.driver.execute_script("window.scrollTo(0, 0);")
        errs = self._errors()
        self.assertEqual([], [e['message'][:120] for e in errs], "加载后出现 JS 错误")

    def _errors(self):
        return [e for e in self.driver.get_log('browser') if e['level'] in ('SEVERE', 'ERROR')]

    def test_01_no_js_errors(self):
        """demos 页无 JS 错误."""
        errs = self._errors()
        self.assertEqual([], [e['message'][:120] for e in errs], "应有 JS 错误")

    def test_02_theme_button(self):
        """主题按钮存在, 点击切换 :root.light 类并写入 localStorage."""
        btn = self.driver.find_element(By.CSS_SELECTOR, '#themeBtn')
        self.assertFalse(self.driver.execute_script(
            "return document.documentElement.classList.contains('light');"), "初始应为深色")
        btn.click()
        time.sleep(0.2)
        self.assertTrue(self.driver.execute_script(
            "return document.documentElement.classList.contains('light');"), "点击后未切浅色")
        self.assertEqual('light', self.driver.execute_script(
            "return localStorage.getItem('html-gen:index_theme');"), "localStorage 未写入 light")
        btn.click()
        time.sleep(0.2)
        self.assertFalse(self.driver.execute_script(
            "return document.documentElement.classList.contains('light');"), "再点未恢复深色")

    def test_03_copy_buttons(self):
        """四卡 cli-box 复制按钮 4 处, data-copy 非空."""
        btns = self.driver.find_elements(By.CSS_SELECTOR, '.cli-box .copy-btn')
        self.assertEqual(4, len(btns), f"cli-box 复制按钮数量应为 4: {len(btns)}")
        for b in btns:
            self.assertTrue(b.get_attribute('data-copy'), "data-copy 为空")

    def test_04_footer_links(self):
        """footer 存在且含 GitHub / Gitee 链接."""
        footer = self.driver.find_element(By.CSS_SELECTOR, 'footer.site-footer')
        hrefs = [a.get_attribute('href') or '' for a in footer.find_elements(By.TAG_NAME, 'a')]
        self.assertTrue(any('github.com/imjaden/html-gen.cli' in h for h in hrefs), "缺 GitHub 链接")
        self.assertTrue(any('gitee.com/imjaden/html-gen.cli' in h for h in hrefs), "缺 Gitee 链接")

    def test_05_dual_source_consistency(self):
        """双源一致性: 根 index.html 与 demos/index.html 关键功能特征一致 (防漂移)."""
        root = ROOT_INDEX.read_text(encoding='utf-8')
        demos = DEMOS_INDEX.read_text(encoding='utf-8')
        features = [
            'id="themeBtn"',            # 主题按钮
            'html-gen:index_theme',     # 主题 localStorage key
            'class="site-footer"',      # footer 元素
            'class="copy-btn"',         # 复制按钮
            'max-width: 1500px',        # 2 列断点
            '--gh-octocat',             # github-corner 浅色变量
            'html-gen table -d data.json',   # A 卡 cli 命令
            'html-gen doc -i report.md',     # B 卡 cli 命令
            'html-gen knowledge -d data.json',  # C 卡 cli 命令
            'html-gen slide -i slides.md',   # D 卡 cli 命令
            'demos-title',              # 案例区
        ]
        missing_root = [f for f in features if f not in root]
        missing_demos = [f for f in features if f not in demos]
        self.assertEqual([], missing_root, f"根 index.html 缺少: {missing_root}")
        self.assertEqual([], missing_demos, f"demos/index.html 缺少: {missing_demos}")

    def test_06_github_corner_light(self):
        """light 模式 demos 页 github-corner octocat 为白色 (双源同步)."""
        btn = self.driver.find_element(By.CSS_SELECTOR, '#themeBtn')
        btn.click()
        time.sleep(0.2)
        color = self.driver.execute_script(
            "return getComputedStyle(document.querySelector('.github-corner')).color;")
        self.assertEqual('rgb(255, 255, 255)', color, f"light 下 octocat 应为白色: {color}")
        btn.click()
        time.sleep(0.2)


if __name__ == '__main__':
    unittest.main()
