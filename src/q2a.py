"""Q2a: adjusted R^2 of (1/H) sum_{h=1}^H xR_{e,t+h} = a + b * D_t/P_t for H = 1, ..., H_max.

Implements spec/q2a.md. Run from the repo root:  uv run python src/q2a.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "eq.csv"
OUT = ROOT / "output"


def load_eq() -> pd.DataFrame:
    """Step 1: eq.csv -> DataFrame with a monthly DatetimeIndex (end of month)."""
    df = pd.read_csv(DATA)
    df.index = pd.to_datetime(dict(year=df["YEAR"], month=df["MONTH"], day=1)) + pd.offsets.MonthEnd(0)
    df.index.name = "date"
    return df.drop(columns=["YEAR", "MONTH"])


def add_levels(df: pd.DataFrame) -> pd.DataFrame:
    """Steps 2-3: exp of dp, re, rf; xR_e = e^re - e^rf."""
    df = df.copy()
    df["DP"] = np.exp(df["dp"])     # D_t / P_t
    df["Re"] = np.exp(df["re"])     # gross annual (deflated) equity return
    df["Rf"] = np.exp(df["rf"])     # gross annual (deflated) risk-free return
    df["xR"] = df["Re"] - df["Rf"]  # annual excess return, simple
    return df


H_MAX = 15          # student decision: H = 1, ..., 15
MONTHS_PER_H = 12   # student decision: h in years; each h is 12 monthly rows ahead


def horizon_average(xR: pd.Series, H: int) -> pd.Series:
    """(1/H) * sum_{h=1}^{H} xR_{t+h}, with each h = MONTHS_PER_H rows ahead of t.

    NaN wherever any of the H future observations is missing, so the estimation sample
    for horizon H is every month t with t + 12H inside the data (student decision).
    """
    future = [xR.shift(-MONTHS_PER_H * h) for h in range(1, H + 1)]
    return pd.concat(future, axis=1).sum(axis=1, skipna=False) / H


def r2adj_by_horizon(df: pd.DataFrame) -> pd.DataFrame:
    """Step 4: OLS of the H-year average excess return on D_t/P_t (with intercept)."""
    rows = []
    for H in range(1, H_MAX + 1):
        y = horizon_average(df["xR"], H)
        data = pd.DataFrame({"y": y, "DP": df["DP"]}).dropna()
        res = sm.OLS(data["y"], sm.add_constant(data["DP"])).fit()
        rows.append({
            "H": H,
            "n_obs": int(res.nobs),
            "first_t": data.index[0].date(),
            "last_t": data.index[-1].date(),
            "b": res.params["DP"],
            "r2": res.rsquared,
            "r2_adj": res.rsquared_adj,
        })
    return pd.DataFrame(rows).set_index("H")


def plot_r2adj(tab: pd.DataFrame, path: Path) -> None:
    """Step 5: x = H, y = adjusted R^2 (single series, so no legend)."""
    fig, ax = plt.subplots(figsize=(6.5, 4))
    ax.plot(tab.index, tab["r2_adj"], color="#1f77b4", linewidth=2, marker="o", markersize=6)
    ax.set_xlabel("Horizon H (years)")
    ax.set_ylabel(r"Adjusted $R^2$")
    ax.set_xticks(tab.index)
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
    tab = r2adj_by_horizon(df)
    tab.to_csv(OUT / "q2a_r2adj.csv", float_format="%.6f")
    plot_r2adj(tab, OUT / "q2a_r2adj.pdf")
    plot_r2adj(tab, OUT / "q2a_r2adj.png")
    # ASCII-only console output (Windows console is cp1252)
    print(f"rows: {len(df)}, first: {df.index[0].date()}, last: {df.index[-1].date()}")
    print(tab.to_string(float_format=lambda v: f"{v:.4f}"))


if __name__ == "__main__":
    main()
