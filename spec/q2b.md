# Spec — Q2b: one-year predictive regression with five standard-error methods

Student-written empirical specification (BUSFIN 8200 AI policy). The AI implements this;
substantive choices not covered here are decided by the student in the "Decisions" section.

## Student specification (verbatim, 2026-09-28)

> the step is as follows:
>
> 1. the regression spec is as follows:
> xR_{e, t+1} = a + b * D_t/P_t + epsilon_t
>
> 2. estimate the coefficient a, b
>
> 3. calculate 5 different the standard errors as below:
>
> (i) OLS standard erros
> (ii) The White (1980) standards errors
> (iii) The Newey and West (1987) standard erros with 11 lags
> (iv) The Hansen and Hodrick (1980) standard errors with 11 lags
> (v) The Newey and West (1987, 1994) standard errors
>
> 4. Do not write the codes from the scratch. Just use existing library for each standard error calcultion.

## Decisions (student)

1. Variable definitions and timing: as in `spec/q2a.md` for the same regression
   (Equation 2.2 of the problem set is the H = 1 case of Equation 2.1):
   xR_{e,t} = e^{re_t} - e^{rf_t}, D_t/P_t = e^{dp_t}, and t+1 is 12 monthly rows after t
   (problem set footnote 3: "H = 12 in our case"). Carried over from the student's Q2a
   decision "12 months per h"; the student may override here.
   - Answer: (carried over from spec/q2a.md unless the student objects)
2. Estimation sample: every month t with t+12 in the data (1927:12 to 2020:12), carried over
   from the student's Q2a decision "All available per H".
   - Answer: (carried over from spec/q2a.md unless the student objects)

## Implementation notes (AI, programming choices under step 4 "use existing library")

- (i)-(iv) via `statsmodels` OLS covariance options: (i) nonrobust; (ii) `HC0`, which is the
  1/T sum of e^2 x x' form in footnote 3; (iii) `HAC` with `maxlags=11`, Bartlett kernel
  (weights 1 - l/(L+1)); (iv) `HAC` with `maxlags=11`, uniform kernel (weights 1), i.e.
  Hansen-Hodrick.
- (v) via `linearmodels` kernel (Bartlett) covariance with automatic bandwidth, which
  implements the Newey-West (1994) plug-in bandwidth (their eq. 2.2, rate T^{1/3}).
- Library detail to be aware of: statsmodels' HAC divides every autocovariance term by T,
  whereas footnote 3 writes 1/(T - l) for lag l. The difference is a finite-sample scaling
  of order l/T; the student instructed the AI to use existing libraries rather than
  re-implement the footnote formulas.

## Outputs
- `output/q2b_se_table.csv` — a-hat, b-hat, and for each of the five methods the SE and
  t-statistic of b-hat (and of a-hat), plus the number of lags used.
- `output/q2b_se_table.tex` — LaTeX table body (booktabs) included by `tex/ps1_solution.tex`.
