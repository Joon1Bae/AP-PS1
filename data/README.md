# Data

Both CSV files are provided by the course and are committed to this repository so that the
results can be reproduced from the repository alone.

| File | Original name | Contents |
|---|---|---|
| `eq.csv` | EQ Dataset.csv | Monthly observations (1927:12 to 2021:12) of annual variables: `dp` (log dividend-price ratio), `dg` (log annual dividend growth), `rf` (log annual deflated risk-free return), `re` (log annual deflated equity market return). Excess returns are constructed in the code as e^re - e^rf. See `ps1.pdf` for the definitions. |
| `bond.csv` | Bond Dataset.csv | CRSP Treasury series; the Fama-Bliss discount bond yields (1- to 5-year, `TTERMTYPE` 5001 to 5005, 1952:06 to 2024:12) are the ones used in Question 4. |
