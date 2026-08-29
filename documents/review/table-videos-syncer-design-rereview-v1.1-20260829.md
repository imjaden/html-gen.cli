# table-videos-syncer 设计复审报告 v1.1

> 复审对象: `documents/solutions/table-videos-syncer-design-v1.1-20260829.md`（commit `431c1df`，git mv 自 v1.0 保留历史）
> 初审: v1.0 CONDITIONAL PASS 85/B（commit `24b9cbc`，HG-SEC-054..060）
> 闭环: HTML-GEN-CL002 ｜ 前置: HTML-GEN-CL001（videos 字段，已闭环）
> 复审日期: 2026-08-29 ｜ 复审者: Security Reviewer（L2 design-document-review）

---

## 一、结论

**✅ PASS 95/100（A）— 闭环，生成 dev 实施 prompt**

| 维度 | v1.0 | v1.1 复审 |
|:---|:---:|:---:|
| 合理性 Reasonableness | 🟢 | 🟢（无变化） |
| 严格性 Rigor | 🟡（3 项） | 🟢（RIG-003 闭合；1 新 🟡 HG-SEC-061 阈值矛盾） |
| 安全性 Security | 🟡（2 项） | 🟢（RIG-001/002 闭合） |

- 评分: 100 − 1×5（HG-SEC-061 🟡）= **95**
- Findings: **0 🔴 / 1 🟡（HG-SEC-061 新发现）/ 0 🟢 残留**（HG-SEC-054..060 全部 closed）
- 3 个 🟡 RIG（054/055/056）+ 4 个 🟢（057..060）全部落地；唯一新发现 HG-SEC-061 为「duration int 容错阈值边界」规格矛盾，非安全面，fold 入 dev 实施 prompt（dev 用正确阈值 `<3600`）一并订正文档，不阻断闭环。

---

## 二、RIG 逐项核验（复审核对项 1-3）

| RIG | HG-SEC | 要求（v1.0） | v1.1 落点 | 核验 |
|:---|:---|:---|:---|:---:|
| RIG-001 | 054 | §4.2 step1 pin `yaml.safe_load`（禁 yaml.load/FullLoader） | §4.2 step1 显式「必须用 `yaml.safe_load`；禁用 yaml.load / FullLoader，防 `!!python/object` 任意代码执行」 | ✅ |
| RIG-002 | 055 | §4.2 step8 subprocess list-form + shell=False | §4.2 step8 显式 `subprocess.run([sys.executable 或 python3, 'html-gen.py', 'table', '-d', target.data, '-o', target.html], shell=False)`，禁 shell=True / 字符串拼接 | ✅ |
| RIG-003 | 056 | §4.2 step2 相对路径以项目根为基准（勿相对 cache/data/） | §4.2 step2 补「一律以项目根为基准解析（脚本须在项目根运行，或以脚本位置推导项目根），勿相对 yaml 所在目录（cache/data/）解析」；step8 引用「按 step 2 以项目根为基准解析」覆盖重建路径 | ✅ |

3/3 RIG 均一句话级补齐，措辞精确覆盖初审要求，无遗漏、无漂移。

## 三、🟢 落地核验（复审核对项 4）

| HG-SEC | 要求 | v1.1 落点 | 核验 |
|:---|:---|:---|:---:|
| 057 | duration int 容错仅 M:SS + H:MM:SS 必须引号（§2/§5 test_02/§7 三处同步） | §2 补充规格 + §5 test_02 + §7 均同步「仅 M:SS；H:MM:SS 必须引号」 | ✅（⚠️ 阈值矛盾 → HG-SEC-061，见 §四） |
| 058 | 脚本名 vides→tool-table-videos-syncer.py（§2/§4.1/§7 + draft 同步） | §2/§4.1/§7 全改 videos；TODO draft「tool-table-videos-syncer.py」 | ✅（全文无残留 vides 脚本名，仅解释性描述「原 vides 拼写错误」） |
| 059 | §5 test_05 增 url 尾部空格 strip 断言（保持 10 用例） | test_05 附「url 带尾部空格 → strip 后去重/回写」断言，用例数仍 10 | ✅ |
| 060 | §1 134KB→131.7KB 实测值 | §1「131.7KB/195 行，实测 2026-08-29」 | ✅（全文无 134KB 残留） |

