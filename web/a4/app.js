"use strict";

const $ = (id) => document.getElementById(id);
const state = {
  projection: null,
  busy: false,
  hallMode: "reputation",
  hallCycleType: "weekly",
  streetApproach: "balanced"
};

const ACTION_LABELS = {
  begin_planning: "PLANUNG BEGINNEN",
  begin_procurement: "BESCHAFFUNG BEGINNEN",
  start_transport: "TRANSPORT STARTEN",
  begin_setup: "AUFBAU BEGINNEN",
  confirm_soundcheck: "SOUNDCHECK BESTÄTIGEN",
  start_live: "EVENT STARTEN",
  finish_live: "EVENT BEENDEN",
  finish_teardown: "ABBAU BEENDEN"
};

const BLOCKER_LABELS = {
  wrong_phase: "Falsche Eventphase",
  confirmed_act: "Mindestens ein bestätigter Act fehlt",
  confirmed_acts: "Nicht alle Acts sind bestätigt",
  confirmed_crew: "Crew ist nicht vollständig bestätigt",
  positive_budget: "Positives Budget fehlt",
  equipment_ready: "Equipment ist noch nicht bereit",
  location_required: "Ort fehlt",
  verified_access_required: "Zugang ist nicht bestätigt",
  time_window_required: "Zeitfenster fehlt",
  safety_clearance_required: "Sicherheitsfreigabe fehlt"
};

const POLARITY_LABELS = { positive: "GLÜCK", negative: "PECH", neutral: "RUHIG" };
const HALL_MODE_LABELS = { reputation: "RUF", level: "LEVEL", resonance: "RESONANZ" };
const HALL_CYCLE_LABELS = { weekly: "WOCHE", monthly: "MONAT" };
const MOVEMENT_SYMBOLS = { up: "↑", down: "↓", same: "→", new: "★", unranked: "–" };
const EFFECT_LABELS = {
  budget_delta_cents: "Budget",
  reputation_delta: "Ruf",
  crew_stress_delta: "Crew-Stress",
  stability_delta: "Stabilität",
  heat_delta: "Heat"
};

function commandId(prefix) {
  const suffix = globalThis.crypto?.randomUUID?.() || `${Date.now()}-${Math.random().toString(16).slice(2)}`;
  return `${prefix}:${suffix}`;
}

function log(message, payload = null) {
  const line = `[${new Date().toLocaleTimeString()}] ${message}`;
  $("log").textContent = payload ? `${line}\n${JSON.stringify(payload, null, 2)}\n\n${$("log").textContent}` : `${line}\n${$("log").textContent}`;
}

function money(cents) {
  return new Intl.NumberFormat("de-DE", { style: "currency", currency: "EUR" }).format((cents || 0) / 100);
}

function signed(value) {
  if (!value) return "0";
  return value > 0 ? `+${value}` : String(value);
}

function signedMoney(cents) {
  if (!cents) return money(0);
  return `${cents > 0 ? "+" : "−"}${money(Math.abs(cents))}`;
}

function displayId(value) {
  return String(value || "").replaceAll("_", " ").toUpperCase();
}

async function request(path, options = {}) {
  if (state.busy) throw new Error("Eine Aktion läuft bereits.");
  state.busy = true;
  document.body.classList.add("busy");
  try {
    const response = await fetch(path, options);
    const payload = await response.json();
    if (!response.ok) {
      const detail = payload.detail ? ` – ${payload.detail}` : "";
      throw new Error(`${payload.error_code || "request_failed"}${detail}`);
    }
    return payload;
  } finally {
    state.busy = false;
    document.body.classList.remove("busy");
  }
}

async function refresh() {
  try {
    const payload = await fetch("/api/state", { cache: "no-store" }).then((r) => r.json());
    state.projection = payload.state;
    $("connection-status").textContent = "● BEREIT";
    render();
  } catch (error) {
    $("connection-status").textContent = "● VERBINDUNG FEHLT";
    log(`State-Fehler: ${error.message}`);
  }
}

function setHidden(id, hidden) { $(id).classList.toggle("hidden", hidden); }

function setInputIfIdle(id, value) {
  const input = $(id);
  if (document.activeElement !== input) input.value = value ?? "";
}

