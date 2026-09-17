# help 契约基础设施 — ops 独立核查 v1.0

> 日期: 2026-09-17
> 闭环: HTML-GEN-CL012（设计 v1.2 §A/§B/§D(table)/§E/§G）
> 实现: `92ff7d9`（`feat@cli: help 契约基础设施 — TEMPLATE_CONTRACT + render_help + table 双向守卫 + 未知键 warn`）
> 口径: 不采信 dev 自报，全部由 ops 独立实测

## 0. 结论

**PASS（12 项实测全过）**，**1 项待人工**：`AGENTS.md` 测试计数同步被守卫拦截（见 §3），需人工应用。

## 1. 逐项实测

| # | 项 | 命令/方法 | 实测 | 判定 |
|:--|:--|:--|:--|:--|
| OV-1 | 提交面 | `git show --name-only HEAD` | 仅 `html-gen.py` + `tests/test_help_contract.py`；工作区空 | ✅ |
| OV-2 | 契约与渲染 | importlib 加载 | `TEMPLATE_CONTRACT` = doc/knowledge/slide/table；`render_help('table')` 4634 字符 | ✅ |
| OV-3 | P0 键 10 个 | `html-gen help table \| grep -qE "\b$k\b"` | initialHidden / splitFull / pillFilter / format / videos / datetime / clickMode / searchFields / showIndex / defaultFilter **全部 OK** | ✅ |
| OV-4 | 语义可辨 | 同上 grep `hide`/`initialHidden` | L65 `hide: 永不可见 (表格/筛选/分栏详情 全部排除)`；L66 `initialHidden: 默认收起, ⚙️ 面板可开启; 分栏详情仍全列渲染 (与 hide 语义不同)` | ✅ |
| OV-5 | 守卫测试 | `pytest tests/test_help_contract.py -q -n 0` | `14 passed, 7 subtests passed` | ✅ |
| OV-6 | 全量回归 | `pytest tests/ -q -n 0` | `326 passed, 7 subtests passed`（基线 312 + 14） | ✅ |
| OV-7 | warn 双用例 | 结构化含 `bogusKey` / 简单数组 | (a) 报「未知」；(b) **不报**（不误伤 data 行字段） | ✅ |
| OV-8 | 生成路径等价 | countries 按 rebuild.args 重建 + `cmp` | 与入库产物**字节一致** | ✅ |
| OV-9 | warn 作用域实现 | `grep -n 未知 html-gen.py` | L509 列属性 / L511 列类型 / L516 选项 / L521 反馈子键 —— 严格限 §E 四项 | ✅ |
| OV-10 | 观感 diff | 旧 `HELP_TABLE`（`0645a29`）vs 新 `help table` | 74 行 → 118 行；`━━━`/两空格缩进/段序**不变**；新增「示例段提示行」「顶层键段」；列属性段改为 `key: 说明 (默认: x)` 逐行式（**见 §2 偏差核实**） | ⚠️ 见下 |
| OV-11 | videos 字段依据 | `layout-table.html` videos 渲染路径 | 模板消费 `title`/`duration`/`platform`/`url`（L566/L619/L658 平台图标映射） | ✅ 属实现 |
| OV-12 | 计数现状 | `grep -n "312 tests" AGENTS.md` | L299 / L326 仍为 312/30 —— **未同步** | ⚠️ 待人工 |

## 2. dev 自报偏差的核实

| dev 自报 | 核实结论 |
|:--|:--|
| ① `AGENTS.md` 写入被守卫拦截 | ✅ 属实。ops 侧同样被拦（"approval prompt timed out… silence is not consent"），且守卫明令不得经 terminal/execute_code 绕过 → **转人工**（§3） |
| ② 契约 `videos` 段含 4 键（设计 §3.1 只写 `{maxShow}`） | ✅ 有据：模板消费 `title`/`duration`/`platform`/`url`（OV-11）。属「视频项固定 schema」而非任意业务字段；若不入契约，R4 ① 断言必红。**判定：合理扩展，需在审计中确认其非白名单兜底** |
| ③ 契约置于 Help System 之前 + `_help_const()` 常量指针 | 属实现细节；不违反零依赖，且 CL013 可拆。**判定：可接受** |
| ④ 键规范段排版重排（密排 → `key: 说明 (默认: x)` + 78 列折行） | ✅ 属实（OV-10）。段序/分隔线/缩进未变，但列属性段从「多键挤一行」改为「一键一行 + 默认值标注」，行数 74→118。**这是本 CL 最需人判的一项**：设计 §B.2 要求「保持现有观感」，dev 主张「只换内容来源的必然重排」。ops 判定：属**非阻断的观感变更**，交审计评分 + 用户裁量 |
| ⑤ warn 不校验 `col.actions[]` / `col.videos` 嵌套项 | ✅ 与设计 §E「四项」一致；docstring 已写明。**判定：符合设计** |
| ⑥ 未做 CL013 范围项 / 未手工同步 `src/` | ✅ 与范围边界一致 |

## 3. 待处置（阻塞本 CL 收口）

**AGENTS.md 测试计数同步**（A8）—— 需人工应用，两处：

```
L299:  - 当前 312 tests（30 文件；
   →   - 当前 326 tests（31 文件，含 test_help_contract 14 + 7 subtests；
       （并在文件清单中 `test_json_output 14 /` 之后插入 `test_help_contract 14 /`）

L326:  ├── tests/                      # Selenium + 回归测试 (312 tests)
   →   ├── tests/                      # Selenium + 回归测试 (326 tests)
```

原因: 本仓 `AGENTS.md` 属受保护 agent-instruction 文件，agent 写入需**交互批准**；
dev oneshot 无用户可批，ops 会话的批准提示亦超时 → 守卫判定「未获同意」，禁止重试或绕道。
应用后请告知，ops 补一笔 `docs@sync` 提交再进 [5/6] 实现审计。

## 4. 复跑指令（含预期）

```bash
cd /Users/jadenli/CodeSpace/html-gen.cli
PYTEST=/opt/homebrew/Caskroom/miniconda/base/envs/py3.12/bin/pytest
$PYTEST tests/test_help_contract.py -q -n 0     # 14 passed, 7 subtests
$PYTEST tests/ -q -n 0                          # 326 passed, 7 subtests
html-gen help table | grep -nE '\binitialHidden\b|\bhide\b'   # L65/L66 语义并列
python3 -c "import importlib.util; s=importlib.util.spec_from_file_location('h','html-gen.py'); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(len(m.render_help('table')))"   # 4634
```
