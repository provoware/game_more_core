# District-Chain Runtime→Browser-E2E – Laienhilfe

## Was wird hier geprüft?

Der Test erzeugt beide vorhandenen District-Micro-Stories in einem frischen, isolierten Spielstand über die echte Runtime. Danach wird derselbe Spielstand über den normalen lokalen A4-Server geöffnet und in einem echten Chromium-Browser gerendert.

Geprüft werden die vollständigen Ketten:

1. **„Das Netz flackert“** → `power_flicker_afterglow` → **„Folge von: Das Netz flackert“**
2. **„Eine Tür steht plötzlich offen“** → `temporary_space_afterimage` → **„Folge von: Eine Tür steht plötzlich offen“**

## Was bedeutet „vollständige Kette“?

Der Nachweis geht nicht nur gegen vorbereitete JSON-Beispiele. Er benutzt nacheinander:

**DistrictWorldEventService → PersistenceKernel/Journal → bestehende Timeline-Projection → `/api/state` → echtes Browser-DOM**

Damit muss dieselbe bestätigte Ursache bis zur sichtbaren Erklärung im Control Deck erhalten bleiben.

## Welche Sicherheitsgrenzen werden zusätzlich geprüft?

- Parent und Follow-up müssen im selben Bezirk liegen.
- Ein späterer Zyklus in einem anderen Bezirk darf den offenen Nachhall nicht verbrauchen.
- Ein Retry desselben bestätigten Zyklus darf keinen zweiten Child-Record schreiben.
- `causation_id` bleibt die Parent-Event-ID.
- `correlation_id` bleibt `district-chain:{parent_event_id}`.
- Es wird kein Journaleintrag direkt von Hand erzeugt.
- Es gibt keine zweite Projection und keine Test-only Browserdarstellung.

## Was verändert der Test nicht?

Der Slice verändert keine Gameplaywerte, keine District-Deltas, keine Storytexte und keine Persistenzregeln. Er fügt ausschließlich einen realen End-to-End-Nachweis für bereits vorhandenes Gameplay hinzu.

## Bekannte Grenze

Der direkte Browsernachweis dieser Iteration läuft über den vorhandenen Chromium-Release-Acceptance-Pfad. Der bestehende Desktop-Browser-E2E prüft weiterhin zusätzlich Chromium und nativen Firefox für seine bisherigen UI-Verträge. Eine Firefox-spezifische District-Chain-DOM-Prüfung ist erst sinnvoll, wenn für diese Storydarstellung ein browserabhängiger Unterschied gefunden wird.
