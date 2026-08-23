<div align="center">

# BUNKERFREQUENZ

### Beton. Bass. Berlin.

**Techno-/FreeTekno-Crew-RPG · Character Forge · Event-Management · Living Districts · Property Progression**

<p>
  <img alt="Runtime Baseline 0.8.4 alpha 1" src="https://img.shields.io/badge/Runtime_Baseline-0.8.4--alpha.1-ff4d00">
  <img alt="Feature Stand 0.8.8 F validiert" src="https://img.shields.io/badge/Feature_Stand-0.8.8--F_validiert-7dff00">
  <img alt="District Biography in Abnahme" src="https://img.shields.io/badge/Berlin_Erinnerungen-STORY_in_Abnahme-00c2ff">
  <img alt="District Cadence validiert" src="https://img.shields.io/badge/District_Cadence-C5_validiert-ff7ad9">
  <img alt="Mergeweg Safe Merge" src="https://img.shields.io/badge/Mergeweg-%2Fsafe--merge-8a2be2">
</p>

> **Entdecken → arbeiten → ansparen → nachvollziehen → entscheiden → planen → handeln → eskalieren → abrechnen → Stadt verändern → erinnern → ausbauen → aufsteigen.**

</div>

![BUNKERFREQUENZ System- und Character-Forge-Blueprint](docs/assets/BUNKERFREQUENZ_SYSTEM_BLUEPRINT_0.4.3.webp)

---

## ⚡ Projekt-Puls

| | Aktueller Stand |
|---|---|
| **Release-Baseline** | `0.8.4-alpha.1` – letzter bewusst freigegebener Produktrelease |
| **Validierter Feature-Stand** | ✅ `0.8.8-F – Berlin Ops Map 2` |
| **Aktive Iteration** | 🟡 `0.8.8-STORY-DISTRICT-BIO – Bezirks-Nachhall` |
| **Nächste Iteration** | `0.8.8-FIN-EXPORT – Kontoauszug TXT/CSV` |
| **Lokaler Game Client** | ✅ schreibender A4-Client, localhost-only |
| **Crew Identity** | ✅ Logo/Fahne als syncbereites Datenrezept, kein Bildblob |
| **Living World** | ✅ replaybare Street Encounters, persistente Districts, District World Events + 24h-Cadence |
| **Timeline** | ✅ Street-, Krisen- und District-Ereignisse read-only im Control Deck sichtbar |
| **Ranking** | ✅ Competitive Top 10 + bestätigte Wochen-/Monatszyklen |
| **Property** | ✅ 7 kaufbare Orte + 10 Ausbauarten, Level 1–3 |
| **Berlin Ops Map 2** | ✅ 8 Districts · 12 Locations · read-only · lokaler Zoom/Pan + Auswahlfokus |
| **Scene Jobs** | ✅ fünf Jobs + persönlicher Wallet-/Ledger-Pfad remote validiert |
| **Assistent C1–C5B** | ✅ Autorität, Steuerung, Rundenausführung, JOBS-UI und bestätigter Freundschafts-Nachhall |
| **Bankkonto D/D2** | ✅ Wallet↔Bank + 1 % bestätigter Sparzins/Zinseszins ohne Rechnerzeit-/Browserautorität |
| **Kontoauszüge** | ✅ bestätigtes Finance-Ledger read-only als Joblohn, Bankbewegung und Sparzins; keine zweite Buchhaltung |
| **Berlin-Erinnerungen** | 🟡 bis zu fünf bestätigte District-Ereignisse als read-only Nachhall im Profil; keine Progressionsengine |
| **Control Deck E** | ✅ lokaler Bereichsfokus + Runtime-abgeleitetes Nächste-Aktion-Signal |
| **Netzwerk/Telegram** | noch nicht implementiert; keine erfundenen Remote-Spieler |

> [!IMPORTANT]
> `0.8.8-F` ist remote validiert und ausschließlich über `/safe-merge` nach `main` gelangt. STORY-DISTRICT-BIO liest nur bereits bestätigte District-Einträge der bestehenden Ereignis-Chronik. Der Browser erzeugt weder Bezirksereignisse noch neue Biografieeinträge, Boni, Zeitstempel oder Gameplaywerte.

