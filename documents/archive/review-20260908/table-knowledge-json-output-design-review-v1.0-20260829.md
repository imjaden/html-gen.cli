# table/knowledge JSON 顶层 output 字段设计 — review报告 v1.0

- **日期**: 2026-08-29
- **审查人**: Security Reviewer（review role）
- **级别**: L2（design-document-review）
- **对象**: `documents/solutions/table-knowledge-json-output-design-v1.0-20260829.md`（HEAD `e76bcde`，HTML-GEN-CL003）
- **结论**: 🔴 **CONDITIONAL PASS 75/100（B）** — 1 🔴 + 2 🟡 + 2 🟢，修 v1.1 后复审

---

## 一、数据验证

核实设计文档引用的代码锚点（html-gen.py，1078 行）：

| 锚点 | 设计声明 | 实测 | 结果 |
|:--|:--|:--|:--:|
| L420-428 | title/subtitle 优先级 CLI > JSON > 默认 | L424 `args.title if ... is not None` / L425-428 subtitle 显式含空串覆盖 | ✅ |
| L441 | cmd_table `out = args.output or 'index.html'` | 一致 | ✅ |
| L484 | cmd_knowledge `out = args.output or 'kb.html'` | 一致 | ✅ |
| L397-399 | 数据文件不存在 exit 1 + stderr | 一致（`❌ 数据文件不存在: ...` → stderr → exit 1） | ✅ |
| L988 | cmd_demo --rebuild 直调 cmd_table 传 output | L985-989 `output=str(DEMOS_DIR/'demos-index.html')` | ✅ |
| L313 / L384 | doc/slide md 派生默认 | L313 `.html` / L384 `.slide.html`，无 JSON 依赖 | ✅ |
| L409-421 | table 结构化 JSON 分支 | L411 `else:` + L412-421 结构化体（`data`/`rows`/`columns`/`tabs`/`options`/`title`/`subtitle`） | ✅（行号略偏，L411 为 `else:`） |
| — | 静默默认值来源 | **argparse L768 `t.add_argument('-o','--output', default='index.html')` / L779 `k.add_argument('-o','--output', default='kb.html')`** | 🔴 **设计遗漏** |

**关键发现（数据验证锚点缺失）**：table/knowledge 的 `-o` 在 argparse 定义处自带 `default='index.html'`/`default='kb.html'`。因此 `args.output` 在未显式传 `-o` 时**恒为真值**。设计 §3.4 的三态步骤 1「`args.output` 非空 → 用之」将永远命中，步骤 2（JSON output）与步骤 3（中断）**不可达**——整个特性空转。设计 §4「影响面分析 → 代码」声称改动点仅「两处 cmd + 两处 JSON 解析分支」，遗漏了 argparse 默认值的两处必改点。

---

## 二、维度评估（6 审计维度）

### 1. 需求覆盖 ✅

4 点需求全部落位：① `output` 字段内嵌（§3.1）；② CLI `-o` 优先级最高（§3.2 矩阵行 1）；③ 无 `-o` 且无 JSON output 中断（§3.3 + exit 1）；④ 批量场景文档化不加 `--all`（决策 5）。9 项决策（1A/2A/3/4A/5/6/7/8/9）在 §2 汇总表与 §3 细节逐条自洽，无决策缺失、无「文档写了但需求没提」的悬空项。

### 2. 架构一致性 ⚠️

- 零依赖：✅ 纯 stdlib 三态解析，无新 import。
- 错误处理风格：✅ stderr + exit 1 对齐「数据文件不存在」语义（§3.3）。
- **🔴 实现落点不完整**：见「数据验证」——三态替换仅定位到 L441/L484（症状位），漏掉 argparse L768/L779 的 `default=`（根因位）。这是「spec 声称 X、代码实为 Y」类缺陷，直接阻断 D1/D2 按文实施。

### 3. 优先级矩阵正确性 ⚠️

