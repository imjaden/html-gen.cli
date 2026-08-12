"""Tests for html-gen prompt subcommand."""
import subprocess, sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
GEN = PROJECT / 'html-gen.py'


def run_prompt(*args):
    return subprocess.run([sys.executable, str(GEN), 'prompt'] + list(args),
                          capture_output=True, text=True, timeout=10)


class TestPromptCmd:
    """prompt subcommand tests — subprocess style."""

    def test_01_prompt_list(self):
        """html-gen prompt lists all skills."""
        r = run_prompt()
        assert r.returncode == 0, f"exit={r.returncode}, stderr={r.stderr}"
        assert 'html-gen-table' in r.stdout
        assert 'html-gen-doc' in r.stdout
        assert 'html-gen-knowledge' in r.stdout
        assert 'html-gen' in r.stdout

    def test_02_prompt_table_full(self):
        """html-gen prompt html-gen-table outputs full SKILL.md."""
        r = run_prompt('html-gen-table')
        assert r.returncode == 0, f"exit={r.returncode}, stderr={r.stderr}"
        assert 'v2.3.0' in r.stdout
        # Should splice references
        assert 'table-demo-prompt' in r.stdout

    def test_03_prompt_doc_full(self):
        """html-gen prompt html-gen-doc outputs full SKILL.md."""
        r = run_prompt('html-gen-doc')
        assert r.returncode == 0, f"exit={r.returncode}, stderr={r.stderr}"
        assert ('B 型文档' in r.stdout or '布局' in r.stdout or 'Markdown' in r.stdout)

    def test_04_prompt_nonexistent(self):
        """html-gen prompt 不存在 → non-zero exit + error."""
        r = run_prompt('不存在')
        assert r.returncode != 0
        assert '不存在' in r.stderr
        assert '可用' in r.stdout or '可用' in r.stderr

    def test_05_prompt_brief(self):
        """html-gen prompt html-gen --brief → 摘要模式."""
        r = run_prompt('html-gen', '--brief')
        assert r.returncode == 0, f"exit={r.returncode}, stderr={r.stderr}"
        assert '章节:' in r.stdout
