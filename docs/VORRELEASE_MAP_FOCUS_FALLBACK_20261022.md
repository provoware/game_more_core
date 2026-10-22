# Vorrelease – Kartenfokus bei Filterung und Aktualisierung (22.10.2026)

**Scope:** ausschließlich `web/a4/map_pro.js`, `tests/presentation/map_focus_refresh_harness.cjs` und zugehörige Kartenhilfe; keine Gameplay-, Geld- oder Spielstandsänderungen.

**Ausgangs-HEAD:** `300da9d213b67661daca182f77c584037e500e66`.

## Befund und Reproduktion
Der bestehende Renderer erhält den Fokus, wenn der Kartenmarker nach einer Aktualisierung sichtbar bleibt. Wird der fokussierte Marker jedoch durch einen Filter ausgeblendet oder aus dem Modell entfernt, ist nach dem DOM-Neuaufbau keine gültige fokussierte Kartelement-Referenz mehr vorhanden.

## Geplante Korrektur
Nach `render()` zuerst den weiterhin sichtbaren fokussierten Marker suchen; sonst den neu ausgewählten sichtbaren Marker fokussieren. Niemals einen ausgeblendeten Marker fokussieren. Vorhandene Gameplay-Projections und persistierte Daten bleiben unverändert.

## Nachweise dieses Arbeitslaufs
- PASS: bestehender, aus GitHub gelesener Renderer + bestehender Harness: 7/7.
- PASS (Negativkontrolle): erweiterter Harness scheitert erwartungsgemäß auf unverändertem Renderer beim Test `hidden focused location transfers focus to visible selection`.
- PASS: mit minimaler Korrektur des echten Renderer-Quelltexts im isolierten JavaScript-Harness: 9/9.
- BLOCKED: GitHub-Dateiaktualisierung wurde durch Sicherheitsprüfung der Schnittstelle verweigert. Die Korrektur ist **nicht** auf GitHub gespeichert.
- NICHT AUSGEFÜHRT: GitHub-CI für diese Korrektur, echter Chromium-Tab-Lauf, 800×600 mit 175–200 % Zoom.

## Verbindliche Vorrelease-Pflichten
Siehe bereits offenen PR #279 (`docs/VORRELEASE_PFLICHTMATRIX.md` auf dessen Entwicklungszweig). Kein Matrix-PASS aus diesem lokalen Test ableiten. Erforderlich bleiben vollständige Spielverläufe, Save/Recovery, Gameplay/Balance, Browser-/Tastatur-/Skalierungstests, Performance, Release-Paket und grüne Required Checks.

## Nächste unabhängige Pflichtarbeit
1. Fokuskorrektur samt zwei Regressionstests regulär übertragen, sobald die Schreibschnittstelle dies erlaubt.
2. Browser-Test: Tab-Folge und Fokus bei Filterwechsel/Markerentfernung sowie 800×600/200 % Zoom auf einem exakt benannten Commit nachweisen.
3. Nach grünen Pflichtprüfungen erst den vollständigen technischen Release-Kandidaten einfrieren; persönliche Kubuntu-/Sichtabnahme bleibt bis dahin zurückgestellt.

**Keine Freigabe, kein Merge, kein Release.**
