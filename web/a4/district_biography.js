"use strict";

(() => {
  const POLL_MS = 4000;
  const LIMIT = 5;

  function displayId(value) {
    return String(value || "").replaceAll("_", " ").toUpperCase();
  }

  function ensureHost() {
    const profile = document.getElementById("profile-panel");
    if (!profile) return null;
    let section = document.getElementById("district-biography");
    if (section) return section;

    section = document.createElement("section");
    section.id = "district-biography";
    section.className = "district-biography";
    section.setAttribute("aria-labelledby", "district-biography-title");

    const eyebrow = document.createElement("p");
    eyebrow.className = "eyebrow";
    eyebrow.textContent = "BERLIN // BESTÄTIGTE ERINNERUNGEN";
    const title = document.createElement("h3");
    title.id = "district-biography-title";
    title.textContent = "Was die Stadt von dir mitträgt";
    const intro = document.createElement("p");
    intro.textContent = "Nur bestätigte Bezirksereignisse aus deiner bestehenden Ereignis-Chronik. Keine neuen Werte, Boni oder erfundenen Zeitangaben.";
    const status = document.createElement("p");
    status.id = "district-biography-status";
    status.className = "notice";
    status.setAttribute("role", "status");
    status.setAttribute("aria-live", "polite");
    status.textContent = "Noch keine bestätigte Berlin-Erinnerung.";
    const list = document.createElement("ol");
    list.id = "district-biography-list";
    list.className = "equipment-list";
    list.setAttribute("aria-label", "Bestätigte Berlin-Erinnerungen");

    section.append(eyebrow, title, intro, status, list);
    const saveButton = document.getElementById("save-profile");
    if (saveButton?.parentElement === profile) profile.insertBefore(section, saveButton);
    else profile.append(section);
    return section;
  }

  function districtEntries(entries) {
    const confirmed = Array.isArray(entries) ? entries : [];
    return confirmed
      .filter((entry) => entry?.kind === "district" && entry?.metadata?.district_id)
      .slice(-LIMIT);
  }

  function deltaText(deltas) {
    const labels = {
      heat: "Heat",
      prestige: "Prestige",
      police_pressure: "Polizeidruck",
      scene_activity: "Szene"
    };
    const parts = [];
    for (const [key, label] of Object.entries(labels)) {
      const value = deltas?.[key];
      if (!Number.isInteger(value) || value === 0) continue;
      parts.push(`${label} ${value > 0 ? "+" : ""}${value}`);
    }
    return parts.join(" · ");
  }

  function render(entries) {
    ensureHost();
    const list = document.getElementById("district-biography-list");
    const status = document.getElementById("district-biography-status");
    if (!list || !status) return;
    list.replaceChildren();

    const memories = districtEntries(entries);
    if (!memories.length) {
      status.textContent = "Noch keine bestätigte Berlin-Erinnerung. Erst ein bestätigtes Bezirksereignis kann hier auftauchen.";
      return;
    }

    for (const entry of memories) {
      const item = document.createElement("li");
      item.className = "equipment-row district-memory";
      item.dataset.sourceEventId = entry.event_id || "";

      const info = document.createElement("div");
      const title = document.createElement("strong");
      title.textContent = `${displayId(entry.metadata.district_id)} // ${entry.title || "Bezirksereignis"}`;
      const body = document.createElement("span");
      body.textContent = entry.body || "";
      info.append(title, body);

      const deltas = deltaText(entry.metadata.deltas);
      if (deltas) {
        const effects = document.createElement("small");
        effects.textContent = `Bestätigte Veränderung: ${deltas}`;
        info.append(effects);
      }
      item.append(info);
      list.append(item);
    }
    status.textContent = `${memories.length} bestätigte Berlin-Erinnerung${memories.length === 1 ? "" : "en"} · Quelle: Ereignis-Chronik.`;
  }

  async function refresh() {
    if (document.hidden) return;
    try {
      const response = await fetch("/api/state", { cache: "no-store" });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const payload = await response.json();
      render(payload?.state?.event_timeline);
    } catch (error) {
      ensureHost();
      const status = document.getElementById("district-biography-status");
      if (status) status.textContent = `Berlin-Erinnerungen vorübergehend nicht verfügbar: ${error.message}`;
    }
  }

  window.BunkerDistrictBiography = Object.freeze({ render, refresh });
  refresh();
  window.setInterval(refresh, POLL_MS);
})();
