# table-videos-syncer 实现审计报告 v1.1

> 审计对象: HTML-GEN-CL002 实现（5 commits，未 push）
> 范围: `89495f8` docs@design HG-SEC-061 → `f275952` feat@script syncer v1.1 → `254ee1d` test@script 10 cases → `0deaf5c` data@table 缅甸1伊朗2 → `afb6742` docs@agents 224
> 设计: `documents/solutions/table-videos-syncer-design-v1.1-20260829.md`（431c1df + 89495f8）
> 设计评审: `documents/review/table-videos-syncer-design-rereview-v1.1-20260829.md`（PASS 95/A）
> 审计日期: 2026-08-29 ｜ 审计者: ops（impl audit）｜ 前置: HTML-GEN-CL001（videos 字段，已闭环）

---

## 一、结论

**✅ PASS 90/100（A）— 实现与设计 §4 规格逐项吻合，功能/安全/数据/测试全绿；附 2 项 🟡 需登记处理 + 3 项 🟢 观察**

| 维度 | 结果 |
|:---|:---:|
| 规格符合度（设计 §4 八步流程） | 🟢 全部吻合 |
| 安全 RIG-001/002/003 | 🟢 全部落实 |
| duration 容错 HG-SEC-061 | 🟢 阈值与语义正确 |
| 测试面（10 用例 + 224 全量） | 🟢 全绿（35.76s） |
| 数据正确性（json/yaml 镜像/产物） | 🟢 逐字段一致 |
| commit 治理（5 提交/无 drama/未 push） | 🟡 0deaf5c 混入列配置变更（FIND-001）+ E 重建产物结构声明不实（FIND-002） |

- 评分: 100 − 2×5（FIND-001 / FIND-002 🟡）= **90** → A → **PASS**
- 运行时实测（非源码推断）：F3 负路径 exit 1 零写盘、G 幂等中断 exit 0、dry-run 预览形态、互斥 exit 2、重建字节级可复现、SyncerDumper 按需引号回读无损、镜像 14==14 精确相等
- 两项 🟡 均有明确处置路径（登记/订正），不构成功能缺陷；建议推送前完成登记（见 §七）

---

## 二、设计 §4 规格逐项核验（审查要点 1）

| # | 设计要求（§4.2） | 实现落点 | 运行时核验 | 结果 |
|:--|:---|:---|:---|:---:|
| 1 | F3 校验先行：任一 country_zh 缺失 → 列清单 exit 1 零写盘 | `validate_countries()` L96-105 在 build_increments/写盘前执行；missing 非空即 return 1 | 实测 `亚特兰蒂斯`（真实 json 195 行中不存在）→ exit 1，输出缺失键，json/yaml/html 三文件零改动 | ✅ |
| 2 | url strip 去重；yaml 内部同 url 只取首条 | L111-137：`(entry.get('url') or '').strip()`；`seen` 集合键 (cz, url) 首条胜出 | test_05/06 覆盖；真实数据缅甸/伊朗 url 均无重复 | ✅ |
| 3 | G 判定：新增 0 → 提示 exit 0 不写盘（幂等） | L267-270：`if not new_items: print 提示; return 0` | 实测对真实 cache yaml 干跑 → `[提示] 所有 videos 均已包含，无需同步` exit 0，三文件零改动 | ✅ |
| 4 | 按 country_zh 分组 append；videos 缺失先初始化 [] | L166-176：`videos is None → videos=[]; row['videos']=videos` 再 append | test_05 缅甸 0→1 通过 | ✅ |
| 5 | platform C1 兜底：URL host 自动识别 | `detect_platform()` L70-80（douyin/bilibili/youtube/youtu.be→识别，其他→None 省略）；run_apply L172 `it['platform'] or detect_platform(url)` | test_08 douyin+bilibili 通过；youtube/未知分支见 OBS-003 | ✅ |
| 6 | W 镜像回写：target 段保留、无 videos 行不产生条目、platform 写 json 现值、url strip | L140-159 `build_mirror_countries`：`if not videos: continue`；L187 `{'target': doc.get('target'), 'countries': ...}` | 真实 yaml 14 条 == json 14 条**精确相等**（脚本逐字段比对 True）；target 段保留；test_07 断言通过 | ✅ |
| 7 | E 重建：列表参数、无 shell；路径以项目根为基准 | L194-205 `subprocess.run([sys.executable, str(html_gen), 'table', '-d', json_path, '-o', html_path], shell=False)`；PROJECT_ROOT=脚本位置 parents[1]（RIG-003） | 重建输出与提交产物**字节级一致**（`diff -q` 无差异）→ 已提交 html 确由该命令生成 | ✅ |
| 8 | duration 回写恒可安全回读（引号策略） | SyncerDumper 仅对会被误解析的标量加引号（见 §四） | 回读无损，见 §四 实测表 | ✅ |

