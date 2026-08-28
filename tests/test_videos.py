"""Selenium test: table videos 视频列（col.type=videos）—
pill 渲染 / maxShow 折叠展开 / 点击新标签页 / 平台图标映射 / 空单元格 /
split 预览数组渲染 / 默认搜索排除 videos.
"""
import json, subprocess, sys, time, unittest
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

CHROMEDRIVER = '/Users/jadenli/CodeSpace/script-miner/cache/chromedriver/chromedriver'
PROJECT = Path(__file__).resolve().parent.parent


def error_collector(driver):
    driver.execute_script(
        "window.__testErrors = [];"
        "window.onerror = function(m) { window.__testErrors.push(String(m)); };"
    )


def get_errors(driver):
    return driver.execute_script("return window.__testErrors;")


class TestVideos(unittest.TestCase):

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

    @staticmethod
    def _videos_col(col_opts=None):
        """videos 列配置：col_opts（如 maxShow）归入 col.videos 命名空间（勿放列顶层）. """
        col = {'key': 'videos', 'label': '视频', 'type': 'videos'}
        if col_opts:
            col['videos'] = col_opts
        return col

    def _gen_page(self, videos_col=None, rows=None, title='videos 测试'):
        """用 html-gen.py table 生成临时 videos 测试页并加载（无 searchFields，默认搜索全列）.
        临时文件用唯一名（时间戳），彻底规避 Chrome file:// 缓存/旧页命中偶发."""
        stamp = str(int(time.time() * 1000))
        src = PROJECT / 'tests' / f'_tmp_videos_{stamp}.json'
        out = PROJECT / 'tests' / f'_tmp_videos_{stamp}.html'
        self._tmp_files += [src, out]
        payload = {
            'title': title,
            'columns': [
                {'key': 'name', 'label': '名称'},
                self._videos_col(videos_col),
            ],
            'data': rows or [],
        }
        with open(src, 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False)
        cmd = [sys.executable, str(PROJECT / 'html-gen.py'), 'table',
               '-d', str(src), '-o', str(out)]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            self.fail(f"html-gen.py 生成失败 ({proc.returncode}): stderr={proc.stderr!r}")
        # .data-table 是静态元素，导航后需等 #tbody tr 出现以确认 render() 已完成
        self.driver.get('file://' + str(out))
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#tbody tr')))
        error_collector(self.driver)

    def _row(self, name):
        for r in self.driver.find_elements(By.CSS_SELECTOR, 'tbody tr'):
            tds = r.find_elements(By.TAG_NAME, 'td')
            if tds and tds[0].text == name:
                return r
        return None

    def _search(self, q):
        inp = self.driver.find_element(By.ID, 'searchInput')
        inp.clear()
        if q:
            inp.send_keys(q)
        time.sleep(0.4)

    @staticmethod
    def _visible_pills(td):
        """可见 video pill（隐藏的 video-rest 内 pill 仍在 DOM，需按 is_displayed 过滤）. """
        return [p for p in td.find_elements(By.CSS_SELECTOR, '.video-pill:not(.video-more)')
                if p.is_displayed()]

    @staticmethod
    def _visible_more(td):
        return [m for m in td.find_elements(By.CSS_SELECTOR, '.video-more') if m.is_displayed()]

    # ── test_01 单元格渲染 ──

    def test_01_cell_render_pill_icon_title_duration(self):
        """videos 列渲染 pill：含平台图标/标题/时长."""
        self._gen_page(rows=[{
            'name': '巴西',
            'videos': [{'title': '巴西建国史', 'url': 'https://v.douyin.com/Y6VCrD4QQg8/',
                        'duration': '8:37', 'platform': 'douyin'}],
        }])
        row = self._row('巴西')
        self.assertIsNotNone(row, "应找到巴西行")
        td = row.find_elements(By.TAG_NAME, 'td')[1]
        pills = td.find_elements(By.CSS_SELECTOR, '.video-pill:not(.video-more)')
        self.assertEqual(len(pills), 1, "应渲染 1 个视频 pill")
        self.assertEqual(pills[0].text, '🎵 巴西建国史 (8:37)',
                         "pill 文案应为 [图标] title (duration)")

    # ── test_02 折叠 ──

    def test_02_fold_maxshow_expand(self):
        """maxShow=2 + 3 视频 → +1 标签；点击展开全部；re-render 重置折叠态."""
        self._gen_page({'maxShow': 2}, rows=[{
            'name': '多视频',
            'videos': [
                {'title': '视频一', 'url': 'https://example.com/1', 'duration': '1:00', 'platform': 'douyin'},
                {'title': '视频二', 'url': 'https://example.com/2', 'duration': '2:00', 'platform': 'bilibili'},
                {'title': '视频三', 'url': 'https://example.com/3', 'duration': '3:00', 'platform': 'youtube'},
            ],
        }])
        row = self._row('多视频')
        self.assertIsNotNone(row)
        td = row.find_elements(By.TAG_NAME, 'td')[1]
        pills = self._visible_pills(td)
        self.assertEqual(len(pills), 2, "折叠态应显示 maxShow=2 个 pill")
        more = td.find_element(By.CSS_SELECTOR, '.video-more')
        self.assertEqual(more.text, '+1', "超出部分应显示 +1 折叠标签")
        # 点击展开 → 全部显示，+N 消失
        self.driver.execute_script("arguments[0].click();", more)
        time.sleep(0.2)
        pills = self._visible_pills(td)
        self.assertEqual(len(pills), 3, "展开后应显示全部 3 个 pill")
        self.assertEqual(self._visible_more(td), [], "展开后 +N 标签应消失（不折叠回）")
        # 跨 re-render 重置为折叠态
        self._search('多视频')
        row = self._row('多视频')
        self.assertIsNotNone(row)
        td = row.find_elements(By.TAG_NAME, 'td')[1]
        pills = self._visible_pills(td)
        self.assertEqual(len(pills), 2, "re-render 后应重置为折叠态 2 个 pill")
        self.assertEqual(self._visible_more(td)[0].text, '+1')

    # ── test_03 点击新标签页 ──

    def test_03_click_opens_new_tab(self):
        """pill 点击 → window.open(url,'_blank','noopener,noreferrer')."""
        url = 'https://v.douyin.com/Y6VCrD4QQg8/'
        self._gen_page(rows=[{
            'name': '巴西',
            'videos': [{'title': '巴西建国史', 'url': url, 'duration': '8:37', 'platform': 'douyin'}],
        }])
        row = self._row('巴西')
        self.assertIsNotNone(row)
        pill = row.find_element(By.CSS_SELECTOR, '.video-pill')
        onclick = self.driver.execute_script("return arguments[0].getAttribute('onclick') || '';", pill)
        self.assertIn('window.open', onclick, "pill onclick 应 window.open")
        self.assertIn('noopener,noreferrer', onclick, "应带 noopener,noreferrer")
        # 拦截 window.open 后点击
        self.driver.execute_script(
            "window.__opened = [];"
            "window.open = function(u, name, feats) { window.__opened.push([u, name, feats]); };"
        )
        self.driver.execute_script("arguments[0].click();", pill)
        time.sleep(0.2)
        opened = self.driver.execute_script("return window.__opened;")
        self.assertEqual(len(opened), 1, f"window.open 应被调用: {opened}")
        self.assertEqual(opened[0][0], url, "应打开视频 url")
        self.assertEqual(opened[0][1], '_blank', "应新标签页打开")
        self.assertEqual(opened[0][2], 'noopener,noreferrer', "应 noopener,noreferrer")

    # ── test_04 平台图标映射 ──

    def test_04_platform_icon_mapping(self):
        """douyin→🎵 / 未知→📹 / 抖音→🎵(别名归一化) / YouTube→▶️(大小写) / bilibili→📺."""
        self._gen_page(rows=[
            {'name': '甲', 'videos': [{'title': 'T1', 'url': 'https://example.com/1', 'platform': 'douyin'}]},
            {'name': '乙', 'videos': [{'title': 'T2', 'url': 'https://example.com/2', 'platform': '其他平台'}]},
            {'name': '丙', 'videos': [{'title': 'T3', 'url': 'https://example.com/3', 'platform': '抖音'}]},
            {'name': '丁', 'videos': [{'title': 'T4', 'url': 'https://example.com/4', 'platform': 'YouTube'}]},
            {'name': '戊', 'videos': [{'title': 'T5', 'url': 'https://example.com/5', 'platform': 'bilibili'}]},
        ])
        expect = {'甲': '🎵', '乙': '📹', '丙': '🎵', '丁': '▶️', '戊': '📺'}
        for name, icon in expect.items():
            row = self._row(name)
            self.assertIsNotNone(row, f"行 {name} 应存在")
            pill = row.find_element(By.CSS_SELECTOR, '.video-pill')
            self.assertTrue(pill.text.startswith(icon),
                            f"{name}: pill 应以 {icon} 开头, 实际 {pill.text!r}")

    # ── test_05 空单元格 ──

    def test_05_empty_cell(self):
        """无 videos / videos=[] → 空单元格；有 videos 行正常渲染."""
        self._gen_page(rows=[
            {'name': '无字段'},
            {'name': '空数组', 'videos': []},
            {'name': '有视频', 'videos': [{'title': 'T', 'url': 'https://example.com/t', 'platform': 'douyin'}]},
        ])
        for name in ('无字段', '空数组'):
            row = self._row(name)
            self.assertIsNotNone(row, f"行 {name} 应存在")
            td = row.find_elements(By.TAG_NAME, 'td')[1]
            self.assertEqual(td.text, '', f"{name} 行 videos 单元格应为空, 实际: {td.text!r}")
            self.assertEqual(len(td.find_elements(By.CSS_SELECTOR, '.video-pill')), 0,
                             f"{name} 行不应有 video pill")
        row = self._row('有视频')
        self.assertIsNotNone(row)
        self.assertEqual(len(row.find_elements(By.CSS_SELECTOR, '.video-pill')), 1,
                         "有 videos 行应渲染 pill")

    # ── test_06 无 JS 错误 ──

    def test_06_no_js_errors(self):
        """videos 表加载 + 展开交互无 JS 错误."""
        self._gen_page({'maxShow': 2}, rows=[
            {'name': '甲', 'videos': [
                {'title': 'T1', 'url': 'https://example.com/1', 'duration': '1:00', 'platform': 'douyin'},
                {'title': 'T2', 'url': 'https://example.com/2', 'duration': '2:00', 'platform': 'bilibili'},
                {'title': 'T3', 'url': 'https://example.com/3', 'duration': '3:00', 'platform': 'youtube'},
            ]},
            {'name': '乙'},
        ])
        self.assertEqual(get_errors(self.driver), [], f"加载 JS 错误: {get_errors(self.driver)}")
        row = self._row('甲')
        self.assertIsNotNone(row)
        more = row.find_element(By.CSS_SELECTOR, '.video-more')
        self.driver.execute_script("arguments[0].click();", more)
        time.sleep(0.2)
        self.assertEqual(get_errors(self.driver), [], f"展开 JS 错误: {get_errors(self.driver)}")
        self.assertEqual(len(self._visible_pills(row.find_elements(By.TAG_NAME, 'td')[1])), 3,
                         "展开后应显示 3 个 pill")

    # ── test_07 split 预览 videos 渲染 ──

    def test_07_split_preview_videos(self):
        """分栏预览 videos 逐条渲染：出现视频标题文本，非 [object Object]，含可点击 url 链接."""
        self._gen_page(rows=[{
            'name': '巴西',
            'videos': [
                {'title': '每天了解一个国家，巴西', 'url': 'https://v.douyin.com/8KyFzcfoH68/',
                 'duration': '3:22', 'platform': 'douyin'},
                {'title': '巴西建国史', 'url': 'https://v.douyin.com/Y6VCrD4QQg8/',
                 'duration': '8:37', 'platform': 'douyin'},
            ],
        }])
        row = self._row('巴西')
        self.assertIsNotNone(row)
        # 点击名称列（第一可见非 actions 列默认 openSplitAt）
        self.driver.execute_script("arguments[0].click();", row.find_elements(By.TAG_NAME, 'td')[0])
        time.sleep(0.4)
        wrapper = self.driver.find_element(By.CSS_SELECTOR, '.wrapper')
        self.assertIn('split-mode', (wrapper.get_attribute('class') or '').split(),
                      "点击名称列应进入分栏预览")
        body = self.driver.find_element(By.ID, 'splitPreviewBody')
        text = body.text
        self.assertIn('每天了解一个国家，巴西', text, "分栏预览应出现视频标题文本")
        self.assertIn('巴西建国史', text, "分栏预览应出现第二条视频标题")
        self.assertNotIn('[object Object]', text, "videos 数组不应 String() 渲染为 [object Object]")
        # url 链接可点击（新标签页打开）
        links = body.find_elements(By.CSS_SELECTOR, 'a')
        onclick_all = ' '.join((l.get_attribute('onclick') or '') for l in links)
        self.assertIn('v.douyin.com', onclick_all, "应含视频 url 链接")
        self.assertIn('noopener,noreferrer', onclick_all, "url 链接应新标签页安全打开")

    # ── test_08 默认搜索排除 videos ──

    def test_08_default_search_excludes_videos(self):
        """无 searchFields 表默认搜索排除 videos：仅 title 命中的词不筛入；
        数组 String 噪音（[object Object]）不误匹配；普通字段命中正常筛出."""
        self._gen_page(rows=[{
            'name': '巴西',
            'videos': [{'title': '巴西建国史', 'url': 'https://v.douyin.com/Y6VCrD4QQg8/',
                        'platform': 'douyin'}],
        }])
        # 1) 词仅存在于 videos title → 不参与搜索，空状态
        self._search('建国史')
        rows = self.driver.find_elements(By.CSS_SELECTOR, 'tbody tr')
        self.assertEqual(len(rows), 0, "仅命中 videos title 的搜索词不应筛出任何行（videos 排除默认搜索）")
        empty = self.driver.find_element(By.ID, 'emptyState')
        self.assertTrue(empty.is_displayed(), "应显示空状态")
        # 2) 数组 String() 噪音不误匹配（HG-SEC-052）
        self._search('[object')
        rows = self.driver.find_elements(By.CSS_SELECTOR, 'tbody tr')
        self.assertEqual(len(rows), 0, "videos 数组 String 噪音不应误命中")
        # 3) 普通字段命中 → 行保留
        self._search('巴西')
        rows = self.driver.find_elements(By.CSS_SELECTOR, 'tbody tr')
        self.assertEqual(len(rows), 1, "命中普通字段应正常筛出该行")


if __name__ == '__main__':
    unittest.main()
