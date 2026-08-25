# AVATAR-CONTEXT-E2E – Laienhilfe

## Was wird geprüft?

Der Release-Browser-Test öffnet BUNKERFREQUENZ in echten Browsern mit kleiner Arbeitsfläche. Für den detaillierten Identitätslauf erzeugt er **immer einen eigenen temporären Test-Spielstand**. Die Crew-Kurzmarke wird im normalen Profil-Editor auf `E2E` geändert und über den vorhandenen `PROFIL SPEICHERN`-Pfad bestätigt.

Der identische vorhandene Test-Harness läuft sowohl im Chromium-Acceptance-Pfad als auch im bereits vorhandenen nativen Firefox-/Geckodriver-Pfad. Es gibt dafür kein zweites Browserframework und keine zweite Avatar-Testlogik.

Danach muss dieselbe bestätigte Kurzmarke sichtbar bleiben in:

- der Profilvorschau,
- dem Live-HUD,
- dem eigenen Ranking-Eintrag,
- einem **wirklich von der Runtime als Eigentum bestätigten Map-Ort**.

Zusätzlich wird der bestehende Modus `Hoher Kontrast` eingeschaltet. Der Test prüft nicht nur, ob Text vorhanden ist, sondern auch, ob `crew_identity.css` im echten Browser erfolgreich geladen wurde, die Crew-Marke sichtbare Geometrie besitzt und die weiße High-Contrast-Kante tatsächlich berechnet wird.

## Wie entsteht das Eigentum im Test?

Ein normaler neuer Spielstand startet mit 1.000 EUR Eventbudget. Die günstigste aktuell katalogisierte kaufbare Immobilie kostet 31.000 EUR. Diesen Unterschied löst der Test **nicht** durch geänderte Spielregeln, billigere Immobilien oder Browser-Tricks.

Stattdessen wird ausschließlich für den isolierten temporären Acceptance-Spielstand vor dem Serverstart folgender Ablauf ausgeführt:

1. Der Test liest die kaufbaren Orte aus dem vorhandenen `CITY_MAP_MANIFEST.json` und wählt deterministisch den günstigsten Eintrag.
2. Nur die **im Speicher liegende Kopie** des Starter-Events erhält für diesen Test exakt das dafür erforderliche Budget. `web/a4/starter.json` und alle Gameplaywerte im Repository bleiben unverändert.
3. Der normale Runtime-Bootstrap legt den temporären Spielstand an.
4. Danach wird über denselben kanonischen Command `property.purchase` gekauft, den auch das Spiel verwendet. Der Test liefert ausschließlich `location_id`; Kaufpreis, Eigentümer und Budgetdelta bleiben Autorität der bestehenden Property-/Economy-Runtime.
5. Erst danach startet der Browser. Die Klasse `.map-marker.owned` muss nun aus der bestätigten Projection entstehen. Fehlt sie, wird der Browsernachweis rot.

Damit prüft der Avatar-E2E nicht mehr nur einen nachgebauten Presentation-Zustand, sondern die reale Kette **Runtime-Kauf → persistierter Besitz → Projection → Map-Marker → Crew-Marke**.

## Was wurde gegenüber dem alten Map-Fixture verbessert?

Früher durfte der Browser für den reinen Darstellungsnachweis kurz selbst ein Element mit der Klasse `.owned` einfügen. Das war klar als Presentation-Fixture begrenzt, konnte aber nicht beweisen, dass die Map-Crew-Marke auch an einem tatsächlich bestätigten Eigentumszustand erscheint.

Diese künstliche Besitzmarkierung ist entfernt. Der Browser-Harness:

- erzeugt keinen `.owned`-Marker mehr,
- setzt keinen Eigentümer,
- setzt keinen Kaufpreis,
- sendet keinen Property-Command,
- wartet ausschließlich auf den von der echten Projection erzeugten Eigentumsmarker.

Ist beim Browserstart noch der First-Run-Bildschirm sichtbar, gilt das ebenfalls als Fehler: Dann wurde das Runtime-Fixture nicht korrekt vorbereitet.

## Was beweist Firefox zusätzlich?

Der Firefox-Release-Pfad startet weiterhin seinen eigenen paketierten Server mit eigenem temporären Save-Verzeichnis. Vor diesem Serverstart ruft er jedoch die **im selben Release-Candidate enthaltene** Acceptance-Routine zur Vorbereitung des Runtime-Owned-Fixtures auf. Damit testen Chromium und Firefox denselben Property-Vertrag, ohne Source- und Paketcode zu vermischen.

Firefox muss anschließend denselben ausgeführten `AVATAR_CONTEXT_E2E: PASS` liefern wie Chromium. Damit sind im zweiten Browser weiterhin abgesichert:

- Profiländerung über die echte Oberfläche,
- bestätigte Crew-Marke im HUD,
- eigener Ranking-Eintrag,
- Runtime-bestätigter Map-Besitz,
- Hoher Kontrast,
- kleines Fenster.

Ein bloß geladener Scripttext reicht nicht: Erst der tatsächlich ausgeführte PASS beendet den Firefox-Slice erfolgreich. Meldet der Harness `FAIL`, wird der Release-Browser-Nachweis sofort rot.

