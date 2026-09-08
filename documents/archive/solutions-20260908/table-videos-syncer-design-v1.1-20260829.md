# A 型表格 videos 同步辅助脚本设计 v1.1 (2026-08-29)

> 闭环: HTML-GEN-CL002 ｜ 探讨确认: A1 B1 C1 D1 E2 F3 W1（2026-08-28 拍板）
> 前置: HTML-GEN-CL001（videos 字段，已闭环）——本脚本为其数据维护配套工具
> v1.1: 评审 CONDITIONAL 85/B（24b9cbc）修复 —— RIG-001/002/003（HG-SEC-054/055/056）+ 🟢 规格落地（HG-SEC-057..060）

## 1. 背景与需求

CL001 落地了 table 模板 `col.type="videos"` 列，countries-table 已有 10 行带 videos。
手工编辑 data/_countries-data.json（131.7KB/195 行，实测 2026-08-29）追加视频易错且无流程。需要一个辅助脚本：【v1.1: HG-SEC-060】

- 以 yaml 为增量输入（手写友好，放 cache/ 本地草稿），按 `country_zh` 外键匹配 json 行
- 以 url 去重，将 yaml 中 json 尚未包含的视频补充进对应行 videos 数组
- 将 json 全部 videos 按 yaml 格式回写 yaml（全局镜像），保持 yaml 为完整工作副本
- 同步后自动重建 demos 产物（html-gen table）

## 2. 决策记录

| 项 | 决策 | 说明 |
|:---|:---|:---|
| A 格式 | 结构化 map，字段与 json 一致 | `countries` 平铺列表，每条 country_zh/title/url/duration/platform 五字段 |
| B 存放 | yaml 留 cache/ 不入库 | cache/ 在 .gitignore，纯本地草稿；入库的仅同步后 json + 重建 html |
| C platform | URL host 自动识别兜底 | v.douyin.com→douyin / bilibili→bilibili / youtube|youtu.be→youtube / 其他省略；回写时写 json 现值 |
| D 依赖 | PyYAML 入 requirements-dev.txt | 仅 dev 依赖（脚本层），不影响运行时零依赖 |
| E 重建 | 同步后自动重建 html | subprocess 调 html-gen.py table -d <target.data> -o <target.html>（命令已实测可复现） |
| F 校验 | 国家键无匹配 → 报错退出 | 写盘前全量校验，任一缺失列清单 exit 1，不写 json/不回写/不重建（避免半写） |
| W 回写 | 全局镜像 | yaml countries 段整体重建为 json 全部 videos（target 段保留原样） |
| G 无增量 | 全存在 → 打印提示中断 | 所有 yaml 视频已含于 json 时，不写 json/不回写/不重建（幂等） |

补充规格（设计内定，无需再确认）：
- 脚本名 scripts/tool-table-videos-syncer.py（v1.1 修正：原 vides 拼写错误，新建文件零迁移成本，统一为 videos 拼写）【v1.1: HG-SEC-058】
- CLI：`scripts/tool-table-videos-syncer.py <yaml-path> [--dry-run] [--apply]`；默认无参 = dry-run 预览；--dry-run 与 --apply 同传 → 报错互斥
- 去重键 = url（strip 后精确比较）；yaml 内部同 url 重复 → 后者忽略
- duration 保持字符串原样（M:SS / H:MM:SS），不转数值；int 容错仅支持 M:SS（未引号 int < 3600 按秒数归一化，如 415 → "6:55"；M:SS 上界 59:59 = 3599s）；H:MM:SS 必须引号包裹（未引号 3723 不在容错语义内）【v1.1: HG-SEC-057】【v1.1: HG-SEC-061 修正 6000→3600】
- additive 语义：只 append 不删除不覆盖；yaml 某国列表为空 = 无操作；未覆盖行不动

## 3. yaml 格式规格（A）

```yaml
target:
- data: data/_countries-data.json
- html: demos/countries-table.html

countries:
- country_zh: 缅甸
  title: 缅甸-散装缅甸
  url: https://v.douyin.com/-IIdHuXNL0o/
  duration: "6:55"
  platform: douyin

- country_zh: 伊朗
  title: 伊朗-美国为什么征服不了伊朗
  url: https://v.douyin.com/1IxN2ag0e8U/
  duration: "11:38"
  platform: douyin
```

