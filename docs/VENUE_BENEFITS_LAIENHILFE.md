# Venue Benefits – einfache Erklärung

Ein eigener Ort darf später einen echten Nutzen haben. Wichtig ist aber: Das Spiel darf keinen Bonus nur deshalb anzeigen, weil die Oberfläche ihn ausdenkt.

Aktuell sind zwei Dinge sicher bestätigt: **Du besitzt den Ort** und **deine Ausbauten verändern bereits fünf Ortswerte**. Diese Werte dürfen deshalb in einem Betriebsprofil verständlich angezeigt werden.

Das Betriebsprofil zeigt bei eigenen Orten jetzt alle fünf Werte mit ausgeschriebenen deutschen Bezeichnungen: **Prestige, Publikumskraft, Risiko, Underground-Faktor und Nutzen**. Es berechnet nichts neu und verändert nichts am Spielstand.

Die Eigentumsgrenze bleibt hart: Bei **nicht besessenen Orten** werden diese fünf Werte nicht als eigenes Betriebsprofil an die Property-Anzeige ausgegeben. Die vorhandenen Basiswerte bleiben intern für Karte und Bezirksdarstellung erhalten; daraus entsteht aber kein Besitz- oder Bonusversprechen.

Zusätzlich ist diese Grenze jetzt direkt abgesichert: Die Browseranzeige darf fehlende Besitzwerte nicht aus der internen Ortswert-Karte zurückholen. Für die sichtbare Zeile zählt ausschließlich `entries[*].effective_values` – fehlt dieser Besitzwert, bleibt das Betriebsprofil leer.

Der echte Chromium-Nachweis startet mit einem isolierten Spielstand, kauft über den normalen `property.purchase`-Pfad genau einen Ort und rendert danach den normalen A4-Server bei **760×680**, **Großer Schrift** und **Hohem Kontrast**. Der Test verlangt genau ein sichtbares Fünf-Werte-Profil beim eigenen Ort, kein solches Profil bei fremden Orten und keine horizontale Überbreite.

Neu prüft derselbe Browser-Nachweis nicht mehr nur die fünf Bezeichnungen: **Hinter jeder Bezeichnung muss tatsächlich ein sichtbarer numerischer Wert stehen.** Damit kann eine leere oder nur beschriftete Profilzeile nicht versehentlich als vollständig funktionierend durch die Release-Abnahme rutschen.

## Mechanik-Audit: Publikumskraft

Als erster einzelner Kandidat wurde **Publikumskraft (`audience_pull`)** gegen die bestehende Event-Abrechnung geprüft. Das Ergebnis ist aktuell **NO-GO für einen mechanischen Bonus**.

Der Grund ist einfach: Die Event-Abrechnung kennt heute Event, Geld und Charakter, aber keinen autoritativen Property-/Upgrade-State. Sie besitzt auch kein Receipt-Feld, das später eindeutig beweisen könnte, welcher Publikumskraft-Wert welchen Bonus erzeugt hat. Eine Prozentzahl einfach in den Gewinn einzurechnen wäre deshalb eine neue versteckte Regel und beim Replay fachlich nicht sauber erklärbar.

Auch Scene Jobs sind kein zulässiger Umweg: Ihr Vertrag verbietet fremd eingespeiste Payout- und Effektmodifikatoren.

Das bedeutet nicht, dass Publikumskraft dauerhaft wirkungslos bleiben muss. Vor einem späteren GO braucht genau ein Zielpfad eine eindeutige Event→Location-Zuordnung, eine begrenzte Formel, Journal-/Receipt-Evidence und denselben Effekt nach Reload/Replay.

### Schutz vor veraltetem Audit

Der Audit-Schutz merkt sich nicht nur „Property fehlt“, sondern die komplette heute gültige Abrechnungsfläche: Welche Zustände hineingehen dürfen, welche Effekte verarbeitet werden, wohin sie angewendet werden, welche Receipt-Regeln existieren und **welche Systemgrenzen ausdrücklich unverändert bleiben müssen**.

Damit zählt jetzt auch der komplette Block `scope_boundaries`. Wird dort später zum Beispiel `property_changes` freigegeben oder eine neue Venue-Grenze ergänzt, schlägt die Regression absichtlich an. Dann muss die Entscheidung neu geprüft werden, statt dass ein altes NO-GO oder ein neuer Bonus unbemerkt neben der tatsächlichen Spielregel weiterlebt.

