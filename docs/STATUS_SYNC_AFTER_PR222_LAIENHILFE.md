# Status-Sync nach PR #222 – einfach erklärt

## Was wurde gemacht?

PR #222 hat **keine neue Story 003** eingebaut. Stattdessen wurde geprüft, ob eine dritte Street-Micro-Story wirklich anders genug wäre und ohne neue versteckte Spielzustände auskommt.

Das Ergebnis: **Noch nicht.** Die zwei vorhandenen Storys unterscheiden sich bereits deutlich. `street.construction_detour` bleibt nur ein Reservekandidat.

## Warum braucht es danach einen Status-Sync?

Nach jedem fachlichen Safe Merge zeigen `TODO.md`, `FEATURE_POOL.md` und `PROJEKTSTATUS.json` zunächst noch auf den vorherigen bestätigten Stand. Das ist absichtlich so: Der Status wird nicht heimlich direkt auf `main` umgeschrieben.

Dieser kleine Folge-PR zieht deshalb ausschließlich die Projektbeschreibung auf den wirklich gemergten Stand PR #222 / `008326acc726e9be513c97682293c4a26e932c3a`.

## Was ändert sich am Spiel?

**Nichts.** Keine Spielwerte, keine Street-Gewichte, keine Saves, keine Runtime und keine Oberfläche werden in diesem Status-Slice verändert.

## Was ist jetzt als Nächstes geplant?

Als nächster fachlicher Owner ist `POOL-UX-010` gezogen. Zuerst wird nur geprüft, wie das bereits vorhandene Nächste-Aktion-Signal verständlicher durchs Spiel führen kann.

Wichtig: Die Oberfläche darf eine sinnvolle nächste Aktion **erklären oder hervorheben**, aber niemals selbst entscheiden oder eine Aktion automatisch ausführen.

## Merksatz

**Erst fachlich sicher mergen, dann Status sauber nachziehen, erst danach den nächsten Ausbau beginnen.**
