Regarding common rule, you can refer to q3_common.md.

CCM link: keep linktype isin {LC, LU}, linkprim ∈ {P, C}, datadate within [linkdt, linkenddt].

Fiscal year: BM of year t uses the accounting record with year(datadate) = t−1. If a PERMNO has
several records with datadate in the same calendar year, keep linkprim = P over C, then the
latest datadate.

BE = SE + TXDITC − BVPS, with SE = seq, else ceq + pstk, else at − lt; TXDITC = txditc, else 0;
BVPS = pstkrv, else pstkl, else pstk, else 0. If SE is unavailable, BE is missing. Keep BE > 0.

ME = |MthPrc|·ShrOut of the linked PERMNO in December of year t−1, from crsp_msf regardless of
the universe in that month. If there is no December row or ME is missing, BM is missing.

Units: BE is in $ millions and ME in $ thousands, so BM_t = 1000·BE/ME.

History requirement: the record used must be preceded by at least two earlier records (distinct
datadates) of the same gvkey in ccm_funda.csv.gz. The file contains only records inside the link
window, so years before the link are not counted.

BM_t is assigned to months June t … May t+1 for the linked PERMNO; first t = 1963, last t = 2024
(months 2024:06 to 2024:12). Universe filter applied at τ.

Validation: BMCZ is CZ's book-to-market ratio in levels. The problem statement writes
BMCZ = exp(BMdec) because it takes BMdec to be a log; in this CZ release BMdec is already the
raw BE/ME ratio (see data/README.md), so BMCZ = BMdec. Merged on (permno, yyyymm = τ). For each
month τ, cross-firm OLS of BMCZ on a constant and my BM, in levels, using firms in the universe
at τ with both non-missing; record intercept, slope, R² (unadjusted), N.

Output: three time-series figures (intercept, slope, R²).


Please use only Compustat records with curcd = USD