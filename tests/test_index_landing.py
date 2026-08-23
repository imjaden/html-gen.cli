"""回归测试: 根 index.html 落地页 — hero 100vh / github-corner / 滑屏 / 上箭头 A+B / 案例区统一.

页面: PROJECT/index.html (落地页, 非 demos 生成物).
"""
import time, unittest
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

CHROMEDRIVER = '/Users/jadenli/CodeSpace/script-miner/cache/chromedriver/chromedriver'
PROJECT = Path(__file__).resolve().parent.parent
INDEX = PROJECT / 'index.html'


class TestIndexLanding(unittest.TestCase):

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
        self.driver.get('file://' + str(INDEX))
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.hero')))
        self.driver.execute_script("window.scrollTo(0, 0);")
        # 每个测试方法加载后统一检查 JS 错误（HG-SEC-017: 覆盖全部用例，不止 test_01）
        errs = self._errors()
        self.assertEqual([], [e['message'][:120] for e in errs], "加载后出现 JS 错误")

    def _errors(self):
        """浏览器 console 中的 SEVERE/ERROR."""
        return [e for e in self.driver.get_log('browser') if e['level'] in ('SEVERE', 'ERROR')]

    def test_01_no_js_errors(self):
        """落地页无 JS 错误."""
        errs = self._errors()
        self.assertEqual([], [e['message'][:120] for e in errs], "应有 JS 错误")

    def test_02_hero_100vh(self):
        """hero 撑满首屏 (100vh)."""
        ratio = self.driver.execute_script(
            "var h = document.querySelector('.hero'); return h.offsetHeight / window.innerHeight;")
        self.assertGreater(ratio, 0.95, f"hero 未撑满视口: {ratio:.2f}")

    def test_03_github_corner_clickable(self):
        """github 图标本体可点 + hover 波浪动画 + 链接指向 html-gen.cli + 无 hit 区."""
        pe = self.driver.execute_script(
            "return getComputedStyle(document.querySelector('.github-corner')).pointerEvents;")
        self.assertEqual('auto', pe, "图标不可点击 (pointer-events 应为 auto)")
        href = self.driver.find_element(By.CSS_SELECTOR, '.github-corner').get_attribute('href')
        self.assertIn('github.com/imjaden/html-gen.cli', href, "github 链接未指向 html-gen.cli")
        self.assertEqual(0, len(self.driver.find_elements(By.CSS_SELECTOR, '.github-corner-hit')),
                         "不应残留隐藏 hit 区")
        ActionChains(self.driver).move_to_element(
            self.driver.find_element(By.CSS_SELECTOR, '.github-corner')).perform()
        time.sleep(0.2)
        anim = self.driver.execute_script(
            "return getComputedStyle(document.querySelector('.octo-arm')).animationName;")
        self.assertEqual('octocat-wave', anim, "hover 未触发波浪动画")

    def test_04_scroll_hint_to_templates(self):
        """'↓ 模板说明' 点击平滑滑到模板区."""
        hint = self.driver.find_element(By.CSS_SELECTOR, 'a.scroll-hint')
        self.assertEqual('templates', hint.get_attribute('href').split('#')[-1])
        hint.click()
        time.sleep(1.2)
        top = self.driver.execute_script(
            "return document.getElementById('templates').getBoundingClientRect().top;")
        self.assertLess(abs(top), 60, f"滑屏未到位: top={top:.0f}")

    def test_05_back_top_a(self):
        """A 形式: 模板区标题行 '↑ 返回首页' 点击回顶."""
        self.driver.execute_script("window.scrollTo(0, document.getElementById('templates').offsetTop);")
        time.sleep(0.6)
        link = self.driver.find_element(By.CSS_SELECTOR, 'a.back-top-link')
        self.assertEqual('top', link.get_attribute('href').split('#')[-1], "A 形式应指向 #top")
        link.click()
        time.sleep(1.2)
        self.assertEqual(0, self.driver.execute_script("return window.scrollY;"), "A 形式未回顶")

    def test_06_back_top_b(self):
        """B 形式: 固定右下角按钮滚动超过一屏显示, 点击回顶, 回顶后隐藏."""
        btn = self.driver.find_element(By.CSS_SELECTOR, 'a.back-to-top')
        self.assertEqual('top', btn.get_attribute('href').split('#')[-1], "B 形式应指向 #top")
        # 初始隐藏
        self.assertFalse(self.driver.execute_script(
            "return document.querySelector('.back-to-top').classList.contains('show');"), "初始应隐藏")
        # 滚动到底显示
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.6)
        self.assertTrue(self.driver.execute_script(
            "return document.querySelector('.back-to-top').classList.contains('show');"), "滚动后应显示")
        self.assertEqual('visible', self.driver.execute_script(
            "return getComputedStyle(document.querySelector('.back-to-top')).visibility;"), "应可见")
        # 点击回顶
        btn.click()
        time.sleep(1.2)
        self.assertEqual(0, self.driver.execute_script("return window.scrollY;"), "B 形式未回顶")
        time.sleep(0.4)
        self.assertFalse(self.driver.execute_script(
            "return document.querySelector('.back-to-top').classList.contains('show');"), "回顶后应隐藏")

    def test_07_case_demos_unified(self):
        """四卡案例区标题统一 '案例演示', demo-item 结构 icon+name+desc+arrow."""
        titles = self.driver.execute_script(
            "return [...document.querySelectorAll('.demos-title')].map(e => e.textContent);")
        self.assertEqual(['案例演示'] * 4, titles, "四卡标题应统一")
        structs = self.driver.execute_script("""
return [...document.querySelectorAll('.tpl .demos')].map(d => {
  const items = [...d.querySelectorAll('.demo-item')];
  return items.every(i => i.querySelector('.demo-icon') && i.querySelector('.demo-info .demo-name') && i.querySelector('.demo-arrow'));
});
""")
        self.assertTrue(all(structs) and len(structs) == 4, f"demo-item 结构不完整: {structs}")

    def test_08_local_links_no_old_repo(self):
        """落地页相对链接均指向 demos/ 前缀且 github 链接为新仓库 (无旧链接)."""
        html = INDEX.read_text(encoding='utf-8')
        self.assertNotIn('github.com/imjaden/html-gen"', html, "存在旧 github 仓库链接")
        self.assertNotIn('github.com/imjaden/html-gen.cli.cli', html, "存在双后缀链接")
        self.assertNotIn('html-gen.lab.jaden.tech', html, "存在旧域名引用")
        self.assertIn('github.com/imjaden/html-gen.cli', html, "缺少新 github 链接")


if __name__ == '__main__':
    unittest.main()
