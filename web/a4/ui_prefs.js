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
  const CONFIRMED_FX_COMMANDS = new Set(["street.walk", "recovery.run", "incident.resolve"]);
  const CONFIRMED_FX_CLASSES = [
    "confirmed-fx",
    "confirmed-fx-positive",
    "confirmed-fx-negative",
    "confirmed-fx-neutral"
  ];
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

  function ensureMotionDepthStylesheet() {
    if (document.querySelector('link[data-motion-depth="true"]')) return;
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = assetUrl("motion_depth.css");
    link.dataset.motionDepth = "true";
    document.head.append(link);
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

  function confirmedFxSnapshot() {
    const projection = state.projection || {};
    const character = projection.character || {};
    const event = projection.event || {};
    return {
      energy: character.energy,
      stress: character.stress,
      reputation: character.reputation,
      budget: event.budget_cents,
      streetText: document.getElementById("street-result")?.textContent || "",
      recoveryText: document.getElementById("jobs-recovery-feedback")?.textContent || "",
      incidentText: document.getElementById("incident-content")?.textContent || ""
    };
  }

  function pulseConfirmedElement(element, tone = "neutral") {
    if (!(element instanceof HTMLElement)) return;
    element.classList.remove(...CONFIRMED_FX_CLASSES);
    void element.offsetWidth;
    element.classList.add("confirmed-fx", `confirmed-fx-${tone}`);
    window.setTimeout(() => element.classList.remove(...CONFIRMED_FX_CLASSES), 900);
  }

  function resourceTone(key, before, after) {
    if (before == null || after == null || before === after) return null;
    if (key === "stress") return after < before ? "positive" : "negative";
    return after > before ? "positive" : "negative";
  }

  function renderConfirmedEventFx(commandType, before) {
    const after = confirmedFxSnapshot();
    let visibleChange = false;

    for (const [key, elementId] of [
      ["energy", "hud-energy"],
      ["stress", "hud-stress"],
      ["reputation", "hud-reputation"],
      ["budget", "hud-budget"]
    ]) {
      const tone = resourceTone(key, before[key], after[key]);
      if (!tone) continue;
      pulseConfirmedElement(document.getElementById(elementId), tone);
      visibleChange = true;
    }

    if (commandType === "street.walk" && before.streetText !== after.streetText) {
      const street = document.getElementById("street-result");
      const polarity = street?.dataset.polarity;
      const tone = polarity === "positive" || polarity === "negative" ? polarity : "neutral";
      pulseConfirmedElement(street, tone);
      visibleChange = true;
    }

    if (commandType === "recovery.run" && before.recoveryText !== after.recoveryText) {
      pulseConfirmedElement(document.getElementById("jobs-recovery-feedback"), "neutral");
      visibleChange = true;
    }

    if (commandType === "incident.resolve" && before.incidentText !== after.incidentText) {
      pulseConfirmedElement(document.getElementById("incident-panel"), "neutral");
      visibleChange = true;
    }

    return visibleChange;
  }

  function installConfirmedEventFx() {
    if (window.__bunkerConfirmedEventFxInstalled || typeof sendCommand !== "function") return;
    const baseSendCommand = sendCommand;
    sendCommand = async function sendCommandWithConfirmedEventFx(command) {
      const before = confirmedFxSnapshot();
      await baseSendCommand(command);
      if (!CONFIRMED_FX_COMMANDS.has(command?.type)) return;
      window.setTimeout(() => renderConfirmedEventFx(command.type, before), 0);
    };
    window.__bunkerConfirmedEventFxInstalled = true;
  }

  function copyConfirmedCrewPreview() {
    const source = document.getElementById("crew-identity-preview");
    const host = document.querySelector(".hud-crew-identity");
    if (!(source instanceof HTMLElement) || !(host instanceof HTMLElement)) return;
    const symbol = source.querySelector(".crew-identity-symbol")?.textContent || "★";
    const mark = source.querySelector(".crew-identity-mark")?.textContent || "";
    const preview = host.querySelector(".hud-crew-preview");
    const symbolNode = host.querySelector(".hud-crew-symbol");
    const markNode = host.querySelector(".hud-crew-mark");
    if (!(preview instanceof HTMLElement) || !(symbolNode instanceof HTMLElement) || !(markNode instanceof HTMLElement)) return;
    preview.dataset.mode = source.dataset.mode || "flag";
    preview.style.background = source.style.background;
    preview.style.setProperty("--crew-accent", source.style.getPropertyValue("--crew-accent") || "#ff5a1f");
    symbolNode.textContent = symbol;
    markNode.textContent = mark;
    markNode.hidden = !mark;
    const sourceLabel = source.getAttribute("aria-label") || "Bestätigte Crew-Identität";
    host.setAttribute("aria-label", `Bestätigt: ${sourceLabel}`);
    host.hidden = false;
  }

  function observeConfirmedCrewIdentity() {
    const hudBrand = document.querySelector(".hud-brand");
    const profilePanel = document.getElementById("profile-panel");
    if (!(hudBrand instanceof HTMLElement) || !(profilePanel instanceof HTMLElement)) return;

    let host = hudBrand.querySelector(".hud-crew-identity");
    if (!host) {
      host = document.createElement("span");
      host.className = "hud-crew-identity";
      host.hidden = true;
      host.setAttribute("role", "img");
      host.innerHTML = '<span class="hud-crew-preview"><span class="hud-crew-symbol">★</span><span class="hud-crew-mark" hidden></span></span>';
      hudBrand.append(host);
    }

    let editorObserver = null;
    let observedEditor = null;
    const attachEditor = () => {
      const editor = document.getElementById("crew-identity-editor");
      if (!(editor instanceof HTMLElement)) return;
      if (editor !== observedEditor) {
        editorObserver?.disconnect();
        observedEditor = editor;
        editorObserver = new MutationObserver(() => copyConfirmedCrewPreview());
        editorObserver.observe(editor, { childList: true });
      }
      copyConfirmedCrewPreview();
    };

    const panelObserver = new MutationObserver(attachEditor);
    panelObserver.observe(profilePanel, { childList: true });
    attachEditor();
  }

  function init() {
    load();
    apply();
    ensureMotionDepthStylesheet();
    ensureFocusModule();
    ensureDistrictBiographyModule();
    ensureFinanceStatementExportModule();
    ensureSceneJobPayoutPreviewModule();
    ensureRecoveryActionsModule();
    ensureMapUsabilityModule();
    installConfirmedEventFx();
    observeConfirmedCrewIdentity();
    for (const control of document.querySelectorAll("[data-ui-pref]")) {
      control.addEventListener("change", () => set(control.dataset.uiPref, control.checked));
    }
    const resetButton = document.getElementById("ui-prefs-reset");
    if (resetButton) resetButton.addEventListener("click", reset);
  }

  window.BunkerUIPrefs = Object.freeze({ init, set, get, reset, assetRevision: ASSET_REVISION });
})();
