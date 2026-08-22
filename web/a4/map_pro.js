"use strict";

(() => {
  let activeFilter = "all";
  let selectedKey = null;

  const FILTERS = new Set(["all", "owned", "prime", "hall"]);

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
    if (!model) {
      panel.classList.add("hidden");
      canvas.replaceChildren();
      return;
    }

    panel.classList.remove("hidden");
    document.getElementById("map-district-count").textContent = String(model.summary.district_count);
    document.getElementById("map-location-count").textContent = String(model.summary.location_count);
    document.getElementById("map-owned-count").textContent = String(model.summary.owned_count);

    canvas.replaceChildren();
    for (const district of model.districts) canvas.append(districtElement(district));
    for (const location of model.locations) canvas.append(locationElement(location));
    bindFilters(model);

    const selected = selectedKey && model.locations.find((item) => `location:${item.location_id}` === selectedKey);
    const first = selected || model.locations.find(matchesFilter);
    if (first) showLocation(first);
    else clearDetail("Berlin Ops", "Wähle einen Bezirk oder Ort aus.");
  }

  window.BunkerMapPro = Object.freeze({ render });
})();
