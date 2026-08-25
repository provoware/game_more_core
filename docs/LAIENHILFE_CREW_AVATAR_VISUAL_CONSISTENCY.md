# Laienhilfe – Crew-Avatar überall eindeutig erkennen

Die Crew-Marke zeigt an mehreren Stellen dieselbe **bereits bestätigte** Identität: im Profil, oben im HUD, an eigenen Orten auf der Karte und beim eigenen Hall-/Ranking-Eintrag.

## Was wurde verbessert?

Im Modus **Hoher Kontrast** besitzen diese Avatar-Flächen jetzt dieselbe klare Außenkante: weißer Rand, schwarze Trennkante und anschließend die bestätigte Crew-Akzentfarbe. Symbol und Kurzmarke bleiben zusätzlich mit Weiß/Schwarz abgegrenzt.

Dadurch ist leichter erkennbar, dass die kleinen Marken in HUD, Karte und Ranking zur gleichen Crew gehören wie die große Profilvorschau.

## Was ändert sich nicht?

- keine Crew-Daten werden neu erzeugt,
- keine Avatar-Datei wird geladen,
- Karte und Ranking erhalten keine eigene Identitätsquelle,
- Gameplay, Werte, Saves und Journal bleiben unverändert,
- `Reduced Motion` schaltet Bewegungen weiterhin ab, ohne Identitätsinformation zu entfernen.

Die Kartenmarke verwendet weiterhin die bereits bestätigte HUD-Marke. Deshalb gilt derselbe Kontrastschutz automatisch auch dort.

## Spätere sinnvolle Prüfung

Als nächster QA-Schritt ist ein echter Browser-Durchlauf sinnvoll: Profil ändern und bestätigen, danach dieselbe Marke nacheinander in HUD, Karte und Ranking prüfen – zusätzlich bei kleinem Fenster und Hohem Kontrast. Dabei soll keine neue Fachlogik entstehen; der Test beweist nur den vorhandenen Datenweg.
