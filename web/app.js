"use strict";

const paths = {
  manifest: "../manifests/UI_MANIFEST.json",
  texts: "../content/de/ui/character_forge.json",
  asset: "../docs/assets/BUNKERFREQUENZ_SYSTEM_BLUEPRINT_0.4.3.webp"
};

const labels = {
  current_goal: "ui.workflow.current_goal", next_action: "ui.workflow.next_action",
  result: "ui.workflow.result", development: "ui.workflow.development",
  next_goal: "ui.workflow.next_goal"
};

const report = { renderer: "blueprint-evaluation", checks: {}, errors: [] };
const byId = (id) => document.getElementById(id);

function record(name, pass, detail) {
  report.checks[name] = { pass, detail };
  if (!pass) report.errors.push(`${name}: ${detail}`);
}

function inspectVisiblePixels(image) {
  const canvas = document.createElement("canvas");
  canvas.width = 64;
  canvas.height = 64;
  const context = canvas.getContext("2d", { willReadFrequently: true });
  context.drawImage(image, 0, 0, canvas.width, canvas.height);
  const pixels = context.getImageData(0, 0, canvas.width, canvas.height).data;
  let visible = 0;
  for (let alpha = 3; alpha < pixels.length; alpha += 4) visible += pixels[alpha] > 16 ? 1 : 0;
  const coverage = visible / (pixels.length / 4);
  record("visual_integrity", coverage >= 0.5, `${Math.round(coverage * 100)} % sichtbare Fläche`);
}

function renderWorkflow(manifest, texts) {
  const workflow = manifest.focus_model.workflow;
  byId("workflow").replaceChildren(...workflow.map((stage) => {
    const item = document.createElement("li");
    const key = labels[stage];
    item.dataset.stage = stage;
    item.innerHTML = `<strong>${texts[key]}</strong><small>${stage}</small>`;
    return item;
  }));
  record("workflow", workflow.length === 5 && workflow.every((item) => labels[item]), `${workflow.length}/5 Stufen`);
}

function renderVariants(manifest) {
  byId("variants").replaceChildren(...manifest.variants.map((variant) => {
    const card = document.createElement("article");
    card.className = "variant-card";
    card.dataset.id = variant.id;
    card.innerHTML = `<p class="eyebrow">${variant.id}</p><h3>${variant.name}</h3><p>${variant.best_for}</p><code>${variant.layout}</code>`;
    return card;
  }));
  record("variants", manifest.variants.length === 4, `${manifest.variants.length}/4 Ansichten`);
}

function finish() {
  report.generated_at = new Date().toISOString();
  report.viewport = { width: innerWidth, height: innerHeight, pixel_ratio: devicePixelRatio };
  report.ok = report.errors.length === 0;
  window.blueprintReport = Object.freeze(report);
  byId("debug-output").textContent = JSON.stringify(report, null, 2);
  byId("debug-summary").textContent = report.ok ? "Alle lokalen Prüfungen sind grün." : `${report.errors.length} Prüfung(en) fehlgeschlagen.`;
  byId("system-status").textContent = report.ok ? "● BEREIT" : "! EINGESCHRÄNKT";
  byId("system-status").style.borderColor = report.ok ? "var(--success)" : "var(--action)";
  document.documentElement.dataset.ready = String(report.ok);
}

async function start() {
  const image = byId("blueprint-image");
  const inspectImage = () => {
    record("reference_asset", image.naturalWidth > 0, `${image.naturalWidth} × ${image.naturalHeight} px`);
    inspectVisiblePixels(image);
    byId("asset-facts").textContent = `${paths.asset} · ${image.naturalWidth} × ${image.naturalHeight} px · unverändert`;
  };
  if (image.complete && image.naturalWidth > 0) inspectImage();
  else image.addEventListener("load", inspectImage, { once: true });
  image.addEventListener("error", () => record("reference_asset", false, "Originalgrafik nicht erreichbar"), { once: true });
  try {
    const responses = await Promise.all([fetch(paths.manifest), fetch(paths.texts)]);
    if (responses.some((response) => !response.ok)) throw new Error("Vertragsdatei nicht erreichbar");
    const [manifest, texts] = await Promise.all(responses.map((response) => response.json()));
    record("manifest", manifest.design_reference_asset.endsWith(paths.asset.slice(3)), manifest.version);
    record("accessibility", manifest.accessibility.keyboard_navigation && manifest.accessibility.reduced_motion, "Tastatur + Reduced Motion");
    renderWorkflow(manifest, texts);
    renderVariants(manifest);
  } catch (error) {
    record("contracts", false, error.message);
  }
  if (!image.complete) await new Promise((resolve) => image.addEventListener("load", resolve, { once: true }));
  finish();
}

byId("toggle-reference").addEventListener("click", (event) => {
  const expanded = byId("reference-frame").classList.toggle("is-large");
  event.currentTarget.setAttribute("aria-pressed", String(expanded));
  event.currentTarget.textContent = expanded ? "REFERENZ EINPASSEN" : "REFERENZ VERGRÖSSERN";
});
byId("copy-debug").addEventListener("click", async () => {
  await navigator.clipboard.writeText(byId("debug-output").textContent);
  byId("copy-debug").textContent = "KOPIERT";
});
start();
