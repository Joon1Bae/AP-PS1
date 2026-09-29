Regarding common rules, refer to q3_common.md.

Signals
- BMCZ = BMdec and GPCZ = GP from CZ, and Dur, with the validity rules as in q3c.md (non-missing, finite, BMdec > 0).
- Dur with FF.YEAR = t is the signal dated June t.

Portfolios
- Decile portfolios of q3c.md type (i) (VW, annual, NYSE bp rules) and type (ii) (EW, annual, NYSE bp rules), for BMCZ and GPCZ
- Dur decile portfolios are built here with the same rules, sorted at the end of June t on Dur with FF.YEAR = t which gives 30 portfolios per weighting (10 portfolios per each feature).

Firm deciles
- For each signal X, a firm's decile in X is its decile from the annual NYSE sort on X at June t, fixed for return months July t … June t+1.

Portfolio regressor
- For portfolio p and return month τ+1, Dec^X_{p,τ} is the average of the firm deciles in X over the members used for the return of τ+1 that have a decile in X, with the same weights as the portfolio return (ME_τ for VW, equal for EW), renormalized over those members.
- For the signal the portfolio is sorted on, Dec^X_{p,τ} equals its own decile.

Panel
- For each spec (i)–(vii), stack xR_{p,τ+1} of the portfolios sorted on the signals in that spec: 10 portfolios for (i)–(iii), 20 for (iv)–(vi), 30 for (vii).
- Regress xR_{p,τ+1} on a constant and the Dec's of that spec.

(i) xR_{p, τ+1} = a + b_{BM}Dec^BM_{p, τ} + epsilon_{p, τ+1}
(ii) xR_{p, τ+1} = a + b_{GP}Dec^GP_{p, τ} + epsilon_{p, τ+1}
(iii) xR_{p, τ+1} = a + b_{Dur}Dec^Dur_{p, τ} + epsilon_{p, τ+1}
(iv) xR_{p, τ+1} = a + b_{BM}Dec^BM_{p, τ} + b_{GP}Dec^GP_{p, τ} + epsilon_{p, τ+1}
(v) xR_{p, τ+1} = a + b_{Dur}Dec^Dur_{p, τ} + b_{BM}Dec^BM_{p, τ} + epsilon_{p, τ+1}
(vi) xR_{p, τ+1} = a + b_{Dur}Dec^Dur_{p, τ} + b_{GP}Dec^GP_{p, τ} + epsilon_{p, τ+1}
(vii) xR_{p, τ+1} = a + b_{Dur}Dec^Dur_{p, τ} + b_{GP}Dec^GP_{p, τ} + b_{BM}Dec^BM_{p, τ} + epsilon_{p, τ+1}

Window
- return months 1963:07 to 2025:01 for specs (i), (ii), (iv)
- return months 1973:07 to 2025:01 for specs (iii), (v), (vi), (vii) (the sample use Dur).

Estimation
- Pooled OLS
- Standard errors should be Driscoll and Kraay (1998) with the Bartlett kernel
- The lag is chosen by the Newey and West (1994) rule of q2b(v), which is applied to the moment series summed across portfolios within each month.

Run once for the VW portfolios and once for the EW portfolios.

Output should be the table analogous to q3d, one panel per weighting, rows = specs (i)–(vii), columns = a, b_BM, b_GP, b_Dur, each with its t-statistic, plus the number of portfolios and of months.
xR is in percent per month, so a coefficient should be percent per month per decile.
