---
title: 转交：html-gen table 模板壳变更（CL036）—— console 页重生成 + 四个必查点
topic: html-gen-cl036-shell
type: handoff
version: 1.0
date: 2026-11-12
author: ops (html-gen.cli)
---

# 转交：html-gen table 模板壳变更（CL036）

- 来件方：`html-gen.cli`（本仓） · 指向：`hermes-manager`（`web_console_lib` + console 生成器）
- 性质：**去件（只提变更与检查点）**，本仓不改对方任何代码
- 落地提交：`af6994f`（本仓 `main`，**评审后已推送**；若需精确对齐，以 `git log -1 -- layout-table.html` 为准）
- 起因：`http://jaden.local:8081/shortcuts/index.html` 目视两问题（分享按钮形同独占一行 / 字号行高偏小），
  定位后确认「壳 = html-gen table 模板，页面 = 你方生成器产出」，故模板侧已改，你方重生成即继承

---

## 1. 模板侧改了什么（`html-gen` v3.4 模板，commit `af6994f`）

| # | 变更 | 影响面 |
|---|---|---|
| S1 | `shareBtn`/`home-link` 从 `.tabs-actions` **移入 `.table-header`**（紧随 `#statTotal` pill，`.flex-1` 之前）；图标 `↗️` → `🔗` | 见 §3 检查点 ① |
| S1b | 无 tab **且** `.tabs-actions` 为空 ⇒ `.tabs-row` 挂 `no-tabs` 整行 `display:none`（开标签保持逐字 `<div class="tabs-row">`，不加 id/属性 —— 你方 `normalize_skeleton` 用精确串定位） | 单视图 console 页不再出现"只有按钮的一行" |
| S2 | 字号收口 `--table-fs`：default 0.82rem/`8px 10px`、compact 0.7rem/`2px 8px`、comfortable 0.94rem/`12px 14px`；`th`(×0.88)、pill(×0.86/×0.8) 联动 | 所有 table 页行高 35→38px、正文 12→13.1px |
| S2b | 密度入口**恒渲染**（原 `tabCount>1 \|\| density!=='default'` 门控已去）；`options.density` 可设页面默认；`?density=` 覆盖并写进分享 URL | console 页可在 payload 用 `options.density` 指定默认档 |
| D9 | `html-gen help <topic> --json`：机器可读契约（`data.contract` + `data.template_stamps`） | 见 §3 检查点 ③ |
| D10 | `table --strict`：未知配置键 ⇒ exit 2；告警带稳定令牌 `WARN_UNKNOWN_KEY`（stderr，`--quiet` 不吞） | 见 §3 检查点 ② |
| D11 | 产物 `<head>` 注入 `<meta name="generator" content="html-gen v3.4+tpl{sha8}">` | 见 §3 检查点 ④ |

兼容性：JSON 侧无破坏性改动（`options.density` 是新增可选键，旧 payload 行为不变）。

## 2. 你方需要重生成的范围（实测：**4 页**，不是全部 8 页）

| 页 | 模板 | 生成链 | 生成入口 |
|---|---|---|---|
| `web/cron/index.html` | table | `gen_split()` → `normalize_skeleton()` | `scripts/web-console/cron-web-refresh.py` |
| `web/memory/index.html` | table | 同上 | `scripts/web-console/memory-web-refresh.py` |
| `web/session/index.html` | table | 同上 | `scripts/web-console/sessions-web-refresh.py` |
| `web/shortcuts/index.html` | table | `gen_page()`（**不调** `normalize_skeleton`） | `scripts/hm-shortcuts-page.py` |

不在本件范围（实测归类）：`web/knowledge/`（knowledge 模板）、`web/feishu/`、`web/todo/`（非 html-gen 产物）、
`web/1acl/`（**自建壳**：有 `.tabs-row`/`.tabs-actions`，无 `.ratio-wrap`/`.flex-1`，不走本链 —— 它有同款
「分享按钮独占一行 + 小字号」观感，若要修按自建壳处理，见 §5）。

