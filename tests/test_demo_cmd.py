"""回归测试: html-gen demo 子命令 (list/<name>/--json/--open 检测)."""
import json, subprocess, unittest
from pathlib import Path

GEN = Path(__file__).resolve().parent.parent / 'html-gen.py'
DEMOS = Path(__file__).resolve().parent.parent / 'demos'


def run(*args):
    return subprocess.run(['python3', str(GEN), 'demo', *args],
                          capture_output=True, text=True, timeout=60)


class TestDemoCmd(unittest.TestCase):

    def test_01_list_columns(self):
        """demo list 输出 5 列信息（name/title/type/entry/featured 标记）."""
        r = run('list')
        self.assertEqual(r.returncode, 0, r.stderr)
        out = r.stdout
        self.assertIn('共', out)
        self.assertIn('★', out, "应有精选标记")
        self.assertIn('drama-knowledge', out)
        self.assertIn('hermes-profile-skills-list.html', out, "归位后路径")
        self.assertIn('table-guide.html', out)

    def test_02_list_json(self):
        r = run('list', '--json')
        self.assertEqual(r.returncode, 0)
        d = json.loads(r.stdout)
        self.assertEqual(d['status'], 'ok')
        self.assertGreaterEqual(len(d['data']), 40, f"应有 40+ demos: {len(d['data'])}")
        # 类型识别
        by_name = {x['name']: x['type'] for x in d['data']}
        self.assertEqual(by_name.get('drama-knowledge'), 'knowledge')
        self.assertEqual(by_name.get('drama-history-timeline-table'), 'table')
        self.assertEqual(by_name.get('table-guide'), 'doc')
        self.assertGreaterEqual(sum(1 for x in d['data'] if x.get('featured')), 9, "精选 ≥9")

    def test_03_detail(self):
        r = run('drama-knowledge')
        self.assertEqual(r.returncode, 0)
        self.assertIn('以剧读史', r.stdout)
        self.assertIn('demos/drama-knowledge.html', r.stdout)
        self.assertIn('预览:', r.stdout)

    def test_04_detail_json(self):
        r = run('drama-history-timeline-table', '--json')
        d = json.loads(r.stdout)
        self.assertEqual(d['status'], 'ok')
        self.assertEqual(d['data']['name'], 'drama-history-timeline-table')
        self.assertEqual(d['data']['type'], 'table')

    def test_05_not_found(self):
        r = run('no-such-demo')
        self.assertNotEqual(r.returncode, 0, "不存在 demo 应非零退出")
        self.assertIn('不存在', r.stderr)

    def test_07_help_covers_prompt_demo(self):
        """help 总览与主题应覆盖 prompt/demo 指令."""
        r = subprocess.run(['python3', str(GEN), 'help'], capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0)
        self.assertIn('prompt', r.stdout, "help 总览应含 prompt")
        self.assertIn('demo', r.stdout, "help 总览应含 demo")
        for topic in ('prompt', 'demo'):
            r2 = subprocess.run(['python3', str(GEN), 'help', topic],
                                capture_output=True, text=True, timeout=60)
            self.assertEqual(r2.returncode, 0, f"help {topic} 失败")
            self.assertIn('用法', r2.stdout, f"help {topic} 应含用法")
        r3 = subprocess.run(['python3', str(GEN), 'help', 'nope'], capture_output=True, text=True, timeout=60)
        self.assertNotEqual(r3.returncode, 0, "不存在的主题应报错")

    def test_08_rebuild_idempotent(self):
        """demo --rebuild 幂等重建 registry（featured 来自 index.html 链接）."""
        r = run('--rebuild')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('registry 重建', r.stdout)
        reg = json.loads((DEMOS / '_registry.json').read_text())
        self.assertEqual(reg['version'], 3)
        self.assertGreaterEqual(sum(1 for d in reg['demos'] if d['featured']), 9, "featured ≥9")
        # 幂等
        r2 = run('--rebuild')
        self.assertEqual(json.loads((DEMOS / '_registry.json').read_text()), reg,
                         "重建应幂等")

    def test_10_demo_error_json_envelope(self):
        """demo <不存在> --json 应输出 checkpoint 错误信封（对齐 prompt）."""
        r = run('no-such-demo', '--json')
        self.assertEqual(r.returncode, 1)
        d = json.loads(r.stdout)
        self.assertEqual(d['status'], 'error')
        self.assertIsNone(d['data'])
        self.assertIn('no-such-demo', d['error'])
        self.assertEqual(r.stderr, '', "错误应走信封，不污染 stderr")

    def test_11_version_flag(self):
        """--version 输出版本号 (CL016: 与 version 子指令同格式)."""
        r = subprocess.run(['python3', str(GEN), '--version'],
                           capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0)
        self.assertIn('html-gen v3.2 (2026-08-28)', r.stdout, f"版本号: {r.stdout}")

    def test_09_registry_exists(self):
        """_registry.json 存在且条目与文件对应."""
        reg = json.loads((DEMOS / '_registry.json').read_text())
        self.assertEqual(reg['version'], 3, "registry 版本应为 3（name 唯一化）")
        entries = {d['entry'] for d in reg['demos']}
        htmls = {str(f.relative_to(DEMOS)).replace('\\', '/')
                 for f in DEMOS.rglob('*.html') if f.name not in ('index.html', '_registry.json')}
        self.assertEqual(entries, htmls, "registry entry 应与实际 html 文件一一对应")


if __name__ == '__main__':
    unittest.main()
