# Laienhilfe – District-Event: passiert, wiederholt oder gar nicht ausgelöst?

Bei Bezirksereignissen gibt es drei Fälle, die technisch ähnlich aussehen können, aber etwas völlig anderes bedeuten:

1. **Neu angewendet** – Ein bestätigtes District-Event wurde ausgewählt, seine katalogisierten Effekte wurden genau einmal gespeichert und ein Journal-Eintrag entstand.
2. **Sichere Wiederholung (Replay)** – Derselbe bereits bestätigte Trigger wird erneut angefragt. Das Spiel verwendet exakt dieselbe Event-Instanz, schreibt nichts ein zweites Mal und würfelt auch mit einem anderen Seed nicht neu.
3. **Kein Event** – Zum Beispiel wegen aktivem Cooldown oder fehlender bestätigter Spielweltzeit. Dann wird kein Event erfunden, kein District-Wert verändert und kein Journal-Eintrag geschrieben.

## Woran erkennt das System die Fälle?

Der vorhandene Rückgabevertrag liefert bereits getrennte Signale:

- `triggered`: Wurde ein District-Event für diesen Trigger bestätigt?
- `no_event_reason`: Warum wurde bewusst kein Event ausgelöst?
- `district_result.applied`: Gehört die angefragte Quelle zum bestätigten District-Zustand?
- `district_result.idempotent_replay`: War diese Wirkung bereits vorhanden und wurde deshalb nur sicher wiederverwendet?
- `district_result.committed_event_ids`: Welche Journal-Ereignisse wurden **in genau diesem Aufruf neu** geschrieben?

Der neue QA-Test hält diese Kombinationen ausdrücklich fest. Dadurch kann eine spätere Änderung nicht versehentlich einen Replay wie einen neuen Write oder ein blockiertes Event wie einen bestätigten Trigger aussehen lassen.

## Wichtig

Diese Iteration ändert **keine** District-Werte, Wahrscheinlichkeiten, Cooldowns, Seeds oder Journalregeln. Sie macht ausschließlich den bestehenden Receipt-Vertrag überprüfbar und regressionssicher.

## Spätere sinnvolle Erweiterung

Falls diese Receipts künftig im Control Deck sichtbar werden, sollte die UI dieselben drei Zustände in Klartext darstellen (`NEU BESTÄTIGT`, `BEREITS BESTÄTIGT`, `NICHT AUSGELÖST`) und niemals aus fehlenden Daten selbst einen Zustand erraten.