## 三、安全（RIG-001/002/003，审查要点 2）

| RIG | 要求 | 核验 | 结果 |
|:---|:---|:---|:---:|
| RIG-001 | yaml.safe_load，禁 yaml.load/FullLoader | L224 `yaml.safe_load`；grep 全文无 `yaml.load(`/`FullLoader` | ✅ |
| RIG-002 | subprocess 列表参数 + shell=False，禁 shell=True/字符串拼接 | L198-201 列表形式 + `shell=False`；grep 无 `shell=True`/`os.system` | ✅ |
| RIG-003 | 相对路径以项目根为基准（勿相对 yaml 所在 cache/） | L30 `PROJECT_ROOT = Path(__file__).resolve().parents[1]`；json/html/html-gen 均基于 PROJECT_ROOT | ✅ |

## 四、duration 容错与引号策略（审查要点 3，HG-SEC-061）

**阈值**：`DURATION_INT_THRESHOLD = 3600`（L33），与 HG-SEC-061 订正一致（89495f8 同步文档 6000→3600）。

**归一化语义**（`normalize_duration` 实测）：

| 输入 | 输出 | 说明 |
|:---|:---|:---|
| int 0 / 59 / 3599 | '0:00' / '0:59' / '59:59' | < 3600 → M:SS 归一化（M:SS 上界 3599 ✓） |
| int 3600 / 3723 | '3600' / '3723' | ≥ 3600 保留原值字符串，不归一化为 H:MM:SS ✓ |
| str '6:55' | '6:55' | 原样 strip ✓ |

**SyncerDumper 按需引号实测**（与设计「统一带引号」措辞的等价性确认）：

| 输入 str | dump 输出 | safe_load 回读 | 结论 |
|:---|:---|:---|:---|
| '0:22' | `0:22`（裸） | '0:22' (str) | 裸写安全（sexagesimal 正则首段需 [1-9]，0:xx 不触发） |
| '4:41' | `"4:41"` | '4:41' (str) | 裸写会被解析为 int 281 → 引号 ✓ |
| '11:38' | `"11:38"` | '11:38' (str) | 同上 ✓ |
| '3723' | `"3723"` | '3723' (str) | 裸写会被解析为 int → 引号 ✓ |
| '123' / 'true' / '' | 均带引号 | 回读 str | 数字/bool/空串防误解析 ✓ |

**结论：实现与设计语义等价。** 设计措辞「回写时 duration 统一带引号」是充分条件；实现采取**最小引号**（仅当裸写会被 safe_load 解析为非 str 时加引号），可观察不变式完全一致——任意 duration 回读均为同值 str，60 进制坑不存在。真实 cache yaml 中 `0:22`/`0:58`/`0:42` 裸写可安全回读（镜像 14==14 精确相等已证）。建议（🟢 OBS-001）设计文档措辞从「统一带引号」改为「按需引号：仅当裸写会被 YAML 解析为非字符串时加引号」，避免读者误读。

## 五、测试面（审查要点 4）

**10 用例与设计 §5 测试计划 1:1 映射**：test_01 解析 / test_02 duration 容错 / test_03 F3 / test_04 全存在 / test_05 补充+url strip / test_06 yaml 内部去重 / test_07 W 镜像 / test_08 platform 兜底 / test_09 dry-run / test_10 重建。非 Selenium 架构（unittest + subprocess + tempdir 隔离）符合设计。

