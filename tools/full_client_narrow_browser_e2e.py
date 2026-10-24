#!/usr/bin/env python3
"""Real Chromium regression for the *complete* local A4 client at small widths.

The fixture is built through the canonical runtime in an isolated temporary
save directory. Browser interactions only change presentation preferences,
filters and anchor navigation; no gameplay command is sent. A 400x300 CSS
viewport exercises narrow responsive layout, NOT Chromium's menu zoom.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile

from playwright.sync_api import sync_playwright

import start_a4_acceptance as acceptance


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def check_geometry(page, label: str) -> None:
    geometry = page.evaluate("""() => {
      const root = document.documentElement;
      const width = window.innerWidth;
      const selectors = ['.masthead', '.ops-hud', '.quick-nav', '.workspace',
                         '#ui-options-toggle', '#map-pro-panel',
                         '#profile-panel', '#event-timeline-panel',
                         '#property-panel', '#economy-panel', '#save-panel'];
      const nodes = selectors.flatMap(selector =>
        Array.from(document.querySelectorAll(selector))
          .filter(node => node.getClientRects().length > 0)
          .map(node => {
            const box = node.getBoundingClientRect();
            return {selector, left: box.left, right: box.right, width: box.width};
          }));
      const overflowing = Array.from(document.querySelectorAll('body *'))
        .filter(node => node.getClientRects().length > 0 &&
                        !node.closest('.quick-nav'))
        .map(node => {
          const box = node.getBoundingClientRect();
          return {tag: node.tagName.toLowerCase(), id: node.id,
                  className: typeof node.className === 'string' ? node.className.slice(0, 80) : '',
                  left: Math.round(box.left), right: Math.round(box.right),
                  scrollWidth: node.scrollWidth, clientWidth: node.clientWidth,
                  overflowX: getComputedStyle(node).overflowX};
        })
        .filter(node => node.right > width + 1)
        .sort((a, b) => b.right - a.right).slice(0, 15);
      return {width, clientWidth: root.clientWidth, scrollWidth: root.scrollWidth,
              nodes, overflowing};
    }""")
    require(geometry["scrollWidth"] <= geometry["clientWidth"] + 1,
            f"{label}: horizontaler Seitenüberlauf: {geometry}")
    require(geometry["nodes"], f"{label}: keine sichtbaren Spielbereiche")
    for node in geometry["nodes"]:
        require(node["width"] > 0 and node["left"] >= -1 and
                node["right"] <= geometry["width"] + 1,
                f"{label}: {node['selector']} außerhalb des Fensters: {node}")


def exercise_client(browser, address: str, width: int, height: int) -> None:
    page = browser.new_page(
        viewport={"width": width, "height": height},
        device_scale_factor=1,
        reduced_motion="reduce",
    )
    writes = []
    page.on("request", lambda request: writes.append(
        f"{request.method} {request.url}"
    ) if request.method not in ("GET", "HEAD", "OPTIONS") else None)
    try:
        page.goto(address, wait_until="domcontentloaded", timeout=20000)
        page.wait_for_function(
            "() => document.getElementById('connection-status')?.textContent.includes('BEREIT')",
            timeout=20000,
        )
        page.wait_for_function(
            "() => !document.getElementById('event-timeline-status')?.textContent.includes('Timeline wird geladen')",
            timeout=20000,
        )
        page.locator("#berlin-map-canvas .map-marker.owned").first.wait_for(
            state="visible", timeout=20000,
        )
        require(page.locator("#first-run").is_hidden(),
                "Bestätigter Runtime-Starter zeigt unerwartet den Erststart")
        for panel in ("profile-panel", "street-panel", "map-pro-panel",
                      "event-timeline-panel", "property-panel",
                      "economy-panel", "save-panel"):
            require(page.locator(f"#{panel}").is_visible(),
                    f"{width}x{height}: Spielbereich {panel} fehlt")
        require(page.evaluate(
            "matchMedia('(prefers-reduced-motion: reduce)').matches"),
            "Reduzierte Bewegung ist nicht im Browser aktiviert")
        require(page.evaluate("innerWidth") == width,
                f"CSS-Viewport stimmt nicht mit {width} überein")
        require(page.evaluate(
            "matchMedia('(max-width: 560px)').matches") == (width <= 560),
            "Responsiver 560px-Umbruch hat falschen Zustand")
        check_geometry(page, f"{width}x{height}: Ausgangsansicht")

        # Real Tab/Enter and Space events, not synthetic DOM KeyboardEvents.
        page.locator('a.skip-link[href="#workspace"]').focus()
        page.keyboard.press("Tab")
        require(page.evaluate("document.activeElement?.id") == "ui-options-toggle",
                "Tab vom Sprunglink erreicht ANSICHT nicht")
        page.keyboard.press("Enter")
        require(page.locator("#ui-options-panel").is_visible(),
                "ANSICHT lässt sich nicht per Enter öffnen")
        require(page.locator("#ui-options-toggle").get_attribute("aria-expanded") == "true",
                "ANSICHT meldet den geöffneten Zustand nicht")
        for preference, body_class in (("largeText", "ui-large-text"),
                                       ("highContrast", "ui-high-contrast")):
            control = page.locator(f'[data-ui-pref="{preference}"]')
            control.focus()
            page.keyboard.press("Space")
            require(control.is_checked(), f"{preference} nicht per Leertaste aktiviert")
            require(page.locator("body").evaluate(
                "(node, name) => node.classList.contains(name)", body_class),
                f"{preference} nicht im ganzen Client wirksam")
        require(page.evaluate(
            "() => parseFloat(getComputedStyle(document.body).fontSize)") >= 21,
            "Große Schrift nicht wirksam")
        check_geometry(page, f"{width}x{height}: große Schrift / hoher Kontrast")
        page.locator("#ui-options-close").focus()
        page.keyboard.press("Enter")
        require(page.locator("#ui-options-panel").is_hidden(),
                "Ansichtseinstellungen lassen sich nicht per Enter schließen")

        nav = page.locator('.quick-nav a[href="#map-pro-panel"]')
        nav.focus()
        page.keyboard.press("Enter")
        require(page.evaluate("location.hash") == "#map-pro-panel",
                "Tastatur-Navigation erreicht die Karte nicht")
        require(page.locator("#map-pro-panel").is_visible(),
                "Karte nach Schnellnavigation nicht sichtbar")
        page.locator('[data-map-filter="all"]').focus()
        page.keyboard.press("Tab")
        require(page.evaluate(
            "document.activeElement?.dataset?.mapFilter") == "owned",
            "Kartenfilter sind nicht in der nativen Tabfolge")
        page.keyboard.press("Enter")
        require(page.locator('[data-map-filter="owned"]').get_attribute(
            "aria-pressed") == "true",
            "Eigentumsfilter reagiert nicht auf Enter")
        require(page.locator("#berlin-map-canvas .map-marker.owned").first.is_visible(),
                "Bestätigtes Eigentum nach Filterung verschwunden")
        check_geometry(page, f"{width}x{height}: Navigation / Eigentumsfilter")
        require(not writes, f"Darstellungsprüfung löste Schreibanfragen aus: {writes}")
        print(f"FULL_CLIENT_NARROW_BROWSER_E2E: PASS {width}x{height} CSS "
              "– gesamte Runtime-Oberfläche, Tab/Enter/Space, große Schrift, "
              "Kontrast, reduzierte Bewegung, kein Seitenüberlauf, keine Schreibanfrage")
    finally:
        page.close()


def run() -> None:
    browser_bin = acceptance.find_browser()
    require(browser_bin is not None,
            "Chromium/Chrome fehlt für den vollständigen Client-Browsertest")
    with tempfile.TemporaryDirectory(prefix="bunkerfrequenz-full-ui-e2e-") as save_dir:
        acceptance.prepare_owned_map_fixture(save_dir)
        process = acceptance._start_server(save_dir)
        try:
            address = acceptance._wait_for_address(process)
            acceptance.probe_http(address)
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(
                    executable_path=browser_bin, headless=True,
                    args=["--no-sandbox", "--disable-dev-shm-usage"],
                )
                try:
                    for width, height in ((800, 600), (400, 300)):
                        exercise_client(browser, address, width, height)
                finally:
                    browser.close()
        finally:
            if process.poll() is None:
                process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
            if process.stdout is not None:
                process.stdout.close()


if __name__ == "__main__":
    try:
        run()
    except Exception as exc:
        print(f"FULL_CLIENT_NARROW_BROWSER_E2E: FAIL – "
              f"{type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(1)
