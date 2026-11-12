/* slimdown 训练方案页 —— 周视图 / 编辑 / 本机保存 / 分享链接 / 截图卡 / 复制图片 */
(function () {
  'use strict';

  var DATA = window.SLIMDOWN || {};
  var META = DATA.plan || {};
  var EX = (DATA.exercises || []).slice();
  var BYID = {};
  EX.forEach(function (e) { BYID[e.id] = e; });

  var LS_KEY = 'slimdown:v1';
  var DEFAULTS = JSON.parse(JSON.stringify(META.days || []));
  var days = JSON.parse(JSON.stringify(DEFAULTS));
  var activeKey = days.length ? days[0].key : '';
  var dirty = false;
  var shared = false;

  var $ = function (id) { return document.getElementById(id); };
  var esc = function (s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  };
  function showToast(msg) {
    var t = document.getElementById('__toast');
    if (!t) {
      t = document.createElement('div');
      t.id = '__toast';
      t.style.cssText = 'position:fixed;left:50%;bottom:26px;transform:translateX(-50%);' +
        'background:#1B1A17;color:#fff;font-size:12.5px;padding:8px 16px;border-radius:3px;' +
        'opacity:0;transition:opacity .18s;z-index:99;pointer-events:none;max-width:80vw;text-align:center';
      document.body.appendChild(t);
    }
    t.textContent = msg;
    t.style.opacity = '1';
    clearTimeout(t.__t);
    t.__t = setTimeout(function () { t.style.opacity = '0'; }, 1800);
  }
  function todayKey() {
    var map = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat'];
    return map[new Date().getDay()];
  }
  function dayBy(key) {
    for (var i = 0; i < days.length; i++) if (days[i].key === key) return days[i];
    return days[0];
  }
  function sumSets(d) {
    return d.items.reduce(function (n, it) { return n + (parseInt(it.sets, 10) || 0); }, 0);
  }

  /* ── 渲染：周视图 ── */
  function renderWeek() {
    var host = $('weekGrid');
    var tk = todayKey();
    host.innerHTML = days.map(function (d, i) {
      var isToday = d.key === tk;
      var items = d.items.map(function (it) {
        var e = BYID[it.id];
        if (!e) return '';
        return '<li>' + esc(e.name) + ' <b>' + esc(it.sets) + '×' + esc(it.reps) + '</b></li>';
      }).join('');
      return '<div class="day-card' + (isToday ? ' today' : '') + '" data-day="' + esc(d.key) + '">' +
        (isToday ? '<span class="today-chip">今天</span>' : '') +
        '<div class="d-top"><span class="d-label">' + esc(d.short || d.label.slice(-1)) + '</span>' +
        '<h3>' + esc(d.theme) + '</h3></div>' +
        '<div class="d-meta">' + esc(d.label) + ' · ' + esc(d.duration) + '</div>' +
        '<ol>' + (items || '<li class="note">空</li>') + '</ol>' +
        '<div class="d-sum"><span>' + d.items.length + ' 个动作</span><span>共 ' + sumSets(d) + ' 组</span></div>' +
        '</div>';
    }).join('');
    host.querySelectorAll('.day-card').forEach(function (c) {
      c.addEventListener('click', function () { openEditor(c.getAttribute('data-day')); });
    });
    $('stateNote').textContent = shared ? '正在查看分享方案' : (dirty ? '未保存（仅本次浏览器）' : '');
  }

  /* ── 编辑器 ── */
  function openEditor(key) {
    activeKey = key || activeKey;
    $('editor').classList.add('open');
    renderEditor();
    $('editor').scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
  function renderEditor() {
    var d = dayBy(activeKey);
    $('dayChips').innerHTML = days.map(function (x) {
      return '<button class="chip' + (x.key === activeKey ? ' on' : '') + '" data-k="' + esc(x.key) + '">' +
        esc(x.label) + '</button>';
    }).join('');
    $('dayChips').querySelectorAll('.chip').forEach(function (b) {
      b.addEventListener('click', function () { activeKey = b.getAttribute('data-k'); renderEditor(); });
    });
    $('editDayLabel').textContent = d.label + ' · ' + d.theme;
    $('editDaySum').textContent = d.items.length + ' 个动作 / 共 ' + sumSets(d) + ' 组 / ' + d.duration;
    var box = $('planList');
    if (!d.items.length) {
      box.innerHTML = '<div class="plan-empty">这一天还没有动作，从左侧点 + 添加。</div>';
    } else {
      box.innerHTML = d.items.map(function (it, i) {
        var e = BYID[it.id] || { name: '（未知动作 ' + it.id + '）' };
        return '<div class="plan-row">' +
          '<span class="nm" title="' + esc(e.name) + '">' + esc(e.name) + '</span>' +
          '<input data-i="' + i + '" data-k="sets" value="' + esc(it.sets) + '" inputmode="numeric">' +
          '<input data-i="' + i + '" data-k="reps" value="' + esc(it.reps) + '">' +
          '<button class="btn mini" data-act="up" data-i="' + i + '" title="上移">↑</button>' +
          '<button class="btn mini" data-act="del" data-i="' + i + '" title="删除">×</button>' +
          '</div>';
      }).join('');
      box.querySelectorAll('input').forEach(function (inp) {
        inp.addEventListener('change', function () {
          var i = +inp.getAttribute('data-i');
          var k = inp.getAttribute('data-k');
          d.items[i][k] = k === 'sets' ? (parseInt(inp.value, 10) || 0) : inp.value;
          markDirty(); renderWeek(); renderEditor();
        });
      });
      box.querySelectorAll('button[data-act]').forEach(function (b) {
        b.addEventListener('click', function () {
          var i = +b.getAttribute('data-i');
          var act = b.getAttribute('data-act');
          if (act === 'del') d.items.splice(i, 1);
          if (act === 'up' && i > 0) {
            var t = d.items[i - 1]; d.items[i - 1] = d.items[i]; d.items[i] = t;
          }
          markDirty(); renderWeek(); renderEditor();
        });
      });
    }
    renderPicker();
  }

  var exFilter = 'all', exQuery = '';
  function renderPicker() {
    var chips = ['all'].concat(EX.map(function (e) { return e.equip; }).filter(function (v, i, a) { return a.indexOf(v) === i; }));
    $('exChips').innerHTML = chips.map(function (c) {
      return '<button class="chip' + (c === exFilter ? ' on' : '') + '" data-e="' + esc(c) + '">' +
        (c === 'all' ? '全部器材' : esc(c)) + '</button>';
    }).join('');
    $('exChips').querySelectorAll('.chip').forEach(function (b) {
      b.addEventListener('click', function () { exFilter = b.getAttribute('data-e'); renderPicker(); });
    });
    var q = exQuery.toLowerCase();
    var list = EX.filter(function (e) {
      if (exFilter !== 'all' && e.equip !== exFilter) return false;
      if (!q) return true;
      return (e.name + ' ' + (e.alias || '')).toLowerCase().indexOf(q) >= 0;
    });
    var d = dayBy(activeKey);
    var has = {};
    d.items.forEach(function (it) { has[it.id] = true; });
    $('exList').innerHTML = list.map(function (e) {
      return '<li><span class="grow"><b>' + esc(e.name) + '</b>' +
        '<span class="sub"> ' + esc(e.muscle) + ' · ' + esc(e.sets) + '×' + esc(e.reps) + '</span></span>' +
        '<button class="btn mini" data-add="' + esc(e.id) + '"' + (has[e.id] ? ' disabled' : '') + '>+</button></li>';
    }).join('') || '<li class="note" style="padding:10px">没有匹配的动作</li>';
    $('exList').querySelectorAll('button[data-add]').forEach(function (b) {
      b.addEventListener('click', function () {
        var e = BYID[b.getAttribute('data-add')];
        if (!e) return;
        d.items.push({ id: e.id, sets: e.sets, reps: e.reps });
        markDirty(); renderWeek(); renderEditor();
      });
    });
  }
  $('exSearch').addEventListener('input', function () { exQuery = this.value.trim(); renderPicker(); });

  /* ── 状态 ── */
  function markDirty() { dirty = true; shared = false; $('stateNote').textContent = '未保存（仅本次浏览器）'; }
  function saveLocal() {
    try {
      localStorage.setItem(LS_KEY, JSON.stringify({ v: 1, days: days }));
      dirty = false; shared = false;
      $('stateNote').textContent = '已保存到本机';
      showToast('已保存到本机');
      setTimeout(function () { if (!dirty) $('stateNote').textContent = ''; }, 1600);
    } catch (e) { showToast('保存失败：浏览器禁用了本地存储'); }
  }
  function loadLocal() {
    try {
      var raw = localStorage.getItem(LS_KEY);
      if (!raw) return false;
      var o = JSON.parse(raw);
      if (!o || o.v !== 1 || !Array.isArray(o.days) || !o.days.length) return false;
      days = o.days; return true;
    } catch (e) { return false; }
  }
  $('btnSave').addEventListener('click', saveLocal);
  $('btnCloseEdit').addEventListener('click', function () { $('editor').classList.remove('open'); });
  $('btnEdit').addEventListener('click', function () {
    if ($('editor').classList.contains('open')) { $('editor').classList.remove('open'); return; }
    openEditor(todayKey());
  });
  $('btnResetDay').addEventListener('click', function () {
    var d = dayBy(activeKey);
    for (var i = 0; i < DEFAULTS.length; i++) {
      if (DEFAULTS[i].key === d.key) { d.items = JSON.parse(JSON.stringify(DEFAULTS[i].items)); break; }
    }
    markDirty(); renderWeek(); renderEditor();
  });
  $('btnLoadDefault').addEventListener('click', function () {
    if (!confirm('还原成默认的七天方案？本机未保存的改动会丢。')) return;
    days = JSON.parse(JSON.stringify(DEFAULTS));
    try { localStorage.removeItem(LS_KEY); } catch (e) {}
    dirty = false; shared = false;
    renderWeek(); renderEditor(); showToast('已还原默认方案');
  });

  /* ── 分享编码 ──
     格式: v1|1=18*4~8%2D10,19*3~10%2F%E8%85%BF|2=...
     day 从 1 起；动作用库内序号（十进制）；sets*sets~encodeURIComponent(reps) */
  function numOf(id) { return parseInt(String(id).replace(/^ex/, ''), 10); }
  function idOf(n) { return 'ex' + (n < 10 ? '0' + n : String(n)); }
  function encodePlan() {
    return 'v1|' + days.map(function (d, i) {
      return (i + 1) + '=' + d.items.map(function (it) {
        return numOf(it.id) + '*' + (parseInt(it.sets, 10) || 0) + '~' + encodeURIComponent(it.reps);
      }).join(',');
    }).join('|');
  }
  function decodePlan(str) {
    var out = [], unknown = 0;
    var segs = String(str).split('|');
    if (segs[0] !== 'v1') return null;
    segs.slice(1).forEach(function (seg) {
      var p = seg.split('=');
      var d = days[parseInt(p[0], 10) - 1];
      if (!d) return;
      var items = [];
      (p[1] || '').split(',').forEach(function (tok) {
        if (!tok) return;
        var m = /^(\d+)\*(\d+)~(.*)$/.exec(tok);
        if (!m) return;
        var id = idOf(parseInt(m[1], 10));
        if (!BYID[id]) { unknown++; return; }
        items.push({ id: id, sets: parseInt(m[2], 10), reps: decodeURIComponent(m[3]) });
      });
      out.push({ key: d.key, items: items });
    });
    return { days: out, unknown: unknown };
  }
  function buildShareUrl() {
    var base = location.href.split('#')[0];
    return base + '#p=' + encodePlan();
  }
  function planText() {
    var L = ['【' + (META.title || '训练方案') + '】', ''];
    days.forEach(function (d) {
      L.push(d.label + ' · ' + d.theme + '（' + d.duration + '）');
      d.items.forEach(function (it, i) {
        var e = BYID[it.id];
        L.push('  ' + (i + 1) + '. ' + (e ? e.name : it.id) + ' ' + it.sets + '×' + it.reps);
      });
      L.push('');
    });
    if (META.meta) L.push(META.meta.goal + ' · ' + META.meta.steps);
    return L.join('\n');
  }

  $('btnShare').addEventListener('click', function () {
    var url = buildShareUrl();
    $('shareUrl').value = url;
    $('shareLen').textContent = url.length + ' 字符';
    $('shareMask').classList.add('open');
    setTimeout(function () { $('shareUrl').select(); }, 50);
  });
  $('btnCloseShare').addEventListener('click', function () { $('shareMask').classList.remove('open'); });
  $('shareMask').addEventListener('click', function (e) {
    if (e.target === this) this.classList.remove('open');
  });
  $('btnCopyUrl').addEventListener('click', function () {
    copyText(buildShareUrl(), '链接已复制');
  });
  $('btnCopyText').addEventListener('click', function () {
    copyText(planText(), '方案文本已复制');
  });

  /* ── 剪贴板（文本复制走 canonical 块；图片剪贴板见 cardToBlob 调用点） ── */
  /* ═══════ html-gen:clipboard-copy v1 BEGIN —— canonical, 四模板逐字节一致, 守卫测试锁定 ═══════ */
  function copyText(text, okMsg, failMsg, onOk) {
    var _toast = (typeof showToast === 'function') ? showToast
      : (typeof showKwToast === 'function') ? showKwToast
      : function (m) { try { console.log('[html-gen] ' + m); } catch (e) {} };
    var done = function () { if (onOk) onOk(); if (okMsg) _toast(okMsg); };
    var fail = function () { _toast(failMsg || '复制失败，请手动选中文本复制'); };
    var fallback = function () {
      var ta = document.createElement('textarea');
      ta.value = text;
      ta.setAttribute('readonly', '');
      ta.style.cssText = 'position:fixed;top:-1000px;left:-1000px;opacity:0';
      document.body.appendChild(ta);
      ta.select();
      ta.setSelectionRange(0, text.length);
      var ok = false;
      try { ok = document.execCommand('copy'); } catch (e) { ok = false; }
      document.body.removeChild(ta);
      if (ok) { done(); } else { fail(); }
    };
    if (navigator.clipboard && navigator.clipboard.writeText && window.isSecureContext) {
      navigator.clipboard.writeText(text).then(done).catch(fallback);
    } else {
      fallback();                       /* 非安全上下文 ⇒ 直接回退, 不得依赖 catch */
    }
  }
  /* ═══════ html-gen:clipboard-copy v1 END ═══════ */

  /* ── 分享卡 ── */
  function cardRows(d) {
    return d.items.map(function (it) {
      var e = BYID[it.id] || { name: it.id };
      return '<tr><td>' + esc(e.name) + '</td>' +
        '<td class="num">' + esc(it.sets) + '</td>' +
        '<td class="reps">' + esc(it.reps) + '</td></tr>';
    }).join('');
  }
  function dateLine() {
    var d = new Date();
    var wk = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'][d.getDay()];
    return d.getFullYear() + '.' + String(d.getMonth() + 1).padStart(2, '0') + '.' +
      String(d.getDate()).padStart(2, '0') + ' ' + wk;
  }
  function buildDayCard(dayKey) {
    var d = dayBy(dayKey);
    return '<div class="card" id="shareCard">' +
      '<h2>' + esc(d.label + ' · ' + d.theme) + '</h2>' +
      '<div class="c-sub">' + esc((META.meta && META.meta.slogan) || '薄肌减脂 · 阶段一') + '</div>' +
      '<div class="c-meta">' + esc(dateLine()) + ' · ' + esc(d.duration) + ' · 共 ' + sumSets(d) + ' 组</div>' +
      '<table><colgroup><col style="width:62%"><col style="width:16%"><col style="width:22%"></colgroup>' +
      '<thead><tr><th>动作</th><th style="text-align:right">组数</th><th style="text-align:right">次数</th></tr></thead>' +
      '<tbody>' + cardRows(d) + '</tbody></table>' +
      '<div class="c-foot"><span>' + esc((META.meta && META.meta.goal) || '') + '</span><span>slimdown</span></div>' +
      '</div>';
  }
  function buildWeekCard() {
    var body = days.map(function (d) {
      return '<div class="w-day"><div class="t"><span class="k">' + esc(d.short || '') + '</span>' +
        esc(d.theme) + '<span class="m">' + esc(d.duration) + '</span></div>' +
        '<div class="l">' + d.items.map(function (it) {
          var e = BYID[it.id];
          return esc(e ? e.name : it.id) + ' ' + esc(it.sets) + '×' + esc(it.reps);
        }).join(' · ') + '</div></div>';
    }).join('');
    return '<div class="card week" id="shareCard">' +
      '<h2>' + esc((META.title || '七日活动方案')) + '</h2>' +
      '<div class="c-meta">' + esc((META.meta && META.meta.slogan) || '') + ' · ' +
      esc((META.meta && META.meta.goal) || '') + '</div>' + body +
      '<div class="c-foot"><span>' + esc((META.meta && META.meta.steps) || '') + '</span><span>slimdown</span></div>' +
      '</div>';
  }
  var previewScope = 'day';
  function openPreview(scope) {
    previewScope = scope;
    $('previewHost').innerHTML = scope === 'week' ? buildWeekCard() : buildDayCard(todayKey());
    $('imgNote').textContent = '';
    $('previewMask').classList.add('open');
    document.body.style.overflow = 'hidden';
  }
  $('btnCardDay').addEventListener('click', function () { openPreview('day'); });
  $('btnCardWeek').addEventListener('click', function () { openPreview('week'); });
  $('btnClosePreview').addEventListener('click', function () {
    $('previewMask').classList.remove('open');
    document.body.style.overflow = '';
  });

  /* ── DOM → PNG（零依赖：foreignObject + canvas） ── */
  function collectCss() {
    var css = '';
    for (var i = 0; i < document.styleSheets.length; i++) {
      var rules;
      try { rules = document.styleSheets[i].cssRules; } catch (e) { continue; }
      for (var j = 0; j < rules.length; j++) css += rules[j].cssText + '\n';
    }
    return css;
  }
  function cardToBlob(node, scale) {
    scale = scale || 2;
    // 导出统一按 720px 定宽重排（屏上窄屏自适应会得到糊图）
    var stage = document.createElement('div');
    stage.style.cssText = 'position:fixed;left:-10000px;top:0;width:720px;background:#FAF8F2;';
    var clone = node.cloneNode(true);
    clone.removeAttribute('id');
    clone.style.width = '720px';
    clone.style.maxWidth = '720px';
    stage.appendChild(clone);
    document.body.appendChild(stage);
    var w = clone.offsetWidth, h = clone.offsetHeight;
    var css = collectCss();
    var svg = '<svg xmlns="http://www.w3.org/2000/svg" width="' + (w * scale) + '" height="' + (h * scale) +
      '" viewBox="0 0 ' + w + ' ' + h + '">' +
      '<foreignObject width="100%" height="100%">' +
      '<div xmlns="http://www.w3.org/1999/xhtml"><style><![CDATA[' + css + ']]></style>' +
      new XMLSerializer().serializeToString(clone) + '</div></foreignObject></svg>';
    var url = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svg);
    document.body.removeChild(stage);
    return new Promise(function (resolve, reject) {
      var img = new Image();
      img.onload = function () {
        var cv = document.createElement('canvas');
        cv.width = w * scale; cv.height = h * scale;
        var ctx = cv.getContext('2d');
        ctx.fillStyle = '#FAF8F2';
        ctx.fillRect(0, 0, cv.width, cv.height);
        ctx.drawImage(img, 0, 0, cv.width, cv.height);
        cv.toBlob(function (b) { b ? resolve(b) : reject(new Error('toBlob failed')); }, 'image/png');
      };
      img.onerror = function () { reject(new Error('SVG rasterize failed')); };
      img.src = url;
    });
  }
  function download(blob, name) {
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = name;
    document.body.appendChild(a);
    a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 1000);
  }
  function fileName() {
    var d = new Date();
    return 'slimdown-' + (previewScope === 'week' ? 'week' : todayKey()) + '-' +
      d.getFullYear() + String(d.getMonth() + 1).padStart(2, '0') + String(d.getDate()).padStart(2, '0') + '.png';
  }
  $('btnCopyImg').addEventListener('click', function () {
    var node = $('shareCard');
    if (!node) return;
    $('imgNote').textContent = '生成中…';
    cardToBlob(node, 2).then(function (blob) {
      if (window.isSecureContext && navigator.clipboard && window.ClipboardItem) {
        return navigator.clipboard.write([new ClipboardItem({ 'image/png': blob })])
          .then(function () { $('imgNote').textContent = '已复制图片，可直接粘贴'; })
          .catch(function () { download(blob, fileName()); $('imgNote').textContent = '复制被拒绝，已下载 PNG'; });
      }
      download(blob, fileName());
      $('imgNote').textContent = '当前环境不支持复制图片，已下载 PNG';
    }).catch(function (e) {
      $('imgNote').textContent = '导出失败：' + e.message + '（可改用截图）';
    });
  });
  $('btnDownloadImg').addEventListener('click', function () {
    var node = $('shareCard');
    if (!node) return;
    cardToBlob(node, 3).then(function (blob) { download(blob, fileName()); $('imgNote').textContent = '已下载'; })
      .catch(function (e) { $('imgNote').textContent = '导出失败：' + e.message; });
  });
  $('btnPrint').addEventListener('click', function () { window.print(); });

  /* ── 卡片模式（?card=day|week[&d=mon]）── */
  function cardMode() {
    var q = new URLSearchParams(location.search);
    var kind = q.get('card');
    if (!kind) return false;
    document.body.classList.add('cardonly');
    var host = document.createElement('div');
    host.id = 'standalone';
    var d = q.get('d');
    host.innerHTML = kind === 'week' ? buildWeekCard() : buildDayCard(d || todayKey());
    document.body.appendChild(host);
    document.title = (kind === 'week' ? '七日活动方案' : dayBy(d || todayKey()).label) + ' · slimdown';
    return true;
  }

  /* ── 启动 ── */
  function applyHash() {
    var m = /#p=(.+)$/.exec(location.hash || '');
    if (!m) return false;
    var res = decodePlan(m[1]);
    if (!res || !res.days.length) { showToast('分享链接已损坏，已按本机方案显示'); return false; }
    res.days.forEach(function (sd) {
      var d = dayBy(sd.key);
      if (d) d.items = sd.items;
    });
    shared = true;
    if (res.unknown) showToast('已忽略 ' + res.unknown + ' 个未知动作');
    return true;
  }

  loadLocal();
  applyHash();
  if (!cardMode()) {
    renderWeek();
    $('stateNote').textContent = shared ? '正在查看分享方案（点「编辑 → 保存到本机」可存下）' : '';
  }
})();
