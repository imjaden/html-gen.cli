"""回归测试: 生成物隐私参数化 — github corner / home 入口默认不带, 显式入参才注入."""
import json, os, subprocess, tempfile, unittest
from pathlib import Path

GEN = Path(__file__).resolve().parent.parent / 'html-gen.py'


def run(*args, env_extra=None):
    env = dict(os.environ)
    if env_extra:
        env.update(env_extra)
    return subprocess.run(['python3', str(GEN), *args],
                          capture_output=True, text=True, timeout=60, env=env)


class TestCornerPrivacy(unittest.TestCase):

    def setUp(self):
        # 每用例独立临时目录 (pytest-xdist 隔离)
        self.tmp = Path(tempfile.mkdtemp(prefix='_tmp_corner_privacy_'))
        self.data = self.tmp / 't.json'
        self.data.write_text(json.dumps({
            'columns': [{'key': 'a', 'label': 'A'}],
            'data': [{'a': '1'}, {'a': '2'}],
        }, ensure_ascii=False), encoding='utf-8')

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _gen(self, *extra, env_extra=None):
        out = self.tmp / 't.html'
        r = run('table', '-d', str(self.data), '-o', str(out), *extra, env_extra=env_extra)
        self.assertEqual(r.returncode, 0, r.stderr)
        return out.read_text(encoding='utf-8')

    def test_01_default_no_corner_no_home(self):
        """默认生成物不含 github corner / home 入口元素 (隐私; CSS 类名保留无碍)."""
        html = self._gen()
        self.assertNotIn('class="github-corner"', html)
        self.assertNotIn('class="github-corner-hit"', html)
        self.assertNotIn('class="home-link"', html)
        self.assertNotIn('imjaden', html)
        self.assertNotIn('jaden.tech', html)

    def test_02_github_url_injects_corner(self):
        """--github-url 注入 corner, href 正确."""
        html = self._gen('--github-url', 'https://github.com/example/repo')
        self.assertIn('class="github-corner"', html)
        self.assertIn('class="github-corner-hit"', html)
        self.assertIn('href="https://github.com/example/repo"', html)
        self.assertNotIn('class="home-link"', html)

    def test_03_home_url_injects_link(self):
        """--home-url 注入 🏠 入口."""
        html = self._gen('--home-url', 'demos/index.html')
        self.assertIn('class="home-link"', html)
        self.assertIn('href="demos/index.html"', html)
        self.assertNotIn('class="github-corner"', html)

    def test_04_env_fallback(self):
        """env HTML_GEN_GITHUB_URL / HTML_GEN_HOME_URL 兜底生效."""
        html = self._gen(env_extra={
            'HTML_GEN_GITHUB_URL': 'https://github.com/env/repo',
            'HTML_GEN_HOME_URL': 'env-index.html',
        })
        self.assertIn('href="https://github.com/env/repo"', html)
        self.assertIn('href="env-index.html"', html)

    def test_05_cli_overrides_env(self):
        """CLI 参数优先于 env."""
        html = self._gen('--github-url', 'https://github.com/cli/repo',
                         env_extra={'HTML_GEN_GITHUB_URL': 'https://github.com/env/repo'})
        self.assertIn('href="https://github.com/cli/repo"', html)
        self.assertNotIn('https://github.com/env/repo', html)

    def test_06_doc_and_knowledge_support_params(self):
        """doc/knowledge 同样支持参数."""
        md = self.tmp / 'd.md'
        md.write_text('# 标题\n\n## 章节\n内容\n', encoding='utf-8')
        dout = self.tmp / 'd.html'
        r = run('doc', '-i', str(md), '-o', str(dout), '--github-url', 'https://github.com/doc/repo')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('class="github-corner"', dout.read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