Noch nicht erlaubt sind daher automatische Vorteile wie „mehr Events“, „billigerer Betrieb“, „mehr Kapazität“ oder „laufender Gewinn“. Für solche Wirkungen fehlt weiterhin eine eigene Spielregel, die Speichern, Wiederholen und Fehlerfälle eindeutig regelt.

## Konkrete Folgeidee: Venue→Settlement-Authority-Vertrag

Als nächste **kleine Erweiterungsidee** soll nicht sofort ein Bonus gebaut werden. Zuerst wird ein minimaler Vertrag geprüft, der genau drei Dinge autoritativ verbindet: **bestätigtes Event → eigener Ort → zum Settlement-Zeitpunkt gültige Publikumskraft**. Zusätzlich muss das Settlement-Receipt den angewandten Ortsbeitrag eindeutig belegen können.

**Nutzen:** Damit würde erstmals eine belastbare technische Brücke zwischen Besitz/Ausbau und Event-Abrechnung entstehen, ohne eine zweite Bonusengine einzuführen. **Begründung:** Erst wenn Zuordnung, Wertquelle und Evidence eindeutig sind, kann ein späterer begrenzter Publikumskraft-Effekt deterministisch, replaybar und für den Spieler nachvollziehbar umgesetzt werden.

Die Folgeidee ändert heute noch keine Balance und gibt keinen Bonus frei. Sie ist ausschließlich der kleinste mögliche Architekturbaustein für einen späteren mechanischen GO.

### Harte Grenze für diesen Folgeschritt

Der nächste Authority-Slice darf **nur den Beweisweg** festlegen: bestätigtes Event, eigener Ort, gültige Publikumskraft und Settlement-Receipt. Er darf **noch keine Bonusformel**, keinen Multiplikator, keine neue Auszahlung und keine Browser-Berechnung einführen.

Damit bleibt die Reihenfolge eindeutig: **erst Autorität und Evidence, danach separat Balance und Wirkung**. Diese Trennung verhindert, dass ein technisch noch ungeklärter Venue-Bonus schon durch einen Vertrags-Patch heimlich spielwirksam wird.

Der Schutz prüft diese Aussage jetzt nicht mehr nur gegen diese Erklärung. Er liest zusätzlich die echte Settlement-Regel, den Property-Upgrade-Vertrag und den vorhandenen Property-Renderer. Solange dort Property-Änderungen gesperrt sind, keine Publikumskraft als Settlement-Effekt katalogisiert ist und die Oberfläche nur bestätigte Werte als Text anzeigt, bleibt der Folgeschritt nachweisbar nicht-mechanisch.

### Ergebnis des Authority-Audits

Der Beweisweg ist jetzt konkret geprüft. **GO gibt es nur für eine reine Evidence-Brücke; der mechanische Bonus bleibt NO-GO.** Event, bestätigter Besitz und Ausbau besitzen bereits denselben fachlichen Schlüssel `location_id`. Deshalb darf ein nächster Implementierungsslice diese bestehenden Autoritäten verbinden, ohne einen zweiten Property-State oder eine neue Venue-Engine einzuführen.

Der aktuelle Settlement-State erlaubt allerdings keine beliebigen Zusatzfelder. Die Venue-Evidence muss deshalb als explizite, versionierte Vertragserweiterung eingeführt werden. Dabei darf sie zunächst nur `location_id`, bestätigten Besitz und den serverseitig bestätigten `audience_pull` belegen; Budget, Ruf, Stress, Heat und Stability bleiben unverändert.

Wichtig: Die Berechnung der fünf effektiven Ortswerte liegt jetzt gemeinsam in `domain.property_upgrade.effective_venue_values(...)`. Karte/Betriebsprofil und spätere Evidence-Verbraucher können damit dieselbe read-only Autorität verwenden. Unbekannte Upgrade-Level, die gar nicht zu den Slots des Orts gehören, werden nun fail-closed abgewiesen statt still ignoriert zu werden.

Zusätzlich prüft jetzt auch der echte Projection-Pfad den **ungefilterten gespeicherten Ausbauzustand**, bevor daraus nur die gültigen Slots für die Anzeige gebildet werden. Ein alter oder fremder Schlüssel wie `ghost_slot` kann damit nicht mehr still verschwinden. Für Spieler bedeutet das: Ein widersprüchlicher Spielstand wird klar abgewiesen, statt unbemerkt mit teilweise ignorierten Ausbauten weiterzulaufen.

