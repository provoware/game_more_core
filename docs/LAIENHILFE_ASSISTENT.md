# Laienhilfe – Geheimer bester Freund

## Was ist bereits vorbereitet?

C1 hat die Sicherheitsregeln festgelegt. C2 speichert dauerhaft **Aus** oder **genau einen vorhandenen Scene Job**. C3 verbindet diese Auswahl jetzt mit einer **intern bestätigten Spielrunde**.

Das bedeutet: Ist der Freund eingeschaltet, arbeitet er pro bestätigter Runde genau einmal den zu diesem Zeitpunkt gewählten Scene Job ab. Die eigentliche Auszahlung sowie Energie- und Stressfolge kommen weiterhin ausschließlich aus dem vorhandenen Scene-Job-Katalog.

## Was kann C3?

- eine bestätigte Runde genau einmal verarbeiten,
- den aktuell gewählten Scene Job über den bestehenden `SceneJobService` ausführen,
- denselben Rundentrigger bei Retry erkennen, ohne erneut zu zahlen,
- eine Runde auch dann als verarbeitet merken, wenn der Freund auf **Aus** steht,
- nach einem Absturz erkennen, wenn der Job schon verbucht wurde, aber der Rundenmarker noch fehlte,
- einen späteren Jobwechsel davon abhalten, eine alte Runde rückwirkend anders auszuführen.

## Warum gibt es einen Rundenmarker?

Nach jeder verarbeiteten Runde wird `assistant.round_processed` journalisiert. Dieser Marker ist kein zweites Rundensystem. Er beantwortet nur eine Sicherheitsfrage: **Hat der Assistent diese bereits bestätigte Runde schon verarbeitet?**

Ohne diesen Marker könnte ein Retry problematisch werden: Die Runde könnte zuerst im Zustand **Aus** eintreffen, später wird ein Job gewählt und derselbe alte Trigger nochmals zugestellt. C3 verhindert, dass daraus nachträglich eine Auszahlung entsteht.

## Was passiert bei einem Absturz zwischen Job und Marker?

Der Job selbst besitzt bereits einen stabilen Retry-Schutz. C3 verwendet für jede Character-/Runden-Kombination dieselbe technische Child-Command-ID.

Falls der Job schon dauerhaft im Journal steht, der `assistant.round_processed`-Marker aber noch fehlt, übernimmt C3 beim Retry die **ursprünglich verbuchte Job-ID**. Der Job wird nicht ein zweites Mal bezahlt; danach wird nur noch der fehlende Rundenmarker ergänzt.

## Wer darf eine Runde bestätigen?

Nicht der Browser und nicht die Rechneruhr. C3 stellt bewusst **keinen neuen Browser-Command** für die Rundenautorität bereit und verwendet keine Systemzeit als Trigger. Der Service erwartet einen bereits intern bestätigten Rundentrigger mit stabiler `round_id` und passender `character_id`.

## Was bleibt unverändert?

Start, Wechsel und Stop des Freundes bleiben der C2-Steuerzustand `assistant.control_changed`. Scene Jobs bleiben die einzige Quelle für Jobwerte. Persönliches Bargeld bleibt vom Eventbudget getrennt.

## Was kommt erst später?

C4 bringt Auswahl, Wechsel, Stop und Status kompakt in den vorhandenen JOBS-Bereich. C5 kann bestätigte Assistentenaktionen später erzählerisch nachhallen lassen. C3 baut weder ein zweites Dashboard noch eine neue Freundschafts-Progressionsengine.
