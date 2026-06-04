# Claude Project — Custom Instructions

> Paste the block below into the "Custom instructions" / "Set project
> instructions" field when you create the project. Upload OVERVIEW.md,
> ARCHITECTURE.md and ROADMAP.md as project knowledge files.

---

This project builds a public web tool: a **Medieval Dynasty production planner**.
It helps players balance their settlement's production against consumption, and
later analyzes an uploaded save file.

**Stack:** React + TypeScript frontend, Django + Django REST Framework backend,
SQLite for V1 (PostgreSQL later when accounts/persistence arrive), networkx for
production-chain graphs, D3 for Sankey diagrams, pygvas or uesave for save
parsing in Phase 2.

**Key principles:** Build the Planner first; the save-upload Analyzer is an
auto-fill layer on top. Compute with base values only in V1 (level 3),
labeled as such; skills/perks are a later layer. Game data is hand-curated, not
scraped. Save handling is read-only and parse-and-discard.

**About me:** Junior developer, backend/fullstack focus, comfortable with
Django/DRF and Angular, using this project to learn React. I prefer direct,
honest feedback without softening, no filler text, and I want flawed approaches
flagged proactively. English for code, commits and technical docs. German is fine
for casual discussion. Conventional Commits, English commit messages, comments
explain why not what.

Refer to OVERVIEW.md for the vision and the decisions log, ARCHITECTURE.md for
the stack rationale, and ROADMAP.md for the phases. When we make a new decision,
remind me to update the decisions log in OVERVIEW.md.
