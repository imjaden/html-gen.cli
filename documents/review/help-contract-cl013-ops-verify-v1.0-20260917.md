# help 契约四模板补齐 — ops 独立核查报告 v1.0

> 日期: 2026-09-17 · 闭环: **HTML-GEN-CL013 [4/6] ops 核查** · 角色: ops（交互式驱动会话）
> 被审对象: `7b99701`（`docs@help:` dev 会话产出, 12 文件）+ `3044139`（`docs@sync:` ops 交互会话落地 AGENTS.md, 1 文件）
> 基线: `90e6bef`（github/main 起点, 归档快照 `/tmp/cl013-base`）
> 需求源: `documents/solutions/html-gen-help-contract-design-v1.3-20260917.md`（§C / §D CL013 行 / §F / §G）
> 核查方式: **自建 harness 独立复跑**（不复用 dev 的 verify 脚本, 不采信其自报）
> **结论: PASS —— 56 项二值判据 全绿（FAIL 0 / N-A 1 人工过目项）**

## 1. 结论要点

| 面 | 结果 | 关键实测 |
|:--|:--|:--|
| 足迹与范围 | ✅ | HEAD 改动集 ⊆ 授权白名单；`git status --short` 空；无未跟踪新增；gitee(origin) 未推进（`7821427`） |
| 契约面（§A/§C/§3） | ✅ | 三模板均无 `legacy`；CLI 实测 **9/9/8/10**；doc `url_state` 3；slide `behaviors` 8；knowledge item 7 / groups 3；table 22/13/6/6/5/7/5 未削弱 |
| help 渲染面 | ✅ | 契约键 + CLI flag **全域覆盖**（T25 无缺口）；`key:` 词元 ⊆ 契约（T26 无泄漏）；无重复渲染（T28）；slide 如实写明无 URL 状态（T27） |
| 守卫测试 + 回归 | ✅ | `tests/test_help_contract.py` 22 passed + 80 subtests；全量 **334 passed / 0 failed**（基线 326, Δ+8, 只增不减）；pytest 未写脏工作树 |
| 独立提取（template→contract） | ✅ | 四模板 CLI ⊆ 契约；doc URL `params.get` 3 项 == 契约；knowledge item 双源 ∪ 白名单 == 契约 7；groups 3；slide 特征串 `.slide-toc-search` 存在 |
| 文档面（§F） | ✅ | `initialHidden` 裸行 0；AGENTS.md **键定义行 0**（修前 26）；L299 总数 334 == 实测 == 逐文件列和；L326 = 334；文件数 31 |
| 产物零回归（A7） | ✅ | 重建 countries 与入库产物 **sha256 相同**（`556d58839fe0c000…`）；基线可比性已实测（90e6bef 同命令亦字节一致） |
| 守卫有效性（变异） | ✅ | `/tmp` 副本内删契约键 → 断言转红并**指名键 + 来源文件 + 修复动作**；还原后全绿（live 树零污染） |

**判据非恒真反证**: 同一 harness 在 `7b99701` 之前（`90e6bef` 工作树）跑 = **29 FAIL**；落地 AGENTS.md 前跑 = **53 PASS / 3 FAIL**（全为计数未同步）；落地后 = 56 PASS / 0 FAIL。

## 2. 可复跑验证清单（命令 + 预期 + 断言）

