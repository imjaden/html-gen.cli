#!/usr/bin/env python3
"""provinces-match.py — 中国省份 ↔ 全球国家 面积/人口/GDP 相近关联匹配草稿生成器。

设计依据: documents/solutions/provinces-table-design-v1.1-20260824.md §三/§四
- 国家侧归一化: area_km2 ÷ 10000 → 万km²; gdp_yi × 7.08 → 亿元 (2023 年均汇率, 国家统计局口径)
- 阈值: 面积 |Δ|≤30% / 人口 ≤20% / GDP ≤30% (相对省份值)
- 每项取 2-3 个 (|Δ| 升序 + 人工复核兜底)
- None 防护: 6 国缺 gdp_yi (也门/南苏丹/厄立特里亚/古巴/朝鲜/梵蒂冈), 梵蒂冈全缺 → 该维度跳过
- 双向: 省份表为基准一次计算, 国家表 3 列反向回填同对
输出: data/_provinces-source.json (草稿, 不入 git, dev 实施中间产物)
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FX = 7.08  # 2023 年均汇率 人民币/美元

# 34 省级行政区基础数据 (ops 整理 2026-08-24, 待复核)
# 面积=官方国土面积(万km²); 人口=七普2020(万); GDP=2023年(亿元, 港澳台按汇率折算)
PROVINCES = [
    # province, abbr, capital, region, area_wan, pop_wan, gdp_yi
    ("北京", "京", "北京", "华北", 1.64, 2189, 43761),
    ("天津", "津", "天津", "华北", 1.19, 1387, 16737),
    ("河北", "冀", "石家庄", "华北", 18.88, 7461, 43944),
    ("山西", "晋", "太原", "华北", 15.67, 3480, 25698),
    ("内蒙古", "蒙", "呼和浩特", "华北", 118.30, 2405, 24627),
    ("辽宁", "辽", "沈阳", "东北", 14.80, 4259, 30209),
    ("吉林", "吉", "长春", "东北", 18.74, 2407, 13531),
    ("黑龙江", "黑", "哈尔滨", "东北", 47.30, 3185, 15884),
    ("上海", "沪", "上海", "华东", 0.63, 2487, 47219),
    ("江苏", "苏", "南京", "华东", 10.72, 8475, 128222),
    ("浙江", "浙", "杭州", "华东", 10.55, 6457, 82553),
    ("安徽", "皖", "合肥", "华东", 14.01, 6103, 47051),
    ("福建", "闽", "福州", "华东", 12.40, 4154, 54355),
    ("江西", "赣", "南昌", "华东", 16.69, 4519, 32200),
    ("山东", "鲁", "济南", "华东", 15.58, 10153, 92069),
    ("河南", "豫", "郑州", "华中", 16.70, 9937, 59132),
    ("湖北", "鄂", "武汉", "华中", 18.59, 5775, 55804),
    ("湖南", "湘", "长沙", "华中", 21.18, 6644, 50013),
    ("广东", "粤", "广州", "华南", 17.97, 12601, 135673),
    ("广西", "桂", "南宁", "华南", 23.76, 5013, 27202),
    ("海南", "琼", "海口", "华南", 3.54, 1008, 7551),
    ("香港", "港", "—", "华南", 0.11, 748, 27200),
    ("澳门", "澳", "—", "华南", 0.0033, 68, 3340),
    ("台湾", "台", "台北", "华南", 3.60, 2357, 54200),
    ("重庆", "渝", "重庆", "西南", 8.24, 3205, 30146),
    ("四川", "川", "成都", "西南", 48.60, 8367, 60133),
    ("贵州", "黔", "贵阳", "西南", 17.62, 3856, 20913),
    ("云南", "滇", "昆明", "西南", 39.40, 4720, 30021),
    ("西藏", "藏", "拉萨", "西南", 122.84, 365, 2393),
    ("陕西", "陕", "西安", "西北", 20.56, 3953, 33786),
    ("甘肃", "甘", "兰州", "西北", 45.37, 2502, 11864),
    ("青海", "青", "西宁", "西北", 72.23, 592, 3799),
    ("宁夏", "宁", "银川", "西北", 6.64, 720, 5315),
    ("新疆", "新", "乌鲁木齐", "西北", 166.49, 2585, 19125),
]

# 阈值: (面积, 人口, GDP)
THRESHOLDS = {"area": 0.30, "pop": 0.20, "gdp": 0.30}
MAX_HITS = 3
MIN_HITS = 1

# 6 国缺 gdp_yi (全表扫描确认, 不参与 GDP 维度)
GPD_MISSING = {"也门", "南苏丹", "厄立特里亚", "古巴", "朝鲜", "梵蒂冈"}


def load_countries():
    d = json.loads((ROOT / "data/_countries-data.json").read_text())
    rows = []
    for r in d["data"]:
        rows.append({
            "name": r["country_zh"],
            "area_wan": r.get("area_km2") / 10000 if r.get("area_km2") else None,
            "pop_wan": r.get("pop_wan"),
            "gdp_yi": r.get("gdp_yi") * FX if r.get("gdp_yi") else None,
        })
    return rows


def pick_hits(prov_value, countries, key, threshold):
    """以省份值为基准, |Δ| ≤ 阈值, 按 |Δ| 升序取前 MAX_HITS."""
    hits = []
    for c in countries:
        cv = c[key]
        if cv is None or prov_value is None:
            continue
        if cv == 0:
            continue
        delta = abs(cv - prov_value) / prov_value
        if delta <= threshold:
            hits.append((delta, c["name"]))
    hits.sort(key=lambda x: x[0])
    return [h[1] for h in hits[:MAX_HITS]]


def main():
    countries = load_countries()
    src = {"provinces": [], "countries_backfill": {}}

    for p in PROVINCES:
        name, abbr, capital, region, area, pop, gdp = p
        area_hits = pick_hits(area, countries, "area_wan", THRESHOLDS["area"])
        pop_hits = pick_hits(pop, countries, "pop_wan", THRESHOLDS["pop"])
        gdp_hits = pick_hits(gdp, countries, "gdp_yi", THRESHOLDS["gdp"])
        src["provinces"].append({
            "province": name, "abbr": abbr, "capital": capital,
            "region": region, "area_wan": area, "pop_wan": pop, "gdp_yi": gdp,
            "area_country": area_hits, "pop_country": pop_hits, "gdp_country": gdp_hits,
        })

    # 反向回填: 国家表 3 列 = 省份表同对回填 (设计 §四 5: 单方向匹配一次 + 反向回填同对)
    # 收集省份表中引用每个国家的省份, 按 |Δ|(国家视角, 以国家值为基准) 排序取前 3
    country_map = {c["name"]: c for c in countries}
    backfill = {c["name"]: {"area_province": [], "pop_province": [], "gdp_province": []}
                for c in countries}
    for p in src["provinces"]:
        pv = {"area": p["area_wan"], "pop": p["pop_wan"], "gdp": p["gdp_yi"]}
        for dim, pc, cp in [("area", "area_country", "area_province"),
                            ("pop", "pop_country", "pop_province"),
                            ("gdp", "gdp_country", "gdp_province")]:
            for cname in p[pc]:
                cv = country_map.get(cname, {}).get("area_wan" if dim == "area" else ("pop_wan" if dim == "pop" else "gdp_yi"))
                if cv is None or pv[dim] is None or cv == 0:
                    continue
                delta = abs(cv - pv[dim]) / cv  # 国家视角差值
                backfill[cname][cp].append((delta, p["province"]))
    for cname, cols in backfill.items():
        for cp in ("area_province", "pop_province", "gdp_province"):
            cols[cp].sort(key=lambda x: x[0])
            cols[cp] = [name for _, name in cols[cp][:MAX_HITS]]
    src["countries_backfill"] = backfill

    out = ROOT / "data/_provinces-source.json"
    out.write_text(json.dumps(src, ensure_ascii=False, indent=2))
    print(f"✅ 草稿已生成: {out}")
    print(f"   省份 {len(src['provinces'])} 个 | 国家回填 {len(src['countries_backfill'])} 个")
    empty_area = sum(1 for p in src["provinces"] if not p["area_country"])
    empty_pop = sum(1 for p in src["provinces"] if not p["pop_country"])
    empty_gdp = sum(1 for p in src["provinces"] if not p["gdp_country"])
    print(f"   省份侧留空: 面积 {empty_area} / 人口 {empty_pop} / GDP {empty_gdp} (待人工复核补/留空)")


if __name__ == "__main__":
    main()
