"""HTML-GEN-CL009: A 型表格 GitHub Issue 反馈通道 — 渲染条件 + 同步脚本行为。

两部分:
1. TestFeedbackRender (Selenium): --feedback-repo 条件渲染、URL 预填参数、列上下文;
2. TestIssueSyncScript (纯 Python): issue body 解析 / 六类校验 / 冲突 / 幂等 / apply 往返。
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

CHROMEDRIVER = '/Users/jadenli/CodeSpace/script-miner/cache/chromedriver/chromedriver'
PROJECT = Path(__file__).resolve().parent.parent
GEN = PROJECT / 'html-gen.py'
SYNC = PROJECT / 'scripts' / 'countries-issue-sync.py'

FIXTURE = {
    'title': '反馈通道夹具',
    'columns': [
        {'key': 'name', 'label': '名称'},
        {'key': 'pop', 'label': '人口', 'type': 'number'},
        {'key': 'note', 'label': '备注'},
    ],
    'data': [
        {'name': '伊朗', 'pop': 9157, 'note': '波斯帝国'},
        {'name': '希腊', 'pop': 1041, 'note': ''},
    ],
    'tabs': [],
    'options': {
        'pageSize': 30,
        'feedback': {'dataset': 'fixture', 'key': 'name', 'altKey': 'note'},
    },
}

ISSUE_BODY = """### 页面

demos/countries-table.html

### 数据集

countries

### 行标识

伊朗

### 行英文标识

Iran

### 字段

pop_wan

### 当前值

9157

### 建议值

9200

### 来源

https://example.org/source

### 补充说明

