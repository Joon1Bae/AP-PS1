Regarding common rules, refer to q3_common.md file.

Signals at τ
- BMCZ = BMdec and GPCZ = GP from CZ (as in q3c.md), and Dur.
- A signal should be non-missing and finite. 
- For BMCZ, firms with BMdec ≤ 0 should be excluded.

Dur alignment
- Dur with FF.YEAR = t should be the signal for months τ from June t to May t+1, which matches with the BM timing.

Quantile
- Q^X_{j,τ} = rank of X_{j,τ} divided by N, where the rank (1 = lowest, average rank for
ties) and N are taken over all firms in the universe at τ with a valid X, whether or not they
enter the regression. X isin {BMCZ, GPCZ, Dur}.

Each month τ esimates the following regression models (use both OLS and WLS):

(i) xR_{j, τ+1} = a + b_{BM}Q^BM_{j, τ} + epsilon_{j, τ+1}
(ii) xR_{j, τ+1} = a + b_{GP}Q^GP_{j, τ} + epsilon_{j, τ+1}
(iii) xR_{j, τ+1} = a + b_{Dur}Q^Dur_{j, τ} + epsilon_{j, τ+1}
(iv) xR_{j, τ+1} = a + b_{BM}Q^BM_{j, τ} + b_{GP}Q^Dur_{j, τ} + epsilon_{j, τ+1}
(v) xR_{j, τ+1} = a + b_{Dur}Q^Dur_{j, τ} + b_{BM}Q^BM_{j, τ} + epsilon_{j, τ+1}
(vi) xR_{j, τ+1} = a + b_{Dur}Q^Dur_{j, τ} + b_{GP}Q^GP_{j, τ} + epsilon_{j, τ+1}
(vii) xR_{j, τ+1} = a + b_{Dur}Q^Dur_{j, τ} + b_{GP}Q^GP_{j, τ} + b_{BM}Q^BM_{j, τ} + epsilon_{j, τ+1}


Firms in the universe at τ with all regressors of that spec should be valid and xR_{j,τ+1} should be non-missing.

Window
- Signal months 1963:06 to 2024:12 for specs (i), (ii), (iv).
- Signal months 1973:06 to 2024:12 for specs (iii), (v), (vi), (vii) (Sample use Dur because it starts at 1973)

Fama–MacBeth estimate = time-series mean of the monthly cross-section coefficients etimates.
t-statistic from a regression of the monthly coefficient series on a constant with Newey and West (1987, 1994) standard errors, same lag rule as q2b(v).

Output should be table, rows = specs (i)–(vii) × {OLS, WLS}, columns = a, b_BM, b_GP, b_Dur, each with its t-statistic, plus the average N and the number of months.
xR is in percent per month, so a coefficient is the difference in percent per month between the highest and the lowest quantile.