---

## 🎮 Spielkern

BUNKERFREQUENZ ist ein lokales Techno-/FreeTekno-Crew-RPG. Bestätigte Aktionen, Ereignisse und ihre Folgen formen Charakter, Crew und Stadt.

```text
SCENE JOBS → PERSÖNLICHES BARGELD → BANK / SPAREN → KONTOAUSZUG
      ↓
STRASSE / SPIELERANSATZ
      ↓
CHARAKTER & CREW
      ↓
EVENT PLANEN
      ↓
EQUIPMENT / PROPERTY / STADTLAGE
      ↓
EVENT STARTEN
      ↓
KRISE? → FOLGEN ANSEHEN → ENTSCHEIDEN
      ↓
SETTLEMENT
      ↓
DISTRICT WORLD EVENT (CADENCE-GEFÜHRT)
      ↓
RUF · SKILLS · BIOGRAFIE · TIMELINE · BERLIN-ERINNERUNGEN
      ↓
LIVING DISTRICTS / BERLIN OPS MAP
      ↓
PROPERTY / HALL OF TRIBUTE
```

### Bereits validiert

- 16 Skills, 165 Trait-Namen, Level 1–50 + Resonanz
- Event-State, Equipment/Economy, Krisen und Settlement
- Save, Snapshot, Restart und Recovery
- Street Encounters ohne Reload-Reroll
- persistente District-Werte
- Property Purchase + dreistufige Upgrades
- Berlin Ops Map PRO + Map 2 mit begrenztem lokalem Zoom/Pan und Auswahlfokus
- Competitive Top 10 + Wochen-/Monatszyklen
- sichtbare read-only Ereignis-Timeline
- District World Events mit deterministischer Auswahl und 24h-Cadence aus bestätigter Spielweltzeit
- Crew-Logo/Fahne als kleine synchronisierbare Identitätsdaten statt Bilddatei
- Scene Jobs mit persönlichem Bargeld, Retry-Schutz und Recovery
- Assistent C1–C5B: Autorität, Steuerzustand, exakt-einmal Rundenausführung, JOBS-UI und bestätigter Freundschafts-Nachhall
- Bankkonto D: atomare Ein-/Auszahlung auf demselben persönlichen Finance-State/Ledger
- Sparzinsen D2: bestätigter Finance-Tick, Zinseszins, Retry-Schutz, keine Rechnerzeit-Autorität
- Control Deck E: lokaler Fokus/Zurücksetzen und Nächste-Aktion-Signal ausschließlich aus vorhandener Runtime-Freigabe
- FIN-STATEMENTS: bestätigtes Finance-Ledger read-only als verständliche persönliche Geldhistorie

---

## 🌆 0.8.7-C – District World Events & Timeline ✅

### C1–C3: Vertrag, Runtime, Application

Vier erste Bezirksereignisse verwenden stabile IDs, katalogisierte Voraussetzungen und kleine District-Effekte. Die Auswahl bleibt deterministisch aus `world_seed + district_id + trigger_id`. Der Browser kann weder Ereignisse aktivieren noch Gewichte oder Effekte einspeisen. `settlement.complete` ist der einzige autorisierte Application-Trigger.

### C4A/C4B: Ereignis-Timeline

Die Timeline liest ausschließlich bestätigte Journalrecords für Street Encounters, gelöste Krisen und District-Ereignisse. C4A liefert die kanonische Projection; C4B zeigt sie im Control Deck an. Der Browser übernimmt Reihenfolge und Texte read-only und besitzt keinen zweiten Story- oder Save-Pfad.

**Remote-Abnahme C4B:** PR #101 · Head `e23271c5dcb1463d68178b37faa2602d24d6eb46` · 5/5 Gates · SAFE MERGE PASS · Merge `3d71f00c5717ae797e6b8f1ca4c65c036bf71c81`.

### C5: Cadence/Cooldown

