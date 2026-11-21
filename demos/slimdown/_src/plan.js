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

  /* ── 渲染：周视图（七天一行） ── */
  function renderWeek() {
    var host = $('weekRow');
    var tk = todayKey();
    host.innerHTML = days.map(function (d) {
      var isToday = d.key === tk;
      var items = d.items.map(function (it) {
        var e = BYID[it.id];
        if (!e) return '';
        return '<li><span class="nm" title="' + esc(e.name) + '">' + esc(e.name) + '</span>' +
          '<span class="v">' + esc(it.sets) + '×' + esc(it.reps) + '</span></li>';
      }).join('');
      return '<div class="day-card' + (isToday ? ' today' : '') + '" data-day="' + esc(d.key) + '" tabindex="0">' +
        (isToday ? '<span class="today-chip">今天</span>' : '') +
        '<div class="d-top"><span class="drag" data-drag="' + esc(d.key) + '" title="拖拽换位（也可 Alt+←/→）">⠿</span>' +
        '<span class="d-label">' + esc(d.short || d.label.slice(-1)) + '</span>' +
        '<h3 title="' + esc(d.theme) + '">' + esc(d.theme) + '</h3></div>' +
        '<div class="d-meta">' + esc(d.label) + ' · ' + esc(d.duration) + '</div>' +
        '<ol>' + (items || '<li class="note">空</li>') + '</ol>' +
        '<div class="d-foot"><span>' + d.items.length + ' 个动作 共 ' + sumSets(d) + ' 组</span>' +
        '<span class="d-acts">' +
        '<button type="button" data-act="edit" data-day="' + esc(d.key) + '" title="编辑方案" aria-label="编辑' + esc(d.label) + '方案">✎</button>' +
        '<button type="button" data-act="preview" data-day="' + esc(d.key) + '" title="预览卡片" aria-label="预览' + esc(d.label) + '卡片">▣</button>' +
        '</span></div>' +
        '</div>';
    }).join('');
    host.querySelectorAll('button[data-act]').forEach(function (b) {
      b.addEventListener('click', function (ev) {
        ev.stopPropagation();
        var key = b.getAttribute('data-day');
        if (b.getAttribute('data-act') === 'edit') openEditor(key);
        else openPreview('day', key);
      });
    });
    bindDrag(host);
    $('stateNote').textContent = shared ? '正在查看分享方案' : (dirty ? '未保存（仅本次浏览器）' : '');
  }

  /* ── 拖拽换位：只换「这两天练什么」，星期标签不动 ── */
  var dragState = null;
  function bindDrag(host) {
    host.querySelectorAll('.drag').forEach(function (h) {
      h.addEventListener('pointerdown', function (ev) {
        ev.preventDefault();
        var card = h.closest('.day-card');
        var ghost = card.cloneNode(true);
        var r = card.getBoundingClientRect();
        ghost.className = 'drag-ghost day-card';
        ghost.style.width = r.width + 'px';
        ghost.style.left = r.left + 'px';
        ghost.style.top = r.top + 'px';
        document.body.appendChild(ghost);
        card.classList.add('dragging');
        dragState = { from: card.getAttribute('data-day'), ghost: ghost, card: card,
                      dx: ev.clientX - r.left, dy: ev.clientY - r.top, over: null };
        try { h.setPointerCapture(ev.pointerId); } catch (e) {}
        h.addEventListener('pointermove', onDragMove);
        h.addEventListener('pointerup', onDragEnd);
        h.addEventListener('pointercancel', onDragCancel);
      });
    });
  }
  function onDragMove(ev) {
    if (!dragState) return;
    var g = dragState.ghost;
    g.style.left = (ev.clientX - dragState.dx) + 'px';
    g.style.top = (ev.clientY - dragState.dy) + 'px';
    var el = document.elementFromPoint(ev.clientX, ev.clientY);
    var card = el && el.closest ? el.closest('.day-card') : null;
    if (card === dragState.ghost) card = null;
    if (dragState.over && dragState.over !== card) dragState.over.classList.remove('drop-target');
    dragState.over = (card && card !== dragState.card) ? card : null;
    if (dragState.over) dragState.over.classList.add('drop-target');
  }
  function onDragEnd(ev) {
    if (!dragState) return;
    var st = dragState;
    cleanupDrag();
    if (st.over) swapItems(st.from, st.over.getAttribute('data-day'));
  }
  function onDragCancel() { if (dragState) cleanupDrag(); }
  function cleanupDrag() {
    var st = dragState;
    dragState = null;
    if (!st) return;
    st.ghost.remove();
    st.card.classList.remove('dragging');
    document.querySelectorAll('.drop-target').forEach(function (x) { x.classList.remove('drop-target'); });
    var h = st.card.querySelector('.drag');
    if (h) {
      h.removeEventListener('pointermove', onDragMove);
      h.removeEventListener('pointerup', onDragEnd);
      h.removeEventListener('pointercancel', onDragCancel);
    }
  }
  function swapItems(aKey, bKey) {
    if (!aKey || !bKey || aKey === bKey) return;
    var a = dayBy(aKey), b = dayBy(bKey);
    ['theme', 'duration', 'items'].forEach(function (k) {
      var t = a[k]; a[k] = b[k]; b[k] = t;
    });
    markDirty(); renderWeek();
    saveLocal();
    showToast('已交换 ' + a.label + ' ↔ ' + b.label);
  }
  /* 键盘：卡片聚焦后 Alt+←/→ 与相邻日交换 */
  document.addEventListener('keydown', function (ev) {
    if (!ev.altKey || (ev.key !== 'ArrowLeft' && ev.key !== 'ArrowRight')) return;
    var card = document.activeElement && document.activeElement.closest
      ? document.activeElement.closest('.day-card') : null;
    if (!card) return;
    var i = days.findIndex(function (d) { return d.key === card.getAttribute('data-day'); });
    var j = i + (ev.key === 'ArrowRight' ? 1 : -1);
    if (i < 0 || j < 0 || j >= days.length) return;
    ev.preventDefault();
    swapItems(days[i].key, days[j].key);
  });

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
    return 'v2|' + days.map(function (d, i) {
      var def = DEFAULTS[i] || {};
      var th = d.theme === def.theme ? '' : encodeURIComponent(d.theme);
      var du = d.duration === def.duration ? '' : encodeURIComponent(d.duration);
      return (i + 1) + '=' + th + '!' + du + '!' +
        d.items.map(function (it) {
          return numOf(it.id) + '*' + (parseInt(it.sets, 10) || 0) + '~' + encodeURIComponent(it.reps);
        }).join(',');
    }).join('|');
  }
  function decodePlan(str) {
    var out = [], unknown = 0;
    var segs = String(str).split('|');
    var ver = segs[0];
    if (ver !== 'v1' && ver !== 'v2') return null;
    segs.slice(1).forEach(function (seg) {
      var p = seg.split('=');
      var d = days[parseInt(p[0], 10) - 1];
      if (!d) return;
      var theme = '', duration = '', itemsStr = p[1] || '';
      if (ver === 'v2') {
        var parts = itemsStr.split('!');
        theme = decodeURIComponent(parts[0] || '');
        duration = decodeURIComponent(parts[1] || '');
        itemsStr = parts[2] || '';
      }
      var items = [];
      itemsStr.split(',').forEach(function (tok) {
        if (!tok) return;
        var m = /^(\d+)\*(\d+)~(.*)$/.exec(tok);
        if (!m) return;
        var id = idOf(parseInt(m[1], 10));
        if (!BYID[id]) { unknown++; return; }
        items.push({ id: id, sets: parseInt(m[2], 10), reps: decodeURIComponent(m[3]) });
      });
      out.push({ key: d.key, items: items, theme: theme, duration: duration });
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
      return '<tr><td class="nm">' + esc(e.name) + '</td>' +
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
  var previewScope = 'day', previewKey = '';
  function openPreview(scope, key) {
    previewScope = scope;
    previewKey = key || todayKey();
    $('previewHost').innerHTML = scope === 'week' ? buildWeekCard() : buildDayCard(previewKey);
    $('imgNote').textContent = '';
    $('previewMask').classList.add('open');
    document.body.style.overflow = 'hidden';
  }
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
  /* 导出 = 预览的实际 CSS 宽 ×1：预览多宽，PNG 就多宽（不再有隐藏的 2x/720 重排） */
  function cardToBlob(node) {
    var w = node.offsetWidth, h = node.offsetHeight;
    var clone = node.cloneNode(true);
    clone.removeAttribute('id');
    var css = collectCss();
    var svg = '<svg xmlns="http://www.w3.org/2000/svg" width="' + w + '" height="' + h +
      '" viewBox="0 0 ' + w + ' ' + h + '">' +
      '<foreignObject width="100%" height="100%">' +
      '<div xmlns="http://www.w3.org/1999/xhtml"><style><![CDATA[' + css + ']]></style>' +
      new XMLSerializer().serializeToString(clone) + '</div></foreignObject></svg>';
    var url = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svg);
    return new Promise(function (resolve, reject) {
      var img = new Image();
      img.onload = function () {
        var cv = document.createElement('canvas');
        cv.width = w; cv.height = h;
        var ctx = cv.getContext('2d');
        ctx.fillStyle = '#FAF8F2';
        ctx.fillRect(0, 0, cv.width, cv.height);
        ctx.drawImage(img, 0, 0, w, h);
        cv.toBlob(function (b) {
          b ? resolve({ blob: b, w: w, h: h }) : reject(new Error('toBlob failed'));
        }, 'image/png');
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
    return 'slimdown-' + (previewScope === 'week' ? 'week' : (previewKey || todayKey())) + '-' +
      d.getFullYear() + String(d.getMonth() + 1).padStart(2, '0') + String(d.getDate()).padStart(2, '0') + '.png';
  }
  $('btnCopyImg').addEventListener('click', function () {
    var node = $('shareCard');
    if (!node) return;
    $('imgNote').textContent = '生成中…';
    cardToBlob(node).then(function (r) {
      var blob = r.blob, size = r.w + '×' + r.h;
      if (window.isSecureContext && navigator.clipboard && window.ClipboardItem) {
        return navigator.clipboard.write([new ClipboardItem({ 'image/png': blob })])
          .then(function () { $('imgNote').textContent = '已复制 · ' + size; })
          .catch(function () { download(blob, fileName()); $('imgNote').textContent = '复制被拒绝，已下载 ' + size; });
      }
      download(blob, fileName());
      $('imgNote').textContent = '当前环境不支持复制图片，已下载 PNG ' + size;
    }).catch(function (e) {
      $('imgNote').textContent = '导出失败：' + e.message + '（可改用截图）';
    });
  });
  $('btnDownloadImg').addEventListener('click', function () {
    var node = $('shareCard');
    if (!node) return;
    cardToBlob(node).then(function (r) {
      download(r.blob, fileName());
      $('imgNote').textContent = '已下载 ' + r.w + '×' + r.h;
    }).catch(function (e) { $('imgNote').textContent = '导出失败：' + e.message; });
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
      if (!d) return;
      d.items = sd.items;
      if (sd.theme) d.theme = sd.theme;
      if (sd.duration) d.duration = sd.duration;
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
