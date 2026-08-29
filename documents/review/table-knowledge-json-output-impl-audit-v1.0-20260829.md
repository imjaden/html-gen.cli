# table/knowledge JSON 顶层 output 字段实现 — review报告 v1.0（实现审计）

- **日期**: 2026-08-29
- **审查人**: Security Reviewer（review role）
- **级别**: L2（implementation-audit）
- **对象**: HTML-GEN-CL003 实现 commit 链 `f6efacb`（fix 源码+测试）→ `27a4470`（docs D5）→ `1fae2fd`（AGENTS 计数同步）
- **设计**: `documents/solutions/table-knowledge-json-output-design-v1.2-20260829.md`（PASS 100/A，commit `0295e8f`）
- **设计评审**: `documents/review/table-knowledge-json-output-design-review-v1.2-20260829.md`（PASS，🟢 HG-SEC-070 折入 D5）
- **结论**: 🟢 **PASS 100/100（A）** — D1-D7 全数落地且逐条实测核验通过；HG-SEC-070（features.md L30）由本次 D5 对称修正闭合；无新增 🔴/🟡；2 处 🟢 记录（非阻断）

---

## 一、数据验证（ops 声称证据逐条复核）

| # | ops 声称 | 实测复核 | 结果 |
|:--|:--|:--|:--:|
| 1 | `table -d countries -o /tmp/x.html` CLI 覆盖 | 生成到 CLI 路径，exit 0 | ✅ |
| 2 | 临时 JSON 带 output 无 -o → JSON output 路径 | 生成到 `json.html`，exit 0 | ✅ |
| 3 | 无 -o 且 JSON 无 output → exit 1 + stderr | `exit=1`，stderr 含「未指定输出文件」 | ✅ |
| 4 | knowledge 三态 + `-g` + data 带 output | JSON output 生成；皆无 `exit=1` 提示 | ✅ |
| 5 | `demo --rebuild` → demos-index.html 不中断 | `18 独立案例 → demos-index.html`，exit 0，幂等（工作树无 diff） | ✅ |
| 6 | `table -d _demos-data.json` 手工无 -o → 中断 | `exit=1` + 提示（预期行为变更） | ✅ |
| 7 | src/html_gen/html-gen.py 与根 byte-identical | sha256 均 `7e50ad87…`，各 47620 bytes | ✅ |
| 8 | 全量 pytest 235 passed | `235 passed in 34.47s`（224 + 11 新增） | ✅ |

**核验结论**：8 项证据全部属实，无「声称已测但实未发生」的半落地。

---

## 二、维度评估

### 1. 实现与设计 D1-D7 一致性 ✅

| 项 | 设计锚点 | 实测 | 结果 |
|:--|:--|:--|:--:|
| D1 根因位 argparse default 删除 | 删 `default='index.html'` | `html-gen.py:790` `t.add_argument('-o','--output', help=…)` 无 default（原 L768，HELP 文本增行致漂移至 L790） | ✅ |
| D2 根因位 argparse default 删除 | 删 `default='kb.html'` | `html-gen.py:801` `k.add_argument('-o','--output', help=…)` 无 default（原 L779 → L801） | ✅ |
| D1 table 三态 | L409-421 分支 + `out = args.output or json_output` | `L414`（简单数组 None）/`L426`（`raw.get('output')`）/`L447-450`（三态 + `not out` → stderr + exit 1） | ✅ |
| D2 knowledge 三态 | L475 raw 最终化后 isinstance dict | `L486` `json_output = raw.get('output') if isinstance(raw, dict) else None`（在 `L484` items 最终化之后） | ✅ |
| D3 中断文案共用常量 | NO_OUTPUT_MSG 两处共用 | `L28` 定义，`L449`/`L498` 引用；stderr + exit 1 + 写盘前（`write_text` 之前） | ✅ |
| 决策 7 多文件源 | knowledge 只认 data output | `-g` 时仍从 data 文件提取 json_output；groups 文件 output 被忽略 | ✅ |
| 向后兼容 | doc/slide md 派生默认不动 | doc/slide argparse 无 default（`L769`/`L779`），`test_11` 通过 | ✅ |

**argparse 行号漂移说明（🟢 记录）**：设计引用的 L768/L779 是「改动前」锚点；实现时 HELP/help 参数文本增加使 table/knowledge 的 `-o` 定义漂移至 L790/L801。实现按内容定位（删除两处 default）正确，无功能影响——记录以利后续追溯，见 HG-SEC-071。

