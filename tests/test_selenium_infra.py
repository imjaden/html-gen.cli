"""CL024 守卫：chromedriver 路径 env 化（tests/conftest.py）。

四条判据（全静态/子进程，不开浏览器）：
1) 测试代码里不得出现 `/Users/…` 形式的用户绝对路径（换机器必红的老坑）；
2) `CHROMEDRIVER` env 只覆盖路径、缺省值按 `~` 展开（向后兼容且不绑用户名）；
3) 二进制不存在时 `chromedriver_service()` 抛 SkipTest（缺驱动是环境问题，不是代码坏）；
4) `CHROMEDRIVER_REQUIRED=1` 时缺驱动必须抛 RuntimeError（CI 口径：门禁不许静默放水）。
"""
import os
import subprocess
import sys
import unittest
from pathlib import Path

TESTS = Path(__file__).resolve().parent
# 期望缺省值按 `~` 现算（不写字面量，test_01 的判据对任何用户都成立）
EXPECTED_DEFAULT = os.path.join(
    os.path.expanduser('~'), 'CodeSpace', 'script-miner', 'cache', 'chromedriver', 'chromedriver')


def _run_in_tests(code, env_extra):
    env = dict(os.environ)
    env.pop('CHROMEDRIVER', None)
    env.pop('CHROMEDRIVER_REQUIRED', None)
    env.update(env_extra)
    return subprocess.run([sys.executable, '-c', code], cwd=str(TESTS),
                          capture_output=True, text=True, env=env)


class TestChromedriverEnv(unittest.TestCase):

    def test_01_no_user_absolute_path_in_tests(self):
        # 判据只看「用户主目录前缀与驱动名同行」⇒ conftest 与本文件同样受约束，无按名豁免。
        # 本行与上方注释含字面量，用 `noqa: user-path-guard` 显式标注为判据自身（不是拼接绕检）。
        skip = 'noqa: user-path-guard'
        hits = []
        for p in sorted(TESTS.rglob('*.py')):
            for i, line in enumerate(p.read_text(encoding='utf-8').splitlines(), 1):
                if skip in line or line.lstrip().startswith('#'):
                    continue
                if '/Users/' in line and 'chromedriver' in line:   # noqa: user-path-guard
                    hits.append(f'{p.relative_to(TESTS)}:{i}')
        self.assertEqual(hits, [], f'测试代码仍绑用户绝对路径: {hits}')

    def test_02_env_overrides_path_and_default_is_expanduser(self):
        code = 'import conftest; print(conftest.CHROMEDRIVER)'
        r_env = _run_in_tests(code, {'CHROMEDRIVER': '/tmp/whatever/chromedriver'})
        self.assertEqual(r_env.returncode, 0, r_env.stderr)
        self.assertEqual(r_env.stdout.strip(), '/tmp/whatever/chromedriver', 'CHROMEDRIVER 未生效')
        r_def = _run_in_tests(code, {})
        self.assertEqual(r_def.returncode, 0, r_def.stderr)
        self.assertEqual(r_def.stdout.strip(), EXPECTED_DEFAULT,
                         '缺省值应按 ~ 展开（向后兼容且不绑用户名）')

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

    def test_04_required_flag_turns_missing_driver_into_failure(self):
        code = ('import conftest\n'
                'try:\n'
                '    conftest.chromedriver_service()\n'
                'except RuntimeError as e:\n'
                '    print("RAISE:" + str(e))\n')
        r = _run_in_tests(code, {'CHROMEDRIVER': '/nonexistent/chromedriver',
                                 'CHROMEDRIVER_REQUIRED': '1'})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(r.stdout.startswith('RAISE:'),
                        f'CHROMEDRIVER_REQUIRED=1 时缺驱动必须失败，实得: {r.stdout!r}{r.stderr}')
        self.assertIn('REQUIRED', r.stdout)


if __name__ == '__main__':
    unittest.main()
