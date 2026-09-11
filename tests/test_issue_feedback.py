"""HTML-GEN-CL009: A 型表格 GitHub Issue 反馈通道 — 渲染条件 + 同步脚本行为。

两部分:
1. TestFeedbackRender (Selenium): --feedback-repo 条件渲染、URL 预填参数、列上下文;
2. TestIssueSyncScript (纯 Python): issue body 解析 / 六类校验 / 冲突 / 幂等 / apply 往返。
"""
import contextlib
import importlib.util
import io
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
        'feedback': {'dataset': 'fixture', 'key': 'name', 'altKey': 'note',
                     'template': 'fx-form.yml'},
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
        self.assertIn('template=fx-form.yml', url)             # v1.3/M1: 模板名来自 options.feedback.template
        self.assertIn('dataset=fixture', url)
        self.assertIn('row=' + '%E4%BC%8A%E6%9C%97', url)      # 伊朗 URL 编码
        self.assertIn('row_en=' + '%E6%B3%A2%E6%96%AF%E5%B8%9D%E5%9B%BD', url)
        self.assertNotIn('field=', url)                        # v1.3/D1: 不再预填字段
        self.assertNotIn('current=', url)                      # v1.3/F2: 不再预填当前值

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

    def test_05_cell_click_does_not_prefill_field(self):
        """v1.3/D1: 点任意列（含 onCellClick='split'）→ URL 仍不含 field/current（字段由表单下拉选）。"""
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
        self.assertNotIn('field=', url)
        self.assertNotIn('current=', url)
        self.assertIn('row=', url)
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

    def _plan(self, fields_patch, created='2026-09-10T00:00:00Z', target=None):
        t = target or self._target()
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
        # v1.3: videos 不在 editable → resolve_field 判定「不可识别」；受保护列仍被拦截
        actions, skips = self._plan({'field': 'videos', 'current': '', 'suggested': 'x'})
        self.assertEqual(actions, [], 'videos')
        self.assertTrue(any('无法识别' in s[1] or '受保护列' in s[1] for s in skips), skips)
        actions, skips = self._plan({'field': 'nonexistent_col', 'current': '', 'suggested': 'x'})
        self.assertEqual(actions, [], 'nonexistent_col')
        self.assertIn('无法识别', skips[0][1])

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

    # ── v1.3：字段解析 / 主键保护 / 模板校验 ──
    def test_23_resolve_field_dual_form(self):
        """K1/O1/N1: `标签｜key` 取末段；裸 key 兼容；未知值报错；--field 覆盖优先。"""
        t = self._target()
        self.assertEqual(self.mod.resolve_field('备注｜note', t)[0], 'note')
        self.assertEqual(self.mod.resolve_field('大洲｜unknown｜region_tags', t)[0], 'region_tags')  # 末段规则
        self.assertEqual(self.mod.resolve_field('note', t)[0], 'note')           # 旧形态兼容
        self.assertIsNone(self.mod.resolve_field('', t)[0])
        self.assertIn('无法识别', self.mod.resolve_field('不存在｜nope', t)[1])
        self.assertEqual(self.mod.resolve_field('x', t, override='pop_wan')[0], 'pop_wan')

    def test_24_key_guard_rejects_pk(self):
        """A1: 主键/匹配键/视频列无论配置如何都被硬保护拒绝。"""
        t = self._target()
        guard = self.mod.guarded_fields(t)
        for k in ('country_zh', 'country_en', 'videos'):
            self.assertIn(k, guard, k)
        t2 = dict(t)
        t2['editable'] = list(t['editable']) + ['country_zh']       # 模拟配置误列
        actions, skips = self._plan({'field': 'country_zh', 'suggested': '阿尔及利亚'}, target=t2)
        self.assertEqual(actions, [], skips)
        self.assertIn('受保护列', skips[0][1])

    def test_25_unknown_dropdown_value(self):
        """O1: 未知名/未知选项 → 跳过并说明。"""
        actions, skips = self._plan({'field': '不存在列｜nope'})
        self.assertEqual(actions, [])
        self.assertIn('无法识别', skips[0][1])

    def test_26_multiline_value_preserved(self):
        """F2/I1: 多行建议值原样进入 action（换行保留）。"""
        text = '第一行\n第二行\n【民族】阿拉伯人'
        actions, skips = self._plan({'field': '备注｜note', 'suggested': text})
        self.assertEqual(len(actions), 1, skips)
        self.assertEqual(actions[0]['field'], 'note')
        self.assertEqual(actions[0]['new'], text)

    def test_27_human_override_requires_issue(self):
        """N1: --field/--value/--value-file 必须与 --issue 联用（否则 exit 2）。"""
        for argv in (['--field', 'note'], ['--value', 'x'], ['--value-file', '/tmp/nope']):
            self.assertEqual(self.mod.main(argv), 2, argv)

    def test_28_check_template_consistency(self):
        """L1: 模板 dropdown ↔ config.editable/数据标签 一致 → 0；篡改 → 1 + 差异。"""
        self.assertEqual(self.mod.main(['--check-template']), 0)
        tmp = Path(tempfile.mkdtemp(prefix='_tmp_tmpl_'))
        try:
            (tmp / '.github' / 'ISSUE_TEMPLATE').mkdir(parents=True)
            (tmp / 'data').mkdir()
            doc = {'columns': [{'key': 'pop_wan', 'label': '人口(万)'}]}
            (tmp / 'data' / 'd.json').write_text(json.dumps(doc, ensure_ascii=False), encoding='utf-8')
            (tmp / '.github' / 'ISSUE_TEMPLATE' / 'bad.yml').write_text(
                'body:\n  - type: dropdown\n    id: field\n    attributes:\n      options:\n'
                '        - 备注｜note\n        - 行标识｜country_zh\n', encoding='utf-8')
            t = dict(self._target())
            t['template'] = 'bad.yml'
            t['data'] = 'data/d.json'
            real = self.mod.PROJECT_ROOT
            self.mod.PROJECT_ROOT = tmp
            try:
                rc = self.mod.check_template(t)
            finally:
                self.mod.PROJECT_ROOT = real
            self.assertEqual(rc, 1)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_29_form_has_dropdown_no_current(self):
        """B1/F2: 表单字段为 dropdown(field) 且不含 current；parse_fields 保留 current 兼容 shim。"""
        cfg = self.mod.yaml.safe_load(
            (PROJECT / 'scripts' / 'feedback-targets.yaml').read_text(encoding='utf-8'))
        t = cfg['targets']['countries']
        tmpl = PROJECT / '.github' / 'ISSUE_TEMPLATE' / t['template']
        self.assertTrue(tmpl.is_file(), tmpl)
        doc = self.mod.yaml.safe_load(tmpl.read_text(encoding='utf-8'))
        ids, kinds = {}, {}
        for blk in doc['body']:
            if 'id' in blk:
                ids[blk['id']] = blk
                kinds[blk['id']] = blk['type']
        self.assertEqual(kinds.get('field'), 'dropdown')
        self.assertEqual(kinds.get('suggested'), 'textarea')
        self.assertNotIn('current', ids)                       # F2
        opts = ids['field']['attributes']['options']
        self.assertEqual([o.rpartition('｜')[2].strip() for o in opts], t['editable'])
        self.assertEqual(t['parse_fields'].get('current'), '当前值')   # 旧 issue 兼容 shim

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

    def _run_main(self, tmp, cfg, argv, dirty=None, commit=None):
        """在临时 PROJECT_ROOT 下运行 main，打桩 gh/rebuild/comment/git；返回 (rc, calls)。"""
        mod = self.mod
        saved = (mod.PROJECT_ROOT, mod.gh_issue_list, mod.rebuild, mod.gh_comment,
                 mod.git_dirty, mod.git_commit)
        calls = {}
        mod.PROJECT_ROOT = tmp
        mod.gh_issue_list = lambda repo, label, limit, issue_no=None: ([{
            'number': 7, 'title': 't', 'url': '', 'createdAt': '2026-09-10T00:00:00Z',
            'body': ISSUE_BODY, 'state': 'OPEN', 'labels': [{'name': 'data-fix'}]}], None)
        mod.rebuild = lambda target: (calls.__setitem__('rebuild', target), 0)[1]
        mod.gh_comment = lambda repo, no, body, close=False: (
            calls.__setitem__('comment', (no, close)), calls.__setitem__('comment_body', body), True)[2]
        mod.git_dirty = dirty if dirty is not None else (
            lambda paths: (calls.__setitem__('dirty_paths', list(paths)), ([], None))[1])
        mod.git_commit = commit if commit is not None else (
            lambda target, title, body, paths: (
                calls.__setitem__('commit', (title, body, list(paths))), ('abc1234', None))[1])
        try:
            rc = mod.main(['--config', str(cfg)] + argv)
        finally:
            (mod.PROJECT_ROOT, mod.gh_issue_list, mod.rebuild, mod.gh_comment,
             mod.git_dirty, mod.git_commit) = saved
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

    # ── v1.4 新增：--apply 自动提交（A1/B1/D1/E1/F1/G1/H1）+ --list 引导行（O1/Q1/M1） ──
    def test_30_git_commit_pathspec_only(self):
        """B1/H1: 真实 git —— 提交只含数据文件与产物；其它脏文件不被裹走；无变化→no-change。"""
        tmp = Path(tempfile.mkdtemp(prefix='_tmp_git_'))
        real_root = self.mod.PROJECT_ROOT
        try:
            for c in (['git', 'init', '-q'], ['git', 'config', 'user.email', 't@t.t'],
                      ['git', 'config', 'user.name', 't']):
                subprocess.run(c, cwd=tmp, check=True)
            (tmp / 'data').mkdir()
            (tmp / 'demos').mkdir()
            (tmp / 'data' / 'd.json').write_text('{"a":1}', encoding='utf-8')
            (tmp / 'demos' / 'x.html').write_text('<html>1</html>', encoding='utf-8')
            (tmp / 'other.txt').write_text('v1', encoding='utf-8')
            subprocess.run(['git', 'add', '-A'], cwd=tmp, check=True)
            subprocess.run(['git', 'commit', '-qm', 'init'], cwd=tmp, check=True)
            # 三处都改
            for rel, val in (('data/d.json', '{"a":2}'), ('demos/x.html', '<html>2</html>'),
                             ('other.txt', 'v2')):
                (tmp / rel).write_text(val, encoding='utf-8')
            target = {'data': 'data/d.json', 'html': 'demos/x.html'}
            self.assertEqual(self.mod.git_paths(target), ['data/d.json', 'demos/x.html'])
            self.mod.PROJECT_ROOT = tmp
            sha, err = self.mod.git_commit(target, 'title', 'body', self.mod.git_paths(target))
            self.assertIsNone(err)
            self.assertTrue(sha)
            shown = subprocess.run(['git', 'show', '--name-only', '--pretty=format:', 'HEAD'],
                                   cwd=tmp, capture_output=True, text=True).stdout
            self.assertEqual(sorted(x for x in shown.splitlines() if x.strip()),
                             ['data/d.json', 'demos/x.html'])
            st = subprocess.run(['git', 'status', '--porcelain'], cwd=tmp,
                                capture_output=True, text=True).stdout
            self.assertIn('other.txt', st, '未列入 pathspec 的脏文件不得被提交')
            # HG-SEC-140 回归：并行会话已暂存(index)的无关文件也不得被 commit 裹走
            (tmp / 'staged.txt').write_text('s1', encoding='utf-8')
            subprocess.run(['git', 'add', 'staged.txt'], cwd=tmp, check=True)
            (tmp / 'data' / 'd.json').write_text('{"a":3}', encoding='utf-8')
            self.mod.PROJECT_ROOT = tmp
            sha3, err3 = self.mod.git_commit(target, 't3', 'b3', self.mod.git_paths(target))
            self.assertIsNone(err3)
            shown3 = subprocess.run(['git', 'show', '--name-only', '--pretty=format:', 'HEAD'],
                                    cwd=tmp, capture_output=True, text=True).stdout
            self.assertEqual(sorted(x for x in shown3.splitlines() if x.strip()), ['data/d.json'])
            st3 = subprocess.run(['git', 'status', '--porcelain'], cwd=tmp,
                                 capture_output=True, text=True).stdout
            self.assertIn('A  staged.txt', st3, '已暂存的无关文件应仍留在 index')
            # 目标文件干净 → 预检通过（其它文件脏不影响）
            d, e = self.mod.git_dirty(self.mod.git_paths(target))
            self.assertEqual(d, [])
            self.assertIsNone(e)
            # 无变化 → no-change（不空提交）
            sha2, err2 = self.mod.git_commit(target, 't2', 'b2', self.mod.git_paths(target))
            self.assertIsNone(sha2)
            self.assertEqual(err2, 'no-change')
        finally:
            self.mod.PROJECT_ROOT = real_root
            shutil.rmtree(tmp, ignore_errors=True)

    def test_31_apply_commits_and_comment_has_sha(self):
        """A1/F1: apply 默认提交（显式 pathspec 两文件），回评含本地短 sha（待推送）。"""
        tmp, data_path, cfg, _ = self._tmp_project()
        try:
            rc, calls = self._run_main(tmp, cfg, ['--apply'])
            self.assertEqual(rc, 0)
            self.assertIn('commit', calls)
            title, body, paths = calls['commit']
            self.assertEqual(paths, ['data/d.json', 'demos/countries-table.html'])
            self.assertIn('本地提交 `abc1234`（待推送）', calls['comment_body'])
            self.assertNotIn('提交由维护者完成', calls['comment_body'])
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_32_apply_commit_message_format(self):
        """D1/E1: 标题 data@<scope>: apply #N <fields> 更新 (HTML-GEN-CL009)；body 逐条列旧→新。"""
        tmp, data_path, cfg, _ = self._tmp_project()
        try:
            rc, calls = self._run_main(tmp, cfg, ['--apply'])
            self.assertEqual(rc, 0)
            title, body, _ = calls['commit']
            self.assertEqual(title, 'data@countries: apply #7 pop_wan 更新 (HTML-GEN-CL009)')
            self.assertIn('#7 伊朗.pop_wan:', body)
            self.assertIn('→ 9200', body)
            self.assertIn('demos/countries-table.html', body)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_33_no_commit_flag(self):
        """A1: --no-commit 不提交，回评注明由维护者完成。"""
        tmp, data_path, cfg, _ = self._tmp_project()
        try:
            rc, calls = self._run_main(tmp, cfg, ['--apply', '--no-commit'])
            self.assertEqual(rc, 0)
            self.assertNotIn('commit', calls)
            self.assertNotIn('dirty_paths', calls, '--no-commit 时不做预检')
            self.assertIn('--no-commit', calls['comment_body'])
            self.assertEqual(json.loads(data_path.read_text(encoding='utf-8'))['data'][0]['pop_wan'], 9200)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_34_dirty_preflight_rejects_before_write(self):
        """C1: 目标文件脏 → 写盘前拒绝（exit 1），数据/产物/提交均不动。"""
        tmp, data_path, cfg, _ = self._tmp_project()
        try:
            before = data_path.read_text(encoding='utf-8')
            rc, calls = self._run_main(tmp, cfg, ['--apply'],
                                       dirty=lambda paths: ([' M data/d.json'], None))
            self.assertEqual(rc, 1)
            self.assertEqual(data_path.read_text(encoding='utf-8'), before)
            self.assertNotIn('rebuild', calls)
            self.assertNotIn('commit', calls)
            self.assertNotIn('comment', calls)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_35_dry_run_and_list_never_commit(self):
        """I1: dry-run / --list 恒不提交、不预检。"""
        tmp, data_path, cfg, _ = self._tmp_project()
        try:
            for argv in ([], ['--list']):
                rc, calls = self._run_main(tmp, cfg, argv)
                self.assertEqual(rc, 0, argv)
                self.assertNotIn('commit', calls, argv)
                self.assertNotIn('dirty_paths', calls, argv)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_36_no_change_skips_commit(self):
        """H1: 无文件变化 → 不产生空提交，回评注明未产生提交。"""
        tmp, data_path, cfg, _ = self._tmp_project()
        try:
            rc, calls = self._run_main(tmp, cfg, ['--apply'],
                                       commit=lambda target, t, b, paths: (None, 'no-change'))
            self.assertEqual(rc, 0)
            self.assertIn('本次无文件变化，未产生提交', calls['comment_body'])
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_37_commit_failure_exit1_and_comment(self):
        """G1: 提交失败不回滚、回评注明待维护者处理、exit 1。"""
        tmp, data_path, cfg, _ = self._tmp_project()
        try:
            rc, calls = self._run_main(tmp, cfg, ['--apply'],
                                       commit=lambda target, t, b, paths: (None, 'git commit 失败: x'))
            self.assertEqual(rc, 1)
            self.assertIn('提交失败，待维护者处理', calls['comment_body'])
            self.assertEqual(json.loads(data_path.read_text(encoding='utf-8'))['data'][0]['pop_wan'], 9200)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_38_list_hint_lines(self):
        """O1/Q1/M1: --list 每条 issue 后跟 python3 引导行（可执行 + 跳过各一条）。"""
        tmp, data_path, cfg, _ = self._tmp_project()
        try:
            mod = self.mod
            saved = (mod.PROJECT_ROOT, mod.gh_issue_list, mod.rebuild, mod.gh_comment)
            mod.PROJECT_ROOT = tmp
            mod.gh_issue_list = lambda repo, label, limit, issue_no=None: ([
                {'number': 7, 'title': 't', 'url': '', 'createdAt': '2026-09-10T00:00:00Z',
                 'body': ISSUE_BODY, 'state': 'OPEN', 'labels': [{'name': 'data-fix'}]},
                {'number': 8, 'title': 't', 'url': '', 'createdAt': '2026-09-10T00:00:00Z',
                 'body': '### 页面\n\ndemos/countries-table.html\n\n### 字段\n\ncountry_zh\n\n'
                         '### 建议值\n\nX\n', 'state': 'OPEN', 'labels': [{'name': 'data-fix'}]}], None)
            mod.rebuild = lambda target: 0
            mod.gh_comment = lambda *a, **k: True
            buf = io.StringIO()
            try:
                with contextlib.redirect_stdout(buf):
                    rc = mod.main(['--config', str(cfg), '--list'])
            finally:
                (mod.PROJECT_ROOT, mod.gh_issue_list, mod.rebuild, mod.gh_comment) = saved
            out = buf.getvalue()
            self.assertEqual(rc, 0)
            self.assertIn('  #7 ', out)
            self.assertIn('     → python3 scripts/countries-issue-sync.py --issue 7 --dry-run', out)
            self.assertIn('#8 [跳过]', out)
            self.assertIn('     → python3 scripts/countries-issue-sync.py --issue 8 --dry-run', out)
            self.assertNotIn('/usr/bin/python3', out)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_39_json_has_no_hint(self):
        """P1: --json 结构不变、无引导行/无 hint 字段。"""
        tmp, data_path, cfg, _ = self._tmp_project()
        try:
            mod = self.mod
            saved = (mod.PROJECT_ROOT, mod.gh_issue_list, mod.rebuild, mod.gh_comment)
            mod.PROJECT_ROOT = tmp
            mod.gh_issue_list = lambda repo, label, limit, issue_no=None: ([{
                'number': 7, 'title': 't', 'url': '', 'createdAt': '2026-09-10T00:00:00Z',
                'body': ISSUE_BODY, 'state': 'OPEN', 'labels': [{'name': 'data-fix'}]}], None)
            mod.rebuild = lambda target: 0
            mod.gh_comment = lambda *a, **k: True
            buf = io.StringIO()
            try:
                with contextlib.redirect_stdout(buf):
                    rc = mod.main(['--config', str(cfg), '--list', '--json'])
            finally:
                (mod.PROJECT_ROOT, mod.gh_issue_list, mod.rebuild, mod.gh_comment) = saved
            out = buf.getvalue()
            self.assertEqual(rc, 0)
            data = json.loads(out)
            self.assertEqual(sorted(data['data'].keys()), ['actions', 'skipped'])
            self.assertNotIn('→', out)
            self.assertNotIn('hint', out)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
