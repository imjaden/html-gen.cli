"""CL012/CL013 守卫测试: help 契约 ⇄ 模板实际消费 ⇄ help 渲染 三维双向闭合。

① 模板消费键 ⊆ 契约键        (template → contract)
② 契约键 ⊆ render_help 输出  (contract → help)
③ help 键规范段键 ⊆ 契约键   (help → contract)

CL012: table 六维度断言全量; CL013: doc/slide/knowledge 维度断言接入
(三模板契约骨架 'legacy' 指针已删, help 由契约渲染)。
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

# 主题 → 模板文件 (契约维度的「模板消费」来源)
TOPIC_TMPL = {
    'table': TABLE_TMPL,
    'doc': ROOT / 'layout-doc.html',
    'slide': ROOT / 'layout-slide.html',
    'knowledge': ROOT / 'layout-knowledge.html',
}

# 词元口径 (HG-SEC-177): 只在 ① 键规范段内取「行首或 ' / ' 分隔符后的 词元 + 冒号」,
# **不得**退化为全文词边界匹配 (会被 ② 手写示例段的 JSON 或通用英文词骗过)。
# 形态覆盖: `?tab` (URL 状态) / `{items|data}` (数据源别名)。起始字符必须是 ASCII 标识符或
# `{`(可选 `?`) —— 中文章节标题 (如「列属性:」「交互行为:」) 与中文键名 (「数组:」) **不**入词元集,
# 否则标题本身会被当成键 (假阳性); 这类键的渲染由 spec_renders_key() 字面量口径覆盖。
KEY_TOKEN_RE = r'(?:^|\s/\s)\s*(\{?\??[a-zA-Z_]\w*(?:\|[a-zA-Z_]\w*)?\}?)\s*:'


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
_GEN_SRC = GEN.read_text(encoding='utf-8')


def spec_text(topic):
    """① 键规范段 (契约渲染) 文本 (含 behaviors 段)。"""
    return HG.render_help_spec(topic)


def tmpl_text(topic):
    """模板文本 (按主题)。"""
    return TOPIC_TMPL[topic].read_text(encoding='utf-8')


def dim_keys(dim, topic='table'):
    """契约某维度的键集合 (data 分区优先, 其次节点顶层; 契约是唯一枚举键名的地方)。"""
    return {e[0] for e in _dim_entries(dim, topic)}


def _dim_entries(dim, topic='table'):
    node = HG.TEMPLATE_CONTRACT[topic]
    data = node.get('data') or {}
    return data[dim] if dim in data else (node.get(dim) or [])


def all_contract_keys(topic='table'):
    """契约声明的全部键名 (data 各维度 ∪ url_state ∪ cli ∪ behaviors)。"""
    node = HG.TEMPLATE_CONTRACT[topic]
    keys = set()
    for entries in (node.get('data') or {}).values():
        keys |= {e[0] for e in entries}
    keys |= {e[0] for e in node.get('url_state') or []}
    keys |= {e[0] for e in node.get('cli') or []}
    keys |= {e[0] for e in node.get('behaviors') or []}
    return keys


def spec_key_tokens(topic='table'):
    """① 键规范段 (render_help_spec) 渲染出的 `key:` 词元集合 (含 `?tab` / `{items|data}` 等带前缀键)。

    test_08 (契约→help) 与 test_09/23 (help→契约) 必须共用同一提取口径 ——
    否则某一方向的假阴性会掩盖另一方向 (HG-SEC-177)。
    """
    return set(re.findall(KEY_TOKEN_RE, spec_text(topic), re.M))


def extract(pattern, text=TMPL_TEXT, flags=0):
    """按维度正则提取模板实际消费的标识符 (调用形式可用 no_call() 排除原生方法)。"""
    return set(re.findall(pattern, text, flags))


def spec_renders_key(topic, key):
    """① 键规范段是否渲染出该键 (行首或 ` / ` 分隔符后的 `key:` 字面量, re.M 锚定)。

    只扫 ① 段、不扫 ② 示例段: 示例 JSON 里同样有 `--output` 之类字面量, 全文匹配会
    掩盖「键规范段漏渲染」(HG-SEC-177 同类假阴性)。
    非标识符键 (CLI flag `--data`、中文键「数组」、别名 `{items|data}`) 不走
    spec_key_tokens() 的词元口径 (词元正则只收 ASCII 标识符形态), 但锚定强度一致。
    """
    return re.search(rf'(?:^|\s/\s)\s*{re.escape(key)}\s*:', spec_text(topic), re.M) is not None


def spec_renders_behavior(topic, key):
    """① 段 behaviors 段是否渲染出该行为 (行首 `key … — 说明` 形态)。"""
    return re.search(rf'^\s*{re.escape(key)}\s+—', spec_text(topic), re.M) is not None


def no_call(pattern):
    """排除 `x.name(` 调用形式与词元截断 — 原生方法/prototype 调用不是配置键。

    `(?!\\s*\\()` 不够: `v.split(` 会回溯成 `v.spli` 而"通过"; 用 `(?![\\w(])` 直接
    否掉"后接词元字符或左括号"的匹配, 杜绝部分回溯。
    """
    return pattern + r'(?![\w(])'


def cli_flags(cmd):
    """子命令的长形 flag 集合 (按 `sub.add_parser('<cmd>')` 块切分)。

    HG-SEC-168: **勿**用 `X\\.add_argument\\('--'` 形态 —— 短形在前的调用
    (`-i/--input`、`-o/--output`、`-d/--data`、`-g/--groups`) 会被漏捕。
    短形 (`-i/-o/-d/-g`) 是别名 ⇒ 不计键 (写进条目说明)。
    块边界 = 本子命令的 add_parser 之后、**下一个** add_parser 之前 (不可一直扫到文件尾,
    否则 prompt/demo 的 flag 会串味到前面的模板)。
    """
    head = rf"\n    [a-z]+ = sub\.add_parser\('{cmd}'"
    hits = re.findall(head, _GEN_SRC)
    assert len(hits) == 1, (f'未唯一定位 html-gen.py 的 {cmd} 子命令块 (实得 {len(hits)} 处) — '
                            f"修复: 确认 argparse 仍写作 `X = sub.add_parser('{cmd}', ...)`")
    m = re.search(head, _GEN_SRC)
    assert m is not None
    start = m.end()
    nxt = _GEN_SRC.find('sub.add_parser(', start)
    body = _GEN_SRC[start:] if nxt == -1 else _GEN_SRC[start:nxt]
    return set(re.findall(r"add_argument\([^)]*'(--[a-z-]+)'", body))


# ── 白名单 (仅可排除正则误捕的非配置项; table 六维度实测为 0 项) ────────────────
# 契约: 每项须注释理由 + 反向断言 (test_10 断言白名单项确实不是契约键);
# 长度趋近 0, 超 3 项须在注释说明原因。当前 0 项 —— 实测 layout-table.html 中
# col./c./OPTIONS./FB_CFG. 均无原生方法或局部变量误捕 (map/find/filter/sort 走大写
# COLUMNS.*, 视频/动作项字段用 no_call() 排除 v.split(/videos.map( 等调用形式)。
WHITELIST = {
    'columns': set(),
    'options': set(),
    'feedback': set(),
    'column_types': set(),
    'tabs': set(),
    'actions': set(),
    'videos': set(),
}

# CL013: 三模板维度白名单 (同样只排除正则误捕的运行时状态, 不得排除真实键)
WHITELIST_TOPIC = {
    'doc': {},                       # doc URL 状态 3 项全部为真实键, 无白名单
    'slide': {},                     # slide 行为项为显式清单, 不走提取正则
    'knowledge': {
        # layout-knowledge.html 中 item.active / item.filtered 是模板渲染用的运行时状态字段
        # (构建 DOM class / 搜索过滤态), 不是条目 JSON 的可配置键 ⇒ 排除; 由反向断言兜底。
        'item': {'active', 'filtered'},
    },
}

# 维度 → (提取正则列表, 契约维度, 修复动作)  ——  CL012: table 维度
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

# CL013: (主题, 维度) → (提取正则列表, 契约维度, 修复动作)
# doc.url_state 的契约键带 `?` 前缀 (与 table 同口径), 比对时统一去前缀 (见 _assert_topic_dim)。
TOPIC_DIMENSIONS = {
    ('doc', 'url_state'): ([r"params\.get\('([a-z]+)'\)"], 'url_state',
                           '在 TEMPLATE_CONTRACT["doc"]["data"]["url_state"] 补该键 '
                           '(键名口径与 table 一致, 带 ? 前缀)'),
    ('knowledge', 'item'): ([r'item\.([a-zA-Z_]\w*)'], 'item',
                            '在 TEMPLATE_CONTRACT["knowledge"]["data"]["item"] 补该键 '
                            "(双源: 模板 item.* ∪ 生成器 item.get('icon'))"),
    ('knowledge', 'groups'): ([r'\bg\.([a-zA-Z_]\w*)'], 'groups',
                              '在 TEMPLATE_CONTRACT["knowledge"]["data"]["groups"] 补该键'),
}

# table CLI / doc CLI / slide CLI / knowledge CLI 维度 (契约 cli 段, CL013 填实)
CLI_TOPICS = ('table', 'doc', 'slide', 'knowledge')

# slide 行为项 (正则不可提取 ⇒ 显式清单 + 模板特征串存在性断言; O-5)
# (契约键, 说明须含的子串, 模板特征串)
SLIDE_BEHAVIORS = [
    ('分页', 'h2', 'slide.pages'),
    ('导航', 'Space Home End', "'ArrowRight'"),
    ('全屏', 'F 键', 'requestFullscreen'),
    ('进度点', '底部圆点', '.slide-dot'),
    ('记忆', 'localStorage', 'html-gen:layoutslide_page'),
    ('侧栏H3', 'H3 子标题', 'toggleH3'),
    ('侧栏搜索', '关键字过滤', '.slide-toc-search'),
    ('性能警告', '加载警告', '.perf-warning'),
]


class TestHelpContract(unittest.TestCase):
    """契约 ⇄ 模板 ⇄ help 三维双向断言 (CL012: table; CL013: + doc/slide/knowledge)。"""

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
    def test_08_contract_keys_present_in_spec(self):
        """契约每个键都出现在 ① 键规范段 (`key:` 词元)，**不得**退化为全文词边界匹配。

        HG-SEC-177: 若对整篇 help 做词边界匹配，键名可能命中 ② 手写示例段的 JSON
        或作为通用英文词出现 → 「契约删键 / 渲染漏段」时测试仍绿 (假阴性)。
        behaviors 渲染形态不同 (`key … — 说明`)，单独断言。
        """
        tokens = spec_key_tokens()
        missing = []
        for dim, entries in NODE['data'].items():
            for key, desc, default in entries:
                if key not in tokens:
                    missing.append(f'{dim}.{key} (说明: {desc!r})')
        for key, *_ in NODE['url_state']:
            if key not in tokens:
                missing.append(f'url_state.{key}')
        for key, *_ in NODE['behaviors']:
            if not re.search(rf'^\s*{re.escape(key)}\s+—', SPEC_TEXT, re.M):
                missing.append(f'behaviors.{key}')
        self.assertFalse(missing,
                         f'契约键未出现在 ① 键规范段 (render_help_spec): {missing}; '
                         f'来源 html-gen.py TEMPLATE_CONTRACT["table"]; '
                         f'修复: 确认该维度在 section_order / _SPEC_NESTED 内且条目已渲染')

    # ── ③ help → 契约 ────────────────────────────────────────────────────
    def test_09_help_spec_keys_subset_of_contract(self):
        """键规范段渲染出的 `key:` 词元 ⊆ 契约键 (help 不得出现契约未声明的键)。"""
        tokens = spec_key_tokens()
        extra = tokens - all_contract_keys()
        self.assertFalse(extra,
                         f'help 键规范段出现契约未声明的键 {sorted(extra)}; 来源 render_help_spec("table"); '
                         f'修复: 或在契约中声明该键, 或修正 TEMPLATE_CONTRACT 中该条目的说明文本')
        self.assertTrue(tokens, '键规范段未提取到任何键 — 渲染格式可能已变 (期望 `key: 说明` 行式排版)')

    # ── 白名单纪律 ───────────────────────────────────────────────────────
    def test_10_whitelist_discipline(self):
        """白名单项必须确实不是契约键 (反向断言); table 每维度 ≤3 项, 三模板白名单同纪律。"""
        contract = all_contract_keys()
        for dim, wl in WHITELIST.items():
            self.assertLessEqual(len(wl), 3,
                                 f'{dim} 白名单 {sorted(wl)} 超 3 项, 须在测试注释说明原因')
            for item in wl:
                self.assertNotIn(item, contract,
                                 f'{dim} 白名单项 {item} 是真实契约键 — 不得用白名单排除真实键, '
                                 f'应在契约中声明')
        for topic, dims in WHITELIST_TOPIC.items():
            for dim, wl in dims.items():
                self.assertLessEqual(len(wl), 3,
                                     f'{topic}.{dim} 白名单 {sorted(wl)} 超 3 项, 须在测试注释说明原因')
                for item in wl:
                    self.assertNotIn(item, all_contract_keys(topic),
                                     f'{topic}.{dim} 白名单项 {item} 是真实契约键 — '
                                     f'不得用白名单排除真实键, 应在契约中声明')

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

    def test_12_all_topics_render_from_contract(self):
        """四模板节点均由契约渲染 (无 legacy 骨架): label/分隔线/键规范段齐备 + 主题清单完整。"""
        for topic, node in HG.TEMPLATE_CONTRACT.items():
            with self.subTest(topic=topic):
                self.assertNotIn('legacy', node,
                                 f'{topic} 不应再有 legacy 骨架指针 (CL013 已补真实维度模型)')
                text = HG.render_help(topic)
                expect_first = node['label'] + (f" ({node['tagline']})" if node.get('tagline') else '')
                self.assertEqual(text.splitlines()[0], expect_first,
                                 f'{topic} 契约 label 与渲染首行不一致')
                self.assertEqual(text.splitlines()[1], '━' * node['rule'],
                                 f'{topic} 第二行应为契约 rule 指定的分隔线')
                self.assertTrue(spec_text(topic).strip(),
                                f'{topic} ① 键规范段为空 — 契约维度或 section_order 缺失')
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

    # ── CL013: 四模板 CLI 参数维度 ───────────────────────────────────────
    def test_15_all_topics_cli_flags_match_contract(self):
        """四模板 CLI: argparse 子命令块长形 flag == 契约 cli 键集 (table 9 / doc 9 / slide 8 / knowledge 10)。

        ① 模板消费 (argparse 定义) ⊆ 契约 — 且反向要求契约不得声明 argparse 未实现的 flag。
        短形 `-i/-o/-d/-g` 是别名 ⇒ 不计键 (HG-SEC-168: 必须按 sub.add_parser 块切分提取)。
        """
        for topic in CLI_TOPICS:
            with self.subTest(topic=topic):
                consumed = cli_flags(topic)
                contract = dim_keys('cli', topic)
                extra = consumed - contract
                missing = contract - consumed
                self.assertFalse(
                    extra,
                    f'{topic}: argparse 声明但契约 cli 段未收录的 flag {sorted(extra)} — 来源 html-gen.py; '
                    f'修复: 在 TEMPLATE_CONTRACT["{topic}"]["cli"] 补该 flag')
                self.assertFalse(
                    missing,
                    f'{topic}: 契约 cli 段声明但 argparse 未实现的 flag {sorted(missing)} — 来源 html-gen.py; '
                    f'修复: 删除契约中该条目, 或补 argparse 定义')
                for flag, _desc, _default in _dim_entries('cli', topic):
                    self.assertTrue(flag.startswith('--'),
                                    f'{topic} cli 条目键名应为长形 flag: {flag!r}')

    def test_16_topic_contract_keys_present_in_spec(self):
        """② doc/slide/knowledge 契约键 (data 各维度 ∪ url_state ∪ cli) 均渲染在 ① 键规范段。

        键名形态三类: 标识符键 (`title`/`?sidebar`)、别名键 (`{items|data}`)、中文键 (「数组」)、
        CLI flag (`--data`) —— 后三类不以 `key:` 词元出现 (词元正则只收 ASCII 标识符形态),
        故用 spec_renders_key() 的字面量锚定口径 (仍只扫 ① 段, 不扫 ② 示例段: 示例 JSON 里
        同样有 `--output` 字面量, 全文匹配会掩盖「键规范段漏渲染」)。
        behaviors 段渲染形态不同 (`key … — 说明`), 单独断言。
        """
        for topic in ('doc', 'slide', 'knowledge'):
            node = HG.TEMPLATE_CONTRACT[topic]
            keys = [k for dim in (node.get('data') or {}).values() for k, _d, _v in dim]
            keys += [k for k, *_ in node.get('url_state') or []]
            keys += [k for k, *_ in node.get('cli') or []]
            for key in keys:
                with self.subTest(topic=topic, key=key):
                    self.assertTrue(
                        spec_renders_key(topic, key),
                        f'{topic} help ① 键规范段未渲染契约键 {key!r} — '
                        f'来源 html-gen.py TEMPLATE_CONTRACT["{topic}"]; '
                        f'修复: 确认该维度在 section_order 内且 _SPEC_TITLES 已登记')
            for key, _desc in node.get('behaviors') or []:
                with self.subTest(topic=topic, behavior=key):
                    self.assertTrue(
                        spec_renders_behavior(topic, key),
                        f'{topic} help ① 段未按 `key … — 说明` 形态渲染行为 {key!r} — '
                        f'修复: 确认 behaviors 在 section_order 内 (或为节点末尾默认段)')

    def test_17_doc_url_state_matches_template(self):
        """doc URL 状态: 模板 params.get('x') 消费键 == 契约 url_state 键 (去 ? 前缀; 3 项)。"""
        self._assert_topic_dim('doc', 'url_state')
        for key in dim_keys('url_state', 'doc'):
            self.assertTrue(key.startswith('?'),
                            f'doc url_state 键名口径应与 table 一致 (带 ? 前缀): {key!r}')

    def test_18_slide_behaviors_explicit_list(self):
        """slide 行为项: 显式清单 (8 项, 含侧栏关键字过滤) + 契约→help + 模板特征串存在性。

        正则无法从 layout-slide.html 提取行为项 (O-5) ⇒ 清单在此登记, 新增 slide 交互能力
        必须同步此表 + 契约 (否则本测试转红)。
        """
        node = HG.TEMPLATE_CONTRACT['slide']
        keys = [k for k, _ in node['behaviors']]
        self.assertEqual(keys, [k for k, _, _ in SLIDE_BEHAVIORS],
                         f'slide 行为项与显式清单不一致 — 来源 html-gen.py '
                         f'TEMPLATE_CONTRACT["slide"]["behaviors"]; '
                         f'修复: 同步新增/删除行为项到本测试 SLIDE_BEHAVIORS')
        text = tmpl_text('slide')
        for key, desc_must, marker in SLIDE_BEHAVIORS:
            with self.subTest(behavior=key):
                desc = dict(node['behaviors'])[key]
                self.assertIn(desc_must, desc,
                              f'slide 行为 {key} 说明缺「{desc_must}」— 契约说明文本被削: {desc!r}')
                self.assertIn(marker, text,
                              f'slide 行为 {key} 的模板特征串 {marker!r} 不在 layout-slide.html — '
                              f'该能力可能已删除; 修复: 同步契约与 SLIDE_BEHAVIORS')
                self.assertTrue(spec_renders_behavior('slide', key),
                                f'slide 行为 {key} 未按 `key … — 说明` 形态渲染 (behaviors 段)')
        self.assertEqual(len(keys), 8, f'slide 行为项应为 8 项: {keys}')

    def test_19_knowledge_item_keys_dual_source(self):
        """knowledge item: 双源 (模板 item.* ∪ 生成器 item.get) 消费键 == 契约 item (7 键)。

        layout-knowledge.html 的 item.active / item.filtered 是运行时状态 (白名单),
        item.icon 只在生成器 (cmd_knowledge 自动分组推导) 消费 ⇒ 必须双源合并 (HG-SEC-169)。
        """
        self._assert_topic_dim('knowledge', 'item')
        self.assertEqual(dim_keys('item', 'knowledge'),
                         {'title', 'group', 'section', 'badge', 'desc', 'url', 'icon'},
                         'knowledge item 契约键集应为 7 项 (含 icon)')

    def test_20_knowledge_groups_keys(self):
        """knowledge groups: 模板 g.* 消费键 == 契约 groups (3 键: key/label/icon)。"""
        self._assert_topic_dim('knowledge', 'groups')
        self.assertEqual(dim_keys('groups', 'knowledge'), {'key', 'label', 'icon'},
                         'knowledge groups 契约键集应为 3 项')

    def test_21_topic_spec_keys_subset_of_contract(self):
        """③ 三模板键规范段 `key:` 词元 ⊆ 契约键 (口径同 test_09, 不用全文词边界)。

        slide 的 ① 段无标识符形态键 (URL 状态为说明句, 行为项用 `—`, CLI 用 `--flag`),
        故词元集可为空 —— 该情形由 test_16 的字面量口径覆盖, 此处不要求非空。
        说明文本若误用「词元:」片段会被此处抓出 (契约注释已列此约束)。
        """
        for topic in ('doc', 'slide', 'knowledge'):
            with self.subTest(topic=topic):
                tokens = spec_key_tokens(topic)
                extra = tokens - all_contract_keys(topic)
                self.assertFalse(
                    extra,
                    f'{topic} ① 键规范段出现契约未声明的键 {sorted(extra)} — '
                    f'来源 render_help_spec("{topic}") / html-gen.py TEMPLATE_CONTRACT["{topic}"]; '
                    f'修复: 或在契约中声明该键, 或改写该条目说明文本 (不得含「词元:」片段)')

    def test_22_doc_syntax_notes_kept_verbatim(self):
        """doc ③ 语法说明段: 保持 CL012 前 HELP_DOC 正文逐字 (Markdown 块级/行内/Callout/不支持)。"""
        notes = HG._help_const(HG.TEMPLATE_CONTRACT['doc']['notes'])
        for must in ('块级元素:', '行内元素:', 'Callout 提示框:', '不支持:',
                     '# 标题', '**加粗**', '> **Note:**', '✗ HTML 标签 (会被转义)'):
            self.assertIn(must, notes, f'doc 语法说明段缺 CL012 前正文内容: {must!r}')
        self.assertNotIn('?sidebar', notes, '③ 语法说明段不得含键名字面量 (§B.3)')

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

    def _assert_topic_dim(self, topic, dim):
        """CL013 维度断言: 模板消费键 (去白名单) == 契约键 (doc.url_state 去 `?` 前缀后比对)。"""
        patterns, contract_dim, fix = TOPIC_DIMENSIONS[(topic, dim)]
        text = tmpl_text(topic)
        consumed = set()
        for pat in patterns:
            consumed |= extract(pat, text)
        if (topic, dim) == ('knowledge', 'item'):
            # 双源之二: 生成器侧 (cmd_knowledge 自动分组推导 item.icon)。
            # 实测生成器两处调用均带默认值 (`item.get('group', '其他')` / `item.get('icon', '')`),
            # 故正则须容忍第二参数 —— 设计 §D 的字面 `item\.get\('([a-z]+)'\)` 在本仓恒为空集,
            # 会让双源断言退化为恒真的单向 ⊆ (设计 errata, 同 ops harness T42 口径)。
            consumed |= set(re.findall(r"item\.get\('([a-z]+)'", _GEN_SRC))
        consumed -= WHITELIST_TOPIC.get(topic, {}).get(dim, set())
        contract = dim_keys(contract_dim, topic)
        if contract_dim == 'url_state':               # 契约键带 `?` 前缀 (与 table 同口径)
            contract = {k.lstrip('?') for k in contract}
        self.assertEqual(
            consumed, contract,
            f'{topic}.{dim}: 消费键 {sorted(consumed)} != 契约键 {sorted(contract)} — '
            f'来源 {TOPIC_TMPL[topic].name}'
            + (' + html-gen.py (双源)' if (topic, dim) == ('knowledge', 'item') else '')
            + f'; 修复: {fix}')
        self.assertTrue(consumed, f'{topic}.{dim}: 未提取到任何键 — 提取正则可能已失效')

    def _run_table(self, payload):
        """写临时 JSON 跑 html-gen table, 返回 CompletedProcess。"""
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / 'in.json'
            src.write_text(json.dumps(payload, ensure_ascii=False), encoding='utf-8')
            return subprocess.run(['python3', str(GEN), 'table', '-d', str(src), '-o', str(Path(td) / 'o.html')],
                                  capture_output=True, text=True, timeout=60)


if __name__ == '__main__':
    unittest.main()
