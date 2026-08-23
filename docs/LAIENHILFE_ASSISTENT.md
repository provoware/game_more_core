# Laienhilfe – Geheimer bester Freund

## Was ist jetzt möglich?

C1 hat die Sicherheitsregeln festgelegt. C2 speichert dauerhaft **Aus** oder **genau einen vorhandenen Scene Job**. C3 sorgt dafür, dass eine intern bestätigte Spielrunde den gewählten Job höchstens einmal ausführt. C4 macht diese vorhandene Steuerung jetzt direkt im **JOBS-Bereich** sichtbar und bedienbar.

Es gibt bewusst kein zweites Assistenten-Dashboard. Der Freund sitzt dort, wo auch die normalen Scene Jobs stehen.

## So benutzt du den Freund

1. Öffne den vorhandenen **JOBS-Bereich**.
2. Bei jedem Scene Job findest du zusätzlich die Assistenten-Schaltfläche.
3. Mit **FREUND STARTEN** wählst du diesen Job als automatische Aufgabe.
4. Bei einem anderen Job kannst du mit **FREUND WECHSELN** die Auswahl ändern.
5. Der aktuell gewählte Job zeigt **FREUND AKTIV**.
6. Mit **FREUND STOPPEN** stellst du den Assistenten wieder auf **Aus**.

Der Status oberhalb der Jobkarten zeigt, ob der Freund aus oder aktiv ist, welchen katalogisierten Job er gewählt hat und welche bestätigte Steuerrevision gespeichert ist.

## Startet der Klick schon eine automatische Runde?

Nein. Die Schaltflächen ändern ausschließlich den bereits vorhandenen `AssistantControlState`. Sie dürfen keine Spielrunde erfinden.

Automatische Arbeit erfolgt weiterhin nur, wenn die Runtime einen **intern bestätigten Rundentrigger** an C3 übergibt. Browser und Rechnerzeit starten keine Runde.

## Welche Daten darf der Browser senden?

Bei der Assistentensteuerung nur die technische Command-ID und:

- eine vorhandene `job_id`, wenn der Freund gestartet oder gewechselt wird,
- `null`, wenn der Freund gestoppt wird.

Lohn, Energie, Stress, Jobfolgen und Rundentrigger kommen nicht aus dem Browser. Zusätzliche Fachwerte werden nicht als Autorität akzeptiert.

## Kann ich normale Scene Jobs weiterhin selbst ausführen?

Ja. Die vorhandene normale Job-Schaltfläche bleibt unverändert. C4 ergänzt nur die Assistentensteuerung daneben.

## Was passiert nach Neustart oder Recovery?

Die Anzeige wird wieder aus dem bestätigten `AssistantControlState` aufgebaut. Die Oberfläche erfindet keinen eigenen Zustand. Verweist ein beschädigter oder veralteter Save auf eine Job-ID, die nicht mehr im kanonischen Scene-Job-Katalog existiert, bricht die Projektion fail-closed ab, statt einen Ersatzjob zu erfinden.

## Was bleibt durch C3 geschützt?

Auch nach der neuen Bedienung gilt unverändert:

- eine bestätigte Runde wird höchstens einmal verarbeitet,
- Retry zahlt nicht doppelt,
- eine Runde im Zustand **Aus** kann später nicht rückwirkend Arbeit auslösen,
- ein späterer Jobwechsel verändert keine alte Runde,
- Systemzeit und Browser besitzen keine Rundenautorität.

## Was kommt danach?

C5 kann ausschließlich tatsächlich bestätigte Assistentenaktionen für kleine erzählerische Freundschaftsreaktionen verwenden. Eine eigene Freundschafts-Progressionsengine ist dafür nicht vorgesehen. Das spätere C6-End-to-End-Harness bleibt abhängig von einem echten kanonischen Rundenproduzenten.
