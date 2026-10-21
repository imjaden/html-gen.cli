"""回归测试: 字数 / 阅读时长口径（CL017 —— 中文按汉字计，不再按空格分词）。"""
import importlib.util
import re
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


class TestWordStats(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.g = load_gen()

    def test_01_chinese_counts_by_char(self):
        # 400 汉字 → 字数 400，阅读 1 分钟（旧实现按空格分词会得到 1 个「词」）
        wc, rt = self.g._word_stats('中' * 400)
        self.assertEqual(wc, 400)
        self.assertEqual(rt, 1)

    def test_02_chinese_read_time_scales(self):
        # 3265 汉字（本仓 renxuan 第四章正文规模）→ 约 8 分钟
        wc, rt = self.g._word_stats('字' * 3265)
        self.assertEqual(wc, 3265)
        self.assertEqual(rt, 8)

    def test_03_english_still_by_word(self):
        text = ' '.join(['word'] * 1000)
        wc, rt = self.g._word_stats(text)
        self.assertEqual(wc, 1000)
        self.assertEqual(rt, 5)

    def test_04_mixed_cjk_and_latin(self):
        wc, rt = self.g._word_stats('Hello world 中文测试')
        self.assertEqual(wc, 6)          # 2 西文词 + 4 汉字
        self.assertEqual(rt, 1)          # 0.02 分钟 → 最小 1

    def test_05_latin_tokens_with_punctuation(self):
        wc, rt = self.g._word_stats("don't stop-believing alpha_beta v1.5")
        # don't / stop-believing / alpha / beta / v1 / 5 —— 撇号与连字符不拆，下划线与小数点拆
        self.assertEqual(wc, 6)
        self.assertGreaterEqual(rt, 1)


class TestDocMetaIntegration(unittest.TestCase):

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix='_tmp_wordcount_'))

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_10_doc_meta_uses_cjk_count(self):
        md = self.tmp / 'zh.md'
        md.write_text('# 标题\n\n' + ('中文' * 600) + '\n', encoding='utf-8')
        out = self.tmp / 'zh.html'
        r = subprocess.run(['python3', str(GEN), 'doc', '-i', str(md), '-o', str(out), '--quiet'],
                           capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stderr)
        html = out.read_text(encoding='utf-8')
        m = re.search(r'字数: ([\d,]+) · 阅读约 (\d+) 分钟', html)
        self.assertIsNotNone(m, '未找到字数/阅读时长 meta')
        wc = int(m.group(1).replace(',', ''))
        rt = int(m.group(2))
        self.assertEqual(wc, 2 + 1200)   # 标题 2 字 + 正文 1200 字
        self.assertEqual(rt, 3)          # 1202 / 400 → 3

    def test_11_slide_meta_uses_cjk_count(self):
        md = self.tmp / 'slides.md'
        md.write_text('# 幻灯片\n\n## 一\n\n' + ('讲' * 800) + '\n', encoding='utf-8')
        out = self.tmp / 'slides.html'
        r = subprocess.run(['python3', str(GEN), 'slide', '-i', str(md), '-o', str(out), '--quiet'],
                           capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stderr)
        html = out.read_text(encoding='utf-8')
        m = re.search(r'字数: ([\d,]+) · 阅读约 (\d+) 分钟', html)
        self.assertIsNotNone(m, '未找到字数/阅读时长 meta')
        wc = int(m.group(1).replace(',', ''))
        self.assertEqual(wc, 3 + 1 + 800)   # 幻灯片 3 + 一 1 + 正文 800
        self.assertEqual(int(m.group(2)), 2)


if __name__ == '__main__':
    unittest.main()
