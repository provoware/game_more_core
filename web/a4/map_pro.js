"use strict";

(() => {
  let activeFilter = "all";
  let selectedKey = null;
  let currentModel = null;
  const view = { zoom: 1, panX: 0, panY: 0 };

  const FILTERS = new Set(["all", "owned", "prime", "hall"]);
  const MIN_ZOOM = 1;
  const MAX_ZOOM = 2.2;
  const ZOOM_STEP = 0.2;
  const PAN_STEP = 8;

  function node(tag, className, text) {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (text !== undefined && text !== null) element.textContent = String(text);
    return element;
  }

  function displayId(value) {
    return String(value || "").replaceAll("_", " ").toUpperCase();
  }

  function bounded(value) {
    const numeric = Number(value);
    return Number.isFinite(numeric) ? Math.max(0, Math.min(100, numeric)) : 0;
  }

  function clamp(value, minimum, maximum) {
    return Math.max(minimum, Math.min(maximum, value));
  }

  function money(cents) {
    return new Intl.NumberFormat("de-DE", { style: "currency", currency: "EUR" }).format((Number(cents) || 0) / 100);
  }

  function matchesFilter(location) {
    if (activeFilter === "owned") return location.owned === true;
    if (activeFilter === "prime") return ["prime", "legendary"].includes(location.tier);
    if (activeFilter === "hall") return location.is_hall_of_tribute === true;
    return true;
  }

  function setSelected(key) {
    selectedKey = key;
    document.querySelectorAll("#berlin-map-canvas .is-selected").forEach((item) => item.classList.remove("is-selected"));
    const target = document.querySelector(`#berlin-map-canvas [data-map-key="${CSS.escape(key)}"]`);
    if (target) target.classList.add("is-selected");
  }

  function detailMetric(label, value) {
    const item = node("div", "map-detail-metric");
    item.append(node("span", "map-detail-label", label), node("strong", "", value));
    return item;
  }

  function clearDetail(title, text) {
    const host = document.getElementById("map-detail");
    if (!host) return;
    host.replaceChildren();
    host.append(node("p", "eyebrow", "MAP // DETAIL"), node("h3", "map-detail-title", title), node("p", "map-detail-copy", text));
  }

  function showDistrict(district) {
    const host = document.getElementById("map-detail");
    if (!host) return;
    setSelected(`district:${district.district_id}`);
    host.replaceChildren();
    host.append(node("p", "eyebrow", "DISTRICT"), node("h3", "map-detail-title", displayId(district.district_id)));
    const metrics = node("div", "map-detail-grid");
    metrics.append(
      detailMetric("Heat", district.metrics.heat),
      detailMetric("Prestige", district.metrics.prestige),
      detailMetric("Polizeidruck", district.metrics.police_pressure),
      detailMetric("Szene", district.metrics.scene_activity)
    );
    host.append(metrics, node("p", "map-detail-copy", "Bestätigte Living-District-Werte. Die Karte verändert diese Werte nicht."));
  }

  function showLocation(location) {
    const host = document.getElementById("map-detail");
    if (!host) return;
    setSelected(`location:${location.location_id}`);
    host.replaceChildren();
    const kind = location.is_hall_of_tribute ? "HALL OF TRIBUTE" : (location.owned ? "EIGENTUM" : "LOCATION");
    host.append(node("p", "eyebrow", kind), node("h3", "map-detail-title", displayId(location.location_id)));

    const badges = node("div", "map-detail-badges");
    badges.append(node("span", `map-chip tier-${location.tier}`, location.tier.toUpperCase()));
    badges.append(node("span", "map-chip", `SCORE ${location.score.toFixed(1)}`));
    if (location.rank != null) badges.append(node("span", "map-chip", `RANG #${location.rank}`));
    if (location.owned) badges.append(node("span", "map-chip owned", "DEIN ORT"));
    host.append(badges);

    const values = node("div", "map-detail-grid");
    values.append(
      detailMetric("Prestige", location.values.prestige),
      detailMetric("Audience", location.values.audience_pull),
      detailMetric("Risiko", location.values.risk),
      detailMetric("Underground", location.values.underground_factor),
      detailMetric("Utility", location.values.utility)
    );
    host.append(values);

    if (location.purchasable) {
      host.append(node("p", "map-detail-copy", `Katalogpreis: ${money(location.purchase_price_cents)} · Besitz: ${location.owned ? "bestätigt" : "offen"}`));
    }

    if (location.upgrades.length) {
      const upgradeTitle = node("h4", "map-detail-subtitle", `Ausbau · ${location.upgrade_level_total} Level gesamt`);
      const list = node("div", "map-upgrade-list");
      for (const upgrade of location.upgrades) {
        const item = node("div", "map-upgrade-item");
        item.append(node("span", "", displayId(upgrade.upgrade_id)), node("strong", "", `L${upgrade.level}/${upgrade.max_level}`));
        list.append(item);
      }
      host.append(upgradeTitle, list);
    }

    host.append(node("p", "map-detail-copy", "Score, Tier, Eigentum und Ausbaulevel stammen aus bestätigten Projections. Kaufen und Ausbauen bleibt im Property-Panel."));
  }

  function districtElement(district) {
    const button = node("button", "map-district", displayId(district.district_id));
    button.type = "button";
    button.dataset.mapKey = `district:${district.district_id}`;
    button.style.left = `${district.map_box.x}%`;
    button.style.top = `${district.map_box.y}%`;
    button.style.width = `${district.map_box.w}%`;
    button.style.height = `${district.map_box.h}%`;
    button.style.setProperty("--district-heat", String(bounded(district.metrics.heat) / 100));
    button.setAttribute(
      "aria-label",
      `${displayId(district.district_id)}. Heat ${district.metrics.heat}, Prestige ${district.metrics.prestige}, Polizeidruck ${district.metrics.police_pressure}, Szene ${district.metrics.scene_activity}.`
    );
    button.addEventListener("click", () => showDistrict(district));
    button.addEventListener("focus", () => showDistrict(district));
    return button;
  }

  function locationElement(location) {
    const classes = ["map-marker", `tier-${location.tier}`];
    if (location.owned) classes.push("owned");
    if (location.is_hall_of_tribute) classes.push("hall");
    const button = node("button", classes.join(" "));
    button.type = "button";
    button.dataset.mapKey = `location:${location.location_id}`;
    button.dataset.locationId = location.location_id;
    button.style.left = `${location.position.x}%`;
    button.style.top = `${location.position.y}%`;
    button.hidden = !matchesFilter(location);
    const glyph = node("span", "map-marker-glyph", location.is_hall_of_tribute ? "H" : String(location.rank || "•"));
    const label = node("span", "map-marker-label", displayId(location.location_id));
    button.append(glyph, label);
    const ownership = location.owned ? ", Eigentum bestätigt" : "";
    const hall = location.is_hall_of_tribute ? ", Hall of Tribute" : "";
    button.setAttribute("aria-label", `${displayId(location.location_id)}, ${location.tier}, Score ${location.score.toFixed(1)}${ownership}${hall}.`);
    button.addEventListener("click", () => showLocation(location));
    button.addEventListener("focus", () => showLocation(location));
    return button;
  }

  function maxPan() {
    return Math.max(0, (view.zoom - 1) * 50);
  }

  function normalizeView() {
    view.zoom = clamp(Number(view.zoom) || MIN_ZOOM, MIN_ZOOM, MAX_ZOOM);
    const limit = maxPan();
    view.panX = clamp(Number(view.panX) || 0, -limit, limit);
    view.panY = clamp(Number(view.panY) || 0, -limit, limit);
  }

  function transformed(value, pan) {
    return 50 + (value - 50) * view.zoom + pan;
  }

  function updateViewStatus(message) {
    const status = document.getElementById("map-view-status");
    if (!status) return;
    status.textContent = message || `Ansicht ${view.zoom.toFixed(1)}× · Pan X ${Math.round(view.panX)} · Y ${Math.round(view.panY)}`;
  }

  function applyView(model = currentModel) {
    if (!model) return;
    normalizeView();
    for (const district of model.districts) {
      const element = document.querySelector(`#berlin-map-canvas [data-map-key="${CSS.escape(`district:${district.district_id}`)}"]`);
      if (!element) continue;
      element.style.left = `${transformed(district.map_box.x, view.panX)}%`;
      element.style.top = `${transformed(district.map_box.y, view.panY)}%`;
      element.style.width = `${district.map_box.w * view.zoom}%`;
      element.style.height = `${district.map_box.h * view.zoom}%`;
    }
    for (const location of model.locations) {
      const element = document.querySelector(`#berlin-map-canvas [data-map-key="${CSS.escape(`location:${location.location_id}`)}"]`);
      if (!element) continue;
      element.style.left = `${transformed(location.position.x, view.panX)}%`;
      element.style.top = `${transformed(location.position.y, view.panY)}%`;
    }
    updateViewStatus();
  }

  function changeZoom(delta) {
    view.zoom = Math.round(clamp(view.zoom + delta, MIN_ZOOM, MAX_ZOOM) * 10) / 10;
    applyView();
  }

  function panBy(deltaX, deltaY) {
    view.panX += deltaX;
    view.panY += deltaY;
    applyView();
  }

  function resetView() {
    view.zoom = 1;
    view.panX = 0;
    view.panY = 0;
    applyView();
    updateViewStatus("Gesamtansicht 1.0× wiederhergestellt.");
  }

  function selectedCenter(model) {
    if (!selectedKey || !model) return null;
    if (selectedKey.startsWith("district:")) {
      const id = selectedKey.slice("district:".length);
      const district = model.districts.find((item) => item.district_id === id);
      return district ? {
        x: district.map_box.x + district.map_box.w / 2,
        y: district.map_box.y + district.map_box.h / 2,
        label: displayId(district.district_id),
      } : null;
    }
    if (selectedKey.startsWith("location:")) {
      const id = selectedKey.slice("location:".length);
      const location = model.locations.find((item) => item.location_id === id);
      return location ? { x: location.position.x, y: location.position.y, label: displayId(location.location_id) } : null;
    }
    return null;
  }

  function focusSelected() {
    const target = selectedCenter(currentModel);
    if (!target) {
      updateViewStatus("Erst einen Bezirk oder Ort auswählen.");
      return;
    }
    view.zoom = Math.max(view.zoom, 1.6);
    view.panX = -(target.x - 50) * view.zoom;
    view.panY = -(target.y - 50) * view.zoom;
    applyView();
    updateViewStatus(`${target.label} fokussiert · ${view.zoom.toFixed(1)}×.`);
  }

  function mapViewButton(label, action, handler, ariaLabel = label) {
    const button = node("button", "utility-button", label);
    button.type = "button";
    button.dataset.mapViewAction = action;
    button.setAttribute("aria-label", ariaLabel);
    button.addEventListener("click", handler);
    return button;
  }

  function ensureViewControls() {
    const canvas = document.getElementById("berlin-map-canvas");
    if (!canvas || document.getElementById("map-view-controls")) return;
    const controls = node("div", "inline-actions");
    controls.id = "map-view-controls";
    controls.setAttribute("role", "group");
    controls.setAttribute("aria-label", "Kartenansicht steuern");
    controls.append(
      mapViewButton("−", "zoom-out", () => changeZoom(-ZOOM_STEP), "Karte verkleinern"),
      mapViewButton("1:1", "reset", resetView, "Gesamtansicht wiederherstellen"),
      mapViewButton("+", "zoom-in", () => changeZoom(ZOOM_STEP), "Karte vergrößern"),
      mapViewButton("←", "pan-left", () => panBy(PAN_STEP, 0), "Kartenausschnitt nach links verschieben"),
      mapViewButton("↑", "pan-up", () => panBy(0, PAN_STEP), "Kartenausschnitt nach oben verschieben"),
      mapViewButton("↓", "pan-down", () => panBy(0, -PAN_STEP), "Kartenausschnitt nach unten verschieben"),
      mapViewButton("→", "pan-right", () => panBy(-PAN_STEP, 0), "Kartenausschnitt nach rechts verschieben"),
      mapViewButton("AUSWAHL FOKUS", "focus-selected", focusSelected, "Ausgewählten Bezirk oder Ort fokussieren")
    );
    const status = node("p", "selection-hint", "Gesamtansicht 1.0×.");
    status.id = "map-view-status";
    status.setAttribute("role", "status");
    status.setAttribute("aria-live", "polite");
    canvas.before(controls, status);
  }

  function updateFilterButtons() {
    document.querySelectorAll("[data-map-filter]").forEach((button) => {
      const selected = button.dataset.mapFilter === activeFilter;
      button.classList.toggle("primary", selected);
      button.setAttribute("aria-pressed", selected ? "true" : "false");
    });
  }

  function bindFilters(model) {
    document.querySelectorAll("[data-map-filter]").forEach((button) => {
      button.onclick = () => {
        const filter = button.dataset.mapFilter;
        if (!FILTERS.has(filter)) return;
        activeFilter = filter;
        updateFilterButtons();
        document.querySelectorAll("#berlin-map-canvas [data-location-id]").forEach((marker) => {
          const location = model.locations.find((item) => item.location_id === marker.dataset.locationId);
          marker.hidden = !location || !matchesFilter(location);
        });
        const visible = model.locations.find(matchesFilter);
        if (visible) showLocation(visible);
        else clearDetail("Keine Treffer", "Dieser reine Sichtfilter blendet alle Locations aus. Spielzustand wurde nicht verändert.");
      };
    });
    updateFilterButtons();
  }

  function render(model) {
    const panel = document.getElementById("map-pro-panel");
    const canvas = document.getElementById("berlin-map-canvas");
    if (!panel || !canvas) return;
    currentModel = model || null;
    if (!model) {
      panel.classList.add("hidden");
      canvas.replaceChildren();
      return;
    }

    panel.classList.remove("hidden");
    document.getElementById("map-district-count").textContent = String(model.summary.district_count);
    document.getElementById("map-location-count").textContent = String(model.summary.location_count);
    document.getElementById("map-owned-count").textContent = String(model.summary.owned_count);

    ensureViewControls();
    canvas.replaceChildren();
    for (const district of model.districts) canvas.append(districtElement(district));
    for (const location of model.locations) canvas.append(locationElement(location));
    bindFilters(model);
    applyView(model);

    const selected = selectedKey && model.locations.find((item) => `location:${item.location_id}` === selectedKey);
    const first = selected || model.locations.find(matchesFilter);
    if (first) showLocation(first);
    else clearDetail("Berlin Ops", "Wähle einen Bezirk oder Ort aus.");
  }

  window.BunkerMapPro = Object.freeze({ render });
})();