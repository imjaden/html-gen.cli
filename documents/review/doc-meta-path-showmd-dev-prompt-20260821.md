────────────────────────────────────────
Dev 实施 prompt — html-gen doc meta 显示 md 路径（show-md）
────────────────────────────────────────

按设计文档实现 doc meta 显示 md 源文件路径功能。工作目录 ~/CodeSpace/html-gen。

聚焦:
- documents/doc-meta-path-showmd-design-v1.0-20260819.md (commit 3f456d3 + 5927f97 确认 + 5f346a6 M4-1 修订)
- documents/review/doc-meta-path-showmd-review-v1.0-20260819.md (REJECT/85, M4-1 追踪; 设计已采纳修复)

设计要点:
- meta 区增加路径行: `路径: <code>{basename}</code>`（脱敏，仅文件名）
- 默认 CSS 隐藏 (.meta-path display:none)，?show-md=1 显示 (body.show-md)
- 与现有 width/sidebar/toolbar 同机制 (URLSearchParams → body class → CSS)
- M4-1: L311 复制闸门正则扩展允许纯文件名
- slide: 生成端统一输出路径行，不做运行时显隐

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
实现清单
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

I1 · html-gen.py :: cmd_doc（L241-250 meta 组装）
  □ 保留 rel 计算（已存在）
  □ meta 字符串追加路径行（脱敏 basename）:
    import os（若未引入）
    md_name = os.path.basename(str(md))
    meta = (f"创建: {ct} · 编辑: {et}<br>"
            f"字数: {wc:,} · 阅读约 {rt} 分钟"
            f"<span class=\"meta-path\"> · 路径: <code>{md_name}</code></span>")

I2 · html-gen.py :: cmd_slide（L300-309 meta 组装）
  □ 同样追加 span.meta-path 路径行（脱敏 basename）

I3 · layout-doc.html CSS（L80 后追加）
  □ .meta-path { display: none; }
  □ body.show-md .meta-path { display: inline; }

I4 · layout-doc.html JS（L269 width 处理后追加）
  □ // md 路径: ?show-md=1 显示 (默认隐藏, 隐私)
    if (params.get('show-md') === '1') document.body.classList.add('show-md');

I5 · layout-doc.html JS L311 闸门正则扩展（M4-1 关键）
  □ 原: if (/^(https?:|\/|~\/)/.test(target)) {
  □ 新: if (/^(https?:|\/|~\/|[\w.\- ]+$)/.test(target)) {
  □ 允许: URL / 绝对路径 / ~/ 路径 / 纯文件名（脱敏后 history-overview.md）

I6 · 测试（并入 tests/test_templates.py）
  □ test_doc_meta_has_path: 生成 doc 的 meta 含 路径: 且为文件名（不含 /）
  □ test_doc_meta_path_hidden_by_default: 无 show-md 时 .meta-path display:none
  □ test_slide_meta_has_path: slide meta 含脱敏路径
  □ Selenium test_doc_show_md_param: ?show-md=1 → .meta-path display:inline
  □ Selenium test_doc_title_click_copy_path: 点击侧边栏标题复制内容 = 文件名（M4-1 验证）
  □ 0 JS errors

I7 · 重新生成产物
  □ demos/ 下 B 型文档重新生成（history-overview.html 等，meta 含路径行）
  □ slide demo 重新生成
  □ 注意: 重新生成后 diff 应仅 meta 区变化 + show-md 相关（模板内联样式更新）

I8 · 文档同步
  □ features.md: B 型 URL 入参节补 show-md 参数说明
  □ AGENTS.md: B 型功能清单补充（若项目惯例维护）

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
验证
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 手动验证:
   - 含 h4/h5 的 md → html-gen doc → meta 含 路径: 文件名
   - 打开生成的 html: 默认不显示路径; ?show-md=1 显示
   - 点击侧边栏标题: toast 显示"已复制: 文件名"
2. 全量测试:
   - python3 -m pytest tests/test_templates.py -q（新增测试通过）
   - python3 -m pytest tests/ -q -n 4（全量 141+ 通过，无回归）
3. 检查: 生成的 html 中无完整路径泄露（仅文件名）

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
收尾
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

- git commit: feat@html-gen: doc meta show-md path (脱敏文件名 + URL 入参 + M4-1 正则)
  （subject 英文；如拆多 commit 用 docs@html-gen 标文档同步部分）
- 不 push（非 review profile）
- 完成后回报: 改动文件清单 + 测试结果 + 生成页面示例链接

约束:
- 零依赖: 仅 Python 标准库（os.basename）
- 只改清单内文件，不做无关重构
- 中文注释与界面消息
