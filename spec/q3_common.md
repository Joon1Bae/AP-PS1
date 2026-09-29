Data (all in data/ directory):
 - crsp_msf.csv.gz: permno, date, ret, dlret, prc, shrout, shrcd, exchcd, siccd, etc
 - ccm_funda.csv.gz: gvkey, lpermno, datadate, fyear, seq, ceq, pstk, at, lt, txditc, pstkrv, pstkl, linktype, linkprim, linkdt, linkenddt, etc
 - cz_signals.csv.gz: permno, yyyymm, Mom12m, BMdec, GP
 - dur_firmlevel_updated2025.csv: PERMNO, FF.YEAR, Dur
 - ff3_monthly.csv: RF (percent → divide by 100)


Time index τ = calendar month.

Sample should span from June 1963 to last month common to the data.

Universe (applied every month): shrcd isin {10,11}, exchcd isin {1,2,3}, exclude 4900 <= SIC <= 4949 and 6000 <= SIC <= 6999, SIC taken from CRSP siccd at month τ (if not available, then use Compustat sic and then CRSP hsiccd order).

Returns: ret in decimals

delisting should be handled in a compound way that ret = (1+ret)(1+dlret)−1.
If ret is missing, use dlret instead.

ME_τ = |prc|·shrout (shrout in thousands, so ME in $ thousands).

If prc or shrout is missing, ME_τ is missing.
The firm-month is kept for return-based calculations but excluded from value weights and WLS weights.

xR_{j,τ+1} = ret_{j,τ+1} − RF_{τ+1}.

CZ timing: a row with yyyymm = τ holds signals observed at the end of τ and should be merged on (permno, τ) with my signals dated τ. The signal predicts the return in τ+1.

Rule: if any step needs a choice not written here, stop and ask!