(function () {
  "use strict";

  var KEY = "gals-hien-thi";

  // Chỗ duy nhất chạm tới nơi lưu cài đặt. Khi có tài khoản riêng cho từng
  // người, đổi hai hàm này sang gọi máy chủ là xong.
  function readPrefs() {
    try {
      var raw = JSON.parse(localStorage.getItem(KEY) || "{}");
      return raw && typeof raw === "object" ? raw : {};
    } catch (e) {
      return {};
    }
  }

  function writePrefs(prefs) {
    try {
      localStorage.setItem(KEY, JSON.stringify(prefs));
    } catch (e) {}
  }

  var el = document.documentElement;

  function hoi(query) {
    return window.matchMedia ? window.matchMedia(query) : { matches: false, addListener: function () {} };
  }

  var MQ_TOI = hoi("(prefers-color-scheme: dark)");
  var MQ_TUONG_PHAN = hoi("(prefers-contrast: more)");

  // Công tắc bật/tắt: không lưu gì nghĩa là tắt.
  var SWITCHES = [
    { name: "motion", on: "giam", attr: "motion" },
    { name: "nen", on: "phang", attr: "nen" },
    // Tương phản cao lưu cả hai chiều, vì "chưa chọn" còn có nghĩa thứ ba là
    // nghe theo hệ điều hành.
    { name: "tuong_phan", on: "cao", off: "thuong", attr: "contrast", mq: MQ_TUONG_PHAN }
  ];

  function themeOf(prefs) {
    var chon = prefs.giao_dien;
    if (chon !== "sang" && chon !== "toi") {
      chon = MQ_TOI.matches ? "toi" : "sang";
    }
    return chon;
  }

  function apply(prefs) {
    el.dataset.theme = themeOf(prefs) === "toi" ? "dark" : "light";

    SWITCHES.forEach(function (s) {
      var value = prefs[s.name];
      if (!s.off) {
        if (value === s.on) {
          el.dataset[s.attr] = s.on;
        } else {
          delete el.dataset[s.attr];
        }
        return;
      }
      if (value !== s.on && value !== s.off) {
        value = s.mq.matches ? s.on : s.off;
      }
      el.dataset[s.attr] = value;
    });
  }

  // Cho màu chạy 160ms khi người dùng bấm đổi, nhưng không chạy ở lần vẽ đầu
  // — nếu không mỗi lần tải trang sẽ thấy cả trang đang tự đổi màu.
  function applyWithFade(prefs) {
    el.dataset.doiMau = "1";
    apply(prefs);
    window.setTimeout(function () { delete el.dataset.doiMau; }, 220);
  }

  function bindTheme() {
    var radios = Array.prototype.slice.call(
      document.querySelectorAll('input[name="giao-dien"]')
    );
    if (!radios.length) return;

    var prefs = readPrefs();
    var chon = prefs.giao_dien;
    if (chon !== "sang" && chon !== "toi") chon = "he-thong";

    radios.forEach(function (radio) {
      radio.checked = radio.value === chon;
      radio.addEventListener("change", function () {
        if (!radio.checked) return;
        var next = readPrefs();
        if (radio.value === "he-thong") {
          delete next.giao_dien;
        } else {
          next.giao_dien = radio.value;
        }
        writePrefs(next);
        applyWithFade(next);
      });
    });

    // Ai để "theo hệ thống" thì phải đổi theo ngay khi máy chuyển sáng/tối,
    // không đợi tải lại trang.
    var onChange = function () {
      if (readPrefs().giao_dien) return;
      applyWithFade(readPrefs());
    };
    if (MQ_TOI.addEventListener) {
      MQ_TOI.addEventListener("change", onChange);
    } else if (MQ_TOI.addListener) {
      MQ_TOI.addListener(onChange);
    }
  }

  function bindSwitches() {
    var prefs = readPrefs();
    SWITCHES.forEach(function (s) {
      var box = document.querySelector('input[data-pref="' + s.name + '"]');
      if (!box) return;
      var value = prefs[s.name];
      if (s.off && value !== s.on && value !== s.off) {
        value = s.mq.matches ? s.on : s.off;
      }
      box.checked = value === s.on;
      box.addEventListener("change", function () {
        var next = readPrefs();
        if (s.off) {
          next[s.name] = box.checked ? s.on : s.off;
        } else if (box.checked) {
          next[s.name] = s.on;
        } else {
          delete next[s.name];
        }
        writePrefs(next);
        applyWithFade(next);
      });
    });
  }

  function bindMenu() {
    var trigger = document.getElementById("nut-tai-khoan");
    var panel = document.getElementById("bang-tai-khoan");
    if (!trigger || !panel) return;

    function items() {
      return Array.prototype.slice.call(panel.querySelectorAll('[role="menuitem"]'));
    }

    function open() {
      panel.hidden = false;
      trigger.setAttribute("aria-expanded", "true");
    }

    function close(refocus) {
      panel.hidden = true;
      trigger.setAttribute("aria-expanded", "false");
      if (refocus) trigger.focus();
    }

    trigger.addEventListener("click", function (event) {
      event.stopPropagation();
      if (panel.hidden) {
        open();
      } else {
        close(false);
      }
    });

    trigger.addEventListener("keydown", function (event) {
      if (event.key !== "ArrowDown" && event.key !== "Enter" && event.key !== " ") return;
      if (!panel.hidden) return;
      event.preventDefault();
      open();
      var first = items()[0];
      if (first) first.focus();
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && !panel.hidden) close(true);
    });

    document.addEventListener("click", function (event) {
      if (panel.hidden) return;
      if (panel.contains(event.target) || trigger.contains(event.target)) return;
      close(false);
    });

    panel.addEventListener("keydown", function (event) {
      if (event.key !== "ArrowDown" && event.key !== "ArrowUp") return;
      var list = items();
      var at = list.indexOf(document.activeElement);
      if (at === -1) return;
      event.preventDefault();
      var step = event.key === "ArrowDown" ? 1 : -1;
      list[(at + step + list.length) % list.length].focus();
    });
  }

  function start() {
    apply(readPrefs());
    bindTheme();
    bindSwitches();
    bindMenu();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }
})();

// Thông báo về lưu trữ: hiện một lần, rồi thôi. Ghi cùng khoá với cài đặt
// hiển thị nên không sinh thêm cookie nào — mà thêm cookie để báo về cookie
// thì thật buồn cười.
(function () {
  var thanh = document.getElementById("thong-bao-luu-tru");
  var nut = document.getElementById("hieu-luu-tru");
  if (!thanh || !nut) return;

  var KEY = "gals-hien-thi";
  function doc() {
    try { return JSON.parse(localStorage.getItem(KEY) || "{}") || {}; } catch (e) { return {}; }
  }
  var prefs = doc();
  if (prefs.hieu_luu_tru) return;

  thanh.hidden = false;
  nut.addEventListener("click", function () {
    thanh.hidden = true;
    var p = doc();
    p.hieu_luu_tru = true;
    try { localStorage.setItem(KEY, JSON.stringify(p)); } catch (e) {}
  });
})();
