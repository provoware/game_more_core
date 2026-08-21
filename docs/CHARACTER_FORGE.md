# Character Forge 0.4.1

## Grundsatz

Alle 11 Hauptfiguren starten spielmechanisch gleich. Narrativer Kontext darf Verhalten anregen, aber keine Fähigkeit festlegen.

## Entwicklung

Charaktere entwickeln sich durch Handlung, Training, Praxis, Krisen, Teamarbeit, Entdeckungen sowie Erfolge und Fehlschläge. Grundstorys geben keine Startboni.

## Skill-Fortschritt

Der Skillbereich reicht von 10 bis 100. Die verbindliche Skill-XP-Formel und Wertebereiche liegen in `manifests/SKILL_MANIFEST.json` und `manifests/PROGRESSION_MANIFEST.json`.

## Training

Training steigert Skills regulär, prägt Traits aber schwächer als echte Praxis. Trait-Evidenzfaktor Training: `0,35`.

Trainingswirkung pro Tag: 100 %, 85 %, 65 %, danach 40 %.

## Traits

Der bestehende Katalog umfasst 165 individuelle Trait-Namen in `manifests/TRAIT_MANIFEST.json`. Die numerische Engine liegt getrennt in `manifests/TRAIT_ENGINE_MANIFEST.json`.

Trait-Stufen:
1. Neigung – Evidenz 220, Level 3, 12 Ereignisse
2. Gewohnheit – Evidenz 480, Level 8, 25 Ereignisse
3. Charakterzug – Evidenz 850, Level 15, 45 Ereignisse, mindestens zwei Quellen
4. Markenzeichen – Evidenz 1300, Level 25, 70 Ereignisse, mindestens zwei Quellen
5. Legendenmerkmal – Evidenz 1900, Level 40, 110 Ereignisse, mindestens drei Quellen

## Trait-Evidenz

- Training: 0,35
- Praxis: 1,00
- Krise: 1,25
- Teamarbeit: 1,10
- Entdeckung: 1,10
- Erfolg: 0,90
- Fehlschlag: 0,70

## Konflikte

0.4.1 verwendet bewusst keine harten Trait-Ausschlüsse. Nur zwei Soft-Konflikte sind begründet:
- Planer ↔ Improvisierer ab Stufe 3: positive Wirkung beider Seiten × 0,85
- Detailmensch ↔ Opportunist ab Stufe 4: positive Wirkung beider Seiten × 0,90

## Spezialisierungen

Spezialisierungen werden aus dauerhaftem Skill-Vorsprung berechnet: Klangarchitektur, Einsatzleitung, Szenenetzwerk, Spurensuche, Impro-Werkstatt und Crew-Stabilität. Stufen: Tendenz, Profil, Identität, Meisterschaft. Generalisten bleiben ausdrücklich möglich.

## Balance-Nachweis

`tools/simulate_characters/progression_simulator.py` simuliert die Regeln reproduzierbar. Referenz: 1.000 Charaktere, 720 Spieltage, Seed 90409, sechs Balance-Gates bestanden. Bericht: `reports/PROGRESSION_SIMULATION_0.4.1.json`.
