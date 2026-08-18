# layout-doc 嵌入降级：侧边栏/工具栏默认隐藏 + URL 入参控制 — 设计文档

## 版本

v1.0 (2026-08-06)

## 背景与问题来源

drama-knowledge.html（C 型知识库）通过 iframe 加载 B 型文档页（history-overview.html 等）时，外层 knowledge 与内层 doc 各有一套"左侧边栏 + 右上语言/主题切换"，视觉重复且互不同步。用户确认：**layout-doc 默认不展示侧边栏与语言/主题切换，通过两个 URL 入参控制展示；layout-knowledge 嵌入时不传参，保持隐藏。**

## 目标形态

| 访问方式 | URL | 侧边栏 | 语言/主题切换 |
|:--|:--|:--:|:--:|
| 知识库嵌入（默认） | `history-overview.html` | 隐藏 | 隐藏 |
| 独立完整浏览 | `page.html?sidebar=1&toolbar=1` | 展示 | 展示 |
| 仅侧边栏 | `page.html?sidebar=1` | 展示 | 隐藏 |
| 仅工具栏 | `page.html?toolbar=1` | 隐藏 | 展示 |

## 设计决策 (D)

### D1 — 入参字段设计（待确认）

| 字段 | 取值 | 语义 |
|:--|:--|:--|
| `sidebar` | `1` | 展示左侧边栏（TOC/折叠/拖拽）；缺省或非 1 = 隐藏 |
| `toolbar` | `1` | 展示右上语言/主题切换；缺省或非 1 = 隐藏 |

- 组合示例：独立完整浏览 `?sidebar=1&toolbar=1`
- 备选命名：`side`/`topbar`（更短）；默认采用 `sidebar`/`toolbar`（语义自明）
- 与其他 URL 参数（`?t=` 时间戳等）正交，`URLSearchParams` 解析互不影响

### D2 — layout-doc 默认隐藏实现

**改动文件**：`layout-doc.html`

1. **CSS 默认隐藏**（无 JS 也生效）：
   ```css
   .doc-wrapper .doc-sidebar { display: none; }
   .top-toolbar { display: none; }
   body.doc-full .doc-wrapper .doc-sidebar { display: flex; }
   body.doc-full .top-toolbar { display: flex; }
   ```
2. **JS 读取入参**（init 最前）：
   ```js
   var params = new URLSearchParams(location.search);
   if (params.get('sidebar') === '1' || params.get('toolbar') === '1') {
     document.body.classList.add('doc-full');
   }
   // 单独控制：若仅 sidebar=1，工具栏仍隐藏（doc-full 后按参数细化 class）
   if (params.get('sidebar') !== '1') document.body.classList.add('no-sidebar');
   if (params.get('toolbar') !== '1') document.body.classList.add('no-toolbar');
   ```
   简化：body 默认无 class → 隐藏；任一参数命中 → 加 `doc-full`；再按参数移除对应 `no-*`。
   具体实现以 dev 阶段简化为主，目标：参数驱动，默认全隐藏。
3. **行为不变项**：localStorage（doc_lang/theme/collapsed）、TOC 生成、搜索、进度条等逻辑不动；仅显示层控制。

### D3 — layout-knowledge 调用不变

- knowledge 的 item `url` 保持不带参（`drama/history-overview.html`）→ iframe 加载默认隐藏侧边栏/工具栏 ✓
- 无需改 layout-knowledge.html；内层 doc 由 URL 参数自行决定

### D4 — 重新生成 doc 模板产物（20+ 页）

layout-doc 改动后，现有 doc 生成物需重新生成才应用新默认（生成物内嵌模板 JS/CSS）。清单（含 doc-wrapper 特征的全部）：
- `demos/drama/`：daming-overview、daming-strategy-01~06、daming-timeline-01~07、history-overview（15）
- `demos/` 根：chaitin-menu-design-v1.0-20260707、ci-issues-demo、html-gen-usage-guide-v1.0-20260707、template-A-guide-v1.0-20260707、template-B-guide-v1.0-20260707（5+）
- 其他 doc 页（如有遗漏，grep `doc-wrapper` 补全）
- 重新生成命令沿用各页原 md 源（drama 用 `html-gen doc -i <md> -o <html> --title ...`；根目录 guide 页用对应源）
- **注**：重新生成后这些页面独立访问默认无侧边栏/工具栏——用户已确认此默认

### D5 — 测试规划

- `tests/test_doc_sidebar.py`：现有用例（theme/lang/collapse/TOC 搜索）加载 URL 改为 `?sidebar=1&toolbar=1`（setUp 拼接），断言不变
- 新增 `tests/test_doc_bare.py`（或并入 test_doc_sidebar）：
  - 无参加载：`#sidebar`、`#topToolbar` 不可见（display none）
  - `?sidebar=1`：sidebar 可见、toolbar 隐藏
  - `?toolbar=1`：toolbar 可见、sidebar 隐藏
  - `?sidebar=1&toolbar=1`：两者可见
- knowledge 嵌入断言（test_drama_knowledge.py 增补）：iframe 加载的 doc 页内 `#sidebar`/`#topToolbar` 不可见（iframe 内 DOM 需 switch_to.frame 或 JS 检查）
- 全量回归：现有 103 + 新增，无破坏

### D6 — 文档同步

- `AGENTS.md`：layout-doc 特性描述补"默认隐藏侧边栏/工具栏，`?sidebar=1&toolbar=1` 展示；知识库嵌入自动降级"
- `skills/html-gen/SKILL.md`（总览）：doc 命令说明补入参
- `features.md`：doc 相关条目补默认行为

## 改动文件清单

| 文件 | 改动 |
|:--|:--|
| layout-doc.html | D2 默认隐藏 CSS + 入参 JS |
| demos/drama/*.html（15） | D4 重新生成 |
| demos/ 根 doc 页（5+） | D4 重新生成 |
| tests/test_doc_sidebar.py | D5 加载 URL 带参 |
| tests/test_doc_bare.py（新增） | D5 入参行为用例 |
| tests/test_drama_knowledge.py | D5 嵌入降级断言 |
| AGENTS.md / skills/html-gen/SKILL.md / features.md | D6 同步 |

## 风险与兼容

- **默认行为变更**：doc 独立访问默认无侧边栏/工具栏（用户已确认）；需重新生成全部 doc 产物才生效
- **旧生成物过渡**：未重新生成的旧 doc 页仍显示完整 UI（模板未改前的产物）——重新生成后统一
- **测试适配**：test_doc_sidebar 全部用例改为带参加载（属预期适配）
- **知识库嵌入降级**：drama/chaitin 等 knowledge 的 doc 内容页自动受益（iframe 无参）

## 待办清单（dev 阶段）

- [ ] D2 layout-doc.html 默认隐藏 CSS + 入参 JS
- [ ] D4 重新生成 doc 产物（drama 15 + 根 5+）
- [ ] D5 test_doc_sidebar 适配 + test_doc_bare 新增 + knowledge 嵌入断言
- [ ] D6 文档同步（AGENTS.md / SKILL.md / features.md）
- [ ] 全量回归 + git commit（不 push）
