# html-gen 12 commits 批量审查 — Design Document Review v1.0

**审查日期**: 2026-08-13
**审查级别**: L2
**范围**: 12 unpushed commits (6658b6d..8d0ec21), 18 files, +1153/-13

---

## 一、Commit 规范检查

12/12 全部遵循 `type@scope: subject` 格式：

| 类型 | 数量 | commits |
|:---|:--:|:---|
| docs@ | 8 | SKILL.md 同步 ×3, 设计文档 ×2, review prompt, verify prompt ×2 |
| feat@ | 3 | prompt subcommand, table pills/split, h4-h6 rendering |
| review@ | 1 | heading-levels re-review |

✅ 无违规。scope 均为 `html-gen`，subject 描述准确。

---

## 二、命名规范检查

18 个文件全部合规：

| 类别 | 文件 | 规范 |
|:---|:---|:---|
| 设计/评审文档 | `documents/*.md` | `{topic}-{type}-v{ver}-{date}.md` |
| 测试 | `tests/test_*.py` | pytest 下划线约定 |
| 技能 | `skills/*/SKILL.md` | 大写 SKILL.md 标准 |
| 引用 | `skills/*/references/*.md` | hyphens |
| 源码/模板 | `html-gen.py` `layout-*.html` | hyphens |

✅ 无中文文件名，无违规扩展名。

---

## 三、实现与设计一致性

| 功能线程 | 设计文档 | 实现 commit | 验证 |
|:---|:---|:---|:--:|
| prompt CLI | html-gen-prompt-cli-design | 8a3987b | ✅ list/full/brief/错误处理 与设计一致 |
| h4-h6 标题 | heading-levels-fix-design | a02897b | ✅ 从长到短匹配 + 拆分 anchor 循环 |
| table pills/split | (无独立设计) | 5ba6dcd | ✅ 斜杠切分 + initialHidden + 分栏全列渲染, 5 tests |

### 关键验证点

- md_to_html: `###### → ... → #` 从长到短，无误吞
- h4-h6 anchor 循环: 用 `'section-' + i`（索引），采纳了 review 🟢 观察（非 textContent）
- prompt cmd_prompt: SKILLS_DIR 自定位，无参/带参/--brief/不存在 四分支完整
- pills 斜杠切分: `[,，、/]+` 三处同步（tabs contains / quickFilter / pills 渲染）
- 分栏详情: `COLUMNS.filter(c => c.key && c.type !== 'actions' && !c.hide)` 全列渲染

---

## 四、测试

`python3 -m pytest tests/ -q` → **100 passed, 0 failed (129s)**

新增测试: test_heading_levels.py (139行), test_initial_hidden_split.py (107行), test_prompt_cmd.py (51行)

---

## 安全事项

无安全发现。prompt CLI 仅本地文件读取 + stdout 输出；h4-h6 为增量渲染；pills/initialHidden 为列配置语义扩展。无 innerHTML 注入、无路径穿越、无 eval。

---

## 结论

**PASS** — 授权 push。12 commits 全部合规，3 个功能线程实现与设计一致，100 tests 全绿。

**备注**: `skills-extension/`（untracked）不在本次审查范围，未纳入 commit。
