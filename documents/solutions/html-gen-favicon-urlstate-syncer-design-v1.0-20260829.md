# html-gen favicon 默认注入 + table URL 状态分享 + syncer 参数体系 — 设计 v1.0

- 编号: HTML-GEN-CL004
- 日期: 2026-08-29
- 状态: 设计定稿（决策清单 1B 2A 3A 4A 5A 已确认，待 review 审计）
- 范围: html-gen.py / layout-doc|table|knowledge|slide.html / scripts/tool-table-videos-syncer.py / tests / 文档

## 一、需求来源

用户在本会话探讨三项改进（先探讨后实施）：

1. 生成产物无 favicon：模板给出默认 favicon，`--favicon` 显式覆盖；syncer 重建时打印执行的 html-gen 命令，并显式传入 github、demo、favicon 三项。
2. demos/countries-table.html 通过拷贝 URL 分享指定页面信息：保存选中的页签、筛选关键字、当前分栏展示的行；刷新页面后恢复；添加拷贝图标按钮复制 URL 到系统剪贴板。
3. tool-table-videos-syncer.py 参数体系：help、empty-video、`<yaml-path>` 等；empty-video 打印 videos 列表为空的行。

## 二、决策记录（探讨确认清单）

| 项 | 决策 | 含义 |
|:---|:---|:---|
| A | A1 | 模板加 `<!--FAVICON-->` 占位，CLI 默认注入 DEFAULT_FAVICON，`--favicon <url>` 覆盖，传空串禁用；四子命令 + env `HTML_GEN_FAVICON` 兜底 |
| B | B1 | "demo" 即现有 `--home-url`（demo 首页入口），syncer 重建显式传 demo 首页 URL |
| C | C1 | 默认 favicon = https://www.jaden.tech/static/img/favicon.png |
| D | D1 | syncer 打印 `[执行] ' '.join(shlex.quote(a))` 完整命令行 |
| E | E1 | 纯 URL 同步：tab/q/split 状态变化即 history.replaceState，刷新/新开页/分享均恢复 |
| F | F1 | 分栏行标识 = filtered 下标 `split=<n>`；恢复顺序 tab/q → 重建 filtered → 定位，越界忽略 |
| G | G1 | header 搜索框右侧 🔗 按钮，拷贝规范化 URL（剔除默认/空参数），navigator.clipboard + execCommand fallback，toast 提示 |
| H | H1 | 搜索词随 300ms debounce 一起 replaceState |
| I | I2 | 保留 positional yaml_path（nargs='?'，缺省 cache/data/_countries-data.videos.yaml），加 `--empty-video` flag（通用命名，不绑定 country） |
| J | J1 | empty-video 数据源读 yaml target.data 指向的 json；无 yaml 参数时用缺省路径 |
| K | K1 | empty-video 输出逐行「首字段 (次字段)」+ 底部计数（按 json 行内字段序） |
| L | L1 | yaml target 段扩展可选 rebuild: {github_url, home_url, favicon}，缺省用固定默认，显式传入并打印命令 |
| 1 | 1B | rebuild 缺省 home_url = https://html-gen.cli.jaden.tech/（站点根） |
| 2 | 2A | github_url 优先级：rebuild 配置 > extract_corner_url（旧 html 提取）> 固定默认 |
| 3 | 3A | --dry-run / --apply / --empty-video 三向互斥 |
| 4 | 4A | empty-video 行格式「首字段 (次字段)」原样打印，空字段显示 (空)，底部「共 N 条 videos 为空」 |
| 5 | 5A | 新 test_url_state.py + test_sync_videos 扩 3 例 + test_json_output favicon 断言 |

记观察（本次不做）：排序/页码/quickFilter 状态不入 URL；empty-video 暂不支持 --json。

## 三、需求 1 — favicon 默认注入 + syncer 重建显式传参并打印命令

### 3.1 html-gen.py 变更

- 新增常量 `DEFAULT_FAVICON = "https://www.jaden.tech/static/img/favicon.png"`（与现有 20+ 产物一致，C1）。
- 四渲染子命令（doc/slide/table/knowledge，argparse 区 L767-800 附近）新增 `--favicon <url>`：
  - 优先级：CLI `--favicon` > env `HTML_GEN_FAVICON` > `DEFAULT_FAVICON`。
  - 显式传空串 `--favicon ""` → 不注入（隐私态，与 github-url 默认空语义对齐）。
