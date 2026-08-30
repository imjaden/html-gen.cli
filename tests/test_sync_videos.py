# -*- coding: utf-8 -*-
"""tests/test_sync_videos.py — table videos 同步辅助脚本测试（HTML-GEN-CL002）.

设计: documents/solutions/table-videos-syncer-design-v1.1-20260829.md（§5 测试计划）

非 Selenium：unittest + subprocess 调 scripts/tool-table-videos-syncer.py。
每用例独立 tempfile.mkdtemp（xdist 多 worker 隔离，勿用模块级共享目录）。
脚本复制到临时目录 scripts/ 下运行，使脚本推导的项目根 = 临时目录
（RIG-003 路径以项目根为基准）；临时目录放 data json + html-gen.py 桩。
"""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

PROJECT = Path(__file__).resolve().parent.parent
SCRIPT_SRC = PROJECT / 'scripts' / 'tool-table-videos-syncer.py'

# html-gen.py 桩：模拟 `html-gen table -d <data> -o <out>`，从 json 渲染含
# <title> 与 videos 标题列表的 html（供 test_10 断言重建结果）。
HTML_GEN_STUB = """\
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, sys
from pathlib import Path

args = sys.argv[1:]  # ['table', '-d', <data>, '-o', <out>, ('--github-url', <url>)]
if '-d' in args:
    with open(args[args.index('-d') + 1], encoding='utf-8') as f:
        doc = json.load(f)
out = Path(args[args.index('-o') + 1])
out.parent.mkdir(parents=True, exist_ok=True)
github_url = None
if '--github-url' in args:
    github_url = args[args.index('--github-url') + 1]
title = doc.get('title', '数据表格')
data = doc.get('data', doc)
titles = []
for row in data:
    for v in (row.get('videos') or []):
        titles.append(v.get('title', ''))
corner = ''
if github_url:
    corner = '<a href="' + github_url + '" class="github-corner">c</a>'
html = (
    '<!DOCTYPE html><html><head><title>' + title + '</title></head><body>'
    '<div class="data-table">' + json.dumps(data, ensure_ascii=False) + '</div>'
    + corner
    + '<ul>' + ''.join('<li>' + t + '</li>' for t in titles) + '</ul></body></html>'
)
with open(out, 'w', encoding='utf-8') as f:
    f.write(html)
"""

YAML_TEMPLATE = """\
target:
- data: data/_countries-data.json
- html: demos/countries-table.html

countries:
{countries}
"""


def make_base_data():
    """3 行国家：缅甸无 videos、伊朗 1 条、中国 1 条（与真实数据形态一致）。"""
    return {
        "title": "测试国家表",
        "columns": [
            {"key": "country_zh", "label": "国家", "sortable": True},
            {"key": "videos", "label": "视频", "type": "videos", "width": "260px",
             "preview": True, "videos": {"maxShow": 2}},
        ],
        "data": [
            {"country_zh": "缅甸", "country_en": "Myanmar"},
            {"country_zh": "伊朗", "country_en": "Iran", "videos": [
                {"title": "中东为何永不团结", "url": "https://v.douyin.com/Ez_SJIkymk0/",
                 "duration": "4:54", "platform": "douyin"}]},
            {"country_zh": "中国", "country_en": "China", "videos": [
                {"title": "既有视频", "url": "https://v.douyin.com/OLD123/",
                 "duration": "2:30", "platform": "douyin"}]},
        ],
        "options": {"pageSize": 30},
    }


