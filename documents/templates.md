---
title: html-gen 模板三层与 Markdown 规则
topic: html-gen
type: reference
version: 1.0
date: 2026-11-09
author: ops
source: AGENTS.md 外移（HTML-GEN-CL023）
---

# html-gen 模板三层与 Markdown 规则

> 由 `AGENTS.md` 外移（HTML-GEN-CL023）：细则只在本文件维护，`AGENTS.md` 只留指针，两处不重复同一段文本。

## 模板注入机制

- 模板使用 `<!--KEY-->` 占位符，CLI 通过 `inject()` 函数替换
- CSS 在生成时内联：替换 `<link rel="stylesheet" href="style-guide.css">` 为 `<style>...</style>`
- 输出为自包含单文件 HTML，无外部依赖

## 模板类型详解

### layout-doc.html（B 型文档）
- 左侧粘性侧边栏 + 右侧内容区
- 自动生成 TOC（h2/h3），实时高亮当前章节
- TOC 搜索（🔍 按钮，150ms debounce，≥2 字符触发过滤）
- **Bare 模式 / 正文宽度三级 / md 路径行**：URL 状态键与取值口径见 `html-gen help doc` 的「URL 状态」段（默认展示侧边栏/工具栏，URL 参数显式隐藏；宽度窄/中/宽默认 960px 不持久化；md 路径行默认 CSS 隐藏，basename 脱敏）
- 折叠/展开侧边栏（48px 收起态，`[` 快捷键）
- 侧边栏宽度拖拽（200-400px，localStorage 持久化）
- H3 子项开关，中/英双语，🌙/☀️ 主题切换
- 标题点击复制路径（textContent 获取 meta 路径，脱敏文件名）
- 代码复制（剪贴板 + fallback）、行号、Callout 提示框、阅读进度条、图片灯箱

### layout-table.html（A 型表格）
- **键规范**（列类型 6 / 列属性 22 / Tab 6 / 选项 16 / options.feedback 5 / actions 7 / videos 5 / URL 状态 3 / CLI 参数 9）见 `html-gen help table` 的键规范段（单一事实源：`TEMPLATE_CONTRACT['table']`，由 `tests/test_help_contract.py` 双向守卫）
- **页面级段落描述**：`--subtitle` / JSON 顶层 `subtitle`（优先级 CLI > JSON），h1 下方段落区，纯文本安全转义 + `\n` → `<br>`，显式传空串清空；无 subtitle 不渲染
- **Cinema 纪律化宽度模型**：`table-layout:fixed`，每列强制显式 width（默认 120px，actions 100px），无 colgroup，td `max-width:0` 强制截断
- 实时搜索（300ms debounce）+ Cmd+F Spotlight 弹窗搜索
- 多字段排序（Shift+点击二级排序），数字/中文 locale 排序
- 客户端分页（默认 30 条/页，可配置）
- **密度切换**：紧凑(28px) / 标准(34px) / 舒适(42px)，设置面板横向展示
- **五种点击模式**（由选项控制）：
  - 🔗 新标签页：`window.open(url, '_blank', 'noopener,noreferrer')`
  - 📋 弹出面板：居中 overlay，键值列表（textContent 安全渲染）；支持自定义渲染器（`options.modalRenderer: 'skills'`）
  - 📑 分栏预览：表格 + 预览并排，拖拽分栏线，比例预设 (▦)，▲▼ 导航；支持 SKILL.md 加载
  - 📂 行内展开：手风琴模式，点击展开详情网格
  - 🎯 单元格点击：`col.onCellClick: 'split'` 直接打开分栏
