# table/knowledge JSON 顶层 output 字段设计 — review报告 v1.1（复审）

- **日期**: 2026-08-29
- **审查人**: Security Reviewer（review role）
- **级别**: L2（design-document-review）
- **对象**: `documents/solutions/table-knowledge-json-output-design-v1.1-20260829.md`（HEAD `2454e37`，HTML-GEN-CL003）
- **结论**: 🟡 **CONDITIONAL PASS 85/100（B）** — 上轮 1 🔴 + 2 🟡 + 2 🟢 全数闭合，但复审新发现 3 处 🟡 影响面遗漏（features.md / html-gen-cli-spec / build-package src 同步）

---

## 一、上轮意见修正核验（逐条实测）

| 意见 | 严重度 | v1.1 声明 | 实测核验 | 结果 |
|:--|:--:|:--|:--|:--:|
| HG-SEC-062 / RIG-1 | 🔴 | §3.4/D1/D2 增 argparse default 删除点（768/779） | html-gen.py:768 `t.add_argument('-o','--output', default='index.html')` / :779 `k.add_argument('-o','--output', default='kb.html')` 逐字一致；§4 更正为「两处 cmd + 两处 argparse default + 两处 JSON 分支」= 6 处 | ✅ 闭合 |
| HG-SEC-063 / RIG-2 | 🟡 | §4 D5 增 usage-guide.md；§3.5 补 _demos-data.json 提示 | usage-guide.md:126「默认 `index.html`」/:186「输出 HTML 路径」/:60「默认同目录同名.html」逐字一致；_demos-data.json 实测 dict 无 `output` 键 | ✅ 闭合 |
| HG-SEC-064 / RIG-3 | 🟡 | §3.4/D2 增 L475 raw 最终化后提取 | html-gen.py:473-475 `raw=json.load` + `items = raw if isinstance(raw,list) else (raw.get('items') or raw.get('data') or raw)` 逐字一致；`json_output = raw.get('output') if isinstance(raw,dict) else None` 提取位置无歧义（L474 `raw` 恒为 data 文件最终解析，有/无 `-g` 均成立） | ✅ 闭合 |
| HG-SEC-065 / OBS-1 | 🟢 | §3.2 矩阵行 1 改「CLI `-o` 非空」+ 空串注 | 矩阵「CLI `-o` 非空（显式传入）」+ 注（`-o ""` truthiness 视为未传）落地，与 §3.1「空串/None 视为未提供」对齐 | ✅ 闭合 |
| HG-SEC-066 / OBS-2 | 🟢 | §5 补「-g + data 带 output」用例 | §5 测试表第 8 行「knowledge -g groups.json + data 带 output | 用 data 的 output（决策 7 完整语义）」 | ✅ 闭合 |

**核验结论**：RIG-1/2/3 三处实现落点（argparse 默认值删除、knowledge json_output 提取位置、usage-guide 纳入 D5）全部到位且可实施；OBS-1/2 随 v1.1 落地。上轮全部 5 项意见闭环，无「声明已修但实未修」的半落地。

---

## 二、数据验证（v1.1 引用锚点实测）

| 锚点 | 声明 | 实测 | 结果 |
|:--|:--|:--|:--:|
| html-gen.py:768 | table `-o` argparse default | 逐字一致 | ✅ |
| html-gen.py:779 | knowledge `-o` argparse default | 逐字一致 | ✅ |
| html-gen.py:441 | `out = args.output or 'index.html'` | 逐字一致 | ✅ |
| html-gen.py:484 | `out = args.output or 'kb.html'` | 逐字一致 | ✅ |
| html-gen.py:409-421 | table 结构化 JSON 分支（`else:` L411，body L412-421） | 一致（行号「L409-421」含 `else:` 前两行，容忍范围内） | ✅ |
| html-gen.py:473-475 | knowledge raw 最终化 + items 提取 | 逐字一致 | ✅ |
| usage-guide.md:126 / :186 / :60 | table/knowledge/doc `-o` 描述 | 逐字一致 | ✅ |
| data/_demos-data.json | 无 `output` 的结构化 JSON | dict，keys=[columns,data,tabs,options]，无 output | ✅ |

---

## 三、新发现问题（复审新增，HG-SEC 追踪）

复审在核验 v1.1 的同时，对「影响面/D5 文档同步清单」做了**系统性 grep 枚举**（`默认 index.html / kb.html / -o 默认 / default=` 全仓扫描），发现 D5 清单仍不完整——还有 3 处会文档化「已被删除的静默默认值」的表面未纳入：

| ID | 严重度 | 标题 | 定位 | 状态 |
|:--|:--:|:--|:--|:--:|
| HG-SEC-067 | 🟡 | D5 遗漏 `features.md`（功能登记表 :23「table -o 默认 index.html」将漂移） | features.md:23 | OPEN |
| HG-SEC-068 | 🟡 | D5 遗漏 `skills/html-gen-cli-spec/SKILL.md`（参数惯例表 :44「默认 index.html / kb.html」将漂移） | html-gen-cli-spec/SKILL.md:44 | OPEN |
| HG-SEC-069 | 🟡 | D1-D6 未含 `scripts/build-package.py` 重新生成 `src/html_gen/`（pip 打包源）；根改动后 src 滞留旧默认，**已安装的 `html-gen` 入口（v3.3）行为漂移** | src/html_gen/html-gen.py:768/779 | OPEN |

**HG-SEC-067 详情**：`features.md` 是 IRIS v1.0 格式功能登记表（263 行，含 `✅ — html-gen.py` 状态标记，持续维护）。L23「html-gen table -o/--output — 输出 HTML 路径 (默认 index.html)」在变更后失效，D5 清单未含 features.md。（另：L10「doc -o 默认 index.html」为**既有错误**——doc 实际是 md 派生默认，非本次引入，建议顺带修正。）

