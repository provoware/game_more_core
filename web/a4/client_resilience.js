"use strict";

(() => {
  const nativeFetch = globalThis.fetch.bind(globalThis);
  const API_TIMEOUT_MS = 8000;
  const SAFE_GET_RETRY_DELAYS_MS = [250, 900];
  const IDEMPOTENT_WRITE_RETRY_DELAYS_MS = [400];
  const REPLAY_SAFE_POST_PATHS = new Set(["/api/command"]);

  function emit(name, detail) {
    window.dispatchEvent(new CustomEvent(name, { detail }));
  }

  function requestInfo(input, init = {}) {
    const request = input instanceof Request ? input : null;
    const url = new URL(request?.url || String(input), window.location.href);
    const method = String(init.method || request?.method || "GET").toUpperCase();
    return { request, url, method };
  }

  function hasCommandId(body) {
    if (typeof body !== "string") return false;
    try {
      const parsed = JSON.parse(body);
      return Boolean(parsed && typeof parsed === "object" && typeof parsed.command_id === "string" && parsed.command_id.trim());
    } catch {
      return false;
    }
  }

  function retryDelays(method, init, url) {
    if (["GET", "HEAD"].includes(method)) return SAFE_GET_RETRY_DELAYS_MS;
    if (method === "POST" && REPLAY_SAFE_POST_PATHS.has(url.pathname) && hasCommandId(init.body)) {
      return IDEMPOTENT_WRITE_RETRY_DELAYS_MS;
    }
    return [];
  }

  function sameOriginApi(url) {
    return url.origin === window.location.origin && url.pathname.startsWith("/api/");
  }

  function delay(milliseconds) {
    return new Promise((resolve) => window.setTimeout(resolve, milliseconds));
  }

  function statusText(text) {
    const status = document.getElementById("connection-status");
    if (status) status.textContent = text;
  }

  async function oneAttempt(input, init, timeoutMs) {
    const controller = new AbortController();
    const upstreamSignal = init.signal;
    let upstreamAbort = null;
    if (upstreamSignal) {
      if (upstreamSignal.aborted) controller.abort(upstreamSignal.reason);
      else {
        upstreamAbort = () => controller.abort(upstreamSignal.reason);
        upstreamSignal.addEventListener("abort", upstreamAbort, { once: true });
      }
    }
    const timer = window.setTimeout(() => controller.abort(new DOMException("API timeout", "TimeoutError")), timeoutMs);
    try {
      const response = await nativeFetch(input, { ...init, cache: "no-store", signal: controller.signal });
      const payload = await response.arrayBuffer();
      return new Response(payload.byteLength ? payload : null, {
        status: response.status,
        statusText: response.statusText,
        headers: response.headers
      });
    } finally {
      window.clearTimeout(timer);
      if (upstreamSignal && upstreamAbort) upstreamSignal.removeEventListener("abort", upstreamAbort);
    }
  }

  async function resilientFetch(input, init = {}) {
    const info = requestInfo(input, init);
    if (!sameOriginApi(info.url)) return nativeFetch(input, init);

    const delays = retryDelays(info.method, init, info.url);
    let lastError = null;
    for (let attempt = 0; attempt <= delays.length; attempt += 1) {
      try {
        const response = await oneAttempt(input, init, API_TIMEOUT_MS);
        const retryableHttp = response.status >= 500 && attempt < delays.length;
        if (!retryableHttp) {
          if (attempt > 0) {
            statusText("● VERBINDUNG WIEDERHERGESTELLT");
            emit("bunker:transport-recovered", { path: info.url.pathname, method: info.method, attempts: attempt + 1 });
          }
          return response;
        }
        try { await response.body?.cancel(); } catch { /* Antwort wird bewusst verworfen. */ }
        lastError = new Error(`HTTP ${response.status}`);
      } catch (error) {
        lastError = error;
        if (attempt >= delays.length) break;
      }

      statusText("● VERBINDUNG WIRD REPARIERT");
      emit("bunker:transport-retry", {
        path: info.url.pathname,
        method: info.method,
        attempt: attempt + 1,
        max_attempts: delays.length + 1,
        reason: String(lastError?.name || lastError?.message || "transport_error")
      });
      await delay(delays[attempt]);
    }

    statusText("● VERBINDUNG FEHLT");
    emit("bunker:transport-failed", {
      path: info.url.pathname,
      method: info.method,
      attempts: delays.length + 1,
      reason: String(lastError?.name || lastError?.message || "transport_error")
    });
    throw lastError || new Error("API request failed");
  }

  globalThis.fetch = resilientFetch;
  window.BunkerClientResilience = Object.freeze({
    apiTimeoutMs: API_TIMEOUT_MS,
    safeGetRetries: SAFE_GET_RETRY_DELAYS_MS.length,
    idempotentWriteRetries: IDEMPOTENT_WRITE_RETRY_DELAYS_MS.length,
    replaySafePostPaths: Object.freeze([...REPLAY_SAFE_POST_PATHS])
  });
})();
