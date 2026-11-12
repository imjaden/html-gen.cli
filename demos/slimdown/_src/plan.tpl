<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{{TITLE}}</title>
<link rel="icon" href="https://www.jaden.tech/static/img/favicon.png" type="image/png">
<style>{{CSS}}</style>
</head>
<body>
<div class="sheet" id="sheet">
  <header class="masthead">
    <h1>薄肌减脂 · 训练方案<span class="thin">slimdown · 七日活动方案</span></h1>
    <div class="tag">版本 {{VERSION}} · {{UPDATED}}<br>《slimdown 案例》</div>
  </header>
  <nav class="case-nav">{{NAV}}</nav>

  <section>
    <div class="sec-head">
      <span class="no">01</span><h2>七日节奏 · 打开就知道今天练什么</h2>
      <span class="hint">跑量 30 km/周 · 力量 4 次 · 核心每天 5 分钟</span>
    </div>
    <div class="toolbar">
      <button class="btn primary" id="btnEdit">✏️ 编辑方案</button>
      <button class="btn" id="btnShare">🔗 分享链接</button>
      <button class="btn" id="btnCardDay">🖼 今日卡片</button>
      <button class="btn" id="btnCardWeek">🗓 整周卡片</button>
      <button class="btn" id="btnPrint">🖨 打印</button>
      <span class="spacer"></span>
      <span class="note" id="stateNote"></span>
    </div>
    <div class="week-grid" id="weekGrid"></div>
  </section>

  <section class="editor" id="editor">
    <div class="editor-head">
      <b style="font-size:13px">编辑</b>
      <div class="day-chips" id="dayChips"></div>
      <span class="spacer" style="flex:1"></span>
      <button class="btn mini" id="btnResetDay">还原本日</button>
      <button class="btn mini" id="btnLoadDefault">还原全部</button>
      <button class="btn mini primary" id="btnSave">保存到本机</button>
      <button class="btn mini" id="btnCloseEdit">收起</button>
    </div>
    <div class="editor-body">
      <div class="picker">
        <div class="p-tools">
          <input type="search" id="exSearch" placeholder="搜动作 / 别名">
          <div class="day-chips" id="exChips"></div>
        </div>
        <ul id="exList"></ul>
      </div>
      <div class="plan-box">
        <div class="p-head">
          <b id="editDayLabel">周一</b>
          <span class="note" id="editDaySum"></span>
          <span style="flex:1"></span>
          <span class="note">组数 / 次数可改，↑↓ 调序</span>
        </div>
        <div id="planList"></div>
      </div>
    </div>
  </section>

  <section>
    <div class="sec-head"><span class="no">02</span><h2>运动量区间 · 时长 / 节奏 / 体感</h2><span class="hint">RPE = 自感用力 0–10</span></div>
    <table>
      <colgroup><col style="width:18%"><col style="width:22%"><col style="width:30%"><col style="width:30%"></colgroup>
      <thead><tr><th>类型</th><th>时长</th><th>节奏</th><th>体感 / RPE</th></tr></thead>
      <tbody>
        <tr><td>热身</td><td>5–8 分</td><td>动态拉伸 + 绕肩 + 猫牛</td><td>微汗、呼吸平稳；RPE 3–4</td></tr>
        <tr><td>力量复合</td><td>每个动作 3–4 组</td><td>向心 1–2 秒 / 离心 2–3 秒</td><td>最后 2 次吃力但动作不变形；RPE 7–8</td></tr>
        <tr><td>力量孤立</td><td>每个动作 3 组</td><td>控制节奏，不借惯性</td><td>目标肌肉烧灼感；RPE 7</td></tr>
        <tr><td>核心</td><td>5–10 分</td><td>动作慢、不憋气</td><td>腹横发力，不腰酸；RPE 6</td></tr>
        <tr><td>轻松跑</td><td>30–60 分</td><td>配速 6:30–7:00</td><td>能整句说话、不喘；心率 109–127；RPE 4–5</td></tr>
        <tr><td>间歇跑</td><td>25–35 分（含热身冷身）</td><td>800 m @5:40 × 6，组间慢跑 400 m</td><td>间歇段喘到说不出整句；RPE 8–9</td></tr>
        <tr><td>壶铃循环</td><td>25–35 分 / 4 轮</td><td>动作间不停，轮间休 90 秒</td><td>出汗但动作不变形；RPE 7–8</td></tr>
        <tr><td>拉伸放松</td><td>5–10 分</td><td>静态拉伸每部位 30 秒</td><td>轻微牵拉感，不痛；RPE 2</td></tr>
      </tbody>
    </table>
  </section>

  <section>
    <div class="sec-head"><span class="no">03</span><h2>一天节奏 · 居家 vs 出勤</h2><span class="hint">窗口 12:30–20:30</span></div>
    <table>
      <colgroup><col style="width:50%"><col style="width:50%"></colgroup>
      <thead><tr><th>居家办公（当前）</th><th>出勤通勤（以后切换）</th></tr></thead>
      <tbody>
        <tr>
          <td>
            <b>06:30 起床</b>：黑咖啡 + 肌酸（0 kcal 不破窗）<br>
            <b>07:00 空腹微出汗</b>：真空腹 + 猫牛 + 绕肩 5–10 分<br>
            <b>12:30 开窗</b>：正餐（蛋白 45 g）<br>
            <b>14:00 餐后</b>：站立办公 + 走动 10 分消食<br>
            <b>16:30 加餐</b>：蛋白 40 g<br>
            <b>18:30 大训练</b>：力量 40–45 分 或 跑 30–60 分<br>
            <b>19:30 练后餐</b>：蛋白 45 g + 主食<br>
            <b>20:30 关窗</b>
          </td>
          <td>
            <b>07:00 起床</b>：空腹 10 分核心（真空腹 + 死虫）<br>
            <b>通勤</b>：提前一站下车快走 15 分<br>
            <b>12:30 开窗</b>：正餐（带饭或公司选轻食）<br>
            <b>13:00 餐后</b>：楼下散步 10–15 分<br>
            <b>工位</b>：每小时起身 2 分（接水 / 拉伸）<br>
            <b>19:00 到家</b>：力量 40 分（周一/三/五）或跑步 30 分（周二/四）<br>
            <b>20:00 练后餐</b>：蛋白 45 g<br>
            <b>20:30 关窗</b>
          </td>
        </tr>
      </tbody>
    </table>
    <p class="note">同日两练（力量 + 5–10 km 跑）：力量压到 ≤30 分钟，只做 2 个复合主项 + 1 个核心；跑在力量后 ≤40 分；间隔 ≥6 小时最优；跑日的力量不算入周 4 次，是补充。</p>
  </section>

  <section>
    <div class="sec-head"><span class="no">04</span><h2>止损线</h2><span class="hint">出现即调整，不硬扛</span></div>
    <p class="warn" style="margin:0 0 6px">{{SAFETY}}</p>
    <p class="note" style="margin:0">周检口径、围度测量 SOP、营养与 FAQ 见 <a href="archive.html">档案</a>；全部动作见 <a href="exercises.html">动作库</a>。</p>
  </section>

  <footer class="foot">
    <div>slimdown · 训练方案 {{VERSION}} · {{UPDATED}}</div>
    <div>主版本 = 结构调整 +1 · 次版本 = 内容增删 +0.1</div>
  </footer>
</div>

<div class="mask" id="shareMask">
  <div class="share-panel">
    <h2>分享这套方案</h2>
    <div class="note">链接里带的是当前这份方案（不含任何个人数据），对方打开即可查看并另存。</div>
    <textarea id="shareUrl" readonly></textarea>
    <div class="row">
      <button class="btn primary" id="btnCopyUrl">复制链接</button>
      <button class="btn" id="btnCopyText">复制纯文本</button>
      <button class="btn ghost" id="btnCloseShare">关闭</button>
      <span class="spacer" style="flex:1"></span>
      <span class="note" id="shareLen"></span>
    </div>
  </div>
</div>

<div class="preview-mask" id="previewMask">
  <div class="preview-inner">
    <div class="preview-bar">
      <button class="btn primary" id="btnCopyImg">📋 复制图片</button>
      <button class="btn" id="btnDownloadImg">⬇️ 下载 PNG</button>
      <button class="btn ghost" id="btnClosePreview">关闭</button>
      <span class="note" id="imgNote" style="align-self:center"></span>
    </div>
    <div class="card-wrap" id="previewHost"></div>
  </div>
</div>

<script>window.SLIMDOWN = {{DATA}};</script>
<script>{{JS}}</script>
</body>
</html>
