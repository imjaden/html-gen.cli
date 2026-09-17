# help 契约 `?show-md` 纳入 doc URL 守卫 — ops 独立核查报告 v1.0

> 日期: 2026-09-17 · 闭环: **HTML-GEN-CL014 [4/6] ops 核查** · 角色: ops（harness 独立判据，不采信 dev 自报）
> 被核对象: `0b387ca`（`feat@cli:` [3/6] dev 实施）+ 设计链 `e6933aa` / `1e473c2` / `5b95469` + 评审 `d9a0e29`
> 起点基线: `4e58407`（= `github/main` 起点）· 核查时 HEAD = `0b387ca` · 工作树干净
> harness: `cache/closed-loop/HTML-GEN-CL014-verify.py`（44 项 + 5 条自带 fixture；A4 门禁）
> 留档: 修前 `cache/closed-loop/cl014-harness-run-pre-impl-r2.log`（30 PASS / **9 FAIL** / 3 N-A）
> · 修后 `cache/closed-loop/cl014-harness-run-ops-final.log`（**44 PASS / 0 FAIL / 0 N-A**）

## 1. 结论要点

| 面 | 结果 | 关键实测 |
|:--|:--|:--|
| 足迹与范围 | ✅ | 累积改动 8 文件 ⊆ 授权白名单；`git status --short` 空；无未跟踪新增；gitee(origin/main) 未推进（`7821427`） |
| 契约面（真源） | ✅ | doc `url_state` = **4 项**（`?sidebar/?toolbar/?width/?show-md`，全带 `?` 前缀，与节点顶层**同一 list 对象**）；说明文本含「默认隐藏」+「basename」且**无 ASCII 词元冒号**（T13/T14）；其他三维度未削弱（table 22/13/6/6/5/7/5 · slide url_state 0 · knowledge 7/3/3）；doc CLI 9 项未变 |
| 模板消费面（**独立提取**） | ✅ | `params\.get\('([a-z][a-z0-9-]*)'\)` 提取 **4 项 == 契约 4 项**（等式成立）；历史口径留档: 老 `[a-z]+` = 3 项（**HG-SEC-180 根因**）；维度隔离: 仅 `layout-doc.html` 用裸 `params.get`（table 用 `_params`、knowledge 用 `urlParams`）⇒ 正则放宽无误伤面 |
| help 渲染面（能力可达性） | ✅ | `html-gen help doc` URL 状态段 **4 行**；该行文本与契约说明**逐字一致**（T42）；①段词元 ⊆ 契约键（无泄漏）；其他三模板 label/分隔线零回归；table 关键语义文本仍在（未被扰动） |
| 文档面 | ✅ | `demos/doc-guide.md` 表命中 1 行且语义含「默认隐藏」+「basename」（T50/T52）；生成物**内容单元格** `<code>show-md</code>` = 1（模板 JS 内联的 7 处不计入 —— 弱代理已排除，T51）；重生成 == 库内产物（去时间戳 **BYTE-IDENTICAL**，T53）；主题手册（存量文档面）已载该键 ⇒ 本批文档面**无漏改**（T54） |
| 守卫测试 + 回归 | ✅ | `tests/test_help_contract.py` **22 passed**；全量 **334 passed / 0 failed**（基线 334，只增不减）；**未新增/删除用例** ⇒ 无需改 `AGENTS.md`（该文件零改动）；pytest **未写脏**工作树 |
| 守卫有效性（变异 + fixture） | ✅ | harness 先跑 **5 条自带 fixture**（FX-1 阳性 / FX-2 阴性+指名 / FX-3 老正则对照 / FX-4 中间态数字键漏捕 / FX-5 钉定正则覆盖）再判实现；`/tmp` 副本变异 ⇒ **转红并指名 `show-md`**；live 工作树**零污染** |
| 判据非恒真（双态自检） | ✅ | 修前 **9 FAIL**（契约/help/文档面三面）→ 修后 **0 FAIL**；同一 harness 同一口径 |
| 出口判据（A3） | ✅ | 上游 `O1`/`HG-SEC-180` **就地闭合**（契约声明 + 守卫等式 + 变异转红 + help 可见 四项齐）；`HG-SEC-182` 已在设计侧订正（`5b95469`）；升级项 `O-CL014-1` / `HG-SEC-183` / `HG-SEC-185` 均带「编号 · 归属批 · 理由」 |

## 2. 可复跑验证清单（命令 + 预期 + 断言）

