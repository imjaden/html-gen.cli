# html-gen → html-gen.cli 改名实现审计 — review报告 v1.0

## 审计概况

- **审计类型**: Implementation Audit (L2)
- **审计对象**: 未 push commits（github/main..HEAD，1 个）
  1. `020ac34` chore@html-gen: rename to html-gen.cli — github/pages links 批量更新 + 上箭头返回首页(A 标题行/B 固定按钮) + 手工微调纳入
  - 注：`982a818` Update CNAME（html-gen.cli.jaden.tech）已包含于 github/main（用户已推送）；gitee origin/main 尚缺 2 个（982a818 + 020ac34）
- **需求来源**: 用户确认清单 D1A/D2A/D3A/D4A/D5C/D6B（R1-R5）
- **审计方法**: 逐条映射 R1-R5 → diff 独立复核（git show 020ac34 + github/main..HEAD 全 diff）→ 残留扫描（旧链接/旧域名/双后缀/产品名）→ 历史文档边界验证 → 全量 pytest 独立复核 → 凭证/XSS 扫描
- **审计日期**: 2026-08-23

## 数据验证

| # | 验证项 | 结果 |
|:--:|:---|:---|
| 1 | 未 push commit 数 | `git log github/main..HEAD` = **1**（020ac34）；982a818 已含于 github/main（merge-base 验证 ✅）；gitee origin/main..HEAD = 2 |
| 2 | diff 范围 | 47 文件 +149/-106：README.md(1/1) + index.html(59/16) + 4 layout 模板源 + 41 demos 生成物 |
| 3 | R1 旧链接残留（排除历史文档） | `git grep 'github.com/imjaden/html-gen[^.]'`（排除 documents/review-log/cache）= **0** ✅ |
| 4 | R1 新链接覆盖 | `git grep -l 'github.com/imjaden/html-gen.cli'` = **46 文件** ✅（根 index + 4 layout + 41 demos） |
| 5 | 双后缀 | `grep html-gen.cli.cli` = **0** ✅ |
| 6 | R2 旧域名残留 | `git grep 'html-gen.lab.jaden.tech'`（排除历史文档）= **0**；CNAME = html-gen.cli.jaden.tech ✅ |
| 7 | D1A 产品名保持 | README h1 `# html-gen`、index `<title>html-gen · 零依赖 HTML 模板生成器</title>`、hero `<h1 class="hero-title">html-gen</h1>` 均未改 ✅ |
| 8 | 历史文档保留旧链接 | 仅 documents/review/index-landing-design-review-v1.0-20260823.md 保留旧链接（预期，未被误改）✅ |
| 9 | 历史文档未被误改 | `git diff github/main..HEAD -- documents/ review-log.md .review-level.yaml cache/` = **0 文件** ✅ |
| 10 | R3-A 上箭头形式 | h2 标题行 `<a href="#" class="back-top-link">↑ 返回首页</a>` + 全局 `html { scroll-behavior: smooth; }`，可见文本可访问 ✅ |
| 11 | R3-B 固定按钮 | `.back-to-top` fixed 右下角，初始 `opacity:0; visibility:hidden`，scroll 监听 `window.scrollY > window.innerHeight` toggle show，`aria-label="返回首页"` ✅ |
| 12 | R4 手工微调 4 项 | hero-blocks max-width 880→1024px / demo-name `display:block` / scroll-hint '↓ 模板说明' / 四卡「A 型」→「A 模板」（A/B/C/D 4 处 + 注释 4 处）✅ |
| 13 | R5 gitee remote | `git remote -v`：origin → git@gitee.com:imjaden/html-gen.cli.git、github → git@github.com:imjaden/html-gen.cli.git（git 配置，无 commit）✅ |
| 14 | commit 单一性 (D6B) | 020ac34 单个 commit 含 R1-R4；R5 为配置无 commit ✅ |
| 15 | demos/index.html featured | 仅 github-corner 链接 2 处替换（4 行），★ 手工精选清单与案例链接零改动 ✅ |
| 16 | 凭证/注入扫描 | 全 diff 无 secret 模式（api_key/token/password/private key）；无 innerHTML/document.write/eval/new Function ✅ |
| 17 | 全量测试 | pytest 全量独立复核 **146 passed** in 25.28s（无 flaky 复现）✅ |

## 实现评估（对照 R1-R5）

### R1. github 链接批量替换 — ✅

- 46 个 html 覆盖完整：根 index.html + 4 layout 模板源（doc/table/knowledge/slide）+ 41 demos 生成物（chaitin/cloudwise/countries/drama/features/templates 全子目录）
- 每文件替换模式：`github-corner` 主链接 + `github-corner-hit` 隐藏区链接（2 处/文件，4 行/文件）；knowledge-demo.html 单链接（无 hit 层，grep 验证 = 0）
- 旧链接 `github.com/imjaden/html-gen`（非 .cli 后缀）排除历史文档后 **0 残留**
- 双后缀 `html-gen.cli.cli` **0**（sed 未重复匹配）
- 无 github 链接的 19 个 html（chaitin 子页/drama timeline 页/features 工具 demo 等）天然无 github-corner，不在替换范围，正确未动