function renderHud(p) {
  const event = p.event;
  const character = p.character;
  $("hud-phase").textContent = event ? displayId(event.phase) : "–";
  $("hud-budget").textContent = event ? money(event.budget_cents) : "–";
  $("hud-energy").textContent = character ? String(character.energy) : "–";
  $("hud-stress").textContent = character ? String(character.stress) : "–";
  $("hud-reputation").textContent = character ? String(character.reputation) : "–";
  $("hud-property").textContent = p.properties ? String(p.properties.owned_count || 0) : "–";
}

function ensureCrewIdentityStyles() {
  if (document.querySelector('link[data-crew-identity-style="true"]')) return;
  const link = document.createElement("link");
  link.rel = "stylesheet";
  link.href = "crew_identity.css";
  link.dataset.crewIdentityStyle = "true";
  document.head.append(link);
}

function crewChoiceSelect(id, labelText, choices, selected) {
  const label = document.createElement("label");
  label.textContent = labelText;
  const select = document.createElement("select");
  select.id = id;
  for (const choice of choices || []) {
    const option = document.createElement("option");
    option.value = choice.id;
    option.textContent = choice.label;
    option.selected = choice.id === selected;
    select.append(option);
  }
  label.append(select);
  return label;
}

function readCrewIdentity() {
  const editor = $("crew-identity-editor");
  if (!editor) return null;
  return {
    mode: $("crew-identity-mode").value,
    style: $("crew-identity-style").value,
    symbol: $("crew-identity-symbol-select").value,
    primary_color_id: $("crew-identity-primary").value,
    secondary_color_id: $("crew-identity-secondary").value,
    accent_color_id: $("crew-identity-accent").value,
    mark: $("crew-identity-mark-input").value.trim().toUpperCase()
  };
}

function renderCrewIdentityPreview(crew) {
  const preview = $("crew-identity-preview");
  if (!preview || !crew) return;
  const identity = readCrewIdentity() || crew.identity;
  const colorMap = new Map((crew.choices?.colors || []).map((item) => [item.id, item.value]));
  const symbolMap = new Map((crew.choices?.symbols || []).map((item) => [item.id, item.glyph]));
  const primary = colorMap.get(identity.primary_color_id) || crew.render?.primary || "#101114";
  const secondary = colorMap.get(identity.secondary_color_id) || crew.render?.secondary || "#5e6670";
  const accent = colorMap.get(identity.accent_color_id) || crew.render?.accent || "#ff5a1f";
  const backgrounds = {
    solid: primary,
    split: `linear-gradient(90deg, ${primary} 0 50%, ${secondary} 50% 100%)`,
    band: `linear-gradient(180deg, ${primary} 0 38%, ${secondary} 38% 62%, ${primary} 62% 100%)`,
    diagonal: `linear-gradient(135deg, ${primary} 0 48%, ${secondary} 48% 100%)`
  };
  preview.dataset.mode = identity.mode;
  preview.style.background = backgrounds[identity.style] || primary;
  preview.style.setProperty("--crew-accent", accent);
  $("crew-identity-symbol").textContent = symbolMap.get(identity.symbol) || crew.render?.symbol_glyph || "★";
  $("crew-identity-mark").textContent = identity.mark || "";
  $("crew-identity-mark").hidden = !identity.mark;
  preview.setAttribute("aria-label", `${identity.mode === "logo" ? "Crew-Logo" : "Crew-Fahne"}: ${identity.symbol}, ${identity.style}`);
}