District-Ereignisse werden global über **24 Stunden bestätigte Spielweltzeit** dosiert. Autorität ist `event.time_window.start_local`; Systemzeit ist kein Fallback. Ein Trigger innerhalb des Cooldowns bleibt ein schreibfreier No-op. Retry und Reload würfeln bestätigte Trigger nicht neu.

**Remote-Abnahme C5:** PR #102 · Head `05eef417efa24f299ebc7de7f2104f6a625d5582` · Runtime `32646269065` · Presentation `32646269053` · Repository Health `32646269009` · Release Acceptance `32646269064` · Release Package `32646269010` · SAFE MERGE PASS · Merge `bd79da8d1e124ec60248a05bf332c6ef338ca7b6`.

---

## 🏴 0.8.8-A – Crew Identity Logo/Fahne ✅

Jeder Spieler kann seine Crew als Logo oder Fahne aus einem kleinen validierten Rezept darstellen:

- Typ `logo` oder `flag`
- Flächenstil `solid`, `split`, `band` oder `diagonal`
- katalogisiertes Symbol
- drei katalogisierte Farb-IDs
- optionale Kurzmarke mit maximal vier Zeichen

Der bestehende `profile.update`-Pfad ist die einzige Schreibgrenze. A4 zeigt einen Live-Editor mit Preview; beim Speichern sendet der Browser nur die katalogisierten IDs und die Kurzmarke. Alte Saves erhalten beim Laden eine stabile neutrale Standardidentität. Für späteren Multiplayer-Sync reichen `character_id + crew_identity`; Bildbytes sind nicht nötig.

**Remote-Abnahme 0.8.8-A:** PR #104 · Head `8d7004f0d835ad3c386ed657b49644fb3c1aa739` · Runtime `32648468121` · Presentation `32648468165` · Repository Health `32648468119` · Release Acceptance `32648468142` · Release Package `32648468140` · 0 Review-Threads · SAFE MERGE PASS · Merge `7e0ed1e36dcc89436c0430d49e547fe2106f756b`.

---

## 💶 0.8.8-B – Scene Jobs & persönliches Bargeld ✅

Fünf katalogisierte Scene Jobs stehen mit Character unabhängig von der Eventphase zur Verfügung:

- Flyer & Einlasslisten
- Load-in Helfer
- Kabel & Kleinkram reparieren
- Bar-Support
- Nacht-Abbau & Cleanup

Jeder Job besitzt serverseitig festgelegte Dauer, Auszahlung, Energie- und Stressfolge. Der A4-Client zeigt diese Folgen vor der Wahl an, sendet beim Arbeiten aber nur `job_id` und die technische Command-ID. Auszahlung und Ressourcenwerte können vom Browser nicht eingespeist werden.

Das persönliche Bargeld läuft über einen eigenen `PlayerFinanceState` und ein gemeinsames Finance-Ledger, das später auch Bank, Zinsen, Anlagen und Dividenden aufnehmen kann. **Persönliches Bargeld und Eventbudget bleiben getrennte Töpfe.** `SceneJobService` verbucht Joblohn und Character-Ressourcen atomar; Retry mit derselben Command-ID zahlt nicht doppelt, Recovery rekonstruiert den bestätigten Finance-State.

B2 ergänzt einen kompakten JOBS-Bereich und eine Bargeldanzeige im OPS-HUD. Alte Saves ohne Finance-State zeigen lesend 0,00 € und werden nicht allein durch die Anzeige umgeschrieben.

**Remote-Abnahme 0.8.8-B:** PR #105 · Head `6a653e40e19c80aed4df827910f7c91110a8a679` · Runtime `32649707398` · Presentation `32649707389` · Repository Health `32649707385` · Release Acceptance `32649707396` · Release Package `32649707391` · 0 Review-Threads · SAFE MERGE PASS · Merge `83aa6d050909e949a42f3c1bb3ab5c267b386693`.

---

## 🤝 0.8.8-C – Secret Best Friend Assistant ✅