class SyncVideosTestBase(unittest.TestCase):
    """公共 setUp：临时目录 + 复制脚本 + 写桩 html-gen.py。"""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix='hg-sync-'))
        scripts_dir = self.tmp / 'scripts'
        scripts_dir.mkdir()
        self.script = scripts_dir / SCRIPT_SRC.name
        shutil.copy(SCRIPT_SRC, self.script)
        (self.tmp / 'html-gen.py').write_text(HTML_GEN_STUB, encoding='utf-8')

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def setup_fixture(self, data_doc, countries_block):
        """写 data json + yaml（target 相对临时项目根）；返回 yaml 路径。"""
        data_path = self.tmp / 'data' / '_countries-data.json'
        data_path.parent.mkdir(parents=True, exist_ok=True)
        data_path.write_text(json.dumps(data_doc, ensure_ascii=False, indent=2),
                             encoding='utf-8')
        yaml_path = self.tmp / 'input.yaml'
        yaml_path.write_text(YAML_TEMPLATE.format(countries=countries_block),
                             encoding='utf-8')
        return yaml_path

    def run_script(self, yaml_path, *flags):
        cmd = [sys.executable, str(self.script)]
        if yaml_path is not None:
            cmd.append(str(yaml_path))
        cmd += list(flags)
        return subprocess.run(cmd, capture_output=True, text=True, cwd=self.tmp)

    def read_json(self):
        return json.loads((self.tmp / 'data' / '_countries-data.json').read_text(encoding='utf-8'))

    def read_yaml(self):
        return yaml.safe_load((self.tmp / 'input.yaml').read_text(encoding='utf-8'))

    def snapshot(self):
        """(mtime_ns, 内容) 快照，用于零写盘断言。"""
        out = {}
        for name in ('data/_countries-data.json', 'input.yaml', 'demos/countries-table.html'):
            p = self.tmp / name
            out[name] = (p.stat().st_mtime_ns, p.read_bytes()) if p.exists() else None
        return out

    def assert_unchanged(self, before):
        after = self.snapshot()
        self.assertEqual(before, after, '文件不应被修改（零写盘）')