- `target`：列表形态 `[{data: ...}, {html: ...}]`，data 为待同步 json 相对路径，html 为重建产物路径
- `countries`：平铺列表，字段名与 json videos 条目一致（country_zh/title/url/duration/platform）
- `country_zh` 必填：外键，对应 json 行 `data[].country_zh`
- `duration` 必须引号包裹（"6:55"）：未加引号时 YAML 按 60 进制解析为整数（415），实测坑
- `platform` 可省略：缺省由 C1 按 URL host 自动识别；回写时始终写 json 现值
- 回写时 duration 统一带引号、url strip 尾部空白

## 4. 脚本行为规格

### 4.1 CLI

```
scripts/tool-table-videos-syncer.py <yaml-path> [--dry-run] [--apply]
```

- 无参/--dry-run：预览模式，打印「新增明细（国家+标题+url）/ 跳过（已存在）/ 回写与重建计划」，不写任何文件
- --apply：执行全部写盘（json → yaml 回写 → html 重建）
- --dry-run 与 --apply 同传：argparse 冲突报错，exit 2

### 4.2 执行流程（--apply）

1. 解析 yaml（PyYAML，必须用 `yaml.safe_load`；禁用 yaml.load / FullLoader，防 `!!python/object` 任意代码执行），取 target.data / target.html 与 countries 列表【v1.1: RIG-001 / HG-SEC-054】
2. 读 target.data json；建 country_zh → row 索引。路径解析基准：target.data / target.html 等相对路径一律以项目根为基准解析（脚本须在项目根运行，或以脚本位置推导项目根），勿相对 yaml 所在目录（cache/data/）解析【v1.1: RIG-003 / HG-SEC-056】
3. F3 校验：countries 每条 country_zh 必须在 json 行存在；任一缺失 → 打印缺失键清单，exit 1，不写任何文件
4. 逐条计算增量：url（strip）不在该行 videos（缺省 []）url 集合中 → 记为新增；yaml 内部同 url 只取首条
5. G 判定：新增总数为 0 → 打印「所有 videos 均已包含，无需同步」，exit 0，不写任何文件
6. 按 country_zh 分组补充：对新增条目 append 至 json 行 videos（字段缺失先初始化 []）；platform 缺省按 C1 识别
7. W 回写：将 json 全部行的 videos 展平为 countries 平铺列表（含 target 段），按 yaml 格式重建 yaml 文档（duration 带引号、url strip、platform 写 json 现值；无 videos 的行不产生条目）
8. E 重建：subprocess 调 html-gen.py table，列表参数、无 shell（target 路径来自 yaml，禁 shell=True / 字符串拼接，防命令注入面）：
   `subprocess.run([sys.executable 或 python3, 'html-gen.py', 'table', '-d', target.data, '-o', target.html], shell=False)`
   （无 --title，标题由 json 顶层 title 兜底，已实测与现产物一致；target.data / target.html 路径按 step 2 以项目根为基准解析）【v1.1: RIG-002 / HG-SEC-055】

### 4.3 输出形态（dry-run）

```
[预览] 新增 2 条:
  - 缅甸: 缅甸-散装缅甸 https://v.douyin.com/-IIdHuXNL0o/ (6:55)
  - 伊朗: 伊朗-美国为什么征服不了伊朗 https://v.douyin.com/1IxN2ag0e8U/ (11:38)
[预览] 将回写 yaml countries 段（全局镜像）+ 重建 demos/countries-table.html
[提示] 使用 --apply 执行
```

## 5. 测试计划

新建 tests/test_sync_videos.py（unittest + subprocess 调脚本，临时目录 fixture 隔离，不依赖 Selenium）：