```bash
cd /Users/jadenli/CodeSpace/html-gen.cli
PYTEST=/opt/homebrew/Caskroom/miniconda/base/envs/py3.12/bin/pytest

# 1) 全量核查（56 项; 含契约/渲染/提取/回归/产物/变异/夹带）  预期 RESULT: PASS, FAIL=0
python3 cache/closed-loop/HTML-GEN-CL013-verify.py
grep -E "PASS=|RESULT" cache/closed-loop/cl013-harness-run-ops-final.log

# 2) 判据非恒真（修前反证）                                   预期大量 FAIL
#    （harness 的 REPO 常量指向 /tmp/cl013-base 后跑）

# 3) 修前基线可复现                                           预期 326 passed, 7 subtests
cd /tmp/cl013-base && $PYTEST tests/ -q -n 0 | tail -2

# 4) 全量回归（live）                                         预期 334 passed, 0 failed
$PYTEST tests/ -q -n 0 | tail -2

# 5) 产物零回归（A7）                                         预期 sha 一致
python3 html-gen.py table -d data/_countries-data.json -o /tmp/rb.html \
  --github-url https://github.com/imjaden/html-gen.cli --home-url https://html-gen.cli.jaden.tech/ \
  --favicon https://www.jaden.tech/static/img/favicon.png --feedback-repo imjaden/html-gen.cli
cmp /tmp/rb.html demos/countries-table.html && echo BYTE-IDENTICAL

# 6) demo 产物重生成保真（D7 三问）                            预期 Q1/Q2/Q3 全 True
python3 cache/closed-loop/cl013-d7-fidelity.py

# 7) 键定义行判据双态自检                                      预期 修前 26 / 修后 0
python3 cache/closed-loop/cl013-t51-precheck.py
```

## 3. dev 申报偏差逐条判定（7 条，**全部成立**）

| # | 内容 | 判定 | 依据（实测） |
|:--|:--|:--|:--|
| D1 | doc/slide `url_state` 双落点（`data` + 节点顶层, 同一 list 别名） | **成立** | 设计 §A 未 pin 落点；渲染只走一次（T28 无重复）；两落点内容一致（T12/T41 双通过） |
| D2 | 设计 §D item 双源正则 `item\.get\('([a-z]+)'\)` **恒为空集** ⇒ 收窄为容忍默认值形态 | **成立（设计 errata）** | 独立复算: 生成器两处调用 `item.get('group','其他')` / `item.get('icon','')` 均带第二实参; 字面正则提取 = 空 ⇒ 双源退化恒真单向 ⊆ |
| D3 | 任务书 R2 称 knowledge 亦消费 `HTML_GEN_FEEDBACK_REPO`；实测仅 `cmd_table` 消费 ⇒ 只在 table 段写 | **成立（任务书字面有误）** | `feedback_repo_args` 调用点仅 `html-gen.py:574`（`cmd_table` 内）; `--feedback-repo` 只在 table 子解析器注册 |
| D4 | knowledge ② 示例段补段首注记行, 三块示例逐字保留 | **成立** | §B.3 ② 段要求；示例块 diff 逐字未变 |
| D5 | AGENTS.md 未由 dev 写（受保护门禁）, 改产补丁 | **成立** | 首轮 ops 直写曾 **BLOCKED fail-closed**（审批超时, 未重试未绕道）; 最终由交互式 ops 会话落地, sha256 与补丁产物逐字节相同 |
| D6 | 顺手订正 README/README.zh「246 用例」→334、features.md「312」→指向 AGENTS.md、cli-spec 删陈旧「`--version` 未实现」 | **成立** | `html-gen version` → `html-gen v3.3 (2026-08-28)`（`--version` 已实现, CL016）; 三处计数均属本批「消除文档漂移」同族 |
| D7 | `demos/table-guide.html` 重生成带入 2 处无关漂移（head 顺序 + meta 时间戳） | **成立** | 保真三问全 True: Q1 本批 md 重建 == 入库新产物（忽略 meta 行）; Q2 **旧 md + 当前生成器**的 head 段 == 入库新产物 ⇒ 顺序变化归因模板演进; Q3 diff 分类 = meta 2 + head 2 + 键名移除 106 |

## 4. 观察项（本批范围外; 已登记待处置）

