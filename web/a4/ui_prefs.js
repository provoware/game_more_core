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

  function ensureFocusModule() {
    if (document.querySelector('script[data-control-deck-focus="true"]')) return;
    const script = document.createElement("script");
    script.src = "control_deck_focus.js";
    script.defer = true;
    script.dataset.controlDeckFocus = "true";
    document.head.append(script);
  }

  function ensureDistrictBiographyModule() {
    if (document.querySelector('script[data-district-biography="true"]')) return;
    const script = document.createElement("script");
    script.src = "district_biography.js";
    script.defer = true;
    script.dataset.districtBiography = "true";
    document.head.append(script);
  }

  function ensureFinanceStatementExportModule() {
    if (document.querySelector('script[data-finance-statement-export="true"]')) return;
    const script = document.createElement("script");
    script.src = "finance_statement_export.js";
    script.defer = true;
    script.dataset.financeStatementExport = "true";
    document.head.append(script);
  }

  function ensureSceneJobPayoutPreviewModule() {
    if (document.querySelector('script[data-scene-job-payout-preview="true"]')) return;
    const script = document.createElement("script");
    script.src = "scene_job_payout_preview.js";
    script.defer = true;
    script.dataset.sceneJobPayoutPreview = "true";
    document.head.append(script);
  }

  function ensureRecoveryActionsModule() {
    if (document.querySelector('script[data-recovery-actions="true"]')) return;
    const script = document.createElement("script");
    script.src = "recovery_actions_ui.js";
    script.defer = true;
    script.dataset.recoveryActions = "true";
    document.head.append(script);
  }

  function ensureMapUsabilityModule() {
    if (document.querySelector('script[data-map-usability="true"]')) return;
    const script = document.createElement("script");
    script.src = "map_usability.js";
    script.defer = true;
    script.dataset.mapUsability = "true";
    document.head.append(script);
  }

  function init() {
    load();
    apply();
    ensureFocusModule();
    ensureDistrictBiographyModule();
    ensureFinanceStatementExportModule();
    ensureSceneJobPayoutPreviewModule();
    ensureRecoveryActionsModule();
    ensureMapUsabilityModule();
    for (const control of document.querySelectorAll("[data-ui-pref]")) {
      control.addEventListener("change", () => set(control.dataset.uiPref, control.checked));
    }
    const resetButton = document.getElementById("ui-prefs-reset");
    if (resetButton) resetButton.addEventListener("click", reset);
  }

  window.BunkerUIPrefs = Object.freeze({ init, set, get, reset });
})();