function renderCrewIdentity(crew) {
  if (!crew?.identity || !crew?.choices) return;
  ensureCrewIdentityStyles();
  let editor = $("crew-identity-editor");
  if (editor?.contains(document.activeElement)) return;
  if (!editor) {
    editor = document.createElement("section");
    editor.id = "crew-identity-editor";
    editor.className = "crew-identity-editor";
    editor.setAttribute("aria-labelledby", "crew-identity-title");
    $("save-profile").before(editor);
  }
  editor.replaceChildren();

  const heading = document.createElement("div");
  const eyebrow = document.createElement("p");
  eyebrow.className = "eyebrow";
  eyebrow.textContent = "CREW IDENTITY // SYNC-READY";
  const title = document.createElement("h3");
  title.id = "crew-identity-title";
  title.textContent = "Logo oder Fahne";
  const intro = document.createElement("p");
  intro.textContent = "Baue deine Crew-Marke aus katalogisierten Symbolen, Formen und Farben. Gespeichert wird nur das kleine Identitätsrezept – keine Bilddatei.";
  heading.append(eyebrow, title, intro);

  const layout = document.createElement("div");
  layout.className = "crew-identity-layout";
  const previewWrap = document.createElement("div");
  previewWrap.className = "crew-identity-preview-wrap";
  const preview = document.createElement("div");
  preview.id = "crew-identity-preview";
  preview.className = "crew-identity-preview";
  preview.setAttribute("role", "img");
  const symbol = document.createElement("span");
  symbol.id = "crew-identity-symbol";
  symbol.className = "crew-identity-symbol";
  const mark = document.createElement("span");
  mark.id = "crew-identity-mark";
  mark.className = "crew-identity-mark";
  preview.append(symbol, mark);
  const sync = document.createElement("small");
  sync.textContent = "Späterer Multiplayer-Sync über Character-ID + Identitätsdaten; kein Bildblob.";
  previewWrap.append(preview, sync);

  const controls = document.createElement("div");
  controls.className = "crew-identity-controls";
  const identity = crew.identity;
  controls.append(
    crewChoiceSelect("crew-identity-mode", "Typ", crew.choices.modes, identity.mode),
    crewChoiceSelect("crew-identity-style", "Flächenstil", crew.choices.styles, identity.style),
    crewChoiceSelect("crew-identity-symbol-select", "Symbol", crew.choices.symbols, identity.symbol),
    crewChoiceSelect("crew-identity-primary", "Primärfarbe", crew.choices.colors, identity.primary_color_id),
    crewChoiceSelect("crew-identity-secondary", "Sekundärfarbe", crew.choices.colors, identity.secondary_color_id),
    crewChoiceSelect("crew-identity-accent", "Akzentfarbe", crew.choices.colors, identity.accent_color_id)
  );
  const markLabel = document.createElement("label");
  markLabel.textContent = "Kurzmarke (max. 4)";
  const markInput = document.createElement("input");
  markInput.id = "crew-identity-mark-input";
  markInput.maxLength = 4;
  markInput.autocomplete = "off";
  markInput.value = identity.mark || "";
  markLabel.append(markInput);
  controls.append(markLabel);

  const note = document.createElement("p");
  note.className = "crew-identity-sync-note";
  note.textContent = "Gameplaywerte und Character-ID ändern sich dadurch nicht. Beim Speichern prüft die Runtime alle IDs erneut.";
  layout.append(previewWrap, controls);
  editor.append(heading, layout, note);

  for (const control of controls.querySelectorAll("select, input")) {
    control.addEventListener("input", () => renderCrewIdentityPreview(crew));
    control.addEventListener("change", () => renderCrewIdentityPreview(crew));
  }
  renderCrewIdentityPreview(crew);
}

function renderProfile(character) {
  if (!character) return;
  setInputIfIdle("profile-display-name", character.display_name);
  setInputIfIdle("profile-alias", character.alias);
  setInputIfIdle("profile-nicknames", (character.additional_nicknames || []).join(", "));
  setInputIfIdle("profile-motto", character.motto);
  $("profile-level").textContent = String(character.level);
  $("profile-reputation").textContent = String(character.reputation);
  $("profile-energy").textContent = String(character.energy);
  $("profile-stress").textContent = String(character.stress);
  $("profile-id").textContent = character.character_id;
  renderCrewIdentity(character.crew_identity);
}

