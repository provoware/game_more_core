"use strict";

(function installAssistantJobsUi() {
  const baseRenderSceneJobs = renderSceneJobs;

  function assistantCommandId() {
    const suffix = globalThis.crypto?.randomUUID?.() || `${Date.now()}-${Math.random().toString(16).slice(2)}`;
    return `assistant-control:${suffix}`;
  }

  function setAssistantJob(jobId) {
    return sendCommand({
      type: "assistant.control",
      command_id: assistantCommandId(),
      job_id: jobId
    });
  }

  function parseBankAmountCents(raw) {
    const normalized = String(raw || "").trim().replace(",", ".");
    const match = normalized.match(/^(\d+)(?:\.(\d{1,2}))?$/);
    if (!match) return null;
    const euros = Number.parseInt(match[1], 10);
    const cents = Number.parseInt((match[2] || "").padEnd(2, "0"), 10) || 0;
    const total = euros * 100 + cents;
    return Number.isSafeInteger(total) && total > 0 ? total : null;
  }

  function transferPersonalMoney(direction) {
    const input = document.getElementById("jobs-bank-amount");
    const amountCents = parseBankAmountCents(input?.value);
    const status = document.getElementById("jobs-bank-status");
    if (amountCents === null) {
      if (status) status.textContent = "Bitte einen positiven Betrag eingeben, zum Beispiel 25 oder 25,50.";
      input?.focus();
      return;
    }
    return sendCommand({
      type: "finance.transfer",
      command_id: commandId("finance-transfer"),
      direction,
      amount_cents: amountCents
    });
  }

  function ensureAssistantControl() {
    let control = document.getElementById("jobs-assistant-control");
    if (control) return control;

    const list = document.getElementById("jobs-list");
    if (!list) return null;

    control = document.createElement("section");
    control.id = "jobs-assistant-control";
    control.className = "notice";
    control.setAttribute("aria-labelledby", "jobs-assistant-title");

    const eyebrow = document.createElement("p");
    eyebrow.className = "eyebrow";
    eyebrow.textContent = "SECRET BEST FRIEND // RUNDENHILFE";

    const title = document.createElement("h3");
    title.id = "jobs-assistant-title";
    title.textContent = "Geheimer bester Freund";

    const status = document.createElement("p");
    status.id = "jobs-assistant-status";
    status.setAttribute("role", "status");
    status.setAttribute("aria-live", "polite");

    const explanation = document.createElement("p");
    explanation.id = "jobs-assistant-explanation";
    explanation.textContent = "Wähle genau einen vorhandenen Scene Job. Der Freund arbeitet erst bei einer intern bestätigten Spielrunde; Browser und Rechnerzeit starten keine Runde.";

    const actions = document.createElement("div");
    actions.className = "inline-actions";
    const stop = document.createElement("button");
    stop.id = "jobs-assistant-stop";
    stop.type = "button";
    stop.textContent = "FREUND STOPPEN";
    stop.addEventListener("click", () => setAssistantJob(null));
    actions.append(stop);

    const afterglow = document.createElement("div");
    afterglow.id = "jobs-assistant-afterglow";
    afterglow.setAttribute("aria-labelledby", "jobs-assistant-afterglow-title");

    const afterglowEyebrow = document.createElement("p");
    afterglowEyebrow.className = "eyebrow";
    afterglowEyebrow.textContent = "NACHHALL // BESTÄTIGTE ARBEIT";

    const afterglowTitle = document.createElement("h4");
    afterglowTitle.id = "jobs-assistant-afterglow-title";
    afterglowTitle.textContent = "Was dein Freund dazu sagt";

    const afterglowList = document.createElement("div");
    afterglowList.id = "jobs-assistant-afterglow-list";
    afterglowList.setAttribute("aria-live", "polite");

    afterglow.append(afterglowEyebrow, afterglowTitle, afterglowList);
    control.append(eyebrow, title, status, explanation, actions, afterglow);
    list.before(control);
    return control;
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
    explanation.textContent = "Verschiebe dein eigenes Geld zwischen Bargeld und Bank. Der Browser nennt nur Richtung und Betrag; die Runtime prüft den bestätigten Stand und bucht atomar im bestehenden Finance-Ledger.";

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
    deposit.addEventListener("click", () => transferPersonalMoney("deposit"));
    const withdraw = document.createElement("button");
    withdraw.id = "jobs-bank-withdraw";
    withdraw.type = "button";
    withdraw.textContent = "ABHEBEN";
    withdraw.addEventListener("click", () => transferPersonalMoney("withdraw"));
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

  function renderAssistantAfterglow(afterglow) {
    const list = document.getElementById("jobs-assistant-afterglow-list");
    if (!list) return;
    list.replaceChildren();

    const entries = Array.isArray(afterglow?.entries) ? afterglow.entries : [];
    if (!afterglow?.available || entries.length === 0) {
      const empty = document.createElement("p");
      empty.textContent = "Noch kein Nachhall: Erst eine bestätigte Assistentenrunde mit tatsächlich gebuchtem Job erzeugt hier eine Reaktion.";
      list.append(empty);
      return;
    }

    for (const entry of entries) {
      const article = document.createElement("article");
      article.className = "assistant-afterglow-entry";

      const heading = document.createElement("strong");
      heading.textContent = entry.headline || entry.job_label || "Bestätigte Freundesrunde";

      const body = document.createElement("p");
      body.textContent = entry.body || "";

      const meta = document.createElement("small");
      meta.textContent = entry.job_label ? `Job: ${entry.job_label}` : "Bestätigte Assistentenarbeit";

      article.append(heading, body, meta);
      list.append(article);
    }
  }

  function renderBankControl(sceneJobs) {
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

  function renderAssistantControl(sceneJobs, hasCharacter) {
    if (!hasCharacter || !sceneJobs?.available) return;
    const control = ensureAssistantControl();
    if (!control) return;

    const assistant = sceneJobs.assistant || {
      enabled: false,
      active_job_id: null,
      active_job_label: null,
      revision: 0
    };
    const status = document.getElementById("jobs-assistant-status");
    const stop = document.getElementById("jobs-assistant-stop");
    if (status) {
      status.textContent = assistant.enabled
        ? `AKTIV · ${assistant.active_job_label || assistant.active_job_id} · Steuerstand ${assistant.revision}`
        : `AUS · kein Job gewählt · Steuerstand ${assistant.revision}`;
    }
    if (stop) stop.disabled = !assistant.enabled;

    renderAssistantAfterglow(sceneJobs.assistant_afterglow);
    renderBankControl(sceneJobs);

    const rows = Array.from(document.querySelectorAll("#jobs-list .equipment-row"));
    for (const [index, job] of (sceneJobs.jobs || []).entries()) {
      const row = rows[index];
      const actions = row?.querySelector(".inline-actions");
      if (!row || !actions) continue;

      const active = assistant.active_job_id === job.job_id;
      row.dataset.assistantActive = active ? "true" : "false";

      const choose = document.createElement("button");
      choose.type = "button";
      choose.dataset.assistantJobId = job.job_id;
      choose.setAttribute("aria-pressed", active ? "true" : "false");
      choose.textContent = active
        ? "FREUND AKTIV"
        : assistant.enabled
          ? "FREUND WECHSELN"
          : "FREUND STARTEN";
      choose.disabled = active;
      choose.addEventListener("click", () => setAssistantJob(job.job_id));
      actions.append(choose);
    }
  }

  renderSceneJobs = function renderSceneJobsWithAssistant(sceneJobs, hasCharacter) {
    baseRenderSceneJobs(sceneJobs, hasCharacter);
    renderAssistantControl(sceneJobs, hasCharacter);
  };
})();
