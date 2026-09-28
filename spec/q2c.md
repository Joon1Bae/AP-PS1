# Spec — Q2c: Amihud and Hurvich (2004) reduced-bias estimate of b

Student-written empirical specification (BUSFIN 8200 AI policy). The AI implements this;
substantive choices not covered here are decided by the student in the "Decisions" section.

## Student specification (verbatim, 2026-09-28)

> For the Q2C, I need to apply the method in Amihud and Hurvich (2004) to the regression model below.
>
> xR_{e, t+1} = a + b Dt/Pt + εt
>
> 1. Could you run the regression of above model? Just use the existing library for analysis.

Procedure referenced: problem set footnote 4 (regress D_{t+1}/P_{t+1} on D_t/P_t by OLS to get
theta-hat and phi-hat; phi-hat^c = phi-hat + (1/T)(1 + 3 phi-hat) + (1/T^2) 3 (1 + 3 phi-hat), with
T the total number of years in the dataset; u-hat^c_{t+1} = D_{t+1}/P_{t+1} - (theta-hat + phi-hat^c D_t/P_t);
then OLS of xR_{e,t+1} on a constant, D_t/P_t and u-hat^c_{t+1}, Equation 2.3; standard errors not required).

## Decisions (student)

Questions raised by the AI before implementing; answers recorded verbatim (2026-09-28).

1. Timing of the AR(1) regression: (a) every month t with D_{t+1}/P_{t+1} taken 12 monthly
   rows after t (overlapping; same 1117-observation sample as Q2b), or (b) one observation per
   year (non-overlapping)?
   - Answer (student, 2026-09-28): "Yes, please use option (a) (the overlapping sample of 1117 observations) so the regression sample perfectly matches Q2b and the coefficients are comparable."

2. Value of T (= n) in the bias correction of footnote 4 (number of years in the dataset).
   - Answer (student, 2026-09-28): "(However, when you calculate the bias correction $\hat{\rho}^c$ using the formula from footnote 4, you must use $n = 94$ (the number of years), not 1117. This ensures the bias correction term doesn't vanish due to artificially inflated observation counts."

3. Library: no Python library implements the Amihud-Hurvich estimator as one function; use
   statsmodels OLS for both steps plus the one-line footnote 4 formula?
   - Answer (student, 2026-09-28): "Yes. If existing python library does not have AH (2004) method, then just run OLS regression and follow the one-line footnote 4 formula."

4. Outputs and standard errors.
   - Answer (student, 2026-09-28): "Just report estimated coefficient and standard errors."
   - Which standard error. Options offered by the AI: (i) the paper's Eq. (10); (i-a) Eq. (10)
     exactly as written, with plain OLS standard errors from the two 1117-observation
     regressions; (i-b) Eq. (10) with overlap-robust ingredients (not in the paper).
     - Answer (student, 2026-09-28): "Let's go with plan c -- (i-a) and (i-b) side by side also works if you'd like to show both."
   - Estimator for (i-b):
     - Answer (student, 2026-09-28): "For the overlap-robust estimator, please use more than one of these, each as its own row: NW(1987) with 11 lags. Since the 11-month overlap is mechanically induced by the 12-month return construction, fixing the lag at 11 is theoretically more appropriate than using automatic lags."
     - Note (AI): only NW(1987) with 11 lags is named, so (i-b) is implemented with NW(11)
       only; the student was asked whether to add a Hansen-Hodrick (11 lags) row.
   - n in the factor (1 + 3/n + 9/n^2) of Eq. (10):
     - Answer (student, 2026-09-28): "For the $n$ in Eq. (10)'s factor, please use n = 94. Just as with the bias correction formula, we must use the number of independent years to ensure the variance adjustment factor properly accounts for the estimation error of $\hat{\rho}^c$ without being washed out by the overlapping months."

## Implementation (follows from the decisions above)

Notation: this section uses the paper's notation. rho is the AR(1) slope of D/P (called phi in
footnote 4); phi is the coefficient on v-hat^c in the augmented regression (b_u in Equation 2.3).

- Sample: every month t with t+12 in the data (1927:12 to 2020:12, T = 1117), as in Q2b.
- Step 1: OLS of D_{t+12}/P_{t+12} on a constant and D_t/P_t -> theta-hat, rho-hat.
  rho-hat^c = rho-hat + (1 + 3 rho-hat)/n + 3 (1 + 3 rho-hat)/n^2 with n = 94.
  v-hat^c_{t+12} = D_{t+12}/P_{t+12} - (theta-hat + rho-hat^c D_t/P_t).
- Step 2: OLS of xR_{e,t+12} on a constant, D_t/P_t and v-hat^c -> a-hat, b-hat^c, phi-hat^c (= b_u-hat).
- SE^c(b-hat^c) = sqrt( phi-hat^c^2 (1 + 3/n + 9/n^2)^2 Var-hat(rho-hat) + SE(b-hat^c)^2 ), n = 94:
  (i-a) Var-hat(rho-hat) and SE(b-hat^c) are the plain OLS values;
  (i-b) both are Newey-West (1987) with 11 lags (statsmodels HAC, Bartlett kernel, as in Q2b).

## Outputs
- `output/q2c_ah.csv` — b-hat^c, SE and t-statistic under (i-a) and (i-b); also a-hat, phi-hat^c,
  rho-hat, rho-hat^c, n, T, and the Q2b OLS b-hat for comparison.
- `output/q2c_ah_table.tex` — LaTeX table body (booktabs), same style as the Q2b table.
