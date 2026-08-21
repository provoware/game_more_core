# Gameplay Action Contract 0.4.4

## Zweck
0.4.4 verbindet die bereits definierte Progressionsmathematik erstmals verbindlich mit konkretem Gameplay. Jede Aktion ist datengetrieben und beschreibt Voraussetzungen, Zeit, Kosten, Risiko, Skill-XP-Gewichte, Trait-Evidenz, Journalereignisse, Undo-Regel und Biografie-Relevanz.

## Resolver-Pipeline
`VORAUSSETZUNGEN → KOSTEN RESERVIEREN → DETERMINISTISCHES ERGEBNIS → SKILL-XP → TRAIT-EVIDENZ → JOURNAL-BUNDLE → PERSISTENZ-COMMIT → BIOGRAFIE-KANDIDAT → UI-FEEDBACK`

Keine UI darf Werte direkt verändern.

## 20 Startaktionen
1. Training
2. Soundcheck
3. Location erkunden
4. Equipment kaufen
5. Location ausbauen
6. Artist/DJ buchen
7. Event vorbereiten
8. Event durchführen
9. Eventkrise lösen
10. Technik reparieren
11. Szene-Networking
12. Location recherchieren
13. Transport/Logistik
14. Club planen
15. Club betreiben
16. Clubanteile handeln
17. Crew-Konflikt lösen
18. Event abbauen
19. Dekoration bauen
20. Musikprogramm gestalten

## Skill-XP
Jede Aktion verteilt exakt 100 % ihres Skill-XP-Pools auf passende Kernskills. Beispiel Soundcheck: Technik 35 %, Musik 25 %, Konzentration 20 %, Risikoeinschätzung 10 %, Improvisation 10 %. Die eigentliche XP-Menge verwendet weiterhin den Progression-Vertrag; 0.4.4 definiert nur die fachliche Verteilung.

## Trait-Evidenz
Auch Trait-Evidenz summiert sich je Aktion auf 100 %. Training wird anschließend weiterhin mit dem bestehenden Faktor 0,35 gedämpft. Krisenaktionen liefern dagegen stärkere passende Verhaltensbelege.

## Zufall
Zufall ist reproduzierbar. Seed-Bestandteile: `world_seed + action_instance_id + server_sequence (online)`. Die lokale Systemzeit ist **kein** Zufallsseed. Gleiche Eingaben erzeugen damit bei Tests dasselbe Ergebnis.

## Ergebnisstufen
- Failed: XP ×0,70
- Partial: XP ×0,90
- Success: XP ×1,00
- Excellent: XP ×1,15
- Legendary: XP ×1,25

## Undo
Planungs- und Profilaktionen können reversibel sein. Verbrauchte Materialien, abgeschlossene Events, bestätigte Entdeckungen oder serverbestätigte gemeinsame Markttransaktionen werden nicht durch Datenlöschung rückgängig gemacht.

## Biografie
Jede Aktion trägt eine Grundrelevanz 0–100. Ereignisse ab den bestehenden Biografie-Schwellen können bei außergewöhnlichem Ergebnis, Erstmaligkeit oder Storybezug als Eintrag übernommen werden.

## Reale Orte
Erkundung und Recherche dürfen reale Bezüge verwenden, liefern aber keine Anleitung für unerlaubtes Betreten. Reale Location-Aktionen verlangen im Datenvertrag legalen/autorisierten Zugang oder eine klar fiktionalisierte Spielabbildung.

## Erweiterbarkeit
Neue Aktion = neuer Datensatz im Action Manifest. Kein neuer UI- oder Character-Sondercode, solange die vorhandenen Resolverbausteine ausreichen.
