"""Q2c: Amihud and Hurvich (2004) reduced-bias estimate of b in xR_{e,t+1} = a + b * D_t/P_t + e_t.

Implements spec/q2c.md. Run from the repo root:  uv run python src/q2c.py
Notation follows the paper: rho is the AR(1) slope of D/P (phi in problem set footnote 4) and
phi is the coefficient on the corrected AR residual v^c (b_u in Equation 2.3).
Both regressions are statsmodels OLS; the bias correction and Eq. (10) are one-line formulas.
"""
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

from q2a import add_levels, load_eq
from q2b import FIXED_LAGS, LEAD_MONTHS, build_sample

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"

N_YEARS = 94   # n in the rho^c correction and in the Eq. (10) factor (spec/q2c.md, decisions 2 and 4)


def build_ah_sample(df: pd.DataFrame) -> pd.DataFrame:
    """Q2b sample (y = xR_{t+12}, DP = D_t/P_t) plus DP_next = D_{t+12}/P_{t+12} (decision 1)."""
    data = build_sample(df)
    data["DP_next"] = df["DP"].shift(-LEAD_MONTHS).reindex(data.index)
    return data.dropna()


def fit_pair(y: pd.Series, X: pd.DataFrame):
    """The same OLS fit with (i-a) plain OLS and (i-b) Newey-West (1987), 11 lags, covariances."""
    model = sm.OLS(y, X)
    return {
        "ols": model.fit(cov_type="nonrobust"),
        "nw11": model.fit(cov_type="HAC", cov_kwds={"maxlags": FIXED_LAGS, "kernel": "bartlett"}),
    }


def amihud_hurvich(data: pd.DataFrame, n: int = N_YEARS) -> dict:
    # Step 1: AR(1) of D/P at the 12-month horizon, then the second-order bias correction (Eq. 7).
    ar = fit_pair(data["DP_next"], sm.add_constant(data["DP"]))
    theta, rho = ar["ols"].params["const"], ar["ols"].params["DP"]
    rho_c = rho + (1 + 3 * rho) / n + 3 * (1 + 3 * rho) / n**2
    v_c = data["DP_next"] - (theta + rho_c * data["DP"])

    # Step 2: augmented regression (Equation 2.3).
    X = sm.add_constant(pd.DataFrame({"DP": data["DP"], "v_c": v_c}))
    aug = fit_pair(data["y"], X)
    b_c, phi_c = aug["ols"].params["DP"], aug["ols"].params["v_c"]

    # Eq. (10): SE^c = sqrt(phi_c^2 * (1 + 3/n + 9/n^2)^2 * Var(rho) + SE(b_c)^2).
    factor = (1 + 3 / n + 9 / n**2) ** 2
    se_c = {k: np.sqrt(phi_c**2 * factor * ar[k].bse["DP"] ** 2 + aug[k].bse["DP"] ** 2)
            for k in ("ols", "nw11")}

    # Check of Theorem 3: b_c = b_ols + phi_s * (rho_c - rho), phi_s from the two OLS residual series.
    b_ols_fit = sm.OLS(data["y"], sm.add_constant(data["DP"])).fit()
    u_hat, v_hat = b_ols_fit.resid, ar["ols"].resid
    phi_s = (u_hat * v_hat).sum() / (v_hat**2).sum()
    theorem3_gap = abs(b_c - (b_ols_fit.params["DP"] + phi_s * (rho_c - rho)))

    return {"a": aug["ols"].params["const"], "b_c": b_c, "phi_c": phi_c, "theta": theta,
            "rho": rho, "rho_c": rho_c, "se_c": se_c, "b_ols": b_ols_fit.params["DP"],
            "n": n, "T": int(aug["ols"].nobs), "theorem3_gap": theorem3_gap}


def to_table(r: dict) -> pd.DataFrame:
    names = {"ols": "(i-a) Eq. (10), OLS ingredients",
             "nw11": "(i-b) Eq. (10), Newey-West (1987) 11 lags ingredients"}
    rows = [{"method": names[k], "b_c": r["b_c"], "se_b_c": r["se_c"][k],
             "t_b_c": r["b_c"] / r["se_c"][k]} for k in ("ols", "nw11")]
    tab = pd.DataFrame(rows).set_index("method")
    for key in ("a", "phi_c", "rho", "rho_c", "b_ols", "n", "T"):
        tab[key] = r[key]
    return tab


def write_tex(r: dict, tab: pd.DataFrame, path: Path) -> None:
    r"""LaTeX tabular body (booktabs), same layout as output/q2b_se_table.tex."""
    lines = [
        r"\begin{tabular}{lcc}",
        r"\toprule",
        r"Standard error of $\hat b^c$ & SE$(\hat b^c)$ & $t(\hat b^c)$ \\",
        r"\midrule",
    ]
    for name, row in tab.iterrows():
        lines.append(f"{name} & {row['se_b_c']:.4f} & {row['t_b_c']:.2f} \\\\")
    lines += [
        r"\midrule",
        rf"\multicolumn{{3}}{{l}}{{$\hat b^c = {r['b_c']:.4f}$, \quad $\hat a = {r['a']:.4f}$, \quad "
        rf"$\hat b_u = {r['phi_c']:.4f}$}} \\",
        rf"\multicolumn{{3}}{{l}}{{$\hat\rho = {r['rho']:.4f}$, \quad $\hat\rho^c = {r['rho_c']:.4f}$, \quad "
        rf"$n = {r['n']}$ years, \quad $T = {r['T']}$ monthly observations}} \\",
        rf"\multicolumn{{3}}{{l}}{{OLS $\hat b$ (Question 2b) $= {r['b_ols']:.4f}$}} \\",
        r"\bottomrule",
        r"\end{tabular}",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT.mkdir(exist_ok=True)
    data = build_ah_sample(add_levels(load_eq()))
    r = amihud_hurvich(data)
    tab = to_table(r)
    tab.to_csv(OUT / "q2c_ah.csv", float_format="%.6f")
    write_tex(r, tab, OUT / "q2c_ah_table.tex")
    # ASCII-only console output (Windows console is cp1252)
    print(f"sample: {data.index[0].date()} to {data.index[-1].date()}, T = {r['T']}, n = {r['n']}")
    print(f"rho = {r['rho']:.6f}, rho_c = {r['rho_c']:.6f}, phi_c = {r['phi_c']:.4f}")
    print(f"b_ols (Q2b) = {r['b_ols']:.6f}, b_c = {r['b_c']:.6f}, a = {r['a']:.6f}")
    print(f"Theorem 3 check |b_c - (b_ols + phi_s*(rho_c - rho))| = {r['theorem3_gap']:.2e}")
    print(tab[["se_b_c", "t_b_c"]].to_string(float_format=lambda v: f"{v:.4f}"))


if __name__ == "__main__":
    main()
