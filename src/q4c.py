"""Q4c: one-year excess bond return regressions on the forward spread, H = 2, ..., 5, with
Newey-West (1987, 1994) standard errors (automatic lag selection).

Implements spec/q4c.md. Run from the repo root:  uv run python src/q4c.py
Series come from src/q4a.py (spec/q4a.md): spreads xr = r - r^(1) and xf = f - f^(1);
t+1 in years is 12 monthly rows. The standard errors use the same linearmodels call as
method (v) of src/q2b.py (Bartlett kernel, Newey-West 1994 bandwidth).
"""
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from linearmodels import OLS as LM_OLS

from q4a import construct, load_yields

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"

HORIZONS = [2, 3, 4, 5]
LEAD_MONTHS = 12   # t+1 is one year = 12 monthly rows ahead


def regress(xr: pd.DataFrame, xf: pd.DataFrame, H: int) -> dict:
    """OLS of xr^(H)_{t+12} on a constant and xf^(H)_t over every t with t+12 in the data
    (student decision, spec/q4c.md), Newey-West (1994) automatic-bandwidth standard errors."""
    df = pd.DataFrame({"y": xr[H].shift(-LEAD_MONTHS), "x": xf[H]}).dropna()
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
    tab = pd.DataFrame([regress(s["xr"], s["xf"], H) for H in HORIZONS])
    # problem set footnote 15: b^(2) here equals b^(2) of Q4b (same sample, xf^(2) = 2 xy^(2))
    q4b = pd.read_csv(OUT / "q4b_regressions.csv")
    b2_q4b = float(q4b.loc[q4b["H"] == 2, "b"].iloc[0])
    assert np.isclose(tab.loc[tab["H"] == 2, "b"].iloc[0], b2_q4b, atol=1e-6), "footnote 15 fails"
    print(tab.to_string(index=False, float_format=lambda v: f"{v:.4f}"))
    print(f"footnote 15 check: b(2) = {tab.loc[tab['H'] == 2, 'b'].iloc[0]:.6f}, Q4b b(2) = {b2_q4b:.6f}")
    tab.to_csv(OUT / "q4c_regressions.csv", index=False, float_format="%.6f")
    write_tex(tab, OUT / "q4c_table.tex")


if __name__ == "__main__":
    main()
