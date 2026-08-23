"use strict";

(function installRecoveryActionsUi() {
  const baseRenderSceneJobs = renderSceneJobs;

  function renderRecoveryActions(sceneJobs) {
    const panel = document.getElementById("jobs-panel");
    if (!panel) return;
    let host = document.getElementById("jobs-recovery-actions");
    if (!host) {
      host = document.createElement("section");
      host.id = "jobs-recovery-actions";
      const title = document.createElement("h3");
      title.textContent = "Regeneration";
      const intro = document.createElement("p");
      intro.textContent = "Aktive Regeneration ist eine bestätigte Character-Aktion. Die Runtime entscheidet, ob sie gerade erlaubt ist.";
      host.append(title, intro);
      document.getElementById("jobs-list")?.after(host);
    }
    for (const old of host.querySelectorAll("article")) old.remove();

    for (const action of sceneJobs?.recovery_actions || []) {
      const row = document.createElement("article");
      row.className = "equipment-row";
      const info = document.createElement("div");
      const title = document.createElement("strong");
      title.textContent = action.label;
      const description = document.createElement("span");
      description.textContent = action.description;
      const effects = document.createElement("span");
      effects.textContent = `Energie +${action.energy_delta} · Stress +${action.stress_delta}`;
      const availability = document.createElement("small");
      availability.textContent = action.can_run
        ? "Jetzt bestätigt möglich."
        : action.blocker === "energy_above_recovery_threshold"
          ? "Noch zu viel Energie für diesen Notfall-Reset."
          : action.blocker === "stress_above_recovery_threshold"
            ? "Zu viel Stress – erst anders runterkommen."
            : "Aktuell nicht verfügbar.";
      info.append(title, description, effects, availability);

      const button = document.createElement("button");
      button.type = "button";
      button.className = "primary";
      button.textContent = "REGENERIEREN";
      button.disabled = action.can_run !== true;
      button.addEventListener("click", () => sendCommand({
        type: "recovery.run",
        command_id: commandId("recovery"),
        recovery_id: action.recovery_id
      }));
      row.append(info, button);
      host.append(row);
    }
  }

  renderSceneJobs = function renderSceneJobsWithRecovery(sceneJobs, hasCharacter) {
    baseRenderSceneJobs(sceneJobs, hasCharacter);
    if (hasCharacter && sceneJobs?.available) renderRecoveryActions(sceneJobs);
  };
})();
