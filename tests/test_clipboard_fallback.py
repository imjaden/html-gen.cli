"""CL015 剪贴板回退守卫 —— canonical copyText 块不变量 + 行为夹具 + 非 localhost origin 端到端。

T1–T4 静态不变量（四模板 / 产物面）· T5–T10 Selenium 行为夹具 · T11 真非 localhost origin（无 LAN ⇒ SKIP）。

背景：`navigator.clipboard` 仅在安全上下文（https / localhost / file://）存在；`http://<局域网 IP>` 下为
undefined，调用处直接抛 TypeError，写在 catch/.catch() 里的兜底永不可达（静默失效 / 假成功）。
canonical `copyText` 块把「安全上下文前置判断 + execCommand('copy') 回退且检查返回值 + 失败可见反馈」
收敛成单一实现，本文件把它变成**提交即拦**的不变量。

未验证面（HG-SEC-192 登记）：移动 Safari（iOS）对 `readonly` textarea + `select()`/`execCommand` 的
已知不生效报告未在本测试覆盖范围内 —— T11 只覆盖桌面 LAN origin。
"""
import functools
import hashlib
import http.server
import re
import subprocess
import tempfile
import threading
import time
import unittest
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

CHROMEDRIVER = '/Users/jadenli/CodeSpace/script-miner/cache/chromedriver/chromedriver'
PROJECT = Path(__file__).resolve().parent.parent

TEMPLATES = ['layout-doc.html', 'layout-slide.html', 'layout-table.html', 'layout-knowledge.html']
BEG = 'html-gen:clipboard-copy v1 BEGIN'
END = 'html-gen:clipboard-copy v1 END'
FAIL_MSG = '复制失败，请手动选中文本复制'
ANCHOR_FAIL_MSG = '复制失败，请手动复制链接'
# 落地页（D6 本批不动，自带另一签名的 copyText，已合规）——不进产物面守卫
LANDING_EXCLUDED = {'demos/index.html'}

DOC_PAGE = PROJECT / 'demos' / 'usage-guide.html'
SLIDE_PAGE = PROJECT / 'demos' / 'slide-demo.html'
KW_PAGE = PROJECT / 'demos' / 'knowledge-demo.html'
TABLE_PAGE = PROJECT / 'demos' / 'countries-table.html'

# ── 假不安全上下文夹具（clipboard 不存在 + isSecureContext=false）──
FIX_INSECURE = """
Object.defineProperty(window, 'isSecureContext', { value: false, configurable: true });
Object.defineProperty(navigator, 'clipboard', { value: undefined, configurable: true });
window.__execCalled = 0;
document.execCommand = function () { window.__execCalled++; return true; };
"""
# ── HG-SEC-190: secure 变体（isSecureContext=true + writeText 返回 reject Promise）──
FIX_SECURE_REJECT = """
Object.defineProperty(window, 'isSecureContext', { value: true, configurable: true });
Object.defineProperty(navigator, 'clipboard', { value: { writeText: function () {
  return Promise.reject(new Error('denied')); } }, configurable: true });
window.__execCalled = 0;
document.execCommand = function () { window.__execCalled++; return true; };
"""
# ── 失败路径夹具（回退可用但 execCommand 返回 false）──
FIX_EXEC_FALSE = """
Object.defineProperty(window, 'isSecureContext', { value: false, configurable: true });
Object.defineProperty(navigator, 'clipboard', { value: undefined, configurable: true });
window.__execCalled = 0;
document.execCommand = function () { window.__execCalled++; return false; };
"""


def read(rel):
    return (PROJECT / rel).read_text(encoding='utf-8')


def extract_block(text):
    """取 canonical 块（起止标记所在注释行之间的完整文本）。"""
    i = text.index(BEG)
    j = text.index(END)
    start = text.rfind('/*', 0, i)
    end = text.index('*/', j) + 2
    return text[start:end]


