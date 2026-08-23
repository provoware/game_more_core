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
  let previewFormat = "txt";
  let previewContent = "";

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

  function serializeStatement(format, statement) {
    if (format === "csv") return csvFromProjection(statement);
    if (format === "txt") return txtFromProjection(statement);
    return null;
  }

  function checksum32(content) {
    let hash = 0x811c9dc5;
    for (const byte of new TextEncoder().encode(content)) {
      hash ^= byte;
      hash = Math.imul(hash, 0x01000193) >>> 0;
    }
    return hash.toString(16).padStart(8, "0");
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

  function renderPreview(format) {
    const statement = projectionStatement();
    const status = document.getElementById("jobs-finance-export-status");
    if (!statement?.available) {
      if (status) status.textContent = "Kontoauszug ist noch nicht verfügbar.";
      return null;
    }
    const content = serializeStatement(format, statement);
    if (content === null) return null;
    previewFormat = format;
    previewContent = content;
    const preview = document.getElementById("jobs-finance-export-preview");
    const checksum = document.getElementById("jobs-finance-export-checksum");
    if (preview) preview.textContent = content;
    if (checksum) checksum.textContent = `${format.toUpperCase()} · ${new TextEncoder().encode(content).length} Bytes · Prüfsumme ${checksum32(content)}`;
    if (status) status.textContent = `${format.toUpperCase()}-Vorschau aus demselben Inhalt wie der Download erstellt.`;
    return content;
  }

  function exportStatement(format) {
    const content = renderPreview(format);
    const status = document.getElementById("jobs-finance-export-status");
    if (content === null) return;
    const mimeType = format === "csv" ? "text/csv" : "text/plain";
    downloadText(`${FILE_BASENAME}.${format}`, mimeType, content);
    if (status) status.textContent = `${format.toUpperCase()} lokal aus exakt der unmittelbar geprüften Vorschau erstellt · Prüfsumme ${checksum32(content)}.`;
  }

  async function copyPreview() {
    const status = document.getElementById("jobs-finance-export-status");
    if (!previewContent) {
      renderPreview(previewFormat);
    }
    if (!previewContent) return;
    try {
      await navigator.clipboard.writeText(previewContent);
      if (status) status.textContent = `${previewFormat.toUpperCase()}-Vorschau kopiert · Prüfsumme ${checksum32(previewContent)}.`;
    } catch {
      if (status) status.textContent = "Kopieren wurde vom Browser blockiert. Die Vorschau bleibt vollständig sichtbar und kann manuell markiert werden.";
    }
  }

  function ensureExportControls() {
    const statement = document.getElementById("jobs-finance-statement");
    if (!statement || document.getElementById("jobs-finance-export-actions")) return;

    const actions = document.createElement("div");
    actions.id = "jobs-finance-export-actions";
    actions.className = "inline-actions";
    actions.setAttribute("role", "group");
    actions.setAttribute("aria-label", "Kontoauszug prüfen und exportieren");

    for (const [format, label] of [["txt", "TXT PRÜFEN"], ["csv", "CSV PRÜFEN"]]) {
      const previewButton = document.createElement("button");
      previewButton.type = "button";
      previewButton.dataset.financePreview = format;
      previewButton.textContent = label;
      previewButton.addEventListener("click", () => renderPreview(format));
      actions.append(previewButton);
    }

    for (const [format, label] of [["txt", "TXT DOWNLOAD"], ["csv", "CSV DOWNLOAD"]]) {
      const button = document.createElement("button");
      button.type = "button";
      button.dataset.financeExport = format;
      button.textContent = label;
      button.addEventListener("click", () => exportStatement(format));
      actions.append(button);
    }

    const copy = document.createElement("button");
    copy.type = "button";
    copy.id = "jobs-finance-export-copy";
    copy.textContent = "VORSCHAU KOPIEREN";
    copy.addEventListener("click", copyPreview);
    actions.append(copy);

    const checksum = document.createElement("p");
    checksum.id = "jobs-finance-export-checksum";
    checksum.textContent = "Noch keine Exportvorschau geprüft.";

    const preview = document.createElement("pre");
    preview.id = "jobs-finance-export-preview";
    preview.tabIndex = 0;
    preview.setAttribute("aria-label", "Lokale Kontoauszug-Exportvorschau");
    preview.textContent = "TXT oder CSV prüfen, bevor du die Datei herunterlädst.";

    const status = document.createElement("p");
    status.id = "jobs-finance-export-status";
    status.className = "notice";
    status.setAttribute("role", "status");
    status.setAttribute("aria-live", "polite");
    status.textContent = "Vorschau, Prüfsumme, Kopieren und Download bleiben lokal und verändern weder Save noch Ledger.";

    statement.append(actions, checksum, preview, status);
  }

  renderSceneJobs = function renderSceneJobsWithFinanceExport(sceneJobs, hasCharacter) {
    baseRenderSceneJobs(sceneJobs, hasCharacter);
    if (hasCharacter && sceneJobs?.available) ensureExportControls();
  };

  window.BunkerFinanceStatementExport = Object.freeze({
    csvFromProjection,
    txtFromProjection,
    serializeStatement,
    checksum32
  });
})();