### 2. 测试质量 ✅

`tests/test_json_output.py` 11 用例覆盖设计 §5 全表：

| 设计 §5 用例 | 实测覆盖 |
|:--|:--:|
| CLI -o 覆盖 JSON output | test_01 ✅ |
| 无 CLI -o + JSON output 生效 | test_02 ✅ |
| 两者皆无 → exit 1 | test_03 ✅ |
| JSON output 空串 | test_04 ✅ |
| CLI -o 空串 | test_05 ✅ |
| --quiet + 两者皆无 | test_06 ✅ |
| knowledge 三态 | test_07 ✅ |
| knowledge -g + data output | test_08 ✅ |
| knowledge groups output 忽略 | test_09 ✅ |
| 简单数组无 -o | test_10 ✅ |
| doc/slide 无回归 | test_11 ✅ |

- 隔离：`setUp`/`tearDown` 用 `tempfile.mkdtemp` 每用例独立临时目录，pytest-xdist 并行安全 ✅
- 纯 subprocess 断言（无 Selenium），与设计 §5「纯 CLI 行为」声明一致 ✅
- 覆盖粒度观察：`test_05` 仅覆盖「CLI 空串→JSON 生效」分支，未单独覆盖「CLI 空串+皆无 JSON→中断」子分支（行为由 `args.output or json_output` truthiness 语义等价 test_03 路径，已正确实现）——🟢 记录，见 HG-SEC-072。

### 3. 文档同步完整性（D5 + HG-SEC-070）✅

| 表面 | 设计要求 | 实测 | 结果 |
|:--|:--|:--|:--:|
| AGENTS.md | `-o` 必填二选一 + 批量场景 + output 字段 | CLI 子命令节 + 批量渲染场景节 + 数据格式节三处齐全 | ✅ |
| html-gen.py HELP | help table/knowledge 补 output + 输出目标 | `HELP_TABLE`（L582-583）+ `HELP_KNOWLEDGE`（L668-669）「CLI -o > JSON output > 中断」 | ✅ |
| features.md L10/L23/L30 | 三处对称 | L10 doc「可选; 缺省 md 派生」、L23 table「必填」、L30 knowledge「必填」 | ✅ |
| cli-spec SKILL.md L44 | 默认值改必填 | 「必填（CLI `-o` 或 JSON 顶层 `output` 二选一；table/knowledge）」 | ✅ |
| html-gen-table/knowledge SKILL | 数据格式补 output | table L56 / knowledge L40 均补 `output` 行 | ✅ |
| README.md / README.zh.md | Commands 节必填说明 | 双语均补 | ✅ |
| usage-guide.md / table-guide / knowledge-guide | 必填表述 + md 源同步 | usage-guide table(:126)/knowledge(:186) 改「必填」 | ✅ |

**兜底 grep 复核**（排除 cache/ src/ documents/review/ documents/solutions/ review-log.md 历史）：
- `*.py` 残留 `默认 index.html / 默认 kb.html / default='index.html'/'kb.html'` → **0 命中** ✅
- `*.html` 残留 `默认.*index.html / 默认.*kb.html / 输出 HTML 路径 (默认` → **0 命中** ✅
- `*.md` 命中仅限历史 review/solutions 文档（描述「将漂移」的旧行为，属预期保留）✅

**HG-SEC-070（design review 🟢 残留）**：`features.md:30`（knowledge `-o`）已由本次 D5 与 L23 对称改「必填」——闭合。

### 4. 打包源（D7）✅

| 项 | 实测 | 结果 |
|:--|:--|:--:|
| src/html_gen/html-gen.py 与根 byte-identical | sha256 均 `7e50ad87…`（47620 bytes） | ✅ |
| src/ git 状态 | `git ls-files src/` 空、`git check-ignore` 命中 → gitignored 生成物，正确不入 commit | ✅ |
| 已装入口 `~/.local/bin/html-gen` | 90-byte bash wrapper：`exec python3 "…/html-gen.cli/html-gen.py" "$@"` — 直指根源码，无 stale 风险 | ✅ |

