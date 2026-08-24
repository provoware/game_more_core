"use strict";

(() => {
  const FOCUS_CLASS = "deck-focus-active";
  const PANEL_CLASS = "is-deck-focused";
  const SIGNAL_CLASS = "next-action-signal";
  const MAX_RECONCILE_FAILURES = 3;
  const OBSERVER_OPTIONS = Object.freeze({
    subtree: true,
    childList: true,
    attributes: true,
    attributeFilter: ["class", "disabled"]
  });
  let focusedPanelId = null;
  let observer = null;
  let workspace = null;
  let reconcileScheduled = false;
  let consecutiveFailures = 0;

  function setTextIfChanged(element, text) {
    if (element.textContent !== text) element.textContent = text;
  }

  function ensureStyles() {
    if (document.getElementById("control-deck-focus-style")) return;
    const style = document.createElement("style");
    style.id = "control-deck-focus-style";
    style.textContent = `
      .deck-focus-button { min-height: 36px; padding: .35rem .6rem; font-size: .66rem; letter-spacing: .06em; }
      body.${FOCUS_CLASS} .workspace > .panel:not(.${PANEL_CLASS}) { display: none !important; }
      body.${FOCUS_CLASS} .workspace { grid-template-columns: 1fr; width: min(1680px, 100%); }
      .panel.${PANEL_CLASS} { grid-column: 1 / -1 !important; min-height: calc(100vh - 10rem); }
      .next-action-signal { position: relative; box-shadow: 0 0 0 3px color-mix(in srgb, var(--accent) 35%, transparent); }
      .next-action-signal::after { content: "NÄCHSTER SCHRITT"; position: absolute; right: .45rem; top: -.65rem; padding: .12rem .35rem; border-radius: 999px; background: var(--accent); color: #101208; font-size: .52rem; font-weight: 900; letter-spacing: .06em; }
      .deck-next-action { display: inline-flex; align-items: center; gap: .35rem; flex: 0 0 auto; padding: .38rem .62rem; border: 1px solid var(--accent); border-radius: 999px; color: var(--accent); font-size: .67rem; font-weight: 850; letter-spacing: .05em; }
      .deck-next-action[data-state="idle"] { border-color: #44515f; color: var(--muted); }
      @media (prefers-reduced-motion: no-preference) { .next-action-signal { animation: deck-next-action-pulse 1.8s ease-in-out infinite; } }
      @keyframes deck-next-action-pulse { 50% { box-shadow: 0 0 0 7px color-mix(in srgb, var(--accent) 10%, transparent); } }
    `;
    document.head.append(style);
  }

  function restoreAll() {
    focusedPanelId = null;
    document.body.classList.remove(FOCUS_CLASS);
    for (const panel of document.querySelectorAll(".workspace > .panel")) panel.classList.remove(PANEL_CLASS);
    syncPanelButtons();
  }

  function focusPanel(panel) {
    if (!(panel instanceof HTMLElement) || !panel.id) return;
    if (focusedPanelId === panel.id) {
      restoreAll();
      return;
    }
    focusedPanelId = panel.id;
    document.body.classList.add(FOCUS_CLASS);
    for (const candidate of document.querySelectorAll(".workspace > .panel")) {
      candidate.classList.toggle(PANEL_CLASS, candidate === panel);
    }
    syncPanelButtons();
    panel.scrollIntoView({ block: "start", behavior: "auto" });
  }

  function ensurePanelButton(panel) {
    if (!(panel instanceof HTMLElement) || !panel.id || panel.classList.contains("hidden")) return;
    const head = panel.querySelector(":scope > .panel-head");
    if (!head || head.querySelector(".deck-focus-button")) return;
    const button = document.createElement("button");
    button.type = "button";
    button.className = "utility-button deck-focus-button";
    button.dataset.focusPanel = panel.id;
    button.addEventListener("click", () => focusPanel(panel));
    head.append(button);
  }

  function syncPanelButtons() {
    for (const panel of document.querySelectorAll(".workspace > .panel")) {
      ensurePanelButton(panel);
      const button = panel.querySelector(":scope > .panel-head .deck-focus-button");
      if (!button) continue;
      const active = focusedPanelId === panel.id;
      setTextIfChanged(button, active ? "GESAMTANSICHT" : "FOKUS");
      button.setAttribute("aria-pressed", String(active));
      button.setAttribute("aria-label", active ? "Gesamtansicht wiederherstellen" : `${panel.querySelector("h2")?.textContent || "Bereich"} fokussieren`);
    }
  }

  function ensureNextActionStatus() {
    const nav = document.querySelector(".quick-nav");
    if (!nav) return null;
    let status = nav.querySelector(".deck-next-action");
    if (!status) {
      status = document.createElement("span");
      status.className = "deck-next-action";
      status.setAttribute("role", "status");
      status.setAttribute("aria-live", "polite");
      nav.prepend(status);
    }
    return status;
  }

  function syncNextAction() {
    const status = ensureNextActionStatus();
    if (!status) return;

    const enabledEventAction = document.querySelector("#event-actions button:not(:disabled)");
    const currentSignal = document.querySelector(`.${SIGNAL_CLASS}`);
    if (currentSignal !== enabledEventAction) {
      currentSignal?.classList.remove(SIGNAL_CLASS);
      if (enabledEventAction instanceof HTMLButtonElement) enabledEventAction.classList.add(SIGNAL_CLASS);
    }

    if (enabledEventAction instanceof HTMLButtonElement) {
      status.dataset.state = "ready";
      setTextIfChanged(status, `NÄCHSTER SCHRITT: ${enabledEventAction.textContent || "EVENT-AKTION"}`);
      return;
    }

    status.dataset.state = "idle";
    setTextIfChanged(status, "NÄCHSTER SCHRITT: Runtime-Gate abwarten");
  }

  function reconcile() {
    if (focusedPanelId) {
      const focused = document.getElementById(focusedPanelId);
      if (!focused || focused.classList.contains("hidden")) restoreAll();
    }
    syncPanelButtons();
    syncNextAction();
  }

  function attachObserver() {
    if (!observer || !workspace || consecutiveFailures >= MAX_RECONCILE_FAILURES) return;
    observer.observe(workspace, OBSERVER_OPTIONS);
  }

  function scheduleReconcile() {
    if (reconcileScheduled || consecutiveFailures >= MAX_RECONCILE_FAILURES) return;
    reconcileScheduled = true;
    window.requestAnimationFrame(() => {
      reconcileScheduled = false;
      observer?.disconnect();
      try {
        reconcile();
        consecutiveFailures = 0;
      } catch (error) {
        consecutiveFailures += 1;
        console.error("BUNKERFREQUENZ Fokus-Recovery", error);
        const status = ensureNextActionStatus();
        if (status) {
          status.dataset.state = "idle";
          setTextIfChanged(
            status,
            consecutiveFailures >= MAX_RECONCILE_FAILURES
              ? "UI-HILFE DEAKTIVIERT · SPIEL BLEIBT BEDIENBAR"
              : `UI-HILFE WIRD REPARIERT · ${consecutiveFailures}/${MAX_RECONCILE_FAILURES}`
          );
        }
      } finally {
        attachObserver();
      }
    });
  }

  function init() {
    ensureStyles();
    reconcile();
    workspace = document.getElementById("workspace");
    if (!workspace) return;
    observer = new MutationObserver(scheduleReconcile);
    attachObserver();
  }

  window.BunkerControlDeckFocus = Object.freeze({
    init,
    restoreAll,
    scheduleReconcile,
    maxReconcileFailures: MAX_RECONCILE_FAILURES
  });
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init, { once: true });
  else init();
})();