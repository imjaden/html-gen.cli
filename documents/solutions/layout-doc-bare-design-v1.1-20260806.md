# layout-doc 嵌入降级：侧边栏/工具栏默认隐藏 + URL 入参控制 — 设计文档

## 版本

v1.1 (2026-08-06) — 修正 review 意见（N1 三 class 改为双 class；N2 产物清单补全 22；N3 ?t= 表述；N4 测试数；N5 collapsed 交互）

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

### D1 — 入参字段设计

| 字段 | 取值 | 语义 |
|:--|:--|:--|
| `sidebar` | `1` | 展示左侧边栏（TOC/折叠/拖拽）；缺省或非 1 = 隐藏 |
| `toolbar` | `1` | 展示右上语言/主题切换；缺省或非 1 = 隐藏 |

- 组合示例：独立完整浏览 `?sidebar=1&toolbar=1`
- 与 `?t=` 时间戳等 URL 参数正交（`URLSearchParams` 解析互不影响）

### D2 — layout-doc 默认隐藏实现（v1.1 修正 N1/N5）

**改动文件**：`layout-doc.html`

1. **CSS 默认隐藏 + 双 class 驱动**（两个独立 class，一一对应参数）：
   ```css
   .doc-sidebar { display: none; }          /* 默认隐藏 */
   .top-toolbar { display: none; }          /* 默认隐藏 */
   body.show-sidebar .doc-sidebar { display: flex; }
   body.show-toolbar .top-toolbar { display: flex; }
   ```
   - 无 `no-*` 死 class；CSS 与 JS 一一对应
   - `show-sidebar` 只控制 `display`，**不触碰 collapsed 折叠/宽度逻辑**（N5）：侧边栏显式展示时仍可折叠（48px 收起态）、拖拽宽度照常；隐藏态下相关交互不可见

2. **JS 读取入参**（init 最前）：
   ```js
   var params = new URLSearchParams(location.search);
   if (params.get('sidebar') === '1') document.body.classList.add('show-sidebar');
   if (params.get('toolbar') === '1') document.body.classList.add('show-toolbar');
   ```

3. **行为不变项**：localStorage（doc_lang/theme/collapsed）、TOC 生成、搜索、进度条、灯箱等逻辑不动；仅显示层控制。

### D3 — layout-knowledge 调用不变（v1.1 修正 N3 表述）

- knowledge 的 item `url` 不带 sidebar/toolbar 参数（如 `drama/history-overview.html`）→ iframe 加载默认隐藏 ✓
- **事实修正**：knowledge 模板实际加载时 `frame.src = item.url + '?t=' + Date.now()`（时间戳防缓存）——`?t=` 与 sidebar/toolbar 参数正交，不影响默认隐藏；测试断言 iframe src 时注意去掉 `?t=` 再比对
- 无需改 layout-knowledge.html

### D4 — 重新生成 doc 模板产物（22 个，v1.1 补全 N2）

layout-doc 改动后，现有 doc 生成物需重新生成才应用新默认。完整清单（grep `doc-wrapper` 实测 22 个）：

**demos/drama/（15）**：
- daming-overview.html
- daming-strategy-01.html ~ daming-strategy-06.html（6）
- daming-timeline-01.html ~ daming-timeline-07.html（7）
- history-overview.html

**demos/ 根（7）**：
- chaitin-menu-design-v1.0-20260707.html
- ci-issues-demo.html
- html-gen-usage-guide-v1.0-20260707.html
- template-A-guide-v1.0-20260707.html
- template-B-guide-v1.0-20260707.html
- template-B-markdown-spec-v1.0-20260707.html
- template-C-guide-v1.0-20260707.html

- 重新生成命令沿用各页原 md 源（drama 用 `html-gen doc -i <md> -o <html> --title ...`；根目录 guide 页用对应源，title 以现有生成物为准）
- **注**：重新生成后这些页面独立访问默认无侧边栏/工具栏——用户已确认此默认

### D5 — 测试规划（v1.1 修正 N4 计数）

- `tests/test_doc_sidebar.py`：现有用例加载 URL 改为 `?sidebar=1&toolbar=1`（setUp 拼接），断言不变
- 新增 `tests/test_doc_bare.py`：
  - 无参加载：`#sidebar`、`#topToolbar` 不可见（display none）
  - `?sidebar=1`：sidebar 可见、toolbar 隐藏
  - `?toolbar=1`：toolbar 可见、sidebar 隐藏
  - `?sidebar=1&toolbar=1`：两者可见
  - `?sidebar=1` 下侧边栏仍可折叠（collapsed 态不受 show-sidebar 影响，N5）
- knowledge 嵌入断言（test_drama_knowledge.py 增补）：iframe 加载的 doc 页内 `#sidebar`/`#topToolbar` 不可见（iframe 内 DOM 用 driver.switch_to.frame 或 JS 检查；src 比对注意去 `?t=`）
- 全量回归：当前 103 tests（实测 `--collect-only`，2026-08-06），实施后 103 + 新增，无破坏

### D6 — 文档同步

- `AGENTS.md`：layout-doc 特性描述补"默认隐藏侧边栏/工具栏，`?sidebar=1&toolbar=1` 展示；知识库嵌入自动降级"
- `skills/html-gen/SKILL.md`（总览）：doc 命令说明补入参
- `features.md`：doc 相关条目补默认行为

## 改动文件清单

| 文件 | 改动 |
|:--|:--|
| layout-doc.html | D2 默认隐藏 CSS + 双 class 入参 JS |
| demos/drama/*.html（15） | D4 重新生成 |
| demos/ 根 doc 页（7） | D4 重新生成 |
| tests/test_doc_sidebar.py | D5 加载 URL 带参 |
| tests/test_doc_bare.py（新增） | D5 入参行为用例 |
| tests/test_drama_knowledge.py | D5 嵌入降级断言 |
| AGENTS.md / skills/html-gen/SKILL.md / features.md | D6 同步 |

## 风险与兼容

- **默认行为变更**：doc 独立访问默认无侧边栏/工具栏（用户已确认）；需重新生成全部 22 个 doc 产物才生效
- **旧生成物过渡**：未重新生成的旧 doc 页仍显示完整 UI——重新生成后统一
- **测试适配**：test_doc_sidebar 全部用例改为带参加载（属预期适配）
- **知识库嵌入降级**：drama/chaitin 等 knowledge 的 doc 内容页自动受益（iframe 无参 + ?t= 正交）

## 待办清单（dev 阶段）

- [ ] D2 layout-doc.html 默认隐藏 CSS + show-sidebar/show-toolbar 入参 JS
- [ ] D4 重新生成 doc 产物 22 个（drama 15 + 根 7）
- [ ] D5 test_doc_sidebar 适配 + test_doc_bare 新增 + knowledge 嵌入断言
- [ ] D6 文档同步（AGENTS.md / SKILL.md / features.md）
- [ ] 全量回归（103 + 新增）+ git commit（不 push）
