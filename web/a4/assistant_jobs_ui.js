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
