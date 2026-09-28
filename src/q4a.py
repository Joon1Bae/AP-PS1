"""Q4a: Fama-Bliss log yields, log forward rates, log annual returns, and their spreads over
the 1-year bond; table of average spreads for H = 2, ..., 5.

Implements spec/q4a.md. Run from the repo root:  uv run python src/q4a.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "bond.csv"
OUT = ROOT / "output"

MATURITIES = [1, 2, 3, 4, 5]
LAG_MONTHS = 12   # t-1 in years = 12 monthly rows (spec: y_{t-12})

# STUDENT DECISION PENDING (spec/q4a.md): months entering the averages -- each variable over
# every month it is available, or a common sample across xy, xf, xr (from 1953:06).
AVERAGING_SAMPLE = None   # "each" or "common"; set from the spec once decided


def load_yields() -> pd.DataFrame:
    """Wide frame of Fama-Bliss yields in percent: index = month-end date, columns = 1..5."""
    raw = pd.read_csv(DATA)
    fb = raw[raw["TTERMLBL"].str.startswith("Fama Bliss Discount Bonds", na=False)].copy()
    fb["H"] = fb["TTERMLBL"].str.extract(r"(\d)-Year").astype(int)
    fb["date"] = pd.to_datetime(fb["MCALDT"]) + pd.offsets.MonthEnd(0)
    wide = fb.pivot(index="date", columns="H", values="TMYTM").sort_index()
    wide = wide[MATURITIES]
    # sanity: contiguous monthly index so that a 12-row shift equals a calendar year
    expected = pd.date_range(wide.index[0], wide.index[-1], freq="ME")
    assert wide.index.equals(expected), "monthly index is not contiguous"
    assert not wide.isna().any().any(), "missing yields"
    return wide


def construct(wide: pd.DataFrame) -> dict[str, pd.DataFrame]:
    y = np.log(1.0 + wide / 100.0)                       # log yields, annual, decimal
    f = pd.DataFrame(index=y.index)
    r = pd.DataFrame(index=y.index)
    for H in MATURITIES:
        y_prev = y[H - 1] if H > 1 else 0.0              # y^(0) = 0 gives f^(1) = y^(1), r^(1) = y^(1)_{t-12}
        f[H] = H * y[H] - (H - 1) * y_prev
        r[H] = H * y[H].shift(LAG_MONTHS) - (H - 1) * y_prev
    spreads = {
        "xy": y.sub(y[1], axis=0),
        "xf": f.sub(f[1], axis=0),
        "xr": r.sub(r[1], axis=0),
    }
    return {"y": y, "f": f, "r": r, **spreads}


def averages(series: dict[str, pd.DataFrame], sample: str) -> pd.DataFrame:
    """Means in percent for H = 2..5; sample = 'each' (all available months per variable)
    or 'common' (months where xy, xf and xr are all available)."""
    cols = [H for H in MATURITIES if H >= 2]
    if sample == "common":
        idx = series["xr"][cols].dropna().index
        tab = {k: series[k].loc[idx, cols].mean() for k in ("xy", "xf", "xr")}
    else:
        tab = {k: series[k][cols].mean() for k in ("xy", "xf", "xr")}
    return (pd.DataFrame(tab) * 100.0).T


def write_tex(tab: pd.DataFrame, path: Path, note: str) -> None:
    labels = {"xy": r"$xy^{(H)}_{b,t}$ (yield spread)",
              "xf": r"$xf^{(H)}_{b,t}$ (forward spread)",
              "xr": r"$xr^{(H)}_{b,t}$ (excess return)"}
    lines = [r"\begin{tabular}{lcccc}", r"\toprule",
             " & ".join([r"Average (\%)"] + [f"$H={H}$" for H in tab.columns]) + r" \\", r"\midrule"]
    for k, row in tab.iterrows():
        lines.append(" & ".join([labels[k]] + [f"{v:.3f}" for v in row]) + r" \\")
    lines += [r"\midrule", rf"\multicolumn{{5}}{{l}}{{{note}}} \\", r"\bottomrule", r"\end{tabular}"]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT.mkdir(exist_ok=True)
    wide = load_yields()
    s = construct(wide)
    long = pd.concat({k: s[k] for k in ("y", "f", "r", "xy", "xf", "xr")}, axis=1)
    long.columns = [f"{k}{H}" for k, H in long.columns]
    long.to_csv(OUT / "q4a_series.csv", float_format="%.8f")
    print(f"yields: {wide.index[0].date()} to {wide.index[-1].date()}, {len(wide)} months; "
          f"returns from {s['r'].dropna().index[0].date()}")
    for sample in ("each", "common"):
        print(f"--- averages in %, sample = {sample}")
        print(averages(s, sample).to_string(float_format=lambda v: f"{v:.3f}"))
    if AVERAGING_SAMPLE is None:
        print("table not written: AVERAGING_SAMPLE pending student decision (spec/q4a.md)")
        return
    tab = averages(s, AVERAGING_SAMPLE)
    tab.to_csv(OUT / "q4a_averages.csv", float_format="%.6f")
    n = len(s["xr"].dropna()) if AVERAGING_SAMPLE == "common" else None
    note = ("Common sample 1953:06--2024:12" if AVERAGING_SAMPLE == "common"
            else "Each series over all available months (yields and forwards from 1952:06, returns from 1953:06)")
    write_tex(tab, OUT / "q4a_averages_table.tex", note)


if __name__ == "__main__":
    main()