- 新增 `favicon_link_html(url)`：返回 `<link rel="icon" href="{url}" type="image/png">`（空 → 空串）。
- 模板 head 加 `<!--FAVICON-->` 占位，渲染管线（render_doc/slide/table/knowledge 四处 inject 调用）传入 favicon 注入串；对齐现有 `github_corner=` / `home_link=` 注入模式（corner_args L98-102）。

### 3.2 模板变更（四个 layout-*.html）

- `<head>` 内 `<title><!--TITLE--></title>` 之后加 `<!--FAVICON-->` 一行。

### 3.3 scripts/tool-table-videos-syncer.py 变更

- yaml `target` 段扩展可选 `rebuild:` 子键（不影响现有 target 列表/字典解析，parse_target 兼容）：
  ```yaml
  target:
  - data: data/_countries-data.json
  - html: demos/countries-table.html
  - rebuild:
      github_url: https://github.com/imjaden/html-gen.cli
      home_url: https://html-gen.cli.jaden.tech/
      favicon: https://www.jaden.tech/static/img/favicon.png
  ```
- 缺省默认（rebuild 节缺失的键）：github_url = https://github.com/imjaden/html-gen.cli、home_url = https://html-gen.cli.jaden.tech/（1B）、favicon = DEFAULT_FAVICON。
- github_url 最终值优先级（2A）：rebuild.github_url > extract_corner_url(旧 html) > 固定默认。
- run_apply() 重建（现 L209-214）改为：
  1. 构建 `cmd = [sys.executable, html_gen, 'table', '-d', json_path, '-o', html_path]`
  2. 追加 `--github-url`、`--home-url`、`--favicon` 三项显式参数（值按上述优先级）
  3. `print('[执行] ' + ' '.join(shlex.quote(str(a)) for a in cmd))`
  4. `subprocess.run(cmd, shell=False)`（保持 RIG-002：列表参数，禁 shell=True）
- 需要 `import shlex`（标准库）。

### 3.4 关联闭合

- FIND-002（CL002 审计）favicon 部分闭合：重建产物恢复 favicon link；github-corner 已由 extract_corner_url 闭合。
- FIND-001（CL002 审计，json columns initialHidden/splitFull 外部变更）在第八节修订日志登记。

## 四、需求 2 — layout-table URL 状态分享 + 拷贝按钮

### 4.1 URL 参数

```
?tab=<tabKey>&q=<searchKeyword>&split=<n>
```

- `tab`：TABS key；`q`：搜索关键字（encodeURIComponent 编码）；`split`：filtered 数组下标（0-based）。
- 默认值状态剔除参数（全部 tab / 空搜索 / 无分栏），URL 保持干净。

### 4.2 同步点（history.replaceState）

| 状态变化 | 位置（layout-table.html） | 动作 |
|:---|:---|:---|
| switchTab | L1295 附近 | replaceState + 现有 localStorage |
| 搜索输入 | L1287 input 事件（300ms debounce） | debounce 内 replaceState |
| 分栏打开 | activateSplit L1011 | replaceState |
| 分栏导航 | splitNav L1027 | replaceState |
| 分栏关闭 | closeSplit L1032 | replaceState（剔除 split 参数） |

- 统一封装 `syncUrlState()`：读当前 activeTab / searchInput.value / (splitActive ? splitIdx : null)，构造参数，`history.replaceState(null, '', url)`（url 无参数时用纯净 location.pathname）。

### 4.3 恢复流程（初始化）

1. 解析 `location.search`（URLSearchParams）。
2. `tab`：白名单校验 `TABS.find(t => t.key === tab)`（沿用 L399 模式），无效忽略。
3. `q`：decodeURIComponent 后仅 `searchInput.value = q`（不走 innerHTML），随后 applyFilters。
4. `split`：parseInt + 越界校验（`n >= 0 && n < filtered.length`，沿用 openSplitAt L1026 模式），有效则 `activateSplit(filtered[n], n)`。
5. 恢复顺序保证 filtered 先按 tab+q 重建，再定位 split（F1）。

### 4.4 拷贝按钮

- 位置：table-header 搜索框右侧（L269 searchInput 之后），`<button class="fs-btn" id="shareBtn" title="拷贝分享链接">🔗</button>`。
- 行为：`buildShareUrl()` = 当前 location.href（replaceState 已同步）或规范化构造；`navigator.clipboard.writeText(url)`，失败走 execCommand fallback（复用 copyAction 模式）；成功 toast「已复制链接」。
- buildShareUrl 规范化：剔除默认/空参数。

### 4.5 安全

