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

  const baseRenderCrewIdentity = renderCrewIdentity;
  renderCrewIdentity = function renderCrewIdentityWithConfirmedHud(crew) {
    // Wichtig: bestätigte Projection zuerst ins HUD spiegeln. Der bestehende
    // Editor-Fokus-Schutz darf danach weiterhin einen Editor-Neuaufbau verhindern.
    renderConfirmedHudCrew(crew);
    return baseRenderCrewIdentity(crew);
  };

  window.BunkerCrewIdentityHudSync = Object.freeze({ renderConfirmedHudCrew });
  window.__bunkerCrewIdentityHudSyncInstalled = true;
})();