## 四、新发现 HG-SEC-061（🟡）

**duration int 容错阈值 `<6000` 与「3723 不在容错语义」自相矛盾。**

§2 补充规格（HG-SEC-057 落地时引入）：
- 「未引号 int < 6000 按秒数归一化，如 415 → "6:55"」
- 「H:MM:SS 必须引号包裹（未引号 3723 不在容错语义内）」

3723 < 6000，故按前句 3723 应被归一化，但后句断言其「不在容错语义内」——两句互斥。根因：M:SS 上界为 59:59 = 3599s，正确阈值应为 **`< 3600`**（而非 `< 6000`）。

- **位置**: §2（补充规格 duration 行）
- **严重度**: 🟡（严格性；自相矛盾规格，dev 实现 test_02 时对边界输入 3600–5999 无确定语义）
- **修法**: §2 阈值 `6000` → `3600`（或 `≤ 3599`）；dev 实施 prompt 已按 `< 3600` 下发，实现不受影响
- **处置**: fold 入 dev 实施 prompt（随 CL002 实施一并订正文档），非安全面，不阻断闭环

## 五、验收清单 §6 可执行性（复审核对项 5）

8 项验收均保留，与 test_sync_videos 10 用例 + 回归面 1:1 映射无漂移（沿用 v1.0 报告 §三/§四 完备性）：

| # | 验收项 | 测试 | 可执行 |
|:-:|:---|:---|:---:|
| 1 | yaml 规范格式可解析（duration 字符串） | test_01/02 | ✅ |
| 2 | --dry-run 预览 + 零写盘 | test_09 | ✅ |
| 3 | --apply 后缅甸 1 条 / 伊朗 2 条（url 去重） | test_05 | ✅ |
| 4 | --apply 后 yaml 全局镜像 == json 全部 videos | test_07 | ✅ |
| 5 | --apply 后 html 含新视频 + title 不变 | test_10 | ✅ |
| 6 | 二次运行 → 中断 | test_04 | ✅ |
| 7 | 缺失国家键 → exit 1 零写盘 | test_03 | ✅ |
| 8 | test_sync_videos 10 用例 + 回归全绿 | 全量 | ✅ |

8/8 可执行，无「验收有、测试无」或「测试有、验收无」悬空项。

## 六、评分

100 − 1×5（HG-SEC-061 🟡）= **95** → A（≥85）→ **PASS**

## 七、验证线索

| 验证项 | 结果 |
|:---|:---|
| commit 范围 | `git show 431c1df --stat` → 1 file changed, 18 insertions(+), 14 deletions(-)（rename v1.0→v1.1，相似度 69%）✓ |
| 历史保留 | `git log --follow --oneline` → 24b9cbc + 431c1df（git mv 保留历史）✓ |
| 残留扫描 | grep `vides`/`134KB`/`yaml.load(`/`FullLoader`/`shell=True` → 命中均为解释性/否定语境，无残留 ✓ |
| draft 同步 | TODO-20260829.md L11 已为 `tool-table-videos-syncer.py` ✓ |
| verify 说明 | verify-review-level.py 词表漂移为已知误报来源（exit=1 不代表本次缺陷）；以 yaml.safe_load + tracking 连续性 + findings_open 字段核对为准 |

## 八、结论与后续

PASS 95/A。RIG-001/002/003（HG-SEC-054/055/056）+ 🟢 057..060 全部落地；唯一新发现 HG-SEC-061（duration 阈值 `<6000`→`<3600`）为规格精度矛盾，fold 入 dev 实施 prompt 一并订正。生成 dev 实施 prompt（`cache/review-prep/prompt-table-videos-syncer-dev-20260829.md`）转 dev；本次复审 auto-push（github/main），工作树 4 个未提交 data/demo 文件属 dev 基线，不随 review 提交。
