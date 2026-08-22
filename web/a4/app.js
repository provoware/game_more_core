"use strict";

const $ = (id) => document.getElementById(id);
const state = { projection: null, busy: false, hallMode: "reputation" };

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
const MOVEMENT_SYMBOLS = { up: "↑", down: "↓", same: "→", new: "★", unranked: "–" };

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
}

function renderStreetEncounter(encounter) {
  const host = $("street-result");
  host.replaceChildren();
  if (!encounter) {
    host.textContent = "Keine bestätigte Straßenrunde erhalten.";
    return;
  }
  host.dataset.polarity = encounter.polarity || "neutral";
  const heading = document.createElement("strong");
  heading.textContent = `${POLARITY_LABELS[encounter.polarity] || "RUNDE"} // ${encounter.title || encounter.encounter_id}`;
  const body = document.createElement("p");
  body.textContent = encounter.body || "";
  const effects = document.createElement("span");
  effects.className = "street-effects";
  effects.textContent = `Energie ${signed(encounter.effects?.energy_delta)} · Stress ${signed(encounter.effects?.stress_delta)} · Ruf ${signed(encounter.effects?.reputation_delta)}`;
  host.append(heading, body, effects);
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

function renderHall(hall) {
  const host = $("hall-ranking");
  host.replaceChildren();
  if (!hall) return;
  $("hall-participants").textContent = String(hall.confirmed_participant_count || 0);
  $("hall-status").textContent = hall.network_competition_available
    ? `Bestätigte Konkurrenz aktiv · Top ${hall.top_limit} · keine Ranggleichstände.`
    : "Nur dein bestätigter lokaler Character ist verfügbar. Keine Gegner oder Netzwerkwerte werden erfunden.";
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

  renderProfile(p.character);
  renderDistricts(p.districts);
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

function renderIncidents(p) {
  const host = $("incident-content");
  host.replaceChildren();
  const active = p.incidents?.active;
  if (active) {
    const title = document.createElement("p");
    title.textContent = `Aktiv: ${active.incident_type} · Severity ${active.severity}`;
    host.append(title);
    const spec = (p.incident_catalog || []).find((item) => item.incident_type === active.incident_type);
    const responses = spec?.responses || [];
    const actions = document.createElement("div");
    actions.className = "action-grid";
    for (const responseId of active.response_ids || []) {
      const response = responses.find((item) => item.response_id === responseId);
      const button = document.createElement("button");
      button.textContent = `${responseId} → ${response?.target_phase || "?"}`;
      button.addEventListener("click", () => sendCommand({ type: "incident.resolve", command_id: commandId("incident-resolve"), response_id: responseId }));
      actions.append(button);
    }
    host.append(actions);
    return;
  }
  if (p.event?.phase !== "live") {
    host.textContent = "Keine aktive Krise.";
    return;
  }
  const intro = document.createElement("p");
  intro.textContent = "Optional: Für den Smoke-Pfad kann während LIVE eine Krise ausgelöst werden.";
  host.append(intro);
  const actions = document.createElement("div");
  actions.className = "action-grid";
  for (const incident of p.incident_catalog || []) {
    const button = document.createElement("button");
    button.textContent = `${incident.incident_type} · S${incident.base_severity}`;
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
  sendCommand({
    type: "profile.update",
    command_id: commandId("profile-update"),
    changes: {
      display_name: $("profile-display-name").value.trim(),
      alias: $("profile-alias").value.trim(),
      additional_nicknames: nicknames,
      motto: $("profile-motto").value.trim()
    }
  });
});

$("street-walk").addEventListener("click", () => sendCommand({ type: "street.walk", command_id: commandId("street-walk") }));
for (const mode of ["reputation", "level", "resonance"]) {
  $(`hall-mode-${mode}`).addEventListener("click", () => {
    state.hallMode = mode;
    renderHall(state.projection?.hall_of_tribute);
  });
}

$("checkpoint").addEventListener("click", async () => {
  try {
    const payload = await request("/api/checkpoint", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ request: "manual_checkpoint" }) });
    log(`Checkpoint bestätigt: ${payload.snapshot_id}`);
  } catch (error) {
    log(`Checkpoint ABGEWIESEN – ${error.message}`);
  }
});

refresh();