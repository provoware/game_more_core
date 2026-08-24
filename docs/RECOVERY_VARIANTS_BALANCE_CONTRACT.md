# 0.8.8-ECON-RECOVERY-VARIANTS – Balancevertrag

## Ziel

Eine zweite aktive Regenerationsentscheidung soll eine **echte situative Alternative** zu `Koffein & kalte Luft` sein. Sie darf die bestehende Aktion weder mathematisch dominieren noch durch Rechnerzeit, Cooldowns oder eine zweite Ressourcenengine künstlich erzwungen werden.

## Bestehende Referenz

`Koffein & kalte Luft`

- Energie: `+20`
- Stress: `+12`
- maximale Energie vorher: `80`
- maximaler Stress vorher: `88`
- Energie je zusätzlichem Stresspunkt: `20 / 12 = 1,666…`

Die Aktion ist damit der **effizientere kleine Reset**.

## Gewählte zweite Variante

`Mate, Zucker & Vollgas`

- Energie: `+30`
- Stress: `+20`
- maximale Energie vorher: `70`
- maximaler Stress vorher: `80`
- Energie je zusätzlichem Stresspunkt: `30 / 20 = 1,5`

Die Aktion ist damit der **größere, aber ineffizientere Sofortschub**.

## Warum genau +30 / +20?

Gegenüber `+20 / +12` liefert die Variante:

- `50 %` mehr Energie in einer einzelnen bestätigten Aktion,
- aber `66,7 %` mehr Stress,
- und damit weniger Energie pro bezahltem Stresspunkt.

Sie ist deshalb kein kostenloses Upgrade. Wer nur einen kleinen Energiemangel schließen muss, fährt mit `Koffein & kalte Luft` günstiger. Wer sofort deutlich mehr Energiereserve benötigt, kann bewusst den höheren Stresspreis akzeptieren.

## Headroom-Vertrag

Beide Aktionen müssen ihren kompletten Gewinn und ihren kompletten Preis anwenden können. Clamping darf keine Kosten abschwächen.

| Aktion | max. Energie vorher | Energie danach | max. Stress vorher | Stress danach |
|---|---:|---:|---:|---:|
| Koffein & kalte Luft | 80 | 100 | 88 | 100 |
| Mate, Zucker & Vollgas | 70 | 100 | 80 | 100 |

Damit bleibt die bestehende Fail-closed-Regel unverändert: Ist nicht genug Headroom vorhanden, ist die jeweilige Aktion gesperrt.

## Beispielentscheidungen

### Energie 70 / Stress 40

- Koffein & kalte Luft → Energie `90`, Stress `52`
- Mate, Zucker & Vollgas → Energie `100`, Stress `60`

Hier ist die Entscheidung klar: zehn zusätzliche Energiepunkte kosten acht zusätzliche Stresspunkte.

### Energie 40 / Stress 30

- Koffein & kalte Luft → Energie `60`, Stress `42`
- Mate, Zucker & Vollgas → Energie `70`, Stress `50`

Der große Schub erzeugt mehr sofortige Reserve, bleibt aber schlechter in der Stress-Effizienz.

### Energie 60 / Stress 81

- Koffein & kalte Luft ist noch möglich.
- Mate, Zucker & Vollgas ist gesperrt, weil der stärkere Stresspreis nicht mehr vollständig bezahlt werden kann.

Die stärkere Variante erweitert also nicht still die Verfügbarkeit.

## Mehrfachnutzung

Es wird **keine neue globale Recovery-Sperre** eingeführt. Mehrfachnutzung bleibt ausschließlich durch die bereits vorhandenen Energie-/Stress-Schwellen begrenzt. Der neue Schub darf deshalb nicht effizienter als die kleine Aktion sein.

Dass mehrere kleine Aktionen in manchen Zuständen langfristig günstiger sein können, ist beabsichtigt: `Mate, Zucker & Vollgas` kauft **Sofortwirkung**, nicht bessere Gesamteffizienz.

## Autoritätsgrenzen

- keine Echtzeitregeneration
- keine Rechnerzeit als Autorität
- kein Cooldown
- keine neue Ressource
- keine XP oder Traits
- keine Zufallsentscheidung
- Browser liefert ausschließlich `recovery_id`
- Energie-/Stresswerte und Availability bleiben Runtime-Autorität
- Retry derselben Command-ID bleibt schreibfrei
- Recovery bleibt auf dem bestehenden `character.resources_changed`-Replay-Pfad

## Abnahmekriterium für den Runtime-Slice

Der Runtime-Slice darf ausschließlich die zweite katalogisierte Aktion in den vorhandenen `RecoveryActionService` aufnehmen und direkte Regressionen ergänzen. Projection, Session und Browser dürfen nur dann geändert werden, wenn ein konkreter Test- oder Gate-Befund zeigt, dass ihre bereits generische Verarbeitung nicht ausreicht.