**C1 ✅** bindet den Assistenten an den vorhandenen Scene-Job-Vertrag: maximal eine Aufgabe, bestätigte Spielrunde als spätere Ausführungsautorität, keine Systemzeit und keine frei lieferbaren Browserfolgen. Remote-Abnahme: PR #107 · Head `3cf918ac98d5a76d2b4ff13b3f6e46b2a458d06f` · Runtime `32653528714` · Presentation `32653528815` · Repository Health `32653528779` · Release Acceptance `32653528627` · Release Package `32653528682` · SAFE MERGE PASS · Merge `a16436582928d02202f38366c63d7cf790d5deb6`.

**C2 ✅** ergänzt ausschließlich den recoverbaren Steuerzustand `Aus / gewählter Scene Job`. Start, Wechsel und Stop laufen über den bestehenden Persistence-Kernel und `assistant.control_changed`. Eine wiederholte identische Auswahl ist schreibfrei; dieselbe Command-ID kann nicht nachträglich eine andere Auswahl bedeuten. Remote-Abnahme: PR #108 · Head `a8d6b9ffe2c8369ff1a41320a87faad069610779` · Runtime `32656644301` · Presentation `32656644312` · Repository Health `32656644321` · Release Acceptance `32656644302` · Release Package `32656644313` · SAFE MERGE PASS · Merge `5c597479afafe64f63aa4ce015cea5365b2320bf`.

**C3 ✅** bindet einen bereits intern bestätigten Rundentrigger an genau eine Ausführung des aktuell gewählten Scene Jobs. `AssistantRoundExecutionService` orchestriert nur; Auszahlung und Ressourcenfolgen bleiben im `SceneJobService`. `assistant.round_processed` verhindert rückwirkende Ausführung alter Trigger und ergänzt einen Crash-sicheren Abschlussmarker. Remote-Abnahme: PR #109 · Head `4d9a571141815cd0a589672308a25e91421dfb70` · Runtime `32658555902` · Presentation `32658555885` · Repository Health `32658555929` · Release Acceptance `32658555886` · Release Package `32658555891` · SAFE MERGE PASS · Merge `85e95995d5e84c53131e24a8ad3dec36717891c6`.

**C4 ✅** integriert die vorhandene Steuerung direkt in den bestehenden JOBS-Bereich. Jeder Job kann den Freund starten oder die Auswahl wechseln; der aktive Job wird sichtbar markiert und ein gemeinsamer Stop-Schalter setzt ihn auf Aus. Der Browser sendet nur `job_id`/`null` plus technische Command-ID. Rundentrigger, Lohn und Effekte bleiben außerhalb der Browserautorität. Remote-Abnahme: PR #110 · Head `06895cefb4fd715a7935578566452c7382fd7a1a` · Runtime `32659349173` · Presentation `32659349181` · Repository Health `32659349195` · Release Acceptance `32659349180` · Release Package `32659349202` · SAFE MERGE PASS · Merge `f8295564a4bddabddb4493c778e549d1cb083374`.

**C5A/C5B ✅** sichern Freundschafts-Nachhall zuerst als read-only Projection aus `assistant.round_processed` plus passender `finance.job_completed`-Buchung ab und zeigen ihn anschließend deterministisch im vorhandenen JOBS-Assistentenblock. Es gibt keinen Freundschaftswert und keine zweite Progressionsengine. C5B Remote-Abnahme: PR #112 · Head `da76621ecea0cd8e1afecd967fe7201a7c1d4c6c` · Runtime `32660419399` · Presentation `32660419381` · Repository Health `32660419392` · Release Acceptance `32660419409` · Release Package `32660419390` · SAFE MERGE PASS · Merge `eaa615e48eecd84ba3ffb69551f8fb324fb42c12`.

---

## 💳 0.8.8-D – Bankkonto & Sparen ✅

**D ✅** verschiebt persönliches Geld atomar zwischen Wallet und Bank. `PlayerFinanceState`, Finance-Ledger und Recovery bleiben die einzige Finanzarchitektur. Browserbefehle liefern nur Richtung und positiven Betrag; Zielstände bleiben Runtime-Autorität. Remote-Abnahme: PR #113 · Head `e41f2b40beb6508c21175a768ea3fb18050c79b1` · Runtime `32662002026` · Presentation `32662002022` · Repository Health `32662002030` · Release Acceptance `32662002025` · Release Package `32662002046` · SAFE MERGE PASS · Merge `c1a27a977ff76a397d95ae097395317c4d46950b`.

