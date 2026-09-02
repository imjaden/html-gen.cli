
# html-gen C 型知识库规范

## 概述
C 型知识库通过顶部 tab 分组、左侧 section-as-menu 的导航结构，以 iframe 或内联 HTML 展示内容。专为多主题知识索引场景设计。

## 何时使用
- 多主题知识索引（如以剧读史、技术文档索引）
- 需要 tab 切换 + 侧栏导航的知识库
- section 与 item 一对一时可跳过 item 行直接点击 section 标题

## CLI 用法

```
html-gen knowledge -d data.json [-g groups.json] [--title "标题"] [--welcome "欢迎语"] [-o kb.html]
```

## 数据格式

```json
[
  {"title": "条目名称", "group": "所属类目", "section": "子分类",
   "url": "detail.html", "desc": "<p>内联 HTML</p>", "badge": "标记"}
]
```

- `title` 必填, `group` 必填, `section` 可选
- `url` 与 `desc` 二选一 (iframe vs 内联渲染)
- `badge` 可选 (自定义标记)
- title 与 section 同名时自动跳过 item 行 (K2 rule)
- 输出目标: 结构化 dict 顶层可带 `"output"`（仅 data 文件识别，groups 文件忽略）；优先级 CLI `-o` > JSON `output` > 均无中断 (exit 1)

## groups 格式

```json
[{"key": "类目key", "label": "显示名", "icon": "🏛️"}]
```

## 模板特性
- 顶部横向标签栏 (按 group 分组)
- 左侧 section-as-menu (section 标题可点击跳转)
- selectItem 双参数 (group, title) 支持跨组同名
- 侧边栏搜索 (150ms debounce, ≥2 字符过滤)
- 折叠/展开侧边栏 (`[` 快捷键, localStorage)
- 双内容模式 (iframe / 内联 HTML)
- 空状态欢迎面板
- localStorage 状态恢复 (group + item)

## 注意事项
- iframe 内容必须与知识库页面同源
- 单条 section (title===section && count===1) 自动跳过 kw-item 渲染
- Selenium headless 测试: iframe 内元素需 `driver.switch_to.frame()` 切换

## 变更记录
- v1.0.0 (2026-08-08): 首次提炼自 drama 知识库实施经验 + AGENTS.md