- tab key 白名单校验；split parseInt 越界忽略；q 仅 input.value 赋值，无 innerHTML 注入面。
- URL 参数仅影响视图状态，不触发任何数据写入。

## 五、需求 3 — syncer 参数体系

### 5.1 CLI 形态（I2）

```
scripts/tool-table-videos-syncer.py <yaml-path> [--dry-run | --apply | --empty-video]
```

- `yaml_path`：nargs='?'，缺省 `cache/data/_countries-data.videos.yaml`（以项目根 PROJECT_ROOT 解析）。
- `--dry-run` / `--apply` / `--empty-video`：三向互斥（argparse mutually exclusive group，3A）；`--empty-video` 只读模式，与 apply 同用 → argparse exit 2。
- help：argparse -h 自动 + description 更新说明参数体系。

### 5.2 --empty-video 行为（J1 K1 4A）

1. 解析 yaml（缺省路径），读 `target.data` 指向的 json。
2. 遍历 data 行，收集 `videos` 缺失或为空数组的行。
3. 输出逐行「首字段 (次字段)」：取行内前两个非空字段（按 json 行内字段序），字段为空显示 `(空)`；底部「共 N 条 videos 为空」。
4. 零写盘，exit 0；无空行 → 输出「全部 N 条均有 videos」，exit 0。
5. 字段序 = json 数组首元素 keys 顺序（国家场景 = country_zh, country_en → 中国 (China)）。

### 5.3 向后兼容

- 现有调用 `python3 scripts/tool-table-videos-syncer.py cache/data/_countries-data.videos.yaml`（默认 dry-run）行为不变。

## 六、测试计划（5A）

1. 新建 `tests/test_url_state.py`：
   - URL 携带 ?tab&q&split 打开 → 页签激活、搜索已应用、分栏行高亮
   - 无效 tab / split 越界 → 忽略恢复，无 JS 错误
   - 状态变化（切 tab/搜索/开关分栏/导航）→ location.search 同步
   - 拷贝按钮 → execCommand fallback 路径（clipboard API 在 headless 权限受限，断言 fallback 分支）
2. `tests/test_sync_videos.py` 扩 3 例：
   - apply 重建命令含 `--github-url` `--home-url` `--favicon` 三参数（mock subprocess 或断言打印行）
   - `--empty-video` 输出与三向互斥（exit 2）
   - 缺省 yaml 路径（无参运行 → 缺省 cache 文件）
3. `tests/test_json_output.py`（或 test_templates）加 favicon 断言：
   - 默认注入 `<link rel="icon" href="https://www.jaden.tech/static/img/favicon.png">`
   - `--favicon <url>` 覆盖
   - `--favicon ""` 禁用（无 link）

## 七、文档同步

- AGENTS.md：CLI 子命令节加 `--favicon`；syncer 用法节更新（--empty-video / 缺省路径 / rebuild 配置）；测试计数 235 → 新值。
- README / README.zh.md：--favicon 参数说明。
- skills/html-gen/SKILL.md、skills/html-gen-table/SKILL.md：prompt 输出同步。
- 三 guide（usage/table/doc 等）如需重新生成：走 `html-gen doc/table` 重建（与 CL003 D5 同流程）。

## 八、修订日志

| 日期 | 编号 | 事项 |
|:---|:---|:---|
| 2026-08-29 | HTML-GEN-CL004 | 本设计定稿（决策 A1 B1 C1 D1 E1 F1 G1 H1 I2 J1 K1 L1 + 1B 2A 3A 4A 5A） |
| 2026-08-29 | FIND-001 登记 | CL002 审计发现 data/_countries-data.json columns 增 initialHidden/splitFull（外部会话编辑，共享文件污染）；本 CL 不触碰 columns，保持现状，推送前由归属 CL 登记 |
| 2026-08-29 | FIND-002 闭合 | CL002 审计 E 重建结构不一致：github-corner 已闭合；favicon link 由本 CL 3.3 闭合 |

## 九、验证命令（实施后复跑）

```bash
python3 -m pytest tests/ -q -n 4                    # 全量（235 → 新计数）
python3 scripts/tool-table-videos-syncer.py cache/data/_countries-data.videos.yaml --empty-video  # 空 videos 名单
python3 scripts/tool-table-videos-syncer.py cache/data/_countries-data.videos.yaml --apply        # 打印 [执行] 命令 + 重建
python3 html-gen.py table -d data/_countries-data.json -o /tmp/countries.html                      # favicon 默认注入检查
grep -c 'rel="icon"' /tmp/countries.html
```