```bash
cd /Users/jadenli/CodeSpace/html-gen.cli
PY=/usr/bin/python3

# 1) harness 全量（44 项 + 5 fixture）            预期 RESULT: PASS, FAIL=0
$PY cache/closed-loop/HTML-GEN-CL014-verify.py

# 2) 判据非恒真反证（修前双态）                  预期 9 FAIL（含 T10/T30/T40/T41/T50/T51/T52）
grep -E 'PASS=|RESULT' cache/closed-loop/cl014-harness-run-pre-impl-r2.log

# 3) 端到端真实使用路径（A2）                    预期 命中 ?show-md 行 且 守卫文件全绿
html-gen help doc | sed -n '/URL 状态:/,/^$/p' | grep -n 'show-md' \
  && $PY -m pytest tests/test_help_contract.py -q -n0

# 4) 全量回归                                    预期 334 passed / 0 failed
$PY -m pytest tests/ -q -n0

# 5) 独立变异（/tmp 副本；live 树零污染）        预期 转红并指名 show-md
cp -a . /tmp/cl014-mut && cd /tmp/cl014-mut && sed -i '' "/'?show-md'/d" html-gen.py \
  && $PY -m pytest tests/test_help_contract.py -q -n0 ; cd - ; rm -rf /tmp/cl014-mut

# 6) 生成物保真                                  预期 去时间戳后逐字节一致
$PY html-gen.py doc -i demos/doc-guide.md -o /tmp/cl014-regen2.html \
  && diff <(sed 's/[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\} [0-9:]*/TS/g' demos/doc-guide.html) \
           <(sed 's/[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\} [0-9:]*/TS/g' /tmp/cl014-regen2.html)

# 7) 白名单/夹带面                                预期 白名单外 0 文件
git diff --name-only 4e58407..HEAD
git status --porcelain
```

## 3. dev 申报偏差逐条判定（D1–D5）

| # | 内容 | 判定 | 依据（实测） |
|:--|:--|:--|:--|
| D1 | 契约条目上方加两行 Python 注释（`?` 前缀 / 禁「词元:」/ 语义溯源行）留痕 | **成立（接受，保留）** | 注释在源码层、不入契约数据：T13/T14 实测说明文本仍无 ASCII 词元冒号，T42 help 行文本**逐字**未变，44 项判据无差异 ⇒ 属纪律留痕（防后人回改成 `[a-z]+`），零行为影响 |
| D2 | A5 用 `cp -a <绝对路径>` 替代仓内 `cp -R .` | **成立** | 语义等价；我的 harness T70–T72 独立复跑同结论（转红 + 指名 + live 零污染） |
| D3 | A5 跑毕 `rm -rf /tmp/cl014-mut` | **成立** | 不影响可复跑性（harness 自建副本）；证据已回执留档 |
| D4 | §10 V5 行数口径 = **单侧计数**（CSS 取增量侧 / corner 取删除侧 / title 取合计） | **成立（建议复盘把口径写明）** | 我独立双向归类: CSS +5/-2、corner +2/-8、title +1/-1 ⇒ 与设计所列 5/8/2 **总和对齐**，无冲突；属**表述口径**问题，非数值错误 |
| D5 | 「无按实测收窄项」 | **成立** | R1 语义三点（默认隐藏 / `show-md=1` 才显示 / 仅 basename）均由 T15 四项判据支撑 |

## 4. 观察项与佐证（本批范围外；均已带归宿）

| # | 事项 | 事实（实测） | 处置 / 归宿 |
|:--|:--|:--|:--|
| O-CL014-1（**范围更新**） | 生成物落后于当前模板 | 本批只刷新 `doc-guide.html`；**其余 4 份 guide + 全量 demos** 实测: `github.com/imjaden/html-gen.cli` 从 **16/18 → 15/18**（本批修正 1 份） | 显式升级 →「生成物刷新批」（与 CL013 O3/O4 合并）；本报告据实更新计数，设计 §11 的 `16/18` 为其锚点（`4e58407`）实测值，二者不矛盾 |
| OB2（dev 申报，ops 同判） | `demos/doc-guide.md` L210-218「迭代记录」表未登记本轮 URL 入参新增 | 末行为 `v2.2 2026-08-19 URL 入参控制展示设置…` | 归属「生成物刷新批 / 文档面补记批」——R3 授权面仅「表补 1 行 + 说明最小确认」，迭代记录不在授权面（成立） |
| OB3 | `HG-SEC-183`（table `?tab/?q/?split` 无提取守卫）/ `HG-SEC-185`（doc 无 `behaviors` 段，标题点击复制为第三行为面） | 本批复测确认两者仍开放 | 归属批已在设计 §11 登记（守卫面补全批 / doc behaviors 段补齐）；本批无新证据推翻定性 |
| OB4（佐证，无需归属） | 产物侧 basename 实测 | 重生成后 `.meta-path` 内容 = `· 路径: <code>doc-guide.md</code>`（仅 basename，无完整路径） | 契约语义「仅 basename 脱敏」在**产物侧**亦成立（F8 追加佐证） |
| OB5（佐证，无需归属） | `home-link` 漂移性质 | 未传 `--home-url` 时页面**无** `class="home-link"` 元素（内联 4 条 CSS 规则） | 新增漂移为纯样式面，不引入新可见元素、不构成隐私面回退 |

## 5. 结论

**PASS（0 阻断 / 0 FAIL）** —— 契约声明 + 模板消费 + help 渲染 + 文档面 + 回归 + 变异六面全绿，
`HG-SEC-180`/`O1` 四项判据齐备（就地闭合），无需回修。**同意进 [5/6] 实现审计**；本报告不代行推送
（推送仍走 review 通道）。

**遗留率 = 升级项 3 / 本批步数 6 = 0.50**（`O-CL014-1` / `HG-SEC-183` / `HG-SEC-185`；均已带归属批与理由）。
