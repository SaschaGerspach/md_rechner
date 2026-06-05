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

**Phase 1 (MVP Planner) im Kern umgesetzt.** Monorepo mit `backend/` + `frontend/`.

- **Backend (Django + DRF, `backend/`):** Calc als pures Python-Modul
  (`planner/calc.py`: `validate` + `compute_balance`, Demand-Balance inkl.
  Bewohner-Verbrauch). Chain-Graph via networkx (`planner/graph.py`: Topo-Sort +
  Zyklen-Erkennung). Statik-Schicht in `planner/data.py` (Gebäude + Bewohner-
  Verbrauch). Endpoints: `POST /api/balance/`, `GET /api/buildings/`,
  `GET /api/chain/`. 10 grüne Tests.
- **Frontend (React + TS + Vite, `frontend/`):** Planner-Formular (Population +
  dynamische Gebäudeliste aus `/api/buildings/`), Balance-Tabelle, Produktions-
  kette als D3-Sankey (`ChainView.tsx`). CORS im Backend für den Dev-Origin.
- **Container:** Backend containerisiert mit Dev/Prod-Parität (Gunicorn als
  Prod-Default, runserver-Override für Dev mit Auto-Reload), SQLite im named
  volume. Siehe `backend/Dockerfile` + `docker-compose*.yml`.
- **Spieldaten:** 8 echte MD-Gebäude im Katalog, **Rezepte/Raten aber noch
  Platzhalter** (Baukosten sind kein Modell-Bestandteil). Datenquelle inzwischen
  geklärt (MD-Manager-Extrakt, siehe „Spieldaten-Quelle"); offen ist die
  Kuratierung der echten Daten ins Schema.
- **Beleg/Keimzelle:** `spike/calc_dryrun.py` (Demand-Balance, geteilter Pool
  ohne Priorität, Zyklen-Erkennung) — diente als Vorlage für das Calc-Modul.

Offene nächste Schritte: echte Rezepte aus dem Extrakt ins Schema kuratieren,
Styling-Durchgang, settlement-gewichtete Sankey (Kantenbreite = Einheiten/Tag).

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

Form siehe `notes/ARCHITECTURE.md`. Der aktuelle Katalog nutzt **Platzhalter**-
Rezepte/Raten, nur zum Modell-Prüfen — nicht ausliefern. Die Quelle für den echten
Datensatz ist inzwischen geklärt (siehe „Spieldaten-Quelle").

## Spieldaten-Quelle (Kuratierung)

Kuratierungs-Quelle für die statische Schicht: `notes/md_manager_extract.json` —
**Rohmaterial, NICHT der auslieferbare Datensatz.** Per Pfad referenziert, nicht
`@`-importiert (≈200 KB; nur lesen, wenn an den Daten gearbeitet wird).

Extrahiert aus MD Manager v1.3 (Xarmo / r00t @ Toplitz Discord, Nexus mod 25);
Lizenz erlaubt Nachnutzung **mit Quellenangabe** — Attribution erhalten.

Verlässlich enthalten (≈378 Prozesse, 22 Gebäude): Gebäude, Rezept-Inputs,
Nebenprodukte (`byproducts`), Werkzeug-Verschleiß, Wirtschaftsdaten; plus
Item-Liste mit Food/Water/Wood-Verbrauchswerten (Bewohner-Bedarf). **NICHT**
enthalten:
- **Tagesraten** (`output_per_day_at_100`) — im Spiel bei Skill 3 messen.
- **Gebäudestufen / max_workers** — separat kuratieren (z. B. Nähhütte 1/1/2).
- **Projekt-IDs** — Quelle nutzt Anzeigenamen („Sewinghut", „Flax Stalk"), auf
  snake_case-IDs mappen.

Werte zielen auf die MD-Manager-v1.3-Spielversion — vor dem Ausliefern gegen das
aktuelle Spiel prüfen. Das echte Fixture aus dieser Quelle kuratieren (Schema in
`notes/ARCHITECTURE.md`); diese Werte nie unverifiziert ausliefern. Feld-Prozesse
(`production_day_flag: 1`) sind in V1 keine Produzenten — beim Mappen weglassen.

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
