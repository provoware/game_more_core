# District-Chain Micro-Story 001 – Laienhilfe

## Was passiert jetzt?

Wenn das bestätigte District-Ereignis **„Das Netz flackert“** (`district.power_flicker`) passiert, merkt sich die Runtime genau diesen bestätigten Journal-Record als mögliche Ursache.

Die Folge wird **nicht sofort** erfunden. Erst wenn im selben Bezirk später wieder ein bestätigter District-Zyklus stattfindet, darf die Runtime den einen katalogisierten Nachhall `power_flicker_afterglow` schreiben:

**„Das Licht ist zurück – die Erinnerung bleibt.“**

Die Geschichte beschreibt, dass die Szene auf den früheren Stromaussetzer reagiert: Taschenlampen, Kabel und Wissen darüber, welcher Keller beim nächsten Flackern zuerst dunkel wird.

## Was bleibt technisch verbindlich?

- Ursache ist ausschließlich ein bereits bestätigter `world.district_effect_applied`-Record.
- Parent und Folge müssen denselben `district_id` besitzen.
- Die Folge verwendet `world.district_followup_resolved` aus Contract V1.
- `causation_id` zeigt auf die Parent-Event-ID.
- `correlation_id` bleibt `district-chain:{parent_event_id}`.
- Die Child-ID ist deterministisch und ein Retry erzeugt keinen zweiten Record.
- Die Folge verändert keine District-Werte, kein Geld, keine Energie und keine Balance.
- Browser, Timeline und Biografie erhalten weiterhin keine Gameplay-Autorität.

## Warum ist das klein gehalten?

Es ist absichtlich **nur eine** Micro-Story auf einer bestehenden Eventengine. Dadurch kann zuerst bewiesen werden, dass Ursache → späterer Nachhall → Replay sauber funktioniert, bevor weitere Geschichten in den Katalog kommen.

## Bekannte Grenze

Der Child-Record ist jetzt Runtime-Evidenz, wird aber noch nicht als eigene kausal verbundene Zeile in Timeline oder Biografie dargestellt. Diese Darstellung soll read-only auf demselben Journal basieren.

## Konkrete spätere Verbesserungsidee

Als nächster UX-Slice kann die vorhandene Timeline beim Child-Record einen kleinen Hinweis wie **„Folge von: Das Netz flackert“** aus `causation_id` und dem Parent-Record ableiten. Dafür darf kein neuer Storyzustand im Browser entstehen.
