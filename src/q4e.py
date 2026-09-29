"""Q4e: one-year excess bond return regressions on the Cochrane-Piazzesi factor cp_t,
H = 2, ..., 5, with Newey-West (1987, 1994) standard errors (automatic lag selection).

Implements spec/q4e.md. Run from the repo root:  uv run python src/q4e.py
cp_t is the fitted value of the Q4d regression (src/q4d.py, spec/q4d.md), defined on every
month t with t+12 in the data; xr^(H) comes from src/q4a.py. The standard errors use the
same linearmodels call as method (v) of src/q2b.py (Bartlett kernel, Newey-West 1994 bandwidth).
"""
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from linearmodels import OLS as LM_OLS

from q4a import construct, load_yields
from q4d import LEAD_MONTHS, build_sample, estimate

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"

HORIZONS = [2, 3, 4, 5]


def regress(xr: pd.DataFrame, cp: pd.Series, H: int) -> dict:
    """OLS of xr^(H)_{t+12} on a constant and cp_t over every t with t+12 in the data
    (spec/q4e.md), Newey-West (1994) automatic-bandwidth standard errors."""
    df = pd.DataFrame({"y": xr[H].shift(-LEAD_MONTHS), "x": cp}).dropna()
    res = LM_OLS(df["y"], sm.add_constant(df["x"])).fit(
        cov_type="kernel", kernel="bartlett", bandwidth=None)
    return {
        "H": H, "N": int(res.nobs), "first_t": df.index[0].date(), "last_t": df.index[-1].date(),
        "lags": int(res.cov_config["bandwidth"]), "a": res.params["const"], "b": res.params["x"],
        "se_b_NW": res.std_errors["x"], "t_b_NW": res.tstats["x"], "r2": res.rsquared,
    }


def write_tex(tab: pd.DataFrame, path: Path) -> None:
    """Table body: columns H = 2..5; rows b^(H), [t-stat], R^2 in percent (one decimal)."""
    head = " & ".join([""] + [f"$H={H}$" for H in tab["H"]]) + r" \\"
    row_b = " & ".join([r"$b^{(H)}$"] + [f"{v:.3f}" for v in tab["b"]]) + r" \\"
    row_t = " & ".join([""] + [f"[{v:.2f}]" for v in tab["t_b_NW"]]) + r" \\"
    row_r2 = " & ".join([r"$R^2$ (\%)"] + [f"{100 * v:.1f}" for v in tab["r2"]]) + r" \\"
    lines = [r"\begin{tabular}{lcccc}", r"\toprule", head, r"\midrule",
             row_b, row_t, row_r2, r"\bottomrule", r"\end{tabular}"]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT.mkdir(exist_ok=True)
    s = construct(load_yields())
    cp = estimate(build_sample(s)).fitted_values.iloc[:, 0].rename("cp")   # Q4d factor
    saved = pd.read_csv(OUT / "q4d_cp.csv", index_col="date", parse_dates=True)["cp"]
    assert np.allclose(cp, saved.loc[cp.index], atol=1e-8), "cp_t differs from output/q4d_cp.csv"
    tab = pd.DataFrame([regress(s["xr"], cp, H) for H in HORIZONS])
    # cp_t is the fitted value of the average of the four dependent variables on the same
    # sample, so the four slopes average to exactly 1 and the four intercepts to exactly 0
    assert np.isclose(tab["b"].mean(), 1.0) and np.isclose(tab["a"].mean(), 0.0, atol=1e-10)
    print(tab.to_string(index=False, float_format=lambda v: f"{v:.4f}"))
    print(f"check: mean of b(H) = {tab['b'].mean():.6f}, mean of a(H) = {tab['a'].mean():.2e}")
    tab.to_csv(OUT / "q4e_regressions.csv", index=False, float_format="%.6f")
    write_tex(tab, OUT / "q4e_table.tex")


if __name__ == "__main__":
    main()