def script_spans(text):
    spans = []
    for m in re.finditer(r'<script[^>]*>', text):
        e = text.find('</script>', m.end())
        if e != -1:
            spans.append((m.end(), e))
    return spans


class TestClipboardStatic(unittest.TestCase):
    """T1–T4：canonical 块不变量 + 产物面「每个调用点都在块内/非脚本内容」。"""

    # ── T1：四模板块成对且逐字节一致 ──

    def test_01_block_paired_and_byte_identical(self):
        digests = {}
        for name in TEMPLATES:
            text = read(name)
            self.assertEqual(text.count(BEG), 1, f'{name} 应有 1 处 BEGIN 标记')
            self.assertEqual(text.count(END), 1, f'{name} 应有 1 处 END 标记')
            digests[name] = hashlib.sha256(extract_block(text).encode('utf-8')).hexdigest()
        self.assertEqual(len(set(digests.values())), 1,
                         f'四模板 canonical 块须逐字节一致，实测: {digests}')

    # ── T2：块外零 navigator.clipboard（块内 3 次 = 2 守卫 + 1 调用）──

    def test_02_no_clipboard_outside_block(self):
        for name in TEMPLATES:
            text = read(name)
            block = extract_block(text)
            total = text.count('navigator.clipboard')
            inside = block.count('navigator.clipboard')
            self.assertEqual(inside, 3, f'{name} 块内应出现 3 次（2 守卫 + 1 调用），实测 {inside}')
            self.assertEqual(total, inside,
                             f'{name} 块外出现 {total - inside} 次 navigator.clipboard（应 0）')

    # ── T3：块内规格 + 解析链命中（HG-SEC-191：落点错会静默降级 console）──

    def test_03_block_spec_and_toast_resolution(self):
        for name in TEMPLATES:
            text = read(name)
            block = extract_block(text)
            lines = block.split('\n')
            # S7 签名
            self.assertIn('function copyText(text, okMsg, failMsg, onOk) {', block, f'{name} 签名')
            # S3 安全上下文判断先于 writeText 调用
            guard = next(i for i, l in enumerate(lines) if 'isSecureContext' in l)
            call = next(i for i, l in enumerate(lines) if 'writeText(text)' in l)
            self.assertLess(guard, call, f'{name} isSecureContext 判断必须先于 writeText 调用')
            # S4 execCommand 返回值被检查
            self.assertIn('if (ok)', block, f'{name} 须检查 execCommand 返回值')
            # S5 失败路径可见反馈
            self.assertIn(FAIL_MSG, block, f'{name} 须含失败文案常量')

            # 解析链命中：块必须落在主 IIFE 内、toast 函数声明之后
            start = text.rfind('/*', 0, text.index(BEG))
            span = next((s for s in script_spans(text) if s[0] <= start <= s[1]), None)
            self.assertIsNotNone(span, f'{name} canonical 块须位于 <script> 内')
            toast_pos = max(text.rfind('function showToast(', span[0], start),
                            text.rfind('function showKwToast(', span[0], start))
            self.assertGreater(toast_pos, -1, f'{name} toast 函数声明须在 canonical 块之前（同作用域）')
            self.assertNotIn('})();', text[toast_pos:start],
                             f'{name} canonical 块须仍在 toast 所在 IIFE 内（否则解析链降级 console）')

    # ── T4：产物面等价巡检口径（0 FAIL / 0 WARN）──

    def test_04_products_no_bare_clipboard_call(self):
        bad = []
        products = sorted(list((PROJECT / 'demos').rglob('*.html'))
                          + list((PROJECT / 'prompts').rglob('*.html')))
        for p in products:
            rel = p.relative_to(PROJECT).as_posix()
            if rel in LANDING_EXCLUDED:
                continue                      # D6：落地页本批不动
            text = read(rel)
            if 'navigator.clipboard' not in text:
                continue
            block = extract_block(text) if BEG in text else ''
            spans = script_spans(text)
            b_start = text.rfind('/*', 0, text.index(BEG)) if BEG in text else -1
            b_end = (text.index('*/', text.index(END)) + 2) if BEG in text else -1
            for m in re.finditer(r'navigator\.clipboard', text):
                pos = m.start()
                if b_start <= pos < b_end:
                    continue                  # 块内（唯一合法调用点）
                in_script = any(s <= pos < e for s, e in spans)
                if in_script:
                    bad.append(f'{rel}:{text.count(chr(10), 0, pos) + 1} 脚本内裸调用')
                # 非脚本区间（正文/代码示例引用）不计 —— 与巡检探针判级口径一致
            self.assertIn('copyText', block or '', f'{rel} 含块但未见 copyText')
        self.assertEqual(bad, [], f'产物面存在块外脚本调用点: {bad}')


