"use strict";

(() => {
  let lastState = null;
  let busy = false;
  let observer = null;

  function commandId(prefix) {
    const suffix = globalThis.crypto?.randomUUID?.() || `${Date.now()}-${Math.random().toString(16).slice(2)}`;
    return `${prefix}:${suffix}`;
  }

  async function send(command) {
    if (busy) return;
    busy = true;
    try {
      const response = await fetch("/api/command", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(command)
      });
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.detail || payload.error_code || "assistant_request_failed");
      }
      lastState = payload.state;
      render(lastState);
      const live = document.getElementById("assistant-status");
      if (live) live.textContent = command.type === "assistant.deactivate"
        ? "Dein geheimer bester Freund wartet wieder auf eine Aufgabe."
        : "Aufgabe bestätigt. Ab der nächsten bestätigten Straßenrunde zieht er sie mit durch.";
    } catch (error) {
      const live = document.getElementById("assistant-status");
      if (live) live.textContent = `Assistent konnte nicht geändert werden: ${error.message}`;
    } finally {
      busy = false;
    }
  }

  function ensureBox(panel) {
    let box = document.getElementById("assistant-box");
    if (box) return box;
    box = document.createElement("section");
    box.id = "assistant-box";
    box.className = "notice";
    box.setAttribute("aria-labelledby", "assistant-title");

    const title = document.createElement("strong");
    title.id = "assistant-title";
    title.textContent = "GEHEIMER BESTER FREUND";
    const story = document.createElement("p");
    story.id = "assistant-story";
    const status = document.createElement("p");
    status.id = "assistant-status";
    status.setAttribute("role", "status");
    status.setAttribute("aria-live", "polite");
    const stop = document.createElement("button");
    stop.id = "assistant-stop";
    stop.type = "button";
    stop.textContent = "AUFGABE STOPPEN";
    stop.addEventListener("click", () => send({
      type: "assistant.deactivate",
      command_id: commandId("assistant-stop")
    }));
    box.append(title, story, status, stop);

    const list = document.getElementById("jobs-list");
    if (list) panel.insertBefore(box, list);
    else panel.append(box);
    return box;
  }

  function decorateJobRows(sceneJobs, assistant) {
    const list = document.getElementById("jobs-list");
    if (!list) return;
    const rows = [...list.querySelectorAll(":scope > .equipment-row")];
    const jobs = Array.isArray(sceneJobs?.jobs) ? sceneJobs.jobs : [];
    rows.forEach((row, index) => {
      const job = jobs[index];
      if (!job?.job_id) return;
      let actions = row.querySelector(".inline-actions");
      if (!actions) {
        actions = document.createElement("div");
        actions.className = "inline-actions";
        row.append(actions);
      }
      let assign = actions.querySelector('[data-assistant-assign="true"]');
      if (!assign) {
        assign = document.createElement("button");
        assign.type = "button";
        assign.dataset.assistantAssign = "true";
        actions.append(assign);
      }
      const active = assistant?.active_task_id === job.job_id;
      assign.textContent = active ? "FREUND: AKTIV" : "FREUND ÜBERNIMMT";
      assign.disabled = active || busy;
      assign.classList.toggle("primary", active);
      assign.onclick = active ? null : () => send({
        type: "assistant.assign",
        command_id: commandId("assistant-assign"),
        task_id: job.job_id
      });
    });
  }

  function render(state) {
    if (state) lastState = state;
    const current = lastState;
    const panel = document.getElementById("jobs-panel");
    if (!panel || !current?.assistant?.available) return;
    const assistant = current.assistant;
    const sceneJobs = current.scene_jobs;
    const box = ensureBox(panel);
    const story = document.getElementById("assistant-story");
    const status = document.getElementById("assistant-status");
    const stop = document.getElementById("assistant-stop");
    if (story) story.textContent = assistant.story || "";
    if (status) {
      if (assistant.active_task) {
        status.textContent = `${assistant.active_task.label} · ${assistant.trigger_label} · ${assistant.completed_rounds} Runde(n) erledigt.`;
      } else {
        status.textContent = "Er wartet auf eine Aufgabe. Wähle sie direkt an einer Jobkarte aus.";
      }
    }
    if (stop) stop.hidden = !assistant.active_task_id;
    box.dataset.active = assistant.active_task_id ? "true" : "false";
    decorateJobRows(sceneJobs, assistant);

    const list = document.getElementById("jobs-list");
    if (list && !observer) {
      observer = new MutationObserver(() => decorateJobRows(lastState?.scene_jobs, lastState?.assistant));
      observer.observe(list, { childList: true });
    }
  }

  window.BunkerAssistantUI = Object.freeze({ render });
})();
