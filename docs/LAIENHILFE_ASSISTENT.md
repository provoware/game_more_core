# Laienhilfe – Geheimer bester Freund

## Was ist bereits vorbereitet?

C1 hat die Sicherheitsregeln des Assistenten festgelegt. C2 ergänzt jetzt den kleinen dauerhaften Steuerzustand: **Aus** oder **genau ein vorhandener Scene Job gewählt**.

Der Assistent führt in C2 weiterhin **noch keinen Job automatisch aus**. Der neue Zustand merkt nur deine Auswahl sicher über Speichern, Neustart und Recovery hinweg.

## Was kann C2?

- einen vorhandenen Scene Job als Assistenten-Aufgabe auswählen,
- auf einen anderen vorhandenen Scene Job wechseln,
- den Assistenten wieder auf **Aus** stellen,
- dieselbe Auswahl ohne zusätzlichen Journal-Eintrag erneut bestätigen,
- den Zustand aus bestätigten Journal-Einträgen rekonstruieren.

Es kann niemals mehr als eine ausgewählte Aufgabe gleichzeitig geben, weil der Zustand nur eine einzige `active_job_id` besitzt.

## Was darf C2 ausdrücklich nicht?

C2 löst noch keine Arbeit aus. Es verändert deshalb weder Bargeld noch Energie, Stress oder Eventbudget. Auch Rechnerzeit und Browser dürfen keine automatische Runde starten.

Erst eine spätere C3-Stufe darf eine **bestätigte Spielrunde** mit genau einer Ausführung des gewählten Scene Jobs verbinden. Dabei muss dieselbe bestätigte Runde bei Retry weiterhin gegen Doppelzahlung geschützt sein.

## Was passiert bei einem falschen Job?

Die Runtime akzeptiert ausschließlich IDs aus dem bestehenden Scene-Job-Katalog. Eine unbekannte ID oder ein falscher Character-Kontext wird vor jedem Write abgewiesen.

## Warum wird der Zustand journalisiert?

Start, Stop und Wechsel sollen nach Neustart oder Recovery nicht verloren gehen oder anders interpretiert werden. Deshalb schreibt C2 nur die bestätigte Steuerentscheidung als `assistant.control_changed` in den vorhandenen Persistence-Pfad. Es entsteht keine zweite Save- oder Assistenten-Datenbank.

## Wichtig

Deine normalen Scene Jobs funktionieren unverändert weiter. C2 verändert keine Jobwerte und startet keine Hintergrundarbeit.