_No response_
"""


def _load_sync_module():
    name = 'countries_issue_sync_under_test'
    spec = importlib.util.spec_from_file_location(name, SYNC)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestFeedbackRender(unittest.TestCase):
    """渲染条件 + URL 预填（Selenium）。"""

    @classmethod
    def setUpClass(cls):
        opts = Options()
        opts.add_argument('--headless')
        opts.add_argument('--no-sandbox')
        opts.add_argument('--disable-dev-shm-usage')
        cls.driver = webdriver.Chrome(service=Service(CHROMEDRIVER), options=opts)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def setUp(self):
        self.driver.set_window_size(1400, 900)
        self.tmp = Path(tempfile.mkdtemp(prefix='_tmp_issue_feedback_'))
        self.data = self.tmp / 'f.json'
        self.data.write_text(json.dumps(FIXTURE, ensure_ascii=False), encoding='utf-8')

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _gen(self, *extra, env_extra=None, mutate=None):
        doc = json.loads(self.data.read_text(encoding='utf-8'))
        if mutate:
            mutate(doc)
        self.data.write_text(json.dumps(doc, ensure_ascii=False), encoding='utf-8')
        out = self.tmp / 'f.html'
        env = dict(os.environ)
        env.pop('HTML_GEN_FEEDBACK_REPO', None)
        if env_extra:
            env.update(env_extra)
        r = subprocess.run([sys.executable, str(GEN), 'table', '-d', str(self.data),
                            '-o', str(out), *extra],
                           capture_output=True, text=True, timeout=60, env=env)
        self.assertEqual(r.returncode, 0, r.stderr)
        return out

    def _load(self, out, query=''):
        self.driver.get('file://' + str(out) + query)
        time.sleep(0.3)

    # ── 渲染条件 ──
    def test_01_default_no_button(self):
        """无 feedback 配置 → 未注入 options.feedback、分栏 header 无 #spFeedbackBtn。

        HG-SEC-112/121: 不断言 JS 源码无 `issues/new` 字面量（buildFeedbackUrl 常驻定义）。
        """
        out = self._gen(mutate=lambda d: d['options'].pop('feedback', None))
        html = out.read_text(encoding='utf-8')
        self.assertNotIn('"feedback"', html)          # 未注入 options.feedback
        self._load(out, '?split=0')
        self.assertEqual(len(self.driver.find_elements(By.ID, 'spFeedbackBtn')), 0)

    def test_02_cli_repo_renders_button(self):
        """--feedback-repo → 分栏 header 出按钮；URL 含全部预填参数且编码正确。"""
        out = self._gen('--feedback-repo', 'imjaden/html-gen.cli')
        html = out.read_text(encoding='utf-8')
        self.assertIn('issues/new', html)
        self.assertIn('"repo": "imjaden/html-gen.cli"', html)
        self._load(out, '?split=0')
        btn = self.driver.find_element(By.ID, 'spFeedbackBtn')
        self.assertTrue(btn.is_displayed())
        url = self.driver.execute_script('return window.buildFeedbackUrl(window.splitRow);')
        self.assertTrue(url.startswith('https://github.com/imjaden/html-gen.cli/issues/new?'), url)
        self.assertIn('template=data-fix.yml', url)
        self.assertIn('dataset=fixture', url)
        self.assertIn('row=' + '%E4%BC%8A%E6%9C%97', url)      # 伊朗 URL 编码
        self.assertIn('row_en=' + '%E6%B3%A2%E6%96%AF%E5%B8%9D%E5%9B%BD', url)
        self.assertNotIn('field=', url)                        # 非单元格入口 → 无字段上下文

    def test_03_empty_repo_disables(self):
        """显式空串 → 禁用（JSON 里有 repo 也不渲染）。"""
        out = self._gen('--feedback-repo', '',
                        mutate=lambda d: d['options']['feedback'].__setitem__('repo', 'imjaden/html-gen.cli'))
        html = out.read_text(encoding='utf-8')
        self.assertIn('"repo": ""', html)             # 显式空串写入（禁用）
        self.assertNotIn('"repo": "imjaden/html-gen.cli"', html)
        self._load(out, '?split=0')
        self.assertEqual(len(self.driver.find_elements(By.ID, 'spFeedbackBtn')), 0)

    def test_04_env_fallback_and_cli_priority(self):
        """env 兜底生效；CLI 覆盖 env。"""
        out = self._gen(env_extra={'HTML_GEN_FEEDBACK_REPO': 'envuser/envrepo'})
        self.assertIn('"repo": "envuser/envrepo"', out.read_text(encoding='utf-8'))
        out2 = self._gen('--feedback-repo', 'cliuser/clirepo',
                         env_extra={'HTML_GEN_FEEDBACK_REPO': 'envuser/envrepo'})
        self.assertIn('"repo": "cliuser/clirepo"', out2.read_text(encoding='utf-8'))

    def test_05_cell_click_carries_field(self):
        """点 onCellClick='split' 单元格 → URL 带 field=<列 key> + current=<值>。"""
        doc = json.loads(self.data.read_text(encoding='utf-8'))
        doc['columns'][1]['onCellClick'] = 'split'
        doc['options'].pop('feedback', None)
        self.data.write_text(json.dumps(doc, ensure_ascii=False), encoding='utf-8')
        out = self._gen('--feedback-repo', 'imjaden/html-gen.cli')
        self._load(out)
        cells = self.driver.find_elements(By.CSS_SELECTOR, 'tbody tr td')
        # 第 2 列（人口）: 第 1 行 → cells[1]
        self.driver.execute_script('arguments[0].click();', cells[1])
        time.sleep(0.3)
        url = self.driver.execute_script('return window.buildFeedbackUrl(window.splitRow);')
        self.assertIn('field=pop', url)
        self.assertIn('current=9157', url)
        self.assertIn('title=' + '%5B%E6%95%B0%E6%8D%AE%E5%8F%8D%E9%A6%88%5D', url)  # [数据反馈]

    def test_06_no_js_errors(self):
        """分栏 + 按钮路径无 JS 报错。"""
        out = self._gen('--feedback-repo', 'imjaden/html-gen.cli')
        self._load(out, '?split=1')
        errs = self.driver.execute_script(
            "window.__e=[]; window.onerror=function(m){window.__e.push(String(m));}; return window.__e;")
        self.assertEqual(errs, [])


class TestIssueSyncScript(unittest.TestCase):
    """同步脚本：解析 / 校验 / 冲突 / 幂等 / apply。"""

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_sync_module()

    # ── 解析 ──
    def test_10_parse_body(self):
        fields = self.mod.parse_issue_body(ISSUE_BODY, self.mod.yaml.safe_load(
            (PROJECT / 'scripts' / 'feedback-targets.yaml').read_text(encoding='utf-8')
        )['targets']['countries']['parse_fields'])
        self.assertEqual(fields['page'], 'demos/countries-table.html')
        self.assertEqual(fields['dataset'], 'countries')
        self.assertEqual(fields['row'], '伊朗')
        self.assertEqual(fields['row_en'], 'Iran')
        self.assertEqual(fields['field'], 'pop_wan')
        self.assertEqual(fields['current'], '9157')
        self.assertEqual(fields['suggested'], '9200')
        self.assertEqual(fields['source'], 'https://example.org/source')
        self.assertEqual(fields['note'], '')            # _No response_ → 空

    def test_12_stray_section_merged(self):
        """HG-SEC-115: 值内 '### <未知>' 段并入上一字段，不丢失也不新建字段。"""
        body = ("### 页面\n\ndemos/countries-table.html\n\n### 数据集\n\ncountries\n\n"
                "### 行标识\n\n伊朗\n\n### 字段\n\npop_wan\n\n### 建议值\n\n9200\n\n"
                "### 来源\n\nhttps://example.org/s\n\n### 补充说明\n\n第一行\n\n"
                "### 备注手写\n\n第二行\n")
        cfg = self.mod.yaml.safe_load(
            (PROJECT / 'scripts' / 'feedback-targets.yaml').read_text(encoding='utf-8'))
        fields = self.mod.parse_issue_body(body, cfg['targets']['countries']['parse_fields'])
        self.assertEqual(fields['suggested'], '9200')
        self.assertEqual(fields['source'], 'https://example.org/s')
        self.assertIn('第一行', fields['note'])
        self.assertIn('第二行', fields['note'])          # 未知段未被丢弃
        self.assertIn('备注手写', fields['note'])         # 段头文本保留为值的一部分
        self.assertEqual(len(fields), 7)                 # 本 body 未含 row_en / current

    def test_11_to_number(self):
        self.assertEqual(self.mod.to_number('9,200'), 9200)
        self.assertEqual(self.mod.to_number('33.5'), 33.5)
        self.assertIsNone(self.mod.to_number('abc'))
        self.assertIsNone(self.mod.to_number(''))

    # ── 校验（plan_issues） ──
    def _target(self):
        return self.mod.yaml.safe_load(
            (PROJECT / 'scripts' / 'feedback-targets.yaml').read_text(encoding='utf-8')
        )['targets']['countries']

    def _rows(self):
        return [{'country_zh': '伊朗', 'country_en': 'Iran', 'pop_wan': 9157, 'videos': []},
                {'country_zh': '希腊', 'country_en': 'Greece', 'pop_wan': 1041, 'videos': []}]

    def _plan(self, fields_patch, created='2026-09-10T00:00:00Z'):
        t = self._target()
        rows = self._rows()
        fields = dict(page='demos/countries-table.html', dataset='countries', row='伊朗',
                      row_en='Iran', field='pop_wan', current='9157', suggested='9200',
                      source='s', note='')
        fields.update(fields_patch)
        issues = [{'number': 1, 'title': 't', 'body': '', 'url': '', 'createdAt': created,
                   'fields': fields}]
        # 直接以 parse 结果驱动：绕过 body 解析，调用内部计划逻辑
        real_parse = self.mod.parse_issue_body
        self.mod.parse_issue_body = lambda body, pf: fields
        try:
            idx = self.mod.build_row_index(rows, t)
            return self.mod.plan_issues(issues, t, rows, idx)
        finally:
            self.mod.parse_issue_body = real_parse

    def test_12_ok(self):
        actions, skips = self._plan({})
        self.assertEqual(len(actions), 1, skips)
        self.assertEqual(actions[0]['new'], 9200)
        self.assertEqual(actions[0]['old'], 9157)

    def test_13_page_mismatch(self):
        actions, skips = self._plan({'page': 'demos/provinces-table.html'})
        self.assertEqual(actions, [])
        self.assertIn('page 不匹配', skips[0][1])

    def test_14_dataset_mismatch(self):
        actions, skips = self._plan({'dataset': 'provinces'})
        self.assertEqual(actions, [])
        self.assertIn('dataset 不匹配', skips[0][1])

    def test_15_protected_and_not_editable(self):
        for field in ('videos', 'nonexistent_col'):
            actions, skips = self._plan({'field': field, 'current': '', 'suggested': 'x'})
            self.assertEqual(actions, [], field)
            self.assertIn('保护列' if field == 'videos' else '白名单', skips[0][1])

    def test_16_row_not_found_and_ambiguous(self):
        actions, skips = self._plan({'row': '不存在国', 'row_en': 'Nowhere'})
        self.assertEqual(actions, [])
        self.assertIn('未找到匹配行', skips[0][1])
        # 退化：key_field 未命中但 alt_key 唯一命中 → 仍可定位（设计 §7.2）
        actions, skips = self._plan({'row': '不存在国'})
        self.assertEqual(len(actions), 1, skips)
        # 歧义：key_field 命中多行（重名行）
        t = self._target()
        rows = self._rows()
        rows[1]['country_zh'] = '伊朗'          # 与首行 country_zh 重复
        idx = self.mod.build_row_index(rows, t)
        fields = {'page': 'demos/countries-table.html', 'dataset': 'countries', 'row': '伊朗',
                  'row_en': 'Iran', 'field': 'pop_wan', 'current': '9157', 'suggested': '9200',
                  'source': 's', 'note': ''}
        real = self.mod.parse_issue_body          # HG-SEC-132: patch 时捕获，避免跨用例恢复失真
        self.mod.parse_issue_body = lambda body, pf: body
        try:
            actions, skips = self.mod.plan_issues(
                [{'number': 2, 'body': fields, 'createdAt': '2026-09-10T00:00:00Z'}], t, rows, idx)
        finally:
            self.mod.parse_issue_body = real
        self.assertEqual(actions, [], skips)
        self.assertIn('歧义', skips[0][1])

    def test_17_bad_number_and_idempotent(self):
        actions, skips = self._plan({'suggested': 'not-a-number'})
        self.assertEqual(actions, [])
        self.assertIn('无法解析', skips[0][1])
        actions, skips = self._plan({'suggested': '9157'})
        self.assertEqual(actions, [])
        self.assertIn('无变化', skips[0][1])

    def test_18_conflict_keeps_newest(self):
        t = self._target()
        rows = self._rows()
        idx = self.mod.build_row_index(rows, t)
        base = {'page': 'demos/countries-table.html', 'dataset': 'countries', 'row': '伊朗',
                'row_en': 'Iran', 'field': 'pop_wan', 'current': '9157', 'source': 's', 'note': ''}
        issues = [
            {'number': 10, 'body': dict(base, suggested='9200'), 'createdAt': '2026-09-10T00:00:00Z'},
            {'number': 11, 'body': dict(base, suggested='9300'), 'createdAt': '2026-09-10T01:00:00Z'},
        ]
        real = self.mod.parse_issue_body          # HG-SEC-132
        self.mod.parse_issue_body = lambda body, pf: body
        try:
            actions, skips = self.mod.plan_issues(issues, t, rows, idx)
        finally:
            self.mod.parse_issue_body = real
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0]['issue'], 11)
        self.assertEqual(actions[0]['new'], 9300)
        self.assertTrue(any('冲突' in s[1] for s in skips))

    # ── apply / dry-run / --issue ──
    def _tmp_project(self):
        """临时项目：data/d.json + cfg.yaml；返回 (tmp, data_path, cfg, doc)。"""
        tmp = Path(tempfile.mkdtemp(prefix='_tmp_issue_sync_'))
        (tmp / 'data').mkdir()
        doc = {'title': 't', 'columns': [{'key': 'country_zh', 'label': '国家'},
                                         {'key': 'pop_wan', 'label': '人口', 'type': 'number'}],
               'data': [{'country_zh': '伊朗', 'country_en': 'Iran', 'pop_wan': 9157}],
               'options': {'feedback': {'dataset': 'countries', 'key': 'country_zh',
                                        'altKey': 'country_en'}}}
        data_path = tmp / 'data' / 'd.json'
        data_path.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding='utf-8')
        cfg = tmp / 'cfg.yaml'
        cfg.write_text(json.dumps({'targets': {'countries': {
            'repo': 'o/r', 'label': 'data-fix', 'dataset': 'countries',
            'page': 'demos/countries-table.html', 'data': 'data/d.json',
            'html': 'demos/countries-table.html', 'key_field': 'country_zh',
            'alt_key': 'country_en', 'editable': ['pop_wan', 'note'],
            'protected': ['videos'], 'types': {'pop_wan': 'number'},
            'parse_fields': {'page': '页面', 'dataset': '数据集', 'row': '行标识',
                             'row_en': '行英文标识', 'field': '字段', 'current': '当前值',
                             'suggested': '建议值', 'source': '来源', 'note': '补充说明'},
            'rebuild': {'args': ['--feedback-repo', 'o/r']}}}}, ensure_ascii=False),
            encoding='utf-8')
        return tmp, data_path, cfg, doc

    def _run_main(self, tmp, cfg, argv):
        """在临时 PROJECT_ROOT 下运行 main，打桩 gh/rebuild/comment；返回 (rc, calls)。"""
        mod = self.mod
        saved = (mod.PROJECT_ROOT, mod.gh_issue_list, mod.rebuild, mod.gh_comment)
        calls = {}
        mod.PROJECT_ROOT = tmp
        mod.gh_issue_list = lambda repo, label, limit, issue_no=None: ([{
            'number': 7, 'title': 't', 'url': '', 'createdAt': '2026-09-10T00:00:00Z',
            'body': ISSUE_BODY, 'state': 'OPEN', 'labels': [{'name': 'data-fix'}]}], None)
        mod.rebuild = lambda target: (calls.__setitem__('rebuild', target), 0)[1]
        mod.gh_comment = lambda repo, no, body, close=False: (calls.__setitem__('comment', (no, close)), True)[1]
        try:
            rc = mod.main(['--config', str(cfg)] + argv)
        finally:
            mod.PROJECT_ROOT, mod.gh_issue_list, mod.rebuild, mod.gh_comment = saved
        return rc, calls

    def test_19_apply_roundtrip(self):
        tmp, data_path, cfg, doc = self._tmp_project()
        try:
            rc, calls = self._run_main(tmp, cfg, ['--apply'])
            self.assertEqual(rc, 0)
            new_raw = data_path.read_text(encoding='utf-8')
            self.assertFalse(new_raw.endswith('\n'), '不得新增尾换行')
            new_doc = json.loads(new_raw)
            self.assertEqual(new_doc['data'][0]['pop_wan'], 9200)
            self.assertEqual(new_doc['data'][0]['country_en'], 'Iran')       # 其余字段未动
            self.assertEqual(new_doc['options'], doc['options'])             # options 未动
            self.assertIn('rebuild', calls)
            self.assertEqual(calls['comment'][1], False)                     # 默认不关闭
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_20_dry_run_writes_nothing(self):
        """HG-SEC-120: 默认 --dry-run 零写盘且不触发重建/回评。"""
        tmp, data_path, cfg, _ = self._tmp_project()
        try:
            before = data_path.read_text(encoding='utf-8')
            rc, calls = self._run_main(tmp, cfg, [])
            self.assertEqual(rc, 0)
            self.assertEqual(data_path.read_text(encoding='utf-8'), before)
            self.assertNotIn('rebuild', calls)
            self.assertNotIn('comment', calls)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_21_issue_flag_direct_lookup(self):
        """HG-SEC-119: --issue N 走 gh issue view 直查，不使用无效的 in:number 搜索限定符。"""
        seen = []

        class _R:
            returncode = 0
            stderr = ''
            stdout = json.dumps({'number': 42, 'state': 'OPEN', 'labels': [{'name': 'data-fix'}],
                                 'title': 't', 'body': '', 'url': '', 'createdAt': ''})

        def fake_run(cmd, **kw):
            seen.append(list(cmd))
            return _R()

        real = self.mod.run
        self.mod.run = fake_run
        try:
            issues, err = self.mod.gh_issue_list('o/r', 'data-fix', 100, issue_no=42)
        finally:
            self.mod.run = real
        self.assertIsNone(err)
        self.assertEqual(len(issues), 1)
        self.assertEqual(seen[0][:3], ['gh', 'issue', 'view'])
        self.assertNotIn('--search', seen[0])

    def test_22_issue_flag_filters_state_and_label(self):
        """HG-SEC-119 口径：非 open 或缺 label 的 issue 不返回。"""
        class _R:
            returncode = 0
            stderr = ''

        real = self.mod.run
        for state, labels, expect in (('CLOSED', [{'name': 'data-fix'}], 0),
                                      ('OPEN', [{'name': 'other'}], 0),
                                      ('OPEN', [{'name': 'data-fix'}], 1)):
            _R.stdout = json.dumps({'number': 5, 'state': state, 'labels': labels,
                                    'title': 't', 'body': '', 'url': '', 'createdAt': ''})
            self.mod.run = lambda cmd, **kw: _R()
            try:
                issues, err = self.mod.gh_issue_list('o/r', 'data-fix', 100, issue_no=5)
            finally:
                self.mod.run = real
            self.assertIsNone(err)
            self.assertEqual(len(issues), expect, f'{state}/{labels}')
