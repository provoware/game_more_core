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

const POLARITY_LABELS = {
  positive: "GLÜCK",
  negative: "PECH",
  neutral: "RUHIG"
};

const HOUSING_LABELS = {
  independent: "Eigenes Zuhause",
  guest: "Bei jemandem untergekommen",
  homeless: "Ohne feste Unterkunft"
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

function setInputIfIdle(id, value) {
  const input = $(id);
  if (document.activeElement !== input) input.value = value ?? "";
}

function renderProfile(character, world) {
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
  $("booking-id").textContent = world?.booking_id || "–";
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

function fillSelect(select, values, selected, labelFor = (value) => value) {
  select.replaceChildren();
  for (const value of values) {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = labelFor(value);
    option.selected = value === selected;
    select.append(option);
  }
}

function citySpec(cityId) {
  return (state.projection?.world?.cities || []).find((city) => city.city_id === cityId) || null;
}

function updateMoveDistricts() {
  const city = citySpec($("move-city").value);
  if (!city) return;
  const currentDistrict = $("move-district").value;
  const district = city.districts.includes(currentDistrict) ? currentDistrict : city.districts[0];
  fillSelect($("move-district"), city.districts, district);
  updateMoveLocations();
}

function updateMoveLocations() {
  const city = citySpec($("move-city").value);
  if (!city) return;
  const district = $("move-district").value;
  const locations = city.locations.filter((item) => item.district_id === district);
  const select = $("move-location");
  select.replaceChildren();
  const districtOnly = document.createElement("option");
  districtOnly.value = "";
  districtOnly.textContent = "Nur Bezirk / unterwegs";
  select.append(districtOnly);
  for (const item of locations) {
    const option = document.createElement("option");
    option.value = item.location_id;
    option.textContent = `${item.location_id} · ${item.category || "Ort"}`;
    select.append(option);
  }
}

function renderMoveSelectors(world) {
  const cities = world.cities || [];
  fillSelect($("move-city"), cities.map((item) => item.city_id), world.position.city_id, (id) => citySpec(id)?.label || id);
  const currentCity = citySpec(world.position.city_id);
  fillSelect($("move-district"), currentCity?.districts || [], world.position.district_id);
  updateMoveLocations();
  $("move-location").value = world.position.location_id || "";
}

function renderMiniGames(world) {
  const actions = $("minigame-actions");
  actions.replaceChildren();
  const games = world.current_location?.mini_games || [];
  for (const gameId of games) {
    if (gameId === "xoxo") continue;
    const button = document.createElement("button");
    button.textContent = gameId === "poker" ? "POKER – 5 KARTEN" : "CASINOAUTOMAT – PUNKTE";
    button.addEventListener("click", () => sendCommand({
      type: "world.minigame",
      command_id: commandId(`minigame-${gameId}`),
      game_id: gameId,
      cell: null
    }));
    actions.append(button);
  }
  if (!games.length) actions.textContent = "An diesem Ort gibt es kein kleines Spiel.";

  const board = $("xoxo-board");
  board.replaceChildren();
  if (!games.includes("xoxo")) return;
  const xoxo = world.mini_games?.xoxo;
  for (let index = 0; index < 9; index += 1) {
    const button = document.createElement("button");
    button.textContent = xoxo?.board?.[index] || "·";
    button.disabled = Boolean(xoxo?.board?.[index]);
    button.setAttribute("aria-label", `XOXO Feld ${index + 1}`);
    button.addEventListener("click", () => sendCommand({
      type: "world.minigame",
      command_id: commandId("minigame-xoxo"),
      game_id: "xoxo",
      cell: index
    }));
    board.append(button);
  }
}

function renderMiniGameResult(result) {
  const host = $("minigame-result");
  if (!result) return;
  if (result.game_id === "poker") {
    host.textContent = `Poker: ${result.outcome.toUpperCase()} · deine Karten ${result.player_hand.join(" ")} · Haus ${result.house_hand.join(" ")} · Punkte +${result.points}`;
  } else if (result.game_id === "slot") {
    host.textContent = `Automat: ${result.reels.join(" | ")} · ${result.outcome.toUpperCase()} · Punkte +${result.points}`;
  } else {
    host.textContent = `XOXO: ${result.status.toUpperCase()} · Punkte +${result.points}`;
  }
}

function renderWorld(world) {
  if (!world) return;
  $("intro-story").textContent = world.intro?.text || "";
  setHidden("intro-panel", Boolean(world.intro?.acknowledged));
  $("world-city").textContent = world.city?.label || world.position.city_id;
  $("world-district").textContent = world.position.district_id;
  $("world-location").textContent = world.position.location_id || "unterwegs";
  $("world-housing").textContent = HOUSING_LABELS[world.housing?.status] || world.housing?.status || "–";
  $("city-price-factor").textContent = `${((world.city?.price_multiplier_bps || 10000) / 100).toFixed(0)} %`;
  $("city-customs").textContent = world.city?.description || (world.city?.customs || []).join(" · ");
  $("metric-heat").textContent = String(world.district_metrics?.heat ?? "–");
  $("metric-prestige").textContent = String(world.district_metrics?.prestige ?? "–");
  $("metric-police").textContent = String(world.district_metrics?.police_pressure ?? "–");
  $("metric-scene").textContent = String(world.district_metrics?.scene_activity ?? "–");
  renderMoveSelectors(world);
  $("inspect-storefront").disabled = !world.current_location?.storefront_available;
  renderMiniGames(world);
  $("honor-list").textContent = world.honors?.length
    ? `Titel: ${world.honors.map((item) => `${item.label} [${item.kind}]`).join(" · ")}`
    : "Noch keine Titel.";
  $("deed-list").textContent = world.great_deeds?.length
    ? world.great_deeds.map((item) => `${item.label} [${item.valence}]`).join(" · ")
    : "Noch keine großen Werke.";
  renderParty(world.party);
}

function renderParty(party) {
  const host = $("party-status");
  const choices = $("party-choices");
  choices.replaceChildren();
  if (!party) {
    host.textContent = "Living-City-Partyvertrag nicht verfügbar.";
    return;
  }
  const check = party.check;
  host.textContent = check?.triggered && !check.resolved
    ? "Gesetzeshüter sind eingetroffen. Wähle eine von genau drei bestätigten Reaktionen."
    : check?.triggered && check.resolved
      ? `Begegnung abgeschlossen: ${check.choice_id}`
      : check?.resolved
        ? "Risikocheck abgeschlossen: keine Begegnung."
        : `Party-Modus: ${party.mode || "official"}`;
  $("party-check").disabled = !party.eligible_to_check;
  for (const choice of party.choices || []) {
    const button = document.createElement("button");
    button.textContent = choice.label || choice.choice_id;
    button.addEventListener("click", () => sendCommand({
      type: "world.party_resolve",
      command_id: commandId("party-resolve"),
      choice_id: choice.choice_id
    }));
    choices.append(button);
  }
}

function renderStorefront(storefront) {
  const host = $("storefront-result");
  const notes = storefront?.notes;
  if (!Array.isArray(notes)) return;
  host.replaceChildren();
  for (const note of notes) {
    const p = document.createElement("p");
    p.textContent = note;
    host.append(p);
  }
}

function render() {
  const p = state.projection || {};
  const event = p.event;
  setHidden("first-run", Boolean(p.character));
  setHidden("profile-panel", !p.character);
  setHidden("street-panel", !p.character);
  setHidden("world-panel", !p.world);
  setHidden("intro-panel", !p.world || Boolean(p.world?.intro?.acknowledged));
  setHidden("event-panel", !event);
  setHidden("economy-panel", !p.economy);
  setHidden("incident-panel", !event || !["live", "crisis"].includes(event.phase));
  setHidden("settlement-panel", !event || !["settlement", "completed"].includes(event.phase));

  renderProfile(p.character, p.world);
  if (p.world) renderWorld(p.world);
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
    detail.textContent = `Besitz ${item.owned} · reserviert ${item.reserved} · Basis ${money(item.base_price_cents)} · tatsächlicher Preis folgt bestätigtem Stadt-/Marktkontext`;
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
  intro.textContent = "Optional: Während LIVE kann eine katalogisierte Krise ausgelöst werden.";
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
    if (command.type === "street.walk") renderStreetEncounter(payload.metadata?.street_encounter);
    if (command.type === "world.inspect_storefront") renderStorefront(payload.metadata?.storefront);
    if (command.type === "world.minigame") renderMiniGameResult(payload.metadata?.minigame);
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

$("intro-ack").addEventListener("click", () => sendCommand({
  type: "world.intro_acknowledge",
  command_id: commandId("intro")
}));

$("save-profile").addEventListener("click", () => {
  const nicknames = $("profile-nicknames").value
    .split(",")
    .map((value) => value.trim())
    .filter(Boolean);
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

$("street-walk").addEventListener("click", () => sendCommand({
  type: "street.walk",
  command_id: commandId("street-walk")
}));

$("move-city").addEventListener("change", updateMoveDistricts);
$("move-district").addEventListener("change", updateMoveLocations);
$("world-move").addEventListener("click", () => sendCommand({
  type: "world.move",
  command_id: commandId("world-move"),
  city_id: $("move-city").value,
  district_id: $("move-district").value,
  location_id: $("move-location").value || null
}));

$("inspect-storefront").addEventListener("click", () => sendCommand({
  type: "world.inspect_storefront",
  command_id: commandId("storefront")
}));

$("party-official").addEventListener("click", () => sendCommand({
  type: "world.party_mode",
  command_id: commandId("party-mode"),
  mode: "official"
}));
$("party-unofficial").addEventListener("click", () => sendCommand({
  type: "world.party_mode",
  command_id: commandId("party-mode"),
  mode: "unofficial"
}));
$("party-check").addEventListener("click", () => sendCommand({
  type: "world.party_check",
  command_id: commandId("party-check")
}));

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
