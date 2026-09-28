# Spec — Q2a: adjusted R^2 of horizon-H predictive regressions

Student-written empirical specification (BUSFIN 8200 AI policy). The AI implements this;
substantive choices not covered here are decided by the student in the "Decisions" section.

## Student specification (verbatim, 2026-09-28)

> 1. from the eq.csv dataset, construct pandas dataframe.
> 2. take exponential on (1) dp, (2) re, (3) rf
> 3. by substracting e^re - e^rf,, calculate xRe,t
> 4. for h in range(1, 15):, regress 1/H \Sigma^H_{h=1}xR_e,t+h onto e^dp, and calculate R^2_adj.
> 5. plot a graph where x axis is H and y axis is R^2_adj for each H.

## Decisions (student)

Questions raised by the AI before implementing steps 4–5; answers recorded verbatim.

1. Horizon range: `range(1, 15)` gives H = 1, ..., 14, while the problem statement asks for
   H = 1, ..., 15. Which is intended?
   - Answer (student, 2026-09-28): "H = 1, ..., 15"

2. Time step of h: the data are monthly observations of annual variables. Is xR_{e,t+h}
   the observation 12*h months after month t (so H years = 12H rows)?
   - Answer (student, 2026-09-28): "12 months per h"

3. Estimation sample per H: use every month t for which t+12H is in the data (sample
   shrinks as H grows), or a common sample across all H (t restricted so that t+12*H_max
   is in the data)?
   - Answer (student, 2026-09-28): "All available per H" (every t with t+12H in the data;
     the sample shrinks as H grows)


## Outputs
- `output/q2a_r2adj.csv` — H and R^2_adj (one row per H)
- `output/q2a_r2adj.pdf` — line/marker plot, x = H, y = R^2_adj
