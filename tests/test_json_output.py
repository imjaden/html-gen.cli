"""回归测试: table/knowledge JSON 顶层 output 字段 (HTML-GEN-CL003) — CLI -o > JSON output > 中断(exit 1)."""
import json, os, shutil, subprocess, tempfile, unittest
from pathlib import Path

GEN = Path(__file__).resolve().parent.parent / 'html-gen.py'


def run(*args, cwd=None):
    return subprocess.run(['python3', str(GEN), *args],
                          capture_output=True, text=True, timeout=60, cwd=cwd)


def write_json(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False), encoding='utf-8')


class TestJsonOutput(unittest.TestCase):
    """纯 CLI 行为断言 (subprocess), 每用例独立临时目录 (pytest-xdist 隔离)."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix='_tmp_json_output_'))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    # ── table 三态 ──
    def test_01_cli_o_overrides_json_output(self):
        """CLI -o 覆盖 JSON output: 指定 CLI 路径生成, JSON output 路径不生成."""
        json_out = self.tmp / 'json-out.html'
        cli_out = self.tmp / 'cli-out.html'
        data = self.tmp / 'data.json'
        write_json(data, {'output': str(json_out), 'data': [{'a': 1}]})
        r = run('table', '-d', str(data), '-o', str(cli_out))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(cli_out.exists())
        self.assertFalse(json_out.exists())

    def test_02_json_output_effective(self):
        """无 CLI -o + JSON output 生效: 生成到 JSON output 路径, 文件含标题."""
        json_out = self.tmp / 'json-out.html'
        data = self.tmp / 'data.json'
        write_json(data, {'title': 'CL003 标题', 'output': str(json_out), 'data': [{'a': 1}]})
        r = run('table', '-d', str(data))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(json_out.exists())
        self.assertIn('CL003 标题', json_out.read_text(encoding='utf-8'))

    def test_03_neither_exit1(self):
        """两者皆无: exit 1 + stderr 含提示文案."""
        data = self.tmp / 'data.json'
        write_json(data, {'data': [{'a': 1}]})
        r = run('table', '-d', str(data))
        self.assertEqual(r.returncode, 1)
        self.assertIn('未指定输出文件', r.stderr)
        self.assertEqual(r.stdout, '')

    def test_04_json_output_empty_string(self):
        """JSON output 空串: 视为未提供 → exit 1."""
        data = self.tmp / 'data.json'
        write_json(data, {'output': '', 'data': [{'a': 1}]})
        r = run('table', '-d', str(data))
        self.assertEqual(r.returncode, 1)
        self.assertIn('未指定输出文件', r.stderr)

    def test_05_cli_o_empty_string(self):
        """CLI -o 空串: 视为未传 → JSON output 生效."""
        json_out = self.tmp / 'json-out.html'
        data = self.tmp / 'data.json'
        write_json(data, {'output': str(json_out), 'data': [{'a': 1}]})
        r = run('table', '-d', str(data), '-o', '')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(json_out.exists())

    def test_06_quiet_still_errors(self):
        """--quiet + 两者皆无: exit 1, stderr 仍打印错误 (错误不静默)."""
        data = self.tmp / 'data.json'
        write_json(data, {'data': [{'a': 1}]})
        r = run('table', '-d', str(data), '--quiet')
        self.assertEqual(r.returncode, 1)
        self.assertIn('未指定输出文件', r.stderr)

    # ── knowledge 三态 ──
    def test_07_knowledge_three_state(self):
        """knowledge: CLI 覆盖 / JSON 生效 / 皆无中断."""
        kb_items = [{'title': 'A', 'group': 'G'}]
        # CLI 覆盖
        json_out = self.tmp / 'kb-json.html'
        cli_out = self.tmp / 'kb-cli.html'
        data = self.tmp / 'kb.json'
        write_json(data, {'output': str(json_out), 'items': kb_items})
        r = run('knowledge', '-d', str(data), '-o', str(cli_out))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(cli_out.exists())
        self.assertFalse(json_out.exists())
        # JSON 生效
        r = run('knowledge', '-d', str(data))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(json_out.exists())
        # 皆无中断
        data2 = self.tmp / 'kb2.json'
        write_json(data2, {'items': kb_items})
        r = run('knowledge', '-d', str(data2))
        self.assertEqual(r.returncode, 1)
        self.assertIn('未指定输出文件', r.stderr)

    def test_08_knowledge_groups_plus_data_output(self):
        """knowledge -g groups.json + data 带 output → 用 data 的 output (决策 7)."""
        kb_out = self.tmp / 'kb-out.html'
        groups = self.tmp / 'groups.json'
        data = self.tmp / 'kb.json'
        write_json(groups, [{'key': 'G', 'label': 'G'}])
        write_json(data, {'output': str(kb_out), 'items': [{'title': 'A', 'group': 'G'}]})
        r = run('knowledge', '-d', str(data), '-g', str(groups))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(kb_out.exists())

    def test_09_knowledge_groups_output_ignored(self):
        """knowledge groups 带 output (data 无) → 被忽略 → 中断."""
        groups = self.tmp / 'groups.json'
        data = self.tmp / 'kb.json'
        write_json(groups, [{'key': 'G', 'label': 'G', 'output': str(self.tmp / 'g-out.html')}])
        write_json(data, {'items': [{'title': 'A', 'group': 'G'}]})
        r = run('knowledge', '-d', str(data), '-g', str(groups))
        self.assertEqual(r.returncode, 1)
        self.assertIn('未指定输出文件', r.stderr)

    # ── favicon 三态 (CL004: 默认注入 / --favicon 覆盖 / 空串禁用) ──
    DEFAULT_FAVICON = 'https://www.jaden.tech/static/img/favicon.png'

    def render_table(self, data, *args):
        out = self.tmp / 'favicon-out.html'
        doc = {'title': 'favicon 测试', 'output': str(out), 'data': data}
        write_json(self.tmp / 'data.json', doc)
        r = run('table', '-d', str(self.tmp / 'data.json'), *args)
        self.assertEqual(r.returncode, 0, r.stderr)
        return out.read_text(encoding='utf-8')

    def test_12_favicon_default_injected(self):
        """默认注入 DEFAULT_FAVICON: <link rel="icon" href=默认> 存在于 head."""
        html = self.render_table([{'a': 1}])
        self.assertIn(f'rel="icon" href="{self.DEFAULT_FAVICON}"', html)

    def test_13_favicon_override(self):
        """--favicon 覆盖默认: 注入指定 URL, 不含默认 URL."""
        custom = 'https://example.com/custom.ico'
        html = self.render_table([{'a': 1}], '--favicon', custom)
        self.assertIn(f'rel="icon" href="{custom}"', html)
        self.assertNotIn(self.DEFAULT_FAVICON, html)

    def test_14_favicon_empty_disables(self):
        """--favicon "" 显式禁用: 无任何 rel="icon" link (HG-SEC-073)."""
        html = self.render_table([{'a': 1}], '--favicon', '')
        self.assertNotIn('rel="icon"', html)

    # ── 边界 ──
    def test_10_plain_array_no_o(self):
        """简单数组无 -o: exit 1 (CLI-only 语义)."""
        data = self.tmp / 'arr.json'
        write_json(data, [{'a': 1}])
        r = run('table', '-d', str(data))
        self.assertEqual(r.returncode, 1)
        self.assertIn('未指定输出文件', r.stderr)

    def test_11_doc_slide_unaffected(self):
        """doc/slide 不受影响: 无 -o 时 md 派生默认照常生成."""
        md = self.tmp / 'note.md'
        md.write_text('# 标题\n\n## 章节\n内容\n', encoding='utf-8')
        r = run('doc', '-i', str(md))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((self.tmp / 'note.html').exists())
        r = run('slide', '-i', str(md))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((self.tmp / 'note.slide.html').exists())


if __name__ == '__main__':
    unittest.main()