**回归**：`tests/test_countries_table.py` 13 + `tests/test_videos.py` 8 + 全量 **224 passed**（35.76s，-n 4）——与 afb6742 声称 224 一致（grep `def test_` 求和亦为 224）。

**断言盲区（🟢 OBS-003，均不阻断）**：
1. `build_mirror_countries` 的「无 videos 行不产生条目」分支未被覆盖（fixture 行 apply 后均有 videos）
2. `detect_platform` youtube 分支 + 未知 host → 省略分支未覆盖
3. F3 缺 country_zh 条目分支（「第 N 条（缺 country_zh）」）未覆盖
4. 畸形条目（缺 url）警告分支未覆盖
5. duration 边界值 3600 未测（3599 归一化 / 3600 保留均已实测但未入用例）
6. E 重建失败路径（html-gen.py 缺失 / 非零退出）未覆盖
7. `normalize_duration(None)` → 字面 'None' 字符串写入 json（yaml 缺 duration 字段时数据污染；建议缺省省略字段或默认 '0:00'）

## 六、数据正确性（审查要点 5）

| 检查项 | 实测结果 |
|:---|:---|
| 缅甸 videos | 1 条：缅甸-散装缅甸 / https://v.douyin.com/-IIdHuXNL0o/ / 6:55 / douyin —— 与设计 §3 样例逐字段一致 ✓ |
| 伊朗 videos | 2 条：中东为何永不团结（原 1 条保留）+ 伊朗-美国为什么征服不了伊朗 / https://v.douyin.com/1IxN2ag0e8U/ / 11:38 / douyin —— url 去重（2 条 url 互异）、顺序为先旧后新 ✓ |
| 全局镜像 | cache/data/_countries-data.videos.yaml countries 14 条 == json 全部 14 条 videos（195 行中 11 行有 videos），**脚本逐字段比对相等**；target 段保留 ✓ |
| cache yaml 归属 | cache/ 在 .gitignore（L27），yaml 纯本地草稿不入库（B1）✓ |
| 产物 html | 含全部新标题文本；`<title>全球国家速查表（195 国）</title>` 与旧产物一致；字节级复现（重建 == 提交产物）✓ |

## 七、发现项汇总

| 编号 | 严重度 | 描述 | 处置建议 |
|:---|:---:|:---|:---|
| **FIND-001** | 🟡 | **0deaf5c 混入列配置变更（超出 CL002 范围）**：json columns 增 6 处 `initialHidden`（ethnic_groups/religions/area_province/pop_province/**videos**/note）+ 4 处 `splitFull` + note `preview: true→false`。254ee1d 时该文件无任何 initialHidden/splitFull；同步器代码路径不触碰 columns（load→append→dump 原样保留），故变更来自外部——与当前工作树未提交的 drama 列配置（`_drama-table-history-strategy.json` 同型 initialHidden/splitFull）同源，属**共享文件污染**（与 CL017 审计同型：`git add data/_countries-data.json` 整文件纳入并行会话编辑）。commit message 仅称「countries videos synced」，未登记。影响：countries-table 演示页默认隐藏 6 列（含 CL001/CL002 主打 videos 列，⚙️ 可开启/分栏全列渲染不受影响）；现有 224 测试无断言冲突。 | 推送前登记至设计修订日志（注明来源与影响）；如非 CL002 意图，拆分为独立提交归入所属 CL；如有意保留，补 commit message 说明 |
| **FIND-002** | 🟡 | **E 重建产物与既有页面结构不一致，设计 §4.2 step8「已实测与现产物一致」声明仅 <title> 成立**：重建后 `github-corner` 标记消失（旧页含 --github-url corner，新页仅剩 CSS 选择器 3 处）、favicon link 移除、`.home-link` CSS 出现（无 anchor）。根因：重建命令未传 `--github-url`（默认隐私态）。AGENTS.md HG-SEC-014 文档化 demo 页应带 corner。 | 若需保留 corner：E 命令补 `--github-url https://github.com/imjaden/html-gen.cli`（并加 test_10 断言）；若接受隐私默认态：订正设计 §4.2 措辞「仅 <title> 与数据一致，页面结构按当前模板默认」 |
| OBS-001 | 🟢 | 设计措辞「统一带引号」→「按需引号」更准确（§四，语义已等价） | 文档措辞优化 |
| OBS-002 | 🟢 | duration 缺失 → 字面 'None' 字符串写入 json | 缺省省略字段或默认 '0:00' |
| OBS-003 | 🟢 | 测试盲区 7 项（§五），均为防御性小分支 | 视需要补充 |

