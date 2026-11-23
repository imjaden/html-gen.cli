/* slimdown 状态层 —— 一份 JSON 管所有点击态（配色 / 视图 / 预设 / 页签 / 筛选 / 打卡）
   设计取舍：
   - 单键 slimdown:ui:v2（多键分散会双源、清理漏）；
   - 首次读时把旧键（slimdownPlanTheme / slimdownPlanFx）搬进来并删除，之后只认新键；
   - 打卡按日期存，只保留最近 28 天，跨周自动滚；不上传、不进分享链接。 */
window.SB = window.SB || {};
(function (SB) {
  'use strict';

  var KEY = 'slimdown:ui:v2';
  var LEGACY = [['theme', 'slimdownPlanTheme'], ['fx', 'slimdownPlanFx']];
  var DEFAULTS = {
    v: 2,
    view: 'week',        /* week | theme */
    preset: '',          /* 由页面按数据默认值补齐 */
    theme: 'ember',      /* 配色皮肤 */
    fx: 0,               /* 百叶窗动效是否已播过 */
    day: '',             /* 上一次选中的日签 */
    panelView: 'edit',   /* 面板分段：edit | prev */
    exFilter: 'all',     /* 编辑左栏器材筛选 */
    exQuery: '',         /* 编辑左栏搜索词 */
    shotWeek: '',        /* 下载面板 · 周视图选中项（day key 或 'week' 速览） */
    shotTheme: 0,        /* 下载面板 · 主题视图选中序号 */
    checkin: {}          /* {'2026-11-23': ['mon','wed']} */
  };
  var KEEP_DAYS = 28;
  var mem = null;

  function read() {
    if (mem) return mem;
    var o = {};
    try { o = JSON.parse(localStorage.getItem(KEY) || '{}') || {}; } catch (e) { o = {}; }
    if (!o.v) {
      for (var i = 0; i < LEGACY.length; i++) {
        try {
          var v = localStorage.getItem(LEGACY[i][1]);
          if (LEGACY[i][0] === 'fx') { if (v === '1') o.fx = 1; } else if (v) { o[LEGACY[i][0]] = v; }
        } catch (e) {}
      }
      o.v = 2;
    }
    for (var k in DEFAULTS) if (!(k in o)) o[k] = DEFAULTS[k];
    if (!o.checkin || typeof o.checkin !== 'object') o.checkin = {};
    mem = o;
    return mem;
  }

  function flush() {
    try {
      localStorage.setItem(KEY, JSON.stringify(mem));
      for (var i = 0; i < LEGACY.length; i++) localStorage.removeItem(LEGACY[i][1]);
    } catch (e) {}
  }

  function get(k) { return read()[k]; }

  function set(k, v) {
    var o = read();
    if (o[k] === v) return v;
    o[k] = v;
    flush();
    return v;
  }

  function dayKey(d) {
    var t = d || new Date();
    return t.getFullYear() + '-' + String(t.getMonth() + 1).padStart(2, '0') + '-' +
      String(t.getDate()).padStart(2, '0');
  }

  function prune(o) {
    var now = new Date();
    var cut = new Date(now.getTime() - KEEP_DAYS * 86400000);
    var floor = dayKey(cut);
    var next = {};
    for (var d in o) if (d >= floor) next[d] = o[d];
    return next;
  }

  /* 打卡：以「今天」为记账日，记下今天练的是哪一天（可补练） */
  function isDone(dayId) {
    var list = read().checkin[dayKey()] || [];
    return list.indexOf(dayId) >= 0;
  }

  function toggleDone(dayId) {
    var o = read();
    var k = dayKey();
    var list = (o.checkin[k] || []).slice();
    var i = list.indexOf(dayId);
    if (i >= 0) list.splice(i, 1); else list.push(dayId);
    o.checkin[k] = list;
    o.checkin = prune(o.checkin);
    flush();
    return i < 0;
  }

  function clear() {
    try { localStorage.removeItem(KEY); } catch (e) {}
    mem = null;
  }

  SB.ui = { get: get, set: set, all: read, clear: clear,
            dayKey: dayKey, isDone: isDone, toggleDone: toggleDone };
})(window.SB);