**D2 ✅** ergänzt 1 % Sparzins pro bereits bestätigter Finance-Periode. Der fortlaufende `confirmed_finance_tick` wird genau einmal verarbeitet; Folgeperioden verzinsen den aktuellen Bankstand und erzeugen dadurch Zinseszins. D2 erzeugt selbst keine Periode und akzeptiert weder Systemzeit noch Browser als Autorität. Remote-Abnahme: PR #114 · Head `897b5717776012376ef20e33093b413700744e07` · Runtime `32663103520` · Presentation `32663103517` · Repository Health `32663103523` · Release Acceptance `32663103519` · Release Package `32663103518` · SAFE MERGE PASS · Merge `bbebc9c3cafeac7f71eebeea1b89d4861b304e76`.

---

## 🎛️ 0.8.8-E – Control Deck Focus ✅

E verdichtet das vorhandene Control Deck ohne neuen Gameplay-State. Sichtbare Bereiche können lokal fokussiert und mit `GESAMTANSICHT` zurückgestellt werden. Das Nächste-Aktion-Signal markiert ausschließlich einen bereits von der Runtime freigegebenen Event-Button; der Browser erfindet keine Gate-Regel. Fokus wird nicht gespeichert, Reduced Motion bleibt statisch nutzbar.

**Remote-Abnahme E:** PR #115 · Head `131d7a8eff787a04ced995b1385ae85e7bdff89f` · Runtime `32664026523` · Presentation `32664026458` · Repository Health `32664026461` · Release Acceptance `32664026528` · Release Package `32664026553` · SAFE MERGE PASS · Merge `6ac72d794ad3565bc40eb23dd501626382aa679a`.

---

## 🧾 0.8.8-FIN-STATEMENTS – Kontoauszüge ✅

FIN-STATEMENTS verwendet **keine zweite Buchhaltung**. Die bestehende Scene-Jobs-/Bank-Projektion liest ausschließlich bestätigte Zeilen aus `PlayerFinanceState.ledger` und stellt vier bereits vorhandene Buchungsarten verständlich dar:

- `job_income` → Joblohn
- `bank_deposit` → Einzahlung
- `bank_withdrawal` → Auszahlung
- `savings_interest` → Sparzins

Die neueste unterstützte Buchung steht oben. Summen entstehen ausschließlich aus den vorhandenen Ledgerzeilen. `ALLE / JOBLOHN / BANK / ZINSEN` sind lokale Anzeige-Filter und schreiben weder Save noch Journal. Da das aktuelle persönliche Ledger keinen kanonisch bestätigten Buchungszeitpunkt trägt, zeigt die UI eine stabile `Buchung #N` und **erfindet kein Datum**. Spätere/andere Ledgerarten werden nicht interpretiert, sondern nur transparent gezählt.

**Remote-Abnahme FIN-STATEMENTS:** PR #116 · Head `614e4363e95f6fedb5aac51e5aac72a67848ffbb` · Runtime `32665075313` · Presentation `32665075287` · Repository Health `32665075289` · Release Acceptance `32665075282` · Release Package `32665075278` · SAFE MERGE PASS · Merge `81dda0d21170a5d876cd5a7ebf05a8409ec735c8`.

---

## 🗺️ 0.8.8-F – Berlin Ops Map 2 ✅

Map 2 erweitert ausschließlich die bestehende bestätigte 0–100-Kartenprojektion: lokaler Zoom von 1,0× bis 2,2×, begrenztes Pan, Reset und Auswahlfokus. Der Fokus verwendet nur vorhandene District-Boxen beziehungsweise Location-Positionen. Es gibt kein Geocoding, keinen externen Kartendienst und keinen gespeicherten Map-Zustand.