function renderStreetApproaches(approaches) {
  const host = $("street-approaches");
  host.replaceChildren();
  const available = Array.isArray(approaches) ? approaches : [];
  if (!available.length) {
    $("street-selected-hint").textContent = "Ansatz: Standard";
    return;
  }
  if (!available.some((item) => item.approach_id === state.streetApproach)) {
    state.streetApproach = available.find((item) => item.selected_by_default)?.approach_id || available[0].approach_id;
  }
  const selected = available.find((item) => item.approach_id === state.streetApproach);
  $("street-selected-hint").textContent = `Ansatz: ${selected?.label || displayId(state.streetApproach)}`;

  for (const approach of available) {
    const button = document.createElement("button");
    const active = approach.approach_id === state.streetApproach;
    button.type = "button";
    button.className = `street-approach-card${active ? " is-selected" : ""}`;
    button.setAttribute("role", "radio");
    button.setAttribute("aria-checked", String(active));
    button.dataset.approachId = approach.approach_id;
    const label = document.createElement("strong");
    label.textContent = approach.label;
    const description = document.createElement("span");
    description.textContent = approach.description;
    button.append(label, description);
    button.addEventListener("click", () => {
      state.streetApproach = approach.approach_id;
      renderStreetApproaches(state.projection?.street_approaches);
    });
    host.append(button);
  }
}

function renderStreetEncounter(encounter) {
  const host = $("street-result");
  host.replaceChildren();
  if (!encounter) {
    host.textContent = "Keine bestätigte Straßenrunde erhalten.";
    return;
  }
  host.dataset.polarity = encounter.polarity || "neutral";
  const approach = (state.projection?.street_approaches || []).find(
    (item) => item.approach_id === encounter.approach_id
  );
  const heading = document.createElement("strong");
  heading.textContent = `${POLARITY_LABELS[encounter.polarity] || "RUNDE"} // ${encounter.title || encounter.encounter_id}`;
  const approachLine = document.createElement("small");
  approachLine.textContent = `Ansatz: ${approach?.label || displayId(encounter.approach_id || "balanced")}`;
  const body = document.createElement("p");
  body.textContent = encounter.body || "";
  const effects = document.createElement("span");
  effects.className = "street-effects";
  effects.textContent = `Energie ${signed(encounter.effects?.energy_delta)} · Stress ${signed(encounter.effects?.stress_delta)} · Ruf ${signed(encounter.effects?.reputation_delta)}`;
  host.append(heading, approachLine, body, effects);
}

function renderDistricts(districts) {
  const host = $("district-list");
  host.replaceChildren();
  if (!districts) return;
  $("district-revision").textContent = String(districts.revision || 0);
  for (const district of districts.entries || []) {
    const row = document.createElement("article");
    row.className = "equipment-row";
    const info = document.createElement("div");
    const title = document.createElement("strong");
    title.textContent = displayId(district.district_id);
    const detail = document.createElement("span");
    const metrics = district.metrics || {};
    detail.textContent = `Heat ${metrics.heat ?? "–"} · Prestige ${metrics.prestige ?? "–"} · Polizeidruck ${metrics.police_pressure ?? "–"} · Szene ${metrics.scene_activity ?? "–"}`;
    info.append(title, detail);
    row.append(info);
    host.append(row);
  }
  const change = districts.last_change;
  $("district-last-change").textContent = change
    ? `Letzte bestätigte Änderung: ${change.district_id} · ${change.source_type} · Heat ${signed(change.deltas?.heat)} · Prestige ${signed(change.deltas?.prestige)} · Polizeidruck ${signed(change.deltas?.police_pressure)} · Szene ${signed(change.deltas?.scene_activity)}`
    : districts.persisted ? "Persistierter District-State ohne neue Änderung." : "Noch keine persistente Bezirksänderung – angezeigt werden die Startwerte.";
}