## Micro-Polish: Warum wurde die Ranking-Kurzmarke leicht vergrößert?

Der gezielte visuelle Audit fand genau eine reproduzierbare Größenabweichung: Die kurze Crew-Kennung im eigenen Ranking-Eintrag war mit `0.30rem` kleiner als die bereits für kompakte HUD-/Map-Kontexte verwendete Untergrenze von `0.34rem`.

Darum wurde **nur** diese eine Schriftgröße auf `0.34rem` angehoben. Das verändert weder den Ranking-Eintrag noch die Crew-Identität selbst. Es sorgt lediglich dafür, dass dieselbe kurze Kennung in den kleinen bestätigten Kontexten nicht unnötig unterschiedlich klein dargestellt wird.

Eine direkte Presentation-Regression schützt diese Untergrenze. High Contrast, Reduced Motion, Profilvorschau, HUD, Map-Klon, Ranking-Datenquelle und alle Runtime-Verträge bleiben unverändert.

## Wie wird die echte Browser-Schriftgröße geprüft?

Die statische CSS-Regel allein reicht nicht aus: Media Queries oder später spezifischere Selektoren könnten den Wert im echten Browser überschreiben. Deshalb liest derselbe bereits vorhandene Avatar-Context-Harness jetzt zusätzlich die **berechnete `font-size`** der bestätigten Kurzmarken in HUD, Map und Ranking aus.

Die Untergrenze bleibt `0.34rem`. Der Test rechnet diesen Wert nicht in eine fest verdrahtete Pixelzahl um, sondern liest zuerst die tatsächlich berechnete Root-Schriftgröße des Dokuments und bildet daraus den wirksamen Grenzwert. Dadurch bleibt die Prüfung korrekt, selbst wenn Browser oder spätere UI-Regeln die Root-Schriftgröße verändern.

Für jeden kompakten Kontext gilt:

- HUD-Kurzmarke muss mindestens `0.34rem` wirksam berechnen,
- Ranking-Kurzmarke muss mindestens `0.34rem` wirksam berechnen,
- Map-Kurzmarke muss mindestens `0.34rem` wirksam berechnen.

Ist ein Wert nicht messbar oder kleiner, meldet der Harness `AVATAR_CONTEXT_E2E: FAIL` und der bestehende Browser-/Release-Nachweis wird rot. Profil bleibt bewusst außerhalb dieser kompakten Untergrenze, weil dort ein anderer, größerer Darstellungskontext gilt.

## Schutz echter Spielstände

Wird `start_a4_acceptance.py` mit `--address` gegen eine bereits laufende Session verwendet, läuft **nur der read-only Browsercheck**. In diesem Modus wird kein Testspielstand vorbereitet, kein Eigentum gekauft, kein Profilfeld verändert und kein Testcharakter angelegt.

Der schreibende Identitätslauf ist ausschließlich an intern erzeugte temporäre Save-Verzeichnisse gebunden. Auch der Firefox-Release-Pfad arbeitet nur in seinem entpackten temporären Release- und Save-Kontext. Die temporäre HTML-Testseite wird im `finally`-Pfad wieder gelöscht.

## Sicherheitsgrenzen

- kein direkter `/api/command`-Aufruf aus dem Browser-Harness,
- kein DOM-erfundenes Eigentum,
- kein künstlich vom Client vorgegebener Kaufpreis oder Eigentümer,
- keine Änderung an `starter.json`, Property-Preisen oder Gameplaywerten,
- keine Änderung an echten oder per `--address` übergebenen Spielständen,
- keine Änderung an Journal-, Save- oder Property-Verträgen,
- keine neue Avatar-, Map-, Property- oder Ranking-Datenquelle,
- Chromium und Firefox verwenden denselben vorhandenen Avatar-Context-Harness und denselben Runtime-Fixture-Vertrag,
- fehlender echter `.map-marker.owned` blockiert den Avatar-E2E,
- fehlender `AVATAR_CONTEXT_E2E: PASS` blockiert den detaillierten Browser-Acceptance-Test,
- fehlendes oder wirkungsloses `crew_identity.css` blockiert den visuellen PASS ebenfalls,
- eine berechnete kompakte Kurzmarke unter `0.34rem` blockiert den visuellen PASS.

## Spätere sinnvolle Erweiterung

**AVATAR-CONTEXT-TEXT-CLIP-E2E:** Der bestehende Harness kann später zusätzlich prüfen, ob die vollständig gerenderte Kurzmarke in HUD, Map und Ranking innerhalb ihres sichtbaren Containers bleibt, indem `scrollWidth/scrollHeight` gegen die reale Content-Box und Overflow-Regeln abgeglichen werden. Nutzen: Eine ausreichend große Schrift könnte durch spätere Padding-, Width- oder Overflow-Änderungen trotzdem abgeschnitten werden. Begründung: Dieser Nachweis ergänzt die jetzt reale Größenprüfung, ohne neue UI- oder Identity-Architektur einzuführen.
