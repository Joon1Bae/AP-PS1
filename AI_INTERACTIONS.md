# AI_INTERACTIONS.md — BUSFIN 8200 Problem Set 1

Contemporaneous record of every substantive AI interaction on this problem set, created by the
`/TP` skill (see `.claude/skills/TP/SKILL.md`). Entries are **append-only**: nothing below is ever
edited, deleted, or merged. Corrections are made by adding a new entry.

Environment: VS Code + Claude Code (Anthropic), workspace = this repository.

## Interaction 1 — General (document skeleton) — 2026-09-11 15:16

- **Problem set item:** General — LaTeX solution document skeleton covering Q1–Q4 (no answer content)
- **Substantive prompt (verbatim):** "Could you write down the LaTeX codes just for skelton? Let's make one by one with me."
- **Purpose:** Create an empty, compilable LaTeX template for the solution PDF so that answers to each sub-question can be added one at a time.
- **Git commit before:** e875adf39cdfad9fbfeacdf4b824af0698b0727d
- **Assistance provided:** Wrote `tex/ps1_solution.tex` containing only a preamble (packages, notation macros, title), one `\section` per question and one `\subsection` per sub-item (Q1a–Q1e, Q2a–Q2e, Q3a–Q3e, Q4a–Q4e), and commented `% TODO` placeholders describing the deliverable of each sub-item as stated in `ps1.pdf`, plus commented figure/table include stubs pointing to `output/`. No derivations, reasoning, results, or interpretation were written. Removed the `tex/.gitkeep` placeholder. Renamed the `\dp` macro to `\dpr` because `\dp` is a TeX primitive and would fail to compile. No TeX engine is installed on this machine, so the file has not been compiled.
- **Files inspected:** ps1.pdf (text extraction), README.md, CLAUDE.md, .claude/skills/TP/SKILL.md, data/README.md, data/eq.csv (head/tail), data/bond.csv (series labels, date range), pyproject.toml, .gitignore
- **Files directly modified by AI:** tex/ps1_solution.tex (created); tex/.gitkeep (deleted)
- **Errors, omissions, or ambiguities identified:** (1) No LaTeX distribution available locally, so compilation is unverified. (2) `data/README.md` states the CSVs are not committed, but they are tracked and `.gitignore` does not exclude them; the note is also in Korean.
- **Substantive mathematical / economic / empirical suggestions made:** none
- **Type of assistance:** formatting/translation (LaTeX template only); other (repository survey)
- **Grouped follow-up requests:** none
- **Git commit after:** <pending>
