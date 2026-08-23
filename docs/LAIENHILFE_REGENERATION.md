# Laienhilfe – Energie aktiv regenerieren

## Worum geht es?

Wenn deine Energie durch Scene Jobs stark gefallen ist, musst du nicht einfach weiter für immer weniger Lohn arbeiten. Im vorhandenen **JOBS-Bereich** gibt es jetzt eine kleine bestätigte Regenerationsaktion.

## Koffein & kalte Luft

Die erste Regenerationsmöglichkeit ist bewusst einfach:

- **+20 Energie**
- **+12 Stress**
- nur möglich, wenn du vorher höchstens **80 Energie** hast
- nur möglich, wenn du vorher höchstens **88 Stress** hast

Das bedeutet: Du bekommst kurzfristig wieder Energie, aber der Reset hat einen echten Preis. Du kannst ihn nicht endlos drücken, weil dein Stress dabei steigt.

## Warum gibt es die Grenzen 80 und 88?

Die Aktion soll immer exakt das tun, was sie ankündigt. Bei höchstens 80 Energie passen die +20 vollständig bis maximal 100. Bei höchstens 88 Stress passen die +12 ebenfalls vollständig bis maximal 100. Dadurch kann keine Hälfte des Preises oder Gewinns unbemerkt durch eine Obergrenze verschwinden.

## Was entscheidet der Browser?

Der Browser entscheidet **nicht**, wie viel Energie oder Stress du bekommst. Er sendet nur die stabile Kennung der gewählten Regenerationsaktion. Die Runtime prüft den bestätigten Character-Zustand und entscheidet, ob die Aktion gerade erlaubt ist.

Ist deine Energie bereits zu hoch oder dein Stress zu hoch, ist der Regenerationsknopf gesperrt und die Oberfläche erklärt den Grund.

## Was passiert beim Speichern und Wiederherstellen?

Die Aktion verwendet denselben bereits vorhandenen, replaybaren Character-Ressourcenpfad wie andere bestätigte Ressourcenänderungen. Deshalb kann ein Neustart oder Recovery den bestätigten Zustand wiederherstellen. Derselbe technische Retry darf die Energie nicht ein zweites Mal erhöhen.

## Was die Regeneration ausdrücklich nicht macht

- keine Rechnerzeit und kein Echtzeit-Warten
- keine automatische Energieaufladung im Hintergrund
- keine zweite Müdigkeits- oder Energiewährung
- keine XP und keine Trait-Punkte
- kein Zufallswurf
- keine Bank- oder Bargeldkosten
- kein neuer separater Journaltyp

Die Aktion ist damit eine kleine echte Gameplay-Entscheidung: **mehr Energie jetzt, dafür mehr Stress**.
