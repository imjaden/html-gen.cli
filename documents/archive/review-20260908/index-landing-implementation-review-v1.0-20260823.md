# index-landing 实现审计 — review报告 v1.0

## 审计概况

- **审计类型**: Implementation Audit (L2)
- **审计对象**: 未 push commits（github/main..HEAD；用户 prompt 记为 7 个，实测 **6 个**）
  1. `87834ef` docs@html-gen: index landing design v1.0 — root index.html + hero + README slim (review 输入)
  2. `c4340b7` review@html-gen: index landing design review — PASS (95/A, HG-SEC-007 open)
  3. `543c9bf` docs@html-gen: index landing design v1.1 — 补全 17 处路径迁移清单 (HG-SEC-007)
  4. `47a3a84` feat@html-gen: root index landing page (hero 100vh + 4 template grid)
  5. `2472152` docs@html-gen: README slim — point to site index
  6. `87d678f` fix@html-gen: hero 100vh 失效 — CSS 注释内 --surface-*/ 提前闭合吞掉 .hero 规则 (ops 核查)
- **设计文档**: `documents/index-landing-design-v1.0-20260822.md` (v1.1，2026-08-22)
- **前置设计评审**: PASS 95/A（2026-08-23，`documents/review/index-landing-design-review-v1.0-20260823.md`），HG-SEC-007 open → 543c9bf 关闭
- **审计方法**: 设计 §1/§2/§3 逐条映射实现 + ops 核查证据复核 + 独立复跑（链接检查 / headless Chrome / 全量 pytest）
- **审计日期**: 2026-08-23

## 数据验证

| # | 验证项 | 结果 |
|:--:|:---|:---|
| 1 | commit 数量 | `git rev-list --count github/main..HEAD` = **6**（用户 prompt 写 7，计数误差，非 commit 缺失） |
| 2 | diff 范围 | 6 文件 +658/-71：`index.html`(新建 366 行) / `README.md`(13+/71-) / 设计文档(+139) / 设计评审报告(+95) / `review-log.md`(+34) / `.review-level.yaml`(+11) |
| 3 | demos/ 是否误改 | `git diff github/main..HEAD -- demos/` = **0 文件** ✅ |
| 4 | 根 style-guide.css | 存在，6361 字节（设计 §2 复用不复制，与设计评审证据一致）✅ |
| 5 | slide 子命令真实存在 | `html-gen.py:646` `add_parser('slide', ...)` — hero 第 4 命令非死命令 ✅ |
| 6 | 17 处链接可达性 | 本地 http.server 实测根页 + 17 本地链接**全部 200**（0 404）✅ |
| 7 | hero 100vh 渲染 | headless Chrome 独立复测：heroHeight = viewport = 614px，**ratio 1.0**（与 ops 757px 复测一致）✅ |
| 8 | 全量回归 | `python3 -m pytest tests/ -q -n 4` → **146 passed** (25.47s) 与 ops 复跑一致 ✅ |
| 9 | 敏感信息 | 变更文件（静态 HTML + 文档）无凭证/密钥/PII；外链仅公开 GitHub 仓库 + favicon ✅ |
| 10 | .review-level.yaml 校验 | `verify-review-level.py`：新增条目无缺失键/坏 verdict/坏 score，无重复 tracking；2 项失败为**已知既有漂移**（2026-07-23 条目缺 score、2026-08-19 REJECT verdict 不在脚本枚举集），顺序 ID 检查因本项目 range+括号描述式 tracking 属脚本限制，非数据错误 | ⚠️ 已知漂移 |

## 实现评估（对照设计文档）

### 1. 路径迁移清单（设计 §2，17 处）— ✅ 全量一致

grep 根 index.html 全部本地引用（排除 https）共 17 个唯一路径，与 v1.1 清单逐条比对：

