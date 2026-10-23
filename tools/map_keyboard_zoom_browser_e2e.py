#!/usr/bin/env python3
"""Real Chromium keyboard and 200% display-scale regression for the canonical Berlin map.

This is an isolated, read-only presentation fixture: it loads the checked-out
map_pro.js, styles.css and map section from index.html. No server, saves, or
runtime commands are involved. The browser receives only synthetic map data.
"""
from __future__ import annotations

from pathlib import Path
import re
import shutil
import sys

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
MODEL = {
    "summary": {"district_count": 1, "location_count": 2, "owned_count": 1},
    "districts": [{
        "district_id": "kreuzberg",
        "map_box": {"x": 12, "y": 12, "w": 70, "h": 70},
        "metrics": {"heat": 42, "prestige": 50, "police_pressure": 10, "scene_activity": 70},
    }],
    "locations": [
        {
            "location_id": name,
            "owned": owned,
            "tier": "prime" if owned else "standard",
            "score": 85.5 if owned else 21.0,
            "rank": 1 if owned else 2,
            "is_hall_of_tribute": False,
            "position": {"x": 40 if owned else 70, "y": 42 if owned else 65},
            "values": {"prestige": 70, "audience_pull": 60, "risk": 20,
                       "underground_factor": 90, "utility": 30},
            "purchasable": True,
            "purchase_price_cents": 120000,
            "upgrades": [],
            "upgrade_level_total": 0,
        }
        for name, owned in (("club_alpha", True), ("club_beta", False))
    ],
}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _map_html() -> str:
    source = (ROOT / "web/a4/index.html").read_text(encoding="utf-8")
    section = re.search(r'<section id="map-pro-panel"[^>]*>.*?</section>', source, re.DOTALL)
    _require(section is not None, "Originaler Kartenabschnitt fehlt in index.html")
    return ('<!doctype html><html lang="de"><head><meta charset="utf-8"></head>'
            '<body><main class="workspace">' + section.group(0) + '</main></body></html>')


def run() -> None:
    browser_bin = next((path for name in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable")
                        if (path := shutil.which(name))), None)
    _require(browser_bin is not None, "Chromium/Chrome ist Pflicht für den echten Karten-Browsertest")
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=browser_bin, headless=True,
                                              args=["--no-sandbox", "--disable-dev-shm-usage"])
        try:
            page = browser.new_page(viewport={"width": 800, "height": 600}, device_scale_factor=1)
            page.set_content(_map_html(), wait_until="load")
            page.add_style_tag(path=str(ROOT / "web/a4/styles.css"))
            page.add_script_tag(path=str(ROOT / "web/a4/map_pro.js"))
            page.evaluate("model => window.BunkerMapPro.render(model)", MODEL)
            owned = page.locator('[data-map-key="location:club_alpha"]')
            other = page.locator('[data-map-key="location:club_beta"]')
            _require(owned.is_visible() and other.is_visible(), "Beide Orte müssen zunächst sichtbar sein")

            # Native keyboard events, not synthetic JS KeyboardEvent or .click().
            all_filter = page.locator('[data-map-filter="all"]')
            all_filter.focus()
            page.keyboard.press("Tab")
            _require(page.evaluate('document.activeElement?.dataset?.mapFilter') == "owned",
                     "Native Tab-Taste erreicht Eigentumsfilter nicht")
            page.keyboard.press("Enter")
            _require(page.locator('[data-map-filter="owned"]').get_attribute("aria-pressed") == "true",
                     "Enter aktiviert den Eigentumsfilter nicht")
            _require(owned.is_visible() and not other.is_visible(), "Eigentumsfilter zeigt falsche Orte")
            _require(page.evaluate('document.activeElement?.dataset?.mapFilter') == "owned",
                     "Filter-Aktivierung verliert den Tastaturfokus")

            # Follow the actual browser tab sequence until the visible location.
            reached = False
            for _ in range(16):
                page.keyboard.press("Tab")
                focused = page.evaluate('document.activeElement?.dataset?.mapKey || null')
                _require(focused != "location:club_beta", "Verborgener Ort wird per Tab erreicht")
                if focused == "location:club_alpha":
                    reached = True
                    break
            _require(reached, "Sichtbarer Kartenort ist per nativer Tabfolge nicht erreichbar")
            page.evaluate("model => window.BunkerMapPro.render(model)", MODEL)
            _require(page.evaluate('document.activeElement?.dataset?.mapKey') == "location:club_alpha",
                     "Kartenaktualisierung verliert den nativen Tastaturfokus")

            # A removed focused marker must hand focus to an existing visible one.
            all_filter.focus()
            page.keyboard.press("Enter")
            other.focus()
            _require(page.evaluate('document.activeElement?.dataset?.mapKey') == "location:club_beta",
                     "Entfernungsprobe konnte Ort B nicht fokussieren")
            page.evaluate("model => window.BunkerMapPro.render(model)",
                          {**MODEL, "locations": [MODEL["locations"][0]],
                           "summary": {**MODEL["summary"], "location_count": 1}})
            _require(page.evaluate('document.activeElement?.dataset?.mapKey') == "location:club_alpha",
                     "Fokus geht bei aktualisiertem Modell verloren")

            # At 200% rendered display scale, map controls must remain usable.
            # CSS zoom is a rendering-scale proxy, NOT a claim of browser UI zoom.
            page.evaluate('document.documentElement.style.zoom = "200%"')
            _require(page.evaluate('getComputedStyle(document.documentElement).zoom') in ("2", "200%"),
                     "200%-Darstellungsskalierung wurde nicht angewendet")
            page.locator('[data-map-view-action="reset"]').focus()
            _require(page.evaluate('document.activeElement?.dataset?.mapViewAction') == "reset",
                     "Ansichtsreset bei 200% nicht fokussierbar")
            page.keyboard.press("Enter")
            _require("Gesamtansicht" in page.locator("#map-view-status").inner_text(),
                     "Ansichtsreset bei 200% reagiert nicht auf Enter")
            _require(page.evaluate('document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1'),
                     "Horizontaler Seitenüberlauf bei 800x600 und 200% Darstellungsskalierung")
            print("MAP_BROWSER_E2E: PASS – Chromium, 800x600, native Tab/Enter, Refresh, 200% CSS-Skalierung")
        finally:
            browser.close()


if __name__ == "__main__":
    try:
        run()
    except Exception as exc:
        print(f"MAP_BROWSER_E2E: FAIL – {type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(1)
