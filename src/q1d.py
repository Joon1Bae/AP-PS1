"""Q1d: infinite-horizon decomposition b_re^(inf), b_dd^(inf) from the VAR of Q1c.

Implements spec/q1d.md. Run from the repo root:  uv run python src/q1d.py
With Gamma, Sigma_z and kappa of Q1c (src/q1c.py) and the VAR-implied Var[dp] = e_dp' Sigma_z e_dp,
    b_re^(inf) =  e_r'  Gamma (I - kappa Gamma)^{-1} Sigma_z e_dp / Var[dp]
    b_dd^(inf) = -e_dd' Gamma (I - kappa Gamma)^{-1} Sigma_z e_dp / Var[dp],
using sum_{h>=1} kappa^{h-1} Gamma^h = Gamma (I - kappa Gamma)^{-1}, valid when all eigenvalues of
kappa Gamma lie inside the unit circle (checked and reported).
"""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.linalg import solve_discrete_lyapunov

from q1c import E, estimate_var
from q2a import load_eq

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"

MACROS = {"b_re": "bReInf", "b_dd": "bDdInf", "sum": "bSumInf", "max_eig": "kappaGammaMaxEig"}


def infinite_horizon(Gamma: np.ndarray, Sigma: np.ndarray, kappa: float) -> dict:
    max_eig = np.abs(np.linalg.eigvals(kappa * Gamma)).max()
    assert max_eig < 1, "sum_{h>=1} kappa^{h-1} Gamma^h does not converge"
    Sigma_z = solve_discrete_lyapunov(Gamma, Sigma)
    var_dp = E["dp"] @ Sigma_z @ E["dp"]
    cov = Gamma @ np.linalg.inv(np.eye(3) - kappa * Gamma) @ Sigma_z @ E["dp"]
    b_re, b_dd = E["re"] @ cov / var_dp, -(E["dg"] @ cov) / var_dp
    return {"b_re": b_re, "b_dd": b_dd, "sum": b_re + b_dd, "max_eig": max_eig}


def main() -> None:
    OUT.mkdir(exist_ok=True)
    df = load_eq()
    kappa = float(pd.read_csv(OUT / "q1b_coefficients.csv")["kappa"].iloc[0])      # same kappa as Q1b, Q1c
    var = estimate_var(df)
    gamma_saved = pd.read_csv(OUT / "q1c_var.csv", index_col=0)[["dg", "re", "dp"]].to_numpy()
    assert np.allclose(var["Gamma"], gamma_saved, atol=1e-6), "Gamma differs from output/q1c_var.csv"
    res = infinite_horizon(var["Gamma"], var["Sigma"], kappa)
    print(f"kappa = {kappa:.6f}, max |eig(kappa Gamma)| = {res['max_eig']:.4f}")
    print(f"b_re(inf) = {res['b_re']:.4f}, b_dd(inf) = {res['b_dd']:.4f}, sum = {res['sum']:.4f}")
    pd.Series(res).to_frame("value").to_csv(OUT / "q1d_values.csv", float_format="%.6f")
    lines = [f"\\newcommand{{\\{MACROS[k]}}}{{{res[k]:.3f}}}" for k in MACROS]
    (OUT / "q1d_values.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