### R2. 域名更新 — ✅

- README.md:5 站点链接 `html-gen.lab.jaden.tech` → `https://html-gen.cli.jaden.tech/`
- CNAME（982a818，用户提交）：`html-gen.cli.jaden.tech`，已推送 github
- 全仓库新域名出现位置：仅 CNAME + README（正确，页面内无硬编码域名）
- **D1A 未违反**：README h1 / index title / hero 产品名保持 "html-gen"，未误改成 html-gen.cli

### R3. 上箭头返回首页 A/B 双形式（D5C）— ✅

**A 形式（模板区标题行）**：`<h2 class="templates-title">四型模板 · 一套深色主题 <a href="#" class="back-top-link">↑ 返回首页</a></h2>`
- href="#" + 全局 `scroll-behavior: smooth` → 平滑回顶
- 可见文本「↑ 返回首页」→ 可访问性达标（非纯 icon 链接）
- pill 样式 + hover 反馈，与模板区视觉一致

**B 形式（固定右下角按钮）**：`<a href="#" class="back-to-top" aria-label="返回首页">↑</a>`
- 初始 `opacity: 0; visibility: hidden`（不占视觉、不可聚焦）
- scroll 监听 `window.scrollY > window.innerHeight` → `.show` toggle（超过一屏显示）
- 点击 href="#" 回顶，回顶后 scroll 事件触发隐藏（符合"回顶隐藏"需求）
- `aria-label="返回首页"` + z-index 900（低于 github-corner 950，不遮挡）
- ops Selenium 8094 已验证：点击 scrollY=0 / 滚动后 show+visible / 回顶后隐藏

### R4. 手工微调纳入 — ✅

| 微调项 | 实现 | 状态 |
|:---|:---|:---:|
| hero-blocks max-width 1024px | `.hero-blocks` 880px → 1024px | ✅ |
| demo-name display:block | `.demo-info .demo-name` 增 `display: block` | ✅ |
| '↓ 模板说明' 文案 | scroll-hint `↓ 模板展示` → `↓ 模板说明` | ✅ |
| 四卡「型」→「模板」 | A/B/C/D 四卡 tpl-name + demo-name + 注释 8 处措辞统一 | ✅ |

### R5. gitee origin remote — ✅

- origin → `git@gitee.com:imjaden/html-gen.cli.git`（gitee 新地址）
- github → `git@github.com:imjaden/html-gen.cli.git`
- 纯 git 配置，无 commit，符合 D6B

### D6B. Commit 单一性 — ✅

- 020ac34 单个 commit 完整含 R1-R4（README + 46 html + index.html 微调），commit 消息准确概括内容
- R5 为 git 配置无 commit
- 982a818 CNAME 为用户独立提交（已推送 github，待推 gitee）

## 安全事项

无 🔴 HIGH / 🟡 MEDIUM 发现。1 个 🟢 LOW 记录（不计分）：

- **HG-SEC-015** 🟢 — A/B 上箭头均使用 `href="#"` 空锚点而非 `href="#top"` + 显式 scrollTo：空锚点会改变 URL hash（若页面已有 #hash 会被替换），依赖全局 `scroll-behavior: smooth` 生效；当前行为经验证正确（scrollY=0），无安全影响，属实现细节建议。`index.html:216,360`

## 评分

| 项 | 值 |
|:---|:---|
| Base | 100 |
| 🔴 HIGH × 0 | −0 |
| 🟡 MEDIUM × 0 | −0 |
| 🟢 LOW × 1 | −0（记录） |
| **Score** | **100 / 100** |
| **Rating** | **A** |
| **Verdict** | **PASS** |

## 结论

**PASS** — 020ac34 与用户确认清单 R1-R5 逐条一致：github 链接 46 文件批量替换完整（0 残留 0 双后缀，历史文档边界清晰未误改）、域名 README+CNAME 双更新且 D1A 产品名 "html-gen" 严格保持、上箭头 A（标题行可见文本链接）/B（固定按钮超一屏显示+回顶隐藏）双形式实现符合 D5C、手工微调 4 项全部纳入、R5 gitee remote 配置正确、commit 单一性符合 D6B（1 commit 含 R1-R4，R5 无 commit）。demos/index.html featured 逻辑零误改；全量 pytest 146 passed 独立复核通过；无凭证、无 XSS、无新增外部资源。1 个 🟢 记录（href="#" 空锚点细节），不阻断。PASS 后由 ops 推双远程（github 推 020ac34；gitee 推 982a818 + 020ac34）。

## 待确认清单

| # | 项 | 建议 | 状态 |
|:--:|:---|:---|:---:|
| 1 | HG-SEC-015: A/B 上箭头 href="#" 空锚点 | 接受现状（行为正确）或后续改 href="#top" + scrollTo | □ |
