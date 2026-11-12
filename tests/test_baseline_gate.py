"""CL029 守卫: 渲染基线门禁（scripts/baseline.py）—— 未改 rc=0，改一字节 rc=1。

全部在临时副本上跑（--root），真仓零写入。
v1.1（复审返工）补：stderr 漂移提示、`--json` 错误分支形状、基线损坏 rc=3、
`--update` 在产物落后时拒绝（越权需 --force 并标 verified=false）。
"""
import importlib.util
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
SUBSET = ['layout-table.html', 'style-guide.css', 'layout-slide.html']


def _load_script():
    """把 scripts/baseline.py 当模块加载（只 import，不跑 main）。"""
    spec = importlib.util.spec_from_file_location('htmlgen_baseline_gate', SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _subset_len():
    """子集项数现取脚本里的 SUBSET（v1.2 扩容后不再写死 10 —— 两边各存一个数必然漂移）。"""
    return len(_load_script().SUBSET)


SUBSET_LEN = _subset_len()


def run(args, root=None):
    cmd = [sys.executable, str(SCRIPT)] + args
    if root:
        cmd += ['--root', str(root)]
    return subprocess.run(cmd, capture_output=True, text=True)


class TestRenderBaseline(unittest.TestCase):
    def _temp_root(self):
        """临时根：只放 3 个钉子源文件；其余子集项由 --update 记成缺项（null ⇒ 视为一致）。"""
        tmp = Path(tempfile.mkdtemp(prefix='cl029_'))
        for rel in SUBSET:
            dst = tmp / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / rel, dst)
        return tmp

    def test_01_repo_check_is_green(self):
        r = run(['--check'])
        self.assertEqual(r.returncode, 0, f'真仓基线应一致:\n{r.stdout}\n{r.stderr}')
        self.assertIn('基线一致', r.stdout)
        self.assertIn(f'{SUBSET_LEN}/{SUBSET_LEN}', r.stdout, f'子集应为 {SUBSET_LEN} 项:\n{r.stdout}')

    def test_02_one_byte_change_turns_red(self):
        tmp = self._temp_root()
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
        # v1.1: 漂移提示在 stderr —— 只断 stdout 会让「提示丢了」也绿
        self.assertIn('漂移 1/', r.stderr, f'stderr 应有漂移计数:\n{r.stderr}')
        self.assertIn('--update', r.stderr, f'stderr 应提示重基线命令:\n{r.stderr}')

    def test_03_json_shape_and_flags(self):
        tmp = self._temp_root()
        run(['--update', '--quiet'], tmp)
        r = run(['--check', '--json'], tmp)
        self.assertEqual(r.returncode, 0, r.stderr)
        data = json.loads(r.stdout)
        self.assertTrue(data['ok'])
        self.assertEqual(data['total'], SUBSET_LEN)
        self.assertEqual(data['mismatches'], [])
        (tmp / 'style-guide.css').unlink()
        r2 = run(['--check', '--json'], tmp)
        self.assertEqual(r2.returncode, 1)
        d2 = json.loads(r2.stdout)
        self.assertFalse(d2['ok'])
        self.assertEqual(d2['mismatches'][0]['path'], 'style-guide.css')
        self.assertEqual(d2['mismatches'][0]['reason'], 'missing')

    def test_04_missing_baseline_exits_2(self):
        tmp = self._temp_root()
        run(['--update', '--quiet'], tmp)
        (tmp / BASELINE_REL).unlink()
        r = run(['--check'], tmp)
        self.assertEqual(r.returncode, 2, f'无基线应 exit 2:\n{r.stdout}{r.stderr}')
        self.assertIn('未找到基线文件', r.stderr)
        # v1.1: 错误分支的 JSON 也必须带 total（否则消费方 data['total'] KeyError）
        rj = run(['--check', '--json'], tmp)
        self.assertEqual(rj.returncode, 2)
        dj = json.loads(rj.stdout)
        self.assertFalse(dj['ok'])
        self.assertEqual(dj['total'], SUBSET_LEN)
        self.assertIn('error', dj)

    def test_05_update_after_drift_restores_green(self):
        tmp = self._temp_root()
        run(['--update', '--quiet'], tmp)
        t = tmp / 'style-guide.css'
        t.write_text(t.read_text(encoding='utf-8') + '\n/* drift */\n', encoding='utf-8')
        self.assertEqual(run(['--check'], tmp).returncode, 1)
        self.assertEqual(run(['--update', '--quiet'], tmp).returncode, 0)
        self.assertEqual(run(['--check'], tmp).returncode, 0, '--update 后应恢复绿')

    # v1.1 新增 -------------------------------------------------------------
    def test_06_corrupt_baseline_exits_3_with_own_message(self):
        tmp = self._temp_root()
        run(['--update', '--quiet'], tmp)
        (tmp / BASELINE_REL).write_text('{not json', encoding='utf-8')
        r = run(['--check'], tmp)
        self.assertEqual(r.returncode, 3, f'基线损坏应 exit 3（与「无基线」分开）:\n{r.stdout}{r.stderr}')
        self.assertIn('损坏', r.stderr)
        self.assertNotIn('未找到基线文件', r.stderr, '文案不得自相矛盾')

    def test_07_update_refuses_when_products_stale(self):
        """产物落后于模板时 --update 必须拒绝（否则把漂移拍成绿）；--force 才越权且标 verified=false。"""
        tmp = self._temp_root()
        prod = tmp / 'demos' / 'countries-table.html'
        prod.parent.mkdir(parents=True, exist_ok=True)
        prod.write_text('<html><body><h1>旧产物</h1></body></html>', encoding='utf-8')
        (tmp / 'data').mkdir(exist_ok=True)
        shutil.copy2(ROOT / 'data' / '_countries-data.json', tmp / 'data' / '_countries-data.json')
        shutil.copy2(ROOT / 'html-gen.py', tmp / 'html-gen.py')
        shutil.copy2(ROOT / 'style-guide.css', tmp / 'style-guide.css')

        r = run(['--update', '--quiet'], tmp)
        self.assertEqual(r.returncode, 1, f'产物落后时 --update 应拒绝:\n{r.stdout}{r.stderr}')
        self.assertIn('落后', r.stderr)

        r2 = run(['--update', '--quiet', '--force'], tmp)
        self.assertEqual(r2.returncode, 0, f'--force 应可越权重建:\n{r2.stdout}{r2.stderr}')
        data = json.loads((tmp / BASELINE_REL).read_text(encoding='utf-8'))
        self.assertFalse(data['verified'], '--force 建的基线必须标 verified=false')

    # v1.2（CL032）新增 -----------------------------------------------------
    def test_08_every_demo_product_is_covered_or_skipped(self):
        """不得有页面悄悄落在门禁之外：既不在 build_jobs 也不在 SKIP 就是漏网。"""
        mod = _load_script()
        jobs = {rel for rel, _ in mod.build_jobs(ROOT)}
        products = {p.relative_to(ROOT).as_posix() for p in (ROOT / 'demos').glob('*.html')}
        uncovered = products - jobs - set(mod.SKIP_PRODUCTS)
        self.assertEqual(uncovered, set(), f'未进门禁的页面: {sorted(uncovered)}')
        self.assertGreaterEqual(len(jobs), 12, f'可 verify 产物应 ≥12，实得 {len(jobs)}')
        self.assertEqual(set(jobs) & set(mod.SKIP_PRODUCTS), set(), '既判定又跳过 = 口径矛盾')
        for rel, reason in mod.SKIP_PRODUCTS.items():
            self.assertTrue(reason.strip(), f'{rel} 的 skip 必须带理由（禁静默漏过）')
        # 子集必须覆盖全部可 verify 产物（--check 才能把「产物被手改」也钉住）
        self.assertTrue(jobs <= set(mod.SUBSET), f'未钉进子集的产物: {sorted(jobs - set(mod.SUBSET))}')

    def test_09_doc_and_kb_jobs_carry_their_source(self):
        """doc/kb 作业必须带单源 + 从产物回收的标题（缺标题会静默退化为默认「知识库」）。"""
        mod = _load_script()
        jobs = dict(mod.build_jobs(ROOT))
        for rel in mod.DOC_PRODUCTS:
            self.assertIn('-i', jobs[rel], f'{rel} 缺 -i 单源')
            self.assertIn(Path(rel).with_suffix('.md').as_posix(), jobs[rel],
                          f'{rel} 的 md 源应走同目录同名约定')
        for rel in mod.KB_PRODUCTS:
            self.assertIn('-d', jobs[rel], f'{rel} 缺 -d 台账')
            self.assertTrue(any(a.startswith('--title=') for a in jobs[rel]),
                            f'{rel} 的标题必须从产物回收（--title=<值> 形式）')


if __name__ == '__main__':
    unittest.main()
