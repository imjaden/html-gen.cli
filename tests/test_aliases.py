"""回归测试: demo 根级短链别名（data/_aliases.json + rebuild 生成/清理/canonical，CL018）。"""
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
GEN = PROJECT / 'html-gen.py'
ROOT_STUB = PROJECT / 'renxuan.html'
TARGET = PROJECT / 'demos' / 'renxuan.html'
CFG = PROJECT / 'data' / '_aliases.json'


def load_gen():
    spec = importlib.util.spec_from_file_location('html_gen', GEN)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestAliasConfig(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.g = load_gen()

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix='_tmp_alias_'))

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_01_missing_file_means_none(self):
        self.assertEqual(self.g._load_alias_config(self.tmp), {'mode': 'none', 'entries': []})

    def test_02_bad_mode_rejected(self):
        (self.tmp / '_aliases.json').write_text('{"mode":"sometimes"}', encoding='utf-8')
        with self.assertRaises(ValueError):
            self.g._load_alias_config(self.tmp)

    def test_03_entries_must_be_list(self):
        (self.tmp / '_aliases.json').write_text('{"mode":"list","entries":{"a":1}}', encoding='utf-8')
        with self.assertRaises(ValueError):
            self.g._load_alias_config(self.tmp)

    def test_04_valid_config(self):
        (self.tmp / '_aliases.json').write_text(
            json.dumps({'mode': 'list', 'entries': [{'demo': 'x'}]}), encoding='utf-8')
        cfg = self.g._load_alias_config(self.tmp)
        self.assertEqual(cfg['mode'], 'list')
        self.assertEqual(cfg['entries'], [{'demo': 'x'}])


class TestResolveAliases(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.g = load_gen()
        cls.demos = [
            {'entry': 'a.html', 'referenced': False},
            {'entry': 'renxuan.html', 'referenced': False},
            {'entry': 'sub/b.html', 'referenced': True},
        ]

    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix='_tmp_aliasroot_'))

    def tearDown(self):
        import shutil
        shutil.rmtree(self.root, ignore_errors=True)

    def test_10_list_mode(self):
        cfg = {'mode': 'list', 'entries': [{'demo': 'renxuan'}]}
        self.assertEqual(self.g._resolve_aliases(cfg, self.demos, self.root),
                         [('renxuan', 'renxuan.html')])

    def test_11_custom_alias(self):
        cfg = {'mode': 'list', 'entries': [{'demo': 'renxuan', 'alias': 'book'}]}
        self.assertEqual(self.g._resolve_aliases(cfg, self.demos, self.root), [('book', 'renxuan.html')])

    def test_12_all_mode_skips_subdirs_and_referenced(self):
        out = self.g._resolve_aliases({'mode': 'all', 'entries': []}, self.demos, self.root)
        self.assertEqual(sorted(out), [('a', 'a.html'), ('renxuan', 'renxuan.html')])

    def test_13_none_mode(self):
        self.assertEqual(self.g._resolve_aliases({'mode': 'none', 'entries': []}, self.demos, self.root), [])

    def test_14_duplicate_alias_rejected(self):
        cfg = {'mode': 'list', 'entries': [{'demo': 'a', 'alias': 'x'}, {'demo': 'renxuan', 'alias': 'x'}]}
        with self.assertRaises(ValueError):
            self.g._resolve_aliases(cfg, self.demos, self.root)

    def test_15_unknown_demo_rejected(self):
        cfg = {'mode': 'list', 'entries': [{'demo': 'nope'}]}
        with self.assertRaises(ValueError):
            self.g._resolve_aliases(cfg, self.demos, self.root)

    def test_16_handwritten_page_not_overwritten(self):
        (self.root / 'renxuan.html').write_text('<html>手写页</html>', encoding='utf-8')
        cfg = {'mode': 'list', 'entries': [{'demo': 'renxuan'}]}
        with self.assertRaises(ValueError):
            self.g._resolve_aliases(cfg, self.demos, self.root)

    def test_17_previous_stub_is_overwritable(self):
        (self.root / 'renxuan.html').write_text(
            self.g.ALIAS_MARKER + '<html>old</html>', encoding='utf-8')
        cfg = {'mode': 'list', 'entries': [{'demo': 'renxuan'}]}
        self.assertEqual(len(self.g._resolve_aliases(cfg, self.demos, self.root)), 1)


class TestCanonicalSync(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.g = load_gen()

    def test_20_add_then_idempotent_then_del(self):
        tmp = Path(tempfile.mkdtemp(prefix='_tmp_canon_'))
        page = tmp / 'p.html'
        page.write_text('<html><head><meta charset="utf-8"></head><body>x</body></html>',
                        encoding='utf-8')
        self.assertEqual(self.g._sync_canonical(page, 'https://e/x.html'), 'add')
        self.assertIn('rel="canonical"', page.read_text(encoding='utf-8'))
        self.assertEqual(self.g._sync_canonical(page, 'https://e/x.html'), 'none')
        self.assertEqual(page.read_text(encoding='utf-8').count('rel="canonical"'), 1)
        self.assertEqual(self.g._sync_canonical(page, None), 'del')
        self.assertNotIn('canonical', page.read_text(encoding='utf-8'))
        self.assertEqual(self.g._sync_canonical(page, None), 'none')
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


class TestAliasIntegration(unittest.TestCase):

    def _rebuild(self):
        return subprocess.run(['python3', str(GEN), 'demo', '--rebuild'],
                              capture_output=True, text=True, timeout=120)

    def test_30_config_present(self):
        cfg = json.loads(CFG.read_text(encoding='utf-8'))
        self.assertEqual(cfg['mode'], 'list')
        self.assertIn('renxuan', [e.get('demo') for e in cfg['entries']])

    def test_31_root_stub_and_canonical(self):
        r = self._rebuild()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('别名桩', r.stdout)
        stub = ROOT_STUB.read_text(encoding='utf-8')
        self.assertIn('<!-- html-gen:alias auto -->', stub)
        self.assertIn('content="0;url=demos/renxuan.html"', stub)
        self.assertIn('https://html-gen.cli.jaden.tech/renxuan.html', stub)
        target = TARGET.read_text(encoding='utf-8')
        self.assertEqual(target.count('<!-- html-gen:canonical auto -->'), 1)
        self.assertIn('<link rel="canonical" href="https://html-gen.cli.jaden.tech/renxuan.html">', target)

    def test_32_rebuild_idempotent(self):
        self._rebuild()
        before = (ROOT_STUB.read_bytes(), TARGET.read_bytes())
        r = self._rebuild()
        self.assertEqual(r.returncode, 0, r.stderr)
        after = (ROOT_STUB.read_bytes(), TARGET.read_bytes())
        self.assertEqual(before, after)
        self.assertIn('新建 0', r.stdout)
        self.assertIn('canonical +0', r.stdout)


if __name__ == '__main__':
    unittest.main()
