"use strict";

(() => {
  const upstreamFetch = globalThis.fetch.bind(globalThis);
  const RECEIPT_LABELS = Object.freeze({
    applied: "NEU BESTÄTIGT",
    idempotent_replay: "BEREITS BESTÄTIGT",
    not_triggered: "NICHT AUSGELÖST"
  });
  const RECEIPT_COPY = Object.freeze({
    applied: "Ein Bezirksereignis wurde für diese Abrechnung erstmals bestätigt.",
    idempotent_replay: "Dieses Bezirksereignis war bereits bestätigt. Der Retry hat nichts doppelt angewendet.",
    not_triggered: "Die Runtime hat für diese Abrechnung kein Bezirksereignis ausgelöst. Es wurde nichts erfunden oder nachgetragen."
  });

  let lastReceipt = null;

  function receiptFromPayload(payload) {
    const event = payload?.metadata?.district_world_event;
    if (!event || typeof event !== "object") return null;

    if (!event.event_id && !event.event_instance_id) {
      return Object.freeze({ state: "not_triggered", label: RECEIPT_LABELS.not_triggered, copy: RECEIPT_COPY.not_triggered });
    }
    if (payload?.idempotent_replay === true) {
      return Object.freeze({ state: "idempotent_replay", label: RECEIPT_LABELS.idempotent_replay, copy: RECEIPT_COPY.idempotent_replay });
    }
    return Object.freeze({ state: "applied", label: RECEIPT_LABELS.applied, copy: RECEIPT_COPY.applied });
  }

  function renderReceipt(receipt = lastReceipt) {
    if (!receipt) return;
    const host = document.getElementById("settlement-content");
    if (!host) return;

    let notice = document.getElementById("district-receipt-clarity");
    if (!notice) {
      notice = document.createElement("div");
      notice.id = "district-receipt-clarity";
      notice.className = "notice";
      notice.setAttribute("role", "status");
      notice.setAttribute("aria-live", "polite");
      host.append(notice);
    }
    notice.dataset.receiptState = receipt.state;
    notice.replaceChildren();

    const label = document.createElement("strong");
    label.textContent = receipt.label;
    const copy = document.createElement("span");
    copy.textContent = ` · ${receipt.copy}`;
    notice.append(label, copy);
  }

  function requestInfo(input, init = {}) {
    const request = input instanceof Request ? input : null;
    const url = new URL(request?.url || String(input), window.location.href);
    const method = String(init.method || request?.method || "GET").toUpperCase();
    return { url, method };
  }

  async function receiptAwareFetch(input, init = {}) {
    const response = await upstreamFetch(input, init);
    const info = requestInfo(input, init);
    if (info.url.origin === window.location.origin && info.url.pathname === "/api/command" && info.method === "POST") {
      const clone = response.clone();
      void clone.json().then((payload) => {
        const receipt = receiptFromPayload(payload);
        if (!receipt) return;
        lastReceipt = receipt;
        window.setTimeout(() => renderReceipt(), 0);
      }).catch(() => { /* Kein Receipt bei nicht lesbarer Antwort. */ });
    }
    return response;
  }

  const settlement = document.getElementById("settlement-content");
  if (settlement) {
    new MutationObserver(() => {
      if (lastReceipt && !document.getElementById("district-receipt-clarity")) {
        queueMicrotask(() => renderReceipt());
      }
    }).observe(settlement, { childList: true });
  }

  globalThis.fetch = receiptAwareFetch;
  window.BunkerReceiptClarity = Object.freeze({ receiptFromPayload, renderReceipt });
})();
