# html-gen index 落地页优化 — review 报告 v1.0

- 日期: 2026-08-25
- Reviewer: Security Reviewer
- 级别: L2（commit-range-audit）
- 范围: 3 commits（2c299ce feat@index / 8260291 test@index / aa5bf38 docs@skills），位于已 PASS 的 46e072e 之后
- 决策依据: http-server.cli 落地页反馈建议（html-gen-optimize-suggestions-20260825.md），决策 1A 采纳行内复制 / 2自定义 对比卡转置 / 3A badges / 4A footer favicon / 5A 品牌圆标 / 6A hero 减留白 + −55px
- 结论: ✅ **PASS 95/100（A）** — 1 🟡 + 2 🟢，无 🔴

---

## 一、数据验证

| 项 | 结果 |
|:---|:---|
| 全量测试 | `python3 -m pytest tests/ -q -n 4` → **183 passed in 35.85s**（20 文件，基线 180 + 新增 test_16/17/18，无回归） |
| prompt 输出 | `python3 html-gen.py prompt pages-index --brief` → exit 0，description + 10 章节（含新增「Footer favicon 图标化」） |
| favicon 外链 | `www.jaden.tech/static/img/favicon.png?=20260705` / `github.com/favicon.ico` / `gitee.com/favicon.ico` → 全部 **200** |
| 对比卡溢出 | 5 个视口（1400/1280/1100/760/390px）实测 `scrollWidth == clientWidth`，表 460px 在 500px 卡内 / 404px 在 444px 卡内（390 移动端），**0 横向溢出、0 截断**；`td:first-child nowrap` 生效 |
| hero 动态两屏 | 1400×900 下 hero 764px ≥ vh−55=702 ✓；760/390 宽下内容撑高（1101/1140px），min-height 语义正确 |
| hero-logo | 实载成功（naturalWidth 344，complete=true），`alt=""` 装饰性 OK |
| JS 错误 | 全视口 0 SEVERE/ERROR（`window.__testErrors` 机制 + 手工驱动均验证） |
| 双源同步 | demos/index.html 同步 footer favicon（+5/−2）；`test_05_dual_source_consistency` 12 项特征双源齐全 |
| 提交格式 | 3/3 `type@scope: subject`（feat@index / test@index / docs@skills） |
| git 状态 | clean；main 领先 github/main 恰好 3 = 评审范围 |

## 二、维度评估

### 功能正确性

- ✅ hero badges 4 项（⚡ 零依赖 · 🌙 深色主题 · 🇨🇳 中文优先 · 📦 单文件输出）落位，测试断言 4 项齐全
- ✅ 安装&快速开始合并：block-title「📋 复制全部」data-copy 用 `&#10;`/`&quot;` 正确转义，live DOM 实测 6 行命令完整（含换行与引号）
- ❌ **PATH 行内复制按钮引号未转义**（见 HG-SEC-038）：live DOM 实测 `data-copy` 截断为 `export PATH=`
- ✅ 对比卡转置表 6 维度 × 4 工具，html-gen 列 6 ✓ 全高亮（th.hl + td.win），行内样式紧凑可读
- ✅ footer favicon 14px + 文本，双源同步；hero padding 120→70 与 `innerHeight − 55` 三处一致（index.html / AGENTS.md / SKILL.md）

### 双源同步

- 根 index.html 与 demos/index.html 独立副本策略（1C 决策）下：hero 相关改动不适用于 demos 页（无 hero），共享元素 footer favicon 已同步 ✓
- 防漂移测试 12 项特征双源一致，无漂移

### 文档一致性

- SKILL.md 骨架新增 badges / 对比卡 / 行内复制 / favicon 四节，与实现 6/6 落位（逐项核对行号）
- AGENTS.md 双源段 hero 高度 −110→−55 同步 ✓
- 🟢 记录：SKILL.md badge 示例列 3 项（略 中文优先），实现 4 项，文本写「3-4」可涵盖，非漂移

## 三、安全事项

无 🔴。无注入面（页面无用户输入/无后端）、无凭证、无外部脚本依赖（仅 3 个 favicon <img>，非可执行资源，无需 SRI）。外链 `rel="noopener"` 双源齐全。

| ID | Severity | 问题 | 位置 | 状态 |
|:---|:---:|:---|:---|:---:|
| HG-SEC-038 | 🟡 | PATH 行内复制按钮 `data-copy` 内引号未转义，live DOM 截断为 `export PATH=` | index.html:289 | ✅ 已修复（93993cb） |
| HG-SEC-039 | 🟢 | test_10 仅断言 data-copy 非空，未覆盖值完整性（本次截断缺陷未被测试暴露） | tests/test_index_landing.py | ✅ 已同步（test_10 精确值断言） |
| HG-SEC-040 | 🟢 | SKILL.md badge 示例 3 项 vs 实现 4 项（「3-4」范围可涵盖） | skills/pages-index/SKILL.md | ✅ 已同步（badge 4 项一致） |

### HG-SEC-038 详情

- 原始 HTML：`data-copy="export PATH="$HOME/.local/bin:$PATH""` — 内层 `"` 未转义为 `&quot;`，HTML 解析器在首个 `"` 后截断属性值
- 实测：`button.getAttribute('data-copy')` 返回 `export PATH=`；点击复制得到无效命令
- 影响：6 个行内复制按钮中 1 个失效（其余 5 个正确转义）；「复制全部」按钮数据完整，可作 workaround；不影响页面其余功能
- 修复（1 行）：`data-copy="export PATH=&quot;$HOME/.local/bin:$PATH&quot;"`，并建议 test_10 增加精确值断言（HG-SEC-039）
- ✅ **复查 2026-08-25（93993cb）已修复**：index.html:289 现为 `data-copy="export PATH=&quot;$HOME/.local/bin:$PATH&quot;"`；live DOM 断言 `getAttribute('data-copy')` == `export PATH="$HOME/.local/bin:$PATH"`（test_10 精确值）；「复制全部」含安装 + slide 命令断言齐全；全页 11 处 data-copy 无未转义内引号（正则扫描 0 命中）；SKILL.md badge 示例 4 项与实现一致；全量 183 passed

## 四、评分

```
Base: 100
🟡 HG-SEC-038 × -5  →  95（原始审计）
复查 93993cb 后 🟡 关闭 → 100
Rating: A（≥85）→ PASS
```

## 五、结论

✅ **PASS 95/100（A）** — 3 commits 实现完整、测试 183 全绿、双源一致、无安全风险。唯一 🟡 为 PATH 行内复制截断（功能缺陷非安全），建议下次迭代优先修复（1 行 + 补测试断言）。按 1A 协议授权 push 至 github/main。

### 复查记录（2026-08-25 二次）

- 修复 commit: `93993cb fix@index: HG-SEC-038 PATH copy data-copy quote escape + exact value test + skill badge sync`（3 文件，+11/−3）
- HG-SEC-038 ✅ 关闭：index.html:289 `&quot;` 转义完整，live DOM 精确值断言通过（截断不再发生）
- HG-SEC-039 ✅ 关闭：test_10 新增 PATH 精确值断言 + 复制全部含安装/slide 命令断言
- HG-SEC-040 ✅ 关闭：SKILL.md badge 示例 ⚡/🌙/🇨🇳/📦 4 项与实现一致
- 全量验证：`python3 -m pytest tests/ -q -n 4` → **183 passed in 35.44s**
- 复查结论：✅ **PASS 100/100（A）** — 0 剩余问题
