"use strict";

(() => {
  const STYLE_ID = "map-usability-styles";
  const LEGEND_ID = "map-usability-legend";
  const LABEL_ACTION = "labels";
  const ASSET_REVISION = document.querySelector('meta[name="bunker-asset-revision"]')?.content || "";
  let labelsVisible = false;
  let observer = null;
  let host = null;
  let scheduled = false;

  function assetUrl(filename) {
    if (!ASSET_REVISION) return filename;
    const url = new URL(filename, document.baseURI);
    url.searchParams.set("v", ASSET_REVISION);
    return url.href;
  }

  function ensureStyles() {
    if (document.getElementById(STYLE_ID)) return;
    const link = document.createElement("link");
    link.id = STYLE_ID;
    link.rel = "stylesheet";
    link.href = assetUrl("map_usability.css");
    document.head.append(link);
  }

  function node(tag, className, text) {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (text !== undefined) element.textContent = String(text);
    return element;
  }

  function legendItem(className, label) {
    const item = node("span", "map-legend-item");
    item.append(node("span", `map-legend-dot ${className}`), node("span", "", label));
    return item;
  }

  function ensureLegend() {
    const canvas = document.getElementById("berlin-map-canvas");
    if (!canvas || document.getElementById(LEGEND_ID)) return;
    const legend = node("div", "map-usability-legend");
    legend.id = LEGEND_ID;
    legend.setAttribute("aria-label", "Kartenlegende");
    legend.append(
      node("strong", "", "LEGENDE"),
      legendItem("", "Standard"),
      legendItem("strong", "Strong"),
      legendItem("prime", "Prime"),
      legendItem("legendary", "Legendary"),
      legendItem("owned", "Eigentum"),
      legendItem("hall", "Hall")
    );
    canvas.before(legend);
  }

  function updateLabelButton(button) {
    const canvas = document.getElementById("berlin-map-canvas");
    if (!canvas) return;
    canvas.classList.toggle("map-labels-all", labelsVisible);
    button.setAttribute("aria-pressed", labelsVisible ? "true" : "false");
    button.textContent = labelsVisible ? "BESCHRIFTUNG AN" : "BESCHRIFTUNG";
    button.setAttribute(
      "aria-label",
      labelsVisible ? "Alle Ortsbeschriftungen ausblenden" : "Alle Ortsbeschriftungen einblenden"
    );
  }

  function ensureLabelControl() {
    const controls = document.getElementById("map-view-controls");
    if (!controls || controls.querySelector(`[data-map-view-action="${LABEL_ACTION}"]`)) return;
    const button = node("button", "utility-button", "BESCHRIFTUNG");
    button.type = "button";
    button.dataset.mapViewAction = LABEL_ACTION;
    button.addEventListener("click", () => {
      labelsVisible = !labelsVisible;
      updateLabelButton(button);
    });
    updateLabelButton(button);
    controls.append(button);
  }

  function annotateCanvas() {
    const canvas = document.getElementById("berlin-map-canvas");
    if (!canvas) return;
    canvas.setAttribute(
      "aria-description",
      "Orte sind als kontrastreiche Marker dargestellt. Namen erscheinen bei Fokus, Auswahl oder über die Beschriftungssteuerung."
    );
  }

  function confirmedCrewPreview() {
    const source = document.querySelector(".hud-crew-preview");
    const identity = document.querySelector(".hud-crew-identity");
    if (!(source instanceof HTMLElement) || !(identity instanceof HTMLElement) || identity.hidden) return null;
    return source;
  }

  function crewBadge(className, size) {
    const source = confirmedCrewPreview();
    if (!source) return null;
    const badge = source.cloneNode(true);
    badge.className = `hud-crew-preview ${className}`;
    badge.setAttribute("aria-hidden", "true");
    badge.style.width = size;
    badge.style.height = size;
    badge.style.flex = `0 0 ${size}`;
    return badge;
  }

  function ensureOwnedCrewMarkers() {
    for (const marker of document.querySelectorAll("#berlin-map-canvas .map-marker.owned")) {
      if (marker.querySelector(".map-crew-badge")) continue;
      const badge = crewBadge("map-crew-badge", "1.35rem");
      if (!badge) continue;
      badge.style.position = "absolute";
      badge.style.right = "-.72rem";
      badge.style.bottom = "-.72rem";
      badge.style.zIndex = "6";
      badge.style.pointerEvents = "none";
      marker.append(badge);
    }
  }

  function ensureOwnedCrewDetail() {
    const detail = document.getElementById("map-detail");
    if (!(detail instanceof HTMLElement) || !detail.querySelector(".map-chip.owned") || detail.querySelector(".map-detail-crew")) return;
    const badge = crewBadge("map-detail-crew-preview", "2rem");
    if (!badge) return;
    const identity = node("div", "map-detail-crew");
    identity.setAttribute("aria-label", "Bestätigte Crew-Marke für diesen eigenen Ort");
    Object.assign(identity.style, {
      display: "inline-flex",
      alignItems: "center",
      gap: ".55rem",
      width: "fit-content",
      margin: "-.2rem 0 .55rem",
      padding: ".35rem .5rem",
      border: "1px solid #3e5261",
      borderRadius: ".48rem",
      background: "#090e14",
      color: "var(--accent-2, #62dfff)",
      fontSize: ".62rem",
      fontWeight: "900",
      letterSpacing: ".08em"
    });
    identity.append(badge, node("span", "", "DEINE CREW"));
    detail.querySelector(".map-detail-title")?.after(identity);
  }

  function enhance() {
    ensureStyles();
    ensureLegend();
    ensureLabelControl();
    annotateCanvas();
    ensureOwnedCrewMarkers();
    ensureOwnedCrewDetail();
  }

  function attachObserver() {
    if (observer && host) observer.observe(host, { childList: true, subtree: true });
  }

  function scheduleEnhance() {
    if (scheduled) return;
    scheduled = true;
    window.requestAnimationFrame(() => {
      scheduled = false;
      observer?.disconnect();
      try {
        enhance();
      } catch (error) {
        console.error("BUNKERFREQUENZ Map-UI-Recovery", error);
      } finally {
        attachObserver();
      }
    });
  }

  function init() {
    enhance();
    host = document.getElementById("map-pro-panel") || document.body;
    observer = new MutationObserver(scheduleEnhance);
    attachObserver();
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init, { once: true });
  else init();
})();