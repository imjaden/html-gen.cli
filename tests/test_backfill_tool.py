"""scripts/backfill-table-json.py 的前置校验与差异报告（HTML-GEN-CL040 / D2-B）。

为什么单独建套件：HG-SEC-253 是「静默丢数据」级缺陷（按索引 zip 截断、legacy 键互相覆盖），
只修不测等于给下一轮重构留复发面。夹具全部落在 mkdtemp（守 test_selenium_infra.test_05 的 tmp 判据）。
被测对象是 CLI 工具 ⇒ 用 subprocess 调，不 import（避免测试与脚本内部结构耦合）。
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from conftest import TmpDirMixin

PROJECT = Path(__file__).resolve().parent.parent
SCRIPT = PROJECT / 'scripts' / 'backfill-table-json.py'


def run(args):
    return subprocess.run([sys.executable, str(SCRIPT)] + args, capture_output=True, text=True)


def make_pair(tmp, columns, data, old_columns, old_data, legacy=None):
    """造一对「产物 HTML + 旧数据源 JSON」，返回 (html_path, json_path)。"""
    html = tmp / 'page.html'
    html.write_text(
        '<script>const COLUMNS = ' + json.dumps(columns, ensure_ascii=False) + ';\n'
        'const DATA = ' + json.dumps(data, ensure_ascii=False) + ';\n</script>',
        encoding='utf-8')
    raw = {'columns': old_columns, 'data': old_data}
    if legacy is not None:
        raw['legacy'] = legacy
    src = tmp / 'src.json'
    src.write_text(json.dumps(raw, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return html, src


COLS = [{'key': 'strategy', 'label': '计', 'width': '60px'},
        {'key': 'note', 'label': '备注', 'width': '80px'}]


class TestBackfillTool(TmpDirMixin, unittest.TestCase):
    def test_01_row_count_mismatch_refuses_apply(self):
        old_rows = [{'strategy': f'计{i}'} for i in range(5)]
        new_rows = [{'strategy': '计0', 'note': 'n0'}, {'strategy': '计1', 'note': 'n1'}]
        html, src = make_pair(self.tmpdir, COLS, new_rows, COLS, old_rows)
        before = src.read_text(encoding='utf-8')

        r = run(['--pair', f'{html}={src}', '--apply'])
        self.assertEqual(r.returncode, 2, f'行数不等必须拒写:\n{r.stdout}{r.stderr}')
        self.assertIn('行数不等', r.stderr)
        self.assertEqual(src.read_text(encoding='utf-8'), before, '拒绝路径不得写盘')

        # 显式声明「旧行可丢」才放行
        r2 = run(['--pair', f'{html}={src}', '--apply', '--drop-orphans'])
        self.assertEqual(r2.returncode, 0, f'--drop-orphans 应放行:\n{r2.stdout}{r2.stderr}')
        self.assertEqual(len(json.loads(src.read_text(encoding='utf-8'))['data']), 2)

    def test_02_duplicate_row_key_refuses_apply(self):
        dup_rows = [{'strategy': '走为上', 'idiom': 'a'}, {'strategy': '走为上', 'idiom': 'b'}]
        new_rows = [{'strategy': '走为上', 'note': 'x'}]
        html, src = make_pair(self.tmpdir, COLS, new_rows, COLS, dup_rows)
        before = src.read_text(encoding='utf-8')

        r = run(['--pair', f'{html}={src}', '--apply'])
        self.assertEqual(r.returncode, 2, f'行标识重复必须拒写:\n{r.stdout}{r.stderr}')
        self.assertIn('行标识重复', r.stderr)
        self.assertIn('走为上', r.stderr, 'stderr 要点名重复的键')
        self.assertEqual(src.read_text(encoding='utf-8'), before, '拒绝路径不得写盘')

        r2 = run(['--pair', f'{html}={src}', '--apply', '--drop-orphans'])
        self.assertEqual(r2.returncode, 0, f'--drop-orphans 应放行:\n{r2.stdout}{r2.stderr}')

    def test_03_field_diff_direction_and_values(self):
        old_rows = [{'strategy': '走为上', 'idiom': '走为上'}]
        new_rows = [{'strategy': '走为上', 'note': 'n1'}]
        html, src = make_pair(self.tmpdir, COLS, new_rows, COLS, old_rows)

        r = run(['--pair', f'{html}={src}', '--dry-run'])
        self.assertEqual(r.returncode, 0, r.stderr)
        # 方向必须正确：note 是新增、idiom 是被摘除，且都带真值
        self.assertIn("+note='n1'", r.stdout, f'新增字段应带新值:\n{r.stdout}')
        self.assertIn("-idiom='走为上'", r.stdout, f'摘除字段应带旧值:\n{r.stdout}')
        self.assertNotIn('<dropped>', r.stdout, '不得再出现占位字面（旧实现的双向错位）')
        self.assertNotIn('<none>', r.stdout)

    def test_04_legacy_dangling_reported(self):
        # 行已改名（旧名 走为上计 → 现行 走为上），legacy 仍按旧名存 ⇒ 悬空
        old_rows = [{'strategy': '走为上'}]
        new_rows = [{'strategy': '走为上', 'note': 'n'}]
        html, src = make_pair(self.tmpdir, COLS, new_rows, COLS, old_rows,
                              legacy={'idiom': {'走为上计': '走为上计'}})
        r = run(['--pair', f'{html}={src}', '--dry-run'])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('悬空', r.stdout, f'dry-run 应报 legacy 悬空键:\n{r.stdout}')
        self.assertIn('走为上计', r.stdout)

        # 真数据三表：re-key 后必须 0 条（只读，不写盘）
        for stem in ('daming', 'yongzheng', 'zhuyuanzhang'):
            page = PROJECT / 'demos' / 'drama' / f'{stem}-strategy-table.html'
            data = PROJECT / 'data' / f'_drama-table-{stem}-strategy.json'
            rr = run(['--pair', f'{page}={data}', '--dry-run'])
            self.assertEqual(rr.returncode, 0, rr.stderr)
            self.assertNotIn('悬空', rr.stdout, f'{stem} 的 legacy 不应有悬空键:\n{rr.stdout}')

    def test_05_rename_reported_in_same_run(self):
        """HG-SEC-260：改名造成的悬空必须在**本次** --apply 当轮报出，不能晚一轮。

        旧实现拿写盘前的旧行当参照系，而 legacy 正是按旧行名写的 ⇒ 参照系与写入端同源，
        本次改名永远「当场绿」。夹具刻意让旧行名与新行名不同：legacy 写在 旧名 下，
        产物行是 新名 ⇒ 本轮就该报。
        """
        old_rows = [{'strategy': '走为上计', 'idiom': 'x'}]
        new_rows = [{'strategy': '走为上', 'note': 'n'}]
        html, src = make_pair(self.tmpdir, COLS, new_rows, COLS, old_rows)

        r = run(['--pair', f'{html}={src}', '--apply'])
        self.assertEqual(r.returncode, 0, f'{r.stdout}{r.stderr}')
        self.assertIn('悬空', r.stdout, f'改名当轮必须报悬空（否则要等下一轮）:\n{r.stdout}')
        self.assertIn('走为上计', r.stdout)
        # 写盘后仍是同一个判定口径：下一次 dry-run 也必须报（数据里确实挂着断链键）
        r2 = run(['--pair', f'{html}={src}', '--dry-run'])
        self.assertIn('悬空', r2.stdout, r2.stdout)


if __name__ == '__main__':
    unittest.main()
