"""Q3a: momentum signal MOM from CRSP and its validation against the Chen-Zimmermann Mom12m.

Implements spec/q3a.md with the common rules of spec/q3_common.md (src/q3_common.py).
Run from the repo root:  uv run python src/q3a.py
MOM_{j,tau} is the cumulative return over the 11 calendar months tau-11, ..., tau-1; it is
missing when any of the 11 months has a missing return or no row. For each signal month tau,
MOM_CZ = Mom12m is regressed on a constant and MOM across the firms in the universe at tau.
"""
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from q3_common import crsp_panel, in_signal_window, load_cz, to_yyyymm

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"

FIRST_LAG, LAST_LAG = 1, 11      # returns of months tau-1, ..., tau-11

SERIES = {"intercept": "Intercept", "slope": "Slope", "r2": r"$R^2$"}


def momentum(panel: pd.DataFrame) -> pd.Series:
    """MOM for every (permno, month), from the returns of the same PERMNO in the whole file."""
    gross = (1 + panel["ret"]).to_frame("g").set_index([panel["month"], panel["permno"]])["g"].unstack()
    gross = gross.reindex(range(gross.index.min(), gross.index.max() + 1))   # every calendar month
    values = gross.to_numpy()
    mom = np.ones_like(values)
    for lag in range(FIRST_LAG, LAST_LAG + 1):
        shifted = np.full_like(values, np.nan)
        shifted[lag:] = values[:-lag]
        mom *= shifted                                   # a missing month makes MOM missing
    mom = pd.DataFrame(mom - 1, index=gross.index, columns=gross.columns)
    return mom.stack().rename("mom")


def cross_section_ols(df: pd.DataFrame) -> pd.DataFrame:
    """For each month, OLS of y on a constant and x: intercept, slope, unadjusted R2, N."""
    g = df.groupby("yyyymm")
    dx = df["x"] - g["x"].transform("mean")
    dy = df["y"] - g["y"].transform("mean")
    sxx = (dx * dx).groupby(df["yyyymm"]).sum()
    sxy = (dx * dy).groupby(df["yyyymm"]).sum()
    syy = (dy * dy).groupby(df["yyyymm"]).sum()
    slope = sxy / sxx
    return pd.DataFrame({"intercept": g["y"].mean() - slope * g["x"].mean(), "slope": slope,
                         "r2": sxy ** 2 / (sxx * syy), "N": g.size()})


def plot_series(s: pd.Series, label: str, reference: float, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.axhline(reference, color="0.6", linewidth=0.8, zorder=1)
    ax.plot(s.index, s.values, color="#1f77b4", linewidth=1.2, zorder=2)
    ax.set_xlabel(r"Month ($\tau$)")
    ax.set_ylabel(label)
    ax.grid(True, color="0.92", linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.set_xlim(s.index[0], s.index[-1])
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def write_tex(summary: pd.DataFrame, path: Path) -> None:
    """Table body: rows intercept, slope, R^2, N; columns time-series mean, minimum, maximum."""
    names = {"intercept": "Intercept", "slope": "Slope", "r2": "$R^2$", "N": "$N$"}
    lines = [r"\begin{tabular}{lccc}", r"\toprule", r" & Mean & Minimum & Maximum \\", r"\midrule"]
    for key, row in summary.iterrows():
        fmt = "{:,.0f}" if key == "N" else "{:.4f}"
        lines.append(" & ".join([names[key]] + [fmt.format(row[c]) for c in ("mean", "min", "max")]) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT.mkdir(exist_ok=True)
    panel = crsp_panel()
    mom = momentum(panel)

    universe = panel.loc[panel["universe"] & in_signal_window(panel["yyyymm"]), ["permno", "yyyymm", "month"]]
    df = universe.merge(mom.reset_index(), on=["month", "permno"], how="left")
    df = df.merge(load_cz(["Mom12m"]), on=["permno", "yyyymm"], how="left")
    print(f"universe firm-months: {len(df)}, with MOM: {df['mom'].notna().sum()}, "
          f"with Mom12m: {df['Mom12m'].notna().sum()}, with both: {df[['mom', 'Mom12m']].notna().all(axis=1).sum()}")

    both = df.dropna(subset=["mom", "Mom12m"]).rename(columns={"mom": "x", "Mom12m": "y"})
    reg = cross_section_ols(both)
    assert len(reg) == len(universe["yyyymm"].unique()), "a signal month has no regression"
    gap = (both["y"] - both["x"]).abs()
    print(f"|Mom12m - MOM|: median = {gap.median():.2e}, share above 1e-4 = {(gap > 1e-4).mean():.4f}")

    summary = reg.agg(["mean", "min", "max"]).T
    print(f"signal months: {reg.index[0]} to {reg.index[-1]} ({len(reg)} regressions)")
    print(summary.to_string(float_format=lambda v: f"{v:.4f}"))
    for key in SERIES:
        print(f"{key}: min in {reg[key].idxmin()}, max in {reg[key].idxmax()}")

    reg.to_csv(OUT / "q3a_regressions.csv", float_format="%.8f")
    summary.index.name = "statistic"
    summary.to_csv(OUT / "q3a_summary.csv", float_format="%.8f")
    write_tex(summary, OUT / "q3a_table.tex")
    dates = pd.to_datetime(reg.index.astype(str), format="%Y%m") + pd.offsets.MonthEnd(0)
    for key, label in SERIES.items():
        s = pd.Series(reg[key].to_numpy(), index=dates)
        for ext in ("pdf", "png"):
            plot_series(s, label, 0.0 if key == "intercept" else 1.0, OUT / f"q3a_{key}.{ext}")


if __name__ == "__main__":
    main()
