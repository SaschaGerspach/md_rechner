# Medieval Dynasty Production Planner — Projektregeln

## Zuerst lesen

Die Design-Entscheidungen, das Datenmodell und die Roadmap liegen in `notes/`.
Vor Design- oder Bau-Arbeit lesen — und **nichts neu entscheiden, was dort schon
entschieden ist** (Decisions-Logs beachten):

@notes/PROJECT_INSTRUCTIONS.md
@notes/OVERVIEW.md
@notes/ARCHITECTURE.md
@notes/ROADMAP.md

(`@` zieht die Dateien fest in den Kontext jeder Session. Falls das mit der Zeit
zu viel wird, die vier Zeilen durch eine Anweisung ersetzen: „Lies `notes/*.md`
bei Bedarf.")

## Aktueller Stand

- **Konzeptphase abgeschlossen.** Vision, Architektur, Datenmodell und Rechen-
  Semantik sind durchdacht und in `notes/` dokumentiert.
- Das Modell ist gegen Testdaten als **rechnerisch korrekt nachgewiesen**
  (Demand-Balance, geteilter Pool ohne Priorität, Zyklen-Erkennung). Lauffähiger
  Beleg: `spike/calc_dryrun.py` — die vier Funktionen dort sind die Keimzelle des
  echten Calc-Moduls.
- **Noch kein Produktionscode.** Nächster Schritt: Django/DRF-Gerüst + Calc als
  sauberes Python-Modul, getestet gegen eine Platzhalter-Fixture. Klein anfangen:
  ein Gebäude, ein Endpoint, ein grüner Test. Nicht gleich alle Gebäude, nicht
  gleich das Frontend.

## Stack

- **Backend:** Django + DRF. Calc als pure Python + networkx (Graph, Topo-Sort,
  Zyklen-Erkennung). Calc läuft serverseitig — Begründung im Decisions-Log.
- **Frontend:** React + TypeScript. Bewusst als Lernziel gewählt (weniger vertraut
  als Angular). Balance als Bar-Charts, Chains als D3-Sankey.
- **DB:** SQLite in V1 (keine Accounts/Persistenz). PostgreSQL erst mit Phase 4 —
  vorher wäre es Ballast.
- **Save-Parsing (Phase 2):** pygvas oder uesave, serverseitig, read-only,
  parse-and-discard.

## Zwei Datenschichten — nie vermischen

- **Statische Spieldaten** (pro Gebäude → Stufe → Rezept): gleich für alle,
  hand-kuratiert.
- **Persönlicher Zustand** (Gebäude, Arbeiter, Population, Allokation): pro Spieler.

Form siehe `notes/ARCHITECTURE.md`. Alle Zahlenwerte sind aktuell **Platzhalter** —
die echte Quelle für den Auslieferungs-Datensatz ist noch offen (Decisions-Log).
Platzhalter dienen nur dazu, das Modell zu prüfen; sie werden nicht ausgeliefert.

## Validierung

- **Backend** (aus `backend/`, venv unter `.venv/Scripts/`):
  - Tests: `./.venv/Scripts/python.exe manage.py test`
  - System-Check: `./.venv/Scripts/python.exe manage.py check`
- **Frontend** (aus `frontend/`, Vite + React + TS, **Node ≥ 20.19 / 22.12+**
  nötig — Vite 8 ist rolldown-basiert):
  - Build (inkl. TS-Check): `npm run build`
  - Lint: `npm run lint`
  - Dev-Server: `npm run dev` (Port 5173, in Backend-CORS erlaubt)
- Noch **keine CI.** Eintragen, sobald real vorhanden.
- **Keine Befehle erfinden.** Existiert ein Script oder Target nicht, nicht danach
  raten — fehlt es, ansprechen statt halluzinieren.

## Commits

- Conventional Commits mit Scope: `type(scope): beschreibung`
  (z. B. `feat(calc): ...`, `test(api): ...`). **Englische** Commit-Messages.

## Arbeitsweise

- **Englisch** für Code, Kommentare, Commits und technische Docs. Deutsch ist fürs
  Gespräch in Ordnung.
- Kommentare erklären das **Warum**, nicht das Was.
- Code-nahe Entscheidungen als Kommentar am betroffenen Code festhalten; neue
  **Richtungs-Entscheidungen** in den Decisions-Log in `notes/OVERVIEW.md`
  eintragen (stehende Projektregel — bei jeder neuen Entscheidung daran erinnern).
- **Direktes, ehrliches Feedback ohne Weichspülen.** Fehlerhafte Ansätze proaktiv
  flaggen, *bevor* sie gebaut werden, nicht erst hinterher.

## Umgebung

- Windows. Python-venv unter `.venv/Scripts/`. Shell teils Git Bash (`/c/...`-
  Pfade), teils PowerShell.
