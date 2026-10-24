#!/usr/bin/env python3
"""Chromium regression for the Berlin map at a narrow responsive layout viewport.

400x300 CSS pixels exercise the breakpoints a nominal 800x600 display can
reach at 200% browser zoom. This is a responsive-layout *proxy*, not proof
that the browser's own zoom control was used.
"""
from __future__ import annotations

import shutil
import sys

from playwright.sync_api import sync_playwright

from map_keyboard_zoom_browser_e2e import MODEL, ROOT, _map_html, _require


def run() -> None:
    browser_bin = next(
        (path for name in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable")
         if (path := shutil.which(name))),
        None,
    )
    _require(browser_bin is not None, "Chromium/Chrome fehlt für den responsiven Kartentest")
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            executable_path=browser_bin, headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        try:
            page = browser.new_page(
                viewport={"width": 400, "height": 300}, device_scale_factor=1,
                reduced_motion="reduce",
            )
            page.set_content(_map_html(), wait_until="load")
            page.add_style_tag(path=str(ROOT / "web/a4/styles.css"))
            page.add_script_tag(path=str(ROOT / "web/a4/map_pro.js"))
            page.evaluate("document.body.classList.add('ui-large-text', 'ui-high-contrast')")
            page.evaluate("model => window.BunkerMapPro.render(model)", MODEL)

            _require(page.evaluate("innerWidth === 400 && innerHeight === 300"),
                     "Responsiver CSS-Viewport ist nicht 400x300")
            _require(page.evaluate("matchMedia('(max-width: 560px)').matches"),
                     "Schmaler CSS-Breakpoint wurde nicht aktiviert")
            _require(page.locator("#map-pro-panel").is_visible(),
                     "Kartenpanel ist im schmalen Layout nicht sichtbar")

            def check_layout(label: str) -> None:
                dimensions = page.evaluate("""() => {
                    const root = document.documentElement;
                    const panel = document.getElementById('map-pro-panel').getBoundingClientRect();
                    const canvas = document.getElementById('berlin-map-canvas').getBoundingClientRect();
                    const detail = document.getElementById('map-detail').getBoundingClientRect();
                    return { overflow: root.scrollWidth - root.clientWidth,
                             panelLeft: panel.left, panelRight: panel.right,
                             canvasBottom: canvas.bottom, detailTop: detail.top,
                             filters: Array.from(document.querySelectorAll('[data-map-filter]'),
                                 node => { const rect = node.getBoundingClientRect();
                                           return {left: rect.left, right: rect.right}; }) };
                }""")
                _require(dimensions["overflow"] <= 1,
                         f"{label}: horizontaler Seitenüberlauf: {dimensions}")
                _require(dimensions["panelLeft"] >= -1 and dimensions["panelRight"] <= 401,
                         f"{label}: Kartenpanel ragt über den Bildschirm: {dimensions}")
                _require(dimensions["detailTop"] >= dimensions["canvasBottom"] - 1,
                         f"{label}: Kartendetails stehen nicht unter der Karte: {dimensions}")
                _require(all(f["left"] >= -1 and f["right"] <= 401
                             for f in dimensions["filters"]),
                         f"{label}: Filterknopf abgeschnitten: {dimensions}")

            check_layout("Start / große Schrift / hoher Kontrast")
            # Native keys must continue to work at the narrow breakpoint.
            page.locator('[data-map-filter="all"]').focus()
            page.keyboard.press("Tab")
            _require(page.evaluate("document.activeElement?.dataset?.mapFilter") == "owned",
                     "Tab erreicht Eigentumsfilter nicht")
            page.keyboard.press("Enter")
            _require(page.locator('[data-map-filter="owned"]').get_attribute("aria-pressed") == "true",
                     "Enter aktiviert Eigentumsfilter nicht")
            _require(page.locator('[data-map-key="location:club_alpha"]').is_visible(),
                     "Eigentumsmarker im schmalen Layout verschwunden")
            _require(not page.locator('[data-map-key="location:club_beta"]').is_visible(),
                     "Ausgeblendeter Ort im schmalen Layout sichtbar")
            page.locator('[data-map-key="location:club_alpha"]').focus()
            page.evaluate("model => window.BunkerMapPro.render(model)", MODEL)
            _require(page.evaluate("document.activeElement?.dataset?.mapKey") == "location:club_alpha",
                     "Fokusverlust nach Aktualisierung im schmalen Layout")
            _require("CLUB ALPHA" in page.locator("#map-detail").inner_text(),
                     "Bestätigte Ortsdetails fehlen nach Fokusaktualisierung")
            check_layout("Filter / Aktualisierung / Details")
            print("MAP_NARROW_BROWSER_E2E: PASS – Chromium, 400x300 CSS, "
                  "560px-Breakpoint, große Schrift, hoher Kontrast, Reduced Motion, "
                  "native Tab/Enter, Fokus, kein horizontaler Seitenüberlauf")
        finally:
            browser.close()


if __name__ == "__main__":
    try:
        run()
    except Exception as exc:
        print(f"MAP_NARROW_BROWSER_E2E: FAIL – {type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(1)
