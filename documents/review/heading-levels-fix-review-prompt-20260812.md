────────────────────────────────────────
Review prompt — html-gen h4-h6 标题渲染支持
────────────────────────────────────────

对 html-gen 项目 ~/CodeSpace/html-gen 审查 h4-h6 标题渲染修正方案。

聚焦:
- documents/heading-levels-fix-design-v1.0-20260812.md (commit 19ee648)

背景:
- cult-analysis-report-v2.1-20260812.html 中 `#### 6.1.5 关键寓意`、`##### 剧情 ↔ 历史对位表`
  等 13 处标题未渲染为 HTML 标题, 泄漏为 `<p>#### xxx</p>`
- 根因: html-gen.py::md_to_html() L88-93 仅识别 #/##/###, h4-h6 落入 else 分支
- 次因: 生成 prompt 使用了 h4/h5 超出语法子集
- 决策: 1C 模板加渲染 + prompt 约束; h4-h6 不进 TOC; 带锚点与独立样式

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
检查项
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

H1 · 方案完整性
  □ 问题根因分析准确 (md_to_html 只支持 h1-h3)
  □ 影响范围覆盖: html-gen.py / layout-doc.html / layout-slide.html / tests / 文档
  □ 修复方案明确可执行 (代码片段/样式/测试用例)

H2 · 模板实现正确性
  □ md_to_html 匹配顺序: ###### → ##### → #### → ### → ## → # (从长到短)
  □ 现有 startswith('# ') 规则不会误吞 '#### ' (第2字符是#非空格, 已安全; 从长到短排列更稳)
  □ slug 锚点: h4-h6 同样生成 id
  □ 零依赖原则: 仅 Python 标准库

H3 · 样式一致性
  □ layout-doc.html h4/h5/h6 字号递减 (0.95/0.88/0.82rem), 颜色递减
  □ light 主题对应样式
  □ 锚点 hover 扩展 (h4:hover .anchor-link)
  □ layout-slide.html 同步合理性

H4 · TOC 决策
  □ TOC 保持 h2/h3 (querySelectorAll('h2, h3') 不动) — 合理
  □ 无 h4 时 TOC 行为不变

H5 · 测试设计
  □ 回归: md_to_html 输出 <h4>/<h5>/<h6>, 无 <p>#### 泄漏
  □ Selenium: doc 模板 h4/h5 渲染 + 0 JS errors + TOC 不含 h4
  □ 测试命名/位置符合项目约定 (tests/test_*.py, unittest.TestCase)

H6 · 文档同步
  □ AGENTS.md 标题规则 h1-h3 → h1-h6
  □ features.md 相关条目
  □ 生成 prompt 约束 (优先 h1-h3, h4-h6 仅小节编号, 禁 h7+)

H7 · 风险
  □ h7+ 泄漏边界说明 (prompt 约束覆盖)
  □ 纯增量, 不影响现有 h1-h3 路径

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
产出
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 按治理规范逐项审查 (实现方案与项目约定一致性)
2. 报告审查结果 (PASS / CONDITIONAL PASS / REJECT + 评分)
3. 若 PASS → 提示切 dev role 实现
