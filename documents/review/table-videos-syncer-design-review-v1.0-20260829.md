# table-videos-syncer 设计评审报告 v1.0

> 评审对象: `documents/solutions/table-videos-syncer-design-v1.0-20260828.md`（commit `24b9cbc`）
> 闭环: HTML-GEN-CL002 ｜ 前置: HTML-GEN-CL001（videos 字段，已闭环）
> 评审日期: 2026-08-29 ｜ 评审者: Security Reviewer（L2 design-document-review）

---

## 一、结论

**⚠️ CONDITIONAL PASS 85/100（B）— 非 PASS，不生成 dev 实施 prompt**

| 维度 | 评级 | 结论 |
|:---|:---:|:---|
| 合理性 Reasonableness | 🟢 | 架构合理，决策闭环，复用既有基础设施 |
| 严格性 Rigor | 🟡 | 3 项待补（路径解析基准 / duration H:MM:SS 归一化 / url strip 用例） |
| 安全性 Security | 🟡 | 2 项待 pin（`yaml.safe_load` / subprocess list-form） |

- 评分: 100 − 3×5（🟡）= **85**
- Findings: **0 🔴 / 3 🟡 / 4 🟢**（HG-SEC-054..060）
- 阻断性: 无 🔴；3 个 🟡 均为「安全/严格性规格一句话补齐」级，非架构缺陷。因任务 gate「结论 PASS 才可进入 dev 实施」且 🟡 未 closed，按项目先例（CL001 v1.0 同为 CONDITIONAL 85/B）判 **CONDITIONAL PASS**，ops 修 v1.1 后复审转 PASS。

---

## 二、决策追踪（A/B/C/D/E/F/G/W 全 8 项）

| 决策 | 内容 | § 对应 | 验收映射 | 追踪状态 |
|:---|:---|:---|:---|:---:|
| A | 结构化 map，字段与 json 一致（五字段平铺） | §2/§3 | §6.1 yaml 可解析 | ✅ 与 yaml 草稿实测一致 |
| B | yaml 留 cache/ 不入库（gitignored） | §2/§7 | — | ✅ `.gitignore` L27 `cache/` 确认 |
| C | platform URL host 自动识别兜底 | §2/§3/§4.2-6 | §6.3（伊朗/缅甸 platform） | ✅ 产物值 douyin/bilibili/youtube 模板可识别 |
| D | PyYAML 入 requirements-dev.txt | §2 | — | ✅ 与运行时零依赖（pyproject 无 dependencies）不冲突 |
| E | 同步后 subprocess 重建 demos | §2/§4.2-8 | §6.5 html 含新视频+title 不变 | ✅ 命令实测可复现（见 §八） |
| F | 国家键无匹配 → exit 1 零写盘 | §2/§4.2-3 | §6.7 缺失键 exit 1 | ✅ 校验先于任何写盘 |
| G | 无增量 → 幂等中断 exit 0 | §2/§4.2-5 | §6.6 二次运行中断 | ✅ 去重后全存在即断 |
| W | 全局镜像回写 yaml（target 段保留） | §2/§4.2-7 | §6.4 yaml == json 全部 videos | ✅ 无 videos 行不产生条目 |

8/8 决策均与 §1 需求、§6 验收清单逐项对应，无悬空决策、无未验收决策。

---

## 三、SC 完备性（验收清单 §6 8 项 → 测试映射）

| # | 验收项 | 对应测试 | 完备性 |
|:-:|:---|:---|:---:|
| 1 | yaml 规范格式可解析（duration 字符串） | test_01/02 | ✅ |
| 2 | --dry-run 预览 + 零写盘 | test_09 | ✅ |
| 3 | --apply 后 json 缅甸 1 条、伊朗 2 条（url 去重） | test_05 | ✅（实测缅甸 0、伊朗 1 基线成立） |
| 4 | --apply 后 yaml countries 段全局镜像 == json | test_07 | ✅ |
| 5 | --apply 后 html 含新视频 + title 一致 | test_10 | ✅ |
| 6 | 二次运行 → 中断 | test_04 | ✅ |
| 7 | 缺失国家键 → exit 1 零写盘 | test_03 | ✅ |
| 8 | test_sync_videos 10 用例 + 回归全绿 | 全量 | ✅ |

8/8 验收项均有对应测试，无「验收有、测试无」或「测试有、验收无」的悬空项。

