Data (all in data/ directory):
 - crsp_msf.csv.gz: PERMNO, MthCalDt, MthRet, MthRetFlg, MthPrc, ShrOut, SICCD, PrimaryExch, ConditionalType, TradingStatusFlg, ShareType, SecurityType, SecuritySubType, USIncFlg, IssuerType, SecInfoStartDt, SecInfoEndDt, etc
 - ccm_funda.csv.gz: gvkey, lpermno, datadate, fyear, seq, ceq, pstk, at, lt, txditc, pstkrv, pstkl, linktype, linkprim, linkdt, linkenddt, etc
 - cz_signals.csv.gz: permno, yyyymm, Mom12m, BMdec, GP
 - dur_firmlevel_updated2025.csv: PERMNO, FF.YEAR, Dur
 - ff3_monthly.csv: RF (percent → divide by 100)


Time index τ = calendar month.

Dates: first signal month [1963:06], first return month [1963:07], last signal month [2024:12], and last return month [2025:01].
The same window applys for Q3a–Q3e, but any calculation using Dur should start at signal month [1973:06] (return month will be [1973:07]).

Universe (applied every month): ShareType = NS, SecurityType = EQTY, SecuritySubType = COM, USIncFlg = Y, IssuerType isin {ACOR, CORP}, PrimaryExch isin {N, A, Q}, ConditionalType = RW, TradingStatusFlg = A, and please exclude 4900 ≤ SIC ≤ 4949 and 6000 ≤ SIC ≤ 6999. And should be applied at the signal/formation month τ only.

SIC = SICCD at τ. SICCD = 0 means missing. 9999 is a valid code. If missing, use the same PERMNO's most recent earlier non-zero SICCD, else its next later one; if the PERMNO never has a non-zero SICCD, keep the firm (no SIC exclusion applies).

Returns: MthRet in decimals, as provided. If MthRet in τ+1 is missing or the PERMNO has no row in τ+1, the stock should be excluded from that month's calculations, with portfolio weights renormalized over members with returns.


ME_τ = |MthPrc|·ShrOut (ShrOut in thousands, so ME in $ thousands). If MthPrc or ShrOut is missing at τ, ME_τ is missing and the firm-month is excluded from the universe at τ.


xR_{j,τ+1} = ret_{j,τ+1} − RF_{τ+1}.

CZ timing: a row with yyyymm = τ holds signals observed at the end of τ and should be merged on (permno, τ) with my signals dated τ. The signal predicts the return in τ+1.

Rule: if any step needs a choice not written here, stop and ask!

Row selection: crsp_msf has several rows per PERMNO-month. First drop the Dis* columns and exact duplicate rows.

Security info (all universe fields and SICCD) at month τ: use the row with SecInfoStartDt ≤ MthCalDt ≤ SecInfoEndDt. If a PERMNO-month has two rows, keep the one satisfying this condition. If no row satisfies it (delisting months that carry only post-delisting security info), the PERMNO fails the universe in that month.

Return and price data (MthRet, MthPrc, ShrOut) are identical across the rows of a PERMNO-month and are taken from the PERMNO-month regardless of the condition above, so the return in τ+1 is kept when τ+1 is the delisting month.

The search for the earlier or later non-zero SICCD uses all rows of the same PERMNO with valid
security info over the whole file (1960:01–2025:12), regardless of the universe screens and the
sample window. A code filled from a later month is dated after τ. This could be accepted because SIC
only defines the sample and is not a signal.