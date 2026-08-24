# BUNKERFREQUENZ – RELEASE EVIDENCE CHAIN PRO

## Zweck

`RELEASE-EVIDENCE-CHAIN-PRO` macht die bereits vorhandenen Release-Nachweise als eine durchgehende SHA-256-Kette sichtbar und maschinenprüfbar. Es entsteht kein neuer Build und keine zweite Release-Logik: Die Stufe prüft ausschließlich die bereits erzeugten Evidence-Dateien und das tatsächlich promovierte Benutzer-ZIP.

## Kette

Ein `RELEASE_READY`-Lauf muss diese vier Glieder exakt verbinden:

1. `failure_containment_pro` – Hash der tatsächlichen `FAILURE_CONTAINMENT_EVIDENCE.json`.
2. `multi_browser_e2e_pro` – Hash der tatsächlichen `DESKTOP_BROWSER_E2E_EVIDENCE.json`; das Kettenglied verweist zusätzlich auf den Failure-Hash.
3. `release_evidence` – Hash der tatsächlichen `RELEASE_EVIDENCE.json`; diese muss die beiden Subgate-Hashes exakt enthalten und verweist im Kettenmodell auf den Browser-Hash.
4. `promoted_user_zip` – SHA-256 der tatsächlich hochgeladenen Benutzer-ZIP; sie muss exakt dem validierten `candidate_sha256` und `promoted_sha256` entsprechen und verweist auf den Release-Evidence-Hash.

Jede Quelldatei wird zusätzlich gegen ihre `.sha256`-Sidecar-Datei geprüft. Ein manipuliertes Evidence-JSON, ein falscher Sidecar-Hash, ein anderer Source Commit/Tree oder ein anderes finales ZIP bricht die Freigabe fail-closed ab.

## Chain Root

Nach erfolgreicher Prüfung entstehen:

- `RELEASE_EVIDENCE_CHAIN.json`
- `RELEASE_EVIDENCE_CHAIN.json.sha256`

Das JSON enthält Source Commit, Source Tree, einen gemeinsamen Candidate-SHA, alle vier Kettenglieder mit `previous_sha256` und einen zusätzlichen Hash über den terminalen Übergang `Release-Evidence → finales ZIP`.

## Für Laien

Vorher war bereits technisch sichergestellt, dass die einzelnen Prüfungen zum richtigen Release gehören. Jetzt wird diese Verbindung zusätzlich wie eine versiegelte Belegkette ausgegeben: Jeder Prüfzettel hat einen digitalen Fingerabdruck, der nächste Prüfzettel nennt den vorherigen Fingerabdruck, und am Ende muss exakt die ZIP-Datei stehen, die vorher geprüft wurde. Wird unterwegs nur ein Byte verändert, passt die Kette nicht mehr und die Release-Ausgabe scheitert.

## CI-Vertrag

Die Chain-Stufe läuft nur bei `RELEASE_READY`, weil nur dann ein Benutzer-ZIP existieren darf. Sie läuft jedoch **vor** dem Upload des Benutzerartefakts. Dadurch kann kein ZIP als Release-Artefakt hochgeladen werden, wenn seine Evidence-Kette nicht vollständig PASS ist.

Die beiden Chain-Dateien werden sowohl dem Release-Evidence-Artefakt als auch dem Benutzer-ZIP-Artefakt beigelegt. Damit können Release-Operator und Nutzer denselben terminalen Chain Root prüfen.

## Sicherheitsgrenzen

- kein neuer Build
- kein Rebuild nach Validierung
- keine Änderung von Gameplay, Save, Journal oder Browserlogik
- keine Netzwerk- oder Paketinstallation
- keine Signaturbehauptung: SHA-256 liefert Integritätsbindung, aber noch keine kryptografische Urheber-Signatur

## Spätere Erweiterungsidee

Als nächste Härtung kann `SIGNED-RELEASE-ATTESTATION-PRO` den Chain Root mit einer GitHub-OIDC-/Sigstore-Attestation oder einer vergleichbaren repository-gebundenen Signatur versehen. Nutzen: Zusätzlich zur Byte-Integrität wäre dann kryptografisch nachweisbar, aus welchem autorisierten CI-Kontext die Belegkette stammt.
