"""Q4d: Cochrane-Piazzesi (2005) factor from the regression of the average one-year excess
bond return on the five Fama-Bliss forward rates, and its time-series plot with NBER
recession shading.

Implements spec/q4d.md. Run from the repo root:  uv run python src/q4d.py
Series come from src/q4a.py (spec/q4a.md): forward rates f^(H) and excess returns xr^(H);
t+1 in years is 12 monthly rows. Standard errors use the same linearmodels call as method (v)
of src/q2b.py (Bartlett kernel, Newey-West 1994 bandwidth); they are saved, not plotted.
NBER recession months: data/USREC.csv (FRED series USREC, 1 = recession month).
"""
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from linearmodels import OLS as LM_OLS

from q4a import construct, load_yields

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"
USREC = ROOT / "data" / "USREC.csv"

LEAD_MONTHS = 12          # t+1 is one year = 12 monthly rows ahead
RETURN_MATURITIES = [2, 3, 4, 5]
FORWARD_MATURITIES = [1, 2, 3, 4, 5]


def build_sample(s: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """y_t = (1/4) sum_{H=2}^{5} xr^(H)_{t+12}; regressors f^(1)_t, ..., f^(5)_t.
    Every month t with t+12 in the data (the fitted value cp_t is defined on these dates only)."""
    y = sum(s["xr"][H].shift(-LEAD_MONTHS) for H in RETURN_MATURITIES) / len(RETURN_MATURITIES)
    X = s["f"][FORWARD_MATURITIES].copy()
    X.columns = [f"f{H}" for H in FORWARD_MATURITIES]
    return pd.concat([y.rename("y"), X], axis=1).dropna()


def estimate(df: pd.DataFrame):
    X = sm.add_constant(df[[c for c in df.columns if c != "y"]])
    return LM_OLS(df["y"], X).fit(cov_type="kernel", kernel="bartlett", bandwidth=None)


def recession_bands(index: pd.DatetimeIndex) -> list[tuple[pd.Timestamp, pd.Timestamp]]:
    """(start, end) of each run of consecutive NBER recession months overlapping the index.
    USREC is dated the first of the month; a band covers the recession months in full."""
    u = pd.read_csv(USREC, parse_dates=["observation_date"])
    u = u[(u["observation_date"] >= index[0] - pd.offsets.MonthBegin(1)) & (u["observation_date"] <= index[-1])]
    rec = u[u["USREC"] == 1]["observation_date"]
    bands, start, prev = [], None, None
    for d in rec:
        if start is None or d != prev + pd.offsets.MonthBegin(1):
            if start is not None:
                bands.append((start, prev + pd.offsets.MonthEnd(0)))
            start = d
        prev = d
    if start is not None:
        bands.append((start, prev + pd.offsets.MonthEnd(0)))
    return bands


def plot_cp(cp: pd.Series, bands: list, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 4))
    for start, end in bands:
        ax.axvspan(start, end, color="0.85", linewidth=0, zorder=0)
    ax.plot(cp.index, cp.values, color="#1f77b4", linewidth=1.6, zorder=2)
    ax.axhline(0, color="0.6", linewidth=0.8, zorder=1)
    ax.set_xlabel("Month ($t$)")
    ax.set_ylabel(r"$cp_t$ (annual excess log return)")
    ax.grid(True, color="0.92", linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.set_xlim(cp.index[0], cp.index[-1])
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def main() -> None:
    OUT.mkdir(exist_ok=True)
    df = build_sample(construct(load_yields()))
    res = estimate(df)
    cp = res.fitted_values.iloc[:, 0].rename("cp")
    bw = int(res.cov_config["bandwidth"])
    coef = pd.DataFrame({"coef": res.params, "se_NW": res.std_errors, "t_NW": res.tstats})
    coef.index.name = "regressor"
    coef["N"], coef["lags"], coef["r2"] = int(res.nobs), bw, res.rsquared
    print(f"sample: {df.index[0].date()} to {df.index[-1].date()}, N = {int(res.nobs)}, "
          f"NW(1994) lags = {bw}, R2 = {res.rsquared:.4f}")
    print(coef[["coef", "se_NW", "t_NW"]].to_string(float_format=lambda v: f"{v:.4f}"))
    print(f"cp_t: mean = {cp.mean():.5f}, sd = {cp.std():.5f}, min = {cp.min():.5f} ({cp.idxmin().date()}), "
          f"max = {cp.max():.5f} ({cp.idxmax().date()})")
    coef.to_csv(OUT / "q4d_coefficients.csv", float_format="%.6f")
    out = pd.concat([df["y"].rename("xr_avg_t+1"), cp], axis=1)
    out.index.name = "date"
    out.to_csv(OUT / "q4d_cp.csv", float_format="%.8f")
    bands = recession_bands(cp.index)
    print(f"NBER recessions in sample: {len(bands)}; first {bands[0][0].date()}..{bands[0][1].date()}, "
          f"last {bands[-1][0].date()}..{bands[-1][1].date()}")
    for ext in ("pdf", "png"):
        plot_cp(cp, bands, OUT / f"q4d_cp.{ext}")


if __name__ == "__main__":
    main()