---

## 四、TC 完备性（test_01..10 逐条）

| 用例 | 目标 | 覆盖决策 | 可验收性 |
|:---|:---|:---|:---:|
| test_01 | yaml 解析 + duration 引号 → str 非 int | A + duration 坑 | ✅ |
| test_02 | duration int 容错归一化（415→"6:55"） | duration 坑 | ✅（仅 M:SS，见 HG-SEC-057） |
| test_03 | F3 校验缺失键 exit 1 零写盘 | F | ✅ |
| test_04 | 全存在中断 exit 0 零写盘 | G | ✅ |
| test_05 | 补充更新缅甸 0→1、伊朗 1→2 + url 去重 | 核心 additive + dedup | ✅ |
| test_06 | yaml 内部重复 url 取首条 | dedup | ✅ |
| test_07 | W 回写镜像（含既有 10 行 + target 保留） | W | ✅ |
| test_08 | platform 兜底（缺省 + v.douyin.com → douyin） | C | ✅ |
| test_09 | dry-run 零写盘（mtime+内容不变） | dry-run | ✅ |
| test_10 | E 重建（html 含标题 + title 不变） | E | ✅ |

10 用例覆盖 8 决策中的 7 个（B「cache/ 存放」与 D「PyYAML」为环境/依赖面，无行为可测，合理豁免）。测试形态 unittest + subprocess + 临时目录 fixture、不依赖 Selenium，符合「新测试非 Selenium」设计意图。

---

## 五、三轴评估

### 合理性 🟢

- yaml 增量 → json 事实源 → yaml 全局镜像 → 重建 demos 的四段式数据流清晰，职责单一。
- additive-only 语义（只 append 不删除不覆盖）+ G 幂等 + F 校验先行，三者共同保证写盘安全，无需回滚逻辑。
- 复用既有 `html-gen.py table` 命令（E）与 videos 列渲染（CL001 前置），无重复造轮子。
- B（yaml 留 cache/ gitignored）正确隔离「手写草稿」与「入库产物」。

### 严格性 🟡

- ✅ duration 60 进制坑实测确认（`yaml.safe_load('6:55')` → `415` int，`11:38` → `698`），设计 §3 断言精确。
- ✅ url strip 去重、F3/G 先于写盘、dry-run 默认态——边界覆盖充分。
- 🟡 HG-SEC-056: target.data/html 相对路径解析基准未定义（见 §六）。
- 🟢 HG-SEC-057: duration int 归一化仅明确 M:SS，H:MM:SS 未指定（见 §六）。

### 安全性 🟡

- ✅ 无凭据、无网络面、无外部输入（yaml 为本地可信草稿）。
- ✅ E 重建产物 html-gen table 沿用 CL001 已审计的 noopener,noreferrer + escapeHtml 转义。
- 🟡 HG-SEC-054: `yaml.safe_load` 未显式指定（见 §六）。
- 🟡 HG-SEC-055: subprocess list-form 未显式指定（见 §六）。

---

## 六、修改建议（Findings）

| # | Severity | Title | 位置 | 修法 |
|:--:|:---:|:---|:---|:---|
| HG-SEC-054 | 🟡 | yaml 解析未 pin `yaml.safe_load` | §4.2 step 1「解析 yaml（PyYAML）」 | 明确 `yaml.safe_load`（禁 `yaml.load`/`FullLoader`，防 `!!python/object` 任意代码执行）。本地草稿缓解但 spec 应显式 |
| HG-SEC-055 | 🟡 | subprocess 未 pin list-form args | §4.2 step 8「subprocess 调 …」 | 明确 `subprocess.run([...], shell=False)` 列表参数，禁 shell=True/字符串拼接（target 路径来自 yaml，防命令注入面） |
| HG-SEC-056 | 🟡 | target.data/html 相对路径解析基准未定义 | §4.2 step 2/8 | 明确 CWD 契约：脚本固定以项目根为基准解析 `data/…`、`demos/…` 与 `html-gen.py`（勿相对 yaml 目录 cache/data/） |
| HG-SEC-057 | 🟢 | duration int 归一化仅覆盖 M:SS | §7 + test_02 | 补充 H:MM:SS 归一化规则（如 3723 → "1:02:03"），或显式声明「int 容错仅支持 M:SS，H:MM:SS 必须引号」 |
| HG-SEC-058 | 🟢 | 脚本名 `vides` 拼写错误 | §2 补充规格 | 新建文件零迁移成本，建议直接命名 `tool-table-videos-syncer.py`（避免永久拼写债）；如坚持保留则保留现说明 |
| HG-SEC-059 | 🟢 | url 尾部空白 strip 无显式用例 | §5 | test_05/06 增一条「url 带尾部空格 → strip 后去重/回写」断言，闭合 §7 已列风险 |
| HG-SEC-060 | 🟢 | §1 背景「134KB」已漂移 | §1 | 工作树未提交 restructure 后实际 131.7KB（非 spec 载荷，随正文更新即可） |

