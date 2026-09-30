"""Q1c: VAR-implied decomposition of Var[dp] by horizon (Equation 1.4 with the VAR 1.5).

Implements spec/q1c.md. Run from the repo root:  uv run python src/q1c.py
z_t = [dd_t, r_{e,t}, dp_t]'. One VAR step is 12 months: z at month t+12 is regressed by OLS,
equation by equation, on a constant and z at month t, over every month t with t+12 in the data.
Sigma_z solves Sigma_z = Gamma Sigma_z Gamma' + Sigma, Cov[z_{t+h}, dp_t] = Gamma^h Sigma_z e_dp,
and Var[dp] = e_dp' Sigma_z e_dp (VAR-implied). kappa is the one of Q1b (src/q1b.py).
"""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.linalg import solve_discrete_lyapunov

from q1b import plot, write_tex
from q2a import H_MAX, MONTHS_PER_H, load_eq

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"

Z = ["dg", "re", "dp"]                     # z_t = [dd_t, r_{e,t}, dp_t]'
E = {name: np.eye(3)[i] for i, name in enumerate(Z)}


def estimate_var(df: pd.DataFrame) -> dict:
    """OLS equation by equation of z_{t+12} on a constant and z_t."""
    data = pd.concat([df[Z], df[Z].shift(-MONTHS_PER_H).add_suffix("_next")], axis=1).dropna()
    X = np.column_stack([np.ones(len(data)), data[Z].to_numpy()])
    Y = data[[f"{c}_next" for c in Z]].to_numpy()
    B = np.linalg.lstsq(X, Y, rcond=None)[0]              # (1 + 3) x 3
    resid = Y - X @ B
    return {"Gamma0": B[0], "Gamma": B[1:].T, "Sigma": resid.T @ resid / (len(data) - X.shape[1]),
            "N": len(data), "first_t": data.index[0].date(), "last_t": data.index[-1].date()}


def implied_terms(Gamma: np.ndarray, Sigma: np.ndarray, kappa: float) -> pd.DataFrame:
    Sigma_z = solve_discrete_lyapunov(Gamma, Sigma)       # Sigma_z = Gamma Sigma_z Gamma' + Sigma
    assert np.allclose(Sigma_z, Gamma @ Sigma_z @ Gamma.T + Sigma)
    var_dp = E["dp"] @ Sigma_z @ E["dp"]
    cov = {h: np.linalg.matrix_power(Gamma, h) @ Sigma_z @ E["dp"] for h in range(1, H_MAX + 1)}
    rows = []
    for H in range(1, H_MAX + 1):
        b_re = sum(kappa ** (h - 1) * E["re"] @ cov[h] for h in range(1, H + 1)) / var_dp
        b_dd = -sum(kappa ** (h - 1) * E["dg"] @ cov[h] for h in range(1, H + 1)) / var_dp
        b_dp = kappa ** H * E["dp"] @ cov[H] / var_dp
        rows.append({"H": H, "b_re": b_re, "b_dd": b_dd, "b_dp": b_dp, "sum": b_re + b_dd + b_dp})
    return pd.DataFrame(rows), Sigma_z


def main() -> None:
    OUT.mkdir(exist_ok=True)
    df = load_eq()
    q1b = pd.read_csv(OUT / "q1b_coefficients.csv")
    kappa = float(q1b["kappa"].iloc[0])                    # same kappa as Q1b
    assert np.isclose(kappa, 1 / (1 + np.exp(df["dp"].mean())))
    var = estimate_var(df)
    eig = np.abs(np.linalg.eigvals(var["Gamma"]))
    assert eig.max() < 1, "VAR is not stationary"
    tab, Sigma_z = implied_terms(var["Gamma"], var["Sigma"], kappa)

    print(f"VAR sample: t = {var['first_t']} to {var['last_t']}, N = {var['N']}; kappa = {kappa:.6f}")
    print("Gamma0 =", np.round(var["Gamma0"], 4))
    print("Gamma (rows: dd, re, dp next; columns: dd, re, dp) =\n", np.round(var["Gamma"], 4))
    print("eigenvalue moduli of Gamma:", np.round(np.sort(eig)[::-1], 4))
    print(f"VAR-implied Var[dp] = {Sigma_z[2, 2]:.5f}, sample Var[dp] = {df['dp'].var():.5f}")
    print(tab.to_string(index=False, float_format=lambda v: f"{v:.4f}"))

    tab_out = tab.assign(N=var["N"])                        # write_tex expects an N column
    tab_out.to_csv(OUT / "q1c_coefficients.csv", index=False, float_format="%.6f")
    pd.DataFrame(var["Gamma"], index=[f"{c}_next" for c in Z], columns=Z).assign(
        const=var["Gamma0"]).to_csv(OUT / "q1c_var.csv", float_format="%.6f")
    write_tex(tab_out, OUT / "q1c_table.tex")

    # same y-axis range as the Q1b figure if the VAR-implied values fit inside it
    q1b_ylim = plot(q1b, OUT / "q1b_decomposition.png")
    lo, hi = tab[["b_re", "b_dd", "b_dp"]].min().min(), tab[["b_re", "b_dd", "b_dp"]].max().max()
    ylim = q1b_ylim if q1b_ylim[0] <= lo and hi <= q1b_ylim[1] else None
    print("y-axis:", "same range as Q1b" if ylim else "own range (values outside the Q1b range)")
    for ext in ("pdf", "png"):
        plot(tab, OUT / f"q1c_decomposition_var.{ext}", ylim=ylim, legend="upper right")


if __name__ == "__main__":
    main()