**Remote-Abnahme F:** PR #117 · Head `91255bbb7bee90050cbd762ce93600802a666940` · Runtime `32666137485` · Presentation `32666137499` · Repository Health `32666137472` · Release Acceptance `32666137497` · Release Package `32666137508` · SAFE MERGE PASS · Merge `8119bf71a6f169d5cac367d5123d2bc1e6a73193`.

---

## 🌃 0.8.8-STORY-DISTRICT-BIO – Bezirks-Nachhall 🟡

Der Story-Slice macht bereits bestätigte Bezirksereignisse im bestehenden Profil als kleine **Berlin-Erinnerungen** sichtbar. Quelle ist ausschließlich die vorhandene `event_timeline`; angezeigt werden höchstens fünf bestätigte `district`-Einträge mit ihren bereits projizierten Titeln, Texten und District-Deltas.

Die Anzeige schreibt nichts zurück. Sie erzeugt keine XP, Ruf-, Beziehungs- oder Bonuswerte, keinen neuen Biografie-Eventtyp und keine erfundenen Zeitangaben. Die persistente Charakterbiografie bleibt unverändert.

---

## 🧭 0.8.8 – geplanter Ausbau

Der Ausbau bleibt in getrennte, prüfbare Slices zerlegt:

| Slice | Ziel | Kernregel |
|---|---|---|
| **0.8.8-A** | Crew-Logo/Fahne | ✅ synchronisierbare Identitätsdaten statt Bildblob |
| **0.8.8-B** | Scene Jobs | ✅ katalogisierte Jobs + persönliches Bargeld; Browser sendet nur `job_id` |
| **0.8.8-C1–C5B** | Secret Best Friend | ✅ bestehende Jobs, bestätigte Runde, sichere Steuerung und read-only Nachhall |
| **0.8.8-C6** | Round-Authority Integration Harness | abhängig vom echten kanonischen Rundenproduzenten |
| **0.8.8-D/D2** | Bank & bestätigte Sparzinsen | ✅ gleicher Finance-State/Ledger, keine Rechnerzeit-Autorität |
| **0.8.8-E** | Control Deck Focus | ✅ lokaler Fokus + Runtime-abgeleitete nächste Aktion |
| **0.8.8-FIN-STATEMENTS** | Kontoauszüge | ✅ bestehendes bestätigtes Ledger read-only verständlich |
| **0.8.8-F** | Berlin Ops Map 2 | ✅ begrenzter lokaler Zoom/Pan + Auswahlfokus auf bestehender Projection |
| **0.8.8-STORY-DISTRICT-BIO** | Berlin-Erinnerungen | 🟡 ausschließlich bestätigte District-Timeline im Profil, keine Progressionsengine |
| **0.8.8-FIN-EXPORT** | Kontoauszug TXT/CSV | als nächstes; ausschließlich aus validierter FIN-STATEMENTS-Projection |

Anlagen/Dividenden und lokaler Timeline-Fokusfilter bleiben eigenständige Folge-Slices, damit Economy, UI und Sync nicht in einer Mega-Änderung vermischt werden.

---

## 🗺️ Berlin Ops Map PRO ✅

Die aktuelle Karte bleibt eine reine Presentation-Schicht:

- 8 District-Flächen und 12 Locations
- Heat, Prestige, Polizeidruck, Szeneaktivität
- Score/Tier/Rang
- Eigentum + Ausbau
- Hall-Markierung
- Filter `all / owned / prime / hall`
- Tastaturfokus + ARIA + Reduced Motion
- begrenzter lokaler Zoom/Pan + Auswahlfokus

`map_pro.js` besitzt keine eigene Domainlogik, kein `/api/command`, kein Geocoding und keinen externen Kartendienst. Map 2 hält diese Grenze ein.

---

## 🚀 Start für absolute Anfänger

Im Projektordner:

```bash
./START_BUNKERFREQUENZ.sh
```

Bei belegtem Port:

```bash
./START_BUNKERFREQUENZ.sh --port 0
```

Alternativ:

```bash
python3 tools/start_a4_game_client.py
```

Der Server bindet ausschließlich an `127.0.0.1`.