Auch doppelt eingetragene `upgrade_slots` werden jetzt von der gemeinsamen Wertautorität abgewiesen. Damit kann ein fehlerhafter Location-Katalog denselben Ausbau nicht versehentlich zweimal auf Prestige, Publikumskraft oder andere Ortswerte anwenden.

Seit PR #273 existiert außerdem der **read-only Evidence-Resolver** `resolve_owned_venue_evidence(...)`. Er verbindet bereits bestätigten Event-Ort, Besitz und dieselbe gemeinsame Wertautorität und liefert für einen eigenen Ort eine versionierte Evidence mit `location_id`, Besitzer, `audience_pull` sowie Property- und Ausbau-Revision.

Die Evidence nennt jetzt zusätzlich die tatsächlich gelesenen **City-Map- und Property-Upgrade-Vertragsversionen**. Für Spieler ändert das keinen Wert und keinen Bonus; für spätere Wiederholungs- und Recovery-Prüfungen ist aber eindeutig erkennbar, aus welchem Datenvertrag die bestätigte Publikumskraft stammt. Fehlt eine dieser Quellversionen, wird keine scheinbar vollständige Evidence erzeugt.

Damit ist die reine Authority-Brücke **bereits vorhanden**. Noch fehlt aber der nächste klar getrennte Vertragsschritt: Diese Evidence wird derzeit **nicht im Settlement-State, Settlement-Receipt, Journal oder Save gespeichert**. Genau deshalb bleibt der mechanische Bonus weiterhin gesperrt.

### Spätere Verbesserungsidee: Manifest-Konsistenz vor dem Spielstart

Als spätere kleine Qualitätsverbesserung kann der Repository-/Startup-Check doppelte Venue-Slots bereits direkt im Location-Manifest melden. **Nutzen:** Ein Katalogfehler wird dann schon beim Prüfen der Spieldaten verständlich angezeigt und nicht erst beim Berechnen eines Ortsprofils. **Begründung:** Die Domain-Grenze muss trotzdem fail-closed bleiben; ein früher Manifest-Hinweis verbessert zusätzlich Diagnose und Wartung, ohne eine zweite Fachregel zu erzeugen.

### Spätere Verbesserungsidee: Receipt-Quellversionen sichtbar diagnostizieren

Wenn Venue-Evidence später im Settlement-Receipt gespeichert wird, kann die Diagnoseansicht die beiden Quellversionen bei Bedarf mit ausgeben. **Nutzen:** Bei alten Saves oder Migrationen ist sofort erkennbar, auf welchem Karten- und Ausbauvertrag eine bestätigte Publikumskraft beruhte. **Begründung:** Diese Information ist jetzt bereits Teil derselben Evidence und benötigt deshalb keine zweite Berechnung oder neue Autorität.

### Spätere Verbesserungsidee: sichtbarer Receipt-Hinweis

Falls der Venue→Settlement-Vertrag später wirklich GO wird, soll die vorhandene Event-Rückmeldung den angewandten Publikumskraft-Beitrag **read-only als bestätigte Ursache** anzeigen. **Nutzen:** Der Spieler sieht dann nicht nur einen veränderten Ausgang, sondern auch, welcher eigene Ort und welcher bestätigte Ortswert dazu beigetragen haben. **Begründung:** Sichtbare Ursache und gespeicherte Receipt-Evidence sollten dieselbe Wahrheit zeigen; deshalb keine neue Berechnung im Browser und keine zweite Bonuslogik nur für die Oberfläche.

## Merksatz

**Anzeigen, was bei deinem Ort bestätigt ist: ja. Einen Bonus erfinden, bevor Server, Journal und Replay dieselbe Ursache beweisen können: nein.**

Der nächste sinnvolle Gameplay-Schritt ist jetzt **nicht mehr der Resolver selbst**, sondern die minimale versionierte Aufnahme der bereits bestätigten Venue-Evidence in den Settlement-Vertrag. Erst danach folgt separat der Replay-/Recovery-Beweis; erst wenn auch dieser grün ist, darf genau ein begrenzter `audience_pull`-Effekt als eigener Folgeslice geprüft werden.
