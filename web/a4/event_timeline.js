"use strict";

(() => {
  const POLL_MS = 4000;
  const KIND_LABELS = {
    street: "STRASSE",
    district: "BEZIRK",
    crisis: "KRISE"
  };

  function host() {
    return document.getElementById("event-timeline-list");
  }

  function status() {
    return document.getElementById("event-timeline-status");
  }

  function render(entries) {
    const list = host();
    const live = status();
    if (!list || !live) return;
    list.replaceChildren();
    const confirmed = Array.isArray(entries) ? entries : [];
    if (!confirmed.length) {
      live.textContent = "Noch keine bestätigten Ereignisse in der Timeline.";
      return;
    }

    for (const entry of confirmed) {
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
    live.textContent = `${confirmed.length} bestätigte Ereignisse · Reihenfolge aus dem Journal.`;
  }

  async function refresh() {
    if (document.hidden) return;
    try {
      const response = await fetch("/api/state", { cache: "no-store" });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const payload = await response.json();
      const gameState = payload?.state;
      render(gameState?.event_timeline);
      window.BunkerAssistantUI?.render(gameState);
    } catch (error) {
      const live = status();
      if (live) live.textContent = `Timeline vorübergehend nicht verfügbar: ${error.message}`;
    }
  }

  function loadAssistantUi() {
    if (document.querySelector('script[data-assistant-ui="true"]')) return;
    const script = document.createElement("script");
    script.src = "assistant_ui.js";
    script.dataset.assistantUi = "true";
    script.addEventListener("load", refresh, { once: true });
    document.head.append(script);
  }

  window.BunkerEventTimeline = Object.freeze({ render, refresh });
  loadAssistantUi();
  refresh();
  window.setInterval(refresh, POLL_MS);
})();
