"""CL029 守卫: 渲染基线门禁（scripts/baseline.py）—— 未改 rc=0，改一字节 rc=1。

全部在临时副本上跑（--root），真仓零写入。
v1.1（复审返工）补：stderr 漂移提示、`--json` 错误分支形状、基线损坏 rc=3、
`--update` 在产物落后时拒绝（越权需 --force 并标 verified=false）。
"""
import importlib.util
import json
import os
import re
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
        """不得有页面悄悄落在门禁之外：既不在 build_jobs 也不在 SKIP 就是漏网。

        CL032 尾项起扫描面从 `demos/*.html` 扩到 `demos/**/*.html`（含 case 子目录）：
        子目录页此前 100% 无覆盖，正是「改了没说」最难发现的盲区。
        """
        mod = _load_script()
        jobs = {rel for rel, _ in mod.build_jobs(ROOT)}
        skip = set(mod.SKIP_PRODUCTS) | {rel for rel, _ in mod.case_skip_files(ROOT, jobs)}
        products = {p.relative_to(ROOT).as_posix() for p in (ROOT / 'demos').rglob('*.html')}
        uncovered = products - jobs - skip
        self.assertEqual(uncovered, set(), f'未进门禁的页面: {sorted(uncovered)}')
        self.assertGreaterEqual(len(jobs), 30, f'可 verify 产物应 ≥30，实得 {len(jobs)}')
        self.assertEqual(jobs & (skip | set(mod.SKIP_PRODUCTS)), set(), '既判定又跳过 = 口径矛盾')
        for rel, reason in {**mod.SKIP_PRODUCTS, **mod.CASE_SKIP}.items():
            self.assertTrue(reason.strip(), f'{rel} 的 skip 必须带理由（禁静默漏过）')
        # 子集必须覆盖全部可 verify 产物（--check 才能把「产物被手改」也钉住）
        self.assertTrue(jobs <= set(mod.SUBSET), f'未钉进子集的产物: {sorted(jobs - set(mod.SUBSET))}')
        # 文档数字与实现绑死（HG-SEC-256 第二次复发的守卫：改口径忘了改文档就红）
        doc = (ROOT / 'documents/testing.md').read_text(encoding='utf-8')
        self.assertIn(f'**{len(jobs)} 个可 verify 产物**', doc,
                      f'testing.md 的「可 verify 产物」数应等于 build_jobs 实际 {len(jobs)} 件')
        self.assertIn(f'= **{len(mod.SUBSET)} 项**', doc,
                      f'testing.md 的子集项数应等于 SUBSET 实际 {len(mod.SUBSET)} 项')
        # HG-SEC-265：文件数与用例数也要绑死（此前只有「N 件 / N 项」被绑）
        tests_dir = ROOT / 'tests'
        n_files = len(list(tests_dir.glob('test_*.py')))
        self.assertIn(f'{n_files} 文件', doc,
                      f'testing.md 的「N 文件」应等于 tests/test_*.py 实际 {n_files} 个')
        gate_src = (tests_dir / 'test_baseline_gate.py').read_text(encoding='utf-8')
        n_gate = len(re.findall(r'^    def test_\w+\(', gate_src, re.M))
        self.assertIn(f'test_baseline_gate.py` {n_gate} 例', doc,
                      f'testing.md 应写 test_baseline_gate.py 实有 {n_gate} 例')
        # subtests 只能实跑才数得出 ⇒ 退一步守「两处同数」（AGENTS.md 是权威、testing.md 复述）
        agents = (ROOT / 'AGENTS.md').read_text(encoding='utf-8')
        self.assertIn(f'{n_files} 文件', agents, f'AGENTS.md 的文件数也应为 {n_files}')
        sub_doc = re.search(r'共 (\d+) subtests', doc)
        sub_agents = re.search(r'含 (\d+) subtests', agents)
        self.assertTrue(sub_doc and sub_agents, '两处都应写 subtests 数量')
        self.assertEqual(sub_doc.group(1), sub_agents.group(1),
                         'testing.md 与 AGENTS.md 的 subtests 数必须同值（改一处忘改另一处即红）')

    # v1.3（CL040）新增 -----------------------------------------------------
    def test_10_param_regression_blocks_update_and_sticks(self):
        """HG-SEC-249/250：漏参重建 ⇒ --update 拒；--force 后普通 --update 也拒（二次洗白封堵）。

        判别性前提写死在用例里：第 3 步 --verify 必须 rc=0 —— 参数回归之所以能被抓到，
        全靠基线里的存在性钉子（--verify 的参数从产物自己回收，漏参后它永远绿）。
        """
        tmp = Path(tempfile.mkdtemp(prefix='cl040_'))
        self.addCleanup(shutil.rmtree, tmp, True)
        for rel in SUBSET:                                   # 快照全家
            if (ROOT / rel).is_file():
                (tmp / rel).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / rel, tmp / rel)
        for rel in ('html-gen.py', 'style-guide.css'):
            shutil.copy2(ROOT / rel, tmp / rel)
        for tpl in ROOT.glob('layout-*.html'):
            shutil.copy2(tpl, tmp / tpl.name)
        (tmp / 'data').mkdir(exist_ok=True)
        shutil.copy2(ROOT / 'data' / '_countries-data.json', tmp / 'data' / '_countries-data.json')

        prod = tmp / 'demos' / 'countries-table.html'
        prod.parent.mkdir(parents=True, exist_ok=True)

        def render(with_corner):
            cmd = [sys.executable, 'html-gen.py', 'table', '-d', 'data/_countries-data.json',
                   '-o', 'demos/countries-table.html', '--title', '全球国家速查表', '--quiet']
            if with_corner:
                cmd.append('--github-url=https://github.com/imjaden/html-gen.cli')
            r = subprocess.run(cmd, cwd=str(tmp), capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, f'渲染失败:\n{r.stderr}')

        # 1) 带 --github-url 建基线：钉子 corner=True、verified=True
        render(True)
        r = run(['--update', '--quiet'], tmp)
        self.assertEqual(r.returncode, 0, f'首次建基线应成功:\n{r.stdout}{r.stderr}')
        base = json.loads((tmp / BASELINE_REL).read_text(encoding='utf-8'))
        self.assertTrue(base['files']['demos/countries-table.html']['corner'])
        self.assertTrue(base['verified'], 'verify 绿 + 无 drops ⇒ verified 必须为 True')
        sha_before = (tmp / BASELINE_REL).read_bytes()

        # 2) 漏参重渲（产物字节变了，但仍是当前模板产物）
        render(False)

        # 2b) HG-SEC-261/266：--check --json 必须带 verified（越权态对机器可见）；
        #     同一产物「内容变了 + 参数丢了」只算 1 项漂移，判据条数另计。
        r = run(['--check', '--json'], tmp)
        self.assertEqual(r.returncode, 1, f'产物已变 ⇒ --check 应 rc=1:\n{r.stdout}{r.stderr}')
        rep = json.loads(r.stdout)
        self.assertTrue(rep.get('verified'), '该基线是正常建立的，JSON 里 verified 应为 true')
        self.assertEqual(rep.get('drifted'), 1, f'同一产物多条判据只算 1 项: {rep}')
        self.assertGreater(len(rep['mismatches']), 1, '判据条数仍要逐条可见（changed + param-lost）')

        # 3) ★ 前提：verify 仍然绿（参数从产物回收）
        r = run(['--verify', '--quiet'], tmp)
        self.assertEqual(r.returncode, 0,
                         f'漏参后 --verify 仍应绿（这正是钉子存在的理由）:\n{r.stdout}{r.stderr}')

        # 4) 普通 --update 被拒，且基线文件逐字节未动
        r = run(['--update', '--quiet'], tmp)
        self.assertEqual(r.returncode, 1, f'参数回归时 --update 必须拒绝:\n{r.stdout}{r.stderr}')
        self.assertIn('基线有 corner', r.stderr)
        self.assertEqual((tmp / BASELINE_REL).read_bytes(), sha_before, '拒绝路径不得写盘')

        # 5) --force 越权：写入 corner=False 且 verified=False（verify 绿也不算数）
        r = run(['--update', '--quiet', '--force'], tmp)
        self.assertEqual(r.returncode, 0, f'--force 应可越权重建:\n{r.stdout}{r.stderr}')
        base = json.loads((tmp / BASELINE_REL).read_text(encoding='utf-8'))
        self.assertFalse(base['files']['demos/countries-table.html']['corner'])
        self.assertFalse(base['verified'], '有参数回归时 --force 不得写 verified=true')

        # 6) ★ HG-SEC-249 回归：越权建立后，普通 --update 一律拒（否则一次 force 就洗白）
        r = run(['--update', '--quiet'], tmp)
        self.assertEqual(r.returncode, 1, f'verified=false 的基线不接受普通 --update:\n{r.stdout}{r.stderr}')
        self.assertIn('越权建立', r.stderr)
        base = json.loads((tmp / BASELINE_REL).read_text(encoding='utf-8'))
        self.assertFalse(base['verified'], '拒绝路径不得把 verified 翻回 true')
        self.assertFalse(base['files']['demos/countries-table.html']['corner'])

        # 7) --check 仍绿（钉子一致），但必须留痕
        r = run(['--check'], tmp)
        self.assertEqual(r.returncode, 0, f'一致时 --check 应 rc=0:\n{r.stdout}{r.stderr}')
        self.assertIn('⚠️', r.stderr)
        self.assertIn('verified=false', r.stderr)

        # 8) 终止性：第二次显式 --force 才恢复常态（verify 绿 + 无 drops ⇒ verified=True）。
        #    若把 verified 写回 `not force`，这里恒为 False ⇒ 一次越权就永久 false（死锁）。
        r = run(['--update', '--quiet', '--force'], tmp)
        self.assertEqual(r.returncode, 0, f'第二次 --force 应成功:\n{r.stdout}{r.stderr}')
        base = json.loads((tmp / BASELINE_REL).read_text(encoding='utf-8'))
        self.assertTrue(base['verified'], 'verify 绿且无参数回归 ⇒ verified 必须回到 True')

        # 9) HG-SEC-263：help 文案不得与第 8 步相反（旧文案「不会写 verified=true」自相矛盾）
        h = run(['--help'])
        self.assertEqual(h.returncode, 0, h.stderr)
        self.assertIn('仍跑 verify', h.stdout)
        self.assertNotIn('不会写 verified=true', h.stdout, '--force 可以写回 true（第 8 步），文案不得否认')

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


