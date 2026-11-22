<!DOCTYPE html>
<html lang="zh-CN" data-theme="ember">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{{TITLE}}</title>
<link rel="icon" href="https://www.jaden.tech/static/img/favicon.png" type="image/png">
<style>{{CSS}}</style>
</head>
<body>

<div class="theme-bar">
  <span class="ic" aria-hidden="true">🎨</span>
  <select id="themeSel" aria-label="主题色"></select>
</div>

<div class="sheet" id="sheet">
  <header class="masthead">
    <div class="kicker">SLIMDOWN · 7-DAY PLAN</div>
    <h1>薄肌减脂 · 七日方案</h1>
    <div class="sub">今天练什么，一眼看懂</div>
  </header>

  <div id="weekRow" aria-label="七日训练方案"></div>

  <footer class="foot">
    <div>slimdown · {{VERSION}} · {{UPDATED}}</div>
    <div><a href="exercises.html">动作库</a> · <a href="archive.html">档案</a> · 右下角可编辑 / 存图</div>
  </footer>
</div>

<div class="fab-group">
  <button class="fab" id="fabEdit" type="button" title="编辑方案" aria-label="编辑方案">✎</button>
  <button class="fab" id="fabShot" type="button" title="保存图片" aria-label="保存图片">⤓</button>
</div>

<div class="panel-mask" id="panelMask">
  <div class="panel" role="dialog" aria-modal="true" aria-labelledby="panelTitle">
    <div class="p-head">
      <h2 id="panelTitle">训练方案</h2>
      <div class="p-seg" id="panelSeg">
        <button type="button" data-view="edit" class="on">编辑方案</button>
        <button type="button" data-view="prev">预览方案图片</button>
      </div>
      <button class="p-x" id="panelClose" type="button" aria-label="关闭">×</button>
    </div>

    <div class="p-tabs" id="panelTabs" role="tablist"></div>

    <div class="p-body">
      <div class="view on" id="viewEdit">
        <div class="edit-grid">
          <div class="picker">
            <div class="p-tools">
              <input type="search" id="exSearch" placeholder="搜动作 / 别名">
              <div id="exChips" style="display:flex;gap:5px;flex-wrap:wrap"></div>
            </div>
            <ul id="exList"></ul>
          </div>
          <div class="plan-box">
            <div class="p-head2">
              <b id="editDayLabel">周一</b>
              <span class="note" id="editDaySum"></span>
              <span style="flex:1"></span>
              <button class="btn mini" id="btnResetDay" type="button">还原本日</button>
              <button class="btn mini" id="btnLoadDefault" type="button">还原全部</button>
            </div>
            <div id="planList"></div>
          </div>
        </div>
      </div>

      <div class="view" id="viewPrev">
        <div class="preview-host" id="previewHost"></div>
      </div>
    </div>

    <div class="p-foot">
      <span class="p-note" id="panelNote"></span>
      <div class="p-links">
        <button class="p-link" id="btnShare" type="button">分享链接</button>
        <button class="p-link" id="btnCopyImg" type="button">复制图片</button>
        <button class="p-link" id="btnPrint" type="button">打印</button>
      </div>
      <div class="p-actions">
        <button class="p-btn primary" id="btnSavePlan" type="button">保存方案</button>
        <button class="p-btn" id="btnDownloadImg" type="button" disabled>下载图片</button>
      </div>
    </div>
  </div>
</div>

<div class="mask" id="shareMask">
  <div class="share-panel">
    <h2>分享这套方案</h2>
    <div class="note">链接里带的是当前这份方案（不含任何个人数据），对方打开即可查看并另存。</div>
    <textarea id="shareUrl" readonly></textarea>
    <div class="row">
      <button class="btn" id="btnCopyUrl" type="button">复制链接</button>
      <button class="btn" id="btnCopyText" type="button">复制纯文本</button>
      <button class="btn" id="btnCloseShare" type="button">关闭</button>
      <span class="spacer" style="flex:1"></span>
      <span class="note" id="shareLen"></span>
    </div>
  </div>
</div>

<script>window.SLIMDOWN = {{DATA}};</script>
<script>{{JS}}</script>
</body>
</html>
