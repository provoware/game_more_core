# Laienhilfe – Scene-Job-Lohnvorschau

## Was ist neu?

Bei sehr wenig Energie kann ein Scene Job weiterhin gestartet werden, aber der Joblohn fällt niedriger aus. Die JOBS-Ansicht zeigt deshalb jetzt vor dem Start den tatsächlich bestätigten aktuellen Lohn.

## So liest du die Anzeige

- **Lohn 55,00 €** bedeutet: Deine bestätigte Energie reicht für den vollen Joblohn.
- **Lohn bis zu 55,00 € · aktuell 27,50 €** bedeutet: Der Job ist weiterhin möglich, aber deine aktuelle bestätigte Energie reicht nur für die Hälfte des normalen Lohns.
- Bei **0 Energie** bleibt der Job verfügbar, der aktuelle Lohn ist aber **0,00 €**.

## Wichtig

Die Anzeige rechnet den Lohn nicht im Browser aus. Die Runtime verwendet dieselbe kanonische Anti-Grind-Regel wie bei der echten Jobausführung und liefert nur das bestätigte Vorschauergebnis an die Oberfläche.

Der Browser kann weiterhin nur den `job_id` wählen. Er kann weder Energie, Lohnfaktor noch Auszahlung vorgeben.

## Gilt das auch für den geheimen Freund?

Ja. Manuelle Scene Jobs und der Assistent benutzen denselben `SceneJobService`. Deshalb gilt für beide dieselbe Erschöpfungs- und Lohnregel.
