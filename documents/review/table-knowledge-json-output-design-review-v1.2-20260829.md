# table/knowledge JSON 顶层 output 字段设计 — review报告 v1.2（复审）

- **日期**: 2026-08-29
- **审查人**: Security Reviewer（review role）
- **级别**: L2（design-document-review）
- **对象**: `documents/solutions/table-knowledge-json-output-design-v1.2-20260829.md`（HEAD `0295e8f`，HTML-GEN-CL003）
- **上轮**: v1.1 复审 CONDITIONAL PASS 85/B，HG-SEC-067..069（3 🟡 影响面遗漏）
- **结论**: 🟢 **PASS 100/100（A）** — RIG-4/5/6 三处修复全部到位且锚点逐字实测核验通过；无新增 🔴/🟡；1 处 🟢 记录（HG-SEC-070，非阻断，折入 D5）

---

## 一、上轮意见修正核验（逐条实测）

| 意见 | 严重度 | v1.2 声明 | 实测核验 | 结果 |
|:--|:--:|:--|:--|:--:|
| HG-SEC-067 / RIG-4 | 🟡 | §4 D5 增 `features.md`：L23 改「必填」；顺带修 L10「doc -o 默认 index.html」既有错误 | `features.md:10`「doc -o/--output — 输出 HTML 路径 (默认 index.html)」逐字一致；`features.md:23`「table -o/--output — 输出 HTML 路径 (默认 index.html)」逐字一致 | ✅ 闭合 |
| HG-SEC-068 / RIG-5 | 🟡 | §4 D5 增 `skills/html-gen-cli-spec/SKILL.md`：L44 改「必填」 | `SKILL.md:44`「输出文件 | --output | -o | 默认 index.html / kb.html」逐字一致 | ✅ 闭合 |
| HG-SEC-069 / RIG-6 | 🟡 | §6 新增 D7 重跑 build-package.py；§4 补注 src/ 打包源 | `scripts/build-package.py` 存在；`src/html_gen/html-gen.py` 与根 `html-gen.py` **byte-identical**（sha256 前缀 459af1bf，均 46266 bytes）；`~/.local/bin/html-gen` 实测 v3.3 (2026-08-28) 已安装 | ✅ 闭合 |
| 兜底建议 | — | §4 D5 增「全仓 grep 兜底枚举」 | 落地于 §4 影响面分析 D5 清单末条（「兜底枚举（dev 实施 D5 时）」） | ✅ 采纳 |

**核验结论**：RIG-4/5/6 三处修复全部到位且可实施。v1.2 对 L10（doc 既有错误）、L23（table）、L44（cli-spec）三处锚点的引用与实际文件逐字一致，无「声明已修但实未修」的半落地。D7 的 build-package 同步是真实必要步骤——已装 `~/.local/bin/html-gen` 入口（v3.3）确认存在，若漏 D7 则特性在已装 CLI 上空转。

---

## 二、数据验证（v1.2 引用锚点实测）

| 锚点 | 声明 | 实测 | 结果 |
|:--|:--|:--|:--:|
| html-gen.py:768 | table `-o` argparse `default='index.html'` | 逐字一致 | ✅ |
| html-gen.py:779 | knowledge `-o` argparse `default='kb.html'` | 逐字一致 | ✅ |
| html-gen.py:441 | `out = args.output or 'index.html'` | 逐字一致 | ✅ |
| html-gen.py:484 | `out = args.output or 'kb.html'` | 逐字一致 | ✅ |
| src/html_gen/html-gen.py | 「当前与根 byte-identical」 | sha256 均 459af1bf…，byte-identical = True | ✅ |
| ~/.local/bin/html-gen | 「已安装 v3.3」 | 存在，`html-gen version` → v3.3 (2026-08-28) | ✅ |
| data/_demos-data.json | 无 `output` 的结构化 JSON | dict，无 `output` 键 | ✅ |
| features.md:10 / :23 | L10/L23 现状与 D5 声明一致 | 逐字一致 | ✅ |
| skills/html-gen-cli-spec/SKILL.md:44 | L44 现状与 D5 声明一致 | 逐字一致 | ✅ |

---

## 三、维度评估

### 1. 需求覆盖 ✅
4 点需求 + 9 项决策闭合状态与 v1.0/v1.1 一致，无悬空项。修订未破坏需求映射。

