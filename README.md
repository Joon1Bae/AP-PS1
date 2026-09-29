# BUSFIN 8200 — Problem Set 1

Author: Joon1Bae

## Reproduce

```
uv sync                         # creates .venv with pinned dependencies (uv.lock)
uv run python src/<script>.py   # regenerates output/ from data/
cd tex && latexmk -pdf ps1_solution.tex   # or: cd tex && tectonic ps1_solution.tex
```

## Contents

| Path | What |
|---|---|
| `ps1.pdf` | Problem set statement |
| `data/eq.csv` | Monthly equity data (1927.12–): `dp`, `dg`, `rf`, `re` (course-provided, originally `EQ Dataset.csv`) |
| `data/bond.csv` | CRSP Treasury data (course-provided, originally `Bond Dataset.csv`) |
| `spec/` | Student-written empirical specifications, one per data question |
| `src/` | Python scripts implementing the specifications |
| `output/` | Figures and tables used by the LaTeX solution |
| `tex/` | LaTeX source and compiled PDF of the solution |
| `AI_INTERACTIONS.md` | Append-only record of AI use (course AI policy) |
| `AI_USAGE.md` | Final AI usage summary (created after completion) |
