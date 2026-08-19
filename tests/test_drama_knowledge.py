"""Selenium test: drama-knowledge.html — 以剧读史影视历史知识库 (v2: section-as-menu)."""
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
DEMO = PROJECT / 'demos' / 'drama-knowledge.html'


class TestDramaKnowledge(unittest.TestCase):

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
        self.driver.get('file://' + str(DEMO))
        time.sleep(0.2)
        self.driver.execute_script("localStorage.clear();")
        self.driver.get('file://' + str(DEMO))
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.kw-tab')))
        self.driver.execute_script(
            "window.__testErrors = [];"
            "window.onerror = function(m) { window.__testErrors.push(String(m)); };"
        )

    def _errors(self):
        return self.driver.execute_script("return window.__testErrors;")

    def _tab_labels(self):
        return [t.text.split('\n')[-1].strip() for t in self.driver.find_elements(By.CSS_SELECTOR, '.kw-tab')]

    def _section_titles(self):
        return [s.text for s in self.driver.find_elements(By.CSS_SELECTOR, '.kw-section-title')]

    def _iframe_src(self):
        src = self.driver.find_element(By.ID, 'contentFrame').get_attribute('src') or ''
        return src.split('?')[0]

    # ── T1: Tab order ──

    def test_01_tabs_render_order(self):
        labels = self._tab_labels()
        self.assertEqual(labels, ['中国历史', '大明王朝1566', '雍正王朝'],
                         f"Tabs: {labels}")

    # ── T2: Section rendering (3 sections, no kw-item rows) ──

    def test_02_sections_render_as_menu(self):
        """D2: 中国历史 group: 3 sections, 0 items (single-item sections skipped)."""
        sections = self._section_titles()
        self.assertEqual([s.split('\n')[-1] for s in sections], ['概述', '时间轴', '36计策'],
                         f"Sections: {sections}")
        self.assertEqual(self._errors(), [], f"JS errors: {self._errors()}")

    def test_02b_section_icons(self):
        """D4: section 菜单项带 icon 前缀（📋/📅/🧮）."""
        sections = self._section_titles()
        self.assertEqual(sections[0].split('\n')[0], '📋', f"概述 icon: {sections[0]}")
        self.assertEqual(sections[1].split('\n')[0], '📅', f"时间轴 icon: {sections[1]}")
        self.assertEqual(sections[2].split('\n')[0], '🧮', f"36计策 icon: {sections[2]}")
        items = self.driver.find_elements(By.CSS_SELECTOR, '.kw-item')
        self.assertEqual(len(items), 0, "Single-item sections should not render kw-item rows")

    # ── T3: Section click opens iframe ──

    def test_03_section_click_timeline_history(self):
        """Click 中国历史 时间轴 section → iframe src = history-timeline-table.html."""
        sections = self.driver.find_elements(By.CSS_SELECTOR, '.kw-section-title')
        # 时间轴 is the 2nd section
        sections[1].click()
        time.sleep(0.15)  # [speedup]

        src = self._iframe_src()
        self.assertTrue(src.endswith('drama/history-timeline-table.html'),
                        f"Expected timeline, got: {src}")

    def test_04_section_click_overview_daming(self):
        """Click 大明 概述 section → iframe src = daming-overview.html."""
        self.driver.find_elements(By.CSS_SELECTOR, '.kw-tab')[1].click()
        time.sleep(0.15)  # [speedup]

        sections = self.driver.find_elements(By.CSS_SELECTOR, '.kw-section-title')
        sections[0].click()  # 概述
        time.sleep(0.15)  # [speedup]

        src = self._iframe_src()
        self.assertTrue(src.endswith('drama/daming-overview.html'),
                        f"Expected overview, got: {src}")

    def test_05_section_click_strategy_daming(self):
        """Click 大明 36计策 section → iframe src = daming-strategy-table.html."""
        self.driver.find_elements(By.CSS_SELECTOR, '.kw-tab')[1].click()
        time.sleep(0.15)  # [speedup]

        sections = self.driver.find_elements(By.CSS_SELECTOR, '.kw-section-title')
        sections[2].click()  # 36计策
        time.sleep(0.15)  # [speedup]

        src = self._iframe_src()
        self.assertTrue(src.endswith('drama/daming-strategy-table.html'),
                        f"Expected strategy, got: {src}")

    # ── T4: Title 重复不串组 ──

    def test_06_title_duplicate_no_cross_group(self):
        """'概述' in 中国历史 != '概述' in 大明 (K1: selectItem by group+title)."""
        # Click 中国历史 概述
        sections = self.driver.find_elements(By.CSS_SELECTOR, '.kw-section-title')
        sections[0].click()
        time.sleep(0.15)  # [speedup]

        self.assertTrue(self._iframe_src().endswith('drama/history-overview.html'))
        # Switch to 大明, click 概述
        self.driver.find_elements(By.CSS_SELECTOR, '.kw-tab')[1].click()
        time.sleep(0.15)  # [speedup]

        sections2 = self.driver.find_elements(By.CSS_SELECTOR, '.kw-section-title')
        sections2[0].click()
        time.sleep(0.15)  # [speedup]

        self.assertTrue(self._iframe_src().endswith('drama/daming-overview.html'),
                        "Cross-group title should not collide")

    # ── T5: State restore ──

    def test_07_restore_state(self):
        """Refresh restores group + section."""
        self.driver.find_elements(By.CSS_SELECTOR, '.kw-tab')[1].click()
        time.sleep(0.15)  # [speedup]

        self.driver.find_elements(By.CSS_SELECTOR, '.kw-section-title')[1].click()  # 时间轴
        time.sleep(0.15)  # [speedup]

        self.driver.get('file://' + str(DEMO))
        time.sleep(0.3)  # [speedup]

        active = self.driver.find_elements(By.CSS_SELECTOR, '.kw-tab.active')
        self.assertEqual(len(active), 1)
        self.assertEqual(active[0].text.split('\n')[-1].strip(), '大明王朝1566',
                         "Should restore group")
        self.assertTrue(self._iframe_src().endswith('drama/daming-timeline-table.html'),
                        "Should restore section URL")

    # ── T6: Table content pages ──

    def test_08_daming_timeline_single_table(self):
        """大明时间轴 table 应为单表 17 年号，默认筛选嘉靖（本剧年号）."""
        self.driver.find_elements(By.CSS_SELECTOR, '.kw-tab')[1].click()
        time.sleep(0.15)  # [speedup]

        self.driver.find_elements(By.CSS_SELECTOR, '.kw-section-title')[1].click()
        time.sleep(0.25)  # [speedup]

        frame = self.driver.find_element(By.ID, 'contentFrame')
        self.driver.switch_to.frame(frame)
        heads = [th.text for th in self.driver.find_elements(By.CSS_SELECTOR, 'thead th')]
        self.assertEqual(heads,
                         ['序号', '年号', '皇帝', '庙号', '起止年份', '关键人物', '主要事件', '出处'],
                         f"大明时间轴表头: {heads}")
        rows = self.driver.find_elements(By.CSS_SELECTOR, 'tbody tr')
        self.assertEqual(len(rows), 8, f"默认应筛选嘉靖拆分 8 行: {len(rows)}")
        self.assertIn('嘉靖', rows[0].text, f"默认行应为嘉靖: {rows[0].text[:40]}")
        self.driver.switch_to.default_content()

    def test_17_section_follows_group_switch(self):
        """需求: 切顶部 tab 时左侧 section 跨组保持（大明 36计策 → 中国历史 36计策）."""
        self.driver.find_elements(By.CSS_SELECTOR, '.kw-tab')[1].click()  # 大明
        time.sleep(0.2)  # [speedup]

        secs = self.driver.find_elements(By.CSS_SELECTOR, '.kw-section-title')
        sec36 = next(s for s in secs if '36计策' in s.text)
        sec36.click()
        time.sleep(0.25)  # [speedup]

        self.driver.find_elements(By.CSS_SELECTOR, '.kw-tab')[0].click()  # 中国历史
        time.sleep(0.3)  # [speedup]

        act = self.driver.execute_script(
            "return document.querySelector('.kw-section-title.active').textContent || '';")
        self.assertIn('36计策', act, f"跨组应保持 36计策: {act}")
        frame = self.driver.find_element(By.ID, 'contentFrame')
        self.assertIn('history-strategy', frame.get_attribute('src') or '',
                      f"iframe 应为中国历史 36计策: {(frame.get_attribute('src') or '')[:70]}")

    def test_18_yongzheng_group(self):
        """新增雍正王朝 group：3 tab + 时间轴默认雍正 9 行 + 36计策 8 行."""
        tabs = self.driver.find_elements(By.CSS_SELECTOR, '.kw-tab')
        self.assertEqual(len(tabs), 3, f"应有 3 个 tab: {[t.text for t in tabs]}")
        tabs[2].click()
        time.sleep(0.25)  # [speedup]

        secs = self.driver.find_elements(By.CSS_SELECTOR, '.kw-section-title')
        self.assertEqual(len(secs), 3, f"雍正应有 3 个 section: {[s.text for s in secs]}")
        # 时间轴：默认筛选雍正 9 行（总览+8 剧情），清筛选 11 行（含康熙前史）
        next(s for s in secs if '时间轴' in s.text).click()
        time.sleep(0.4)  # [speedup]

        frame = self.driver.find_element(By.ID, 'contentFrame')
        self.driver.switch_to.frame(frame)
        rows = self.driver.find_elements(By.CSS_SELECTOR, 'tbody tr')
        self.assertEqual(len(rows), 9, f"默认应筛选雍正 9 行: {len(rows)}")
        self.assertIn('追缴国库', ' '.join(r.text for r in rows), "应含追缴欠款剧情")
        self.driver.execute_script("clearQuickFilter();")
        time.sleep(0.25)  # [speedup]

        self.assertEqual(self.driver.execute_script(
            "return document.getElementById('statTotal').textContent;"), '21',
            "清筛选后总行数应 21（清朝 12 帝 + 本剧剧情 9）")
        # 皇帝姓名 + 清庙号（第 1 页内康熙行）
        kang = next(r for r in self.driver.find_elements(By.CSS_SELECTOR, 'tbody tr')
                    if r.find_elements(By.TAG_NAME, 'td')[1].text == '康熙'
                    and '1661' in r.find_elements(By.TAG_NAME, 'td')[4].text)
        ktd = kang.find_elements(By.TAG_NAME, 'td')
        self.assertEqual(ktd[2].text, '玄烨', "康熙皇帝列应为姓名")
        self.assertEqual(ktd[3].text, '清圣祖', "康熙庙号应为清圣祖")
        self.driver.switch_to.default_content()
        # 36计策 26 行（用户梳理表：典故+剧中事件）
        next(s for s in self.driver.find_elements(By.CSS_SELECTOR, '.kw-section-title')
             if '36计策' in s.text).click()
        time.sleep(0.4)  # [speedup]

        self.driver.switch_to.frame(self.driver.find_element(By.ID, 'contentFrame'))
        heads = [th.text for th in self.driver.find_elements(By.CSS_SELECTOR, 'thead th')]
        self.assertEqual(heads,
                         ['序号', '计策名称', '分类', '衍生成语', '历史典故', '典故人物', '剧中事件', '剧中人物'],
                         f"雍正计策表头: {heads}")
        rows = self.driver.find_elements(By.CSS_SELECTOR, 'tbody tr')
        self.assertEqual(len(rows), 26, f"雍正 36计策应 26 行: {len(rows)}")
        first = rows[0].find_elements(By.TAG_NAME, 'td')
        self.assertEqual(first[1].text, '瞒天过海', "首行应为瞒天过海")
        self.assertEqual(first[3].text, '', "衍生成语与计名相同应空")
        self.assertIn('薛仁贵', first[4].text, "典故列应含典故人物")
        self.assertIn('江夏镇', first[6].text, "剧中事件应含江夏镇")
        # 非 36 计计名：分类用相近计策 + 成语保留
        sj = next(r for r in rows if r.find_elements(By.TAG_NAME, 'td')[1].text == '杀鸡儆猴')
        self.assertEqual(sj.find_elements(By.TAG_NAME, 'td')[2].find_elements(By.CSS_SELECTOR, '.cell-pill')[0].text,
                         '并战计', "杀鸡儆猴应相近于指桑骂槐（并战计）")
        self.assertEqual(sj.find_elements(By.TAG_NAME, 'td')[3].text, '杀鸡儆猴', "非 36 计成语应保留")
        self.driver.switch_to.default_content()

    def test_08b_iframe_doc_bare_mode(self):
        """iframe 内 doc 页默认隐藏 sidebar/toolbar (嵌入降级)."""
        # 中国历史 → 概述 (doc page, 非 table)
        self.driver.find_elements(By.CSS_SELECTOR, '.kw-section-title')[0].click()
        time.sleep(0.3)  # [speedup]

        frame = self.driver.find_element(By.ID, 'contentFrame')
        self.driver.switch_to.frame(frame)
        # doc page inside iframe: sidebar/toolbar hidden by default (no param)
        sidebar_disp = self.driver.execute_script(
            "var el = document.getElementById('sidebar'); return el ? getComputedStyle(el).display : 'MISSING';"
        )
        toolbar_disp = self.driver.execute_script(
            "var el = document.getElementById('topToolbar'); return el ? getComputedStyle(el).display : 'MISSING';"
        )
        self.driver.switch_to.default_content()
        self.assertEqual(sidebar_disp, 'none', f"iframe doc sidebar should be hidden, got {sidebar_disp}")
        self.assertEqual(toolbar_disp, 'none', f"iframe doc toolbar should be hidden, got {toolbar_disp}")

    # ── T7: JS errors ──

    def test_15_tab_memory_restore(self):
        """需求 3: 切页签后刷新，恢复之前查看的页签（group 单独记忆）."""
        tabs = self.driver.find_elements(By.CSS_SELECTOR, '.kw-tab')
        tabs[1].click()  # 大明王朝1566
        time.sleep(0.2)  # [speedup]

        self.driver.refresh()
        time.sleep(0.4)  # [speedup]

        active = self.driver.execute_script(
            "var a=document.querySelector('.kw-tab.active'); return a ? a.textContent : 'NONE';")
        self.assertIn('大明', active, f"刷新后应恢复大明页签: {active}")

    def test_16_url_sync_and_restore(self):
        """需求 3: 点 section 实时更新 URL（group+item）；带 URL 打开定位指定页."""
        # 中国历史 → 36计策 section
        sections = self.driver.find_elements(By.CSS_SELECTOR, '.kw-section-title')
        sections[2].click()  # 36计策
        time.sleep(0.3)  # [speedup]

        url = self.driver.execute_script("return location.href;")
        self.assertIn('group=', url, f"URL 应含 group: {url}")
        self.assertIn('item=', url, f"URL 应含 item: {url}")
        # 带 URL 重新打开 → 定位 36计策
        self.driver.get(url)
        time.sleep(0.45)  # [speedup]

        active_sec = self.driver.execute_script(
            "var a=document.querySelector('.kw-section-title.active'); return a ? a.textContent : 'NONE';")
        self.assertIn('36计策', active_sec, f"URL 打开应定位 36计策: {active_sec}")
        frame_src = self.driver.find_element(By.ID, 'contentFrame').get_attribute('src') or ''
        self.assertIn('history-strategy-table.html', frame_src, f"iframe 应为 36计策表: {frame_src}")

    def test_09_no_js_errors(self):
        """Exercise all sections → no JS errors."""
        for tab_idx in [0, 1]:
            self.driver.find_elements(By.CSS_SELECTOR, '.kw-tab')[tab_idx].click()
            time.sleep(0.15)  # [speedup]

            sections = self.driver.find_elements(By.CSS_SELECTOR, '.kw-section-title')
            for si in range(len(sections)):
                sections = self.driver.find_elements(By.CSS_SELECTOR, '.kw-section-title')
                sections[si].click()
                time.sleep(0.15)
        self.assertEqual(self._errors(), [], f"JS errors: {self._errors()}")


if __name__ == '__main__':
    unittest.main()
