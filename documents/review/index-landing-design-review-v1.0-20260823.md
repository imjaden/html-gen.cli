# index-landing-design — review报告 v1.0

> 日期: 2026-08-23
> 文件: documents/index-landing-design-v1.0-20260822.md
> 项目路径: /Users/jadenli/CodeSpace/html-gen
> 待 push commit: 87834ef (docs@html-gen: index landing design v1.0 — root index.html + hero + README slim (review 输入))
> review维度: 合理性 / 严格性 / 安全性
> review_type: design-document-review
> review_level: L2

## 数据验证

| 验证项 | 方法 | 结果 |
|:-------|:-----|:-----|
| 根目录无 index.html | `ls -la` 根目录 | ✅ 确认（根目录仅 layout-*.html，无 index.html） |
| style-guide.css 字节数 | `wc -c style-guide.css` | ✅ 6361 字节（设计文档 §2 声明一致） |
| demos/index.html 相对路径引用全集 | `grep -noE '(href\|src)="[^"]+"' demos/index.html` | ✅ 27 处引用（含 head CSS 1 处 + grid 内 12 目标文件 14 处 + footer 12 处） |
| grid 内（L62-196）引用去重目标 | `sed -n '62,196p' \| sort -u` | ✅ 12 个目标文件：template-A/B/C/D-guide、template-B-markdown-spec、template-D-slide-demo、demos-index、features/hermes-profile-skills-list、features/phase2-demo、drama-knowledge、cloudwise-business-analysis、chaitin-business-analysis + head CSS 1 处 |
| 设计 §2 清单完整性（8 行 vs 实际） | 清单逐行对比实际引用 | ❌ 通配符 `templates/template-*-guide-v1.0-20260707.html` 仅匹配 4 个 guide 文件，漏 `template-B-markdown-spec-v1.0-20260707.html` 与 `template-D-slide-demo.html`（grid 内 B 卡 L124 / D 卡 L194 演示链接） |
| CNAME | `cat CNAME` | ✅ `html-gen.lab.jaden.tech`（与背景一致） |
| install.sh 子命令 | `grep -nE 'install\|status\|uninstall\|help' install.sh` | ✅ 支持 install/uninstall/status/help（-i/-u/-s/-h），hero 安装命令可行 |
| README 现状 | `wc -lc README.md` | ✅ 85 行 / 3338 字节，含 四型模板/安装/快速开始/指令速查/案例演示/测试/零依赖 章节 |
| 设计文档命名规范 | 文件名检查 | ✅ `index-landing-design-v1.0-20260822.md` — Style A kebab-case，topic 无点无下划线，日期 8 位 |
| 设计文档 frontmatter | `head -4` | ✅ 项目惯例无 YAML frontmatter（13 个设计文档均同），用 `## 版本` 标题段；文件名 v1.0 与正文 v1.0 一致 |
| 提交规范 | `git log --oneline` | ✅ 87834ef `docs@html-gen: index landing design v1.0 — ...` — type@scope: subject，docs 在枚举内 |
| 待确认清单 6 项定稿 | 设计文档 §待确认清单 | ✅ 1C/2A+B+C/3A/4B/5A/6A 全部有用户确认结果，与本次 prompt 一致 |

## 合理性评估

| # | 检查项 | 判定 |
|:--|:-------|:----:|
| REA-1 | 问题匹配：站点首页无主题色、无落地页 → 新建根 index.html 覆盖 README 渲染 | ✅ 切中痛点，dogfood 合理 |
| REA-2 | 架构：hero 100vh + 第二屏网格复用 demos/index.html | ✅ 组件拆分自然，复用而非重建 |
| REA-3 | 范围控制：两份独立维护（1C）而非抽取共享模板 | ✅ 与用户确认一致，未过度工程化 |
| REA-4 | 集成：demos/index.html 多处被引用（README/usage-guide/hermes-profile-skills-list），不动 | ✅ 现状评估准确（背景节明确引用方） |
| REA-5 | 需求追溯：hero 内容 ↔ 确认清单 2A+B+C / 3A / 4B / 5A / 6A | ✅ 全部 1:1 对应（价值定位/安装/4 命令/100vh/README 精简/案例演示/使用说明） |
| REA-6 | 漂移风险（1C）在设计 §风险明确 | ✅ 明确"接受漂移、同步维护两处、治理上可在 AGENTS.md 备注" |

## 严格性评估

