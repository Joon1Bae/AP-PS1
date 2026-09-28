The procedure should be the same as q2d except â_t = G_t − 1, b̂_t = G_t, where 

G_t = mean of exp(Δd_m) over m = 1928:12, …, t (monthly index m = 12, …, t with 1927:12 = 0), i.e. exactly the months whose returns xR_{e,m} enter x̄R_{e,t} at origin t.

The 1927:12 observation is excluded, as in q2d (apple to apple comparision). Δd_m is the dg column dated m.
Rationale: keep everything identical to q2d so that the only difference between the 2d and 2e forecasts is the restriction â_t = G_t − 1, b̂_t = G_t; then the change in R²_OS is attributable to that restriction alone.

Forecast: Ê^OS_t[xR_e] = (G_t − 1) + G_t · D_t/P_t, with the same origins, targets, evaluation period, and 600-month rolling windows as q2d.

Forecast plot: x̄R_{e,t}, Ê^IS_t[xR_e] (unchanged from 2b), and the 2e Ê^OS_t[xR_e], dated as in q2d. Rolling R²_OS: one figure with the q2d and q2e series overlaid.

Outputs should be identical to q2d (forecast plot, R²_OS full period, 50-year rolling R²_OS on the same axes as q2d).