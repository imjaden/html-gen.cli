"""Tests for html-gen: doc, slide, table, knowledge templates."""
import json, os, re, sys, unittest
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
DEMOS = PROJECT / 'demos'
GEN = PROJECT / 'html-gen.py'


def run_gen(*args):
    cmd = [sys.executable, str(GEN)] + list(args)
    r = os.system(' '.join(f"'{c}'" if ' ' in c else c for c in cmd))
    assert r == 0, f"gen failed: {' '.join(args)}"


class TestDoc(unittest.TestCase):
    """Doc mode — flat HTML, no slide code."""

    def test_gen_all_demos(self):
        for md_name, title in [
            ('html-gen-usage-guide-v1.0-20260707.md', '使用指南'),
            ('template-A-guide-v1.0-20260707.md', 'A 型'),
            ('template-B-guide-v1.0-20260707.md', 'B 型'),
            ('template-B-markdown-spec-v1.0-20260707.md', 'B 型规范'),
            ('template-C-guide-v1.0-20260707.md', 'C 型'),
        ]:
            out = Path('/tmp') / f'test-doc-{md_name.replace(".md", ".html")}'
            run_gen('doc', '-i', str(DEMOS / md_name), '--title', title, '-o', str(out))
            html = out.read_text()
            self.assertTrue(html.startswith('<!DOCTYPE html>'))
            self.assertTrue(html.strip().endswith('</html>'))
            # No unreplaced placeholders
            leftovers = re.findall(r'<!--[A-Z_]+-->', html)
            self.assertEqual(len(leftovers), 0, f"{md_name}: leftovers {leftovers}")
            # Doc template should NOT have slide-specific elements
            self.assertNotIn('slide-main', html, f"{md_name}: has slide code")
            self.assertNotIn('slideMode', html, f"{md_name}: has slideMode JS")
            self.assertNotIn('mode-toggle', html, f"{md_name}: has mode toggle")
            # Doc template should have doc elements
            self.assertIn('doc-main', html)
            self.assertIn('doc-body', html)
            self.assertIn('doc-toc', html)


class TestSlide(unittest.TestCase):
    """Slide mode — standalone template, no doc/slide toggle."""

    def test_gen_slide(self):
        out = Path('/tmp/test-slide-demo.html')
        run_gen('slide', '-i', str(DEMOS / 'template-B-markdown-spec-v1.0-20260707.md'),
                '--title', 'Slide Test', '-o', str(out))
        html = out.read_text()
        self.assertTrue(html.startswith('<!DOCTYPE html>'))
        leftovers = re.findall(r'<!--[A-Z_]+-->', html)
        self.assertEqual(len(leftovers), 0, f"leftovers: {leftovers}")
        # Must have slide elements
        for eid in ['slideMain', 'slidePage', 'slideDots', 'slideNav', 'slidePageNum',
                     'docBody', 'toc']:
            self.assertIn(f'id="{eid}"', html, f"missing id={eid}")
        # Must NOT have doc/slide toggle
        self.assertNotIn('mode-toggle', html)
        self.assertNotIn('switchMode', html)
        # Must have slide JS
        self.assertIn('slide.goTo', html)
        self.assertIn('slide.init()', html)

    def test_cover_page(self):
        out = Path('/tmp/test-slide-cover.html')
        run_gen('slide', '-i', str(DEMOS / 'template-B-guide-v1.0-20260707.md'),
                '--title', 'Cover Test', '-o', str(out))
        html = out.read_text()
        self.assertIn('slide-cover', html)
        self.assertIn('slide-cover-count', html)

    def test_perf_warning(self):
        out = Path('/tmp/test-slide-perf.html')
        src = DEMOS / 'template-B-guide-v1.0-20260707.md'
        run_gen('slide', '-i', str(src), '--title', 'Perf', '-o', str(out))
        html = out.read_text()
        # Small doc should have empty perf warning
        m = re.search(r'<div class="perf-warning" id="perfWarning">(.*?)</div>', html, re.DOTALL)
        self.assertIsNotNone(m)
        if m:
            self.assertEqual(m.group(1).strip(), '')

    def test_no_slide_code_in_doc(self):
        """Verify doc template doesn't leak slide code."""
        tmpl = (PROJECT / 'layout-doc.html').read_text()
        self.assertNotIn('slideMode', tmpl)
        self.assertNotIn('switchMode', tmpl)
        self.assertNotIn('mode-toggle', tmpl)
        self.assertNotIn('slide-main', tmpl)
        self.assertNotIn('slide-nav', tmpl)


class TestBackwardCompat(unittest.TestCase):
    """Table and knowledge still work."""

    def test_table(self):
        out = Path('/tmp/test-table-compat.html')
        run_gen('table', '-d', str(PROJECT / 'data/_demos-data.json'), '--title', 'T', '-o', str(out))
        html = out.read_text()
        self.assertIn('data-table', html)

    def test_knowledge(self):
        out = Path('/tmp/test-kb-compat.html')
        run_gen('knowledge', '-d', str(PROJECT / 'data/_chaitin-kb-data.json'),
                '-g', str(PROJECT / 'data/_chaitin-groups.json'), '--title', 'K', '-o', str(out))
        html = out.read_text()
        self.assertIn('kw-wrapper', html)


if __name__ == '__main__':
    unittest.main(verbosity=2)