Ausführliche Erklärung: [`docs/A4_FIRST_RUN_ANLEITUNG.md`](docs/A4_FIRST_RUN_ANLEITUNG.md)

---

## 🧱 Architekturgrenzen

```text
DOMAIN
  ↓
APPLICATION SERVICES
  ↓
PERSISTENCE / JOURNAL / RECOVERY
  ↓
READ-ONLY PROJECTIONS
  ↓
A4 CONTROL DECK
```

| Ebene | Darf | Darf nicht |
|---|---|---|
| Domain | Invarianten/Zustandsregeln | UI kennen |
| Application | Use Cases und Orchestrierung | Persistenz umgehen |
| Infrastructure | Journal/State/Snapshot/Recovery | Gameplay erfinden |
| Presentation | bestätigte Daten erklären/darstellen | Domain-/Save-State direkt schreiben |
| Browser-UI | Auswahl-IDs und lokale Darstellung senden | Preise, Erträge, Jobfolgen, Zinsen, Rundenautorität oder Regeln autorisieren |

Neue UI-Funktionen wie Zoom, Filter, Fokus-Maximierung, Aktionshervorhebung oder Berlin-Erinnerungen bleiben lokale Presentation. Wiederholte Assistentenaktionen, Zinsen und Dividenden benötigen bestätigte Spielautorität und dürfen nicht durch die Rechneruhr allein fortschreiten.

---

## 🛡️ Persistenz & Recovery

- append-only JSONL-Journal
- SHA-256-Hashkette
- atomare State-/Meta-Writes
- Snapshots
- Replay/Recovery aus bestätigtem Journal
- Quarantäne beschädigter Journal-Tails
- Fault-Injection-Regressionen

> **Ein UI-Refresh, Zoom, Filter oder andere Anzeigeeinstellung darf niemals Gameplay erneut würfeln, Jobs doppelt auszahlen, Zinsen doppelt buchen oder bestätigte Fachwerte verändern.**

---

## ✅ Wichtige Meilensteine

| Iteration | Kern | Merge |
|---|---|---|
| 0.8.4-alpha.1 | erster freigegebener lokaler Release | `3fdb5cc3d57e...` |
| 0.8.5-C | replaybare Street Encounters | `38de9f42c290...` |
| 0.8.5-D | Living Districts | `98c8b84715cc...` |
| 0.8.5-E | Hall of Tribute | `d383a3f364c6...` |
| 0.8.6-A | Property Purchase | `192b3eb4ad9d...` |
| 0.8.6-B | Property Upgrades | `0b301bc9004f...` |
| 0.8.6-C | Berlin Ops Map PRO | `10c7d6b5e048...` |
| 0.8.7-A | Saisonale Hall of Tribute | `841258a37915...` |
| 0.8.7-B | Control Deck & Player Choices | `4d1a35bfbc08...` |
| 0.8.7-C4B | sichtbare Ereignis-Timeline | `3d71f00c5717...` |
| 0.8.7-C5 | District-Event Cadence/Cooldown | `bd79da8d1e12...` |
| 0.8.8-A | Crew Identity Logo/Fahne | `7e0ed1e36dcc...` |
| 0.8.8-B | Scene Jobs & persönliches Bargeld | `83aa6d050909...` |
| 0.8.8-C1 | Assistant Authority Contract | `a16436582928...` |
| 0.8.8-C2 | Assistant Control State | `5c597479afaf...` |
| 0.8.8-C3 | Confirmed-Round Execution | `85e95995d5e8...` |
| 0.8.8-C4 | JOBS-UI-Integration | `f8295564a4bd...` |
| 0.8.8-C5B | sichtbarer Freundschafts-Nachhall | `eaa615e48eec...` |
| 0.8.8-D | Atomic Wallet ↔ Bank Transfers | `c1a27a977ff7...` |
| 0.8.8-D2 | Confirmed Savings Interest | `bbebc9c3cafe...` |
| 0.8.8-E | Control Deck Focus | `6ac72d794ad3...` |
| 0.8.8-FIN-STATEMENTS | read-only Kontoauszüge | `81dda0d21170...` |
| **0.8.8-F** | **Berlin Ops Map 2** | `8119bf71a6f1...` |

