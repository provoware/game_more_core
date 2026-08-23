"use strict";

(function installFinanceStatementExport() {
  const baseRenderSceneJobs = renderSceneJobs;
  const FILE_BASENAME = "bunkerfrequenz-kontoauszug";
  const ENTRY_FIELDS = [
    "sequence",
    "transaction_id",
    "kind",
    "group",
    "label",
    "amount_cents",
    "cash_after_cents",
    "bank_after_cents",
    "source_label"
  ];
  const TOTAL_FIELDS = [
    "job_income_cents",
    "bank_deposit_cents",
    "bank_withdrawal_cents",
    "savings_interest_cents"
  ];

  function csvCell(value) {
    const text = value == null ? "" : String(value);
    return `"${text.replaceAll('"', '""')}"`;
  }

  function projectionStatement() {
    return state.projection?.scene_jobs?.finance_statement || null;
  }

  function csvFromProjection(statement) {
    const rows = [
      ["section", "key", "value"],
      ["meta", "available", statement?.available === true],
      ["meta", "supported_entries", statement?.supported_entries ?? 0],
      ["meta", "other_entries", statement?.other_entries ?? 0],
      ["meta", "filters", Array.isArray(statement?.filters) ? statement.filters.join("|") : ""]
    ];
    const totals = statement?.totals || {};
    for (const field of TOTAL_FIELDS) rows.push(["total", field, totals[field] ?? 0]);
    rows.push([]);
    rows.push(ENTRY_FIELDS);
    for (const entry of Array.isArray(statement?.entries) ? statement.entries : []) {
      rows.push(ENTRY_FIELDS.map((field) => entry?.[field] ?? ""));
    }
    return rows.map((row) => row.map(csvCell).join(",")).join("\r\n") + "\r\n";
  }

  function txtFromProjection(statement) {
    const totals = statement?.totals || {};
    const lines = [
      "BUNKERFREQUENZ KONTOAUSZUG",
      "Quelle: bestätigte FIN-STATEMENTS-Projection",
      "",
      `available: ${statement?.available === true}`,
      `supported_entries: ${statement?.supported_entries ?? 0}`,
      `other_entries: ${statement?.other_entries ?? 0}`,
      `filters: ${Array.isArray(statement?.filters) ? statement.filters.join("|") : ""}`,
      ...TOTAL_FIELDS.map((field) => `${field}: ${totals[field] ?? 0}`),
      "",
      `Felder: ${ENTRY_FIELDS.join(" | ")}`
    ];
    for (const entry of Array.isArray(statement?.entries) ? statement.entries : []) {
      lines.push(ENTRY_FIELDS.map((field) => entry?.[field] ?? "").join(" | "));
    }
    return lines.join("\n") + "\n";
  }

  function downloadText(filename, mimeType, content) {
    const blob = new Blob([content], { type: `${mimeType};charset=utf-8` });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = filename;
    anchor.hidden = true;
    document.body.append(anchor);
    anchor.click();
    anchor.remove();
    URL.revokeObjectURL(url);
  }

  function exportStatement(format) {
    const statement = projectionStatement();
    const status = document.getElementById("jobs-finance-export-status");
    if (!statement?.available) {
      if (status) status.textContent = "Kontoauszug ist noch nicht verfügbar.";
      return;
    }
    if (format === "csv") {
      downloadText(`${FILE_BASENAME}.csv`, "text/csv", csvFromProjection(statement));
    } else if (format === "txt") {
      downloadText(`${FILE_BASENAME}.txt`, "text/plain", txtFromProjection(statement));
    } else {
      return;
    }
    if (status) status.textContent = `${format.toUpperCase()} lokal aus der bestätigten Kontoauszug-Projection erstellt.`;
  }

  function ensureExportControls() {
    const statement = document.getElementById("jobs-finance-statement");
    if (!statement || document.getElementById("jobs-finance-export-actions")) return;

    const actions = document.createElement("div");
    actions.id = "jobs-finance-export-actions";
    actions.className = "inline-actions";
    actions.setAttribute("role", "group");
    actions.setAttribute("aria-label", "Kontoauszug exportieren");

    for (const [format, label] of [["txt", "TXT EXPORT"], ["csv", "CSV EXPORT"]]) {
      const button = document.createElement("button");
      button.type = "button";
      button.dataset.financeExport = format;
      button.textContent = label;
      button.addEventListener("click", () => exportStatement(format));
      actions.append(button);
    }

    const status = document.createElement("p");
    status.id = "jobs-finance-export-status";
    status.className = "notice";
    status.setAttribute("role", "status");
    status.setAttribute("aria-live", "polite");
    status.textContent = "Export bleibt lokal und verändert weder Save noch Ledger.";

    statement.append(actions, status);
  }

  renderSceneJobs = function renderSceneJobsWithFinanceExport(sceneJobs, hasCharacter) {
    baseRenderSceneJobs(sceneJobs, hasCharacter);
    if (hasCharacter && sceneJobs?.available) ensureExportControls();
  };

  window.BunkerFinanceStatementExport = Object.freeze({
    csvFromProjection,
    txtFromProjection
  });
})();
