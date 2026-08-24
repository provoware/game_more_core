"use strict";

(() => {
  const baseMap = window.BunkerMapPro;
  if (!baseMap?.render) return;

  function ensureStyles() {
    if (document.querySelector('link[data-avatar-map-presence="true"]')) return;
    const link = document.createElement("link");
    link.rel = "stylesheet";
    const current = document.currentScript?.src || document.baseURI;
    link.href = new URL("avatar_map_presence.css", current).href;
    link.dataset.avatarMapPresence = "true";
    document.head.append(link);
  }

  function confirmedPreview() {
    const source = document.querySelector(".hud-crew-preview");
    const host = document.querySelector(".hud-crew-identity");
    if (!(source instanceof HTMLElement) || !(host instanceof HTMLElement) || host.hidden) return null;
    return source;
  }

  function cloneBadge(className) {
    const source = confirmedPreview();
    if (!source) return null;
    const badge = source.cloneNode(true);
    badge.className = className;
    badge.removeAttribute("id");
    badge.setAttribute("aria-hidden", "true");
    return badge;
  }

  function syncOwnedMarkers() {
    for (const marker of document.querySelectorAll("#berlin-map-canvas .map-marker.owned")) {
      if (marker.querySelector(".map-crew-badge")) continue;
      const badge = cloneBadge("map-crew-badge");
      if (badge) marker.append(badge);
    }
  }

  function syncOwnedDetail() {
    const detail = document.getElementById("map-detail");
    if (!(detail instanceof HTMLElement)) return;
    const owned = detail.querySelector(".map-chip.owned");
    if (!owned || detail.querySelector(".map-detail-crew")) return;
    const badge = cloneBadge("map-detail-crew-preview");
    if (!badge) return;
    const identity = document.createElement("div");
    identity.className = "map-detail-crew";
    identity.setAttribute("aria-label", "Bestätigte Crew-Marke für diesen eigenen Ort");
    const copy = document.createElement("span");
    copy.textContent = "DEINE CREW";
    identity.append(badge, copy);
    detail.querySelector(".map-detail-title")?.after(identity);
  }

  function sync() {
    syncOwnedMarkers();
    syncOwnedDetail();
  }

  ensureStyles();
  window.BunkerMapPro = Object.freeze({
    render(model) {
      baseMap.render(model);
      sync();
    }
  });

  const canvas = document.getElementById("berlin-map-canvas");
  canvas?.addEventListener("click", () => queueMicrotask(syncOwnedDetail));
  canvas?.addEventListener("focusin", () => queueMicrotask(syncOwnedDetail));
})();