class TestClipboardBehavior(unittest.TestCase):
    """T5–T10：headless Chrome 行为夹具（spy 断言行可达；真实复制由 T11 + 实机确认）。"""

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
        self.driver.set_window_size(1280, 900)

    def _load(self, page):
        self.driver.get('file://' + str(page))
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.doc-body, #docBody, .kw-tab, .data-table')))
        self.driver.execute_script("localStorage.clear();")

    def _fix(self, script=FIX_INSECURE):
        self.driver.execute_script(script)

    def _exec_called(self):
        return self.driver.execute_script('return window.__execCalled;')

    def _toast(self, tid):
        return self.driver.execute_script(
            "var e = document.getElementById(arguments[0]); return e ? e.textContent : null;", tid)

    # ── T5：doc 标题点击（+ 代码块按钮）在假不安全上下文下走回退且反馈真实 ──

    def test_05_doc_title_and_code_button_fallback(self):
        self._load(DOC_PAGE)
        self._fix()
        self.driver.find_element(By.ID, 'sidebarTitle').click()
        time.sleep(0.3)
        self.assertEqual(self._exec_called(), 1, '非安全上下文下必须走 execCommand 回退（修前 spy=0）')
        self.assertEqual(self._toast('docToast'), '已复制: usage-guide.md', '成功文案应来自调用点传入的 okMsg')

        # 代码块复制按钮（调用点 #3：okMsg/failMsg 为空 ⇒ 走默认失败文案 + onOk 承担按钮文案）
        self._load(DOC_PAGE)
        self._fix()
        self.driver.execute_script("document.querySelector('.doc-body pre .copy-btn').click()")
        time.sleep(0.3)
        self.assertEqual(self._exec_called(), 1, '代码块按钮也须走回退')
        self.assertEqual(
            self.driver.execute_script(
                "return document.querySelector('.doc-body pre .copy-btn').textContent;"),
            '已复制', 'onOk 仅在真成功时把按钮文案改成「已复制」')

    # ── T6：doc TOC 锚点 —— ✓ 仅在真成功出现；失败必须可见 ──

    def test_06_doc_anchor_onok_only_on_success(self):
        self._load(DOC_PAGE)
        self._fix()
        self.driver.execute_script("document.querySelector('.doc-body h2 .anchor-link').click()")
        time.sleep(0.3)
        self.assertEqual(self._exec_called(), 1, '锚点复制须走回退')
        self.assertEqual(
            self.driver.execute_script("return document.querySelector('.doc-body h2 .anchor-link').textContent;"),
            '\u2713', 'D5：真成功时锚点才变 ✓')

        # 失败路径：execCommand 返回 false ⇒ 不得出现 ✓，且必须有失败文案
        self._load(DOC_PAGE)
        self._fix(FIX_EXEC_FALSE)
        self.driver.execute_script("document.querySelector('.doc-body h2 .anchor-link').click()")
        time.sleep(0.3)
        self.assertEqual(
            self.driver.execute_script("return document.querySelector('.doc-body h2 .anchor-link').textContent;"),
            '\u00b6', 'D5：失败时锚点不得变 ✓')
        self.assertEqual(self._toast('docToast'), ANCHOR_FAIL_MSG, '失败必须有可见反馈（禁假成功）')

    # ── T7：slide 标题点击 + TOC 锚点 ──

    def test_07_slide_title_and_anchor(self):
        self._load(SLIDE_PAGE)
        self._fix()
        self.driver.find_element(By.ID, 'slideTitle').click()
        time.sleep(0.3)
        self.assertEqual(self._exec_called(), 1, 'slide 标题点击须走回退（修前 fallbackCopy 不查返回值）')
        self.assertEqual(self._toast('slideToast'), '已复制: markdown-spec.md')

        self._load(SLIDE_PAGE)
        self._fix()
        self.driver.execute_script("document.querySelector('#docBody h2 .anchor-link').click()")
        time.sleep(0.3)
        self.assertEqual(self._exec_called(), 1, 'slide TOC 锚点须走回退（修前裸调用 FAIL）')
        self.assertEqual(
            self.driver.execute_script("return document.querySelector('#docBody h2 .anchor-link').textContent;"),
            '\u2713', 'slide 锚点真成功才变 ✓')

    # ── T8：knowledge 标题点击 —— showKwToast 解析链命中 + D10 闸门正则可达 basename ──

    def test_08_knowledge_title_resolution_and_gate(self):
        self._load(KW_PAGE)
        # D10：闸门正则须与 doc 版一致（含 [\w.\- ]+$ 兜底），否则脱敏 basename 静默无反应
        self.assertIn(r'/^(https?:|\/|~\/|[\w.\- ]+$)/.test(target)',
                      read('layout-knowledge.html'), 'D10：knowledge 闸门正则须并入 doc 版兜底')
        # 构造脱敏 basename（products 的 sidebar-title 属性为标题而非路径，故显式置位）
        self.driver.execute_script(
            "document.querySelector('.kw-sidebar-header .sidebar-title').title = '路径: knowledge-demo.html';")
        self._fix()
        self.driver.execute_script("document.querySelector('.kw-sidebar-header .sidebar-title').click()")
        time.sleep(0.3)
        self.assertEqual(self._exec_called(), 1, 'D10：basename 目标须通过闸门并复制')
        self.assertEqual(self._toast('kwToast'), '已复制: knowledge-demo.html',
                         'showKwToast 解析链须命中（否则降级 console 无 toast）')

    # ── T9：table copyAction 两路都要有反馈（① clipboard 存在但 reject ② 假不安全上下文）──

    def test_09_table_copy_action_both_paths(self):
        # ① secure 变体：clipboard 存在但 writeText reject ⇒ 经 .catch 回退，不得静默
        self._load(TABLE_PAGE)
        self._fix(FIX_SECURE_REJECT)
        self.driver.execute_script("window.copyAction('PROBE-ROW')")
        time.sleep(0.4)
        self.assertGreaterEqual(self._exec_called(), 1, 'reject 后必须落到 execCommand 回退')
        self.assertEqual(self._toast('toast'), '已复制: PROBE-ROW')
        # ② 假不安全上下文
        self._load(TABLE_PAGE)
        self._fix(FIX_INSECURE)
        self.driver.execute_script("window.copyAction('PROBE-ROW')")
        time.sleep(0.3)
        self.assertEqual(self._exec_called(), 1)
        self.assertEqual(self._toast('toast'), '已复制: PROBE-ROW')
        # shareLink 对外名字保持且走 canonical（原 fallbackCopyUrl 已删除）
        self.assertIn('window.shareLink = function() {', read('layout-table.html'))
        self.assertNotIn('function fallbackCopyUrl(', read('layout-table.html'))

    # ── T10：失败路径总闸（execCommand→false 时必须出现失败文案，禁假成功）──

    def test_10_failure_path_never_fake_success(self):
        self._load(TABLE_PAGE)
        self._fix(FIX_EXEC_FALSE)
        self.driver.execute_script("window.shareLink()")
        time.sleep(0.3)
        self.assertEqual(self._toast('toast'), '复制失败', '失败路径必须给出可见失败反馈')

    # ── T5 A/B 负例：修前形态（旧 snippet）在同夹具下「假成功」──

    def test_11_ab_negative_prefix_snippet_fake_success(self):
        legacy = """<!DOCTYPE html><html><head><meta charset="utf-8"><title>legacy</title></head><body>
<div id="docToast"></div>
<button id="b">copy</button>
<script>
function showToast(msg) { document.getElementById('docToast').textContent = msg; }
document.getElementById('b').addEventListener('click', function() {
  var target = 'legacy.md';
  try { navigator.clipboard.writeText(target).catch(function(){}); } catch(e) {}
  showToast('已复制: ' + target);        // 修前：无条件报已复制（假成功）；回退不可达
});
</script>
</body></html>
"""
        d = Path(tempfile.mkdtemp()) / 'legacy.html'
        d.write_text(legacy, encoding='utf-8')
        self.driver.get('file://' + str(d))
        self._fix(FIX_INSECURE)
        self.driver.find_element(By.ID, 'b').click()
        time.sleep(0.2)
        self.assertEqual(self._exec_called(), 0, '修前形态：非安全上下文下回退永不可达（spy=0）')
        self.assertEqual(self._toast('docToast'), '已复制: legacy.md',
                         '修前形态：仍报「已复制」= 假成功（本批修复的判据）')


