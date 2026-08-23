# Laienhilfe – Scene Jobs & persönliches Bargeld

## Wozu sind die Jobs da?

Nicht jede Spielphase soll von einem großen Event abhängen. Unter **JOBS** kannst du deshalb normale szenetypische Arbeiten übernehmen und dir persönliches Bargeld ansparen.

Aktuell gibt es fünf Jobs:

- Flyer & Einlasslisten,
- Load-in Helfer,
- Kabel & Kleinkram reparieren,
- Bar-Support,
- Nacht-Abbau & Cleanup.

Die Jobs sind unabhängig von der aktuellen Eventphase verfügbar. Du brauchst also kein laufendes Event, um arbeiten zu können.

## Was sehe ich vor dem Start?

Jede Jobkarte zeigt dir bereits vor der Entscheidung:

- Dauer,
- Lohn,
- Energieänderung,
- Stressänderung.

Diese Werte kommen aus dem Spielvertrag auf der Runtime-Seite. Der Browser berechnet sie nicht selbst.

## Was passiert beim Klick auf „ARBEITEN“?

Der Browser sendet nur die ID des ausgewählten Jobs. Lohn, Energie und Stress kann die Oberfläche nicht frei vorgeben.

Die Runtime prüft den Job, verbucht die Ressourcenfolge und schreibt den Lohn in dein persönliches Finance-Ledger. Beides wird zusammen bestätigt. Wird derselbe technische Befehl nach einem Verbindungsproblem erneut übertragen, darf er nicht ein zweites Mal auszahlen.

## Ist das Bargeld dasselbe wie das Eventbudget?

Nein. Das ist wichtig:

- **Bargeld** gehört deinem Spieler und entsteht zum Beispiel durch Scene Jobs.
- **Eventbudget** gehört zur Planung und Durchführung eines Events.

B2 vermischt diese beiden Töpfe nicht.

## Was passiert mit alten Spielständen?

Ein alter Spielstand ohne persönlichen Finance-State bleibt lesbar. Die Anzeige beginnt dann bei **0,00 € Bargeld**. Das reine Anzeigen schreibt nichts nachträglich ins Journal.

## Warum gibt es schon Bank- und Anlagefelder im Finance-Modell?

Damit später nicht drei verschiedene Geldsysteme entstehen. Scene Jobs legen die gemeinsame persönliche Finance-Basis an. Bank, Zinsen, Anlagen, Dividenden und Kontoauszüge können danach denselben bestätigten Ledger weiterverwenden.

Diese Funktionen sind in B2 aber noch nicht freigeschaltet.

## Bekannte Balance-Grenze

Die Jobs sind absichtlich phasenunabhängig. Eine spätere Balanceiteration soll noch festlegen, wie starke Erschöpfung oder wiederholtes Endlosarbeiten behandelt wird, ohne die einfache Grundidee „jederzeit einen normalen Job annehmen“ unnötig kompliziert zu machen.
