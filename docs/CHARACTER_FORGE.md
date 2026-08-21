# Character Forge 0.4.1

## Grundsatz

Alle 11 Hauptfiguren starten spielmechanisch gleich. Narrativer Kontext darf Verhalten anregen, aber keine Fähigkeit festlegen.

## Startwerte

Alle 16 Kernwerte starten bei `10`, Level bei `1`, Gesamt-XP bei `0`, Energie bei `100`, Stress und Ruf bei `0`.

Kernwerte:
`technik`, `musik`, `organisation`, `kreativitaet`, `kommunikation`, `menschenkenntnis`, `orientierung`, `handwerk`, `logistik`, `improvisation`, `verhandlung`, `szenewissen`, `risikoeinschaetzung`, `konzentration`, `belastbarkeit`, `instinkt`.

## Entwicklung

Charaktere entwickeln sich durch:
- Handlung
- Training
- Praxis
- Krisen
- Teamarbeit
- Entdeckungen
- Erfolge und Fehlschläge

Grundstorys geben keine Startboni. Eine Figur kann sich vollständig entgegen ihrer erzählerischen Ausgangsrolle entwickeln.

## XP-Grundformel

```text
Skill-XP =
Basis-XP
× Schwierigkeit
× Qualität
× Neuheit
× Erschöpfung
× Wiederholung
× Quellenfaktor
× Trainingswirkung (nur bei Training)
```

Die exakten Wertebereiche sind in `manifests/SKILL_MANIFEST.json` definiert. Skillwerte reichen von 10 bis 100; die XP-Kurve liegt in `manifests/PROGRESSION_MANIFEST.json`.

## Training

Training steigert Skills regulär, erzeugt für Traits aber nur `0,35` der normalen Evidenz und kann Praxis damit nicht vollständig ersetzen.

Trainingswirkung pro Tag als Ausgangspunkt:
- erste Einheit: 100 %
- zweite Einheit: 85 %
- dritte Einheit: 65 %
- danach: 40 %

## Gesamtlevel

Ausgangsformel:

```text
Gesamt-XP(L) = 120 × (L - 1)^1,62 + 80 × (L - 1)
```

Nach Level 50 beginnt ein offenes Resonanzsystem.

## Traits

Es existieren 15 gemeinsame Effektvorlagen und 165 individuelle Trait-Namen. Alle Traits starten gesperrt. Der bestehende Trait-Katalog bleibt in `manifests/TRAIT_MANIFEST.json` unverändert; die numerische Engine liegt getrennt in `manifests/TRAIT_ENGINE_MANIFEST.json`.

Trait-Stufen:
1. Neigung – Evidenz 220, Level 3, 12 Ereignisse
2. Gewohnheit – Evidenz 480, Level 8, 25 Ereignisse
3. Charakterzug – Evidenz 850, Level 15, 45 Ereignisse, mindestens zwei Quellen
4. Markenzeichen – Evidenz 1300, Level 25, 70 Ereignisse, mindestens zwei Quellen
5. Legendenmerkmal – Evidenz 1900, Level 40, 110 Ereignisse, mindestens drei Quellen

Trait-Evidenzquellen:
- Training: 0,35
- Praxis: 1,00
- Krise: 1,25
- Teamarbeit: 1,10
- Entdeckung: 1,10
- Erfolg: 0,90
- Fehlschlag: 0,70

Fehlschläge dürfen Entwicklung auslösen, aber schwächer als echte Praxis oder Krisenbewältigung.

## Trait-Konflikte

0.4.1 verwendet bewusst keine harten Trait-Ausschlüsse.

Nur zwei Soft-Konflikte sind zunächst fachlich begründet:
- Planer ↔ Improvisierer ab Stufe 3: positive Wirkung beider Seiten × 0,85
- Detailmensch ↔ Opportunist ab Stufe 4: positive Wirkung beider Seiten × 0,90

Ein Charakter verliert dadurch keinen bereits entwickelten Trait. Positive Modifikatoren werden pro Zielwert bei +35 %, negative bei -20 % gekappt.

## Spezialisierungen

Spezialisierungen werden nicht ausgewählt, sondern aus dauerhaftem Skill-Vorsprung berechnet.

Richtungen:
- Klangarchitektur
- Einsatzleitung
- Szenenetzwerk
- Spurensuche
- Impro-Werkstatt
- Crew-Stabilität

Stufen:
1. Tendenz
2. Profil
3. Identität
4. Meisterschaft

Je höher die Spezialisierung, desto größer der XP-Bonus in Fokus-Skills und desto moderater die Abwertung außerhalb des Fokus. Generalisten bleiben ausdrücklich möglich. Details stehen in `manifests/PROGRESSION_MANIFEST.json`.

## Biografie

Nur bedeutsame validierte Journal-Ereignisse werden Biografie-Kandidaten:
- erstes Mal
- großer Erfolg/Fehlschlag
- Levelmeilenstein
- Trait/Spezialisierung
- Beziehung
- bedeutender Fund
- Event/Club
- Wirtschaft
- persönliche Mission
- seltenes Zufallsereignis

Freitext aus ungesicherten Zuständen wird vermieden. Biografie entsteht aus Textschlüsseln und validierten Ereignisdaten.

## Balance-Nachweis 0.4.1

`tools/simulate_characters/progression_simulator.py` simuliert die Progression reproduzierbar und ohne externe Bibliotheken.

Referenz:
- 1.000 Charaktere
- 720 Spieltage
- Seed 90409
- sechs Balance-Gates bestanden

Der Bericht liegt unter `reports/PROGRESSION_SIMULATION_0.4.1.json`.