## 3. 四个必查点（顺序即风险序）

**① 骨架兼容（分两种页，判据不同）**
- `gen_split()` 三页（cron / memory / session）：`normalize_skeleton()` 把 `.ratio-wrap` / `.col-toggle-wrap`
  搬进 `.tabs-actions`，抓不到即 `RuntimeError`（exit 2、保旧壳）。重生成后应满足：
  `.tabs-actions` 内只有 `▦`/`⚙` 两个控件 ⇒ **`.tabs-row` 不折叠**（有子节点）。
- `gen_page()` 的 shortcuts：不经 `normalize_skeleton`，`const TABS = [];` 且 `.tabs-actions` 为空
  ⇒ **`.tabs-row` 应折叠为 `display:none`**（这正是 §4 想要的「不再有空白操作行」）。
- 折叠判定看两处：`#tabsBar` **与** `.tabs-actions` **皆空**才折叠（有一处非空即保留）。

**② `run_html_gen()` 应开始读 stderr（治静默漂移）**
现状：只 `returncode != 0` 时才把 stderr 拼进异常，且带 `--quiet` ⇒ 未知键告警 100% 被丢。
建议：`rc == 0` 时若 stderr 含 `WARN_UNKNOWN_KEY`，记一条 warning（或直接用 `table --strict` 让拼错键当场失败）。

```python
if r.returncode != 0:
    raise RuntimeError(...)
warns = [l for l in (r.stderr or '').splitlines() if 'WARN_UNKNOWN_KEY' in l]
if warns:
    print(f'[html-gen] 未知配置键 {len(warns)} 条: {warns[:3]}', file=sys.stderr)
```

**覆盖面如实说明**：未知键检查只覆盖 3 类 —— `columns[].<属性>`、`columns[].type`、`options.<键>`（含
`options.feedback.<子键>`）；**不覆盖** `data[]` 行内字段名、`col.actions[]`/`col.videos` 嵌套项。
所以它是"拼错列属性/选项"的护栏，不是全量 schema 校验。

**③ 契约比对（建议加到你方生成器启动处）**

```bash
html-gen help table --json | python3 -c 'import json,sys; d=json.load(sys.stdin)["data"]; \
  print(d["version"], d["template_stamps"]["table"]); \
  print(sorted(e[0] for e in d["contract"]["data"]["options"]))'
```
把 `options` 键集合与你方 payload 的键做交集校验，可在 CI 拦住"模板删键/改名 → 页面静默少功能"。

**④ 产物版本戳（drift 巡检只扫这 4 页）**

```bash
grep -o 'content="html-gen v[^"]*"' \
  web/cron/index.html web/memory/index.html web/session/index.html web/shortcuts/index.html \
  | sort | uniq -c
```
指纹不一致的页 = 该重生成。（`knowledge` / `feishu` / `todo` / `1acl` 不看戳：它们不是 table 模板产物，
全局 `web/*/index.html` 扫会得到永久噪声。）

## 4. 视觉验收（三条，按两类页分别看）

1. cron/memory/session：首屏「标题 + `N 条` + 🔗」同行；其下 tab 行只承载 tab + `▦`/`⚙`（不空、不折叠）。
2. shortcuts：首屏「标题 + `N 条` + 🔗」同行，**tab 行整行消失**（无空白行）。
3. 任一页：行高 ≈ 38px、正文 13.1px（原 35/12），⚙ 面板「密度」三档恒在；切「舒适」后 URL 带
   `?density=comfortable`，复制链接可还原该视图。

## 5. 边界

- 本件不改你方任何文件；重生成与兼容改造由你方发起。
- `web/1acl/` 自建壳（及 daily-checker 的 fork 移植件）不在本件范围：前者如需修，按其壳自身 CSS 处理；
  后者应迁回调用 html-gen（另议）。
- 若希望 console 页固定某密度档，在 payload 写 `options.density`（`default|compact|comfortable`）。