| # | 检查项 | 判定 |
|:--|:-------|:----:|
| RIG-1 | 路径迁移清单完整可执行 | ❌ 见 SEC-007：通配符漏 2 个 templates 文件，清单数字"8 处"不准确（实际 grid 内 12 目标文件 + CSS） |
| RIG-2 | hero 4 条快速开始命令具体文本 | ⚠️ 见 SEC-009：设计仅写"doc/table/knowledge/slide 4 命令"，未给出命令文本（实现需从 README 复制） |
| RIG-3 | README 精简方案覆盖全部现有章节 | ⚠️ 见 SEC-010：保留/移除清单未提 案例演示/测试/零依赖 3 章节 |
| RIG-4 | CSS 引用 query 参数处理 | ⚠️ 见 SEC-008：实际为 `../style-guide.css?=20260705`，清单写 `../style-guide.css` |
| RIG-5 | 验证步骤（§4）：本地冒烟 + 无 404 + 无 JS 错误 + 100vh 检查 | ✅ 覆盖关键风险点，404 检查可兜底 SEC-007 |
| RIG-6 | 变更文件清单 | ⚠️ 见 SEC-011：3 文件（index.html/README/设计文档），未含 §风险提及的可选 AGENTS.md 备注 |

## 安全性评估

| # | 检查项 | 判定 |
|:--|:-------|:----:|
| SEC-A1 | 注入面 | ✅ 纯静态 HTML/CSS，无用户数据输入、无 SQL/命令拼接 |
| SEC-A2 | 第三方依赖 | ✅ 零外部依赖（CSS 内联、无 CDN 脚本）；github-corner 指向 github.com/imjaden/html-gen 仓库链接，安全 |
| SEC-A3 | 敏感信息 | ✅ 无 API key/token/凭据，无 .env 引用 |
| SEC-A4 | 数据流 | ✅ 无数据流，静态展示页 |

## 安全事项

🟡 SEC-007 — 路径迁移清单不完整：通配符 `templates/template-*-guide-v1.0-20260707.html` 只匹配 4 个 guide 文件，漏掉 grid 内实际引用的 `templates/template-B-markdown-spec-v1.0-20260707.html`（L124 B 卡演示链接）与 `templates/template-D-slide-demo.html`（L194 D 卡演示链接）；清单声明"共 8 处引用点（7 个目标文件 + 1 个 CSS）"与实际不符（grid 内 12 个目标文件 + CSS，均已在 demos/templates/、demos/features/ 确认存在）。按清单迁移将产生 2 个 404 演示链接。

修复建议：将清单第 2 行通配符改为显式列出全部 6 个 templates 文件（A/B/C/D guide + B-markdown-spec + D-slide-demo），或按 prompt 原文改用 `templates/*.html` 全量迁移（demos/templates/ 下共 11 个文件，含 .md 源 4 个，grid 引用仅 6 个 html）；同步更正"8 处引用点"数字描述。

🟢 SEC-008 — CSS 引用 query 参数未标注：实际为 `../style-guide.css?=20260705`（缓存版本参数），清单写作 `../style-guide.css`。迁移时保留或去除需明确（建议去除，根 index.html 新建无缓存需求）。

🟢 SEC-009 — hero 快速开始命令文本未给出：设计仅写"doc/table/knowledge/slide 4 命令"，未列出具体命令（README §快速开始 4 条可直接复制）。实现时可从 README 复制，不影响正确性。

🟢 SEC-010 — README 精简方案未覆盖全部现有章节：保留 4 项 + 移除 4 项，未明确 案例演示（L62-70）/测试（L72-79）/零依赖（L81-85）3 章节去留。建议默认保留（案例演示链接与 5A 呼应，测试/零依赖为仓库开发说明），设计应写明。

🟢 SEC-011 — 漂移治理备注未列入变更清单：§风险写"治理上可在 AGENTS.md 备注两文件关系"（可选措辞"可"），但 §变更文件清单仅 3 个文件。若落实治理备注需将 AGENTS.md 加入变更清单；1C 已接受漂移，不阻塞。

## 评分

| 严重性 | 数量 | 扣分 |
|:------:|:----:|:----:|
| 🔴 HIGH | 0 | 0 |
| 🟡 MEDIUM | 1 | -5 |
| 🟢 LOW | 4 | 0 |

得分: 95 / 100 → Rating: A

## 结论

**PASS** — 设计方案整体合理，与用户确认清单 6 项一致，无安全风险。1 个 🟡 非阻塞（迁移清单不完整，验证步骤 §4 的 404 检查可兜底），4 个 🟢 记录。SEC-007 建议由 ops 修订设计文档后进入实现（或实现时直接按全量 `templates/*.html` 迁移并在验证步骤确认无 404）。

## 待确认清单

| □ | 项 | 类别 |
|:-:|:---|:-----|
| □ | SEC-007: 迁移清单补 2 个 templates 文件（或改全量 `templates/*.html`）并更正"8 处"数字 | 严格性 🟡 |
| □ | SEC-008: CSS query 参数保留/去除 | 严格性 🟢 |
| □ | SEC-009: hero 快速开始命令文本来源（README 复制） | 严格性 🟢 |
| □ | SEC-010: README 案例演示/测试/零依赖章节去留 | 严格性 🟢 |
| □ | SEC-011: AGENTS.md 漂移备注是否纳入变更清单 | 合理性 🟢 |
