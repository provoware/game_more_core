# Laienhilfe – Berlin Ops Map 2

## Was ist neu?

Die Berlin Ops Map kann jetzt **vergrößert, verschoben und auf einen ausgewählten Bezirk oder Ort fokussiert** werden. Das verändert ausschließlich deine Ansicht der Karte.

Die Karte bleibt read-only: Sie kauft nichts, baut nichts aus und verändert keine Bezirkswerte.

## Die acht Ansichts-Schalter

- **−** verkleinert die Karte schrittweise.
- **1:1** stellt die komplette Gesamtansicht wieder her.
- **+** vergrößert die Karte schrittweise.
- **← ↑ ↓ →** verschieben den sichtbaren Kartenausschnitt.
- **AUSWAHL FOKUS** richtet die Ansicht auf den Bezirk oder Ort aus, den du zuletzt angeklickt oder mit der Tastatur fokussiert hast.

Der Zoom ist absichtlich begrenzt: von **1,0× bis 2,2×**. Auch das Verschieben wird begrenzt, damit die Karte nicht vollständig aus dem sichtbaren Bereich geschoben werden kann.

## Tastatur

Alle Ansichts-Schalter sind normale Buttons. Mit **Tab** wechselst du zwischen ihnen, mit **Enter** oder **Leertaste** löst du die gewählte Funktion aus.

Auch Bezirke und Orte bleiben per Tastatur fokussierbar. Sobald du einen Bezirk oder Ort fokussierst, erscheinen seine bestätigten Informationen weiterhin im Detailbereich.

## Was bedeutet „Auswahl Fokus“?

1. Klicke einen Bezirk oder Ort an oder fokussiere ihn mit der Tastatur.
2. Drücke **AUSWAHL FOKUS**.
3. Die Karte zoomt mindestens auf 1,6× und verschiebt den Ausschnitt möglichst weit zur gewählten Position.
4. Mit **1:1** kommst du jederzeit zur Gesamtansicht zurück.

## Was wird gespeichert?

Nichts. Zoom, Pan und Kartenfokus sind nur lokale Anzeigezustände. Nach einem Neustart beginnt die Karte wieder in der normalen Gesamtansicht.

## Was darf die Karte ausdrücklich nicht?

- keine Domain- oder Save-Daten schreiben,
- keine Preise oder Ausbauten verändern,
- keine Navigation oder echte Geodaten verwenden,
- keine Rechnerzeit oder externen Kartendienste benötigen,
- keine zweite Map- oder Property-Engine aufbauen.

Alle dargestellten Bezirke, Orte, Scores, Eigentumsstände und Ausbaulevel stammen weiterhin aus den bereits bestätigten BUNKERFREQUENZ-Projections.


## Karte aktualisiert sich während der Tastaturbedienung

Wenn neue bestätigte Spielinformationen eintreffen, baut die Oberfläche die Kartenknöpfe neu auf. Der aktuell fokussierte sichtbare Ort beziehungsweise Bezirk soll dabei ausgewählt bleiben; der Tastaturfokus springt auf seinen neuen Knopf. Ist der Ort verschwunden oder durch einen Sichtfilter ausgeblendet, wird stattdessen ein sichtbarer Ort gewählt. Gibt es keine passenden Orte, bleibt die Karte leer und die Tastatur wechselt zum aktiven Sichtfilter.

**Wichtig:** Diese Korrektur betrifft nur Anzeige und Tastatur. Weder Spielstand noch Geld, Besitz, Bezirkswerte oder Karte werden dadurch verändert. Für die Bedienung außerhalb der Karte wird der Fokus nicht an sich gezogen.

Bei unerwarteter Auswahl: Sichtfilter „Alle“ wählen und den gewünschten Ort erneut mit **Tab** erreichen.


## Tastatur-Kurzprüfung bei großer Anzeige

Mit **Tab** erreichst du zunächst die Sichtfilter und danach die Kartensteuerung sowie die sichtbaren Orte. **Enter** aktiviert den gewählten Filter oder den Schalter **1:1**. Wenn du gerade einen Ort mit der Tastatur ausgewählt hast und die Karte neue bestätigte Informationen erhält, soll die Auswahl sichtbar bleiben. Verschwindet der Ort, springt der Fokus auf einen noch vorhandenen sichtbaren Ort.

Für die technische Vorrelease-Prüfung wird die Karte automatisch bei **800 × 600** und einer **zweifachen Darstellungsskalierung** geprüft. Das ist eine zusätzliche Sicherheitsprüfung, aber noch kein Nachweis für den Browser-Menüzoom aller Spielansichten. Dein eigener Sichttest ist erst unmittelbar vor der späteren Veröffentlichung vorgesehen.

## Schmale Fenster und starke Vergrößerung

Bei stark vergrößerter Darstellung steht dem Spiel weniger Platz für die einzelnen Bedienelemente zur Verfügung. Deshalb werden die Kartenfilter bei schmaler Ansicht in zwei Spalten angeordnet; die Ortsdetails stehen unter der Karte. Die Schaltflächen funktionieren weiterhin mit **Tab** und **Enter**, auch bei großer Schrift und hohem Kontrast.

Die automatische Prüfung verwendet zusätzlich eine **400 × 300 Bildpunkte große Browser-Innenfläche**. Das prüft die schmale Anordnung, die bei einem 800 × 600 großen Bildschirm und ungefähr 200 % Browserzoom entstehen kann. **Das ist eine technische Näherung und noch kein echter Browser-Menüzoom-Test.** Die vollständige Prüfung aller Spielansichten bleibt vor dem Vorrelease erforderlich. Deine persönliche Sichtprüfung erfolgt erst am fertigen, eingefrorenen Kandidaten.
