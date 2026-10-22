"""回归测试: Markdown 行内高亮 ==文字== → <mark class="hl">（CL018 T1）。"""
import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path

GEN = Path(__file__).resolve().parent.parent / 'html-gen.py'


def load_gen():
    spec = importlib.util.spec_from_file_location('html_gen', GEN)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestInlineHighlight(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.g = load_gen()

    def test_01_basic(self):
        self.assertEqual(self.g.inline_format('前 ==高亮== 后'),
                         '前 <mark class="hl">高亮</mark> 后')

    def test_02_multi_per_line(self):
        out = self.g.inline_format('==a== 与 ==b==')
        self.assertEqual(out.count('<mark class="hl">'), 2)

    def test_03_unpaired_left_alone(self):
        self.assertEqual(self.g.inline_format('a == b'), 'a == b')

    def test_04_with_bold(self):
        out = self.g.inline_format('**粗** 与 ==亮==')
        self.assertIn('<strong>粗</strong>', out)
        self.assertIn('<mark class="hl">亮</mark>', out)


class TestDocHighlightIntegration(unittest.TestCase):

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix='_tmp_hl_'))

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_10_doc_renders_mark_and_css(self):
        md = self.tmp / 'a.md'
        md.write_text('# 标题\n\n普通 ==重点句== 结尾。\n', encoding='utf-8')
        out = self.tmp / 'a.html'
        r = subprocess.run(['python3', str(GEN), 'doc', '-i', str(md), '-o', str(out), '--quiet'],
                           capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stderr)
        html = out.read_text(encoding='utf-8')
        self.assertIn('<mark class="hl">重点句</mark>', html)
        self.assertIn('--hl-bg', html)          # CSS 变量随模板内联
        self.assertIn('mark.hl', html)

    def test_11_slide_also_supports(self):
        md = self.tmp / 's.md'
        md.write_text('# 幻灯片\n\n## 一\n\n==闪亮==\n', encoding='utf-8')
        out = self.tmp / 's.html'
        r = subprocess.run(['python3', str(GEN), 'slide', '-i', str(md), '-o', str(out), '--quiet'],
                           capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('<mark class="hl">闪亮</mark>', out.read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