**RIG 清单（ops 修 v1.1，全部 Bucket A 一句话补齐）**:

| # | 项 | 修复 |
|:-:|:---|:---|
| RIG-001 | §4.2 step 1 | `解析 yaml（PyYAML，safe_load）` |
| RIG-002 | §4.2 step 8 | `subprocess.run([sys.executable 或 python3, 'html-gen.py', 'table', '-d', target.data, '-o', target.html])` 列表参数，无 shell |
| RIG-003 | §4.2 step 2 | 补一行「相对路径以项目根为基准解析（脚本须在项目根运行或以脚本位置推导项目根）」 |

---

## 七、待确认清单

- □ HG-SEC-058 脚本名是否坚持 `vides` 拼写（推荐直接 `videos`）—— Reasonableness
- □ HG-SEC-057 duration H:MM:SS 是补归一化规则还是显式声明「仅 M:SS 容错」—— Rigor
- □ 工作树当前有 4 个未提交文件（data/_countries-data.json 列重构 + drama history-strategy videos 列 + 两个 demos 产物），dev 实施 --apply 前需先界定基线（先提交或确认 syncer 基于当前工作树运行）—— Process

---

## 八、实测证据

| 验证项 | 命令/来源 | 结果 |
|:---|:---|:---|
| E 命令可复现 | `python3 html-gen.py table -d data/_countries-data.json -o /tmp/cl002-repro.html` | ✅ 生成成功，195 行 × 18 列 · 6 标签页 |
| title 兜底 | 产物 `<title>` | ✅ `全球国家速查表（195 国）` == JSON 顶层 title（cmd_table L424 无 --title 时取 json_title） |
| duration 60 进制坑 | `yaml.safe_load('6:55')` / `('11:38')` | ✅ 415 / 698（int），设计断言精确 |
| 缅甸基线 | data/_countries-data.json L3170 | ✅ `country_zh: 缅甸` 无 videos 字段（0 条） |
| 伊朗基线 | data/_countries-data.json L470 | ✅ 伊朗 1 条「中东为何永不团结」（v.douyin.com/Ez_SJIkymk0/） |
| 既有 videos 行数 | grep `"videos"` | ✅ 10 行带 videos（§1「已有 10 行」成立） |
| yaml 草稿存在 | cache/data/_countries-data.videos.yaml | ✅ 与设计 §3 示例逐字一致（缅甸 1 + 伊朗 1，url 与 json 伊朗既有 url 不同 → 1→2 成立） |
| videos 列渲染 | layout-table.html L636-685 | ✅ col.type="videos" + VIDEO_PLATFORM_ICONS + maxShow 折叠 + noopener,noreferrer |
| platform 识别一致性 | 设计 C（v.douyin→douyin/bilibili/youtube|youtu.be→youtube）vs 模板图标表 | ✅ 同步器输出 douyin/bilibili/youtube 均为模板可识别值 |
| 回归面安全 | test_countries_table.py 14 用例 / test_videos.py 8 用例 | ✅ 无列数/videos 硬断言；videos 增不减不改 195 行计数/tab 计数/region pills |
| 前置 CL001 衔接 | table-videos-design-v1.1 §3/§5 | ✅ yaml 字段（country_zh/title/url/duration/platform）与 CL001 videos 对象字段一致 |

---

## 九、结论与后续

CONDITIONAL PASS 85/B。设计整体合理、决策闭环、测试可验收，无 🔴；3 个 🟡（HG-SEC-054/055/056）为安全/严格性规格一句话补齐，4 个 🟢 记录。ops 修 v1.1 后复审，PASS 后生成 dev 实施 prompt 转 dev。
