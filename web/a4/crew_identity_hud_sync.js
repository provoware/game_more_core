"use strict";

(() => {
  if (window.__bunkerCrewIdentityHudSyncInstalled || typeof renderCrewIdentity !== "function") return;

  const backgrounds = (identity, render) => ({
    solid: render.primary,
    split: `linear-gradient(90deg, ${render.primary} 0 50%, ${render.secondary} 50% 100%)`,
    band: `linear-gradient(180deg, ${render.primary} 0 38%, ${render.secondary} 38% 62%, ${render.primary} 62% 100%)`,
    diagonal: `linear-gradient(135deg, ${render.primary} 0 48%, ${render.secondary} 48% 100%)`
  })[identity.style] || render.primary;

  function renderConfirmedHudCrew(crew) {
    const identity = crew?.identity;
    const render = crew?.render;
    const host = document.querySelector(".hud-crew-identity");
    const preview = host?.querySelector(".hud-crew-preview");
    const symbolNode = host?.querySelector(".hud-crew-symbol");
    const markNode = host?.querySelector(".hud-crew-mark");
    if (
      !identity || !render ||
      !(host instanceof HTMLElement) ||
      !(preview instanceof HTMLElement) ||
      !(symbolNode instanceof HTMLElement) ||
      !(markNode instanceof HTMLElement)
    ) return;

    preview.dataset.mode = identity.mode || "flag";
    preview.style.background = backgrounds(identity, render);
    preview.style.setProperty("--crew-accent", render.accent || "#ff5a1f");
    symbolNode.textContent = render.symbol_glyph || "★";
    markNode.textContent = identity.mark || "";
    markNode.hidden = !identity.mark;
    host.setAttribute(
      "aria-label",
      `Bestätigt: ${identity.mode === "logo" ? "Crew-Logo" : "Crew-Fahne"}: ${identity.symbol}, ${identity.style}`
    );
    host.hidden = false;
  }

  function confirmedHudPreviewClone() {
    const source = document.querySelector(".hud-crew-preview");
    const identity = document.querySelector(".hud-crew-identity");
    if (!(source instanceof HTMLElement) || !(identity instanceof HTMLElement) || identity.hidden) return null;
    const badge = source.cloneNode(true);
    badge.className = "hall-local-crew-preview";
    badge.setAttribute("aria-hidden", "true");
    return badge;
  }

  function renderConfirmedHallCrew(hall) {
    if (!hall || typeof state !== "object") return;
    const board = hall.boards?.[state.hallMode] || hall.boards?.[hall.default_mode];
    const host = document.getElementById("hall-ranking");
    if (!board || !(host instanceof HTMLElement)) return;

    const rows = Array.from(host.children);
    for (const row of rows) row.querySelector(".hall-local-crew")?.remove();
    const localIndex = (board.entries || []).findIndex((entry) => entry.character_id === hall.local_character_id);
    if (localIndex < 0 || localIndex >= rows.length) return;

    const row = rows[localIndex];
    if (!(row instanceof HTMLElement)) return;
    const badge = confirmedHudPreviewClone();
    if (!badge) return;
    const marker = document.createElement("span");
    marker.className = "hall-local-crew";
    marker.setAttribute("role", "img");
    marker.setAttribute("aria-label", "Deine bestätigte Crew-Marke");
    marker.append(badge);
    row.prepend(marker);
  }

  const baseRenderCrewIdentity = renderCrewIdentity;
  renderCrewIdentity = function renderCrewIdentityWithConfirmedHud(crew) {
    // Wichtig: bestätigte Projection zuerst ins HUD spiegeln. Der bestehende
    // Editor-Fokus-Schutz darf danach weiterhin einen Editor-Neuaufbau verhindern.
    renderConfirmedHudCrew(crew);
    return baseRenderCrewIdentity(crew);
  };

  if (typeof renderHall === "function") {
    const baseRenderHall = renderHall;
    renderHall = function renderHallWithConfirmedCrew(hall) {
      const result = baseRenderHall(hall);
      renderConfirmedHallCrew(hall);
      return result;
    };
  }

  window.BunkerCrewIdentityHudSync = Object.freeze({ renderConfirmedHudCrew, renderConfirmedHallCrew });
  window.__bunkerCrewIdentityHudSyncInstalled = true;
})();
