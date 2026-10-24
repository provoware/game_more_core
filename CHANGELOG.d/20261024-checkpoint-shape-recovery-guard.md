# 24.10.2026 – Vorrelease-Q01: ungültige Checkpoint-Formate

- State- und Save-Metadaten werden vor dem Zugriff auf Pflichtfelder strukturell validiert; ungültige JSON-Wurzeltypen, Sequenzen, Hashes und Schema-Versionen werden kontrolliert abgelehnt.
- Neue Regressionen für beschädigte lokale Test-Spielstände, gültigen Snapshot-Fallback und verweigerte Recovery ohne sichere Quelle.
- Bestehende Journal-, Snapshot-, Gameplay- und Kartenverträge unverändert; kein echtes Nutzersave bearbeitet.
- Kein Release-PASS ohne grünen Runtime- und Gesamt-CI-Nachweis auf finalem SHA.
