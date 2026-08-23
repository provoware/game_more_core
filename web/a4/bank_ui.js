"use strict";

(function installPersonalBankUi() {
  const baseRenderSceneJobs = renderSceneJobs;

  function parseAmountCents(raw) {
    const normalized = String(raw || "").trim().replace(",", ".");
    const match = normalized.match(/^(\d+)(?:\.(\d{1,2}))?$/);
    if (!match) return null;
    const euros = Number.parseInt(match[1], 10);
    const cents = Number.parseInt((match[2] || "").padEnd(2, "0"), 10) || 0;
    const total = euros * 100 + cents;
    return Number.isSafeInteger(total) && total > 0 ? total : null;
  }

  function transfer(direction) {
    const input = document.getElementById("jobs-bank-amount");
    const amountCents = parseAmountCents(input?.value);
    const status = document.getElementById("jobs-bank-status");
    if (amountCents === null) {
      if (status) status.textContent = "Bitte einen positiven Betrag eingeben, zum Beispiel 25 oder 25,50.";
      input?.focus();
      return;
    }
    sendCommand({
      type: "finance.transfer",
      command_id: commandId("finance-transfer"),
      direction,
      amount_cents: amountCents
    });
  }

  function ensureBankControl() {
    let control = document.getElementById("jobs-bank-control");
    if (control) return control;

    const list = document.getElementById("jobs-list");
    if (!list) return null;
    control = document.createElement("section");
    control.id = "jobs-bank-control";
    control.className = "notice";
    control.setAttribute("aria-labelledby", "jobs-bank-title");

    const eyebrow = document.createElement("p");
    eyebrow.className = "eyebrow";
    eyebrow.textContent = "PERSÖNLICHES GELD // WALLET ↔ BANK";
    const title = document.createElement("h3");
    title.id = "jobs-bank-title";
    title.textContent = "Bankkonto";
    const balances = document.createElement("p");
    balances.id = "jobs-bank-balances";
    const explanation = document.createElement("p");
    explanation.textContent = "Verschiebe dein eigenes Geld zwischen Bargeld und Bank. Der Browser nennt nur Richtung und Betrag; die Runtime prüft den bestätigten Kontostand und bucht alles atomar im bestehenden Finance-Ledger.";

    const amountLabel = document.createElement("label");
    amountLabel.htmlFor = "jobs-bank-amount";
    amountLabel.textContent = "Betrag in Euro";
    const input = document.createElement("input");
    input.id = "jobs-bank-amount";
    input.type = "text";
    input.inputMode = "decimal";
    input.autocomplete = "off";
    input.placeholder = "z. B. 25,00";
    input.setAttribute("aria-describedby", "jobs-bank-status");
    amountLabel.append(input);

    const actions = document.createElement("div");
    actions.className = "inline-actions";
    const deposit = document.createElement("button");
    deposit.id = "jobs-bank-deposit";
    deposit.type = "button";
    deposit.textContent = "EINZAHLEN";
    deposit.addEventListener("click", () => transfer("deposit"));
    const withdraw = document.createElement("button");
    withdraw.id = "jobs-bank-withdraw";
    withdraw.type = "button";
    withdraw.textContent = "ABHEBEN";
    withdraw.addEventListener("click", () => transfer("withdraw"));
    actions.append(deposit, withdraw);

    const status = document.createElement("p");
    status.id = "jobs-bank-status";
    status.setAttribute("role", "status");
    status.setAttribute("aria-live", "polite");
    status.textContent = "Noch kein Banktransfer in dieser Ansicht.";

    control.append(eyebrow, title, balances, explanation, amountLabel, actions, status);
    const assistant = document.getElementById("jobs-assistant-control");
    if (assistant) assistant.after(control);
    else list.before(control);
    return control;
  }

  function renderBankControl(sceneJobs, hasCharacter) {
    if (!hasCharacter || !sceneJobs?.available) return;
    const control = ensureBankControl();
    if (!control) return;
    const cash = Number.isInteger(sceneJobs.cash_cents) ? sceneJobs.cash_cents : 0;
    const bank = Number.isInteger(sceneJobs.bank_cents) ? sceneJobs.bank_cents : 0;
    const balances = document.getElementById("jobs-bank-balances");
    if (balances) balances.textContent = `BARGELD ${money(cash)} · BANK ${money(bank)} · Finanzstand ${sceneJobs.finance_revision || 0}`;
    const deposit = document.getElementById("jobs-bank-deposit");
    const withdraw = document.getElementById("jobs-bank-withdraw");
    if (deposit) deposit.disabled = cash <= 0;
    if (withdraw) withdraw.disabled = bank <= 0;
  }

  renderSceneJobs = function renderSceneJobsWithPersonalBank(sceneJobs, hasCharacter) {
    baseRenderSceneJobs(sceneJobs, hasCharacter);
    renderBankControl(sceneJobs, hasCharacter);
  };
})();
