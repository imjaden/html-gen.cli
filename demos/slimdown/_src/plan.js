/* slimdown 训练方案页 v1.2 —— 深色周视图 / 四套主题 / 统一面板（编辑 · 预览）/ 分享 / 出图 */
(function () {
  'use strict';

  var DATA = window.SLIMDOWN || {};
  var META = DATA.plan || {};
  var EX = (DATA.exercises || []).slice();
  var BYID = {};
  EX.forEach(function (e) { BYID[e.id] = e; });

  var LS_KEY = 'slimdown:v1';
  var THEME_KEY = 'slimdownPlanTheme';
  var FX_KEY = 'slimdownPlanFx';

  var THEMES = [
    { id: 'ember', label: '赤金' },
    { id: 'forest', label: '墨绿' },
    { id: 'indigo', label: '靛蓝' },
    { id: 'amber', label: '暖橙' }
  ];
  var VARS = ['--bg', '--bg-2', '--glow', '--card', '--card-2', '--edge', '--edge-soft',
              '--ink', '--muted', '--faint', '--acc', '--acc-2', '--acc-deep', '--gold', '--gold-soft'];

  var DEFAULTS = JSON.parse(JSON.stringify(META.days || []));
  var days = JSON.parse(JSON.stringify(DEFAULTS));
  var dirty = false;
  var shared = false;
  var activeKey = '';

  var $ = function (id) { return document.getElementById(id); };
  var esc = function (s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  };
  function showToast(msg) {
    var t = $('__toast');
    if (!t) {
      t = document.createElement('div');
      t.id = '__toast';
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
  function chipText(d) {
    if (d.rest) return '★ 恢复日 ★';
    var lo = 0, hi = 0;
    d.items.forEach(function (it) {
      var s = parseInt(it.sets, 10) || 0;
      if (s <= 1) return;            /* 单次有氧不参与“建议组数”，避免 1–3 组这种噪音 */
      if (!lo || s < lo) lo = s;
      if (s > hi) hi = s;
    });
    if (!hi) return '★ 自由安排 ★';
    if (hi === lo) return lo > 1 ? ('★ 建议 ' + lo + ' 组 ★') : '★ 单次完成 ★';
    return '★ 建议 ' + lo + '–' + hi + ' 组 ★';
  }
  function sloganOf(d) {
    return d.slogan || (META.meta && META.meta.slogan) || '循序渐进 · 动作到位';
  }
  function labelOfTheme(id) {
    for (var i = 0; i < THEMES.length; i++) if (THEMES[i].id === id) return THEMES[i].label;
    return id;
  }

  /* ── 主题：data-theme + localStorage（优先级：localStorage > 默认赤金） ── */
  function applyTheme(id, persist) {
    var hit = THEMES.filter(function (t) { return t.id === id; })[0];
    if (!hit) { id = 'ember'; hit = THEMES[0]; }
    document.documentElement.setAttribute('data-theme', id);
    var sel = $('themeSel');
    if (sel && sel.value !== id) sel.value = id;
    if (persist !== false) {
      try { localStorage.setItem(THEME_KEY, id); } catch (e) {}
    }
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) {
      meta.setAttribute('content',
        getComputedStyle(document.documentElement).getPropertyValue('--bg').trim() || '#12100e');
    }
    return hit;
  }
  function initTheme() {
    var sel = $('themeSel');
    sel.innerHTML = THEMES.map(function (t) {
      return '<option value="' + t.id + '">' + esc(t.label) + '</option>';
    }).join('');
    var stored = null;
    try { stored = localStorage.getItem(THEME_KEY); } catch (e) {}
    applyTheme((THEMES.filter(function (t) { return t.id === stored; })[0] || {}).id || 'ember', false);
    sel.addEventListener('change', function () {
      var t = applyTheme(sel.value);
      showToast('主题：' + t.label);
    });
  }
  function themeVarsInline() {
    var cs = getComputedStyle(document.documentElement);
    return VARS.map(function (n) { return n + ':' + cs.getPropertyValue(n).trim(); }).join(';');
  }

  /* ── 周视图 ── */
  function renderWeek() {
    var host = $('weekRow');
    var tk = todayKey();
    host.innerHTML = days.map(function (d, i) {
      var isToday = d.key === tk;
      var items = d.items.map(function (it, k) {
        var e = BYID[it.id];
        if (!e) return '';
        var cn = e.name_cn || e.name, en = e.name_en || '';
        var full = cn + (en ? ' · ' + en : '') + ' · ' + it.sets + ' 组 × ' + it.reps;
        return '<li><span class="idx">' + (k + 1) + '.</span>' +
          '<span class="nm" title="' + esc(full) + '">' +
            '<span class="cn">' + esc(cn) + '</span>' +
            (en ? '<span class="en">' + esc(en) + '</span>' : '') +
          '</span>' +
          '<span class="badge" title="' + esc(it.sets + ' 组 × ' + it.reps) + '">' + esc(it.reps) + '</span></li>';
      }).join('');
      return '<div class="day-card' + (isToday ? ' today' : '') + '" style="--i:' + i + '"' +
        ' data-day="' + esc(d.key) + '" tabindex="0" role="button"' +
        ' aria-label="' + esc(d.label + ' ' + d.theme) + '">' +
        (isToday ? '<span class="today-chip">今天</span>' : '') +
        '<span class="drag" data-drag="' + esc(d.key) + '" title="按住拖拽换位（键盘 Alt+←/→）">⠿</span>' +
        '<div class="d-banner">' +
          '<div class="b-day">' + esc(d.rest ? '恢复日' : d.label) + '</div>' +
          '<div class="b-tag" title="' + esc(d.theme) + '">' + esc(d.theme) + '</div>' +
          '<div class="b-time">' + (d.rest ? '全天休息' : '约 ' + esc(d.duration)) + '</div>' +
        '</div>' +
        '<div class="d-chip">' + esc(chipText(d)) + '</div>' +
        '<ul class="d-list">' + (items || '<li class="nm" style="color:var(--faint)">空</li>') + '</ul>' +
        '<div class="d-foot"><span class="s2" title="' + esc(sloganOf(d)) + '">' + esc(sloganOf(d)) + '</span></div>' +
        '</div>';
    }).join('');
    bindDrag(host);
    host.querySelectorAll('.day-card').forEach(function (card) {
      card.addEventListener('click', function (ev) {
        if (ev.target.closest && ev.target.closest('.drag')) return;
        if (suppressClick) { suppressClick = false; return; }
        openPanel('edit', card.getAttribute('data-day'));
      });
    });
  }
  /* 百叶窗：一次会话只播一次，尊重 reduced-motion；脚本失败也不影响可见性 */
  function shouldAnimate() {
    var played = false;
    try { played = localStorage.getItem(FX_KEY) === '1'; } catch (e) {}
    var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    return !played && !reduce;
  }
  function startReveal(animate) {
    var row = $('weekRow');
    if (!animate) { row.classList.add('expanded'); return; }
    requestAnimationFrame(function () {
      setTimeout(function () {
        row.classList.add('expanded');
        try { localStorage.setItem(FX_KEY, '1'); } catch (e) {}
        setTimeout(function () { document.documentElement.classList.remove('anim-in'); }, 1400);
      }, 200);
    });
  }

  /* ── 拖拽：换整天方案（主题/时长/动作），星期标签不动 ── */
  var dragState = null, suppressClick = false;
  function bindDrag(host) {
    host.querySelectorAll('.drag').forEach(function (h) {
      h.addEventListener('pointerdown', function (ev) {
        ev.preventDefault();
        ev.stopPropagation();
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
  function onDragEnd() {
    if (!dragState) return;
    var st = dragState;
    cleanupDrag();
    suppressClick = true;
    setTimeout(function () { suppressClick = false; }, 60);
    if (st.over) swapDays(st.from, st.over.getAttribute('data-day'));
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
  function swapDays(aKey, bKey) {
    if (!aKey || !bKey || aKey === bKey) return;
    var a = dayBy(aKey), b = dayBy(bKey);
    ['theme', 'duration', 'slogan', 'items'].forEach(function (k) {
      var t = a[k]; a[k] = b[k]; b[k] = t;
    });
    markDirty(); renderWeek();
    if (panelState.open) renderPanelBody();
    showToast('已交换 ' + a.label + ' ↔ ' + b.label);
  }
  document.addEventListener('keydown', function (ev) {
    if (ev.key === 'Escape') {
      if ($('panelMask').classList.contains('open')) closePanel();
      else if ($('shareMask').classList.contains('open')) $('shareMask').classList.remove('open');
      return;
    }
    if (!ev.altKey || (ev.key !== 'ArrowLeft' && ev.key !== 'ArrowRight')) return;
    var card = document.activeElement && document.activeElement.closest
      ? document.activeElement.closest('.day-card') : null;
    if (!card) return;
    var i = days.findIndex(function (d) { return d.key === card.getAttribute('data-day'); });
    var j = i + (ev.key === 'ArrowRight' ? 1 : -1);
    if (i < 0 || j < 0 || j >= days.length) return;
    ev.preventDefault();
    swapDays(days[i].key, days[j].key);
  });

  /* ── 统一面板：标题 / 七天页签 / 功能区（编辑 · 预览）/ 底部按钮 ── */
  var panelState = { open: false, view: 'edit' };
  function openPanel(view, key) {
    if (key) activeKey = key;
    if (!activeKey) activeKey = todayKey();
    panelState.view = view || 'edit';
    panelState.open = true;
    $('panelMask').classList.add('open');
    document.body.style.overflow = 'hidden';
    renderPanel();
  }
  function closePanel() {
    panelState.open = false;
    $('panelMask').classList.remove('open');
    document.body.style.overflow = '';
  }
  function renderPanel() {
    $('panelTitle').textContent = '训练方案 · ' + dayBy(activeKey).label;
    renderTabs();
    setView(panelState.view);
  }
  function renderPanelBody() {
    if (panelState.view === 'edit') renderEdit(); else renderPreview();
  }
  function renderTabs() {
    var tk = todayKey();
    $('panelTabs').innerHTML = days.map(function (d) {
      return '<button type="button" role="tab" class="p-tab' + (d.key === activeKey ? ' on' : '') +
        '" data-k="' + esc(d.key) + '" aria-selected="' + (d.key === activeKey) + '">' +
        esc(d.label) + (d.key === tk ? '<span class="dot" title="今天"></span>' : '') + '</button>';
    }).join('');
    $('panelTabs').querySelectorAll('.p-tab').forEach(function (b) {
      b.addEventListener('click', function () { selectDay(b.getAttribute('data-k')); });
    });
    var on = $('panelTabs').querySelector('.p-tab.on');
    if (on) {
      var t = $('panelTabs');
      t.scrollLeft = Math.max(0, on.offsetLeft - (t.clientWidth - on.offsetWidth) / 2);
    }
  }
  function selectDay(key) {
    activeKey = key;
    $('panelTitle').textContent = '训练方案 · ' + dayBy(key).label;
    renderTabs();
    renderPanelBody();
  }
  function setView(v) {
    panelState.view = v;
    $('viewEdit').classList.toggle('on', v === 'edit');
    $('viewPrev').classList.toggle('on', v === 'prev');
    $('panelSeg').querySelectorAll('button').forEach(function (b) {
      b.classList.toggle('on', b.getAttribute('data-view') === v);
    });
    $('btnSavePlan').disabled = v !== 'edit';
    $('btnDownloadImg').disabled = v !== 'prev';
    $('btnCopyImg').disabled = v !== 'prev';
    renderPanelBody();
  }
  $('panelSeg').addEventListener('click', function (ev) {
    var b = ev.target.closest('button[data-view]');
    if (b) setView(b.getAttribute('data-view'));
  });
  $('panelClose').addEventListener('click', closePanel);
  $('panelMask').addEventListener('click', function (ev) {
    if (ev.target === this) closePanel();
  });
  $('fabEdit').addEventListener('click', function () { openPanel('edit', todayKey()); });
  $('fabShot').addEventListener('click', function () { openPanel('prev', todayKey()); });

  /* ── 编辑视图 ── */
  function renderEdit() {
    var d = dayBy(activeKey);
    $('editDayLabel').textContent = d.label + ' · ' + d.theme;
    $('editDaySum').textContent = d.items.length + ' 个动作 / 共 ' + sumSets(d) + ' 组 / ' + d.duration;
    var box = $('planList');
    if (!d.items.length) {
      box.innerHTML = '<div class="plan-empty">这一天还没有动作，从左栏点 + 添加。</div>';
    } else {
      box.innerHTML = d.items.map(function (it, i) {
        var e = BYID[it.id] || { name: '（未知动作 ' + it.id + '）' };
        return '<div class="plan-row">' +
          '<span class="nm" title="' + esc(e.name) + '">' + esc(e.name) + '</span>' +
          '<input data-i="' + i + '" data-k="sets" value="' + esc(it.sets) + '" inputmode="numeric" aria-label="组数">' +
          '<input data-i="' + i + '" data-k="reps" value="' + esc(it.reps) + '" aria-label="次数">' +
          '<button class="btn mini" type="button" data-act="up" data-i="' + i + '" title="上移">↑</button>' +
          '<button class="btn mini" type="button" data-act="del" data-i="' + i + '" title="删除">×</button>' +
          '</div>';
      }).join('');
      box.querySelectorAll('input').forEach(function (inp) {
        inp.addEventListener('change', function () {
          var i = +inp.getAttribute('data-i');
          var k = inp.getAttribute('data-k');
          d.items[i][k] = k === 'sets' ? (parseInt(inp.value, 10) || 0) : inp.value;
          markDirty(); renderWeek(); renderEdit();
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
          markDirty(); renderWeek(); renderEdit();
        });
      });
    }
    renderPicker();
  }

  var exFilter = 'all', exQuery = '';
  function renderPicker() {
    var chips = ['all'].concat(EX.map(function (e) { return e.equip; })
      .filter(function (v, i, a) { return a.indexOf(v) === i; }));
    $('exChips').innerHTML = chips.map(function (c) {
      return '<button type="button" class="chip' + (c === exFilter ? ' on' : '') + '" data-e="' + esc(c) + '">' +
        (c === 'all' ? '全部' : esc(c)) + '</button>';
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
        '<button type="button" class="btn mini" data-add="' + esc(e.id) + '"' + (has[e.id] ? ' disabled' : '') + '>+</button></li>';
    }).join('') || '<li class="note" style="padding:10px">没有匹配的动作</li>';
    $('exList').querySelectorAll('button[data-add]').forEach(function (b) {
      b.addEventListener('click', function () {
        var e = BYID[b.getAttribute('data-add')];
        if (!e) return;
        d.items.push({ id: e.id, sets: e.sets, reps: e.reps });
        markDirty(); renderWeek(); renderEdit();
      });
    });
  }
  $('exSearch').addEventListener('input', function () { exQuery = this.value.trim(); renderPicker(); });

  /* ── 状态：改即自动存本机；「保存方案」= 显式落盘 + 提示 ── */
  function markDirty() {
    dirty = true; shared = false;
    saveLocal(true);
    $('panelNote').textContent = '已自动保存到本机';
  }
  function saveLocal(silent) {
    try {
      localStorage.setItem(LS_KEY, JSON.stringify({ v: 1, days: days }));
      dirty = false; shared = false;
      if (!silent) {
        showToast('已保存到本机');
        $('panelNote').textContent = '已保存到本机 · ' + new Date().toLocaleTimeString();
      }
      return true;
    } catch (e) {
      showToast('保存失败：浏览器禁用了本地存储');
      return false;
    }
  }
  function loadLocal() {
    try {
      var raw = localStorage.getItem(LS_KEY);
      if (!raw) return false;
      var o = JSON.parse(raw);
      if (!o || o.v !== 1 || !Array.isArray(o.days) || !o.days.length) return false;
      days = o.days;
      days.forEach(function (d) {
        for (var i = 0; i < DEFAULTS.length; i++) {
          if (DEFAULTS[i].key === d.key) {
            if (!d.slogan) d.slogan = DEFAULTS[i].slogan;
            if (!d.theme) d.theme = DEFAULTS[i].theme;
            if (!d.duration) d.duration = DEFAULTS[i].duration;
          }
        }
      });
      return true;
    } catch (e) { return false; }
  }
  $('btnSavePlan').addEventListener('click', function () { saveLocal(false); });
  $('btnResetDay').addEventListener('click', function () {
    var d = dayBy(activeKey);
    for (var i = 0; i < DEFAULTS.length; i++) {
      if (DEFAULTS[i].key === d.key) {
        d.items = JSON.parse(JSON.stringify(DEFAULTS[i].items));
        d.slogan = DEFAULTS[i].slogan;
        break;
      }
    }
    markDirty(); renderWeek(); renderEdit();
  });
  $('btnLoadDefault').addEventListener('click', function () {
    if (!confirm('还原成默认的七天方案？本机保存的改动会丢。')) return;
    days = JSON.parse(JSON.stringify(DEFAULTS));
    try { localStorage.removeItem(LS_KEY); } catch (e) {}
    dirty = false; shared = false;
    renderWeek(); renderEdit();
    $('panelNote').textContent = '已还原默认方案';
    showToast('已还原默认方案');
  });

  /* ── 分享编码 v2 ──
     v2|天号=主题!时长!动作表（与默认一致时留空）；动作 = 库内序号*sets~encodeURIComponent(reps)
     解码兼容 v1（只带动作表） */
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
    return location.href.split('#')[0] + '#p=' + encodePlan();
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
  $('btnCopyUrl').addEventListener('click', function () { copyText(buildShareUrl(), '链接已复制'); });
  $('btnCopyText').addEventListener('click', function () { copyText(planText(), '方案文本已复制'); });

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

  /* ── 出图卡（深色，与页面同主题） ── */
  function dateLine() {
    var d = new Date();
    var wk = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'][d.getDay()];
    return d.getFullYear() + '.' + String(d.getMonth() + 1).padStart(2, '0') + '.' +
      String(d.getDate()).padStart(2, '0') + ' ' + wk;
  }
  function cardRows(d) {
    return d.items.map(function (it, i) {
      var e = BYID[it.id] || { name: it.id };
      var cn = e.name_cn || e.name, en = e.name_en || '';
      return '<div class="c-row"><span class="i">' + (i + 1) + '.</span>' +
        '<span class="n" title="' + esc(cn + (en ? ' · ' + en : '')) + '">' +
          '<span class="cn">' + esc(cn) + '</span>' +
          (en ? '<span class="en">' + esc(en) + '</span>' : '') +
        '</span>' +
        '<span class="s">' + esc(it.sets) + ' 组</span>' +
        '<span class="b">' + esc(it.reps) + '</span></div>';
    }).join('') || '<div class="c-row"><span class="n" style="color:var(--faint)">这一天没有安排</span></div>';
  }
  function buildDayCard(key) {
    var d = dayBy(key);
    return '<div class="card" id="shareCard">' +
      '<div class="c-banner">' +
        '<div class="k">SLIMDOWN · ' + esc(d.label) + '</div>' +
        '<h2>' + esc(d.theme) + '</h2>' +
        '<div class="m">约 ' + esc(d.duration) + ' · ' + d.items.length + ' 个动作 · 共 ' + sumSets(d) + ' 组</div>' +
      '</div>' +
      '<div class="c-body">' + cardRows(d) + '</div>' +
      '<div class="c-foot"><span class="sl">' + esc(sloganOf(d)) + '</span>' +
      '<span class="dt">' + esc(dateLine()) + '</span></div>' +
      '</div>';
  }
  function buildWeekCard() {
    var body = days.map(function (d) {
      return '<div class="c-row"><span class="i">' + esc(d.short || '') + '</span>' +
        '<span class="n"><b>' + esc(d.theme) + '</b>　' + esc(d.items.map(function (it) {
          var e = BYID[it.id];
          return (e ? e.name : it.id) + ' ' + it.sets + '×' + it.reps;
        }).join(' · ')) + '</span>' +
        '<span class="b">' + esc(d.duration) + '</span></div>';
    }).join('');
    return '<div class="card" id="shareCard">' +
      '<div class="c-banner"><div class="k">SLIMDOWN · 7-DAY</div>' +
      '<h2>' + esc(META.title || '七日方案') + '</h2>' +
      '<div class="m">' + esc((META.meta && META.meta.slogan) || '') + '</div></div>' +
      '<div class="c-body">' + body + '</div>' +
      '<div class="c-foot"><span class="sl">' + esc((META.meta && META.meta.goal) || '') + '</span>' +
      '<span class="dt">' + esc(dateLine()) + '</span></div>' +
      '</div>';
  }
  function renderPreview() {
    $('previewHost').innerHTML = buildDayCard(activeKey);
  }

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
  function bgColor() {
    var v = getComputedStyle(document.documentElement).getPropertyValue('--bg').trim();
    return v || '#12100e';
  }
  /* 导出 = 预览实际 CSS 宽 ×1：PNG 多宽，预览就多宽；主题变量内联到克隆根，保证出图与屏幕同色 */
  function cardToBlob(node) {
    var w = node.offsetWidth, h = node.offsetHeight;
    var clone = node.cloneNode(true);
    clone.removeAttribute('id');
    clone.setAttribute('style', themeVarsInline() + ';' + (clone.getAttribute('style') || ''));
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
        ctx.fillStyle = bgColor();
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
    return 'slimdown-' + (activeKey || todayKey()) + '-' +
      d.getFullYear() + String(d.getMonth() + 1).padStart(2, '0') + String(d.getDate()).padStart(2, '0') + '.png';
  }
  function currentCardNode() { return $('shareCard'); }
  $('btnDownloadImg').addEventListener('click', function () {
    var node = currentCardNode();
    if (!node) return;
    $('panelNote').textContent = '生成中…';
    cardToBlob(node).then(function (r) {
      download(r.blob, fileName());
      $('panelNote').textContent = '已下载 ' + r.w + '×' + r.h;
    }).catch(function (e) { $('panelNote').textContent = '导出失败：' + e.message; });
  });
  $('btnCopyImg').addEventListener('click', function () {
    var node = currentCardNode();
    if (!node) return;
    $('panelNote').textContent = '生成中…';
    cardToBlob(node).then(function (r) {
      var blob = r.blob, size = r.w + '×' + r.h;
      if (window.isSecureContext && navigator.clipboard && window.ClipboardItem) {
        return navigator.clipboard.write([new ClipboardItem({ 'image/png': blob })])
          .then(function () { $('panelNote').textContent = '已复制 · ' + size; })
          .catch(function () { download(blob, fileName()); $('panelNote').textContent = '复制被拒绝，已下载 ' + size; });
      }
      download(blob, fileName());
      $('panelNote').textContent = '当前环境不支持复制图片，已下载 PNG ' + size;
    }).catch(function (e) {
      $('panelNote').textContent = '导出失败：' + e.message + '（可改用截图）';
    });
  });
  var btnPrint = $('btnPrint');
  if (btnPrint) btnPrint.addEventListener('click', function () { window.print(); });

  /* ── 卡片模式（?card=day|week[&d=mon]）：只留卡本身，方便截图 ── */
  function cardMode() {
    var q = new URLSearchParams(location.search);
    var kind = q.get('card');
    if (!kind) return false;
    document.body.classList.add('cardonly');
    var host = document.createElement('div');
    host.id = 'standalone';
    var k = q.get('d') || todayKey();
    host.innerHTML = kind === 'week' ? buildWeekCard() : buildDayCard(k);
    document.body.appendChild(host);
    document.title = (kind === 'week' ? '七日方案' : dayBy(k).label) + ' · slimdown';
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

  initTheme();
  loadLocal();
  applyHash();
  activeKey = todayKey();
  if (!cardMode()) {
    var animate = shouldAnimate();
    if (animate) document.documentElement.classList.add('anim-in');
    renderWeek();
    startReveal(animate);
  }
})();