function renderProperties(properties, propertyUpgrades) {
  const host = $("property-list");
  host.replaceChildren();
  if (!properties) return;
  $("property-owned-count").textContent = `${properties.owned_count || 0} / ${properties.purchasable_count || 0}`;
  const upgradeByLocation = new Map((propertyUpgrades?.entries || []).map((entry) => [entry.location_id, entry]));
  for (const property of properties.entries || []) {
    const row = document.createElement("article");
    row.className = "equipment-row";
    const info = document.createElement("div");
    const title = document.createElement("strong");
    title.textContent = `${displayId(property.location_id)}${property.owned ? " · EIGENTUM" : ""}`;
    const detail = document.createElement("span");
    const upgradeEntry = upgradeByLocation.get(property.location_id);
    const values = upgradeEntry?.effective_values;
    const valueText = values
      ? ` · P ${values.prestige} · Pull ${values.audience_pull} · Risiko ${values.risk} · UG ${values.underground_factor} · Nutzen ${values.utility}`
      : "";
    detail.textContent = `${displayId(property.district_id)} · ${money(property.purchase_price_cents)}${valueText}`;
    info.append(title, detail);
    row.append(info);

    if (!property.owned) {
      const actions = document.createElement("div");
      actions.className = "inline-actions";
      const buy = document.createElement("button");
      buy.textContent = "ÜBERNEHMEN";
      buy.addEventListener("click", () => sendCommand({
        type: "property.purchase",
        command_id: commandId("property-purchase"),
        location_id: property.location_id
      }));
      actions.append(buy);
      row.append(actions);
    } else if (upgradeEntry) {
      const actions = document.createElement("div");
      actions.className = "inline-actions";
      for (const upgrade of upgradeEntry.upgrades || []) {
        const button = document.createElement("button");
        if (upgrade.can_upgrade) {
          button.textContent = `${displayId(upgrade.upgrade_id)} L${upgrade.level}→${upgrade.next_level} · ${money(upgrade.next_cost_cents)}`;
          button.addEventListener("click", () => sendCommand({
            type: "property.upgrade",
            command_id: commandId("property-upgrade"),
            location_id: property.location_id,
            upgrade_id: upgrade.upgrade_id
          }));
        } else {
          button.textContent = `${displayId(upgrade.upgrade_id)} · MAX L${upgrade.level}`;
          button.disabled = true;
          button.className = "disabled-action";
        }
        actions.append(button);
      }
      row.append(actions);
    }
    host.append(row);
  }
}

function renderHallSeason(seasonal) {
  const status = $("hall-season-status");
  const titleStatus = $("hall-season-title-status");
  titleStatus.replaceChildren();
  for (const cycleType of ["weekly", "monthly"]) {
    const button = $(`hall-cycle-${cycleType}`);
    if (button) {
      const selected = cycleType === state.hallCycleType;
      button.classList.toggle("primary", selected);
      button.setAttribute("aria-pressed", String(selected));
    }
  }
  if (!seasonal?.available) {
    status.textContent = "Keine bestätigte Saison verfügbar. Ein lokaler Wochen-/Monatsanker entsteht erst aus einem bestätigten abgeschlossenen Event; Systemzeit allein zählt nicht.";
    titleStatus.textContent = "Keine Saisontitel vergeben.";
    return;
  }
  const cycle = seasonal.cycles?.[state.hallCycleType];
  if (!cycle) {
    status.textContent = `Für ${HALL_CYCLE_LABELS[state.hallCycleType] || state.hallCycleType} liegt kein bestätigter Zyklus vor.`;
    titleStatus.textContent = "Keine Saisontitel vergeben.";
    return;
  }
  const finalLabel = cycle.closed ? "ZYKLUS BESTÄTIGT ABGESCHLOSSEN" : "BESTÄTIGTER ANKER · NOCH NICHT FINAL";
  status.textContent = `${HALL_CYCLE_LABELS[cycle.cycle_type]} ${cycle.cycle_id} · ${finalLabel} · Autorität ${displayId(cycle.authority)}`;
  const modeResult = cycle.modes?.[state.hallMode];
  if (!modeResult?.leader) {
    titleStatus.textContent = "Für diese Metrik gibt es keinen bestätigten Leader.";
    return;
  }
  const leader = modeResult.leader.display_name || modeResult.leader.alias || modeResult.leader.character_id;
  const line = document.createElement("strong");
  if (modeResult.awarded_title) {
    line.textContent = `${modeResult.awarded_title} · ${leader} · bestätigter Rang 1`;
  } else if (!cycle.closed) {
    line.textContent = `${leader} führt · Kandidat: ${modeResult.title_candidate} · Titel erst nach bestätigtem Zyklusabschluss.`;
  } else if (!cycle.confirmed_competition) {
    line.textContent = `${leader} ist lokal Rang 1 · keine bestätigte Konkurrenz, daher kein Titel.`;
  } else {
    line.textContent = `${leader} führt · Titelstatus nicht final bestätigt.`;
  }
  titleStatus.append(line);
  if (cycle.grand_title) {
    const grand = document.createElement("span");
    grand.textContent = `GRAND TITLE: ${cycle.grand_title.title}`;
    titleStatus.append(grand);
  }
  const localTitles = (seasonal.local_titles || []).filter((item) => item.cycle_id === cycle.cycle_id);
  if (localTitles.length) {
    const own = document.createElement("span");
    own.textContent = `DEINE BESTÄTIGTEN TITEL: ${localTitles.map((item) => item.title).join(" · ")}`;
    titleStatus.append(own);
  }
}

