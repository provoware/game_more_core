# Repository-Regeln: Tool, Dokumentation und Vertrag

## Zweck

Diese Regeln halten das Repository klein und eindeutig. Jede Information besitzt genau einen zuständigen Ort; Kopien und parallele Implementierungen werden vermieden.

## Einordnung

| Art | Ort | Enthält | Enthält nicht |
|---|---|---|---|
| Runtime-Code | `src/` | ausführbare Spiellogik und technische Adapter | Entwickler-Skripte, sichtbare Texte |
| Basistool | `tools/` | kleines direkt ausführbares Hilfsprogramm für Prüfung oder reproduzierbare Erzeugung | Fachvertrag, Runtime-Code, lange Anleitung |
| Dokumentation | `docs/` | Erklärung, Architekturentscheidung, Bedien- oder Entwicklungsanleitung | ausführbare Logik, doppelte Zahlenregeln |
| Manifest | `manifests/` | kanonische maschinenlesbare Fachregeln und Kataloge | Erläuterung in Prosa |
| Schema | `schemas/` | maschinenlesbare Struktur- und Typverträge | Beispieldaten oder Berichte |
| Inhalt | `content/` | lokalisierte sichtbare Texte und Figureninhalte | technische Regeln |
| Test | `tests/` | prüfbare Erwartungen an direkte Verträge | Produktionslogik |
| Bericht | `reports/` | reproduzierbarer, versionierter Prüfnachweis | volatile Laufdaten ohne Freigabegrund |

## Was als Basistool gilt

Ein Basistool unter `tools/` muss alle folgenden Bedingungen erfüllen:

1. Es löst genau eine Entwicklungsaufgabe und ist direkt über die Kommandozeile startbar.
2. Es importiert keine Spiel-UI und wird nicht von Runtime-Code benötigt.
3. Es liest kanonische Regeln aus Manifesten oder Schemas, statt sie nochmals festzuschreiben.
4. Es nutzt möglichst die Standardbibliothek; jede neue Abhängigkeit braucht einen belegten Vorteil.
5. Bei Zufall besitzt es einen expliziten Seed (Startwert für reproduzierbaren Zufall).
6. Bei erzeugten Dateien dokumentiert der Aufruf Quelle, Parameter und Ziel.
7. Die Kurzbedienung steht in `README.md`; längere Erklärungen stehen in `docs/`.

Unterverzeichnisse sind nur zulässig, wenn ein Tool mehrere eng zusammengehörige Dateien benötigt. Ein einzelnes Skript bleibt direkt unter `tools/`.

## Was Dokumentation leisten muss

- Markdown-Dateien erklären **warum** ein Vertrag besteht und **wie** er benutzt wird.
- Zahlen, IDs und erlaubte Ereignistypen werden aus Manifesten referenziert, nicht als zweite Wahrheit gepflegt.
- Ein Orientierungsdokument kennzeichnet klar, wenn ein Manifest, Schema oder Fachvertrag Vorrang hat.
- Bilder liegen unter `docs/assets/` und werden von einem Dokument aus eingebunden.
- Dateinamen sind stabil, sprechend und für fachliche Verträge in Großbuchstaben gehalten.

## Entscheidungsweg für neue Dateien

```text
Muss die Datei im Spiel ausgeführt werden?       → src/
Ist sie ein kleines ausführbares Entwicklerwerkzeug? → tools/
Definiert sie maschinenlesbare Fachregeln?       → manifests/
Definiert sie eine Datenstruktur?                → schemas/
Ist sie sichtbarer/lokalisierter Inhalt?         → content/
Prüft sie einen Vertrag?                         → tests/
Belegt sie einen reproduzierbaren Prüflauf?      → reports/
Erklärt sie einen Zusammenhang?                  → docs/
```

Im Zweifel wird keine neue Datei angelegt, bevor die bestehende zuständige Stelle geprüft wurde.

## Bestehende Basiswerkzeuge

| Tool | Aufgabe | Kanonische Eingaben |
|---|---|---|
| `tools/validate_action_contract.py` | Action-Gewichte und Referenzen prüfen | Action-, Skill-, Trait- und Journal-Manifeste |
| `tools/simulate_characters/progression_simulator.py` | Progression deterministisch simulieren | Progression- und Trait-Engine-Manifeste |

Beide Werkzeuge bleiben von Runtime und Dokumentation getrennt. Weitere Kopien oder Wrapper (Aufrufhüllen) werden nur bei einem neuen, belegten Bedarf angelegt.

## Änderungsregel

Verschiebungen erfolgen nur in einer eigenen geplanten Iteration, nachdem alle Referenzen ermittelt wurden. Reine Aufräumarbeiten dürfen keine stabilen Importpfade, Berichte oder historischen Nachweise brechen.
