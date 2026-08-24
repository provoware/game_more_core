"use strict";

(() => {
  const POLL_MS = 4000;
  const MAX_BACKOFF_MS = 30000;
  const KIND_LABELS = Object.freeze({
    street: "STRASSE",
    district: "BEZIRK",
    crisis: "KRISE"
  });
  const FILTERS = Object.freeze({
    all: Object.freeze({ label: "ALLE", kind: null }),
    street: Object.freeze({ label: "STRASSE", kind: "street" }),
    crisis: Object.freeze({ label: "KRISE", kind: "crisis" }),
    district: Object.freeze({ label: "BEZIRK", kind: "district" })
  });

  let activeFilter = "all";
  let confirmedEntries = [];
  let refreshPromise = null;
  let pollTimer = null;
  let consecutiveFailures = 0;

  function host() {
    return document.getElementById("event-timeline-list");
  }

  function status() {
    return document.getElementById("event-timeline-status");
  }

  function filterHost() {
    return document.getElementById("event-timeline-filters");
  }

  function visibleEntries() {
    const selected = FILTERS[activeFilter];
    if (!selected || selected.kind === null) return confirmedEntries;
    return confirmedEntries.filter((entry) => entry?.kind === selected.kind);
  }

  function syncFilterButtons() {
    const controls = filterHost();
    if (!controls) return;
    for (const button of controls.querySelectorAll("[data-timeline-filter]")) {
      button.setAttribute("aria-pressed", String(button.dataset.timelineFilter === activeFilter));
    }
  }

  function renderCurrent() {
    const list = host();
    const live = status();
    if (!list || !live) return;
    list.replaceChildren();

    if (!confirmedEntries.length) {
      live.textContent = "Noch keine bestätigten Ereignisse in der Timeline.";
      return;
    }

    const visible = visibleEntries();
    if (!visible.length) {
      live.textContent = `Keine bestätigten Ereignisse für Filter ${FILTERS[activeFilter].label}.`;
      return;
    }

    for (const entry of visible) {
      const item = document.createElement("li");
      item.className = "equipment-row";
      const info = document.createElement("div");
      const title = document.createElement("strong");
      const kind = KIND_LABELS[entry?.kind] || "EREIGNIS";
      title.textContent = `${kind} // ${entry?.title || ""}`;
      const body = document.createElement("span");
      body.textContent = entry?.body || "";
      info.append(title, body);
      item.append(info);
      list.append(item);
    }

    const suffix = activeFilter === "all"
      ? `${visible.length} bestätigte Ereignisse`
      : `${visible.length} von ${confirmedEntries.length} bestätigten Ereignissen`;
    live.textContent = `${suffix} · Reihenfolge aus dem Journal.`;
  }

  function render(entries) {
    confirmedEntries = Array.isArray(entries) ? entries : [];
    renderCurrent();
  }

  function setFilter(filterId) {
    if (!Object.hasOwn(FILTERS, filterId)) return;
    activeFilter = filterId;
    syncFilterButtons();
    renderCurrent();
  }

  function ensureFilters() {
    if (filterHost()) return;
    const panel = document.getElementById("event-timeline-panel");
    const live = status();
    if (!panel || !live) return;

    const controls = document.createElement("div");
    controls.id = "event-timeline-filters";
    controls.className = "action-grid";
    controls.setAttribute("role", "group");
    controls.setAttribute("aria-label", "Timeline filtern");

    for (const [filterId, filter] of Object.entries(FILTERS)) {
      const button = document.createElement("button");
      button.type = "button";
      button.dataset.timelineFilter = filterId;
      button.textContent = filter.label;
      button.setAttribute("aria-pressed", String(filterId === activeFilter));
      button.addEventListener("click", () => setFilter(filterId));
      controls.append(button);
    }

    panel.insertBefore(controls, live);
  }

  function nextDelay() {
    if (consecutiveFailures === 0) return POLL_MS;
    return Math.min(MAX_BACKOFF_MS, POLL_MS * (2 ** Math.min(consecutiveFailures, 3)));
  }

  function scheduleRefresh(delay = nextDelay()) {
    if (pollTimer !== null) window.clearTimeout(pollTimer);
    pollTimer = window.setTimeout(() => {
      pollTimer = null;
      void refresh();
    }, delay);
  }

  function refresh() {
    if (document.hidden) return Promise.resolve();
    if (refreshPromise) return refreshPromise;

    refreshPromise = (async () => {
      try {
        const response = await fetch("/api/state", { cache: "no-store" });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const payload = await response.json();
        render(payload?.state?.event_timeline);
        consecutiveFailures = 0;
      } catch (error) {
        consecutiveFailures += 1;
        const live = status();
        if (live) {
          const waitSeconds = Math.round(nextDelay() / 1000);
          live.textContent = `Timeline-Verbindung wird automatisch repariert · Versuch ${consecutiveFailures} · nächste Prüfung in ${waitSeconds}s · ${error.message}`;
        }
      } finally {
        refreshPromise = null;
        scheduleRefresh();
      }
    })();
    return refreshPromise;
  }

  document.addEventListener("visibilitychange", () => {
    if (document.hidden) {
      if (pollTimer !== null) window.clearTimeout(pollTimer);
      pollTimer = null;
      return;
    }
    consecutiveFailures = 0;
    void refresh();
  });

  window.addEventListener("bunker:transport-retry", (event) => {
    if (event.detail?.path !== "/api/state") return;
    const live = status();
    if (live) live.textContent = "Timeline-Verbindung wird automatisch neu aufgebaut …";
  });

  window.BunkerEventTimeline = Object.freeze({ render, refresh, setFilter, scheduleRefresh });
  ensureFilters();
  void refresh();
})();