function renderHall(hall) {
  const host = $("hall-ranking");
  host.replaceChildren();
  if (!hall) return;
  $("hall-participants").textContent = String(hall.confirmed_participant_count || 0);
  $("hall-status").textContent = hall.network_competition_available
    ? `Bestätigte Konkurrenz aktiv · Top ${hall.top_limit} · keine Ranggleichstände.`
    : "Nur dein bestätigter lokaler Character ist verfügbar. Keine Gegner oder Netzwerkwerte werden erfunden.";
  renderHallSeason(hall.seasonal);
  const board = hall.boards?.[state.hallMode] || hall.boards?.[hall.default_mode];
  if (!board) {
    host.textContent = "Für diese Rankingmetrik liegen keine bestätigten Daten vor.";
    return;
  }
  for (const mode of hall.modes || []) {
    const button = $(`hall-mode-${mode}`);
    if (button) button.classList.toggle("primary", mode === state.hallMode);
  }
  for (const entry of board.entries || []) {
    const row = document.createElement("article");
    row.className = "equipment-row";
    const info = document.createElement("div");
    const title = document.createElement("strong");
    const movement = entry.history?.movement || "new";
    const movementLabel = hall.movement_labels?.[movement] || movement.toUpperCase();
    const local = entry.character_id === hall.local_character_id ? " · DU" : "";
    title.textContent = `#${entry.rank ?? "–"} ${MOVEMENT_SYMBOLS[movement] || "–"} ${entry.display_name || entry.alias || entry.character_id}${local}`;
    const detail = document.createElement("span");
    const value = entry.selected_metric?.available ? entry.selected_metric.value : "NICHT BESTÄTIGT";
    const delta = entry.history?.rank_delta;
    const change = delta == null ? movementLabel : `${movementLabel} ${signed(delta)}`;
    detail.textContent = `${HALL_MODE_LABELS[state.hallMode] || state.hallMode.toUpperCase()} ${value} · ${change} · ${entry.competition?.zone === "top10" ? "TOP-10" : "FREIES FELD"}`;
    info.append(title, detail);
    row.append(info);
    host.append(row);
  }
}

function render() {
  const p = state.projection || {};
  const event = p.event;
  setHidden("first-run", Boolean(p.character));
  setHidden("profile-panel", !p.character);
  setHidden("street-panel", !p.character);
  setHidden("district-panel", !p.districts);
  setHidden("property-panel", !p.properties);
  setHidden("hall-panel", !p.hall_of_tribute);
  setHidden("event-panel", !event);
  setHidden("economy-panel", !p.economy);
  setHidden("incident-panel", !event || !["live", "crisis"].includes(event.phase));
  setHidden("settlement-panel", !event || !["settlement", "completed"].includes(event.phase));

  renderHud(p);
  renderProfile(p.character);
  renderStreetApproaches(p.street_approaches);
  renderDistricts(p.districts);
  window.BunkerMapPro?.render(p.berlin_ops_map);
  renderProperties(p.properties, p.property_upgrades);
  renderHall(p.hall_of_tribute);
  $("phase-badge").textContent = event ? event.phase.toUpperCase() : "NOCH KEIN EVENT";
  if (!event) return;

  $("event-name-view").textContent = event.display_name;
  $("location").textContent = event.location?.display_name || "–";
  $("safety").textContent = event.safety_status;
  $("event-revision").textContent = String(event.revision);
  $("budget").textContent = money(event.budget_cents);
  renderEventActions(event.actions || []);
  renderEconomy(p.economy);
  renderIncidents(p);
  renderSettlement(p);
}

