/**
 * PRPCEM College Assistant - Theme Switcher Engine
 * Supports: Dark Modern (default), Light Professional, Blue College,
 * Purple Modern, Green Academic. Saves to localStorage.
 */

(function () {
  const THEME_KEY = "prpcem_assistant_theme";
  const DEFAULT_THEME = "dark-modern";

  function initTheme() {
    const savedTheme = localStorage.getItem(THEME_KEY) || DEFAULT_THEME;
    applyTheme(savedTheme);
  }

  function applyTheme(themeName) {
    if (themeName === "dark-modern") {
      document.documentElement.removeAttribute("data-theme");
    } else {
      document.documentElement.setAttribute("data-theme", themeName);
    }
    localStorage.setItem(THEME_KEY, themeName);

    // Update active state in theme selector modal if present
    document.querySelectorAll(".theme-option-row").forEach(row => {
      if (row.getAttribute("data-theme-val") === themeName) {
        row.classList.add("active");
        const radio = row.querySelector("input[type='radio']");
        if (radio) radio.checked = true;
      } else {
        row.classList.remove("active");
        const radio = row.querySelector("input[type='radio']");
        if (radio) radio.checked = false;
      }
    });
  }

  // Expose globally
  window.ThemeManager = {
    init: initTheme,
    apply: applyTheme,
    getCurrent: function () {
      return localStorage.getItem(THEME_KEY) || DEFAULT_THEME;
    }
  };

  // Run on script load to prevent flash of wrong theme
  initTheme();
})();
