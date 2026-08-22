# Equipment & Economy 0.8.2

## Ziel und Grenze

0.8.2 verbindet Beschaffung, Event-Budget und Equipment-Anforderungen als einen journalfähigen Funktionsschnitt. Es ergänzt weder Client noch Netzwerk, Clubsystem oder den vollständigen Event-Ablauf aus 0.8.3.

## Zustände

Der Save-Block `economy` trennt vier Bereiche:

- `catalog`: feste Equipment-Definitionen und Preisdaten,
- `inventory`: bestätigter Besitz und davon reservierte Menge,
- `ledger`: unveränderliche Folge bestätigter Operationen,
- `market_tick` und `revision`: deterministische Preisstufe und Änderungsversion.

Der Katalog ist die Definition, das Inventar der Besitz. Sichtbare Namen sind keine IDs.

## Durchgängige Spielregel

1. Der Katalog wird einmal für einen vorhandenen Eventzustand bestätigt.
2. Kaufen erhöht Besitz und senkt das Event-Budget atomar (gemeinsam oder gar nicht).
3. Reservieren bindet freien Besitz an die Event-Anforderung.
4. Eine Anforderung ist erst `ready`, wenn ihre vollständige Menge reserviert ist.
5. Verbrauch entfernt nur freie, als verbrauchbar katalogisierte Ware.
6. Verkauf entfernt nur freien Besitz und erhöht das Budget.

Marktpreise hängen nur von Grundpreis, Schwankung in Basispunkten und `market_tick` ab. Systemzeit und Zufall werden nicht verwendet.

## Fehler- und Kompensationsregeln

- Budget, Besitz und Reservierung dürfen nie negativ werden.
- Reservierter Besitz kann nicht verkauft oder verbraucht werden.
- Dieselbe Command-ID mit demselben Inhalt ist ein folgenloser Replay; anderer Inhalt wird abgelehnt.
- Nur bestätigte Käufe und Verkäufe sind kompensierbar.
- Eine Kompensation verwendet den ursprünglichen Stückpreis genau einmal und prüft erneut den Bestand.

## Persistenz und Recovery

`economy.transaction_posted` enthält den bestätigten Economy- und Event-Folgezustand. Inventarereignisse dokumentieren Erwerb und Entfernung innerhalb derselben Transaktion. Recovery replayt den atomaren Folgezustand über den bestehenden `GameRecoveryService`; unabhängige Character-Blöcke bleiben erhalten.

## Spätere Erweiterung

Ein datengetriebener Lieferantenkatalog mit Lieferzeit und Verfügbarkeit sollte nach 0.8.3 ergänzt werden. Er schafft echte Beschaffungsentscheidungen, ohne die jetzt bestätigten Besitz-, Budget- und Replay-Regeln zu verändern.
