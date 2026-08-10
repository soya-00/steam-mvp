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

  var SWITCHES = [
    { name: "motion", on: "giam", attr: "motion" },
    { name: "nen", on: "phang", attr: "nen" }
  ];

  function apply(prefs) {
    SWITCHES.forEach(function (s) {
      if (prefs[s.name] === s.on) {
        document.documentElement.dataset[s.attr] = s.on;
      } else {
        delete document.documentElement.dataset[s.attr];
      }
    });
  }

  function bindSwitches() {
    var prefs = readPrefs();
    SWITCHES.forEach(function (s) {
      var box = document.querySelector('input[data-pref="' + s.name + '"]');
      if (!box) return;
      box.checked = prefs[s.name] === s.on;
      box.addEventListener("change", function () {
        var next = readPrefs();
        if (box.checked) {
          next[s.name] = s.on;
        } else {
          delete next[s.name];
        }
        writePrefs(next);
        apply(next);
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
    bindSwitches();
    bindMenu();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }
})();