**HG-SEC-068 详情**：`skills/html-gen-cli-spec/SKILL.md` 是 CLI 参数惯例权威表（§3「对齐 cli-args-reference.md」），L44「输出文件 | --output | -o | 默认 index.html / kb.html」。D5 的 skills 清单只列 html-gen-table + html-gen-knowledge，未含 html-gen-cli-spec。（附注：该 SKILL 引用 `cli-args-reference.md`，该文件在仓内不存在，为既有悬空引用，非本次范围。）

**HG-SEC-069 详情**：`src/html_gen/` 是 `scripts/build-package.py` 生成的 pip 打包源（`rmtree` + 从根 `copy2` html-gen.py/style-guide.css/layout-* + `copytree` skills）。当前 `src/html_gen/html-gen.py` 与根 `html-gen.py` **byte-identical**，且已安装为 `~/.local/bin/html-gen`（v3.3，`[project.scripts] html-gen = "html_gen:main"`）。若 dev 按 D1-D6 只改根 html-gen.py 而不重跑 build-package.py，则 `html-gen table -d x.json`（文档中所有示例命令形态）仍走旧默认值、特性在已装 CLI 上空转。需在 D-list 补「重跑 build-package.py 同步 src/（若已 pip 安装需同步重装）」。

---

## 四、维度评估（复审新增维度）

### 1. 需求覆盖 ✅（无变化）

4 点需求 + 9 项决策闭合状态与 v1.0 一致，无悬空项。修订未破坏需求映射。

### 2. 架构一致性 ✅

零依赖约束（纯 stdlib 三态解析）不变；中断 stderr + exit 1 对齐「数据文件不存在」；§3.3 显式标注「中断位于写盘之前」。6 处代码改动点（两 cmd + 两 argparse default + 两 JSON 分支）实现落点完整、可实施。

### 3. 优先级矩阵正确性 ✅

三态矩阵行 1「CLI `-o` 非空」+ 空串注消除措辞歧义；`-o ""` 与 title（`is not None`）/subtitle（显式含空串覆盖）的空串语义不对称已显式文档化、有意区分。

### 4. 向后兼容 ✅

cmd_demo --rebuild（L988 显式传 output）/ doc/slide（md 派生）/ 现有测试（grep 全部显式传 `-o`）零依赖静默默认值，v1.0 已实测确认。修订未改变此结论。

### 5. 文档同步完整性 ⚠️（新发现 3 处）

D5 清单已覆盖 AGENTS.md / HELP / table-guide + knowledge-guide（含 md 源）/ usage-guide.md（v1.1 增）/ README / skills table + knowledge。但系统性 grep 枚举发现仍漏 `features.md`、`skills/html-gen-cli-spec`、以及 `src/` 打包源（非文档但同属「变更面」）三处。D5 完整性是**连续两轮**的问题（v1.0 漏 usage-guide，v1.1 仍漏 3 处），建议 dev 以「全仓 grep `默认 index.html`/`kb.html`/`-o 默认`」为兜底枚举，而非靠人工回忆。

### 6. 测试规划 ✅

§5 测试表 11 用例覆盖三态主路径 + 空串 + --quiet + knowledge 三态 + `-g` 组合（OBS-2 已补）+ 简单数组 + doc/slide 回归；纯 CLI 行为（subprocess 断言、无需 Selenium）声明正确。无新增缺口。

---

## 五、评分

```
Base 100
  🟡 HG-SEC-067  -5  (features.md:23 文档漂移)
  🟡 HG-SEC-068  -5  (html-gen-cli-spec SKILL 文档漂移)
  🟡 HG-SEC-069  -5  (src/ build-package 未同步 → 已装 CLI 滞留旧默认)
  ─────────────────────
  85 / 100（B）
```

## 六、修改意见（按文档待办清单编号定位）

**RIG-4（067）→ D5**：D5 文档同步清单增 `features.md`——L23「table -o/--output 默认 index.html」改「必填（CLI `-o` 或 JSON `output` 二选一）」；顺带修 L10「doc -o 默认 index.html」既有错误（doc 实为 md 派生默认，`-o` 可选）。

**RIG-5（068）→ D5**：D5 增 `skills/html-gen-cli-spec/SKILL.md`——L44「默认 index.html / kb.html」改「必填（CLI `-o` 或 JSON `output` 二选一）」。

**RIG-6（069）→ D-list**：D 清单补一步「`python3 scripts/build-package.py` 重新生成 src/html_gen/（含 skills 副本）；若已 pip 安装（`~/.local/bin/html-gen` v3.3）需同步重装」。建议并入 D5 或单列 D7，并在 §4 影响面分析「代码 6 处」补注「+ src/ 打包源（build-package.py 重生成）」。

**兜底建议（非计分）**：dev 实施 D5 时以全仓 `grep -rn "默认.*index.html\|默认.*kb.html\|default='index.html'\|default='kb.html'"` 结果为准逐项清点，避免第三轮遗漏。

---

## 七、结论

**CONDITIONAL PASS（B）**。上轮 5 项意见（1 🔴 + 2 🟡 + 2 🟢）全部正确闭合，核心三态解析设计已可实施、实现落点完整、向后兼容零回归。复审新发现 3 处 🟡 均为「影响面/D5 清单完整性」遗漏（features.md、html-gen-cli-spec、build-package src 同步），不涉及逻辑缺陷，但会导致 dev 按 D1-D6 实施后残留 3 处漂移表面（含已安装 CLI 行为滞留）。

**处理**：不 push；ops 按 RIG-4/5/6 修 v1.2 后复审（PASS 后生成 dev 实施 prompt 转 dev 按 D1-D6 + 3 补充实施）。
