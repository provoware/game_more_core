"use strict";

const $ = (id) => document.getElementById(id);
const state = { projection: null, busy: false };

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

function setHidden(id, hidden) {
  $(id).classList.toggle("hidden", hidden);
}

function render() {
  const p = state.projection || {};
  const event = p.event;
  setHidden("first-run", Boolean(p.character));
  setHidden("event-panel", !event);
  setHidden("economy-panel", !p.economy);
  setHidden("incident-panel", !event || !["live", "crisis"].includes(event.phase));
  setHidden("settlement-panel", !event || !["settlement", "completed"].includes(event.phase));

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
  if (!actions.length) {
    host.textContent = "Für diese Phase gibt es keine normale Event-Aktion.";
  }
  for (const action of actions) {
    const button = document.createElement("button");
    button.textContent = ACTION_LABELS[action.action_id] || action.action_id;
    button.disabled = !action.enabled;
    button.className = action.enabled ? "primary" : "disabled-action";
    button.addEventListener("click", () => sendCommand({
      type: "event.execute",
      command_id: commandId(action.action_id),
      action_id: action.action_id
    }));
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
    buy.addEventListener("click", () => sendCommand({
      type: "economy.transact", command_id: commandId("buy"), kind: "buy", item_id: item.item_id, quantity: 1
    }));
    const reserve = document.createElement("button");
    reserve.textContent = "RESERVIEREN";
    reserve.addEventListener("click", () => sendCommand({
      type: "economy.transact", command_id: commandId("reserve"), kind: "reserve", item_id: item.item_id, quantity: 1
    }));
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
      button.addEventListener("click", () => sendCommand({
        type: "incident.resolve", command_id: commandId("incident-resolve"), response_id: responseId
      }));
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
    button.addEventListener("click", () => sendCommand({
      type: "incident.open",
      command_id: commandId("incident-open"),
      incident_type: incident.incident_type,
      severity: incident.base_severity
    }));
    actions.append(button);
  }
  host.append(actions);
}

function renderSettlement(p) {
  const host = $("settlement-content");
  host.replaceChildren();
  if (p.settlement) {
    const pre = document.createElement("pre");
    pre.textContent = JSON.stringify({
      status: p.settlement.status,
      effects: p.settlement.effects,
      budget: p.settlement.budget,
      stress: p.settlement.stress,
      reputation: p.settlement.reputation
    }, null, 2);
    host.append(pre);
    return;
  }
  if (p.event?.phase === "settlement") {
    const text = document.createElement("p");
    text.textContent = "Die Runtime hat die Abrechnungsphase erreicht. Jetzt bestätigte Folgen genau einmal verbuchen.";
    const button = document.createElement("button");
    button.className = "primary";
    button.textContent = "SETTLEMENT ABSCHLIESSEN";
    button.addEventListener("click", () => sendCommand({
      type: "settlement.complete", command_id: commandId("settlement")
    }));
    host.append(text, button);
  }
}

async function sendCommand(command) {
  try {
    const payload = await request("/api/command", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(command)
    });
    log(`${command.type}: bestätigt${payload.idempotent_replay ? " (Replay)" : ""}`, payload.committed_event_ids);
    state.projection = payload.state;
    render();
  } catch (error) {
    log(`${command.type}: ABGEWIESEN – ${error.message}`);
  }
}

$("new-game").addEventListener("click", async () => {
  try {
    const payload = await request("/api/new-game", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        command_id: commandId("first-run"),
        character_name: $("character-name").value,
        event_name: $("event-name").value
      })
    });
    log("First Run bestätigt", payload.committed_event_ids);
    state.projection = payload.state;
    render();
  } catch (error) {
    log(`First Run ABGEWIESEN – ${error.message}`);
  }
});

$("checkpoint").addEventListener("click", async () => {
  try {
    const payload = await request("/api/checkpoint", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ request: "manual_checkpoint" })
    });
    log(`Checkpoint bestätigt: ${payload.snapshot_id}`);
  } catch (error) {
    log(`Checkpoint ABGEWIESEN – ${error.message}`);
  }
});

refresh();