| # | 事项 | 事实 | 建议 |
|:--|:--|:--|:--|
| O1 | `?show-md` 守卫盲区 | `layout-doc.html:273` 真实 URL 键; 设计 §D 正则 `params\.get\('([a-z]+)'\)` 不匹配连字符参数 ⇒ 无守卫 | 补它 = doc 契约 3→4 项（**口径扩容**）⇒ 另批 + 评审 |
| O2 | repo `skills/` 是镜像, 真源在 `~/.hermes/profiles/dev/skills/software-development/html-gen*`（`cli-spec §5`） | 本批只改镜像; 正向同步会覆盖回来 | 跨 profile 写需用户授权; 建议镜像/真源口径单独治理 |
| O3 | `prompts/` 生成物未重建 | `grep` 实测 prompts 内 17 处键名 vs repo skills 2 处（残留 1 处为版本历史行） | 与 O4 同类（生成物刷新）, 可合并一小批 |
| O4 | `src/html_gen/` 未重建 | 设计 §OUT 明确不做（构建产物随 `build-package.py` 传播） | 分发前重建 |
| O5 | `skills/html-gen-table/references/table-demo-prompt.md` 仍枚举列键骨架（L10/L13/L23） | 无 help 指针; 非设计 §F 逐一点名的文件 | 待 [5/6] 审计裁定「真缺口 vs 可接受作者脚手架」 |
| O6 | AGENTS.md knowledge 节「Bare 模式：默认隐藏侧边栏/工具栏（URL 参数显式展示）」 | 实测 `layout-knowledge.html` **无** sidebar/toolbar URL 参数读写（L396 仅给 iframe 内详情页追加 `sidebar=0&toolbar=0`）⇒ 疑历史漂移 | 本批按「只去键名、不动极性」最小改动; 语义订正另批 |

## 5. 核查过程披露（须纳入 [5/6] 审计判断）

- **X1 ops 自身动作**: (a) AGENTS.md 落地（10 次 `patch` 工具写入; 首轮 BLOCKED; 最终 sha256 `42d1273e…` 与补丁产物逐字节一致）;
  (b) ops **改动自己的判据** 2 处（T52b 正则漏含数字文件名; T51 由 grep 单键改为「键定义行」形态 —— 原判据会被弱代理假通过）。
- **X2 dev 会话读过 ops harness**（同仓 `cache/closed-loop/`）并按其形状适配（即 D1 别名）。ops 结论所依赖的
  T40–T44 为**独立重提取**（自己的正则扫 `layout-*.html` / `html-gen.py`），不以 dev 测试为输入。
- **X3 复核中发现的 ops 自身笔误**: 第 7 步落地时一度把 knowledge 的 Bare 极性写反（`默认展示…显式隐藏`）,
  经 `shasum`/`diff` 逐字节复核发现并**按补丁原文复正**（`默认隐藏…显式展示`）。过程留痕: 中间态未提交、未影响最终产物。

## 6. 证据索引

| 类型 | 路径 |
|:--|:--|
| harness（56 项） | `cache/closed-loop/HTML-GEN-CL013-verify.py` |
| 全量日志（含判据双态） | `cache/closed-loop/cl013-harness-run-ops-final.log`（本轮）/ `…-run-ops.log`（AGENTS.md 前）/ dev 预跑 `cache/handoff/cl013-harness-run.log` |
| 修前基线归档 | `/tmp/cl013-base`（`git archive 90e6bef`）+ 基线 help 文本 `cache/closed-loop/cl013-baseline-help.txt` |
| 专项脚本 | `cache/closed-loop/cl013-d7-fidelity.py`（D7 三问）· `cl013-t51-precheck.py`（键定义行双态）· `cl013-step-accounting.py`（步骤账/草案绑定） |
| dev 交付 | `7b99701`（12 文件）+ `cache/handoff/cl013-agents-md.patch` / `.new.md` |
| 步骤账 | `cache/closed-loop/20260917-html-gen-ops-HTML-GEN-CL013-{design,design-review,dev-impl,ops-check}.json` |
