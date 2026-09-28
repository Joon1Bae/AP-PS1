"""Q2a: adjusted R^2 of (1/H) sum_{h=1}^H xR_{e,t+h} = a + b * D_t/P_t for H = 1, ..., H_max.

Implements spec/q2a.md. Run from the repo root:  uv run python src/q2a_r2adj.py
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


# ---------------------------------------------------------------------------
# Steps 4-5: PENDING student decisions recorded in spec/q2a.md (horizon range,
# time step of h, estimation sample per H). Do not implement until decided.
# ---------------------------------------------------------------------------


def main() -> None:
    OUT.mkdir(exist_ok=True)
    df = add_levels(load_eq())
    # Sanity output (ASCII only; Windows console is cp1252)
    print(f"rows: {len(df)}, first: {df.index[0].date()}, last: {df.index[-1].date()}")
    print(df[["DP", "xR"]].describe().round(4).to_string())


if __name__ == "__main__":
    main()