- **快速过滤**：点击单元格值 → 筛选该列该值的行，filter pill 可关闭；列属性启用（默认关，键名见 help）
- **列冻结**：sticky 列，动态计算 left 偏移（基于该列 width 配置）
- **右侧固定列**：水平滚动时保持在视口右侧
- **分栏详情跨列与空值**（CL025）：列属性 `splitSpan` = `"full"`（整行，旧 `splitFull` 等价）或正整数 N（`grid-column:span N`，上限 6）；选项 `hideEmptyCells: true` 时空值字段整格不渲染、剩余格自动重排（缺省 false 保持全列，向后兼容）。
- **分栏模式列过滤**：标记为「分栏可见」的列显示于分栏表格；可用选项显式指定分栏列集
- **列隐藏双语义**：「永不可见」vs「默认收起·可开启·分栏仍全列」—— 语义与键名对照见 `html-gen help table`
- **快捷键**：↑↓ 键盘导航行，Enter 点击，F 全屏
- **批量操作**：选中行出现工具栏（全选/取消/导出 CSV）
- **URL 状态分享**（CL004/CL005）：`?tab&q&split` 参数 replaceState 同步 + 加载恢复（tab 白名单 / split 越界忽略 / q 仅 input.value）；tabs 行居右按钮区 `.tabs-actions`：↗ 拷贝分享链接（clipboard + execCommand fallback）+ 🏠 home 入口（`--home-url` 注入, 与 share 同容器 36px 圆角深底）；排序/quickFilter 变化自动 closeSplit
- **视图预设**：保存/加载/删除设置（密度/模式/排序/列可见性，最多 10 个，≤2KB）
- 列名从 JSON 首条 key 自动推导
- 支持单元格 HTML（`<a>`、`<code>` 等）
- 支持操作按钮列（复制字段值 / 打开链接 / 描述兜底 / 自定义 handler 四种模式）、多标签页、CSV 导出
- `handler` 模式：自定义 JS 函数名，由模板 `window.{handler}(event, row)` 调用
- 列可见性 / 列宽度 localStorage 持久化（`html-gen:table:col-visibility` / `html-gen:table:col-widths`），拖拽 resize 直接操作 DOM
- 列宽拖拽可禁用（选项关闭）
- 设置面板：⚙️ 下拉，密度/点击模式/列可见性/视图预设，内部点击不关闭，✕ 关闭按钮
- `printColWidths()` 控制台调试函数
- 安全：`copyAction()` 含 execCommand fallback（headless Chrome 兼容）
- **Videos 视频列**：行字段为对象数组 `[{url,title,duration,platform}]`，每视频一个 pill（图标+标题+时长）；`col.videos.maxShow` 折叠 "+N" 点击展开（不折叠回，re-render 重置）；平台图标映射 douyin/抖音🎵 bilibili/B站/b站📺 youtube▶️ 其他📹；pill 点击新标签页（noopener,noreferrer）；默认搜索排除 videos；split/expand 数组特判渲染

### layout-knowledge.html（C 型知识库）
- **键规范**（item 8 / groups 3 / 数据源与输出目标 / CLI 参数 10）见 `html-gen help knowledge` 的键规范段（单一事实源：`TEMPLATE_CONTRACT['knowledge']`）
- 顶部横向标签栏（按 group 分组），与侧边栏标题行对齐
- 左侧章节列表（按 section 分组，badge 标记显式）
- 侧边栏搜索（🔍 按钮，150ms debounce，≥2 字符过滤，无匹配 section 自动隐藏）
- **嵌入降级**：条目带 `url` 时以 iframe 加载详情页，并在该 URL 追加 `sidebar=0&toolbar=0` 使其进入 Bare 模式（知识库页自身无 sidebar/toolbar URL 状态；键口径见 `html-gen help doc` 的「URL 状态」段）
- 折叠/展开侧边栏（48px 收起态，`[` 快捷键）
- 双内容模式：条目带详情页地址 → iframe 加载；带正文 HTML → 内联渲染（键名见 `html-gen help knowledge`）
- section 标题可点击：单条目 section 点击标题直接加载 (K2)
- 空状态显示欢迎面板
- 上次选择状态 localStorage 恢复（group + item）

## Markdown → HTML 转换规则

`md_to_html()` 在 `html-gen.py` 中实现，零依赖纯 Python：
- h1–h6 标题（自动加 id 锚点，h4-h6 不入 TOC）
- `**加粗**`、`*斜体*`、`==高亮==`（→ `<mark class="hl">`）、`` `代码` ``、`[链接](url)`
- 围栏代码块（支持变长 fence 嵌套）
- 表格（Markdown pipe table）
- 无序/有序列表（连续自动合并为 `<ul>`）
- Callout：`> **Note/Warning/Tip/Danger/注意/警告/提示/危险**：内容`
- 分隔线 `---`、引用 `> 文字`
- 不解析图片（安全限制）
