"use strict";

(() => {
  const STORAGE_KEY = "bunkerfrequenz.ui-prefs.v1";
  const ASSET_REVISION = document.querySelector('meta[name="bunker-asset-revision"]')?.content || "";
  const DEFAULTS = Object.freeze({ compact: false, highContrast: false, largeText: false });
  const CLASS_BY_PREF = Object.freeze({
    compact: "ui-compact",
    highContrast: "ui-high-contrast",
    largeText: "ui-large-text"
  });
  let current = { ...DEFAULTS };

  function assetUrl(filename) {
    if (!ASSET_REVISION) return filename;
    const url = new URL(filename, document.baseURI);
    url.searchParams.set("v", ASSET_REVISION);
    return url.href;
  }

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

  function appendModule(filename, datasetKey) {
    if (document.querySelector(`script[data-${datasetKey}="true"]`)) return;
    const script = document.createElement("script");
    script.src = assetUrl(filename);
    script.defer = true;
    script.dataset[datasetKey.replace(/-([a-z])/g, (_, letter) => letter.toUpperCase())] = "true";
    document.head.append(script);
  }

  function ensureFocusModule() {
    appendModule("control_deck_focus.js", "control-deck-focus");
  }

  function ensureDistrictBiographyModule() {
    appendModule("district_biography.js", "district-biography");
  }

  function ensureFinanceStatementExportModule() {
    appendModule("finance_statement_export.js", "finance-statement-export");
  }

  function ensureSceneJobPayoutPreviewModule() {
    appendModule("scene_job_payout_preview.js", "scene-job-payout-preview");
  }

  function ensureRecoveryActionsModule() {
    appendModule("recovery_actions_ui.js", "recovery-actions");
  }

  function ensureMapUsabilityModule() {
    appendModule("map_usability.js", "map-usability");
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

  window.BunkerUIPrefs = Object.freeze({ init, set, get, reset, assetRevision: ASSET_REVISION });
})();