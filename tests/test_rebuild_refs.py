"""回归测试: demo --rebuild 的 kb-data 引用收集形状防护（CL017）。"""
import importlib.util
import json
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


class TestCollectDemoRefs(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.g = load_gen()

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix='_tmp_refs_'))

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_01_array_of_objects(self):
        (self.tmp / '_a-kb-data.json').write_text(
            json.dumps([{'url': 'x/1.html'}, {'title': '无 url'}, {'url': ''}]),
            encoding='utf-8')
        refs = self.g._collect_demo_refs(self.tmp)
        self.assertEqual(refs, {'x/1.html': ['_a-kb-data']})

    def test_02_multiple_sources_same_url(self):
        payload = json.dumps([{'url': 'x/1.html'}])
        (self.tmp / '_a-kb-data.json').write_text(payload, encoding='utf-8')
        (self.tmp / '_b-kb-data.json').write_text(payload, encoding='utf-8')
        refs = self.g._collect_demo_refs(self.tmp)
        self.assertEqual(sorted(refs['x/1.html']), ['_a-kb-data', '_b-kb-data'])

    def test_03_dict_file_skipped(self):
        """knowledge catalog 形状（dict）不得让 rebuild 崩溃。"""
        (self.tmp / '_catalog-kb-data.json').write_text(
            json.dumps({'items': [{'url': 'y/1.html'}], 'output': 'o.html'}), encoding='utf-8')
        self.assertEqual(self.g._collect_demo_refs(self.tmp), {})

    def test_04_broken_json_skipped(self):
        (self.tmp / '_broken-kb-data.json').write_text('not json {', encoding='utf-8')
        self.assertEqual(self.g._collect_demo_refs(self.tmp), {})

    def test_05_non_string_url_skipped(self):
        (self.tmp / '_d-kb-data.json').write_text(
            json.dumps([{'url': 123}, 'junk', {'url': None}, {'url': 'z/9.html'}]),
            encoding='utf-8')
        self.assertEqual(self.g._collect_demo_refs(self.tmp), {'z/9.html': ['_d-kb-data']})

    def test_06_missing_dir_is_empty(self):
        self.assertEqual(self.g._collect_demo_refs(self.tmp / 'no-such-dir'), {})


class TestRebuildIntegration(unittest.TestCase):

    def test_10_rebuild_still_works(self):
        r = subprocess.run(['python3', str(GEN), 'demo', '--rebuild'],
                           capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('registry 重建', r.stdout)
        reg = json.loads((GEN.parent / 'demos' / '_registry.json').read_text(encoding='utf-8'))
        self.assertGreaterEqual(reg['count'], 65)
        entry = [d for d in reg['demos'] if d['entry'] == 'the-price-you-choose.html']
        self.assertEqual(len(entry), 1)
        self.assertFalse(entry[0]['referenced'])


if __name__ == '__main__':
    unittest.main()
