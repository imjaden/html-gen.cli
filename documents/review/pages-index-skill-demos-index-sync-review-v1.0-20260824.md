# pages-index skill + demos-index sync — review报告 v1.0

> 日期: 2026-08-24
> 项目路径: /Users/jadenli/CodeSpace/html-gen.cli
> 待 push commit: 7a0f591 / a75733f / 4b06b8d（位于已 PASS 的 e3ac2ff 之后）
> review维度: 合理性 / 严格性 / 安全性（commit-range-audit, L2）
> 前置基线: e3ac2ff review@html-gen index-landing sync re-review — PASS 100/A (HG-SEC-029..036 closed)

## 数据验证

| 验证项 | 方法 | 结果 |
|:-------|:-----|:-----|
| 全量测试 | `python3 -m pytest tests/ -q -n 4` | ✅ **180 passed in 33.12s**（20 文件，与基线 180 一致，无回归） |
| prompt 输出 | `python3 html-gen.py prompt pages-index --brief` | ✅ exit 0，description + 9 章节（概述~Pitfalls）正常输出 |
| skill 注册 | `python3 html-gen.py prompt --json` | ✅ data 列表含 `pages-index`（description 匹配） |
| 主题按钮 right:88px | grep index.html:196 | ✅ `position: fixed; top: 16px; right: 88px` |
| localStorage key | grep index.html:447,452 | ✅ `html-gen:index_theme`（读写两处） |
| hero 动态两屏 | grep index.html:430 | ✅ `minHeight = (window.innerHeight - 110) + 'px'` |
| copyText orig 恢复 | grep index.html:458-461 | ✅ `var orig = btn ? btn.textContent : ''` + 恢复 `btn.textContent = orig` |
| execCommand 返回值检查 | grep index.html:468 | ✅ `try { ok = document.execCommand('copy'); } catch(e) {}` + `if (ok) done()` |
| github-corner 浅色变量 | grep index.html:187-190,237 + style-guide.css:36-37,69-70 | ✅ `--gh-corner-fill`/`--gh-octocat` 深浅两组 + `:root.light .github-corner` 高特异性覆盖 |
| :root.light 浅色组 | grep style-guide.css | ✅ 9 处，--text-*/--gh-* 全套变量 |
| 模板页 theme key | grep layout-doc.html:300,308 / layout-knowledge.html:258,266 / demos/slide-demo.html:1003,1011 | ✅ doc_theme / kw_theme / layoutslide_theme 三处与 SKILL.md 声称一致 |
| 双源防漂移测试 | read tests/test_demos_index.py:83-104 | ✅ test_05_dual_source_consistency features 与 SKILL.md 声称一致（themeBtn/index_theme/site-footer/copy-btn/1500px/gh-octocat/noopener/4 cli 命令/demos-title） |
| demos-index 无 JS 错误 | selenium 直接加载 demos/demos-index.html | ✅ JS errors: NONE；18 行表格渲染；3 列 sortable 点击排序 OK；search input 存在 |
| demos-index 无主题按钮 | selenium + grep | ✅ themeBtn count 0，light class 未激活（A 型表格变量仅基座） |
| 生成器回归一致性 | `html-gen.py table -d data/_demos-data.json` 重新生成 → diff 已提交产物 | ✅ 仅 title 参数差异（"T" vs "DEMO 案例索引"），其余 0 差异 |
| 提交格式 | git log e3ac2ff..HEAD | ✅ 3/3 `type@scope: subject`（docs@skills / chore@project / sync@demos-index） |
| git 状态 | git status --porcelain | ✅ clean（无未跟踪文件） |
| 未 push 范围 | git branch -vv | ✅ main 领先 github/main 恰好 3 commit = 本次评审范围 |

## 合理性评估

| # | 项 | 评估 |
|:-:|:---|:-----|
| 1 | SKILL.md 内容来自 index 落地页两轮迭代（e1add13/0b015a4/25f299a/5e9508a/775d27f），是对已实现行为的规范化沉淀，非空想设计 | ✅ |
| 2 | 文档与实现的一致性核对 6/6 项全部落位（主题按钮/theme key/hero/copy/corner/light 组），无漂移 | ✅ |
| 3 | demos-index 重建仅内联 style-guide.css 新变量，不引入新行为；该页无主题按钮，light 变量组为惰性基座 | ✅ |
| 4 | a75733f 为 .hermes-project.yaml handoff updated_at 时间戳更新（2026-08-22 → 2026-08-24），trivial | ✅ |

## 严格性评估

| # | 项 | 评估 |
|:-:|:---|:-----|
| 1 | SKILL.md 覆盖骨架/主题/corner/两屏/复制/双源/测试/Pitfalls 八节，含特异性陷阱（`:root.light a` 覆盖 corner）与 inline style 硬编码色警示 | ✅ |
| 2 | SKILL.md 的代码片段（updateHeroHeight / copyText / 防漂移测试 features）与仓库真实实现逐行一致 | ✅ |
| 3 | 生成产物回归一致（重新生成 diff 0 差异）证明 4b06b8d 为真实生成产物，非手工修补 | ✅ |
| 4 | 防漂移测试 test_05 断言双源 12 项功能特征一致，覆盖主题/复制/footer/断点/corner/外链安全/4 命令 | ✅ |

## 安全事项

🟢 SEC-037 — demos/demos-index.html 页面本身无直接测试覆盖

描述: test_demos_index.py 直接加载的是 demos/index.html（模板展示首页），A 型表格索引页 demos/demos-index.html 未进入任何 Selenium 测试的 URL。其功能回归目前仅靠 test_templates.py:150 的生成路径测试 + test_demo_cmd.py:73 test_08_rebuild_idempotent 间接覆盖。本次手动 selenium 验证（无 JS 错误、18 行渲染、排序可用）通过，但建议后续将 demos-index 页面纳入 test_demos_index 或模板测试的 URL 列表，防止未来重建引入 JS 错误时无测试兜底。
修复建议: 在 test_demos_index.py 增加一个指向 demos/demos-index.html 的加载断言（或复用现有 class 传参 URL），记录性建议，不阻断。

无 🔴 / 🟡。无注入面（无用户输入进 innerHTML 的新路径）、无凭证、无外部脚本依赖、无新增依赖。

## 评分

| 级别 | 数量 | 扣分 |
|:---:|:---:|:---:|
| 🔴 HIGH | 0 | 0 |
| 🟡 MEDIUM | 0 | 0 |
| 🟢 LOW | 1 | 0 |
| **Base 100 → 得分** | | **100 / 100 → A** |

## 结论

**PASS (A, 100/100)** — 3 个 commit 全部通过:

1. **7a0f591 docs@skills**: pages-index SKILL.md 与已实现 index.html 行为 6/6 项一致性核对全部落位，prompt 输出正常，frontmatter 完整，提交格式合规。
2. **a75733f chore@project**: trivial 时间戳更新，2 行 diff，无风险。
3. **4b06b8d sync@demos-index**: 真实生成产物（回归 diff 0 差异），无 JS 错误，浅色变量仅基座不破坏 A 型表格功能。

全量 180 passed，git status clean，PASS 授权 push 至 github/main。

## 待确认清单

| □ | 项 | 类别 |
|:-:|:---|:-----|
| □ | SEC-037（🟢 记录）: 为 demos/demos-index.html 增加直接页面测试 | 安全性 🟢 |
