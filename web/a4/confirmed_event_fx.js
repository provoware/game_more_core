"use strict";

(() => {
  const SUPPORTED_COMMANDS = new Set(["street.walk", "recovery.run", "incident.resolve"]);
  const FX_CLASSES = [
    "confirmed-fx",
    "confirmed-fx-positive",
    "confirmed-fx-negative",
    "confirmed-fx-neutral"
  ];
  let lastCommandReceipt = null;

  function snapshot() {
    const projection = state.projection || {};
    const character = projection.character || {};
    const event = projection.event || {};
    return {
      energy: character.energy,
      stress: character.stress,
      reputation: character.reputation,
      budget: event.budget_cents,
      recoveryText: document.getElementById("jobs-recovery-feedback")?.textContent || ""
    };
  }

  function pulse(element, tone = "neutral") {
    if (!(element instanceof HTMLElement)) return;
    element.classList.remove(...FX_CLASSES);
    void element.offsetWidth;
    element.classList.add("confirmed-fx", `confirmed-fx-${tone}`);
    window.setTimeout(() => element.classList.remove(...FX_CLASSES), 900);
  }

  function resourceTone(key, before, after) {
    if (before == null || after == null || before === after) return null;
    if (key === "stress") return after < before ? "positive" : "negative";
    return after > before ? "positive" : "negative";
  }

  function render(commandType, before, receipt) {
    if (!receipt || receipt.idempotent_replay === true) return;
    const after = snapshot();

    for (const [key, elementId] of [
      ["energy", "hud-energy"],
      ["stress", "hud-stress"],
      ["reputation", "hud-reputation"],
      ["budget", "hud-budget"]
    ]) {
      const tone = resourceTone(key, before[key], after[key]);
      if (tone) pulse(document.getElementById(elementId), tone);
    }

    if (commandType === "street.walk" && receipt.metadata?.street_encounter) {
      const street = document.getElementById("street-result");
      const polarity = receipt.metadata.street_encounter.polarity || street?.dataset.polarity;
      const tone = polarity === "positive" || polarity === "negative" ? polarity : "neutral";
      pulse(street, tone);
    }

    if (commandType === "recovery.run" && before.recoveryText !== after.recoveryText) {
      pulse(document.getElementById("jobs-recovery-feedback"), "neutral");
    }

    if (commandType === "incident.resolve") {
      pulse(document.getElementById("hud-phase"), "neutral");
    }
  }

  if (
    window.__bunkerConfirmedEventFxInstalled ||
    typeof sendCommand !== "function" ||
    typeof request !== "function"
  ) return;

  const baseRequest = request;
  request = async function requestWithConfirmedReceipt(path, options = {}) {
    const payload = await baseRequest(path, options);
    if (path === "/api/command") lastCommandReceipt = payload;
    return payload;
  };

  const baseSendCommand = sendCommand;
  sendCommand = async function sendCommandWithConfirmedEventFx(command) {
    const before = snapshot();
    lastCommandReceipt = null;
    await baseSendCommand(command);
    const receipt = lastCommandReceipt;
    lastCommandReceipt = null;
    if (!SUPPORTED_COMMANDS.has(command?.type) || !receipt) return;
    window.setTimeout(() => render(command.type, before, receipt), 0);
  };
  window.__bunkerConfirmedEventFxInstalled = true;
})();
