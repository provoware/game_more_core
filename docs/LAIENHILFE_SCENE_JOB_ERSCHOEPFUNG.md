# Laienhilfe – Scene Jobs bei sehr niedriger Energie

## Was ändert sich?

Scene Jobs bleiben weiterhin **jederzeit verfügbar**, sobald ein Character vorhanden ist. Es gibt keinen Rechnerzeit-Cooldown und keine neue Erschöpfungsleiste.

Neu ist nur die Auszahlung bei sehr niedriger Energie: Für den vollen Joblohn muss vor dem Job mindestens so viel Energie vorhanden sein, wie der Job laut Katalog verbraucht.

## Einfache Regel

- Genug Energie für den kompletten Energieverbrauch → voller katalogisierter Lohn.
- Weniger Energie als der Job verbraucht → Lohn wird im gleichen Verhältnis reduziert.
- 0 Energie → der Job kann weiterhin ausgeführt werden, erzeugt aber 0 Cent Joblohn.

Beispiel: Ein Job kostet 8 Energie und zahlt normalerweise 55,00 €. Mit nur 4 Energie sind noch 50 % des Energiebedarfs verfügbar, also werden 27,50 € bestätigt. Danach liegt die Energie bei 0.

## Warum bleibt der Job trotzdem verfügbar?

Die bestehende Grundregel lautet, dass Scene Jobs nicht von Eventphase oder Rechnerzeit abhängen. ANTI-GRIND ändert diese Regel nicht. Der Spieler darf weiterhin arbeiten; nur endloses Geldfarmen ohne verfügbare Energie wird verhindert.

## Gilt das auch für den geheimen besten Freund?

Ja. Der Assistent besitzt keine eigene Erschöpfungsregel. Eine bestätigte Assistentenrunde delegiert den ausgewählten Job an denselben `SceneJobService`, den auch ein manueller Scene Job verwendet. Deshalb gelten Auszahlung, Energieverbrauch, Retry und Recovery identisch.

## Was bleibt unverändert?

- katalogisierte Energie- und Stresswerte der fünf Scene Jobs
- Jobauswahl und Verfügbarkeit
- Finance-Ledger und `job_income`
- Retry-Schutz: derselbe Command zahlt nie zweimal
- Recovery aus Journal und bestätigtem Finance-State
- keine Rechnerzeit als Autorität
- keine zweite Erschöpfungswährung
- Browser darf keinen Lohnfaktor und keinen Zielbetrag liefern

## Technischer Balancevertrag

Der maschinenlesbare Vertrag liegt im bestehenden `SCENE_JOB_MANIFEST.json` unter `exhaustion_policy`. Die Runtime akzeptiert nur den Modus `pre_job_energy_proportional_payout` und bricht bei unsicheren Abweichungen fail-closed ab.

Die Berechnung verwendet ausschließlich die **bestätigte Energie direkt vor dem Job**, den katalogisierten Energieverbrauch und den katalogisierten Basislohn. Es gibt keinen Zufall und keine Zeitberechnung.