class TestClipboardRealOrigin(unittest.TestCase):
    """T11：真非 localhost origin（LAN IP + http）端到端 —— 无 LAN IP / 端口不可用 ⇒ SKIP。"""

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

    def test_11_real_insecure_origin_end_to_end(self):
        ip = subprocess.run(['ipconfig', 'getifaddr', 'en0'],
                            capture_output=True, text=True).stdout.strip()
        if not ip:
            self.skipTest('无 LAN IP（en0 无地址）⇒ SKIP；移动端 Safari 亦不在本测试覆盖范围（HG-SEC-192）')

        class _Quiet(http.server.SimpleHTTPRequestHandler):
            def log_message(self, *args):
                pass

        try:
            srv = http.server.ThreadingHTTPServer(
                ('', 0), functools.partial(_Quiet, directory=str(PROJECT)))
        except OSError as e:
            self.skipTest(f'本地 http server 启动失败（{e}）⇒ SKIP；移动端不在覆盖范围（HG-SEC-192）')
        port = srv.server_address[1]
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        try:
            self.driver.set_window_size(1280, 900)
            self.driver.get(f'http://{ip}:{port}/demos/usage-guide.html')
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.doc-body')))
            self.assertFalse(self.driver.execute_script('return window.isSecureContext'),
                             'LAN http origin 必须是非安全上下文（T11 前提）')
            self.assertEqual(self.driver.execute_script('return typeof navigator.clipboard'),
                             'undefined', '非安全上下文下 navigator.clipboard 应不存在')
            self.driver.execute_script(
                "window.__execCalled = 0;"
                "document.execCommand = function () { window.__execCalled++; return true; };")
            self.driver.find_element(By.ID, 'sidebarTitle').click()
            time.sleep(0.3)
            self.assertGreaterEqual(self.driver.execute_script('return window.__execCalled'), 1,
                                    '真非 localhost origin 下必须真实走到 execCommand 回退')
            self.assertEqual(
                self.driver.execute_script(
                    "var e = document.getElementById('docToast'); return e ? e.textContent : null;"),
                '已复制: usage-guide.md')
        finally:
            srv.shutdown()
            srv.server_close()


if __name__ == '__main__':
    unittest.main(verbosity=2)
