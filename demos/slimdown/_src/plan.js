/* slimdown 训练方案页 v1.3 —— 按星期 / 按主题 双视图 + 点击态记忆（state.js）+ 出图（shot.js）
   面板：编辑 / 预览（周视图）· 预览 / 出图（主题视图）；分享链接 v3 带预设位。 */
(function () {
  'use strict';

  var DATA = window.SLIMDOWN || {};
  var PLAN = DATA.plan || {};
  var PRESET = (PLAN.presets || [])[0] || { id: 'home', days: [] };
  var LAYOUTS = PLAN.themes || [];
  var EX = (DATA.exercises || []).slice();
  var BYID = {};
  EX.forEach(function (e) { BYID[e.id] = e; });

  var SKINS = [
    { id: 'ember', label: '赤金' },
    { id: 'forest', label: '墨绿' },
    { id: 'indigo', label: '靛蓝' },
    { id: 'amber', label: '暖橙' }
  ];
  var EDITS_KEY = 'slimdown:edits:v2';
  var LEGACY_EDITS = 'slimdown:v1';
  var REST_ICONS = ['Z', '松', '步', '水', '电'];

  var ui = window.SB.ui;
  var shot = window.SB.shot;

  var cur = PRESET, DEFAULTS = [], days = [];
  var EDITS = readEdits();
  var shared = false;
  var activeKey = '';
  var view = 'week';
  var dragState = null, suppressClick = false;
  var panelState = { open: false, scope: 'week', view: 'edit' };

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
  function clone(o) { return JSON.parse(JSON.stringify(o)); }
  function todayKey() {
    var map = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat'];
    return map[new Date().getDay()];
  }
  function dayBy(key) {
    for (var i = 0; i < days.length; i++) if (days[i].key === key) return days[i];
    return days[0];
  }
  function sumSets(d) {
    return (d.items || []).reduce(function (n, it) { return n + (parseInt(it.sets, 10) || 0); }, 0);
  }
  function chipText(d) {
    if (d.rest) return '★ 恢复日 ★';
    if (d.setsHint) return '★ 建议 ' + d.setsHint + ' 组 ★';
    var lo = 0, hi = 0;
    (d.items || []).forEach(function (it) {
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
    return d.slogan || (cur && cur.slogan) || (PLAN.meta && PLAN.meta.slogan) || '循序渐进 · 动作到位';
  }
  function exName(it) {
    return BYID[it.id] || { name: '（未知动作 ' + it.id + '）' };
  }

  /* ── 配色：data-theme + state.js（记忆优先于默认赤金） ── */
  function applySkin(id, persist) {
    var hit = SKINS.filter(function (t) { return t.id === id; })[0] || SKINS[0];
    document.documentElement.setAttribute('data-theme', hit.id);
    var sel = $('themeSel');
    if (sel && sel.value !== hit.id) sel.value = hit.id;
    if (persist !== false) ui.set('theme', hit.id);
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) {
      meta.setAttribute('content',
        getComputedStyle(document.documentElement).getPropertyValue('--bg').trim() || '#12100e');
    }
    return hit;
  }
  function initSkins() {
    var sel = $('themeSel');
    sel.innerHTML = SKINS.map(function (t) {
      return '<option value="' + t.id + '">' + esc(t.label) + '</option>';
    }).join('');
    applySkin(ui.get('theme'), false);
    sel.addEventListener('change', function () {
      var t = applySkin(sel.value);
      showToast('配色：' + t.label);
    });
  }

  /* ── 预设（居家七日 / 力量版）：编辑稿按预设分开存 ── */
  function readEdits() {
    var o = {};
    try { o = JSON.parse(localStorage.getItem(EDITS_KEY) || '{}') || {}; } catch (e) { o = {}; }
    if (!o.v) o.v = 2;
    /* v1.3 的 byPreset 结构一次性收编成单份（力量版预设已移除，旧 v1 编辑稿随力量版一起弃用） */
    if (!Array.isArray(o.days) && o.byPreset && Array.isArray(o.byPreset.home)) o.days = o.byPreset.home;
    delete o.byPreset;
    return o;
  }
  function writeEdits() {
    try {
      localStorage.setItem(EDITS_KEY, JSON.stringify(EDITS));
      localStorage.removeItem(LEGACY_EDITS);
    } catch (e) {}
  }
  function loadPlan() {
    DEFAULTS = clone(cur.days || []);
    days = clone(EDITS.days || DEFAULTS);
  }

  /* ── 视图切换（按星期 / 按主题） ── */
  function setPageView(v, opts) {
    opts = opts || {};
    view = (v === 'theme') ? 'theme' : 'week';
    document.documentElement.setAttribute('data-view', view);
    if (!opts.silent) ui.set('view', view);
    $('viewSeg').querySelectorAll('button[data-view]').forEach(function (b) {
      var on = b.getAttribute('data-view') === view;
      b.classList.toggle('on', on);
      b.setAttribute('aria-selected', on ? 'true' : 'false');
    });
    $('weekRow').hidden = view !== 'week';
    $('themeRow').hidden = view !== 'theme';
    $('fabEdit').hidden = view !== 'week';
  }
  $('viewSeg').addEventListener('click', function (ev) {
    var b = ev.target.closest('button[data-view]');
    if (!b) return;
    setPageView(b.getAttribute('data-view'));
    if (panelState.open) renderPanel();
  });

  /* ── 周视图 ── */
  function renderWeek() {
    var host = $('weekRow');
    var tk = todayKey();
    host.innerHTML = days.map(function (d, i) {
      var isToday = d.key === tk;
      var body;
      if (d.rest) {
        body = '<ul class="r-list">' + (d.recover || []).map(function (t, k) {
          return '<li><span class="r-ic">' + esc(REST_ICONS[k] || '·') + '</span>' +
            '<span class="rt">' + esc(t) + '</span></li>';
        }).join('') + '</ul>';
      } else {
        body = '<ul class="d-list">' + (d.items || []).map(function (it, k) {
          var e = exName(it);
          var cn = e.name_cn || e.name, en = e.name_en || '';
          var muscle = it.muscle || e.muscle || '—';
          var tip = cn + (en ? ' · ' + en : '') + ' · ' + muscle +
            (it.sets ? ' · ' + it.sets + ' 组' : '') + ' × ' + it.reps;
          return '<li><span class="idx">' + (k + 1) + '.</span>' +
            '<span class="nm" title="' + esc(tip) + '">' +
              '<span class="cn">' + esc(cn) + '</span>' +
              '<span class="mt">' + esc(muscle) + '</span>' +
            '</span>' +
            '<span class="badge" title="' + esc(tip) + '">' + esc(it.reps) + '</span></li>';
        }).join('') + '</ul>';
      }
      var done = ui.isDone(d.key);
      return '<div class="day-card' + (isToday ? ' today' : '') + (done ? ' done' : '') +
        '" style="--i:' + i + '" data-day="' + esc(d.key) + '" tabindex="0" role="button"' +
        ' aria-label="' + esc(d.label + ' ' + d.theme) + '">' +
        (isToday ? '<span class="today-chip">今天</span>' : '') +
        '<span class="drag" data-drag="' + esc(d.key) + '" title="按住拖拽换位（键盘 Alt+←/→）">⠿</span>' +
        '<div class="d-banner">' +
          '<div class="b-day">' + esc(d.rest ? '恢复日' : d.label) + '</div>' +
          '<div class="b-tag" title="' + esc(d.theme) + '">' + esc(d.theme) + '</div>' +
          '<div class="b-time">' + (d.rest ? '全天休息' : esc(d.duration)) + '</div>' +
        '</div>' +
        '<div class="d-chip">' + esc(chipText(d)) + '</div>' +
        body +
        '<div class="d-foot"><span class="s2" title="' + esc(sloganOf(d)) + '">' + esc(sloganOf(d)) + '</span></div>' +
        '<button class="chk" type="button" data-chk="' + esc(d.key) + '"' +
          ' aria-pressed="' + (done ? 'true' : 'false') + '" title="标记今天完成 / 取消">✓</button>' +
        '</div>';
    }).join('');
    bindDrag(host);
    host.querySelectorAll('.day-card').forEach(function (card) {
      card.addEventListener('click', function (ev) {
        if (ev.target.closest && (ev.target.closest('.drag') || ev.target.closest('.chk'))) return;
        if (suppressClick) { suppressClick = false; return; }
        openPanel('week', 'edit', card.getAttribute('data-day'));
      });
    });
    host.querySelectorAll('.chk').forEach(function (b) {
      b.addEventListener('click', function (ev) {
        ev.stopPropagation();
        var key = b.getAttribute('data-chk');
        var on = ui.toggleDone(key);
        var card = b.closest('.day-card');
        card.classList.toggle('done', on);
        b.setAttribute('aria-pressed', on ? 'true' : 'false');
        showToast(on ? '已标记完成 · ' + ui.dayKey() : '已取消完成标记');
      });
    });
  }

  /* ── 主题视图 ── */
  function themeRows(t) {
    return (t.items || []).map(function (it, k) {
      var note = it.note ? '<span class="note">' + esc(it.note) + '</span>' : '';
      return '<li><span class="idx">' + (k + 1) + '.</span>' +
        '<span class="nm"><b>' + esc(it.cn) + '</b>' +
          '<span class="en">' + esc(it.en) + '</span>' + note + '</span>' +
        '<span class="m-badge" title="' + esc(it.m) + '">' + esc(it.m) + '</span></li>';
    }).join('');
  }
  function themeFoot(t) {
    if (t.video && t.video.url) {
      return '<div class="t-foot"><a class="video-link" href="' + esc(t.video.url) + '"' +
        ' target="_blank" rel="noopener noreferrer"><span class="v-ico">▶</span>' +
        '<span class="v-title">' + esc(t.video.title) + '</span>' +
        '<span class="v-arrow">↗</span></a></div>';
    }
    return '<div class="t-foot"><div class="no-video"><span class="v-ico">▷</span>' +
      '<span class="v-title">跟练视频待补充</span></div></div>';
  }
  function renderThemes() {
    var host = $('themeRow');
    host.innerHTML = LAYOUTS.map(function (t, i) {
      return '<div class="theme-card" style="--i:' + i + '" data-theme-card="' + i + '">' +
        '<div class="d-banner">' +
          '<div class="b-head"><span class="b-day">' + esc(t.name) + '</span>' +
          '<span class="b-tag">' + esc(t.tag) + '</span></div>' +
          '<div class="b-pace">' + esc(t.pace) + '</div>' +
          '<div class="b-time">' + esc(t.time) + ' · 建议 ' + esc(t.sets) + ' 组</div>' +
        '</div>' +
        '<ul class="d-list tall">' + themeRows(t) + '</ul>' +
        themeFoot(t) +
        '</div>';
    }).join('');
    host.querySelectorAll('.theme-card').forEach(function (el) {
      el.addEventListener('dblclick', function () { openPanel('theme', 'prev'); });
      var foot = el.querySelector('.t-foot');
      if (foot) {
        foot.addEventListener('click', function (ev) {
          if (!ev.target.closest('a')) openPanel('theme', 'prev');
        });
      }
    });
  }

  /* ── 百叶窗：一次会话只播一次，尊重 reduced-motion ── */
  function shouldAnimate() {
    var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    return !ui.get('fx') && !reduce;
  }
  function startReveal(animate) {
    var row = $('weekRow');
    if (!animate) { row.classList.add('expanded'); return; }
    requestAnimationFrame(function () {
      setTimeout(function () {
        row.classList.add('expanded');
        ui.set('fx', 1);
        setTimeout(function () { document.documentElement.classList.remove('anim-in'); }, 1400);
      }, 200);
    });
  }

  /* ── 拖拽：换整天方案（主题/时长/口号/动作/恢复清单一起来），星期标签不动 ── */
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
    ['theme', 'duration', 'slogan', 'items', 'setsHint', 'rest', 'recover'].forEach(function (k) {
      var t = a[k]; a[k] = b[k]; b[k] = t;
    });
    markDirty(); renderWeek();
    if (panelState.open) renderPanelBody();
    showToast('已交换 ' + a.label + ' ↔ ' + b.label);
  }
  document.addEventListener('keydown', function (ev) {
    if (!ev.altKey && panelState.open && panelState.view === 'prev' && !ev.ctrlKey && !ev.metaKey &&
        ev.key !== 'Escape' && ev.target && /^(INPUT|TEXTAREA|SELECT)$/.test(ev.target.tagName) === false) {
      if (ev.key === 'ArrowDown' || ev.key === 'ArrowUp') {
        ev.preventDefault();
        selectShot(shotIndex() + (ev.key === 'ArrowDown' ? 1 : -1));
        return;
      }
      if (ev.key === 'Enter') {
        ev.preventDefault();
        $('btnDownloadImg').click();
        return;
      }
    }
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

  /* ── 统一面板（scope: week | theme） ── */
  function openPanel(scope, v, key) {
    panelState.scope = (scope === 'theme') ? 'theme' : 'week';
    if (panelState.scope === 'week') {
      if (key) activeKey = key;
      if (!activeKey) activeKey = ui.get('day') || todayKey();
      ui.set('day', activeKey);
      panelState.view = (v === 'prev') ? 'prev' : 'edit';
    } else {
      panelState.view = 'prev';
    }
    ui.set('panelView', panelState.view);
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
    var isTheme = panelState.scope === 'theme';
    $('panelTitle').textContent = isTheme
      ? '主题跟练 · ' + LAYOUTS.length + ' 套'
      : '训练方案 · ' + dayBy(activeKey).label;
    $('panelTabs').hidden = isTheme;
    $('panelSeg').querySelector('button[data-view="edit"]').hidden = isTheme;
    if (isTheme) renderTabsStatic(); else renderTabs();
    setPanelView(panelState.view);
  }
  function renderTabsStatic() {
    $('panelTabs').innerHTML = LAYOUTS.map(function (t) {
      return '<span class="p-tab on" style="pointer-events:none">' + esc(t.tag) + '</span>';
    }).join('');
  }
  function renderPanelBody() {
    if (panelState.view === 'edit') renderEdit(); else renderShot();
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
    ui.set('day', key);
    $('panelTitle').textContent = '训练方案 · ' + dayBy(key).label;
    renderTabs();
    renderPanelBody();
  }
  function setPanelView(v) {
    panelState.view = v;
    ui.set('panelView', v);
    $('viewEdit').classList.toggle('on', v === 'edit');
    $('viewPrev').classList.toggle('on', v === 'prev');
    $('panelSeg').querySelectorAll('button').forEach(function (b) {
      b.classList.toggle('on', b.getAttribute('data-view') === v);
    });
    var isTheme = panelState.scope === 'theme';
    $('btnSavePlan').disabled = isTheme || v !== 'edit';
    $('btnDownloadImg').disabled = v !== 'prev';
    $('btnCopyImg').disabled = v !== 'prev';
    $('btnShare').disabled = isTheme;
    renderPanelBody();
  }
  $('panelSeg').addEventListener('click', function (ev) {
    var b = ev.target.closest('button[data-view]');
    if (b && !b.hidden) setPanelView(b.getAttribute('data-view'));
  });
  $('panelClose').addEventListener('click', closePanel);
  $('panelMask').addEventListener('click', function (ev) {
    if (ev.target === this) closePanel();
  });
  $('fabEdit').addEventListener('click', function () {
    openPanel('week', 'edit', ui.get('day') || todayKey());
  });
  $('fabShot').addEventListener('click', function () {
    if (view === 'theme') openPanel('theme', 'prev');
    else openPanel('week', 'prev', ui.get('day') || todayKey());
  });

  /* ── 编辑视图 ── */
  function renderEdit() {
    var d = dayBy(activeKey);
    $('editDayLabel').textContent = d.label + ' · ' + d.theme;
    $('editDaySum').textContent = (d.items || []).length + ' 个动作 / ' + d.duration +
      (d.setsHint ? ' / 建议 ' + d.setsHint + ' 组' : ' / 共 ' + sumSets(d) + ' 组');
    var box = $('planList');
    if (!(d.items || []).length) {
      box.innerHTML = '<div class="plan-empty">' +
        (d.rest ? '恢复日不需要动作清单，左栏可手动添加。' : '这一天还没有动作，从左栏点 + 添加。') + '</div>';
    } else {
      box.innerHTML = d.items.map(function (it, i) {
        var e = exName(it);
        var cn = e.name_cn || e.name, en = e.name_en || '';
        return '<div class="plan-row">' +
          '<span class="nm" title="' + esc(cn + (en ? ' · ' + en : '')) + '">' + esc(cn) + '</span>' +
          '<input data-i="' + i + '" data-k="sets" value="' + esc(it.sets == null ? '' : it.sets) +
            '" inputmode="numeric" aria-label="组数" placeholder="—">' +
          '<input data-i="' + i + '" data-k="reps" value="' + esc(it.reps) + '" aria-label="次数">' +
          '<button class="btn mini" type="button" data-act="up" data-i="' + i + '" title="上移">↑</button>' +
          '<button class="btn mini" type="button" data-act="del" data-i="' + i + '" title="删除">×</button>' +
          '</div>';
      }).join('');
      box.querySelectorAll('input').forEach(function (inp) {
        inp.addEventListener('change', function () {
          var i = +inp.getAttribute('data-i');
          var k = inp.getAttribute('data-k');
          if (k === 'sets') {
            var n = parseInt(inp.value, 10);
            if (n) d.items[i].sets = n; else delete d.items[i].sets;
          } else {
            d.items[i].reps = inp.value;
          }
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

  function renderPicker() {
    var exFilter = ui.get('exFilter'), exQuery = ui.get('exQuery');
    var chips = ['all'].concat(EX.map(function (e) { return e.equip; })
      .filter(function (v, i, a) { return a.indexOf(v) === i; }));
    $('exChips').innerHTML = chips.map(function (c) {
      return '<button type="button" class="chip' + (c === exFilter ? ' on' : '') +
        '" data-e="' + esc(c) + '">' + (c === 'all' ? '全部' : esc(c)) + '</button>';
    }).join('');
    $('exChips').querySelectorAll('.chip').forEach(function (b) {
      b.addEventListener('click', function () {
        ui.set('exFilter', b.getAttribute('data-e'));
        renderPicker();
      });
    });
    var q = exQuery.toLowerCase();
    var list = EX.filter(function (e) {
      if (exFilter !== 'all' && e.equip !== exFilter) return false;
      if (!q) return true;
      return (e.name + ' ' + (e.alias || '')).toLowerCase().indexOf(q) >= 0;
    });
    var d = dayBy(activeKey);
    var has = {};
    (d.items || []).forEach(function (it) { has[it.id] = true; });
    $('exList').innerHTML = list.map(function (e) {
      return '<li><span class="grow"><b>' + esc(e.name) + '</b>' +
        '<span class="sub"> ' + esc(e.muscle) + ' · ' + esc(e.sets) + '×' + esc(e.reps) + '</span></span>' +
        '<button type="button" class="btn mini" data-add="' + esc(e.id) + '"' +
        (has[e.id] ? ' disabled' : '') + '>+</button></li>';
    }).join('') || '<li class="note" style="padding:10px">没有匹配的动作</li>';
    $('exList').querySelectorAll('button[data-add]').forEach(function (b) {
      b.addEventListener('click', function () {
        var e = BYID[b.getAttribute('data-add')];
        if (!e) return;
        if (!d.items) d.items = [];
        var item = { id: e.id, reps: e.reps };
        if (d.setsHint == null && e.sets) item.sets = e.sets;
        d.items.push(item);
        markDirty(); renderWeek(); renderEdit();
      });
    });
  }
  var searchTimer = null;
  $('exSearch').addEventListener('input', function () {
    var v = this.value.trim();
    clearTimeout(searchTimer);
    searchTimer = setTimeout(function () {
      ui.set('exQuery', v);
      renderPicker();
    }, 120);
  });

  /* ── 方案改动：改即自动存本机（按预设分开） ── */
  function markDirty() {
    EDITS.days = clone(days);
    writeEdits();
    $('panelNote').textContent = '已自动保存到本机';
  }
  function saveLocal(silent) {
    if (!cur) return false;
    EDITS.days = clone(days);
    writeEdits();
    if (!silent) {
      showToast('已保存到本机');
      $('panelNote').textContent = '已保存到本机 · ' + new Date().toLocaleTimeString();
    }
    return true;
  }
  $('btnSavePlan').addEventListener('click', function () { saveLocal(false); });
  $('btnResetDay').addEventListener('click', function () {
    var d = dayBy(activeKey);
    for (var i = 0; i < DEFAULTS.length; i++) {
      if (DEFAULTS[i].key === d.key) {
        var fresh = clone(DEFAULTS[i]);
        Object.keys(d).forEach(function (k) { if (!(k in fresh)) delete d[k]; });
        Object.keys(fresh).forEach(function (k) { d[k] = fresh[k]; });
        break;
      }
    }
    markDirty(); renderWeek(); renderEdit();
  });
  $('btnLoadDefault').addEventListener('click', function () {
    if (!confirm('还原成「' + cur.label + '」的默认七天方案？本机保存的改动会丢。')) return;
    days = clone(DEFAULTS);
    delete EDITS.days;
    writeEdits();
    renderWeek(); renderEdit();
    $('panelNote').textContent = '已还原默认方案';
    showToast('已还原默认方案');
  });
  $('btnClearMemory').addEventListener('click', function () {
    if (!confirm('清空本机的配色、视图、筛选、打卡与方案改动？页面会重新加载。')) return;
    ui.clear();
    try { localStorage.removeItem(EDITS_KEY); localStorage.removeItem(LEGACY_EDITS); } catch (e) {}
    location.reload();
  });

  /* ── 分享编码 v3：v3|预设|天号=主题!时长!动作表（动作 = 库内序号*sets~reps，sets 可空）
     解码兼容 v1（只带动作）/ v2（主题!时长!动作） */
  function numOf(id) { return parseInt(String(id).replace(/^ex/, ''), 10); }
  function idOf(n) { return 'ex' + (n < 10 ? '0' + n : String(n)); }
  function encodePlan() {
    return 'v3|' + cur.id + '|' + days.map(function (d, i) {
      var def = DEFAULTS[i] || {};
      var th = d.theme === def.theme ? '' : encodeURIComponent(d.theme);
      var du = d.duration === def.duration ? '' : encodeURIComponent(d.duration);
      return (i + 1) + '=' + th + '!' + du + '!' +
        (d.items || []).map(function (it) {
          return numOf(it.id) + '*' + (it.sets == null ? '' : it.sets) + '~' + encodeURIComponent(it.reps);
        }).join(',');
    }).join('|');
  }
  function decodePlan(str) {
    var out = [], unknown = 0;
    var segs = String(str).split('|');
    var ver = segs[0], preset = '';
    if (ver !== 'v1' && ver !== 'v2' && ver !== 'v3') return null;
    var body = segs.slice(1);
    if (ver === 'v3') preset = body.shift() || '';
    body.forEach(function (seg) {
      var p = seg.split('=');
      var d = days[parseInt(p[0], 10) - 1];
      if (!d) return;
      var theme = '', duration = '', itemsStr = p[1] || '';
      if (ver !== 'v1') {
        var parts = itemsStr.split('!');
        theme = decodeURIComponent(parts[0] || '');
        duration = decodeURIComponent(parts[1] || '');
        itemsStr = parts[2] || '';
      }
      var items = [];
      itemsStr.split(',').forEach(function (tok) {
        if (!tok) return;
        var m = /^(\d+)\*(\d*)~(.*)$/.exec(tok);
        if (!m) return;
        var id = idOf(parseInt(m[1], 10));
        if (!BYID[id]) { unknown++; return; }
        var item = { id: id, reps: decodeURIComponent(m[3]) };
        if (m[2]) item.sets = parseInt(m[2], 10);
        items.push(item);
      });
      out.push({ key: d.key, items: items, theme: theme, duration: duration });
    });
    return { days: out, unknown: unknown, preset: preset };
  }
  function buildShareUrl() {
    return location.href.split('#')[0] + '#p=' + encodePlan();
  }
  function planText() {
    var L = ['【' + (PLAN.title || '训练方案') + ' · ' + cur.label + '】', ''];
    days.forEach(function (d) {
      L.push(d.label + ' · ' + d.theme + '（' + d.duration + '）');
      if (d.rest) (d.recover || []).forEach(function (t) { L.push('  · ' + t); });
      (d.items || []).forEach(function (it, i) {
        var e = exName(it);
        var cn = e.name_cn || e.name, en = e.name_en || '';
        L.push('  ' + (i + 1) + '. ' + cn + (en ? ' ' + en : '') + ' ' +
          (it.sets ? it.sets + '×' : '') + it.reps);
      });
      L.push('');
    });
    if (cur.slogan) L.push(cur.slogan);
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
    var rows = (d.items || []).map(function (it, i) {
      var e = exName(it);
      var cn = e.name_cn || e.name, en = e.name_en || '';
      var muscle = it.muscle || e.muscle || '';
      return '<div class="c-row"><span class="i">' + (i + 1) + '.</span>' +
        '<span class="n" title="' + esc(cn + (en ? ' · ' + en : '')) + '">' +
          '<span class="cn">' + esc(cn) + '</span>' +
          (muscle ? '<span class="en">' + esc(muscle) + '</span>' : '') +
        '</span>' +
        (it.sets ? '<span class="s">' + esc(it.sets) + ' 组</span>' : '') +
        '<span class="b">' + esc(it.reps) + '</span></div>';
    }).join('');
    if (!rows && d.rest) {
      rows = (d.recover || []).map(function (t, i) {
        return '<div class="c-row"><span class="i">' + (i + 1) + '.</span>' +
          '<span class="n"><span class="cn">' + esc(t) + '</span></span></div>';
      }).join('');
    }
    return rows || '<div class="c-row"><span class="n" style="color:var(--faint)">这一天没有安排</span></div>';
  }
  function buildDayCard(key) {
    var d = dayBy(key);
    var meta = d.rest
      ? '全天休息 · ' + (d.recover || []).length + ' 条恢复建议'
      : (esc(d.duration) + ' · ' + (d.items || []).length + ' 个动作' +
         (d.setsHint ? ' · 建议 ' + esc(d.setsHint) + ' 组' : ' · 共 ' + sumSets(d) + ' 组'));
    return '<div class="card" id="shareCard">' +
      '<div class="c-banner">' +
        '<div class="k">SLIMDOWN · ' + esc(d.label) + '</div>' +
        '<h2>' + esc(d.theme) + '</h2>' +
        '<div class="m">' + meta + '</div>' +
      '</div>' +
      '<div class="c-body">' + cardRows(d) + '</div>' +
      '<div class="c-foot"><span class="sl">' + esc(sloganOf(d)) + '</span>' +
      '<span class="dt">' + esc(dateLine()) + '</span></div>' +
      '</div>';
  }
  function buildWeekCard() {
    var body = days.map(function (d) {
      return '<div class="c-row"><span class="i">' + esc(d.short || '') + '</span>' +
        '<span class="n"><b>' + esc(d.theme) + '</b>　' + esc(d.rest
          ? (d.recover || []).join(' · ')
          : (d.items || []).map(function (it) {
              var e = exName(it);
              return (e.name_cn || e.name) + ' ' + (it.sets ? it.sets + '×' : '') + it.reps;
            }).join(' · ')) + '</span>' +
        '<span class="b">' + esc(d.duration) + '</span></div>';
    }).join('');
    return '<div class="card" id="shareCard">' +
      '<div class="c-banner"><div class="k">SLIMDOWN · 7-DAY</div>' +
      '<h2>' + esc(PLAN.title || '训练方案') + '</h2>' +
      '<div class="m">' + esc(cur.label + ' · ' + (cur.slogan || '')) + '</div></div>' +
      '<div class="c-body">' + body + '</div>' +
      '<div class="c-foot"><span class="sl">' + esc(cur.slogan || '') + '</span>' +
      '<span class="dt">' + esc(dateLine()) + '</span></div>' +
      '</div>';
  }
  function buildThemeCard(t) {
    return '<div class="card tcard">' +
      '<div class="c-banner"><div class="k">HOME WORKOUT · ' + esc(t.tag) + '</div>' +
      '<h2>' + esc(t.name) + '</h2>' +
      '<div class="m">' + esc(t.time) + ' · 建议 ' + esc(t.sets) + ' 组 · ' + esc(t.pace) + '</div></div>' +
      '<div class="c-body">' + (t.items || []).map(function (it, i) {
        return '<div class="c-row"><span class="i">' + (i + 1) + '.</span>' +
          '<span class="n"><span class="cn">' + esc(it.cn) + '</span>' +
          '<span class="en">' + esc(it.en) + '</span>' +
          (it.note ? '<span class="note">' + esc(it.note) + '</span>' : '') + '</span>' +
          '<span class="mb">' + esc(it.m) + '</span></div>';
      }).join('') + '</div>' +
      '<div class="c-foot"><span class="sl">' + esc(t.video ? t.video.title : '跟练视频待补充') + '</span>' +
      '<span class="dt">' + esc(dateLine()) + '</span></div>' +
      '</div>';
  }
  /* ── 下载面板：左方案列表 + 右预览（预览 = 下载物），单张下载 ── */
  function shotItems() {
    if (panelState.scope === 'theme') {
      return LAYOUTS.map(function (t, i) {
        return { key: 't' + i, title: t.name,
                 meta: t.time + ' · ' + (t.items || []).length + ' 项 · 建议 ' + t.sets + ' 组',
                 build: (function (x) { return function () { return buildThemeCard(x); }; })(t) };
      });
    }
    var items = [{ key: 'week', title: '本周速览', meta: cur.label + ' · 七日一览', build: buildWeekCard }];
    days.forEach(function (d) {
      items.push({ key: d.key, title: d.label + ' · ' + d.theme,
                   meta: d.rest ? '恢复日 · ' + (d.recover || []).length + ' 条建议'
                                : d.duration + ' · ' + (d.items || []).length + ' 项',
                   build: (function (k) { return function () { return buildDayCard(k); }; })(d.key) });
    });
    return items;
  }
  function shotIndex() {
    var items = shotItems();
    if (panelState.scope === 'theme') {
      var i = parseInt(ui.get('shotTheme'), 10) || 0;
      return Math.min(Math.max(i, 0), items.length - 1);
    }
    var want = ui.get('shotWeek') || activeKey || todayKey();
    for (var j = 0; j < items.length; j++) if (items[j].key === want) return j;
    return 0;
  }
  function renderShot() {
    var items = shotItems(), idx = shotIndex();
    $('shotList').innerHTML = items.map(function (it, i) {
      return '<li class="' + (i === idx ? 'on' : '') + '" data-i="' + i + '" tabindex="0"' +
        ' aria-selected="' + (i === idx) + '"><b>' + esc(it.title) + '</b>' +
        '<span class="meta">' + esc(it.meta) + '</span></li>';
    }).join('');
    $('shotList').querySelectorAll('li').forEach(function (li) {
      li.addEventListener('click', function () { selectShot(+li.getAttribute('data-i')); });
    });
    $('previewHost').innerHTML = items[idx].build();
  }
  function selectShot(i) {
    var items = shotItems();
    if (i < 0 || i >= items.length) return;
    if (panelState.scope === 'theme') ui.set('shotTheme', i);
    else ui.set('shotWeek', items[i].key);
    renderShot();
    $('panelNote').textContent = '预览：' + items[i].title;
  }
  function previewNode() {
    var items = shotItems(), idx = shotIndex();
    return shotHost(items[idx].build());
  }

  function shotHost(html) {
    var host = $('shotHost');
    host.innerHTML = html;
    return host.firstElementChild;
  }
  function pngName(tag) {
    return 'slimdown-' + tag + '-' + shot.stamp() + '.png';
  }
  /* 单张下载：下载的就是右栏预览的那张（合并长图 / 逐张已按 v1.4 裁定撤除） */
  $('btnDownloadImg').addEventListener('click', function () {
    var items = shotItems(), idx = shotIndex(), node = previewNode();
    if (!node) return;
    $('panelNote').textContent = '生成中…';
    shot.nodeToBlob(node, { maxH: 6000 }).then(function (r) {
      shot.download(r.blob, pngName(items[idx].key || 'plan'));
      $('panelNote').textContent = '已下载 ' + r.w + '×' + r.h + ' · ' + items[idx].title;
      shotHost('');
    }).catch(function (e) {
      $('panelNote').textContent = '导出失败：' + e.message;
      shotHost('');
    });
  });
  $('btnCopyImg').addEventListener('click', function () {
    var items = shotItems(), idx = shotIndex(), node = previewNode();
    if (!node) return;
    $('panelNote').textContent = '生成中…';
    shot.nodeToBlob(node, { maxH: 6000 }).then(function (r) {
      var blob = r.blob, size = r.w + '×' + r.h;
      if (window.isSecureContext && navigator.clipboard && window.ClipboardItem) {
        return navigator.clipboard.write([new ClipboardItem({ 'image/png': blob })])
          .then(function () { $('panelNote').textContent = '已复制 · ' + size + ' · ' + items[idx].title; })
          .catch(function () {
            shot.download(blob, pngName(items[idx].key || 'plan'));
            $('panelNote').textContent = '复制被拒绝，已下载 ' + size;
          });
      }
      shot.download(blob, pngName(items[idx].key || 'plan'));
      $('panelNote').textContent = '当前环境不支持复制图片，已下载 PNG ' + size;
    }).catch(function (e) {
      $('panelNote').textContent = '导出失败：' + e.message + '（可改用截图）';
    });
  });
  var btnPrint = $('btnPrint');
  if (btnPrint) btnPrint.addEventListener('click', function () { window.print(); });

  /* ── 卡片模式（?card=day|week|theme[&d=mon|&t=1]）：只留卡本身，方便截图 ── */
  function cardMode() {
    var q = new URLSearchParams(location.search);
    var kind = q.get('card');
    if (!kind) return false;
    document.body.classList.add('cardonly');
    var host = document.createElement('div');
    host.id = 'standalone';
    var k = q.get('d') || ui.get('day') || todayKey();
    if (kind === 'week') host.innerHTML = buildWeekCard();
    else if (kind === 'theme') {
      var idx = Math.max(0, (parseInt(q.get('t'), 10) || 1) - 1);
      host.innerHTML = buildThemeCard(LAYOUTS[idx] || LAYOUTS[0]);
    } else host.innerHTML = buildDayCard(k);
    document.body.appendChild(host);
    document.title = (kind === 'week' ? '七日方案' : kind === 'theme' ? '主题跟练' : dayBy(k).label) + ' · slimdown';
    return true;
  }

  /* ── 启动 ── */
  function applyHash() {
    var m = /#p=(.+)$/.exec(location.hash || '');
    if (!m) return false;
    var res = decodePlan(m[1]);
    if (!res || !res.days.length) { showToast('分享链接已损坏，已按本机方案显示'); return false; }
    if (res.preset && res.preset !== cur.id) {
      showToast('链接里的「' + res.preset + '」预设已下线，按当前方案显示');
    }
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
  $('btnUnshare').addEventListener('click', function () {
    days = clone(EDITS.days || DEFAULTS);
    shared = false;
    $('sharedBar').hidden = true;
    if (history.replaceState) history.replaceState(null, '', location.pathname + location.search);
    setPageView(ui.get('view'), { silent: true });   /* 回到本机记忆的视图（分享期间被强制星期） */
    renderWeek();
    showToast('已恢复我的方案');
  });

  initSkins();
  loadPlan();
  applyHash();
  activeKey = ui.get('day') || todayKey();
  setPageView(ui.get('view'));
  if (shared) setPageView('week', { silent: true });  /* 分享的是七日方案 ⇒ 强制星期视图，不动本机记忆 */
  $('sharedBar').hidden = !shared;
  if (!cardMode()) {
    var animate = shouldAnimate();
    if (animate) document.documentElement.classList.add('anim-in');
    renderWeek();
    renderThemes();
    startReveal(animate);
  }
})();
