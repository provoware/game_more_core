# Laienhilfe – zweite Street-Micro-Story

## Was ist jetzt eingebaut?

Die zuvor geprüfte zweite kleine Straßen-Geschichte ist jetzt umgesetzt:

**Ein Handschuh weniger → Der Handschuh wartet noch.**

Du verlierst bei einem bestätigten Straßengang einen Handschuh. Bei einem späteren bestätigten Straßengang desselben Charakters kann genau dieser Moment nachhallen: Der Handschuh hängt sichtbar über einem Bauzaun, weil ihn jemand aufgehoben und dort abgelegt hat.

## Was passiert dabei im Spiel?

- Die ursprüngliche Begegnung bleibt eine normale Street-Begegnung.
- Erst ein späterer bestätigter Street-Walk darf den Nachhall auslösen.
- Ursache und Folge werden eindeutig miteinander verknüpft.
- Ein Retry oder Neuladen erzeugt keine zweite Kopie derselben Folge.
- Pro späterem Street-Walk entsteht weiterhin höchstens ein Street-Nachhall.

## Wichtig: Der Handschuh wird nicht zum Gegenstand

Die Szene ist **nur Story und Atmosphäre**. Der Handschuh wird nicht ins Inventar gelegt, nicht als wiedergefunden verbucht und erzeugt keinen Bonus. Energie, Stress, Ruf, Geld und Economy erhalten durch den Nachhall keine zusätzliche Wirkung.

Dadurch bleibt die Geschichte glaubwürdig, ohne heimlich ein neues Inventar-, Orts- oder Belohnungssystem einzuführen.

## Warum ist das technisch robust?

Story 002 verwendet exakt denselben vorhandenen `street.followup_resolved`-Vertrag wie der Kabeltipp-Nachhall. Die Runtime besitzt bereits einen generischen Resolver für mehrere `micro_story_*`-Einträge. Es wurde deshalb **keine zweite Storyengine** ergänzt.

Eine Regression erzeugt den verlorenen Handschuh über den normalen Street-Service, löst den Nachhall erst beim späteren Walk aus und prüft Parent-ID, `causation_id`, `correlation_id`, Character-Bindung, fehlende Gameplay-Effekte und Exactly-once beim Retry.

## Was bleibt noch offen?

Die vorhandene read-only Timeline kann Street-Follow-ups grundsätzlich bereits darstellen. Ein eigener Browser-Ende-zu-Ende-Nachweis für Story 002 ist jedoch ein sinnvoller späterer QA-Schritt, damit auch der komplette Weg Save → `/api/state` → sichtbares Browser-DOM ausdrücklich für diese zweite Geschichte belegt ist.

## Sinnvolle spätere Erweiterung

Nach zwei unterschiedlichen Street-Nachhallen sollte vor Story 003 ein kleiner **Story-Tone-Diversity-Audit** prüfen, ob die Geschichten abwechslungsreich genug wirken und nicht immer nach demselben Muster funktionieren.
