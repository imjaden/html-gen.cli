────────────────────────────────────────
验证 prompt — html-gen h4-h6 标题渲染支持
────────────────────────────────────────

对 html-gen 项目 ~/CodeSpace/html-gen 验证 h4-h6 标题渲染支持实现。

聚焦:
- documents/heading-levels-fix-design-v1.0-20260812.md (设计方案, 含 c33005f 复检修订)
- documents/review/heading-levels-fix-review-v1.0-20260812.md (审计报告, PASS)
- 本 session commit: a02897b (dev 实现)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
检查项
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

D1 · md_to_html h4-h6 分支 (html-gen.py L88-93)
  □ 顺序从长到短: ###### → ##### → #### → ### → ## → #
  □ h6: line[7:], h5: line[6:], h4: line[5:] 切片正确
  □ 每个标题加 id="{slug(...)}" 锚点
  □ 不误吞: `# ` 后接空格不会吞 `#### `

D2 · layout-doc.html CSS
  □ .doc-body h4/h5/h6 字号梯度 (0.95/0.88/0.82rem)
  □ 颜色梯度 (#c0c0c0/#b0b0b0/#a0a0a0)
  □ light 主题: h4/h5/h6 颜色覆盖 (#444/#555/#666)
  □ anchor hover 扩展: h4/h5/h6:hover .anchor-link opacity:1

D3 · layout-doc.html JS anchor 循环
  □ 新增独立循环 (h4/h5/h6), 原 h2/h3 循环不动
  □ 用索引生成 id (勿用 textContent 空格非法 id)
  □ anchor-link 子元素: class='anchor-link', href='#id', '¶'
  □ 不加入 TOC: TOC 循环保持 querySelectorAll('h2, h3')

D4 · layout-slide.html
  □ slide 无 h4+ 使用场景, 默认样式渲染不泄漏
  □ md_to_html 共享, 无需 CSS 改动

D5 · 测试 test_heading_levels.py (6 tests)
  □ test_md_to_html_h4_h5_h6: 输出含 <h4 id>/<h5 id>/<h6 id>
  □ test_md_to_html_no_leak: #### 不产生 <p>####
  □ test_slug_anchor: h4 id 与 slug() 一致
  □ test_doc_h4_h5_render: h4/h5/h6 textContent 正确 + 0 JS errors
  □ test_doc_toc_excludes_h4: TOC 不含 h4
  □ test_doc_h4_anchor_link: h4 含 .anchor-link 子元素

D6 · 文档同步
  □ AGENTS.md: h1–h3 → h1–h6 (h4-h6 不入 TOC)
  □ features.md: doc 模板标题渲染条目更新

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
手动验证
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  含 h4/h5 的 md → html-gen doc → 检查:
  - 无 <p>#### 泄漏
  - h4/h5/h6 有锚点
  - TOC 仍只含 h2/h3

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
产出
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 按治理规范逐项验证（实现是否与设计一致）
2. 报告验证结果（功能/测试/质量）
3. 若 PASS → 提示切 review role 做最终审计

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
关键路径
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  html-gen.py:L88-93         md_to_html h4-h6 分支
  layout-doc.html:L80-82     h4/h5/h6 CSS (dark)
  layout-doc.html:L157-160   h4/h5/h6 CSS (light)
  layout-doc.html:L110       anchor hover 扩展
  layout-doc.html:L393-402   h4-h6 anchor 循环
  tests/test_heading_levels.py  6 tests

  全量: pytest tests/ -q → 100 passed
────────────────────────────────────────
