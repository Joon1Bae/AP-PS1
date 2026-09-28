"""Q2b: xR_{e,t+1} = a + b * D_t/P_t + e_t, with b-hat and its t-statistic under five
standard-error methods: (i) OLS, (ii) White (1980), (iii) Newey-West (1987) with 11 lags,
(iv) Hansen-Hodrick (1980) with 11 lags, (v) Newey-West (1987, 1994) with automatic lag selection.

Implements spec/q2b.md. Run from the repo root:  uv run python src/q2b.py
All estimators come from existing libraries (statsmodels, linearmodels); nothing is re-implemented.
"""
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from linearmodels import OLS as LM_OLS

from q2a import add_levels, load_eq  # same data construction as Q2a (spec/q2a.md)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"

LEAD_MONTHS = 12   # t+1 is one year = 12 monthly rows ahead (spec/q2b.md, decision 1)
FIXED_LAGS = 11    # methods (iii) and (iv)


def build_sample(df: pd.DataFrame) -> pd.DataFrame:
    """y_t = xR_{t+12}, x_t = D_t/P_t; every month t with t+12 in the data (decision 2)."""
    data = pd.DataFrame({"y": df["xR"].shift(-LEAD_MONTHS), "DP": df["DP"]}).dropna()
    return data


def statsmodels_fits(data: pd.DataFrame) -> dict:
    """Methods (i)-(iv) via statsmodels OLS covariance options."""
    X = sm.add_constant(data["DP"])
    model = sm.OLS(data["y"], X)
    return {
        "(i) OLS": model.fit(cov_type="nonrobust"),
        "(ii) White (1980)": model.fit(cov_type="HC0"),
        "(iii) Newey-West (1987), 11 lags": model.fit(
            cov_type="HAC", cov_kwds={"maxlags": FIXED_LAGS, "kernel": "bartlett"}),
        "(iv) Hansen-Hodrick (1980), 11 lags": model.fit(
            cov_type="HAC", cov_kwds={"maxlags": FIXED_LAGS, "kernel": "uniform"}),
    }


def linearmodels_nw1994(data: pd.DataFrame):
    """Method (v): Bartlett-kernel HAC with the Newey-West (1994) automatic bandwidth."""
    X = sm.add_constant(data["DP"])
    res = LM_OLS(data["y"], X).fit(cov_type="kernel", kernel="bartlett", bandwidth=None)
    return res


def summarize(sm_fits: dict, lm_res) -> pd.DataFrame:
    rows = []
    for name, r in sm_fits.items():
        lags = FIXED_LAGS if "lags" in name else 0
        rows.append({"method": name, "a": r.params["const"], "b": r.params["DP"],
                     "se_a": r.bse["const"], "t_a": r.tvalues["const"],
                     "se_b": r.bse["DP"], "t_b": r.tvalues["DP"], "lags": lags})
    bw = int(lm_res.cov_config["bandwidth"])
    rows.append({"method": "(v) Newey-West (1987, 1994), automatic lags",
                 "a": lm_res.params["const"], "b": lm_res.params["DP"],
                 "se_a": lm_res.std_errors["const"], "t_a": lm_res.tstats["const"],
                 "se_b": lm_res.std_errors["DP"], "t_b": lm_res.tstats["DP"], "lags": bw})
    tab = pd.DataFrame(rows).set_index("method")
    tab["n_obs"] = int(sm_fits["(i) OLS"].nobs)
    return tab


def write_tex(tab: pd.DataFrame, path: Path) -> None:
    r"""LaTeX tabular body (booktabs) for tex/ps1_solution.tex to input."""
    a, b, n = tab["a"].iloc[0], tab["b"].iloc[0], int(tab["n_obs"].iloc[0])
    lines = [
        r"\begin{tabular}{lccc}",
        r"\toprule",
        r"Standard-error method & SE$(\hat b)$ & $t(\hat b)$ & Lags \\",
        r"\midrule",
    ]
    for name, r in tab.iterrows():
        lags = "--" if r["lags"] == 0 else f"{int(r['lags'])}"
        lines.append(f"{name} & {r['se_b']:.4f} & {r['t_b']:.2f} & {lags} \\\\")
    lines += [
        r"\midrule",
        rf"\multicolumn{{4}}{{l}}{{$\hat a = {a:.4f}$, \quad $\hat b = {b:.4f}$, \quad $T = {n}$ monthly observations}} \\",
        r"\bottomrule",
        r"\end{tabular}",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT.mkdir(exist_ok=True)
    df = add_levels(load_eq())
    data = build_sample(df)
    sm_fits = statsmodels_fits(data)
    lm_res = linearmodels_nw1994(data)

    # Internal consistency check: linearmodels with bandwidth fixed at 11 should match
    # statsmodels HAC(11, bartlett) since both scale autocovariances by 1/T with no correction.
    X = sm.add_constant(data["DP"])
    lm11 = LM_OLS(data["y"], X).fit(cov_type="kernel", kernel="bartlett", bandwidth=FIXED_LAGS)
    diff = abs(lm11.std_errors["DP"] - sm_fits["(iii) Newey-West (1987), 11 lags"].bse["DP"])
    print(f"cross-check NW(11): |SE_linearmodels - SE_statsmodels| = {diff:.2e}")

    tab = summarize(sm_fits, lm_res)
    tab.to_csv(OUT / "q2b_se_table.csv", float_format="%.6f")
    write_tex(tab, OUT / "q2b_se_table.tex")
    print(f"sample: {data.index[0].date()} to {data.index[-1].date()}, n = {len(data)}")
    print(tab[["b", "se_b", "t_b", "lags"]].to_string(float_format=lambda v: f"{v:.4f}"))


if __name__ == "__main__":
    main()
