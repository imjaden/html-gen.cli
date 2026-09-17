"""CL012 守卫测试: help 契约 ⇄ 模板实际消费 ⇄ help 渲染 三维双向闭合 (table 维度)。

① 模板消费键 ⊆ 契约键        (template → contract)
② 契约键 ⊆ render_help 输出  (contract → help)
③ help 键规范段键 ⊆ 契约键   (help → contract)

doc/slide/knowledge 的维度断言在 CL013 启用 (契约中仍是骨架节点)。
失败信息必须指名「哪个键 / 来源文件 / 修复动作」。
"""
import json
import re
import subprocess
import tempfile
import unittest
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GEN = ROOT / 'html-gen.py'
TABLE_TMPL_NAME = 'layout-table.html'
TABLE_TMPL = ROOT / TABLE_TMPL_NAME


def _load_gen():
    spec = spec_from_file_location('html_gen_contract', GEN)
    assert spec is not None and spec.loader is not None
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


HG = _load_gen()
NODE = HG.TEMPLATE_CONTRACT['table']
HELP_TEXT = HG.render_help('table')
SPEC_TEXT = HG.render_help_spec('table')
TMPL_TEXT = TABLE_TMPL.read_text(encoding='utf-8')


def dim_keys(dim):
    """契约某维度的键集合 (契约是唯一枚举键名的地方)。"""
    return {e[0] for e in NODE['data'][dim]}


def all_contract_keys():
    """契约声明的全部键名 (各维度条目 ∪ 行为名)。"""
    keys = set()
    for entries in NODE['data'].values():
        keys |= {e[0] for e in entries}
    keys |= {e[0] for e in NODE['url_state']}
    keys |= {e[0] for e in NODE['behaviors']}
    return keys


def extract(pattern, text=TMPL_TEXT, flags=0):
    """按维度正则提取模板实际消费的标识符 (调用形式可用 (?!\\s*\\() 排除原生方法)。"""
    return set(re.findall(pattern, text, flags))


def no_call(pattern):
    """排除 `x.name(` 调用形式与词元截断 — 原生方法/prototype 调用不是配置键。

    `(?!\\s*\\()` 不够: `v.split(` 会回溯成 `v.spli` 而"通过"; 用 `(?![\\w(])` 直接
    否掉"后接词元字符或左括号"的匹配, 杜绝部分回溯。
    """
    return pattern + r'(?![\w(])'


# ── 白名单 (仅可排除正则误捕的非配置项; 实测全部维度为空) ──────────────────────
# 契约: 每项须注释理由 + 反向断言 (test_10 断言白名单项确实不是契约键);
# 长度趋近 0, 超 3 项须在注释说明原因。当前 0 项 —— 实测 layout-table.html 中
# col./c./OPTIONS./FB_CFG. 均无原生方法或局部变量误捕 (map/find/filter/sort 走大写
# COLUMNS.*, 视频/动作项字段用 (?!\s*\() 排除 v.split(/videos.map( 等调用形式)。
WHITELIST = {
    'columns': set(),
    'options': set(),
    'feedback': set(),
    'column_types': set(),
    'tabs': set(),
    'actions': set(),
    'videos': set(),
}

# 维度 → (提取正则列表, 契约维度, 修复动作)
DIMENSIONS = {
    'columns': ([r'\b(?:col|c)\.([a-zA-Z_]\w*)'], 'columns',
                '在 TEMPLATE_CONTRACT["table"]["data"]["columns"] 补该键 (或确认白名单理由)'),
    'options': ([r'OPTIONS\.([a-zA-Z_]\w*)'], 'options',
                '在 TEMPLATE_CONTRACT["table"]["data"]["options"] 补该键'),
    'feedback': ([r'FB_CFG\s*&&\s*FB_CFG\.([a-zA-Z_]\w*)', r'(?<![\w.])FB_CFG\.([a-zA-Z_]\w*)'], 'feedback',
                 '在 TEMPLATE_CONTRACT["table"]["data"]["feedback"] 补该键'),
    'tabs': ([r'\btab\.([a-zA-Z_]\w*)', r'\bt\.(key|label|field|match|contains|value)\b'], 'tabs',
             '在 TEMPLATE_CONTRACT["table"]["data"]["tabs"] 补该键 (t.key/t.label 为 tab 局部变量简写)'),
    'actions': ([no_call(r'\bact\.([a-zA-Z_]\w*)')], 'actions',
                '在 TEMPLATE_CONTRACT["table"]["data"]["actions"] 补该键'),
    'videos': ([r'col\.videos\.([a-zA-Z_]\w*)', no_call(r'\bv\.([a-zA-Z_]\w*)')], 'videos',
               '在 TEMPLATE_CONTRACT["table"]["data"]["videos"] 补该键 (v.* 为视频项字段)'),
}


