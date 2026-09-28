"""Q2e: out-of-sample forecasts with the steady-state restriction a_t = G_t - 1, b_t = G_t.

Implements spec/q2e.md. Run from the repo root:  uv run python src/q2e.py
Everything is identical to Q2d (origins, targets, historical mean, in-sample line, evaluation
period, 600-month rolling windows) except the coefficients: G_t is the expanding mean of
exp(dg_m) over m = 1927:12, ..., t, the same months that enter the historical mean at origin t.
"""
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from q2a import add_levels, load_eq
from q2d import expanding_forecasts, r2_os, rolling_r2_os

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"


def steady_state_forecasts(df: pd.DataFrame) -> pd.DataFrame:
    """Q2d frame plus G_t and the restricted forecast E_OS_2e; E_OS_2d kept for comparison."""
    fc = expanding_forecasts(df).rename(columns={"E_OS": "E_OS_2d"})
    G = np.exp(df["dg"]).expanding().mean()          # mean over 1927:12 ... t, incl. 1927:12
    fc["G_t"] = G.reindex(fc["origin"]).to_numpy()
    fc["a_t"] = fc["G_t"] - 1.0
    fc["b_t"] = fc["G_t"]
    dp_t = df["DP"].reindex(fc["origin"]).to_numpy()
    fc["E_OS"] = fc["a_t"] + fc["b_t"] * dp_t         # the Q2e forecast
    return fc


def plot_forecasts(fc: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(fc.index, fc["xRbar"], color="#1f77b4", linewidth=2, label=r"$\overline{xR}_{e,t}$ (historical mean)")
    ax.plot(fc.index, fc["E_IS"], color="#ff7f0e", linewidth=2, label=r"$\hat{E}^{IS}_t[xR_e]$ (full-sample fit)")
    ax.plot(fc.index, fc["E_OS"], color="#2ca02c", linewidth=2, label=r"$\hat{E}^{OS}_t[xR_e]$ ($\hat a_t = G_t-1,\ \hat b_t = G_t$)")
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


def plot_rolling(r2_2d: pd.Series, r2_2e: pd.Series, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(r2_2d.index, r2_2d.values, color="#1f77b4", linewidth=2, label="Question 2d (expanding-window OLS)")
    ax.plot(r2_2e.index, r2_2e.values, color="#d62728", linewidth=2, label=r"Question 2e ($\hat a_t = G_t-1,\ \hat b_t = G_t$)")
    ax.axhline(0, color="0.6", linewidth=0.8)
    ax.set_xlabel("End of 50-year window ($T$)")
    ax.set_ylabel(r"$R^2_{OS}$ (50-year rolling)")
    ax.grid(True, color="0.85", linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.legend(frameon=False, loc="upper right")
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def main() -> None:
    OUT.mkdir(exist_ok=True)
    df = add_levels(load_eq())
    fc = steady_state_forecasts(df)
    r2 = r2_os(fc)
    roll = rolling_r2_os(fc)
    fc_2d = fc.assign(E_OS=fc["E_OS_2d"])
    r2_2d, roll_2d = r2_os(fc_2d), rolling_r2_os(fc_2d)

    cols = ["origin", "n_est", "xR", "xRbar", "E_IS", "E_OS_2d", "G_t", "a_t", "b_t", "E_OS"]
    fc[cols].to_csv(OUT / "q2e_forecasts.csv", float_format="%.6f")
    pd.DataFrame({"r2_os_rolling_2d": roll_2d, "r2_os_rolling_2e": roll}).to_csv(
        OUT / "q2e_r2os_rolling.csv", float_format="%.6f")
    (OUT / "q2e_r2os.tex").write_text(f"{r2:.4f}", encoding="utf-8")
    for ext in ("pdf", "png"):
        plot_forecasts(fc, OUT / f"q2e_forecasts.{ext}")
        plot_rolling(roll_2d, roll, OUT / f"q2e_r2os_rolling.{ext}")

    print(f"forecast targets: {fc.index[0].date()} to {fc.index[-1].date()}, n = {len(fc)}")
    print(f"G_t: first (origin {fc['origin'].iloc[0].date()}) = {fc['G_t'].iloc[0]:.6f}, "
          f"last (origin {fc['origin'].iloc[-1].date()}) = {fc['G_t'].iloc[-1]:.6f}")
    print(f"R2_OS 2e = {r2:.6f}   (2d, same code path: {r2_2d:.6f})")
    print(f"rolling R2_OS 2e: {roll.index[0].date()} to {roll.index[-1].date()}, n = {len(roll)}, "
          f"min = {roll.min():.4f}, max = {roll.max():.4f}, last = {roll.iloc[-1]:.4f}")


if __name__ == "__main__":
    main()