function renderEventActions(actions) {
  const host = $("event-actions");
  host.replaceChildren();
  const blockers = [];
  if (!actions.length) host.textContent = "Für diese Phase gibt es keine normale Event-Aktion.";
  for (const action of actions) {
    const button = document.createElement("button");
    button.textContent = ACTION_LABELS[action.action_id] || action.action_id;
    button.disabled = !action.enabled;
    button.className = action.enabled ? "primary" : "disabled-action";
    button.addEventListener("click", () => sendCommand({ type: "event.execute", command_id: commandId(action.action_id), action_id: action.action_id }));
    host.append(button);
    blockers.push(...action.blockers);
  }
  $("blockers").textContent = blockers.length
    ? `Blockiert: ${[...new Set(blockers)].map((value) => BLOCKER_LABELS[value] || value).join(" · ")}`
    : "Runtime-Gates: frei.";
}

function renderEconomy(economy) {
  const host = $("equipment-list");
  host.replaceChildren();
  if (!economy) return;
  for (const item of economy.items || []) {
    const row = document.createElement("article");
    row.className = "equipment-row";
    const info = document.createElement("div");
    const title = document.createElement("strong");
    title.textContent = item.label;
    const detail = document.createElement("span");
    detail.textContent = `Besitz ${item.owned} · reserviert ${item.reserved} · Basis ${money(item.base_price_cents)}`;
    info.append(title, detail);
    const actions = document.createElement("div");
    actions.className = "inline-actions";
    const buy = document.createElement("button");
    buy.textContent = "KAUFEN";
    buy.addEventListener("click", () => sendCommand({ type: "economy.transact", command_id: commandId("buy"), kind: "buy", item_id: item.item_id, quantity: 1 }));
    const reserve = document.createElement("button");
    reserve.textContent = "RESERVIEREN";
    reserve.addEventListener("click", () => sendCommand({ type: "economy.transact", command_id: commandId("reserve"), kind: "reserve", item_id: item.item_id, quantity: 1 }));
    actions.append(buy, reserve);
    row.append(info, actions);
    host.append(row);
  }
}

function incidentEffectText(effects) {
  const items = [];
  for (const [key, value] of Object.entries(effects || {})) {
    if (!(key in EFFECT_LABELS)) continue;
    const formatted = key === "budget_delta_cents" ? signedMoney(value) : signed(value);
    items.push(`${EFFECT_LABELS[key]} ${formatted}`);
  }
  return items.length ? items.join(" · ") : "Keine katalogisierte direkte Änderung";
}

function renderIncidents(p) {
  const host = $("incident-content");
  host.replaceChildren();
  const active = p.incidents?.active;
  if (active) {
    const title = document.createElement("p");
    title.className = "crisis-active-line";
    title.textContent = `Aktiv: ${displayId(active.incident_type)} · Severity ${active.severity}`;
    host.append(title);
    const spec = (p.incident_catalog || []).find((item) => item.incident_type === active.incident_type);
    const responses = spec?.responses || [];
    const actions = document.createElement("div");
    actions.className = "incident-choice-grid";
    for (const responseId of active.response_ids || []) {
      const response = responses.find((item) => item.response_id === responseId);
      const card = document.createElement("article");
      card.className = "incident-choice";
      const heading = document.createElement("strong");
      heading.textContent = displayId(responseId);
      const target = document.createElement("span");
      target.className = "incident-target";
      target.textContent = `Danach: ${displayId(response?.target_phase || "unbekannt")}`;
      const preview = document.createElement("p");
      preview.className = "effect-preview";
      preview.textContent = incidentEffectText(response?.effects);
      const button = document.createElement("button");
      button.className = "primary";
      button.textContent = "DIESE ANTWORT WÄHLEN";
      button.addEventListener("click", () => sendCommand({
        type: "incident.resolve",
        command_id: commandId("incident-resolve"),
        response_id: responseId
      }));
      card.append(heading, target, preview, button);
      actions.append(card);
    }
    host.append(actions);
    return;
  }
  if (p.event?.phase !== "live") {
    host.textContent = "Keine aktive Krise.";
    return;
  }
  const intro = document.createElement("p");
  intro.textContent = "Optionaler Test-/Gameplay-Pfad: Während LIVE kann eine katalogisierte Krise ausgelöst werden.";
  host.append(intro);
  const actions = document.createElement("div");
  actions.className = "incident-trigger-grid";
  for (const incident of p.incident_catalog || []) {
    const button = document.createElement("button");
    button.textContent = `${displayId(incident.incident_type)} · S${incident.base_severity}`;
    button.addEventListener("click", () => sendCommand({ type: "incident.open", command_id: commandId("incident-open"), incident_type: incident.incident_type, severity: incident.base_severity }));
    actions.append(button);
  }
  host.append(actions);
}

