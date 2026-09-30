Data
- data/eq.csv

Variables
- dp_t
- \delta d_t = dg
- r_{e,t} = re.

κ = 1/(1 + e^{dp̄}), where dp̄ = full-sample average of dp.
Compute once and keep it safe for using the same κ for every H (You don't have to recompute on each H's subsample).

For each H = 1, ..., 15,

compute the following variables
  - A_t = \Sigma_{h=1}^H κ^{h−1} r_{e,t+12h}
  - B_t = −\Sigma_{h=1}^H κ^{h−1} \delta d_{t+12h}
  - C_t = κ^H dp_{t+12H}

and the OLS slopes of A, B, C onto dp_t.

Output should be figure (H on x-axis, three terms should have different colors on it), table (for each H terms, coefficients, their summation, and Num. of Obs.)

Your questions have been answered
- "The spec says 'OLS slopes of A, B, C onto dp_t' but not whether the regressions include a constant. With a constant, the slope equals Cov(dp, ·)/Var(dp) on the sample, the form of Equation 1.4; without one it does not. Which regression do you want?"="With a constant"

- "The spec doesn't state the estimation sample for each H. Which months t should enter?"="All t with t+12H in data"