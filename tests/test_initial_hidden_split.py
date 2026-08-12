"""Selenium test: 模板新能力 — initialHidden 默认隐藏 + 分栏详情全列渲染 + pills 斜杠切分."""
import json, subprocess, tempfile, time, unittest
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

CHROMEDRIVER = '/Users/jadenli/CodeSpace/script-miner/cache/chromedriver/chromedriver'
PROJECT = Path(__file__).resolve().parent.parent

# 测试数据：含 initialHidden 列 + 斜杠 pills 列 + 全列 preview
TEST_DATA = {
    "columns": [
        {"key": "name", "label": "名称", "sortable": True, "locale": "zh", "width": "120px", "preview": True},
        {"key": "tags", "label": "标签", "type": "pills", "sortable": True, "width": "200px", "preview": True},
        {"key": "hidden_f", "label": "隐藏字段", "sortable": True, "width": "150px", "preview": True, "initialHidden": True},
        {"key": "note", "label": "备注", "sortable": True, "width": "200px", "preview": True}
    ],
    "data": [
        {"name": "样例A", "tags": "脂肪/蛋白", "hidden_f": "机密数据A", "note": "说明A"},
        {"name": "样例B", "tags": "碳水,纤维", "hidden_f": "机密数据B", "note": "说明B"}
    ],
    "options": {"pageSize": 10}
}


class TestInitialHiddenAndSplit(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # 临时生成测试页（模板新能力）
        cls.tmpdir = tempfile.TemporaryDirectory()
        data_p = Path(cls.tmpdir.name) / 'test-data.json'
        data_p.write_text(json.dumps(TEST_DATA, ensure_ascii=False), encoding='utf-8')
        out_p = Path(cls.tmpdir.name) / 'test-page.html'
        r = subprocess.run(
            ['python3', 'html-gen.py', 'table', '-d', str(data_p), '-o', str(out_p), '--title', '测试页'],
            cwd=PROJECT, capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
        cls.demo = str(out_p)

        opts = Options()
        opts.add_argument('--headless')
        opts.add_argument('--no-sandbox')
        opts.add_argument('--disable-dev-shm-usage')
        cls.driver = webdriver.Chrome(service=Service(CHROMEDRIVER), options=opts)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        cls.tmpdir.cleanup()

    def setUp(self):
        self.driver.set_window_size(1400, 900)
        self.driver.get('file://' + self.demo)
        time.sleep(0.3)
        self.driver.execute_script("localStorage.clear();")
        self.driver.get('file://' + self.demo)
        time.sleep(0.8)
        self.driver.execute_script(
            "window.__testErrors = [];"
            "window.onerror = function(m) { window.__testErrors.push(String(m)); };"
        )

    def _errors(self):
        return self.driver.execute_script("return window.__testErrors;")

    def test_01_initial_hidden_column_not_shown(self):
        # initialHidden 列不在表格显示
        ths = [th.text for th in self.driver.find_elements(By.CSS_SELECTOR, 'thead th')]
        self.assertEqual(ths, ['名称', '标签', '备注'], f"表头应 3 列（隐藏字段不显示）: {ths}")

    def test_02_split_detail_shows_all_fields(self):
        # 点击第 1 列 → 分栏详情含隐藏字段（全列渲染）
        row = self.driver.find_elements(By.CSS_SELECTOR, 'tbody tr')[0]
        row.find_elements(By.TAG_NAME, 'td')[0].click()
        time.sleep(0.4)
        body = self.driver.find_element(By.ID, 'splitPreviewBody')
        text = body.text
        self.assertIn('隐藏字段', text, "分栏详情应显示 initialHidden 列")
        self.assertIn('机密数据A', text, "分栏详情应显示隐藏字段值")

    def test_03_pills_slash_split(self):
        # 斜杠切分：脂肪/蛋白 → 2 个标签
        row = self.driver.find_elements(By.CSS_SELECTOR, 'tbody tr')[0]
        pills = row.find_elements(By.CSS_SELECTOR, '.cell-pill')
        self.assertEqual([p.text for p in pills], ['脂肪', '蛋白'], f"斜杠应切分为 2 标签: {[p.text for p in pills]}")

    def test_04_pill_click_filter(self):
        # 点击标签筛选（contains）
        row = self.driver.find_elements(By.CSS_SELECTOR, 'tbody tr')[0]
        pill = next(p for p in row.find_elements(By.CSS_SELECTOR, '.cell-pill') if p.text == '脂肪')
        self.driver.execute_script("arguments[0].click();", pill)
        time.sleep(0.4)
        fp = self.driver.find_element(By.ID, 'quickFilterPill')
        self.assertIn('脂肪', fp.text, "filter pill 应显示脂肪")
        rows = self.driver.find_elements(By.CSS_SELECTOR, 'tbody tr')
        self.assertEqual(len(rows), 1, "脂肪标签应筛出 1 行")

    def test_05_no_js_errors(self):
        self.assertEqual(self._errors(), [], f"JS 错误: {self._errors()}")


if __name__ == '__main__':
    unittest.main()