---

## 📦 Release-Baseline

```text
BUNKERFREQUENZ-0.8.4-alpha.1.zip
SHA-256:
fccf16ee3728827ba4eba0dfd0e3cbaf844dd68c382b3c29c766f94a7ef85146
```

Feature-Fortschritt auf `main` ist kein stiller Produktrelease. Eine neue Produktversion braucht eine eigene Release-Iteration.

---

## 🧪 Qualitäts-Gates

```bash
PYTHONPATH=src python3 -m unittest discover -s tests/runtime -v
PYTHONPATH=src python3 -m unittest discover -s tests/presentation -v
PYTHONPATH=src:. python3 -m unittest discover -s tests/repository -v
PYTHONPATH=src python3 tools/repository_health.py
```

Normaler Mergepfad:

```text
aktueller main enthalten
        ↓
Runtime Core ✅
Presentation Core ✅
Repository Health ✅
Release Acceptance ✅
Release Package ✅
        ↓
0 Review-Threads
        ↓
/safe-merge
        ↓
SAFE MERGE PASS
```

---

## 🗂️ Schnellzugriff

| Gesucht | Datei |
|---|---|
| Maschinenstand | [`PROJEKTSTATUS.json`](PROJEKTSTATUS.json) |
| aktive Arbeit | [`TODO.md`](TODO.md) |
| Ausbauvorrat | [`FEATURE_POOL.md`](FEATURE_POOL.md) |
| Projektmanifest | [`PROJEKTMANIFEST.json`](PROJEKTMANIFEST.json) |
| Anfängerstart | [`docs/A4_FIRST_RUN_ANLEITUNG.md`](docs/A4_FIRST_RUN_ANLEITUNG.md) |
| Crew-Logo/Fahne | [`docs/LAIENHILFE_CREW_LOGO_FAHNE.md`](docs/LAIENHILFE_CREW_LOGO_FAHNE.md) |
| Scene Jobs & Bargeld | [`docs/LAIENHILFE_SCENE_JOBS.md`](docs/LAIENHILFE_SCENE_JOBS.md) |
| Bank, Sparen & Kontoauszug | [`docs/LAIENHILFE_BANK_UND_SPAREN.md`](docs/LAIENHILFE_BANK_UND_SPAREN.md) |
| Berlin-Erinnerungen | [`docs/LAIENHILFE_DISTRICT_BIO.md`](docs/LAIENHILFE_DISTRICT_BIO.md) |
| Geheimer bester Freund | [`docs/LAIENHILFE_ASSISTENT.md`](docs/LAIENHILFE_ASSISTENT.md) |
| District-Event-Vertrag | [`manifests/DISTRICT_EVENT_MANIFEST.json`](manifests/DISTRICT_EVENT_MANIFEST.json) |
| Berlin Ops Map | [`manifests/BERLIN_OPS_MAP_PRO_MANIFEST.json`](manifests/BERLIN_OPS_MAP_PRO_MANIFEST.json) |
| Safe Merge | [`docs/SAFE_MERGE.md`](docs/SAFE_MERGE.md) |

---

## 🔧 Entwicklungsregel

Eine Iteration bearbeitet eine klar begründete Zielstelle. Vor dem ersten Patch wird gemäß `AGENTS.md` eine **Planned-Read-Liste** festgelegt: nur geplante Änderungsdateien, direkte Verträge und konkret nötige Regressionen werden eingelesen. Große oder fachfremde Dateien kommen erst nach einem konkreten Befund in den Scope. Keine zweite Architektur, keine Browser-Fachlogik und keine stillen Versionssprünge. Normale PRs nach `main` werden ausschließlich über `/safe-merge` übernommen.

Details: [`AGENTS.md`](AGENTS.md) · [`docs/REPOSITORY_GUARD.md`](docs/REPOSITORY_GUARD.md) · [`docs/SAFE_MERGE.md`](docs/SAFE_MERGE.md)