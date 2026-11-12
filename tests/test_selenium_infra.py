"""CL024 守卫：chromedriver 路径 env 化（tests/conftest.py）。

三条判据（全静态/子进程，不开浏览器）：
1) 除 conftest.py 外，测试代码不得再出现第三方仓的绝对路径（换机器必红的老坑）；
2) `CHROMEDRIVER` env 只覆盖路径、缺省值保持不变（本机行为不掉）；
3) 二进制不存在时 `chromedriver_service()` 抛 SkipTest（是 skip 而不是 64 个文件各自炸）。
"""
import os
import subprocess
import sys
import unittest
from pathlib import Path

TESTS = Path(__file__).resolve().parent
ROOT = TESTS.parent
# 拼出来而不是写字面量：否则本文件自己会被 test_01 扫中（仍是同一条判据的合法豁免写法）
HARDCODE = 'script-miner/cache/' + 'chromedriver/chromedriver'
DEFAULT = '/Users/jadenli/CodeSpace/' + HARDCODE


def _run_in_tests(code, env_extra):
    env = dict(os.environ)
    env.update(env_extra)
    return subprocess.run([sys.executable, '-c', code], cwd=str(TESTS),
                          capture_output=True, text=True, env=env)


class TestChromedriverEnv(unittest.TestCase):

    def test_01_no_hardcoded_path_outside_conftest(self):
        hits = []
        for p in sorted(TESTS.glob('*.py')):
            if p.name == 'conftest.py':
                continue
            if HARDCODE in p.read_text(encoding='utf-8'):
                hits.append(p.name)
        self.assertEqual(hits, [], f'这些文件仍硬编码 chromedriver 绝对路径: {hits}')

    def test_02_env_overrides_path_default_kept(self):
        code = ('import conftest; print(conftest.CHROMEDRIVER)')
        r_env = _run_in_tests(code, {'CHROMEDRIVER': '/tmp/whatever/chromedriver'})
        self.assertEqual(r_env.returncode, 0, r_env.stderr)
        self.assertEqual(r_env.stdout.strip(), '/tmp/whatever/chromedriver', 'CHROMEDRIVER 未生效')
        env = dict(os.environ)
        env.pop('CHROMEDRIVER', None)
        r_def = subprocess.run([sys.executable, '-c', code], cwd=str(TESTS),
                               capture_output=True, text=True, env=env)
        self.assertEqual(r_def.stdout.strip(), DEFAULT, '缺省值必须保持历史现值（向后兼容）')

    def test_03_missing_binary_skips_with_reason(self):
        code = ('import unittest, conftest\n'
                'try:\n'
                '    conftest.chromedriver_service()\n'
                'except unittest.SkipTest as e:\n'
                '    print("SKIP:" + str(e))\n')
        r = _run_in_tests(code, {'CHROMEDRIVER': '/nonexistent/chromedriver'})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(r.stdout.startswith('SKIP:'), f'缺驱动应抛 SkipTest，实得: {r.stdout!r}{r.stderr}')
        self.assertIn('/nonexistent/chromedriver', r.stdout, 'skip 理由应带实际路径')
        self.assertIn('CHROMEDRIVER', r.stdout, 'skip 理由应提示 env 覆盖方式')


if __name__ == '__main__':
    unittest.main()
