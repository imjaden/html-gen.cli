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

  <section>
    <div class="sec-head">
      <span class="no">01</span><h2>七日节奏 · 打开就知道今天练什么</h2>
      <span class="hint">跑量 30 km/周 · 力量 4 次 · 核心每天 5 分钟</span>
    </div>
    <div class="toolbar">
      <button class="btn primary" id="btnEdit">✏️ 编辑方案</button>
      <button class="btn" id="btnShare">🔗 分享链接</button>
      <button class="btn" id="btnPrint">🖨 打印</button>
      <span class="spacer"></span>
      <span class="note" id="stateNote"></span>
    </div>
    <div class="week-grid" id="weekRow"></div>
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


  <footer class="foot">
    <div>slimdown · 训练方案 {{VERSION}} · {{UPDATED}}</div>
    <div><a href="exercises.html">动作库</a> · <a href="archive.html">档案</a> · 主版本 +1 / 次版本 +0.1</div>
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
