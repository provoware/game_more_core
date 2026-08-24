# Laienhilfe – Receipt-Klartext im Control Deck

Nach einer bestätigten Abrechnung kann die Runtime zusätzlich versuchen, ein Bezirksereignis auszulösen. Das Control Deck zeigt jetzt verständlich, was dabei tatsächlich passiert ist.

- **NEU BESTÄTIGT** – Für diese Abrechnung wurde erstmals ein Bezirksereignis bestätigt.
- **BEREITS BESTÄTIGT** – Derselbe bestätigte Vorgang wurde erneut angefragt. Die Runtime erkennt den Replay und wendet nichts doppelt an.
- **NICHT AUSGELÖST** – Die Runtime hat bewusst kein Bezirksereignis ausgelöst. Das Control Deck erfindet dafür weder eine Eventinstanz noch einen Journal-Eintrag.

## Woher kommt die Aussage?

Der Browser berechnet diese Bedeutung nicht selbst aus Spielwerten. Er liest ausschließlich die bereits vorhandene bestätigte Antwort des bestehenden `/api/command`-Pfads: die vorhandene District-Event-Identität und das vorhandene Replay-Signal.

## Was wird nicht gespeichert?

Die Klartextmeldung ist nur eine flüchtige Anzeige im bestehenden Settlement-Bereich. Sie erzeugt keinen zusätzlichen Save-Zustand, keinen Journal-Eintrag und keine zweite Ereignis-Timeline. Nach einem Reload kann die letzte Meldung deshalb verschwunden sein; der bestätigte Spielzustand selbst bleibt davon unberührt.

## Warum ist das nützlich?

Vorher waren Retry, erstmalige Wirkung und bewusstes Nichtauslösen technisch unterscheidbar, aber im Control Deck nicht verständlich benannt. Jetzt ist direkt sichtbar, ob wirklich etwas neu passiert ist oder ein sicherer Replay lediglich bestätigt, dass nichts doppelt ausgeführt wurde.