function renderSettlement(p) {
  const host = $("settlement-content");
  host.replaceChildren();
  if (p.settlement) {
    const pre = document.createElement("pre");
    pre.textContent = JSON.stringify({ status: p.settlement.status, effects: p.settlement.effects, budget: p.settlement.budget, stress: p.settlement.stress, reputation: p.settlement.reputation }, null, 2);
    host.append(pre);
    return;
  }
  if (p.event?.phase === "settlement") {
    const text = document.createElement("p");
    text.textContent = "Die Runtime hat die Abrechnungsphase erreicht. Jetzt bestätigte Folgen genau einmal verbuchen.";
    const button = document.createElement("button");
    button.className = "primary";
    button.textContent = "SETTLEMENT ABSCHLIESSEN";
    button.addEventListener("click", () => sendCommand({ type: "settlement.complete", command_id: commandId("settlement") }));
    host.append(text, button);
  }
}

async function sendCommand(command) {
  try {
    const payload = await request("/api/command", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(command) });
    log(`${command.type}: bestätigt${payload.idempotent_replay ? " (Replay)" : ""}`, payload.committed_event_ids);
    state.projection = payload.state;
    render();
    if (command.type === "street.walk") renderStreetEncounter(payload.metadata?.street_encounter);
  } catch (error) {
    log(`${command.type}: ABGEWIESEN – ${error.message}`);
  }
}

$("new-game").addEventListener("click", async () => {
  try {
    const payload = await request("/api/new-game", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ command_id: commandId("first-run"), character_name: $("character-name").value, event_name: $("event-name").value })
    });
    log("First Run bestätigt", payload.committed_event_ids);
    state.projection = payload.state;
    render();
  } catch (error) {
    log(`First Run ABGEWIESEN – ${error.message}`);
  }
});

$("save-profile").addEventListener("click", () => {
  const nicknames = $("profile-nicknames").value.split(",").map((value) => value.trim()).filter(Boolean);
  const crewIdentity = readCrewIdentity();
  const changes = {
    display_name: $("profile-display-name").value.trim(),
    alias: $("profile-alias").value.trim(),
    additional_nicknames: nicknames,
    motto: $("profile-motto").value.trim()
  };
  if (crewIdentity) changes.crew_identity = crewIdentity;
  sendCommand({
    type: "profile.update",
    command_id: commandId("profile-update"),
    changes
  });
});

$("street-walk").addEventListener("click", () => sendCommand({
  type: "street.walk",
  command_id: commandId("street-walk"),
  approach_id: state.streetApproach
}));

for (const mode of ["reputation", "level", "resonance"]) {
  $(`hall-mode-${mode}`).addEventListener("click", () => {
    state.hallMode = mode;
    renderHall(state.projection?.hall_of_tribute);
  });
}
for (const cycleType of ["weekly", "monthly"]) {
  $(`hall-cycle-${cycleType}`).addEventListener("click", () => {
    state.hallCycleType = cycleType;
    renderHallSeason(state.projection?.hall_of_tribute?.seasonal);
  });
}

function setOptionsOpen(open) {
  setHidden("ui-options-panel", !open);
  $("ui-options-toggle").setAttribute("aria-expanded", String(open));
}
$("ui-options-toggle").addEventListener("click", () => {
  setOptionsOpen($("ui-options-toggle").getAttribute("aria-expanded") !== "true");
});
$("ui-options-close").addEventListener("click", () => setOptionsOpen(false));

$("checkpoint").addEventListener("click", async () => {
  try {
    const payload = await request("/api/checkpoint", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ request: "manual_checkpoint" }) });
    log(`Checkpoint bestätigt: ${payload.snapshot_id}`);
  } catch (error) {
    log(`Checkpoint ABGEWIESEN – ${error.message}`);
  }
});

window.BunkerUIPrefs?.init();
refresh();
