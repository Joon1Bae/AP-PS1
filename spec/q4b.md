xr_{t→t+H} = Σ_{h=1}^H xr^{(H−h+1)}_{t+12h} (h=H term is xr^(1) = 0).

Regress (1/H)·xr_{t→t+H} on constant and xy^(H)_t.

t-stats should be calculated following Hansen and Hodrick (1980), as defined in Footnote 3, i.e. w_l = 1 for all l and L = overlap = 12H − 1 months.

Output should be a table with b, t(b), R^2 for H=2..5.

Table layout (slide 4.5): columns H = 2, 3, 4, 5 years and rows b^(H) with the t-statistic in brackets and R^2 in percent with one decimal.
You don't have to report the intercept or N in the table as in slide 4.5.

Every t whose non-zero terms are observed, i.e. t + 12(H−1) ≤ 2024:12.