/* slimdown 出图层 —— DOM → PNG（零依赖：foreignObject + canvas），周视图与主题视图共用
   设计取舍（沿用 v1.2 已实测口径）：
   - 1x：PNG 宽 = 节点 CSS 宽（出图卡固定 720），不做 2x；
   - 克隆前把主题变量内联到克隆根，保证 PNG 与屏幕同色；
   - 长图超过 maxH 时按比例缩到 maxH，避免撞 canvas 面积上限。 */
window.SB = window.SB || {};
(function (SB) {
  'use strict';

  var VARS = ['--bg', '--bg-2', '--glow', '--card', '--card-2', '--edge', '--edge-soft',
              '--ink', '--muted', '--faint', '--acc', '--acc-2', '--acc-deep', '--gold', '--gold-soft'];
  var MAX_H = 4000;

  function collectCss() {
    var css = '';
    for (var i = 0; i < document.styleSheets.length; i++) {
      var rules;
      try { rules = document.styleSheets[i].cssRules; } catch (e) { continue; }
      for (var j = 0; j < rules.length; j++) css += rules[j].cssText + '\n';
    }
    return css;
  }

  function themeVarsInline() {
    var cs = getComputedStyle(document.documentElement);
    return VARS.map(function (n) { return n + ':' + cs.getPropertyValue(n).trim(); }).join(';');
  }

  function bgColor() {
    var v = getComputedStyle(document.documentElement).getPropertyValue('--bg').trim();
    return v || '#12100e';
  }

  function nodeToBlob(node, opts) {
    opts = opts || {};
    var w = node.offsetWidth, h = node.offsetHeight;
    if (!w || !h) return Promise.reject(new Error('节点尺寸为 0'));
    var maxH = opts.maxH || MAX_H;
    var scale = h > maxH ? maxH / h : 1;
    var cw = Math.round(w * scale), ch = Math.round(h * scale);
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
        cv.width = cw; cv.height = ch;
        var ctx = cv.getContext('2d');
        ctx.fillStyle = bgColor();
        ctx.fillRect(0, 0, cw, ch);
        ctx.drawImage(img, 0, 0, cw, ch);
        cv.toBlob(function (b) {
          b ? resolve({ blob: b, w: cw, h: ch, scaled: scale < 1 }) : reject(new Error('toBlob failed'));
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

  function stamp() {
    var d = new Date();
    return d.getFullYear() + String(d.getMonth() + 1).padStart(2, '0') + String(d.getDate()).padStart(2, '0');
  }

  SB.shot = { nodeToBlob: nodeToBlob, download: download, stamp: stamp,
              collectCss: collectCss, vars: themeVarsInline };
})(window.SB);
