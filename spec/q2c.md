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

## Decisions (student) — PENDING, to be answered before implementation

1. Timing of the AR(1) regression: is D_{t+1}/P_{t+1} the observation 12 monthly rows after t
   (as for xR_{e,t+1} in Q2b), using all overlapping monthly observations?
   - Answer: (pending)
2. Value of T in the bias correction ("total number of years in the dataset", footnote 4):
   which count should be used? For reference, the Q2b estimation sample has 1117 monthly
   observations with predictor dates 1927:12 to 2020:12, and the data file spans 1927:12 to 2021:12.
   - Answer: (pending)
3. Library: no standard Python library implements the Amihud-Hurvich estimator as a single
   function. Is it acceptable to run both OLS steps with `statsmodels` and compute phi-hat^c
   with the one-line formula from footnote 4?
   - Answer: (pending)
4. Outputs: which numbers should be reported (e.g. b-hat from Equation 2.3 next to the Q2b OLS
   b-hat; also phi-hat, phi-hat^c, b_u-hat, T)? Table in LaTeX, CSV, or both?
   - Answer: (pending)
