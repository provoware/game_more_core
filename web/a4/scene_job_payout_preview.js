"use strict";

(function installSceneJobPayoutPreview() {
  const baseRenderSceneJobs = renderSceneJobs;
  const reducedPayoutContext = "Aktueller Lohn reduziert – deine Energie reicht nicht für die volle Auszahlung.";

  function renderProjectedPayouts(sceneJobs, hasCharacter) {
    baseRenderSceneJobs(sceneJobs, hasCharacter);
    if (!hasCharacter || !sceneJobs?.available) return;

    const rows = Array.from(document.querySelectorAll("#jobs-list .equipment-row"));
    for (const [index, job] of (sceneJobs.jobs || []).entries()) {
      const row = rows[index];
      if (!row) continue;
      const info = row.querySelector(":scope > div:first-child");
      const detail = info?.querySelector("span:last-child");
      const run = row.querySelector(":scope > .inline-actions > button.primary");
      const effective = Number.isInteger(job.effective_payout_cents)
        ? job.effective_payout_cents
        : job.payout_cents;
      const reduced = job.payout_reduced_by_energy === true;

      if (detail) {
        detail.textContent = reduced
          ? `${job.duration_hours} h · Lohn bis zu ${money(job.payout_cents)} · aktuell ${money(effective)} · Energie ${signed(job.energy_delta)} · Stress ${signed(job.stress_delta)} · ${reducedPayoutContext}`
          : `${job.duration_hours} h · Lohn ${money(effective)} · Energie ${signed(job.energy_delta)} · Stress ${signed(job.stress_delta)}`;
      }
      if (run) {
        run.textContent = reduced
          ? `ARBEITEN · AKTUELL ${money(effective)}`
          : `ARBEITEN · ${money(effective)}`;
        run.setAttribute(
          "aria-label",
          reduced
            ? `${job.label}: aktuell ${money(effective)}, maximal ${money(job.payout_cents)}. ${reducedPayoutContext}`
            : `${job.label}: ${money(effective)}`
        );
      }
      row.dataset.payoutReducedByEnergy = reduced ? "true" : "false";
    }
  }

  renderSceneJobs = renderProjectedPayouts;

  if (state.projection) {
    renderProjectedPayouts(state.projection.scene_jobs, Boolean(state.projection.character));
  }
})();