### 2. 架构一致性 ✅
零依赖约束（纯 stdlib 三态解析）不变；中断 stderr + exit 1 对齐「数据文件不存在」；§3.3 显式标注「中断位于写盘之前」。6 处代码改动点（两 cmd + 两 argparse default + 两 JSON 分支）实现落点完整。

### 3. 修订引入问题检查 ✅（无新增问题）
- **D7 位置**：§6 排在 D6（全量回归）之后，正确——D7 是打包/部署同步步骤，回归验证根代码在前、build-package 同步在后；§7 验证清单 item 8「src 与根 byte-identical」兜住同步正确性。
- **影响面一致性**：§4 保留「代码 6 处」计数，src/ 打包源以独立注记（HG-SEC-069）补充，未与「6 处」计数混淆，与 RIG-6「§4 补注 src/」指令一致。
- **修订记录表**：§0 v1.1→v1.2 表完整列出 HG-SEC-067/068/069 及兜底建议处理，无缺项。

### 4. 向后兼容 ✅
cmd_demo --rebuild（L988 显式传 output）/ doc/slide（md 派生）/ 现有测试（全部显式 -o）零依赖静默默认值，v1.0/v1.1 已实测确认，修订未改变。

### 5. 测试规划 ✅
§5 测试表 11 用例覆盖三态主路径 + 空串 + --quiet + knowledge 三态 + `-g` 组合 + 简单数组 + doc/slide 回归；纯 CLI subprocess 断言（无需 Selenium）声明正确。

### 6. 文档同步完整性 🟢（1 处残留记录，非阻断）
D5 现覆盖 AGENTS.md / HELP / guides / usage-guide.md / README / features.md / skills（含 html-gen-cli-spec），并附全仓 grep 兜底。但 features.md 有三条 `-o` 行（doc L10 / table L23 / knowledge L30），D5 显式枚举 L10、L23，**未显式列 L30**（knowledge `-o`）。L30 现状为「输出 HTML 路径」（无错误默认声明，非错误），但实施后应与 L23 对称改「必填」。兜底 grep 模式（`默认.*index.html\|默认.*kb.html\|default=...`）**不会命中 L30**（L30 无「默认/default」字样），属兜底枚举的盲区。定 🟢 HG-SEC-070 记录，折入 D5 由 dev 一并对称修正，不阻断交付。

---

## 四、评分

```
Base 100
  （上轮 🟡×3 已闭合，本轮无 🔴/🟡）
  🟢 HG-SEC-070  -0  (features.md:30 knowledge -o 对称表述，折入 D5，记录)
  ─────────────────────
  100 / 100（A）
```

---

## 五、结论

**PASS（A）**。上轮 CONDITIONAL PASS 的 3 处 🟡（RIG-4/5/6）全部正确闭合，锚点逐字实测核验通过（features.md L10/L23、cli-spec SKILL.md L44、build-package.py src/ 同步 + 已装 CLI v3.3 确认）。修订未引入新 🔴/🟡，D7 位置、影响面计数、修订记录表均一致。整体方案可交付 dev 按 D1-D7 实施。

**残留 1 处 🟢（HG-SEC-070，非阻断）**：D5 未显式枚举 `features.md:30`（knowledge `-o` 行），且兜底 grep 模式不会命中该行（无「默认/default」字样）；dev 实施 D5 时需将 L30 与 L23 对称改「必填（CLI `-o` 或 JSON `output` 二选一）」。

**处理**：PASS → 生成 dev 实施 prompt（转 dev 按 D1-D7 实施）；审计链三件套 + commit + auto-push。

---

## 六、dev 实施依据（D1-D7）

| 步骤 | 内容 |
|:--|:--|
| D1 | cmd_table 三态解析 + argparse L768 删 `default='index.html'` + L409-421 加 json_output |
| D2 | cmd_knowledge 三态解析 + argparse L779 删 `default='kb.html'` + L475 raw 最终化后提取 json_output |
| D3 | 中断文案统一（两处共用，stderr + exit 1，写盘前） |
| D4 | tests/test_json_output.py 11 用例 |
| D5 | 文档同步（AGENTS.md / HELP / guides / usage-guide.md / README / features.md / skills 含 html-gen-cli-spec）；**补 features.md L30 knowledge -o 与 L23 对称改「必填」**；全仓 grep 兜底枚举 |
| D6 | 全量回归 `python3 -m pytest tests/ -q -n 4` |
| D7 | `python3 scripts/build-package.py` 同步 src/html_gen/（含 skills 副本）+ 已 pip 安装则重装 |
