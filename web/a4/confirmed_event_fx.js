"use strict";

(() => {
  const SUPPORTED_COMMANDS = new Set(["street.walk", "recovery.run", "incident.resolve"]);
  const FX_CLASSES = [
    "confirmed-fx",
    "confirmed-fx-positive",
    "confirmed-fx-negative",
    "confirmed-fx-neutral"
  ];

  function snapshot() {
    const projection = state.projection || {};
    const character = projection.character || {};
    const event = projection.event || {};
    return {
      energy: character.energy,
      stress: character.stress,
      reputation: character.reputation,
      budget: event.budget_cents,
      streetText: document.getElementById("street-result")?.textContent || "",
      recoveryText: document.getElementById("jobs-recovery-feedback")?.textContent || "",
      incidentText: document.getElementById("incident-content")?.textContent || ""
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

  function render(commandType, before) {
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

    if (commandType === "street.walk" && before.streetText !== after.streetText) {
      const street = document.getElementById("street-result");
      const polarity = street?.dataset.polarity;
      const tone = polarity === "positive" || polarity === "negative" ? polarity : "neutral";
      pulse(street, tone);
    }

    if (commandType === "recovery.run" && before.recoveryText !== after.recoveryText) {
      pulse(document.getElementById("jobs-recovery-feedback"), "neutral");
    }

    if (commandType === "incident.resolve" && before.incidentText !== after.incidentText) {
      pulse(document.getElementById("incident-panel"), "neutral");
    }
  }

  if (window.__bunkerConfirmedEventFxInstalled || typeof sendCommand !== "function") return;
  const baseSendCommand = sendCommand;
  sendCommand = async function sendCommandWithConfirmedEventFx(command) {
    const before = snapshot();
    await baseSendCommand(command);
    if (!SUPPORTED_COMMANDS.has(command?.type)) return;
    window.setTimeout(() => render(command.type, before), 0);
  };
  window.__bunkerConfirmedEventFxInstalled = true;
})();
