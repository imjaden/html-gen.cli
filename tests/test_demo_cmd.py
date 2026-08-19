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
        self.assertIn('features/hermes-profile-skills-list.html', out, "归位后路径")
        self.assertIn('templates/template-A-guide-v1.0-20260707.html', out)

    def test_02_list_json(self):
        r = run('list', '--json')
        self.assertEqual(r.returncode, 0)
        d = json.loads(r.stdout)
        self.assertEqual(d['status'], 'ok')
        self.assertGreaterEqual(len(d['data']), 40, f"应有 40+ demos: {len(d['data'])}")
        # 类型识别
        by_name = {x['name']: x['type'] for x in d['data']}
        self.assertEqual(by_name.get('drama-knowledge'), 'knowledge')
        self.assertEqual(by_name.get('history-timeline-table'), 'table')
        self.assertEqual(by_name.get('template-A-guide-v1.0-20260707'), 'doc')
        self.assertGreaterEqual(sum(1 for x in d['data'] if x.get('featured')), 9, "精选 ≥9")

    def test_03_detail(self):
        r = run('drama-knowledge')
        self.assertEqual(r.returncode, 0)
        self.assertIn('以剧读史', r.stdout)
        self.assertIn('demos/drama-knowledge.html', r.stdout)
        self.assertIn('预览:', r.stdout)

    def test_04_detail_json(self):
        r = run('history-timeline-table', '--json')
        d = json.loads(r.stdout)
        self.assertEqual(d['status'], 'ok')
        self.assertEqual(d['data']['name'], 'history-timeline-table')
        self.assertEqual(d['data']['type'], 'table')

    def test_05_not_found(self):
        r = run('no-such-demo')
        self.assertNotEqual(r.returncode, 0, "不存在 demo 应非零退出")
        self.assertIn('不存在', r.stderr)

    def test_06_registry_exists(self):
        """_registry.json 存在且条目与文件对应."""
        reg = json.loads((DEMOS / '_registry.json').read_text())
        self.assertEqual(reg['version'], 2, "registry 版本应为 2（含 referenced/stale）")
        entries = {d['entry'] for d in reg['demos']}
        htmls = {str(f.relative_to(DEMOS)).replace('\\', '/')
                 for f in DEMOS.rglob('*.html') if f.name not in ('index.html', '_registry.json')}
        self.assertEqual(entries, htmls, "registry entry 应与实际 html 文件一一对应")


if __name__ == '__main__':
    unittest.main()