**D7 打包同步确认**：src/html_gen/html-gen.py mtime `Aug 29 10:30`，含 8 处新逻辑（NO_OUTPUT_MSG/json_output），byte-identical 于根——build-package 同步已生效。已装 CLI 为 exec 根源码的 thin wrapper，特性在已装入口上立即生效，无需重装（优于设计评审时的担忧）。

### 5. 无回归 ✅

全量 `python3 -m pytest tests/ -q -n 4` → **235 passed**（224 + 11 新增 test_json_output）。AGENTS.md 计数 224→235 同步（`1fae2fd`）准确。

### 6. 提交单元自洽 ✅

| commit | 文件 | 夹带检查 |
|:--|:--|:--:|
| f6efacb | html-gen.py + tests/test_json_output.py（2 文件） | 无 drama 文件 |
| 27a4470 | 13 文件（AGENTS/README/features/skills/guides，纯 docs） | 无 drama 文件 |
| 1fae2fd | AGENTS.md（1 文件，计数同步） | 无 drama 文件 |

`data/_drama-table-history-strategy.json` + `demos/drama/history-strategy-table.html` 为另一会话 pre-existing working-tree 修改，**不在** 3 commit 内（`git show --stat` 复核确认）。

---

## 三、安全事项

实现为纯 Python 标准库三态解析，无新增攻击面：

- 无 subprocess / shell=True / 字符串拼接命令构造（零注入面）
- `json.load` + `Path.write_text`，无 innerHTML/XSS 新路径
- `NO_OUTPUT_MSG` 走 stderr，`--quiet` 不静默错误（正确）
- JSON `output` 路径与既有 `-o` 同信任模型（用户自有数据文件），覆盖保护/后缀校验按设计 4A 显式不保护——非本次引入，非新漏洞

| # | Severity | Title | Status |
|:--:|:---:|:---|:---:|
| HG-SEC-070 | 🟢 | features.md:30（knowledge `-o`）未纳入 D5 — 折入 D5 对称修正 | ✅ closed（本次 D5） |
| HG-SEC-071 | 🟢 | 设计 argparse 行号锚点 L768/779 → 实际 L790/801 漂移（HELP 增行），内容定位正确 | ✅ record（非缺陷） |
| HG-SEC-072 | 🟢 | test_05 未单独覆盖「CLI 空串+皆无 JSON→中断」子分支（等价 test_03 truthiness 路径） | ✅ record（可选补断言） |

---

## 四、评分

```
Base 100
  无 🔴 / 无 🟡
  🟢 HG-SEC-070  -0  (features.md L30，本次 D5 闭合)
  🟢 HG-SEC-071  -0  (行号漂移，记录)
  🟢 HG-SEC-072  -0  (测试粒度，记录)
  ─────────────────────
  100 / 100（A）
```

---

## 五、结论

**PASS（A）**。HTML-GEN-CL003 实现链（`f6efacb`/`27a4470`/`1fae2fd`）对设计 D1-D7 全数落地，ops 声称 8 项证据逐条实测复核通过：

- 三态逻辑 `CLI -o > JSON output > 中断(exit 1)` 在 table（L447-450）与 knowledge（L496-499）均正确实现，argparse 两处 default 已删（根因位），NO_OUTPUT_MSG 共用常量 + stderr + 写盘前中断
- knowledge 决策 7（只认 data output、groups 忽略）完整语义通过 test_08/test_09 锁定
- 11 用例覆盖设计 §5 全表，tempfile 隔离 xdist 兼容
- D5 文档同步 8 表面全齐，HG-SEC-070（features.md L30）对称修正闭合，兜底 grep 0 残留
- D7 打包源 byte-identical（`7e50ad87`），已装 CLI 为 exec 根源码 wrapper 无 stale 风险
- 全量 235 passed 无回归；3 commit 自洽无 drama WIP 夹带

**处理**：PASS → 写审计三件套 + commit + auto-push（github + gitee 双 remote）。遗留 2 处 🟢（HG-SEC-071/072）为记录级非阻断，不需 dev 回改。

---

## 六、dev 后续（非阻断，可选）

| 项 | 内容 | 优先级 |
|:--|:--|:--:|
| HG-SEC-072 | 可选为 test_05 补「`-o ""` 且 JSON 无 output → exit 1」断言，锁死空串退化全路径 | P2 |
| — | 后续可选增强：output 指向不存在父目录时 FileNotFoundError 友好提示（设计 §3.5 已注明不在本次范围） | P2 |