class TestSyncVideos(SyncVideosTestBase):

    def test_01_parse_quoted_duration(self):
        """解析：duration 引号 → str "6:55" 非 int 415。"""
        countries = (
            '- country_zh: 缅甸\n'
            '  title: 缅甸-散装缅甸\n'
            '  url: https://v.douyin.com/-IIdHuXNL0o/\n'
            '  duration: "6:55"\n'
            '  platform: douyin\n'
        )
        yaml_path = self.setup_fixture(make_base_data(), countries)
        # 输入 yaml 解析：duration 是字符串而非 sexagesimal int
        doc = yaml.safe_load(yaml_path.read_text(encoding='utf-8'))
        self.assertEqual(doc['countries'][0]['duration'], '6:55')
        self.assertIsInstance(doc['countries'][0]['duration'], str)
        self.assertEqual(len(doc['target']), 2)
        self.assertEqual(doc['target'][0]['data'], 'data/_countries-data.json')
        # apply 后 json 写入的是字符串时长
        r = self.run_script(yaml_path, '--apply')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        row = next(x for x in self.read_json()['data'] if x['country_zh'] == '缅甸')
        self.assertEqual(row['videos'][0]['duration'], '6:55')

    def test_02_duration_int_tolerance(self):
        """duration int 容错：415 → "6:55"（仅 M:SS）；H:MM:SS 必须引号，
        未引号 3723 不在容错语义内，不自动归一化。"""
        countries = (
            '- country_zh: 缅甸\n'
            '  title: 缅甸-散装缅甸\n'
            '  url: https://v.douyin.com/-IIdHuXNL0o/\n'
            '  duration: 415\n'
            '  platform: douyin\n'
            '- country_zh: 伊朗\n'
            '  title: 伊朗-长视频\n'
            '  url: https://v.douyin.com/1IxN2ag0e8U/\n'
            '  duration: 3723\n'
            '  platform: douyin\n'
        )
        yaml_path = self.setup_fixture(make_base_data(), countries)
        r = self.run_script(yaml_path, '--apply')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        rows = {x['country_zh']: x for x in self.read_json()['data']}
        self.assertEqual(rows['缅甸']['videos'][0]['duration'], '6:55')
        # 伊朗新增条目的 3723 不归一化为 "1:02:03"，保留原值字符串
        iran_new = rows['伊朗']['videos'][-1]
        self.assertEqual(iran_new['title'], '伊朗-长视频')
        self.assertNotEqual(iran_new['duration'], '1:02:03')
        self.assertEqual(iran_new['duration'], '3723')

    def test_03_f3_missing_country_exit1_no_write(self):
        """F3 校验：yaml 含 json 不存在的国家键 → exit 1，json/yaml/html 零写盘。"""
        countries = (
            '- country_zh: 越南\n'
            '  title: 越南-测试\n'
            '  url: https://v.douyin.com/VN123/\n'
            '  duration: "3:00"\n'
        )
        yaml_path = self.setup_fixture(make_base_data(), countries)
        before = self.snapshot()
        r = self.run_script(yaml_path, '--apply')
        self.assertEqual(r.returncode, 1)
        self.assertIn('越南', r.stdout)
        self.assert_unchanged(before)

    def test_04_all_exist_exit0_no_write(self):
        """全存在中断：yaml 视频均已含于 json → 打印提示 exit 0，零写盘。"""
        countries = (
            '- country_zh: 伊朗\n'
            '  title: 中东为何永不团结\n'
            '  url: https://v.douyin.com/Ez_SJIkymk0/\n'
            '  duration: "4:54"\n'
            '  platform: douyin\n'
        )
        yaml_path = self.setup_fixture(make_base_data(), countries)
        before = self.snapshot()
        r = self.run_script(yaml_path, '--apply')
        self.assertEqual(r.returncode, 0)
        self.assertIn('均已包含', r.stdout)
        self.assert_unchanged(before)

    def test_05_append_and_url_strip_dedupe(self):
        """补充更新：缅甸 0→1、伊朗 1→2（url 去重）；yaml url 尾部空格
        strip 后去重/回写（既有 url 带空格不重复新增，新 url 写盘无空白）。"""
        countries = (
            '- country_zh: 缅甸\n'
            '  title: 缅甸-散装缅甸\n'
            '  url: https://v.douyin.com/-IIdHuXNL0o/   \n'
            '  duration: "6:55"\n'
            '  platform: douyin\n'
            '- country_zh: 伊朗\n'
            '  title: 伊朗-美国为什么征服不了伊朗\n'
            '  url: https://v.douyin.com/1IxN2ag0e8U/\n'
            '  duration: "11:38"\n'
            '  platform: douyin\n'
            '- country_zh: 伊朗\n'
            '  title: 中东为何永不团结\n'
            '  url: https://v.douyin.com/Ez_SJIkymk0/  \n'
            '  duration: "4:54"\n'
            '  platform: douyin\n'
            # HG-SEC-084: 第三条与 json 既有伊朗视频同 url 且 title 相同 →
            # v1.2 下保持 skip 语义（勿用「（重复）」后缀，否则漂移为 update）
        )
        yaml_path = self.setup_fixture(make_base_data(), countries)
        r = self.run_script(yaml_path, '--apply')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        rows = {x['country_zh']: x for x in self.read_json()['data']}
        # 缅甸 0→1，url 尾部空格已 strip
        self.assertEqual(len(rows['缅甸']['videos']), 1)
        self.assertEqual(rows['缅甸']['videos'][0]['url'],
                         'https://v.douyin.com/-IIdHuXNL0o/')
        # 伊朗 1→2，既有 url（strip 后）不重复新增
        self.assertEqual(len(rows['伊朗']['videos']), 2)
        urls = [v['url'] for v in rows['伊朗']['videos']]
        self.assertEqual(len(set(urls)), 2)
        # 回写 yaml：url 无尾部空白（镜像内容断言见 test_07）
        yaml_doc = self.read_yaml()
        for c in yaml_doc['countries']:
            if c['country_zh'] == '缅甸':
                self.assertEqual(c['url'], 'https://v.douyin.com/-IIdHuXNL0o/')

    def test_06_yaml_internal_duplicate_url_first_wins(self):
        """yaml 内部重复 url：同国同 url 两条 → 仅取首条。"""
        countries = (
            '- country_zh: 缅甸\n'
            '  title: 第一条\n'
            '  url: https://v.douyin.com/-IIdHuXNL0o/\n'
            '  duration: "6:55"\n'
            '- country_zh: 缅甸\n'
            '  title: 第二条（应忽略）\n'
            '  url: https://v.douyin.com/-IIdHuXNL0o/\n'
            '  duration: "1:00"\n'
        )
        yaml_path = self.setup_fixture(make_base_data(), countries)
        r = self.run_script(yaml_path, '--apply')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        row = next(x for x in self.read_json()['data'] if x['country_zh'] == '缅甸')
        self.assertEqual(len(row['videos']), 1)
        self.assertEqual(row['videos'][0]['title'], '第一条')

    def test_07_w_global_mirror(self):
        """W 回写：apply 后 yaml countries 段 == json 全部 videos（target 保留）。"""
        countries = (
            '- country_zh: 缅甸\n'
            '  title: 缅甸-散装缅甸\n'
            '  url: https://v.douyin.com/-IIdHuXNL0o/\n'
            '  duration: "6:55"\n'
            '  platform: douyin\n'
            '- country_zh: 伊朗\n'
            '  title: 伊朗-美国为什么征服不了伊朗\n'
            '  url: https://v.douyin.com/1IxN2ag0e8U/\n'
            '  duration: "11:38"\n'
            '  platform: douyin\n'
        )
        yaml_path = self.setup_fixture(make_base_data(), countries)
        r = self.run_script(yaml_path, '--apply')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        json_doc = self.read_json()
        yaml_doc = self.read_yaml()
        # target 段保留
        self.assertEqual(yaml_doc['target'], [{'data': 'data/_countries-data.json'},
                                              {'html': 'demos/countries-table.html'}])
        # countries 段 == json 全部 videos 展平（顺序、字段一致；platform 写现值）
        expected = []
        for row in json_doc['data']:
            for v in (row.get('videos') or []):
                item = {'country_zh': row['country_zh'], 'title': v['title'],
                        'url': v['url'], 'duration': v['duration']}
                if v.get('platform'):
                    item['platform'] = v['platform']
                expected.append(item)
        self.assertEqual(yaml_doc['countries'], expected)
        # 回写 duration 全部为带引号字符串（parse 回来不是 int）
        for c in yaml_doc['countries']:
            self.assertIsInstance(c['duration'], str)

    def test_08_platform_fallback_by_url_host(self):
        """platform 兜底：yaml 缺 platform + v.douyin.com → douyin（json 补全）。"""
        countries = (
            '- country_zh: 缅甸\n'
            '  title: 缅甸-散装缅甸\n'
            '  url: https://v.douyin.com/-IIdHuXNL0o/\n'
            '  duration: "6:55"\n'
            '- country_zh: 中国\n'
            '  title: 中国-bilibili视频\n'
            '  url: https://www.bilibili.com/video/BV123\n'
            '  duration: "10:00"\n'
        )
        yaml_path = self.setup_fixture(make_base_data(), countries)
        r = self.run_script(yaml_path, '--apply')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        rows = {x['country_zh']: x for x in self.read_json()['data']}
        self.assertEqual(rows['缅甸']['videos'][0]['platform'], 'douyin')
        self.assertEqual(rows['中国']['videos'][1]['platform'], 'bilibili')

    def test_09_dry_run_zero_write(self):
        """dry-run（默认无参）：预览输出新增明细与计划，json/yaml/html 零写盘。"""
        countries = (
            '- country_zh: 缅甸\n'
            '  title: 缅甸-散装缅甸\n'
            '  url: https://v.douyin.com/-IIdHuXNL0o/\n'
            '  duration: "6:55"\n'
            '  platform: douyin\n'
        )
        yaml_path = self.setup_fixture(make_base_data(), countries)
        before = self.snapshot()
        r = self.run_script(yaml_path)  # 无参 = dry-run
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn('[预览] 新增 1 条', r.stdout)
        self.assertIn('缅甸', r.stdout)
        self.assertIn('使用 --apply 执行', r.stdout)
        self.assert_unchanged(before)
        # 显式 --dry-run 同样零写盘
        before2 = self.snapshot()
        r2 = self.run_script(yaml_path, '--dry-run')
        self.assertEqual(r2.returncode, 0, r2.stdout + r2.stderr)
        self.assertIn('[预览] 新增 1 条', r2.stdout)
        self.assert_unchanged(before2)

    def test_10_rebuild_html_contains_video_title_unchanged(self):
        """E 重建：apply 后 html 含新视频标题文本、<title> 不变、github-corner 保留（FIND-002）。"""
        countries = (
            '- country_zh: 缅甸\n'
            '  title: 缅甸-散装缅甸\n'
            '  url: https://v.douyin.com/-IIdHuXNL0o/\n'
            '  duration: "6:55"\n'
            '  platform: douyin\n'
        )
        yaml_path = self.setup_fixture(make_base_data(), countries)
        # 预置旧产物：含 github-corner（HG-SEC-014 demo 页规范），E 重建应提取并透传
        old_html = self.tmp / 'demos' / 'countries-table.html'
        old_html.parent.mkdir(parents=True, exist_ok=True)
        old_html.write_text(
            '<html><head><title>测试国家表</title></head><body>'
            '<a href="https://github.com/imjaden/html-gen.cli" class="github-corner">c</a>'
            '<div class="data-table"></div></body></html>',
            encoding='utf-8')
        r = self.run_script(yaml_path, '--apply')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn('[重建] demos/countries-table.html', r.stdout)
        html = (self.tmp / 'demos' / 'countries-table.html').read_text(encoding='utf-8')
        self.assertIn('<title>测试国家表</title>', html)
        self.assertIn('缅甸-散装缅甸', html)
        self.assertIn('中东为何永不团结', html)
        # FIND-002：corner 保留（提取旧 html 的 repo URL 透传 --github-url）
        self.assertIn('github-corner', html)
        self.assertIn('href="https://github.com/imjaden/html-gen.cli"', html)

    # ── CL004: rebuild 显式三参数 / --empty-video / 缺省 yaml 路径 ──

    def test_11_apply_rebuild_prints_full_cmd(self):
        """E 重建命令含 --github-url/--home-url/--favicon 三参数（[执行] 打印行断言,
        HG-SEC-079: HTML_GEN_STUB 仅识别 --github-url, 新增断言走打印行路径）。"""
        countries = (
            '- country_zh: 缅甸\n'
            '  title: 缅甸-散装缅甸\n'
            '  url: https://v.douyin.com/-IIdHuXNL0o/\n'
            '  duration: "6:55"\n'
            '  platform: douyin\n'
        )
        yaml_path = self.setup_fixture(make_base_data(), countries)
        r = self.run_script(yaml_path, '--apply')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        # [执行] 打印行含三参数与缺省默认值（target 无 rebuild 节 → 固定默认; 无旧 html → 默认 github）
        self.assertRegex(r.stdout,
                         r'\[执行\].*--github-url https://github\.com/imjaden/html-gen\.cli')
        self.assertRegex(r.stdout,
                         r'\[执行\].*--home-url https://html-gen\.cli\.jaden\.tech/')
        self.assertRegex(r.stdout,
                         r'\[执行\].*--favicon https://www\.jaden\.tech/static/img/favicon\.png')
        # 重建产物仍含新视频（stub 忽略未知参数, 行为不变）
        html = (self.tmp / 'demos' / 'countries-table.html').read_text(encoding='utf-8')
        self.assertIn('缅甸-散装缅甸', html)

    def test_12_empty_video_lists_and_mutex(self):
        """--empty-video: 逐行「首字段 (次字段)」+ 空字段 (空) + 底部计数 + 零写盘；
        与 --apply 同用 → argparse exit 2（三向互斥）。"""
        data_doc = {
            "title": "空 videos 测试",
            "data": [
                {"country_zh": "缅甸", "country_en": "Myanmar"},
                {"country_zh": "中国", "country_en": ""},
                {"country_zh": "", "country_en": "EmptyZh"},
                {"country_zh": "伊朗", "country_en": "Iran", "videos": [
                    {"title": "x", "url": "https://v.douyin.com/x/"}]},
            ],
        }
        yaml_path = self.setup_fixture(data_doc, '')
        before = self.snapshot()
        r = self.run_script(yaml_path, '--empty-video')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn('缅甸 (Myanmar)', r.stdout)
        self.assertIn('中国 ((空))', r.stdout)
        # 首字段为空 → 跳过取次非空字段 EmptyZh; 无第二个非空 → (空)（K1: 取前两个非空字段）
        self.assertIn('EmptyZh ((空))', r.stdout)
        self.assertNotIn('伊朗', r.stdout)  # 有 videos 的行不列出
        self.assertIn('共 3 条 videos 为空', r.stdout)
        self.assert_unchanged(before)
        # 三向互斥: --empty-video + --apply → argparse exit 2
        r2 = self.run_script(yaml_path, '--empty-video', '--apply')
        self.assertEqual(r2.returncode, 2)
        self.assert_unchanged(before)

    def test_13_default_yaml_path(self):
        """无参运行 → 缺省 cache/data/_countries-data.videos.yaml（项目根解析, dry-run）。"""
        countries = (
            '- country_zh: 缅甸\n'
            '  title: 缅甸-散装缅甸\n'
            '  url: https://v.douyin.com/-IIdHuXNL0o/\n'
            '  duration: "6:55"\n'
            '  platform: douyin\n'
        )
        self.setup_fixture(make_base_data(), countries)  # 写 data json（target 指向它）
        default_dir = self.tmp / 'cache' / 'data'
        default_dir.mkdir(parents=True, exist_ok=True)
        (default_dir / '_countries-data.videos.yaml').write_text(
            YAML_TEMPLATE.format(countries=countries), encoding='utf-8')
        before = self.snapshot()
        r = self.run_script(None)  # 无参 → 缺省 yaml
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn('[预览] 新增 1 条', r.stdout)
        self.assertIn('使用 --apply 执行', r.stdout)
        self.assert_unchanged(before)

    # ── v1.2 (HTML-GEN-CL006): 三态增量 — 更新/跳过 + 全包含统计 ──

    def test_14_update_title_apply(self):
        """v1.2 更新 apply：yaml 同 url 新 title → json 既有条目 title 覆盖；
        yaml 镜像回写带新值；行数不变。"""
        countries = (
            '- country_zh: 伊朗\n'
            '  title: 中东为何永不团结#阿拉伯国家为何分裂\n'
            '  url: https://v.douyin.com/Ez_SJIkymk0/\n'
            '  duration: "4:54"\n'
            '  platform: douyin\n'
        )
        yaml_path = self.setup_fixture(make_base_data(), countries)
        r = self.run_script(yaml_path, '--apply')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn('[同步] 更新 1 条视频（title 变更）', r.stdout)
        row = next(x for x in self.read_json()['data'] if x['country_zh'] == '伊朗')
        self.assertEqual(len(row['videos']), 1)  # 行数不变（不新增不删除）
        self.assertEqual(row['videos'][0]['title'],
                         '中东为何永不团结#阿拉伯国家为何分裂')
        # yaml 镜像回写带新值（下次运行 url+title 相同 → 跳过，幂等闭环）
        yaml_doc = self.read_yaml()
        self.assertIn('中东为何永不团结#阿拉伯国家为何分裂',
                      [c['title'] for c in yaml_doc['countries']])

    def test_15_update_only_no_early_exit(self):
        """v1.2 G 判定：所有 url 已存在但 1 条 title 不同 → apply 执行写盘
        （非「均已包含」），修复「仅更新无新增误判中断」。"""
        countries = (
            '- country_zh: 伊朗\n'
            '  title: 中东为何永不团结#阿拉伯国家为何分裂\n'
            '  url: https://v.douyin.com/Ez_SJIkymk0/\n'
            '  duration: "4:54"\n'
            '  platform: douyin\n'
            '- country_zh: 中国\n'
            '  title: 既有视频\n'
            '  url: https://v.douyin.com/OLD123/\n'
            '  duration: "2:30"\n'
            '  platform: douyin\n'
        )
        yaml_path = self.setup_fixture(make_base_data(), countries)
        r = self.run_script(yaml_path, '--apply')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertNotIn('均已包含', r.stdout)
        self.assertIn('[同步] 更新 1 条视频（title 变更）', r.stdout)
        row = next(x for x in self.read_json()['data'] if x['country_zh'] == '伊朗')
        self.assertEqual(row['videos'][0]['title'],
                         '中东为何永不团结#阿拉伯国家为何分裂')

    def test_16_dry_run_update_preview(self):
        """v1.2 dry-run 更新预览：含 `[预览] 更新 N 条（url 已存在, title 变更）`
        与旧→新 title + url；零写盘。"""
        countries = (
            '- country_zh: 伊朗\n'
            '  title: 中东为何永不团结#阿拉伯国家为何分裂\n'
            '  url: https://v.douyin.com/Ez_SJIkymk0/\n'
            '  duration: "4:54"\n'
            '  platform: douyin\n'
        )
        yaml_path = self.setup_fixture(make_base_data(), countries)
        before = self.snapshot()
        r = self.run_script(yaml_path)  # 无参 = dry-run
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn('[预览] 更新 1 条（url 已存在, title 变更）', r.stdout)
        self.assertIn('中东为何永不团结 → 中东为何永不团结#阿拉伯国家为何分裂',
                      r.stdout)
        self.assertIn('https://v.douyin.com/Ez_SJIkymk0/', r.stdout)
        self.assertIn('使用 --apply 执行', r.stdout)
        self.assert_unchanged(before)

    def test_17_all_included_statistics(self):
        """v1.2 全包含统计：`（yaml 检查 N 条 / 涉及 M 个国家）`，N/M 与去重口径
        一致（yaml 内部同 country+url 去重；畸形条目缺 url 不计入 N）；零写盘。"""
        countries = (
            '- country_zh: 伊朗\n'
            '  title: 中东为何永不团结\n'
            '  url: https://v.douyin.com/Ez_SJIkymk0/\n'
            '  duration: "4:54"\n'
            '  platform: douyin\n'
            '- country_zh: 中国\n'
            '  title: 既有视频\n'
            '  url: https://v.douyin.com/OLD123/\n'
            '  duration: "2:30"\n'
            '  platform: douyin\n'
            '- country_zh: 伊朗\n'
            '  title: 中东为何永不团结\n'
            '  url: https://v.douyin.com/Ez_SJIkymk0/\n'
            '  duration: "4:54"\n'
            '  platform: douyin\n'
            # 畸形条目（缺 url）被 warn+continue，不计入 N（HG-SEC-085）
            '- country_zh: 缅甸\n'
            '  title: 无 url 畸形条目\n'
        )
        yaml_path = self.setup_fixture(make_base_data(), countries)
        before = self.snapshot()
        r = self.run_script(yaml_path, '--apply')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn('均已包含', r.stdout)
        self.assertIn('（yaml 检查 2 条 / 涉及 2 个国家）', r.stdout)
        self.assert_unchanged(before)

    def test_18_update_keep_existing_when_missing(self):
        """HG-SEC-081 回归护栏：更新条目 yaml 缺 duration/platform 或 duration 空
        → json 既有 duration/platform 保留，不写 'None'（判空用 raw 值）。"""
        countries = (
            '- country_zh: 伊朗\n'
            '  title: 中东为何永不团结#阿拉伯国家为何分裂\n'
            '  url: https://v.douyin.com/Ez_SJIkymk0/\n'
            # 缺 duration/platform
            '- country_zh: 中国\n'
            '  title: 既有视频#更新\n'
            '  url: https://v.douyin.com/OLD123/\n'
            '  duration: ""\n'
            '  platform: douyin\n'
        )
        yaml_path = self.setup_fixture(make_base_data(), countries)
        r = self.run_script(yaml_path, '--apply')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        rows = {x['country_zh']: x for x in self.read_json()['data']}
        iran = rows['伊朗']['videos'][0]
        self.assertEqual(iran['title'], '中东为何永不团结#阿拉伯国家为何分裂')
        # 伊朗缺 duration → 保留 json 既有 '4:54'；缺 platform → detect 兜底命中同值 douyin
        self.assertEqual(iran['duration'], '4:54')
        self.assertEqual(iran['platform'], 'douyin')
        china = rows['中国']['videos'][0]
        self.assertEqual(china['title'], '既有视频#更新')
        # duration 空串 → 保留 json 既有 '2:30'
        self.assertEqual(china['duration'], '2:30')
        # 全 json 无 'None' 字符串（normalize_duration(None) 防护）
        self.assertNotIn('None', json.dumps(self.read_json(), ensure_ascii=False))

    def test_19_update_platform_detect_fallback(self):
        """U1：更新条目 yaml 缺 platform 但 url 可识别 → json platform 更新为
        识别值（与新增条目 C1 一致）。"""
        data_doc = make_base_data()
        # 既有值与 url host 不符（bilibili vs v.douyin.com）→ detect 兜底应覆盖
        data_doc['data'][2]['videos'][0]['platform'] = 'bilibili'
        countries = (
            '- country_zh: 中国\n'
            '  title: 既有视频#更新\n'
            '  url: https://v.douyin.com/OLD123/\n'
            '  duration: "2:30"\n'
        )
        yaml_path = self.setup_fixture(data_doc, countries)
        r = self.run_script(yaml_path, '--apply')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        china = next(x for x in self.read_json()['data']
                     if x['country_zh'] == '中国')['videos'][0]
        self.assertEqual(china['title'], '既有视频#更新')
        self.assertEqual(china['platform'], 'douyin')  # detect 兜底更新

    def test_20_empty_title_skips_update(self):
        """HG-SEC-085 回归护栏：yaml title 为空且 url 已存在 → 跳过，json 既有
        title 保留（2A 清空防护，防空 title 覆盖既有标题）。"""
        countries = (
            '- country_zh: 伊朗\n'
            '  title: ""\n'
            '  url: https://v.douyin.com/Ez_SJIkymk0/\n'
            '  duration: "4:54"\n'
            '  platform: douyin\n'
        )
        yaml_path = self.setup_fixture(make_base_data(), countries)
        r = self.run_script(yaml_path, '--apply')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn('均已包含', r.stdout)
        row = next(x for x in self.read_json()['data'] if x['country_zh'] == '伊朗')
        self.assertEqual(row['videos'][0]['title'], '中东为何永不团结')


if __name__ == '__main__':
    unittest.main()
