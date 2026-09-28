"""Q2d: out-of-sample expanding-window forecasts of xR_{e,t+1} = a + b * D_t/P_t + e_t.

Implements spec/q2d.md. Run from the repo root:  uv run python src/q2d.py
Conventions (all from the spec):
  * pair (D_s/P_s, xR_{e,s+1}) has its return realized at s + 12 months;
  * at forecast origin t the regression uses pairs with s <= t - 12 (return realized by t);
  * the historical mean at t averages all returns realized by t, including 1927:12;
  * forecasts start with origin 1939:12 (target 1940:12) and run to the end of the sample;
  * R2_OS = 1 - sum(xR - E_OS)^2 / sum(xR - xRbar)^2 over targets 1940:12 to the end;
  * rolling R2_OS: 600 consecutive target months ending at T, T = 1990:12, ..., end.
"""
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from q2a import add_levels, load_eq
from q2b import LEAD_MONTHS, build_sample

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"

FIRST_TARGET = pd.Timestamp("1940-12-31")
WINDOW = 600          # months, 50-year rolling window
FIRST_WINDOW_END = pd.Timestamp("1990-12-31")


def ols_ab(x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    """OLS of y on a constant and x; returns (a, b)."""
    X = np.column_stack([np.ones_like(x), x])
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    return float(coef[0]), float(coef[1])


def expanding_forecasts(df: pd.DataFrame) -> pd.DataFrame:
    """One row per forecast target date t+12 (origin t), origins 1939:12 onward."""
    pairs = build_sample(df)                       # index s: DP_s, y = xR_{s+12}
    realized = pairs.index + pd.DateOffset(months=LEAD_MONTHS)  # date the pair's return is known
    realized = realized + pd.offsets.MonthEnd(0)
    xR = df["xR"]
    a_full, b_full = ols_ab(pairs["DP"].to_numpy(), pairs["y"].to_numpy())  # Q2b full sample

    rows = []
    for t in pairs.index:
        target = t + pd.DateOffset(months=LEAD_MONTHS) + pd.offsets.MonthEnd(0)
        if target < FIRST_TARGET:
            continue
        use = pairs[realized <= t]                 # pairs whose return is realized by t
        a_t, b_t = ols_ab(use["DP"].to_numpy(), use["y"].to_numpy())
        xbar_t = xR.loc[:t].mean()                 # all returns realized by t, incl. 1927:12
        dp_t = df.at[t, "DP"]
        rows.append({
            "target": target, "origin": t, "n_est": len(use),
            "xR": pairs.at[t, "y"],
            "xRbar": xbar_t,
            "E_IS": a_full + b_full * dp_t,
            "E_OS": a_t + b_t * dp_t,
            "a_t": a_t, "b_t": b_t,
        })
    fc = pd.DataFrame(rows).set_index("target")
    fc.attrs["a_full"], fc.attrs["b_full"] = a_full, b_full
    return fc


def r2_os(fc: pd.DataFrame) -> float:
    e_os = fc["xR"] - fc["E_OS"]
    e_bar = fc["xR"] - fc["xRbar"]
    return 1.0 - float((e_os**2).sum() / (e_bar**2).sum())


def rolling_r2_os(fc: pd.DataFrame) -> pd.Series:
    sse_os = ((fc["xR"] - fc["E_OS"]) ** 2).rolling(WINDOW).sum()
    sse_bar = ((fc["xR"] - fc["xRbar"]) ** 2).rolling(WINDOW).sum()
    out = (1.0 - sse_os / sse_bar).dropna()
    return out[out.index >= FIRST_WINDOW_END].rename("r2_os_rolling")


def plot_forecasts(fc: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(fc.index, fc["xRbar"], color="#1f77b4", linewidth=2, label=r"$\overline{xR}_{e,t}$ (historical mean)")
    ax.plot(fc.index, fc["E_IS"], color="#ff7f0e", linewidth=2, label=r"$\hat{E}^{IS}_t[xR_e]$ (full-sample fit)")
    ax.plot(fc.index, fc["E_OS"], color="#2ca02c", linewidth=2, label=r"$\hat{E}^{OS}_t[xR_e]$ (expanding window)")
    ax.axhline(0, color="0.6", linewidth=0.8)
    ax.set_xlabel("Forecast target month ($t+1$)")
    ax.set_ylabel("Expected annual excess return")
    ax.grid(True, color="0.85", linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.legend(frameon=False, loc="upper right")
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def plot_rolling(r2: pd.Series, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(r2.index, r2.values, color="#1f77b4", linewidth=2)
    ax.axhline(0, color="0.6", linewidth=0.8)
    ax.set_xlabel("End of 50-year window ($T$)")
    ax.set_ylabel(r"$R^2_{OS}$ (50-year rolling)")
    ax.grid(True, color="0.85", linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def main() -> None:
    OUT.mkdir(exist_ok=True)
    df = add_levels(load_eq())
    fc = expanding_forecasts(df)
    r2 = r2_os(fc)
    roll = rolling_r2_os(fc)

    fc.to_csv(OUT / "q2d_forecasts.csv", float_format="%.6f")
    roll.to_csv(OUT / "q2d_r2os_rolling.csv", float_format="%.6f")
    (OUT / "q2d_r2os.tex").write_text(f"{r2:.4f}", encoding="utf-8")
    for name, fn, obj in (("q2d_forecasts", plot_forecasts, fc), ("q2d_r2os_rolling", plot_rolling, roll)):
        fn(obj, OUT / f"{name}.pdf")
        fn(obj, OUT / f"{name}.png")

    first, last = fc.index[0], fc.index[-1]
    print(f"forecast targets: {first.date()} to {last.date()}, n = {len(fc)}")
    print(f"first estimation: origin {fc['origin'].iloc[0].date()}, n_est = {fc['n_est'].iloc[0]}; "
          f"last: origin {fc['origin'].iloc[-1].date()}, n_est = {fc['n_est'].iloc[-1]}")
    print(f"full-sample a = {fc.attrs['a_full']:.6f}, b = {fc.attrs['b_full']:.6f} (should equal Q2b)")
    print(f"R2_OS ({first.date()} to {last.date()}) = {r2:.6f}")
    print(f"rolling R2_OS: {roll.index[0].date()} to {roll.index[-1].date()}, n = {len(roll)}, "
          f"min = {roll.min():.4f}, max = {roll.max():.4f}, last = {roll.iloc[-1]:.4f}")


if __name__ == "__main__":
    main()