| # | 设计 §2 新路径 | 实现出现次数 | 状态 |
|:--:|:---|:--:|:---:|
| 1 | `style-guide.css?=20260705` | 1 | ✅ |
| 2 | `demos/chaitin-business-analysis.html` | 2 | ✅ |
| 3 | `demos/cloudwise-business-analysis.html` | 1 | ✅ |
| 4 | `demos/countries/countries-table.html` | 1 | ✅ |
| 5 | `demos/demos-index.html` | 2 | ✅ |
| 6 | `demos/drama-knowledge.html` | 2 | ✅ |
| 7 | `demos/features/hermes-profile-skills-list.html` | 2 | ✅ |
| 8 | `demos/features/knowledge-demo.html` | 1 | ✅ |
| 9 | `demos/features/phase2-demo.html` | 2 | ✅ |
| 10 | `demos/features/table-actions-demo.html` | 1 | ✅ |
| 11 | `demos/html-gen-usage-guide-v1.0-20260707.html` | 1 | ✅ |
| 12 | `demos/templates/template-A-guide-v1.0-20260707.html` | 3 | ✅ |
| 13 | `demos/templates/template-B-guide-v1.0-20260707.html` | 3 | ✅ |
| 14 | `demos/templates/template-B-markdown-spec-v1.0-20260707.html` | 2 | ✅ |
| 15 | `demos/templates/template-C-guide-v1.0-20260707.html` | 1 | ✅ |
| 16 | `demos/templates/template-D-guide-v1.0-20260707.html` | 1 | ✅ |
| 17 | `demos/templates/template-D-slide-demo.html` | 2 | ✅ |

- `grep '\.\./' index.html` → **无残留** ✅
- CSS 为根级引用（非 `../style-guide.css`）✅
- HG-SEC-007 关闭确认：v1.1 全量 17 处清单（含 template-B-markdown-spec、template-D-slide-demo、countries/knowledge-demo/table-actions-demo/usage-guide 等）与实现逐条匹配 ✅

### 2. Hero 内容与形态（确认清单 2A+B+C + 3A）— ✅

| 确认项 | 设计要求 | 实现 | 状态 |
|:--:|:---|:---|:---:|
| 2A 价值定位 | 大标题 + 一句话定位 | `.hero-title` html-gen + `.hero-tagline`「零依赖 Python CLI：Markdown/JSON → 自包含单文件 HTML · 深色主题 · 中文优先」 | ✅ |
| 2B 安装 | ⚡ 安装 install.sh install + PATH | `.hero-block`「⚡ 安装」两条 code-block：`bash install.sh install` / `export PATH="$HOME/.local/bin:$PATH"` | ✅ |
| 2C 快速开始 | 🚀 4 命令（不含导航锚点） | doc / table / knowledge / slide 4 条（含 `--title` 变体），无导航锚点 | ✅ |
| 3A 100vh | 真 100vh 整屏 | `.hero { min-height: 100vh; display:flex; ... }`；实测 ratio 1.0 | ✅ |
| — | github-corner | 复制自 demos/index.html，外链带 `rel="noopener"` | ✅ |

### 3. 87d678f 修复正确性 — ✅

| 检查项 | 证据 | 状态 |
|:---|:---|:---:|
| 修复前根因成立 | `git show 47a3a84:index.html` 第 10 行注释含 `--surface-*/`（`*/` 提前闭合），与 ops 记录一致 | ✅ |
| 修复后注释无 `*/` 序列 | 当前注释「基于 style-guide.css 变量」；style 块 3 个 `/*` ↔ 3 个 `*/`，无 stray `*/`（正则剥离注释后无残留） | ✅ |
| .hero 规则恢复 | headless Chrome：`cssRules` 含 .hero，computed `min-height: 614px`（=100vh），display:flex | ✅ |
| 渲染形态 | heroHeight 614 = viewport 614，ratio 1.0 | ✅ |

### 4. README 精简（设计 §3）— ✅（含 1 个 🟢 偏差，见 HG-SEC-012）

| 设计要求 | 实现 | 状态 |
|:---|:---|:---:|
| 保留：一句话定位 | 首段定位句与 hero 一致 | ✅ |
| 保留：项目目录结构（简要） | 4 个链接点（模板/生成器/主题基座） | ✅ |
| 保留：站点首页链接 | `https://html-gen.lab.jaden.tech/` | ✅ |
| 保留：本地开发 | `python3 -m http.server 8089` + 访问路径 | ✅ |
| 精简幅度 | 85 行 → 27 行（-68%） | ✅ |
| 移除：四型模板表格 / 安装详细命令 / 指令速查 | 均已移除 | ✅ |
| 移除：快速开始命令 | **未移除**（保留精简版 4 命令 + install） | 🟢 见 HG-SEC-012 |

### 5. 第二屏模板网格（确认清单 5A + 6A）— ✅