- 三态（CLI > JSON > 中断）主路径无歧义，与 title/subtitle 优先级顺序自洽。
- **🟢 空串语义不对称**：title 用 `is not None`（`--title ""` 被 honored），subtitle 用「显式传入含空串覆盖」；而 output 的步骤 1 用 truthiness（`-o ""` 视为未传 → 落到 JSON/中断）。矩阵行 1 写「显式传入」未限定「非空」，`-o ""` 属退化输入，建议矩阵改「CLI `-o` 非空」表述（详见 HG-SEC-065）。

### 4. 向后兼容 ✅

- cmd_demo --rebuild（L988）已显式传 output → 移除 argparse 默认后零影响（实测已确认）。
- doc/slide（L313/L384）md 派生默认，无 JSON 分支 → 不受影响。
- **已排查现有测试**：grep tests/ 全部 table/knowledge 子进程调用（test_templates / test_render_summary / test_corner_privacy / test_initial_hidden_split / test_videos / test_table_features `_gen_table_page`）均显式传 `-o`；`test_demos_index.py:97/99` 的「table -d data.json」仅为展示字符串非真实调用。**零测试依赖静默默认值**，行为变更（静默默认 → 中断）无回归风险。
- 行为变更点（静默 index.html/kb.html → 中断）在 §3.5 明确标注「有意」，符合需求 3。

### 5. 文档同步完整性 ⚠️

D5 清单覆盖 AGENTS.md / HELP 文本 / table-guide + knowledge-guide / README.md + README.zh.md / skills table + knowledge，但 **🟡 遗漏 `demos/usage-guide.md`**——「html-gen 完整使用说明」，其 table 节（usage-guide.md:126）明确写「`-o, --output` 输出 HTML 路径（默认 `index.html`）」，knowledge 节（:186）写「输出 HTML 路径」，doc 节（:60）写「默认同目录同名.html」。此变更后 usage-guide 若不更新，将文档化一个已被删除的默认行为（详见 HG-SEC-063）。

### 6. 测试规划 ⚠️

§5 测试表覆盖三态主路径（CLI 覆盖 / JSON 生效 / 皆无中断）、空串、--quiet、knowledge 三态、groups、简单数组、doc/slide 回归——主分支齐全。**🟡 两处缺口**：① 缺「`-g` groups.json + data 文件带 output → 用 data 的 output」组合（现仅测「groups 文件自身带 output 被忽略」）；② 纯 CLI 行为断言（subprocess）无需 Selenium，设计已正确声明。D4 用例可执行，但 knowledge json_output 提取位置未指定（见 HG-SEC-064）。

---

## 三、安全事项（findings，HG-SEC 追踪）

| ID | 严重度 | 标题 | 定位 | 状态 |
|:--|:--:|:--|:--|:--:|
| HG-SEC-062 | 🔴 | argparse `default=` 未纳入实现计划，三态步骤 2/3 不可达 | html-gen.py:768/779（§3.4/D1/D2/§4 遗漏） | OPEN |
| HG-SEC-063 | 🟡 | D5 文档同步清单遗漏 `demos/usage-guide.md`（「默认 index.html」将漂移） | usage-guide.md:126/186 | OPEN |
| HG-SEC-064 | 🟡 | D2 cmd_knowledge 的 json_output 提取位置未指定（raw 三处读取、items/data 键） | html-gen.py:473-475 | OPEN |
| HG-SEC-065 | 🟢 | 矩阵「显式传入」未限定非空，`-o ""` 与 title/subtitle 空串语义不对称 | §3.2 | 随 v1.1 |
| HG-SEC-066 | 🟢 | §5 测试矩阵缺「`-g` + data 文件 output 生效」组合用例 | §5 | 随 v1.1 |

---

## 四、修改意见（按文档待办清单编号定位）

**🔴 RIG-1 → D1 + D2（必须修，一句话级）**
- **问题**：§3.4/D1/D2 只改 cmd_table L441 / cmd_knowledge L484 的 `out = args.output or ...`，但静默默认值的根因在 argparse——L768 `default='index.html'`、L779 `default='kb.html'`。不删这两个 default，`args.output` 恒真，JSON output 与中断两条分支永不触发。
- **建议改法**：D1 增「html-gen.py:768 `t.add_argument('-o','--output', default='index.html')` → 删 `default='index.html'`（argparse 缺省为 None）」，D2 同理删 L779 `default='kb.html'`；§4「影响面分析 → 代码」同步把「两处 cmd」更正为「两处 cmd + 两处 argparse default + 两处 JSON 解析分支」。

