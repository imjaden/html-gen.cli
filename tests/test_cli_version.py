"""回归测试: CL016 CLI help 版本日期规范 (version 常量/子指令/--version 兼容/help 首屏)."""
import subprocess, unittest
from pathlib import Path

GEN = Path(__file__).resolve().parent.parent / 'html-gen.py'


def run(*args):
    return subprocess.run(['python3', str(GEN), *args],
                          capture_output=True, text=True, timeout=60)


class TestCliVersion(unittest.TestCase):
    """版本常量 + version 子指令 + --version 兼容 + help 首屏内嵌."""

    def test_01_help_overview_has_version_date(self):
        """html-gen help 首屏标题含 v{ver}({date}) 紧凑格式."""
        r = run('help')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('v3.3(2026-08-28)', r.stdout, "help 首屏应内嵌 v3.3(2026-08-28)")

    def test_02_version_subcommand(self):
        """version 子指令输出 {name} v{ver} ({date}) 空格分隔."""
        r = run('version')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.strip(), 'html-gen v3.3 (2026-08-28)')

    def test_03_version_flag_compatible(self):
        """--version flag 兼容, 输出与 version 子指令一致."""
        r = run('--version')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.strip(), 'html-gen v3.3 (2026-08-28)')

    def test_04_argparse_help_description(self):
        """argparse -h description 内嵌版本日期."""
        r = run('-h')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('v3.3(2026-08-28)', r.stdout, "-h 首屏应内嵌 v3.3(2026-08-28)")

    def test_05_version_constants(self):
        """模块常量: __version__ 格式 \\d+\\.\\d+, __release_date__ 格式 YYYY-MM-DD."""
        from importlib.util import spec_from_file_location, module_from_spec
        import re
        spec = spec_from_file_location('html_gen', GEN)
        assert spec is not None and spec.loader is not None
        mod = module_from_spec(spec)
        spec.loader.exec_module(mod)
        self.assertRegex(mod.__version__, r'^\d+\.\d+$')
        self.assertRegex(mod.__release_date__, r'^20\d\d-\d\d-\d\d$')


if __name__ == '__main__':
    unittest.main()