class TestDocsIndexGate(unittest.TestCase):
    """文档清单门禁（HTML-GEN-CL046）: `documents/docs-index.md` 不得落后于文档现状。

    生成器单源在 hermes-manager（本仓只消费、不复制脚本）：上游脚本缺失时 skip，
    在时用 `--check --quiet` 判定，rc≠0 即「改了文档没说」。
    """

    GEN = Path(os.path.expanduser('~/CodeSpace/hermes-manager/scripts/hm-docs-index.py'))
    INDEX = ROOT / 'documents' / 'docs-index.md'

    def test_01_index_exists_with_rows(self):
        self.assertTrue(self.INDEX.is_file(), 'documents/docs-index.md 必须入库（生成器单源产出）')
        rows = [ln for ln in self.INDEX.read_text(encoding='utf-8').splitlines()
                if ln.startswith('| documents/')]
        # 下限只防「清单被清空/截断」，不是口径断言：生成器 v1.1 的 durable 面
        # 只收 documents/*.md + documents/solutions/（排除 review/reports/handoff 等子目录），
        # 本仓实测 19 篇；口径真值由 test_02 的逐字节 --check 钉住。
        self.assertGreaterEqual(len(rows), 10, f'清单行数异常: {len(rows)}')

    def test_02_index_not_stale(self):
        if not self.GEN.is_file():
            self.skipTest(f'上游生成器缺失，跳过门禁: {self.GEN}')
        r = subprocess.run([sys.executable, str(self.GEN), '--root', str(ROOT),
                            '--check', '--quiet'],
                           cwd=str(ROOT), capture_output=True, text=True, timeout=180)
        self.assertEqual(r.returncode, 0,
                         f'文档清单落后于现状（跑 {self.GEN} --root . 重新生成）\n'
                         f'stdout: {r.stdout.strip()[:400]}\nstderr: {r.stderr.strip()[:400]}')


if __name__ == '__main__':
    unittest.main()
