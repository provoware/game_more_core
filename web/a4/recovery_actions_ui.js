"use strict";

(function installRecoveryActionsUi() {
  const baseRenderSceneJobs = renderSceneJobs;

  function availabilityText(action) {
    if (action?.can_run) return "Nächste Regeneration: bestätigt möglich.";
    if (action?.blocker === "energy_above_recovery_threshold") {
      return "Nächste Regeneration gesperrt: Noch zu viel Energie für diesen Notfall-Reset.";
    }
    if (action?.blocker === "stress_above_recovery_threshold") {
      return "Nächste Regeneration gesperrt: Zu viel Stress – erst anders runterkommen.";
    }
    return "Nächste Regeneration aktuell nicht verfügbar.";
  }

  function ensureFeedbackHost() {
    const panel = document.getElementById("jobs-panel");
    if (!panel) return null;
    let feedback = document.getElementById("jobs-recovery-feedback");
    if (!feedback) {
      feedback = document.createElement("div");
      feedback.id = "jobs-recovery-feedback";
      feedback.className = "notice";
      feedback.setAttribute("role", "status");
      feedback.setAttribute("aria-live", "polite");
      feedback.textContent = "Noch keine Regeneration bestätigt.";
      document.getElementById("jobs-recovery-actions")?.after(feedback);
    }
    return feedback;
  }

  function renderConfirmedFeedback(recoveryId, beforeCharacter) {
    const afterCharacter = state.projection?.character;
    if (!beforeCharacter || !afterCharacter) return;
    if (
      beforeCharacter.energy === afterCharacter.energy &&
      beforeCharacter.stress === afterCharacter.stress
    ) return;

    const action = (state.projection?.scene_jobs?.recovery_actions || []).find(
      (item) => item.recovery_id === recoveryId
    );
    const feedback = ensureFeedbackHost();
    if (!feedback) return;
    feedback.textContent = `Energie ${beforeCharacter.energy} → ${afterCharacter.energy} · Stress ${beforeCharacter.stress} → ${afterCharacter.stress}. ${availabilityText(action)}`;
  }

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
    ensureFeedbackHost();
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
      button.addEventListener("click", async () => {
        const beforeCharacter = state.projection?.character
          ? { ...state.projection.character }
          : null;
        await sendCommand({
          type: "recovery.run",
          command_id: commandId("recovery"),
          recovery_id: action.recovery_id
        });
        renderConfirmedFeedback(action.recovery_id, beforeCharacter);
      });
      row.append(info, button);
      host.append(row);
    }
  }

  renderSceneJobs = function renderSceneJobsWithRecovery(sceneJobs, hasCharacter) {
    baseRenderSceneJobs(sceneJobs, hasCharacter);
    if (hasCharacter && sceneJobs?.available) renderRecoveryActions(sceneJobs);
  };
})();
