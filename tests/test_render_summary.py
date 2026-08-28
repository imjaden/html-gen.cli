"""回归测试: 渲染完成统计信息 (源/产物大小, 耗时, 模板统计行, --quiet)."""
import json, subprocess, unittest
from pathlib import Path

GEN = Path(__file__).resolve().parent.parent / 'html-gen.py'
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data'
TMP = Path(__file__).resolve().parent / '_tmp_render_summary'


def run(*args):
    return subprocess.run(['python3', str(GEN), *args],
                          capture_output=True, text=True, timeout=60)


def setUpModule():
    TMP.mkdir(exist_ok=True)


def tearDownModule():
    import shutil
    shutil.rmtree(TMP, ignore_errors=True)


class TestRenderSummary(unittest.TestCase):
    """4 模板默认输出统计信息卡; --quiet 仅打印路径."""

    def _assert_summary(self, stdout, marker):
        self.assertIn("✅ 已生成:", stdout)
        self.assertIn("📄 源文件:", stdout)
        self.assertIn("📦 产物:", stdout)
        self.assertIn("⏱ 耗时:", stdout)
        self.assertIn(marker, stdout)

    def test_01_table_summary(self):
        """table: 行数 × 列数 + 标签页数."""
        data = self._table_data()
        out = TMP / 't_table.html'
        r = run('table', '-d', str(data), '-o', str(out))
        self.assertEqual(r.returncode, 0, r.stderr)
        self._assert_summary(r.stdout, '📊 数据: 5 行 × 3 列 · 2 标签页')

    def _table_data(self):
        """自包含 table JSON（不依赖 data/ 下的易变数据源）."""
        data = TMP / 't_table.json'
        data.write_text(json.dumps({
            'title': '测试表',
            'columns': [{'key': 'a', 'label': 'A'}, {'key': 'b', 'label': 'B'}, {'key': 'c', 'label': 'C'}],
            'data': [{'a': str(i), 'b': str(i * 2), 'c': str(i * 3)} for i in range(5)],
            'tabs': [{'key': 'x', 'label': 'X'}, {'key': 'y', 'label': 'Y'}],
        }, ensure_ascii=False), encoding='utf-8')
        return data

    def test_02_doc_summary(self):
        """doc: h2 章节数 + h3 子节数."""
        md = TMP / 't_doc.md'
        md.write_text('# 标题\n\n## 第一节\n内容\n\n### 子节\n内容\n\n## 第二节\n内容\n', encoding='utf-8')
        out = TMP / 't_doc.html'
        r = run('doc', '-i', str(md), '-o', str(out))
        self.assertEqual(r.returncode, 0, r.stderr)
        self._assert_summary(r.stdout, '📑 章节: 2 节 · 1 子节')

    def test_03_slide_summary(self):
        """slide: h2 分页数 + 封面页."""
        md = TMP / 't_slide.md'
        md.write_text('# 封面\n\n## 页一\n内容\n\n## 页二\n内容\n', encoding='utf-8')
        out = TMP / 't_slide.html'
        r = run('slide', '-i', str(md), '-o', str(out))
        self.assertEqual(r.returncode, 0, r.stderr)
        self._assert_summary(r.stdout, '🖥 页面: 3 页')

    def test_04_knowledge_summary(self):
        """knowledge: 类目(顶部) + 章节(侧栏) + 条目数."""
        data = TMP / 't_kb.json'
        data.write_text(json.dumps([
            {'title': 'A', 'group': 'G1', 'section': 'S1', 'desc': '<p>a</p>'},
            {'title': 'B', 'group': 'G1', 'section': 'S1', 'desc': '<p>b</p>'},
            {'title': 'C', 'group': 'G2', 'section': 'S2', 'desc': '<p>c</p>'},
            {'title': 'D', 'group': 'G2', 'desc': '<p>d</p>'},
        ], ensure_ascii=False), encoding='utf-8')
        out = TMP / 't_kb.html'
        r = run('knowledge', '-d', str(data), '-o', str(out))
        self.assertEqual(r.returncode, 0, r.stderr)
        self._assert_summary(r.stdout, '🏷 类目 2 · 章节 2 · 条目 4')

    def test_05_quiet_before_subcommand(self):
        """--quiet 在子命令前: 仅打印 ✅ 已生成."""
        out = TMP / 'tq1.html'
        r = run('--quiet', 'table', '-d', str(self._table_data()), '-o', str(out))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn(f"✅ 已生成: {out}", r.stdout)
        self.assertNotIn('📄 源文件:', r.stdout)
        self.assertNotIn('📊 数据:', r.stdout)

    def test_06_quiet_after_subcommand(self):
        """--quiet 在子命令后同样生效."""
        out = TMP / 'tq2.html'
        r = run('table', '--quiet', '-d', str(self._table_data()), '-o', str(out))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn(f"✅ 已生成: {out}", r.stdout)
        self.assertNotIn('📄 源文件:', r.stdout)

    def test_07_human_size(self):
        """human_size: <1KB 显示 B, ≥1KB 显示 KB 1 位小数."""
        from importlib.util import spec_from_file_location, module_from_spec
        spec = spec_from_file_location('html_gen', GEN)
        assert spec is not None and spec.loader is not None
        mod = module_from_spec(spec)
        spec.loader.exec_module(mod)
        self.assertEqual(mod.human_size(512), '512 B')
        self.assertEqual(mod.human_size(131072), '128.0 KB')


if __name__ == '__main__':
    unittest.main()
