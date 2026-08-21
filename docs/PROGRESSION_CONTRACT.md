# Progression Contract 0.4.1

## Zweck

Dieser Vertrag definiert die mathematische Character-Forge-Basis, bevor Spiel-Laufzeitcode entsteht.

## Datenprinzip

Die 165 Traits sind individuelle Namen für 15 gemeinsame Wirkungsfamilien. Numerische Werte werden nicht 165-mal kopiert. Jeder Trait referenziert bereits eine Effektvorlage. Ein Balance-Fix an einer Vorlage korrigiert damit alle zugehörigen Traits ohne redundante Daten.

## Trait-Fortschritt

Eine Stufe entsteht nur, wenn gleichzeitig Evidenz, Character-Level, Anzahl qualifizierender Ereignisse und bei höheren Stufen mehrere Erfahrungsquellen erreicht wurden. Ein einzelner Glückstreffer kann deshalb keinen Legenden-Trait erzeugen.

## Effektgrenzen

Pro Zielwert gelten Stack-Caps: positive Prozentmodifikatoren maximal +35 %, negative maximal -20 %.

## Spezialisierung

Eine Spezialisierung benötigt genügend Level, Mindestdurchschnitt der Fokus-Skills und einen messbaren Vorsprung gegenüber dem Durchschnitt aller Skills. Eine primäre Spezialisierung ist vorgesehen. Ab Level 25 darf eine sekundäre entstehen, wenn ihr Score maximal 10 % hinter der primären liegt; ihre Wirkung beträgt 60 %. Ein Wechsel benötigt 30 Spieltage anhaltend veränderter Entwicklung.

Konsequenzen:
- Tendenz: +2 % Fokus-XP, 0 % außerhalb
- Profil: +5 % Fokus-XP, -1 % außerhalb
- Identität: +8 % Fokus-XP, -3 % außerhalb
- Meisterschaft: +12 % Fokus-XP, -5 % außerhalb

## Simulator

Der Simulator ist unabhängig von UI-, Save- und Sync-Code, nutzt nur die Python-Standardbibliothek und einen deterministischen Seed.

```bash
python3 tools/simulate_characters/progression_simulator.py --runs 1000 --days 720 --seed 90409 --output reports/PROGRESSION_SIMULATION_0.4.1.json
```

Balance-Gates:
1. Generalisten erhalten keine erzwungene Spezialisierung.
2. fokussierte Spielweisen entwickeln zuverlässig Spezialisierungen.
3. fokussierte Spielweisen entwickeln mehrere tiefe Traits.
4. Generalisten bleiben breit, aber nicht automatisch tief spezialisiert.
5. Tier 5 wird nicht massenhaft freigeschaltet.
6. der Referenzzeitraum erreicht nicht automatisch Level 50.
