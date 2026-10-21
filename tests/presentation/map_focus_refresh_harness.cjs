"use strict";
// Regression harness for the real map renderer's render() function.
// No browser, network, persistence, or production state is required.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const source = fs.readFileSync(path.resolve(__dirname, "../../web/a4/map_pro.js"), "utf8");
const start = source.indexOf("  function render(model) {");
const end = source.indexOf("\n  window.BunkerMapPro", start);
assert.ok(start >= 0 && end > start, "renderer function must remain discoverable");
const renderSource = source.slice(start, end);
assert.match(source, /if \(visible\) showLocation\(visible\);\s*else \{\s*selectedKey = null;/);

const canvas = {
  children: [],
  contains(element) { return this.children.includes(element); },
  replaceChildren() { this.children = []; },
  append(element) { this.children.push(element); },
  querySelectorAll() { return this.children; },
};
const panel = { classList: { add() {}, remove() {} } };
const counters = Object.fromEntries(
  ["map-district-count", "map-location-count", "map-owned-count"].map((id) => [id, { textContent: "" }])
);
const document = {
  activeElement: null,
  getElementById(id) {
    if (id === "berlin-map-canvas") return canvas;
    if (id === "map-pro-panel") return panel;
    return counters[id] || null;
  },
};

// Evaluate the real renderer with deliberately narrow presentation-only stubs.
// This catches selection and focus regressions without mocking a gameplay engine.
const makeHarness = new Function("document", "canvas", "renderSource", `
  let selectedKey = null;
  let currentModel = null;
  let activeFilter = "all";
  let detail = null;
  let focusCount = 0;
  const matchesFilter = (item) => activeFilter === "owned"
    ? item.owned === true : activeFilter === "hall" ? false : true;
  const showLocation = (item) => {
    selectedKey = "location:" + item.location_id;
    detail = selectedKey;
  };
  const showDistrict = (item) => {
    selectedKey = "district:" + item.district_id;
    detail = selectedKey;
  };
  const clearDetail = (title) => { detail = title; };
  const ensureViewControls = () => {};
  const bindFilters = () => {};
  const applyView = () => {};
  const createMarker = (key, hidden = false) => ({
    dataset: { mapKey: key },
    hidden,
    focus() {
      document.activeElement = this;
      focusCount++;
      if (key.startsWith("location:")) showLocation({ location_id: key.slice(9) });
      else showDistrict({ district_id: key.slice(9) });
    },
  });
  const districtElement = (item) => createMarker("district:" + item.district_id);
  const locationElement = (item) => createMarker(
    "location:" + item.location_id, !matchesFilter(item)
  );
  eval(renderSource);
  return {
    render,
    select(key) { selectedKey = key; },
    filter(value) { activeFilter = value; },
    state() {
      return {
        selectedKey, detail, focusCount,
        focused: document.activeElement?.dataset?.mapKey,
        children: canvas.children.map((item) => ({
          key: item.dataset.mapKey, hidden: item.hidden,
        })),
      };
    },
  };
`);
const harness = makeHarness(document, canvas, renderSource);
const model = {
  summary: { district_count: 1, location_count: 2, owned_count: 1 },
  districts: [{ district_id: "kreuzberg" }],
  locations: [
    { location_id: "A", owned: true, tier: "prime" },
    { location_id: "B", owned: false, tier: "standard" },
  ],
};
let passed = 0;
function check(name, condition) {
  assert.ok(condition, name);
  passed++;
  process.stdout.write("PASS " + name + "\n");
}

harness.render(model);
check("initial selection", harness.state().selectedKey === "location:A");

harness.select("location:B");
document.activeElement = canvas.children.find((item) => item.dataset.mapKey === "location:B");
harness.render(model);
check("location focus survives refresh",
  harness.state().selectedKey === "location:B" && harness.state().focused === "location:B");

harness.select("district:kreuzberg");
document.activeElement = canvas.children.find((item) => item.dataset.mapKey === "district:kreuzberg");
harness.render(model);
check("district focus survives refresh",
  harness.state().selectedKey === "district:kreuzberg" && harness.state().focused === "district:kreuzberg");

document.activeElement = null;
harness.select("location:B");
harness.filter("owned");
harness.render(model);
check("filtered location cannot remain selected",
  harness.state().selectedKey === "location:A" &&
  harness.state().children.find((item) => item.key === "location:B").hidden);

harness.filter("hall");
harness.render(model);
check("empty filter clears selection",
  harness.state().selectedKey === null && harness.state().detail === "Keine Treffer");

harness.filter("all");
const outside = { dataset: { mapKey: "outside" } };
document.activeElement = outside;
harness.render(model);
check("refresh does not steal outside focus", document.activeElement === outside);

harness.select("location:missing");
harness.render(model);
check("removed location falls back to visible location",
  harness.state().selectedKey === "location:A");

process.stdout.write("RESULT: " + passed + "/7 PASS\n");
