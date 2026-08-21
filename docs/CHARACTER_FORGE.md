# Character Forge 0.4

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

## XP-Grundformel

```text
Skill-XP =
Basis-XP
× Schwierigkeit
× Qualität
× Neuheit
× Praxisfaktor
× Erschöpfungsfaktor
× Wiederholungsfaktor
```

Grundbereiche:
- Basis-XP: 4–40
- Schwierigkeit: 0,80–1,50
- Qualität: 0,75–1,35
- Neuheit: 0,55–1,15
- Praxis: 0,90–1,25
- Erschöpfung: 0,60–1,00
- Wiederholung: 0,40–1,00

Trainingswirkung pro Tag als Ausgangspunkt: 100 %, 85 %, 65 %, danach 40 %.

## Gesamtlevel

Ausgangsformel:

```text
Gesamt-XP(L) = 120 × (L - 1)^1,62 + 80 × (L - 1)
```

Nach Level 50 beginnt ein offenes Resonanzsystem.

## Traits

Es existieren 15 gemeinsame Effektvorlagen und 165 individuelle Trait-Namen. Alle Traits starten gesperrt.

Trait-Stufen:
1. Neigung
2. Gewohnheit
3. Charakterzug
4. Markenzeichen
5. Legendenmerkmal

Numerische Effekte und exakte Unlock-Schwellen gehören bewusst in Iteration 0.4.1 und werden nicht vorzeitig erfunden.

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
