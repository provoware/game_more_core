# BUNKERFREQUENZ – Vorrelease-Pflichtmatrix

Stand: 21.10.2026. Ausgangs-HEAD: `15b440c974acb3bc594d2d4c8e7ecd3f53d28c31`.

Diese Matrix ist eine Entwicklungsplanung, keine Freigabe. Ein PASS erfordert den tatsächlich geprüften Commit und die dazugehörige CI-Run-ID.

| Pflicht | Prüfquelle | Status |
|---|---|---|
| Spiellogik und vollständige Eventpartie | `tests/runtime/test_a4_first_run_smoke.py` | Neue Gesamtabnahme offen |
| Charakter, Jobs, Bank, Handel, Immobilien, Bezirke und Ranking | `TODO.md`, `FEATURE_POOL.md` | Funktionen dokumentiert; Regression offen |
| Speicherung, Journal, Snapshot, Neustart und Recovery | `docs/PERSISTENCE_CONTRACT.md` | Neue Gesamtabnahme offen |
| Sicherheit, Startbarkeit und Belastung | `docs/RELEASE_ACCEPTANCE_0.8.4.md` | Neue Gesamtabnahme offen |
| Layout 800×600, 200 % Skalierung, Kontrast, Tastatur | `tools/desktop_browser_e2e_pro.py` | Vollständiger Nachweis offen |
| Paket, SHA-256, Wiederherstellung und Release-Unterlagen | `docs/RELEASE_AUTOPILOT_PRO.md` | Neue Gesamtabnahme offen |
| Main-Integrität und Status-Sync | `.github/workflows/` | Rote Checks auf Ausgangs-HEAD; zu klären |
| Nutzer-Sichtprüfung und Kubuntu-Praxistest | Einmaliges finales Release-Gate | Ausschließlich unmittelbar vor Release |

Nächster technischer Schritt: Release-Prüfung gegen leere oder unbekannte Gate-Zustände absichern. Kein Release, kein ungeprüfter Merge und keine Nutzer-Zwischenabnahme.
