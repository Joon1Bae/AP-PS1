Regarding common rule, you can refer to q3_common.md.

MOM_{j,τ} = \Pi_{m=τ−11}^{τ−1}(1+ret_{j,m}) − 1 (the cumulative return from the end of month τ−12 to the end of month τ−1 (footnote 6), using the 11 monthly returns of calendar months τ−11 to τ−1).

ret = MthRet as in q3_common.md.

Returns in the window are taken from crsp_msf for the same PERMNO regardless of whether the firm passes the universe in those months, including months before 1963:06. All 11 monthly returns must be non-missing. A calendar month with missing MthRet or with no row makes MOM_{j,τ} missing.

Universe filter applied at τ. Signal months as in q3_common.md (1963:06 to 2024:12).

Validation: MOMCZ = Mom12m, merged on (permno, yyyymm = τ). For each month τ, cross-firm OLS of MOMCZ on a constant and my MOM using firms in the universe at τ with both non-missing.
And pleaase record intercept, slope, R² (unadjusted), N (# of obs.).

Output: three time-series figures (intercept, slope, R²), and a table with the time-series mean, minimum and maximum of the intercept, slope, R² and N.
