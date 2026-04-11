/**
 * Lightweight UI helpers (no Bootstrap).
 * - Mobile nav toggle
 * - Dropdown toggle on small screens
 * - Flash dismiss buttons
 * - Simple accessible modal
 */

function qs(sel, root) {
  return (root || document).querySelector(sel);
}

function qsa(sel, root) {
  return Array.prototype.slice.call((root || document).querySelectorAll(sel));
}

// Flash close
document.addEventListener("click", function (e) {
  var btn = e.target.closest("[data-flash-close]");
  if (!btn) return;
  var flash = btn.closest(".flash");
  if (flash) flash.remove();
});

// Nav toggle
document.addEventListener("DOMContentLoaded", function () {
  var toggle = qs("[data-nav-toggle]");
  var nav = qs("[data-nav]");
  if (!toggle || !nav) return;

  function setOpen(open) {
    nav.classList.toggle("is-open", open);
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
  }

  toggle.addEventListener("click", function () {
    setOpen(!nav.classList.contains("is-open"));
  });

  // Dropdown toggle (click) for mobile
  qsa("[data-dropdown-toggle]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var dd = btn.closest("[data-dropdown]");
      var open = dd.classList.toggle("open");
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    });
  });

  // Close nav when clicking a link (mobile)
  qsa(".site-nav a").forEach(function (a) {
    a.addEventListener("click", function () {
      setOpen(false);
    });
  });
});

// Simple modal
window.HMSModal = (function () {
  var active = null;
  var lastFocus = null;

  function open(id) {
    var el = document.getElementById(id);
    if (!el) return;
    lastFocus = document.activeElement;
    active = el;
    el.classList.add("open");
    el.setAttribute("aria-hidden", "false");

    var focusable = el.querySelector("button, [href], input, select, textarea, [tabindex]:not([tabindex='-1'])");
    if (focusable) focusable.focus();
    document.body.classList.add("modal-open");
  }

  function close() {
    if (!active) return;
    active.classList.remove("open");
    active.setAttribute("aria-hidden", "true");
    document.body.classList.remove("modal-open");
    var prev = lastFocus;
    active = null;
    lastFocus = null;
    if (prev && prev.focus) prev.focus();
  }

  // click outside / close button
  document.addEventListener("click", function (e) {
    if (!active) return;
    if (e.target.matches("[data-modal-close]") || e.target.closest("[data-modal-close]")) {
      close();
      return;
    }
    if (e.target.classList.contains("modal-backdrop")) {
      close();
    }
  });

  // escape
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") close();
  });

  return { open: open, close: close };
})();

