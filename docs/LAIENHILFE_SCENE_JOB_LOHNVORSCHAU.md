# Laienhilfe – Scene-Job-Lohnvorschau

## Was ist neu?

Bei sehr wenig Energie kann ein Scene Job weiterhin gestartet werden, aber der Joblohn fällt niedriger aus. Die JOBS-Ansicht zeigt deshalb vor dem Start den tatsächlich bestätigten aktuellen Lohn.

Wenn der Lohn wegen zu wenig Energie reduziert ist, erklärt die Jobkarte die Ursache jetzt direkt:

**„Aktueller Lohn reduziert – deine Energie reicht nicht für die volle Auszahlung.“**

## So liest du die Anzeige

- **Lohn 55,00 €** bedeutet: Deine bestätigte Energie reicht für den vollen Joblohn. Dann erscheint kein zusätzlicher Warnhinweis.
- **Lohn bis zu 55,00 € · aktuell 27,50 €** bedeutet: Der Job ist weiterhin möglich, aber deine aktuelle bestätigte Energie reicht nur für einen Teil des normalen Lohns. Direkt daneben steht der Hinweis zur reduzierten Auszahlung.
- Bei **0 Energie** bleibt der Job verfügbar, der aktuelle Lohn ist aber **0,00 €**. Auch hier erklärt derselbe bestätigte Hinweis die Ursache.

## Wichtig

Die Anzeige rechnet den Lohn nicht im Browser aus. Die Runtime verwendet dieselbe kanonische Anti-Grind-Regel wie bei der echten Jobausführung und liefert das bestätigte Vorschauergebnis sowie den Fakt `payout_reduced_by_energy` an die Oberfläche.

Der Browser kann weiterhin nur den `job_id` wählen. Er kann weder Energie, Lohnfaktor noch Auszahlung vorgeben.

Der Hinweis ist **nur eine Erklärung des aktuellen Lohns**. Er empfiehlt nicht automatisch eine Regenerationsaktion, startet nichts selbst und entscheidet nicht, was du als Nächstes tun sollst.

## Gilt das auch für den geheimen Freund?

Ja. Manuelle Scene Jobs und der Assistent benutzen denselben `SceneJobService`. Deshalb gilt für beide dieselbe Erschöpfungs- und Lohnregel.

## Später sinnvoll prüfen

Erst wenn mehrere verschiedene bestätigte Hinweise gleichzeitig auf derselben Spielsituation konkurrieren, sollte geprüft werden, ob die Runtime zusätzlich eine fachliche Priorität liefern muss. Bis dahin bleibt jeder Hinweis lokal bei seiner eigenen Ursache.
