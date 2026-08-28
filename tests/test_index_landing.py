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

    def test_02_hero_height(self):
        """hero 首屏高度 ≥0.75vh (80vh 设计, 容差)."""
        ratio = self.driver.execute_script(
            "var h = document.querySelector('.hero'); return h.offsetHeight / window.innerHeight;")
        self.assertGreaterEqual(ratio, 0.75, f"hero 高度不足: {ratio:.2f}")

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

    def test_09_theme_toggle(self):
        """主题按钮存在, 点击切换 :root.light 类并写入 localStorage, 再点恢复."""
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

    def test_10_copy_buttons(self):
        """复制按钮: hero 安装&快速开始块(复制全部 1 + 行内 6) + 四卡 cli-box 4 = 11 处, data-copy 非空且关键命令完整."""
        btns = self.driver.find_elements(By.CSS_SELECTOR, '.copy-btn')
        self.assertEqual(11, len(btns), f"复制按钮数量应为 11: {len(btns)}")
        for b in btns:
            self.assertTrue(b.get_attribute('data-copy'), "data-copy 为空")
        # HG-SEC-038: 含引号命令必须完整转义（此前 PATH 行被截断为 'export PATH='）
        path_btn = next(b for b in btns if (b.get_attribute('data-copy') or '').startswith('export PATH'))
        self.assertEqual('export PATH="$HOME/.local/bin:$PATH"', path_btn.get_attribute('data-copy'),
                         "PATH 行 data-copy 应完整含引号")
        all_btn = next(b for b in btns if '复制全部' in (b.text or ''))
        all_copy = all_btn.get_attribute('data-copy') or ''
        self.assertIn('bash install.sh install', all_copy, "复制全部缺安装命令")
        self.assertIn('html-gen slide', all_copy, "复制全部缺 slide 命令")

    def test_11_footer_links(self):
        """footer 存在且含 GitHub / Gitee / PyPI 链接 + favicon 图标."""
        footer = self.driver.find_element(By.CSS_SELECTOR, 'footer.site-footer')
        hrefs = [a.get_attribute('href') or '' for a in footer.find_elements(By.TAG_NAME, 'a')]
        self.assertTrue(any('github.com/imjaden/html-gen.cli' in h for h in hrefs), "缺 GitHub 链接")
        self.assertTrue(any('gitee.com/imjaden/html-gen.cli' in h for h in hrefs), "缺 Gitee 链接")
        self.assertTrue(any('pypi.org/project/html-gen-cli' in h for h in hrefs), "缺 PyPI 链接")
        imgs = [i.get_attribute('src') or '' for i in footer.find_elements(By.CSS_SELECTOR, 'img.favicon')]
        self.assertEqual(3, len(imgs), f"应有 3 个 favicon 图标: {imgs}")
        self.assertTrue(all('favicon' in s for s in imgs), f"favicon src 异常: {imgs}")

    def test_12_theme_persist(self):
        """浅色偏好 localStorage 持久化: 预置 light 后刷新仍为浅色."""
        self.driver.execute_script("localStorage.setItem('html-gen:index_theme', 'light');")
        self.driver.refresh()
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.hero')))
        time.sleep(0.2)
        self.assertTrue(self.driver.execute_script(
            "return document.documentElement.classList.contains('light');"), "刷新后浅色未恢复")
        self.driver.execute_script("localStorage.removeItem('html-gen:index_theme');")

    def test_13_hero_dynamic_height(self):
        """动态两屏: hero 高度 ≥ 视口高 − 55px (JS min-height, 内容可更高)."""
        hero_h = self.driver.execute_script("return document.querySelector('.hero').offsetHeight;")
        vh = self.driver.execute_script("return window.innerHeight;")
        self.assertGreaterEqual(hero_h, vh - 55,
                                f"hero 高度应 ≥ vh−55: hero={hero_h} vh={vh}")

    def test_14_scroll_hint_fixed_and_fade(self):
        """'↓ 模板说明' fixed 定位居首屏底部, 滚动后淡出, 回顶恢复."""
        hint = self.driver.find_element(By.CSS_SELECTOR, 'a.scroll-hint')
        self.assertEqual('fixed', self.driver.execute_script(
            "return getComputedStyle(document.querySelector('.scroll-hint')).position;"), "应 fixed 定位")
        # 首屏可见
        self.assertFalse(self.driver.execute_script(
            "return document.querySelector('.scroll-hint').classList.contains('hide');"), "初始应可见")
        # 滚动后淡出
        self.driver.execute_script("window.scrollTo(0, 300);")
        time.sleep(0.3)
        self.assertTrue(self.driver.execute_script(
            "return document.querySelector('.scroll-hint').classList.contains('hide');"), "滚动后应隐藏")
        # 回顶恢复
        self.driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(0.3)
        self.assertFalse(self.driver.execute_script(
            "return document.querySelector('.scroll-hint').classList.contains('hide');"), "回顶应恢复显示")

    def test_15_github_corner_light_white(self):
        """light 模式 github-corner octocat 为白色 (深三角 + 白猫)."""
        btn = self.driver.find_element(By.CSS_SELECTOR, '#themeBtn')
        btn.click()
        time.sleep(0.2)
        color = self.driver.execute_script(
            "return getComputedStyle(document.querySelector('.github-corner')).color;")
        self.assertEqual('rgb(255, 255, 255)', color, f"light 下 octocat 应为白色: {color}")
        btn.click()
        time.sleep(0.2)

    def test_16_hero_badges(self):
        """hero 特性徽章行存在, 4 项核心卖点."""
        badges = self.driver.find_elements(By.CSS_SELECTOR, '.hero-badges span')
        self.assertEqual(4, len(badges), f"badges 应为 4 项: {[b.text for b in badges]}")
        text = ' '.join(b.text for b in badges)
        for kw in ['零依赖', '深色主题', '中文优先', '单文件']:
            self.assertIn(kw, text, f"badges 缺 {kw}")

    def test_17_compare_table(self):
        """竞品对比卡: 6 维度行, html-gen 列全 ✓ 高亮."""
        table = self.driver.find_element(By.CSS_SELECTOR, '.compare-table')
        rows = table.find_elements(By.CSS_SELECTOR, 'tbody tr')
        self.assertEqual(6, len(rows), f"对比表应 6 行: {len(rows)}")
        heads = [th.text for th in table.find_elements(By.CSS_SELECTOR, 'thead th')]
        self.assertEqual(['', '手写 HTML', 'pandoc', 'mdbook', 'html-gen'], heads,
                         f"对比表头: {heads}")
        wins = table.find_elements(By.CSS_SELECTOR, 'td.win')
        self.assertEqual(6, len(wins), f"html-gen 列应全 ✓: {len(wins)}")
        for w in wins:
            self.assertEqual('✓', w.text, f"win 单元格应为 ✓: {w.text}")

    def test_18_hero_logo(self):
        """hero-title 前置品牌图标 (favicon)."""
        logo = self.driver.find_element(By.CSS_SELECTOR, '.hero-title img.hero-logo')
        src = logo.get_attribute('src') or ''
        self.assertIn('favicon', src, f"hero 图标应为 favicon: {src}")


if __name__ == '__main__':
    unittest.main()
