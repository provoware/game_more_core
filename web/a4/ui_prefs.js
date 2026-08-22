"use strict";

(() => {
  const STORAGE_KEY = "bunkerfrequenz.ui-prefs.v1";
  const DEFAULTS = Object.freeze({ compact: false, highContrast: false, largeText: false });
  const CLASS_BY_PREF = Object.freeze({
    compact: "ui-compact",
    highContrast: "ui-high-contrast",
    largeText: "ui-large-text"
  });
  let current = { ...DEFAULTS };

  function normalize(value) {
    const source = value && typeof value === "object" ? value : {};
    return Object.fromEntries(
      Object.keys(DEFAULTS).map((key) => [key, source[key] === true])
    );
  }

  function load() {
    try {
      current = normalize(JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}"));
    } catch {
      current = { ...DEFAULTS };
    }
    return { ...current };
  }

  function save() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(current));
    } catch {
      // Anzeigeoptionen sind optional; fehlender Storage darf das Spiel nie blockieren.
    }
  }

  function apply() {
    for (const [key, className] of Object.entries(CLASS_BY_PREF)) {
      document.body.classList.toggle(className, current[key] === true);
      const control = document.querySelector(`[data-ui-pref="${key}"]`);
      if (control instanceof HTMLInputElement) control.checked = current[key] === true;
    }
  }

  function set(key, enabled) {
    if (!(key in DEFAULTS)) return;
    current = { ...current, [key]: enabled === true };
    save();
    apply();
  }

  function get() {
    return { ...current };
  }

  function reset() {
    current = { ...DEFAULTS };
    save();
    apply();
  }

  function init() {
    load();
    apply();
    for (const control of document.querySelectorAll("[data-ui-pref]")) {
      control.addEventListener("change", () => set(control.dataset.uiPref, control.checked));
    }
    const resetButton = document.getElementById("ui-prefs-reset");
    if (resetButton) resetButton.addEventListener("click", reset);
  }

  window.BunkerUIPrefs = Object.freeze({ init, set, get, reset });
})();
