# 转交：html-gen table 模板 v3.4 壳变更（CL036）—— console 页需重生成 + 两处兼容检查

- 来件方：`html-gen.cli`（本仓） · 指向：`hermes-manager`（`web_console_lib` / 8 个 console 生成器）
- 日期：2026-11-12 · 性质：**去件（只提变更与检查点）**，本仓不改对方任何代码
- 起因：`http://jaden.local:8081/shortcuts/index.html` 目视两问题（分享按钮形同独占一行 / 字号行高偏小），
  定位后确认「壳 = html-gen table 模板，页面 = 你方生成器产出」，故模板侧已改，你方重生成即继承

---

## 1. 模板侧改了什么（`html-gen` v3.4 模板，commit `b217461`）

| # | 变更 | 影响面 |
|---|---|---|
| S1 | `shareBtn`/`home-link` 从 `.tabs-actions` **移入 `.table-header`**（紧随 `#statTotal` pill，`.flex-1` 之前）；图标 `↗️` → `🔗` | 见 §3 检查点 ①（你方 M11 后处理仍可工作） |
| S1b | 无 tab 且 `.tabs-actions` 为空 ⇒ `.tabs-row` 挂 `no-tabs` 整行 `display:none`（**开标签保持逐字 `<div class="tabs-row">`，不加 id/属性** —— 你方 `normalize_skeleton` 用精确串定位） | 单视图 console 页不再出现"只有按钮的一行" |
| S2 | 字号收口 `--table-fs`：default 0.82rem/`8px 10px`、compact 0.7rem/`2px 8px`、comfortable 0.94rem/`12px 14px`；`th`(×0.88)、pill(×0.86/×0.8) 联动 | 所有 table 页行高 35→38px、正文字号 12→13.1px |
| S2b | 密度入口**恒渲染**（原 `tabCount>1 || density!=='default'` 门控已去）；`options.density` 可设页面默认；`?density=` 覆盖并写进分享 URL | console 页可在 payload `options.density` 指定默认档 |
| D9 | `html-gen help <topic> --json`：机器可读契约（`data.contract` + `data.template_stamps`） | 见 §3 检查点 ② |
| D10 | `table --strict`：未知配置键 ⇒ exit 2；告警加稳定令牌 `WARN_UNKNOWN_KEY`（stderr，`--quiet` 不吞） | 见 §3 检查点 ③ |
| D11 | 产物 `<head>` 注入 `<meta name="generator" content="html-gen v3.4+tpl{sha8}">` | 见 §3 检查点 ④ |

兼容性：JSON 侧无破坏性改动（`options.density` 是新增可选键；旧 payload 行为不变）。

## 2. 你方需要做的（重生成 8 个 console 页）

```bash
# 逐页重生成（命令形如，实际以各生成器为准）
python3 scripts/hm-shortcuts-page.py            # web/shortcuts/index.html
# …其余 console 页各自的生成脚本
```

生成链不变：`hm-shortcuts-page.py` → `web_console_lib.gen_page()` → `run_html_gen()`（PATH 里的 `html-gen`，
实测 `~/.local/bin/html-gen` → `~/CodeSpace/html-gen.cli/html-gen.py`）→ 菜单/页脚注入 → `normalize_skeleton()`。

## 3. 四个必查点（顺序即风险序）

**① `normalize_skeleton()` 锚点仍在（最重要）**
它把 `.ratio-wrap` / `.col-toggle-wrap` 从 `.table-header` 搬进 `.tabs-actions`，抓不到即 `RuntimeError`（exit 2、保旧壳）。
本批**没有删这两块**，也没删 `.tabs-row` / `.tabs-actions` 容器 —— 但 `.tabs-actions` 现在默认为空（分享/Home 已迁走）。
⇒ 重生成后应满足：`.tabs-actions` 内只有 `▦`/`⚙` 两个控件，`.tabs-row` 因有子节点而**不折叠**（`no-tabs` 不出现）。
若你在 `.tabs-actions` 里还塞过别的东西，请核一眼 `syncTabsRow()` 的判定（只看 `.tabs-row` 是否存在 `.tabs-actions` 子节点）。

**② `run_html_gen()` 应开始读 stderr（治静默漂移）**
现状：只 `returncode != 0` 时才把 stderr 拼进异常，且带 `--quiet` ⇒ 未知键告警 100% 被丢。
建议：`rc == 0` 时若 `stderr` 含 `WARN_UNKNOWN_KEY`，记一条 warning 日志（或直接改调用 `table --strict`，让拼错键在生成时炸）。
参考实现（你方代码，本仓不代改）：

```python
if r.returncode != 0:
    raise RuntimeError(...)
warns = [l for l in (r.stderr or '').splitlines() if 'WARN_UNKNOWN_KEY' in l]
if warns:
    print(f'[html-gen] 未知配置键 {len(warns)} 条: {warns[:3]}', file=sys.stderr)
```

**③ 契约比对（可选，建议加到你方生成器启动处）**

```bash
html-gen help table --json | python3 -c 'import json,sys; d=json.load(sys.stdin)["data"]; \
  print(d["version"], d["template_stamps"]["table"]); \
  print(sorted(e[0] for e in d["contract"]["data"]["options"]))'
```
把 `options` 键集合与你方 payload 的键做交集校验，可在 CI 里拦住"模板删键/改名 → 页面静默少功能"。

**④ 产物版本戳**
重生成后每页 `<head>` 应出现 `<meta name="generator" content="html-gen v3.4+tpl{sha8}">`。
据此可做 drift 巡检：`grep -o 'content="html-gen v[^"]*"' web/*/index.html | sort | uniq -c`，
版本/指纹不一致的页 = 该重生成。

## 4. 你方视觉验收（建议三条）

1. 单视图页（如 shortcuts）：首屏顺序应为「标题 + `N 条` + 🔗」同一行，其上不再有空白操作行；
2. 表格行高 ≈ 38px、正文 13.1px（原 35px / 12px），⚙ 面板里「密度」三档恒在；
3. 切到「舒适」后 URL 带 `?density=comfortable`，复制链接可还原该视图。

## 5. 边界

- 本件不改你方任何文件；重生成与兼容改造由你方发起。
- 你方尚未迁移的 fork（如 daily-checker 的 `index.html` 移植件）不在本件范围，另行处理。
- 若你方希望 console 页固定用某一密度档，请在 payload 写 `options.density`（`default|compact|comfortable`）。