**🟡 RIG-2 → D5（文档同步）**
- **问题**：D5 清单漏 `demos/usage-guide.md`（→ usage-guide.html 重新生成）。usage-guide.md:126 现写「默认 `index.html`」，变更后失效。
- **建议改法**：D5 增 `demos/usage-guide.md`（table 节 :126 改「必填（CLI `-o` 或 JSON `output` 二选一）」；knowledge 节 :186 同理；doc 节 :60 不受影响，md 派生默认保留）。

**🟡 RIG-3 → D2（实现精度）**
- **问题**：§3.4「结构化 JSON 分支（L411-421）加 json_output」仅对应 cmd_table；cmd_knowledge 无对应提取指令。其 `raw` 在 L473-475 最终化（无 `-g` 时 data_path 读 2 次、有 `-g` 时读 1 次），且结构化键为 `items`/`data`（非 table 的 `columns`）。
- **建议改法**：D2 增「在 L475 raw 最终化后加 `json_output = raw.get('output') if isinstance(raw, dict) else None`；knowledge 结构化格式键为 `items`/`data`（非 `columns`），简单数组 `json_output = None`」。

**🟢 OBS-1 → §3.2（随 v1.1，不阻断）**：矩阵行 1「显式传入」改为「CLI `-o` 非空」，与 §3.1「output 空串/None 视为未提供」语义对齐，消除 `-o ""` 与 title/subtitle `is not None` 的措辞歧义。

**🟢 OBS-2 → §5（随 v1.1，不阻断）**：测试表补一行「knowledge `-g` groups.json + data 文件带 output → 用 data 的 output」（覆盖决策 7 的完整语义：只认 data 文件的 output）。

---

## 五、遗漏的风险点（补充提示）

1. **`data/_demos-data.json` 现为「无 output 的结构化 JSON」**：`demo --rebuild` 内部直调 cmd_table 已传 output（零影响），但此后**手工** `html-gen table -d data/_demos-data.json`（不带 `-o`）将从「静默写 index.html」变为「中断」。这是需求 3 的预期行为变更，但建议在 D5 的 usage-guide / AGENTS.md 批量场景说明中顺带提一句，避免用户误判为 bug。
2. **中断必须置于写盘之前**：三态解析在 L441/L484 计算 `out` 后、`Path(out).write_text` 之前执行 `sys.exit(1)` 是自然顺序，但 D1/D2 实施时应确认中断分支位于写盘前（当前代码结构天然满足，仅提示不要写成「先写再判断」）。
3. **`output` 指向不存在的父目录**：`Path(out).write_text` 会抛 FileNotFoundError（Python traceback 而非友好文案）。此为 `-o` 既有行为、非本次引入，但既然需求 3 已做「友好提示」方向，可作为后续可选增强（非本次范围）。

---

## 六、评分

```
Base 100
  🔴 HG-SEC-062  -15  (argparse default 遗漏 → 特性空转)
  🟡 HG-SEC-063   -5  (usage-guide.md 文档漂移)
  🟡 HG-SEC-064   -5  (D2 实现落点未指定)
  🟢 HG-SEC-065/066  0 (记录)
─────────────────────
  75 / 100（B）
```

## 七、结论

**CONDITIONAL PASS（B）**。方案方向正确、需求覆盖完整、向后兼容零回归（已实测排查测试与内部调用方），仅 1 处 🔴 实现落点遗漏（argparse `default=`）会直接导致特性空转，须修 v1.1 后复审；2 处 🟡（usage-guide 文档漂移、D2 提取位置）与 2 处 🟢 随 v1.1 一并落地。

**处理**：不 push；ops 按 RIG-1/2/3 修 v1.1 后通知复查（PASS 后生成 dev 实施 prompt 转 dev 按 D1-D6 实施）。
