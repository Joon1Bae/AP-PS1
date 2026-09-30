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