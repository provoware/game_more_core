# Eigene Veranstaltungsorte und ihre Nachweise

Bei eigenen Orten zeigt das Betriebsprofil fünf bestätigte Werte: **Prestige, Publikumskraft, Risiko, Underground-Faktor und Nutzen**. Ausbauten verändern diese Ortswerte. Die Anzeige berechnet keine eigenen Boni.

Bei fremden oder nicht gekauften Orten erscheint kein eigenes Betriebsprofil. Fehlende Besitzwerte werden nicht aus internen Kartenwerten ergänzt.

## Was du nach der Event-Abrechnung siehst

1. Schließe dein Event regulär bis zur Abrechnungsphase ab.
2. Wähle **SETTLEMENT ABSCHLIESSEN**.
3. Unter **Abrechnung** erscheint bei einem eigenen Event-Ort der bestätigte Veranstaltungsort mit seiner **Publikumskraft bei der Abrechnung**, beispielsweise `94/100`.

Der Ortsnachweis wird zusammen mit der Abrechnung gespeichert. **Er erzeugt keinen zusätzlichen Gewinn oder Bonus.** Budget, Ruf und Stress folgen weiterhin den bestehenden Event-Regeln. Ein späterer Ausbau ändert den bereits gespeicherten Nachweis nicht.

Wurde für das Event kein eigener Ort bestätigt, steht dort **„Kein eigener Veranstaltungsort für diese Abrechnung nachgewiesen“**. Das ist eine gültige Abrechnung ohne Ortsnachweis; es werden keine Besitzwerte erfunden.

Bei einer alten Abrechnung liest du **„Ältere Abrechnung: Damals wurde noch kein Ortsnachweis gespeichert“**. Dein bestehendes Event-Ergebnis bleibt erhalten. Es wird kein nachträglicher Ortswert aus deinen heutigen Ausbauten eingesetzt.

## Speichern, Wiederholen und Wiederherstellen

Seit PR #273 existiert der read-only Resolver `resolve_owned_venue_evidence(...)`. Die neue lokale Entwicklungsstufe verbindet ihn nun mit dem bestehenden Abrechnungspfad: **bestätigtes Event → eigener Ort → zum Settlement-Zeitpunkt gültige Publikumskraft**.

Die Abrechnung speichert Besitzer, Orts-ID, Publikumskraft, Besitz-/Ausbaurevisionen und die verwendeten Karten-/Ausbauvertragsversionen. Der Vertrag `0.8.8-venue-evidence-v1` enthält dafür ausdrücklich `venue_evidence`; ältere Abrechnungen mit `0.8.3-c1` bleiben ohne dieses Feld lesbar.

Ein wiederholter identischer Abschluss zahlt nichts doppelt aus. Nach einer unterbrochenen Speicherung verwendet die Wiederherstellung denselben bereits im Journal bestätigten Nachweis. Sie berechnet historische Publikumskraft nicht aus heutigen Katalogwerten neu.

## Wenn Ortsdaten nicht geprüft werden können

Ein fehlender eigener Ortsbezug ergibt eine Abrechnung ohne Ortsnachweis. Widersprüchliche Daten bei einem eigenen Event-Ort brechen dagegen die Prüfung ab: Es entsteht keine teilweise gespeicherte Abrechnung. Die bestehende Fehlerrückmeldung nennt die Ursache. Prüfe in diesem Fall die Meldung und verwende den vorgesehenen Wiederherstellungsweg, statt Spielstandsdateien manuell zu ändern.

Mitgelieferte Besitzer- oder Publikumskraftangaben ersetzen keine bestätigten Serverdaten. Die Oberfläche liest lediglich den gespeicherten Nachweis und gibt Ortsnamen sicher als Text aus.

## Warum Publikumskraft noch keinen Bonus gibt

Die technischen Nachweise sind jetzt vorhanden. **Eine mechanische Wirkung bleibt NO-GO**, solange eine begrenzte, deterministische Formel samt Balance-Abnahme fehlt. Auch Scene Jobs sind kein Umweg für zusätzliche Auszahlungen.

Die Schutztests unterscheiden deshalb die erlaubte Receipt-Evidence von weiterhin gesperrten neuen Effekten. Keine generische Venue-Bonusengine und keine neue Berechnung im Browser werden eingeführt.

## Vergleich: Publikumskraft damals und heute

Unter der gespeicherten Publikumskraft der Abrechnung steht jetzt getrennt **„Heutige Publikumskraft“**. Beispiel: Beim Abschluss war die Bühne auf Stufe 2 und die Publikumskraft betrug **94/100**. Nach dem späteren Ausbau auf Stufe 3 zeigt die aktuelle Zeile **99/100**; der alte Nachweis bleibt bei **94/100**.

Der aktuelle Wert kommt vom bestätigten Besitz- und Ausbauzustand desselben Orts. Fehlt diese Quelle oder gehört der Ort inzwischen einem anderen Charakter, erscheint „nicht verfügbar“. Eine alte Abrechnung ohne historischen Nachweis erhält auch nach heutigen Ausbauten keinen erfundenen damaligen Wert.

## Geprüfte Idee: begrenzter zusätzlicher Ruf

Ein Audit hat einen möglichen Zusatz von höchstens **2 Ruf und höchstens 25 % eines bereits positiven Event-Rufgewinns** geprüft. Bei Verlust, keinem Rufgewinn oder einem fremden Ort wäre der Zusatz null. **Diese Idee ist nicht aktiviert.** Geld, Ruf und andere Ressourcen ändern sich dadurch heute nicht. Vor einer Einführung fehlen der gesonderte Wirkungsvertrag und ein Spieltest mit wiederholten Events.

## Spätere Verbesserungsidee: Herkunft eines alten Nachweises erklären

Eine ausklappbare Diagnose könnte die bereits gespeicherten Besitz-/Ausbaurevisionen und Datenvertragsversionen anzeigen. **Nutzen:** Bei Rückfragen zu alten Abrechnungen ist die damalige Datenbasis erkennbar. **Begründung:** Diese Herkunft ist bereits gespeichert; sie lässt sich read-only erklären, ohne den historischen Nachweis umzuschreiben oder eine zweite Bonusengine zu erzeugen.