class TestHelpContract(unittest.TestCase):
    """契约 ⇄ 模板 ⇄ help 三维双向断言 (CL012: 仅 table)。"""

    # ── 结构 ──────────────────────────────────────────────────────────────
    def test_01_contract_shape(self):
        """契约四模板节点齐备; table 节点含 label/tagline/cli/data/section_order/url_state/behaviors。"""
        self.assertEqual(sorted(HG.TEMPLATE_CONTRACT), ['doc', 'knowledge', 'slide', 'table'],
                         '契约应含四模板节点')
        for field in ('label', 'tagline', 'cli', 'data', 'section_order', 'url_state', 'behaviors'):
            self.assertIn(field, NODE, f'契约 table 节点缺字段: {field}')
        for dim, entries in NODE['data'].items():
            self.assertTrue(entries, f'契约维度 {dim} 不应为空')
            for e in entries:
                self.assertEqual(len(e), 3, f'{dim} 条目应为 (键, 说明, 默认) 三元组: {e!r}')

    # ── ① 模板消费 → 契约 ────────────────────────────────────────────────
    def test_02_template_column_attrs_subset_of_contract(self):
        """列属性: col./c. 消费键 ⊆ 契约 columns (22 项)。"""
        self._assert_dim('columns')

    def test_03_template_options_subset_of_contract(self):
        """options 顶层: OPTIONS. 消费键 ⊆ 契约 options (13 项)。"""
        self._assert_dim('options')

    def test_04_template_feedback_subset_of_contract(self):
        """options.feedback 子键: FB_CFG. 消费键 ⊆ 契约 feedback (5 项)。"""
        self._assert_dim('feedback')

    def test_05_template_column_types_equal_contract(self):
        """列类型: 模板显式 .type === '...' 分支 ∪ {默认 string} == 契约 6 类。"""
        explicit = extract(r"\.type\s*===\s*'([a-z]+)'")
        consumed = explicit | {'string'}          # 模板无 'string' 分支, 默认值以常量注入
        contract = dim_keys('column_types')
        self.assertEqual(consumed, contract,
                         f'列类型不一致 — 模板分支 {sorted(explicit)} ∪ {{string}} = {sorted(consumed)}, '
                         f'契约 {sorted(contract)}; 来源 {TABLE_TMPL_NAME}; '
                         f'修复: 以模板渲染分支为准更新 TEMPLATE_CONTRACT["table"]["data"]["column_types"]')
        self.assertNotIn('string', explicit,
                         f'模板出现显式 .type === \'string\' 分支时须改为显式提取 (当前默认值注入) — 来源 {TABLE_TMPL_NAME}')

    def test_06_template_tabs_subset_of_contract(self):
        """tabs 键: tab.* 与 t.key/t.label 简写消费键 ⊆ 契约 tabs (6 项)。"""
        self._assert_dim('tabs')

    def test_07_template_nested_subset_of_contract(self):
        """嵌套子键: act.* (actions 项) 与 col.videos.*/v.* (videos 配置与项字段) ⊆ 契约。"""
        self._assert_dim('actions')
        self._assert_dim('videos')

    # ── ② 契约 → help ────────────────────────────────────────────────────
    def test_08_contract_keys_present_in_help(self):
        """契约每个键都出现在 render_help('table') 输出 (词边界匹配, 防 clickMode ⊂ clickModes 假阳性)。"""
        missing = []
        for dim, entries in NODE['data'].items():
            for key, desc, default in entries:
                if not self._key_in_help(key):
                    missing.append(f'{dim}.{key} (说明: {desc!r})')
        for key, *_ in NODE['url_state']:
            if key not in HELP_TEXT:
                missing.append(f'url_state.{key}')
        for key, *_ in NODE['behaviors']:
            if not re.search(rf'\b{re.escape(key)}\b', HELP_TEXT):
                missing.append(f'behaviors.{key}')
        self.assertFalse(missing,
                         f'契约键未出现在 html-gen help table 输出: {missing}; '
                         f'修复: 检查 TEMPLATE_CONTRACT["table"] 对应条目是否被 render_help_spec 渲染')

    # ── ③ help → 契约 ────────────────────────────────────────────────────
    def test_09_help_spec_keys_subset_of_contract(self):
        """键规范段渲染出的 `key:` 词元 ⊆ 契约键 (help 不得出现契约未声明的键)。"""
        tokens = set(re.findall(r'(?:^|\s/\s)\s*([a-zA-Z_]\w*)\s*:', SPEC_TEXT, re.M))
        extra = tokens - all_contract_keys()
        self.assertFalse(extra,
                         f'help 键规范段出现契约未声明的键 {sorted(extra)}; 来源 render_help_spec("table"); '
                         f'修复: 或在契约中声明该键, 或修正 TEMPLATE_CONTRACT 中该条目的说明文本')
        self.assertTrue(tokens, '键规范段未提取到任何键 — 渲染格式可能已变 (期望 `key: 说明` 行式排版)')

    # ── 白名单纪律 ───────────────────────────────────────────────────────
    def test_10_whitelist_discipline(self):
        """白名单项必须确实不是契约键 (反向断言); 每维度 ≤3 项。"""
        contract = all_contract_keys()
        for dim, wl in WHITELIST.items():
            self.assertLessEqual(len(wl), 3,
                                 f'{dim} 白名单 {sorted(wl)} 超 3 项, 须在测试注释说明原因')
            for item in wl:
                self.assertNotIn(item, contract,
                                 f'{dim} 白名单项 {item} 是真实契约键 — 不得用白名单排除真实键, '
                                 f'应在契约中声明')

    # ── 渲染观感与语义 ───────────────────────────────────────────────────
    def test_11_render_help_style_and_semantics(self):
        """渲染观感 (banner/分隔线/2 空格缩进/示例段注记) 与 4 项关键语义文本。"""
        lines = HELP_TEXT.splitlines()
        self.assertEqual(lines[0], f"{NODE['label']} ({NODE['tagline']})", '首行应为 label (tagline)')
        self.assertEqual(lines[1], '━' * NODE['rule'], '第二行应为契约 rule 指定的分隔线')
        self.assertIn('示例', lines[3] if len(lines) > 3 else '', '② 示例段段首应标注「示例」口径')
        for entry_line in (l for l in lines if re.match(r'^\s{2}\w+:', l)):
            self.assertTrue(entry_line.startswith('  '), f'键规范条目应两空格缩进: {entry_line!r}')
        for must in ('永不可见',                    # hide 语义
                     '分栏详情仍全列渲染',           # initialHidden 语义 (与 hide 可辨)
                     '默认开启',                    # escape 自 CL010 起默认开启
                     '分栏表只显 preview 列',        # preview 规则
                     '100px',                      # width 默认 (actions 列)
                     'data-fix.yml'):               # feedback.template 默认
            self.assertIn(must, HELP_TEXT, f'help table 缺关键语义文本: {must}')
        for key, default in (('width', '120px'), ('search', 'true'), ('showIndex', 'false'),
                             ('columnResize', 'true'), ('pageSize', '30'), ('maxShow', '3')):
            self.assertRegex(HELP_TEXT, rf'\b{key}\b[^\n]*默认: {re.escape(default)}',
                             f'{key} 默认值 {default} 未在 help 中标注')

    def test_12_skeleton_topics_consistent(self):
        """骨架节点 (doc/slide/knowledge): 渲染 = 现况文案常量, label/rule 与文案自身一致。"""
        for topic, const in (('doc', 'HELP_DOC'), ('slide', 'HELP_SLIDE'), ('knowledge', 'HELP_KNOWLEDGE')):
            node = HG.TEMPLATE_CONTRACT[topic]
            self.assertTrue(node.get('legacy'), f'{topic} 骨架节点应有 legacy 常量指针')
            text = HG.render_help(topic)
            self.assertEqual(text, getattr(HG, const),
                             f'{topic} 渲染应与现况常量 {const} 一致 (CL012 不补维度)')
            first = text.splitlines()[0]
            expect = node['label'] + (f" ({node['tagline']})" if node.get('tagline') else '')
            self.assertEqual(first, expect, f'{topic} 契约 label 与文案首行不一致')
            self.assertTrue(text.splitlines()[1].startswith('━'), f'{topic} 文案第二行应为分隔线')
        topics = [k for k, _ in HG._help_topics()]
        for topic in list(HG.TEMPLATE_CONTRACT) + ['prompt', 'demo']:
            self.assertIn(topic, topics, f'HELP_OVERVIEW 主题清单漏列 {topic}')

    # ── 未知键 warn (R3) ─────────────────────────────────────────────────
    def test_13_unknown_keys_warn_on_stderr(self):
        """未知列属性/列类型/选项/反馈子键 → stderr 提示, 不阻断 (exit 0), 不污染 stdout。"""
        cases = [
            ({'columns': [{'key': 'a', 'label': 'A', 'bogusKey': 1}], 'data': [{'a': 1}]}, 'bogusKey'),
            ({'columns': [{'key': 'a', 'label': 'A', 'type': 'nope'}], 'data': [{'a': 1}]}, '未知列类型'),
            ({'columns': [{'key': 'a', 'label': 'A'}], 'data': [{'a': 1}],
              'options': {'nope': True}}, '未知选项'),
            ({'columns': [{'key': 'a', 'label': 'A'}], 'data': [{'a': 1}],
              'options': {'feedback': {'repo': 'o/r', 'nope': 1}}}, '未知反馈子键'),
        ]
        for payload, token in cases:
            with self.subTest(payload=payload):
                out = self._run_table(payload)
                self.assertEqual(out.returncode, 0, f'未知键不应阻断: {out.stderr}')
                self.assertIn('未知', out.stderr, f'stderr 应提示未知键: {out.stderr}')
                self.assertIn(token, out.stderr, f'stderr 应指名 {token}')
                self.assertIn('help table', out.stderr, 'stderr 应指向 html-gen help table')
                self.assertNotIn('未知', out.stdout, '未知键提示不得污染 stdout')

    def test_14_no_false_positive_warn(self):
        """不误报: 简单数组推导列名 / data[] 行内字段 / render-hander 值。"""
        cases = [
            ([{'任意字段名': 1, '另一个': 2}], '简单数组推导列名'),
            ({'data': [{'任意字段名': 1, 'biz_field': 2}]}, 'data[] 行内字段名 (无 columns 推导)'),
            ({'columns': [{'key': 'a', 'label': 'A', 'render': 'myRenderer', 'actions': [
                {'label': 'x', 'handler': 'myHandler', 'copyKey': 'a'}]}],
              'data': [{'a': 1}], 'options': {'feedback': {'repo': 'o/r', 'key': 'name'}}},
             'render/handler 是值不是键 + 合法嵌套'),
        ]
        for payload, why in cases:
            with self.subTest(why=why):
                out = self._run_table(payload)
                self.assertEqual(out.returncode, 0, out.stderr)
                self.assertNotIn('未知', out.stderr, f'{why} 不应触发未知键提示: {out.stderr}')

    # ── helpers ──────────────────────────────────────────────────────────
    def _assert_dim(self, dim):
        patterns, contract_dim, fix = DIMENSIONS[dim]
        consumed = set()
        for pat in patterns:
            consumed |= extract(pat)
        consumed -= WHITELIST[dim]
        contract = dim_keys(contract_dim)
        extra = consumed - contract
        self.assertFalse(
            extra,
            f'{dim}: 模板消费但契约未声明的键 {sorted(extra)} — 来源 {TABLE_TMPL_NAME}; 修复: {fix}')
        self.assertTrue(consumed, f'{dim}: 未从 {TABLE_TMPL_NAME} 提取到任何键 — 提取正则可能已失效')

    def _key_in_help(self, key):
        if re.match(r'^\W', key):                 # ?tab/?q/?split 等带前缀的 URL 状态键
            return key in HELP_TEXT
        return bool(re.search(rf'\b{re.escape(key)}\b', HELP_TEXT))

    def _run_table(self, payload):
        """写临时 JSON 跑 html-gen table, 返回 CompletedProcess。"""
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / 'in.json'
            src.write_text(json.dumps(payload, ensure_ascii=False), encoding='utf-8')
            return subprocess.run(['python3', str(GEN), 'table', '-d', str(src), '-o', str(Path(td) / 'o.html')],
                                  capture_output=True, text=True, timeout=60)


if __name__ == '__main__':
    unittest.main()
