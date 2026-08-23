# Laienhilfe – Geheimer bester Freund & persönliches Geld

## Was ist jetzt möglich?

C1 hat die Sicherheitsregeln für den Assistenten festgelegt. C2 speichert dauerhaft **Aus** oder **genau einen vorhandenen Scene Job**. C3 sorgt dafür, dass eine intern bestätigte Spielrunde den gewählten Job höchstens einmal ausführt. C4 macht diese Steuerung direkt im **JOBS-Bereich** sichtbar und bedienbar. C5A/C5B ergänzen dort kleine, ausschließlich aus bestätigter Assistentenarbeit abgeleitete Storyreaktionen – ohne Freundschaftslevel oder zweite Progressionsengine.

0.8.8-D ergänzt im selben Bereich das persönliche **Bankkonto**. Dein bereits vorhandenes Bargeld und dein Bankguthaben sind zwei Ansichten desselben `PlayerFinanceState` und werden im selben Finance-Ledger nachvollziehbar geführt.

## So benutzt du den Freund

1. Öffne den vorhandenen **JOBS-Bereich**.
2. Bei jedem Scene Job findest du zusätzlich die Assistenten-Schaltfläche.
3. Mit **FREUND STARTEN** wählst du diesen Job als automatische Aufgabe.
4. Bei einem anderen Job kannst du mit **FREUND WECHSELN** die Auswahl ändern.
5. Der aktuell gewählte Job zeigt **FREUND AKTIV**.
6. Mit **FREUND STOPPEN** stellst du den Assistenten wieder auf **Aus**.

Der Status oberhalb der Jobkarten zeigt, ob der Freund aus oder aktiv ist, welchen katalogisierten Job er gewählt hat und welche bestätigte Steuerrevision gespeichert ist.

## So benutzt du das Bankkonto

Direkt im vorhandenen JOBS-/Geldbereich gibt es den Block **Bankkonto**. Dort siehst du **Bargeld**, **Bankguthaben** und den bestätigten Finanzstand.

1. Gib einen positiven Betrag in Euro ein, zum Beispiel `25` oder `25,50`.
2. **EINZAHLEN** verschiebt diesen Betrag vom Bargeld auf die Bank.
3. **ABHEBEN** verschiebt ihn von der Bank zurück ins Bargeld.
4. Ist auf der Quellseite nicht genug Geld vorhanden, wird der Transfer vollständig abgelehnt. Es gibt keinen halben Zwischenstand.

Ein Transfer verändert immer gemeinsam Wallet, Bankguthaben, Ledger und Finance-Revision. Retry derselben technischen Command-ID kann denselben Transfer nicht doppelt buchen.

## Welche Bankdaten darf der Browser bestimmen?

Nur die **Richtung** (`deposit` oder `withdraw`) und den **positiven Betrag in Cent**. Die Runtime liest die bestätigten Geldstände selbst und berechnet daraus die Zielstände.

Der Browser darf insbesondere **nicht** liefern:

- neuen Bargeld-Endstand,
- neuen Bank-Endstand,
- Zinsen oder Zinseszinsen,
- Dividenden oder Anlagenwerte,
- irgendeinen Systemzeit-basierten Finanzfortschritt.

Damit kann eine manipulierte Oberfläche keinen Geldstand erfinden.

## Gibt es schon Zinsen?

Nein. 0.8.8-D enthält bewusst nur atomare Ein- und Auszahlungen. Zinsen folgen als eigener Slice, weil sie eine bestätigte Spielautorität für den Fortschritt brauchen. Die Rechneruhr allein darf niemals Zinsen auslösen.

## Wann erscheint eine Freundschaftsreaktion?

Der Nachhall braucht immer zwei bereits bestätigte Journal-Einträge:

- `assistant.round_processed`: Die intern bestätigte Runde wurde vom Assistenten verarbeitet.
- `finance.job_completed`: Der exakt zu dieser Runde gehörende Scene Job wurde tatsächlich dauerhaft verbucht.

Nur wenn **beide Einträge zusammenpassen**, erscheint ein kleiner Storytext. Ein normal manuell ausgeführter Job reicht nicht. Ein einzelner Rundenmarker reicht ebenfalls nicht. Eine Runde, in der der Assistent auf **Aus** stand, erzeugt keinen Freundschafts-Nachhall.

## Wo sehe ich den Nachhall?

Direkt im vorhandenen **Geheimer-bester-Freund-Bereich** oberhalb der Jobkarten. Dort steht unter **„Was dein Freund dazu sagt“** der kleine Nachhall der letzten bestätigten Assistentenarbeiten. Es gibt bewusst **kein zweites Freundschafts-Dashboard**.

Bis zu drei letzte bestätigte Einträge werden angezeigt. Jeder Eintrag zeigt einen kurzen Spruch und den zugehörigen katalogisierten Scene Job.

## Warum wechseln die Texte, aber nicht bei jedem Neuladen?

Für jeden der fünf vorhandenen Scene Jobs gibt es mehrere externe deutsche Textvarianten. Die Auswahl wird aus der bereits bestätigten Kombination aus **Character-ID + Runden-ID + Job-ID** deterministisch bestimmt.

Das heißt:

- verschiedene bestätigte Runden können unterschiedliche Sprüche bekommen,
- dieselbe bestätigte Runde zeigt nach Refresh oder Retry immer denselben Spruch,
- die Rechneruhr und Browser-Zufall bestimmen keinen Storytext,
- es entsteht kein neuer gespeicherter Freundschaftszustand.

## Startet ein Klick schon eine automatische Runde?

Nein. Die Assistenten-Schaltflächen ändern ausschließlich den vorhandenen `AssistantControlState`. Sie dürfen keine Spielrunde erfinden. Bank-Einzahlungen oder -Auszahlungen starten ebenfalls keine Runde und verändern keine Assistentenautorität.

Automatische Arbeit erfolgt weiterhin nur, wenn die Runtime einen **intern bestätigten Rundentrigger** an C3 übergibt. Browser und Rechnerzeit starten keine Runde.

## Kann ich normale Scene Jobs weiterhin selbst ausführen?

Ja. Die vorhandene normale Job-Schaltfläche bleibt unverändert. Manuelle Jobs werden ausdrücklich **nicht** als Assistenten-Freundschaftsreaktion gewertet. Joblohn landet weiterhin im persönlichen Bargeld und kann danach freiwillig auf die Bank verschoben werden.

## Was bleibt geschützt?

- eine bestätigte Assistentenrunde wird höchstens einmal verarbeitet,
- Retry zahlt Joblohn oder Banktransfer nicht doppelt,
- eine Runde im Zustand **Aus** kann später nicht rückwirkend Arbeit auslösen,
- ein späterer Jobwechsel verändert keine alte Runde,
- Banktransfer bricht bei unzureichendem Quellguthaben vor jedem Write ab,
- Systemzeit und Browser besitzen weder Runden- noch Zinsautorität.

## Was kommt danach?

Als sauberer Finance-Folgeslice bietet sich **0.8.8-D2 – bestätigte Sparzinsen** an: Zinsfortschritt nur aus einer kanonisch bestätigten Spielperiode, niemals aus Rechnerzeit allein. Alternativ bleibt **0.8.8-E – Control Deck Focus** als unabhängiger UX-Slice bereit. **C6 – Round-Authority Integration Harness** bleibt abhängig, bis ein echter kanonischer Rundenproduzent vorhanden ist.