- 4 卡（A 表格 / B 文档 / C 知识库 / D 幻灯片），icon + 场景 pills + 6 特性 + CLI 框 + 案例演示链接 ✅
- tpl-guide「模板使用说明 ↗」链接均带 `demos/templates/` 前缀（6A）✅
- 案例演示链接均带 `demos/` 前缀，与 5A「与现状一致」✅
- 案例演示清单区（html-gen demo list 提示 + 3 分组链接）完整 ✅

### 6. Commit 分组与消息规范 — ✅

| Commit | type@scope | 分组独立性 |
|:---|:---:|:---|
| 87834ef docs@html-gen: 设计 v1.0（review 输入） | ✅ | 独立（仅设计文档） |
| c4340b7 review@html-gen: 设计评审 PASS | ✅ | 独立（仅审计产物） |
| 543c9bf docs@html-gen: 设计 v1.1（HG-SEC-007） | ✅ | 独立（仅设计文档） |
| 47a3a84 feat@html-gen: 根 index.html | ✅ | 独立（仅 index.html） |
| 2472152 docs@html-gen: README slim | ✅ | 独立（仅 README） |
| 87d678f fix@html-gen: hero 100vh 修复 | ✅ | 独立（仅 1 行 CSS 注释） |

6/6 符合 `type@scope: subject` 格式；feat/docs/fix/review 职责分离干净 ✅

## 安全事项

无 🔴 HIGH / 🟡 MEDIUM 发现。2 个 🟢 LOW 记录（不计分）：

- **HG-SEC-012** 🟢 — README 章节去留与设计 §3 偏差：实现保留「快速开始」（设计列在移除清单），同时移除「案例演示/测试/零依赖」3 节（设计评审 SEC-010 建议默认保留）。无功能影响；二选一：接受现状（设计 v1.1 补注）或按设计再精简。
- **HG-SEC-013** 🟢 — 根 index.html 全部 `target="_blank"` **内链**（tpl-guide ×4、demo-item ×9 等，均 `demos/*` 同源）未带 `rel="noopener"`；外链（github-corner ×2）已带。同源页反向控制 opener 属边缘场景，且与源文件 demos/index.html 一致；建议批量补 `rel="noopener"`。

前置设计评审 🟢 处置核销：

| 前置 ID | 建议 | 实现处置 | 状态 |
|:---:|:---|:---|:---:|
| SEC-008 | CSS query 参数建议去除 | 保留 `?=20260705`（无害缓存参数） | 接受 |
| SEC-009 | hero 命令文本来源 README | 已从 README 复制，slide 命令经核实真实存在 | ✅ |
| SEC-010 | README 章节去留 | 见 HG-SEC-012 | 记录 |
| SEC-011 | AGENTS.md 漂移治理备注（可选「可」） | 未落实，1C 漂移风险维持设计评审时的接受状态 | 接受 |

## 评分

| 项 | 值 |
|:---|:---|
| Base | 100 |
| 🔴 HIGH × 0 | −0 |
| 🟡 MEDIUM × 0 | −0 |
| 🟢 LOW × 2 | −0（记录） |
| **Score** | **100 / 100** |
| **Rating** | **A** |
| **Verdict** | **PASS** |

## 结论

**PASS** — 6 个未 push commits 实现与已评审设计 v1.1 高度一致：17 处路径迁移逐条匹配、无 `../` 残留、CSS 根级引用；Hero 满足确认清单 2A+B+C（价值/安装/4 命令，无导航锚点）与 3A（100vh 实测 ratio 1.0）；87d678f 修复正确（注释不再含 `*/` 序列，.hero 规则恢复，浏览器实测整屏）；README 保留定位/目录/站点链接/本地开发 4 项且精简 68%；commit 6/6 符合 type@scope 规范且职责分离；demos/ 零误改；18 个 URL 全 200；全量 146 tests 无回归。2 个 🟢 记录（HG-SEC-012/013）不阻断发布，待用户确认处理方式。

## 待确认清单

| # | 项 | 建议 | 状态 |
|:--:|:---|:---|:---:|
| 1 | HG-SEC-012: README 保留「快速开始」与设计 §3 不一致 | 接受现状（推荐，README 27 行仍精简）并在设计 v1.1 补注，或按设计移除 | □ |
| 2 | HG-SEC-013: 内链 target=_blank 缺 rel="noopener" | 批量补 `rel="noopener"`（一次性，非阻断） | □ |

用户确认后关闭；无需复查亦可视为接受记录。
