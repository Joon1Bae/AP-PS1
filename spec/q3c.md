Regarding common rules, refer to q3_common.md

Signals: BMCZ = BMdec (as in q3b.md), MOMCZ = Mom12m, GPCZ = GP, all from CZ, dated τ.
A firm enters a sort only if its signal is non-missing and finite.
For BMCZ, firms with BMdec ≤ 0 should be excluded.

Formation and holdings Rules
 - annual: form at the end of June t using the signal dated June t, hold for return months
   July t … June t+1. A firm with no signal in June t should be excluded from the sample until the next June. The universe is evaluated in June t only.
 - monthly: form at the end of τ using the signal dated τ, hold for return month τ+1, and universe is evaluated at τ.

Breakpoints rules at the formation date: the 10th, 20th, …, 90th percentiles of the signal
 - NYSE: firms in the sort with PrimaryExch = N
 - general: all firms in the sort.
Decile 1 has the lowest signal, and Decile 10 has the largest signal.
A firm is in decile d if cut_{d−1} < signal ≤ cut_d (If a firm equal to a breakpoint, then it should go to the lower decile).

Weights for return month τ+1, over members with non-missing return in τ+1:
 - EW: equal weights, reset every month
 - VW: ME_τ (end of the previous month), updated every month, also within the annual holding period. A member with missing ME_τ is excluded from the VW return of τ+1.
Weights are renormalized over the members used. Excess return = portfolio return − RF_{τ+1}.

Five types: (i) VW, annual, NYSE bp rules, (ii) EW, annual, NYSE bp rules, (iii) VW, monthly, NYSE bp rules, (iv) VW, annual, general bp rules, (v) EW, monthly, general bp rules.

Sample: return months 1963:07 to 2025:01 for all five types. The last annual formation is June 2024, held for 2024:07 to 2025:01.

Output 1: five scatterplots (one per type), x = decile 1..10, y = average monthly excess return in percent, blue = BMCZ, red = MOMCZ, green = GPCZ.

Output 2: HML = decile 10 − decile 1 for each (type, signal), 15 series. Table of the mean (percent per month) and its t-statistic, from a regression of HML on a constant with Newey and West (1987, 1994) standard errors, same lag rule as q2b(v).
