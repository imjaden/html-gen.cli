/* slimdown 档案页 —— 基线表格只在本机填写（不上传、不随页面发布） */
(function () {
  'use strict';
  var KEY = 'slimdown:baseline:v1';
  var data = {};
  try { data = JSON.parse(localStorage.getItem(KEY) || '{}') || {}; } catch (e) { data = {}; }
  var inputs = Array.prototype.slice.call(document.querySelectorAll('input[data-b]'));
  inputs.forEach(function (inp) {
    var k = inp.getAttribute('data-b');
    if (data[k] != null) inp.value = data[k];
    inp.addEventListener('input', function () {
      data[k] = inp.value;
      try { localStorage.setItem(KEY, JSON.stringify(data)); } catch (e) {}
    });
  });
})();
