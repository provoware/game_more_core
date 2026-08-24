# Control Deck – Bewegung und visuelle Tiefe

## Was ist neu?

Das Control Deck reagiert sichtbarer auf deine Bedienung, ohne Spielregeln zu verändern. Buttons heben sich beim Darüberfahren leicht an, Panels bekommen mehr räumliche Tiefe, Listen reagieren dezent und Kartenmarker treten beim Fokus klarer hervor. Eine gewählte Street-Strategie leuchtet außerdem eindeutiger als aktive Auswahl.

## Was bedeutet die Bewegung?

Die Bewegung ist ausschließlich Rückmeldung der Oberfläche. Ein angehobener Button bedeutet nicht, dass eine Aktion bereits ausgeführt wurde. Erst die vorhandene bestätigte Runtime entscheidet über Spielwerte, Ereignisse und Speicherzustand.

## Weniger Bewegung

Wenn dein Browser oder Betriebssystem **reduzierte Bewegung** (`prefers-reduced-motion`) verlangt, werden Übergänge und Animationen weiterhin vollständig abgeschaltet. Dadurch bleibt die Oberfläche auch ohne Bewegung verständlich und bedienbar.

## Bewusst nicht geändert

- keine Spielwerte oder Wahrscheinlichkeiten,
- keine Street-, Economy- oder District-Regeln,
- keine neuen API-Kommandos,
- keine zusätzlichen Schreibzugriffe,
- keine externe Grafik- oder Animationsbibliothek.

## Sinnvolle spätere Erweiterung

Eine spätere kleine Presentation-Iteration kann **bestätigte Ereignisse** kurz und lokal hervorheben, beispielsweise einen tatsächlich bestätigten Street-Ausgang oder eine Ressourcenänderung. Dabei muss weiterhin gelten: Die Runtime liefert die Bedeutung; die Animation visualisiert sie nur.
