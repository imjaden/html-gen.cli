"""CL029 守卫: 渲染基线门禁（scripts/baseline.py）—— 未改 rc=0，改一字节 rc=1。

全部在临时副本上跑（--root），真仓零写入。
"""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / 'scripts' / 'baseline.py'
BASELINE_REL = 'data/_render-baseline.json'
SUBSET = ['layout-table.html', 'style-guide.css', 'demos/demos-index.html']


def run(args, root=None):
    cmd = [sys.executable, str(SCRIPT)] + args
    if root:
        cmd += ['--root', str(root)]
    return subprocess.run(cmd, capture_output=True, text=True)


class TestRenderBaseline(unittest.TestCase):
    def _temp_root(self):
        tmp = Path(tempfile.mkdtemp(prefix='cl029_'))
        base = json.loads((ROOT / BASELINE_REL).read_text(encoding='utf-8'))
        for rel in SUBSET:
            dst = tmp / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / rel, dst)
        # 基线只保留子集里的条目，避免临时根缺文件导致 not-in-baseline
        sub = {'version': base['version'], 'generated': base['generated'],
               'note': base['note'],
               'files': {k: v for k, v in base['files'].items() if k in SUBSET}}
        (tmp / BASELINE_REL).parent.mkdir(parents=True, exist_ok=True)
        (tmp / BASELINE_REL).write_text(json.dumps(sub, ensure_ascii=False, indent=2), encoding='utf-8')
        return tmp, sub

    def test_01_repo_check_is_green(self):
        r = run(['--check'])
        self.assertEqual(r.returncode, 0, f'真仓基线应一致:\n{r.stdout}\n{r.stderr}')
        self.assertIn('基线一致', r.stdout)
        self.assertIn('9/9', r.stdout)

    def test_02_one_byte_change_turns_red(self):
        tmp, sub = self._temp_root()
        # 临时根的基线只含 3 个文件 ⇒ 但脚本 SUBSET 是固定 9 个，其余应为 not-in-baseline/缺失
        # ⇒ 用 --update 先让临时根自洽，再改一个字节
        r0 = run(['--update', '--quiet'], tmp)
        self.assertEqual(r0.returncode, 0, r0.stderr)
        self.assertEqual(run(['--check'], tmp).returncode, 0, '临时根重建基线后应绿')

        target = tmp / 'layout-table.html'
        target.write_text(target.read_text(encoding='utf-8') + '\n<!-- drift -->\n', encoding='utf-8')
        r = run(['--check'], tmp)
        self.assertEqual(r.returncode, 1, f'改一字节必须红:\n{r.stdout}')
        self.assertIn('layout-table.html', r.stdout)
        self.assertIn('changed', r.stdout)
        # 其它文件仍绿（只报漂移项，不连坐）
        self.assertEqual(r.stdout.count('❌'), 1, f'应只报一个漂移项:\n{r.stdout}')

    def test_03_json_shape_and_flags(self):
        tmp, _ = self._temp_root()
        run(['--update', '--quiet'], tmp)
        r = run(['--check', '--json'], tmp)
        self.assertEqual(r.returncode, 0, r.stderr)
        data = json.loads(r.stdout)
        self.assertTrue(data['ok'])
        self.assertEqual(data['total'], 9)
        self.assertEqual(data['mismatches'], [])
        (tmp / 'style-guide.css').unlink()
        r2 = run(['--check', '--json'], tmp)
        self.assertEqual(r2.returncode, 1)
        d2 = json.loads(r2.stdout)
        self.assertFalse(d2['ok'])
        self.assertEqual(d2['mismatches'][0]['path'], 'style-guide.css')
        self.assertEqual(d2['mismatches'][0]['reason'], 'missing')

    def test_04_missing_baseline_exits_2(self):
        tmp, _ = self._temp_root()
        (tmp / BASELINE_REL).unlink()
        r = run(['--check'], tmp)
        self.assertEqual(r.returncode, 2, f'无基线应 exit 2:\n{r.stdout}{r.stderr}')
        self.assertIn('未找到基线文件', r.stderr)

    def test_05_update_after_drift_restores_green(self):
        tmp, _ = self._temp_root()
        run(['--update', '--quiet'], tmp)
        t = tmp / 'style-guide.css'
        t.write_text(t.read_text(encoding='utf-8') + '\n/* drift */\n', encoding='utf-8')
        self.assertEqual(run(['--check'], tmp).returncode, 1)
        self.assertEqual(run(['--update', '--quiet'], tmp).returncode, 0)
        self.assertEqual(run(['--check'], tmp).returncode, 0, '--update 后应恢复绿')


if __name__ == '__main__':
    unittest.main()
