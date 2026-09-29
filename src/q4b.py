"""Q4b: hold-to-maturity excess bond return regressions on the yield spread, H = 2, ..., 5,
with Hansen-Hodrick (1980) standard errors.

Implements spec/q4b.md. Run from the repo root:  uv run python src/q4b.py
Series come from src/q4a.py (spec/q4a.md): log yields y, log annual returns r, and the
spreads xy = y - y^(1), xr = r - r^(1); t+h in years is 12h monthly rows.
"""
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

from q4a import construct, load_yields

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"

HORIZONS = [2, 3, 4, 5]
STEP = 12   # one year = 12 monthly rows


def hold_to_maturity_xr(xr: pd.DataFrame, H: int) -> pd.Series:
    """(1/H) * xr_{t->t+H}, with xr_{t->t+H} = sum_{h=1}^{H} xr^{(H-h+1)}_{t+12h}.

    The h = H term is xr^(1) = 0 identically and is omitted, so the series is defined for
    every t with t + 12(H-1) <= end of sample (student decision, spec/q4b.md)."""
    return sum(xr[H - h + 1].shift(-STEP * h) for h in range(1, H)) / H


def regress(dep: pd.Series, xy: pd.Series, H: int) -> dict:
    """OLS of dep on a constant and xy with Hansen-Hodrick (1980) standard errors:
    HAC with uniform weights (w_l = 1) and L = 12H - 1 lags, same statsmodels call as
    method (iv) of src/q2b.py."""
    df = pd.DataFrame({"y": dep, "x": xy}).dropna()
    lags = STEP * H - 1
    res = sm.OLS(df["y"], sm.add_constant(df["x"])).fit(
        cov_type="HAC", cov_kwds={"maxlags": lags, "kernel": "uniform"})
    return {
        "H": H, "N": len(df), "first_t": df.index[0].date(), "last_t": df.index[-1].date(),
        "lags": lags, "a": res.params["const"], "b": res.params["x"],
        "se_b_HH": res.bse["x"], "t_b_HH": res.tvalues["x"], "r2": res.rsquared,
    }


def sanity_checks(s: dict[str, pd.DataFrame]) -> None:
    y, xr = s["y"], s["xr"]
    for H in HORIZONS:
        # telescoping: (1/H) xr_{t->t+H} = y^(H)_t - (1/H) sum_{h=0}^{H-1} y^(1)_{t+12h}
        lhs = hold_to_maturity_xr(xr, H).dropna()
        rhs = (y[H] - sum(y[1].shift(-STEP * h) for h in range(H)) / H).loc[lhs.index]
        assert np.allclose(lhs, rhs), f"telescoping identity fails for H={H}"
    # problem set footnote 15: xr_{t->t+2} = xr^(2)_{t+1}
    assert np.allclose(2 * hold_to_maturity_xr(xr, 2).dropna(), xr[2].shift(-STEP).dropna())


def write_tex(tab: pd.DataFrame, path: Path) -> None:
    """Table body: columns H = 2..5; rows b^(H), [t-stat], R^2 in percent (one decimal)."""
    head = " & ".join([""] + [f"$H={H}$" for H in tab["H"]]) + r" \\"
    row_b = " & ".join([r"$b^{(H)}$"] + [f"{v:.3f}" for v in tab["b"]]) + r" \\"
    row_t = " & ".join([""] + [f"[{v:.2f}]" for v in tab["t_b_HH"]]) + r" \\"
    row_r2 = " & ".join([r"$R^2$ (\%)"] + [f"{100 * v:.1f}" for v in tab["r2"]]) + r" \\"
    lines = [r"\begin{tabular}{lcccc}", r"\toprule", head, r"\midrule",
             row_b, row_t, row_r2, r"\bottomrule", r"\end{tabular}"]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT.mkdir(exist_ok=True)
    s = construct(load_yields())
    sanity_checks(s)
    dep = pd.DataFrame({f"xr_htm{H}": hold_to_maturity_xr(s["xr"], H) for H in HORIZONS})
    dep.index.name = "date"
    dep.to_csv(OUT / "q4b_htm_returns.csv", float_format="%.8f")
    rows = [regress(dep[f"xr_htm{H}"], s["xy"][H], H) for H in HORIZONS]
    tab = pd.DataFrame(rows)
    print(tab.to_string(index=False, float_format=lambda v: f"{v:.4f}"))
    tab.to_csv(OUT / "q4b_regressions.csv", index=False, float_format="%.6f")
    write_tex(tab, OUT / "q4b_table.tex")


if __name__ == "__main__":
    main()