## 八、commit 治理（审查要点 6）

| 检查项 | 实测结果 |
|:---|:---|
| 5 commits type@scope | docs@design / feat@script / test@script / data@table / docs@agents —— 全部小写 type@scope + (HTML-GEN-CL002) ✓ |
| 提交内容纯净 | 5 commits 文件清单无任何 drama 文件（grep 计数 0）；drama WIP（`_drama-table-history-strategy.json` + `demos/drama/history-strategy-table.html`）仍为未提交状态，未混入 ✓（flag-don't-fix，本次不动） |
| 未 push | `git rev-list @{u}..HEAD --count` = 5（ahead 5）✓ |
| AGENTS.md 计数 | 224 tests 与实际一致（grep 求和 224 + 实测 224 passed）✓；scripts 目录注释更新 ✓ |
| requirements-dev.txt | `PyYAML>=6.0` 已加入（D 决策）✓ |

## 九、验证线索（本次审计实测命令）

| 验证项 | 命令/证据 | 结果 |
|:---|:---|:---:|
| 全量测试 | `python3 -m pytest tests/ -q -n 4` → `224 passed in 35.76s` | ✅ |
| 镜像相等 | python 脚本比对 cache yaml 14 条 vs json 14 条 → `镜像完全相等: True` | ✅ |
| 缅甸/伊朗 | json 读取：缅甸 1 条 / 伊朗 2 条（url 去重） | ✅ |
| G 幂等 | 真实 cache yaml 干跑 → 提示 exit 0 | ✅ |
| F3 负路径 | 未知键 `亚特兰蒂斯` → exit 1 + 缺失清单，三文件零改动（hash 前后一致） | ✅ |
| 互斥 | `--dry-run --apply` 同传 → argparse exit 2 | ✅ |
| 重建复现 | `html-gen.py table -d ... -o /tmp/...` → `diff -q` 与提交产物字节一致 | ✅ |
| SyncerDumper | importlib 直接调用 → 按需引号表（§四） | ✅ |
| normalize_duration | 边界 3599/3600/3723 实测（§四） | ✅ |
| RIG grep | 无 `yaml.load(`/`FullLoader`/`shell=True`/`os.system` | ✅ |

> 注：审计过程中曾误用合法国家键「越南」做 F3 探测导致真实数据被写入，已立即 `git checkout -- data/_countries-data.json demos/countries-table.html` 精确还原，工作树恢复至仅剩 2 个 drama WIP 文件（基线不变）。

## 十、评分明细

```
基准分: 100
  FIND-001  🟡 -5  0deaf5c 混入列配置变更（范围外变更未登记，共享文件污染）
  FIND-002  🟡 -5  E 重建产物结构不一致 + 设计「已实测与现产物一致」声明不实
  (OBS-001/002/003 🟢 不计分)
────────────────────────
得分: 90 → A → PASS
```

## 十一、结论与后续

**PASS 90/100（A）。** 功能实现、安全、数据、测试、commit 治理核心全部达标；设计 §4 八步流程与 HG-SEC-061 语义逐项吻合且经运行时实测。两项 🟡 需在推送前处置（推荐）：FIND-001 在设计修订日志登记列配置变更来源/影响（或拆分提交）；FIND-002 由 ops 决定 E 命令是否补 `--github-url`（保留 corner）或订正设计文档措辞。审计产物待 ops 提交；5 commits 保持未 push，留待 review profile 审计后推送。