1. test_01 解析：yaml 规范格式 → target list + countries 平铺；duration 引号 → str("6:55") 非 int(415)
2. test_02 duration 容错：未加引号 duration（int 415）→ 归一化为 "6:55"（容错仅限 M:SS；H:MM:SS 必须引号，int 3723 不在容错语义内）【v1.1: HG-SEC-057】
3. test_03 F3 校验：yaml 含 json 不存在国家键 → exit 1，json/yaml/html 均未修改
4. test_04 全存在中断：yaml 视频均已含于 json → 打印提示 exit 0，无写盘
5. test_05 补充更新：缅甸 0→1、伊朗 1→2（url 去重，同 url 不重复）；附 url strip 断言：yaml url 带尾部空格 → strip 后去重/回写（与既有 url strip 后相同 → 不重复新增；回写 yaml 时 url 已 strip 空白）【v1.1: HG-SEC-059】
6. test_06 yaml 内部重复 url：同国同 url 两条 → 仅取首条
7. test_07 W 回写：apply 后 yaml countries 段 == json 全部 videos（含既有 10 行，target 保留）
8. test_08 platform 兜底：yaml 缺 platform + v.douyin.com → json 补 "douyin"
9. test_09 dry-run 不写盘：json/yaml/html mtime 与内容不变
10. test_10 E 重建：apply 后 html 含新视频标题文本，且 <title> 不变

回归：tests/test_countries_table.py、test_videos.py（videos 数据只增不减，现有断言不受影响）；全量 `python3 -m pytest tests/ -q -n 4`

## 6. 验收清单

1. [ ] cache/data/_countries-data.videos.yaml 规范格式可解析（duration 字符串）
2. [ ] --dry-run 预览输出新增明细与计划，零写盘
3. [ ] --apply 后 json：缅甸 videos 1 条、伊朗 2 条（url 去重）
4. [ ] --apply 后 yaml：countries 段全局镜像 == json 全部 videos
5. [ ] --apply 后 html：含新视频，<title> 与现产物一致
6. [ ] 二次运行 → 「所有 videos 均已包含」中断
7. [ ] 缺失国家键 → exit 1 且零写盘
8. [ ] test_sync_videos.py 10 用例 + 回归全绿

## 7. 风险与边界

- duration 60 进制坑：结构化 YAML 未引号时长解析为整数；脚本对 int 容错归一化（仅支持 M:SS，H:MM:SS 必须引号）+ 回写恒带引号【v1.1: HG-SEC-057】
- url 空白：尾部空白导致去重失效；解析与比较均 strip
- 写盘安全：F3 与 G 判定均先于任何写盘；dry-run 为默认态
- B1 语义：yaml 仅本地草稿（gitignored），不入 commit；入库的是 json + html 产物
- 脚本名拼写：v1.1 已将 vides 修正为 videos（新建文件零迁移成本，全文档与 draft 同步）【v1.1: HG-SEC-058】
- 依赖面：pyyaml 仅 requirements-dev.txt（dev 环境），运行时 html-gen 零依赖不受影响
- 幂等：url 去重 + G 中断，重复运行结果稳定

## 8. 修订记录

- v1.0 (2026-08-28)：初始设计（HTML-GEN-CL002），探讨确认 A1 B1 C1 D1 E2 F3 W1；评审 CONDITIONAL 85/B（24b9cbc，HG-SEC-054..060）
- v1.1 (2026-08-29)：评审修正 —— RIG-001（§4.2 step1 `yaml.safe_load`）/ RIG-002（§4.2 step8 subprocess 列表参数无 shell）/ RIG-003（§4.2 step2 路径解析以项目根为基准）；🟢 HG-SEC-057（duration 容错仅 M:SS，§2/§5 test_02/§7）、HG-SEC-058（脚本名 → tool-table-videos-syncer.py，§2/§4.1/§7）、HG-SEC-059（§5 test_05 增 url strip 断言）、HG-SEC-060（§1 134KB → 131.7KB）
- v1.1 追加（2026-08-29 审计后）：FIND-001 登记 —— 0deaf5c 混入工作区既有列配置变更（6 列 initialHidden 含 videos + 4 列 splitFull + note preview 反转），非 CL002 设计范围、与 drama WIP 同源；用户确认为有意保留，随 CL002 推送，影响：countries-table 默认隐藏 6 列（⚙️ 可开启/分栏全列渲染不受影响）；FIND-002 —— E 重建丢 github-corner，修复：E 命令自动提取旧产物 corner URL 透传 --github-url（0af421d + test_10 断言）
