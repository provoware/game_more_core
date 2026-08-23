# Laienhilfe – Geheimer bester Freund

## Was ist jetzt möglich?

C1 hat die Sicherheitsregeln festgelegt. C2 speichert dauerhaft **Aus** oder **genau einen vorhandenen Scene Job**. C3 sorgt dafür, dass eine intern bestätigte Spielrunde den gewählten Job höchstens einmal ausführt. C4 macht diese vorhandene Steuerung direkt im **JOBS-Bereich** sichtbar und bedienbar.

C5A ergänzt nun die sichere Grundlage für kleine erzählerische Reaktionen. Wichtig: Es entsteht dadurch **kein Freundschaftslevel, keine XP-Leiste und keine zweite Progressionsengine**.

## So benutzt du den Freund

1. Öffne den vorhandenen **JOBS-Bereich**.
2. Bei jedem Scene Job findest du zusätzlich die Assistenten-Schaltfläche.
3. Mit **FREUND STARTEN** wählst du diesen Job als automatische Aufgabe.
4. Bei einem anderen Job kannst du mit **FREUND WECHSELN** die Auswahl ändern.
5. Der aktuell gewählte Job zeigt **FREUND AKTIV**.
6. Mit **FREUND STOPPEN** stellst du den Assistenten wieder auf **Aus**.

Der Status oberhalb der Jobkarten zeigt, ob der Freund aus oder aktiv ist, welchen katalogisierten Job er gewählt hat und welche bestätigte Steuerrevision gespeichert ist.

## Wann darf künftig eine Freundschaftsreaktion erscheinen?

C5A prüft dafür zwei bereits bestätigte Journal-Einträge gemeinsam:

- `assistant.round_processed`: Die intern bestätigte Runde wurde vom Assistenten verarbeitet.
- `finance.job_completed`: Der exakt zu dieser Runde gehörende Scene Job wurde tatsächlich dauerhaft verbucht.

Nur wenn **beide Einträge zusammenpassen**, entsteht ein kleiner Nachhall-Eintrag. Ein normal manuell ausgeführter Job reicht nicht. Ein einzelner Rundenmarker reicht ebenfalls nicht. Eine Runde, in der der Assistent auf **Aus** stand, erzeugt keinen Freundschafts-Nachhall.

Damit kann die spätere Anzeige nicht einfach aus einer Browseraktion oder aus einem halben Zwischenzustand eine Geschichte erfinden.

## Was zeigt C5A bereits?

Technisch kann die neue read-only Projektion bis zu drei letzte bestätigte Nachhall-Einträge aufbauen. Für jeden der fünf vorhandenen Scene Jobs gibt es einen kleinen externen deutschen Text. Die Texte liegen außerhalb der Spiellogik.

C5A selbst hängt diese Texte **noch nicht sichtbar** in die Oberfläche ein. Das ist bewusst der nächste kleine Slice C5B. Dadurch bleibt dieser Schritt leicht prüfbar und die Herkunft der Storydaten ist zuerst abgesichert.

## Startet ein Klick schon eine automatische Runde?

Nein. Die Schaltflächen ändern ausschließlich den bereits vorhandenen `AssistantControlState`. Sie dürfen keine Spielrunde erfinden.

Automatische Arbeit erfolgt weiterhin nur, wenn die Runtime einen **intern bestätigten Rundentrigger** an C3 übergibt. Browser und Rechnerzeit starten keine Runde.

## Welche Daten darf der Browser senden?

Bei der Assistentensteuerung nur die technische Command-ID und:

- eine vorhandene `job_id`, wenn der Freund gestartet oder gewechselt wird,
- `null`, wenn der Freund gestoppt wird.

Lohn, Energie, Stress, Jobfolgen, Rundentrigger und Freundschaftsreaktionen kommen nicht aus dem Browser.

## Kann ich normale Scene Jobs weiterhin selbst ausführen?

Ja. Die vorhandene normale Job-Schaltfläche bleibt unverändert. Manuelle Jobs werden außerdem ausdrücklich **nicht** als Assistenten-Freundschaftsreaktion gewertet.

## Was bleibt durch C3 geschützt?

- eine bestätigte Runde wird höchstens einmal verarbeitet,
- Retry zahlt nicht doppelt,
- eine Runde im Zustand **Aus** kann später nicht rückwirkend Arbeit auslösen,
- ein späterer Jobwechsel verändert keine alte Runde,
- Systemzeit und Browser besitzen keine Rundenautorität.

## Was kommt danach?

**C5B** kann die bereits abgesicherte Projektion kompakt im vorhandenen JOBS-Assistentenblock anzeigen, ohne ein zweites Dashboard zu bauen. **C6** bleibt abhängig von einem echten kanonischen Rundenproduzenten und soll später den kompletten Pfad Runde → Assistent → Scene Job → Journal → Recovery → Retry end-to-end prüfen.
