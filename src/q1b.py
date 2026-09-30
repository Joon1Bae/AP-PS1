"""Q1b: variance decomposition of dp_t by horizon (Equation 1.4) on the EQ Dataset.

Implements spec/q1b.md. Run from the repo root:  uv run python src/q1b.py
kappa = 1/(1 + e^{dpbar}) with dpbar the full-sample mean of dp, fixed for every H. For each
H = 1, ..., 15 the terms
    A_t =  sum_{h=1}^{H} kappa^{h-1} r_{e,t+12h}
    B_t = -sum_{h=1}^{H} kappa^{h-1} dd_{t+12h}
    C_t =  kappa^H dp_{t+12H}
are regressed by OLS on a constant and dp_t, over every month t with t + 12H in the data;
the slopes are b_re^(H), b_dd^(H) and b_dp^(H).
"""
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from q2a import H_MAX, MONTHS_PER_H, load_eq

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"

TERMS = {"b_re": "A", "b_dd": "B", "b_dp": "C"}
LABELS = {"b_re": r"$b^{(H)}_{r_e}$ (returns)", "b_dd": r"$b^{(H)}_{\Delta d}$ (dividend growth)",
          "b_dp": r"$b^{(H)}_{dp}$ (future $dp$)"}
COLORS = {"b_re": "#1f77b4", "b_dd": "#d62728", "b_dp": "#2ca02c"}


def terms(df: pd.DataFrame, kappa: float, H: int) -> pd.DataFrame:
    """A_t, B_t, C_t and dp_t; NaN wherever t + 12H is outside the data."""
    lead = lambda s, h: s.shift(-MONTHS_PER_H * h)
    A = pd.concat([kappa ** (h - 1) * lead(df["re"], h) for h in range(1, H + 1)], axis=1).sum(axis=1, skipna=False)
    B = -pd.concat([kappa ** (h - 1) * lead(df["dg"], h) for h in range(1, H + 1)], axis=1).sum(axis=1, skipna=False)
    C = kappa ** H * lead(df["dp"], H)
    return pd.DataFrame({"dp": df["dp"], "A": A, "B": B, "C": C})


def decomposition(df: pd.DataFrame, kappa: float) -> pd.DataFrame:
    rows = []
    for H in range(1, H_MAX + 1):
        data = terms(df, kappa, H).dropna()
        X = sm.add_constant(data["dp"])
        row = {"H": H, "N": len(data), "first_t": data.index[0].date(), "last_t": data.index[-1].date()}
        for name, col in TERMS.items():
            row[name] = sm.OLS(data[col], X).fit().params["dp"]
            # with a constant, the OLS slope equals Cov(dp, term) / Var(dp) on the sample
            assert np.isclose(row[name], data[col].cov(data["dp"]) / data["dp"].var())
        row["sum"] = row["b_re"] + row["b_dd"] + row["b_dp"]
        rows.append(row)
    return pd.DataFrame(rows)


def plot(tab: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 4))
    for name in TERMS:
        ax.plot(tab["H"], tab[name], color=COLORS[name], marker="o", linewidth=1.8, label=LABELS[name])
    ax.axhline(0, color="0.6", linewidth=0.8)
    ax.set_xticks(tab["H"])
    ax.set_xlabel("Horizon $H$ (years)")
    ax.set_ylabel("Share of Var[$dp$]")
    ax.grid(True, color="0.92", linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.legend(frameon=False, loc="center right")
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def write_tex(tab: pd.DataFrame, path: Path) -> None:
    """Table body: one row per H; columns b_re, b_dd, b_dp, their sum, N."""
    lines = [r"\begin{tabular}{rccccr}", r"\toprule",
             r"$H$ & $b^{(H)}_{r_e}$ & $b^{(H)}_{\Delta d}$ & $b^{(H)}_{dp}$ & Sum & $N$ \\", r"\midrule"]
    for _, r in tab.iterrows():
        lines.append(f"{int(r['H'])} & {r['b_re']:.3f} & {r['b_dd']:.3f} & {r['b_dp']:.3f} & "
                     f"{r['sum']:.3f} & {int(r['N']):,} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT.mkdir(exist_ok=True)
    df = load_eq()
    dpbar = df["dp"].mean()                      # full sample, computed once
    kappa = 1 / (1 + np.exp(dpbar))
    tab = decomposition(df, kappa)
    print(f"full sample {df.index[0].date()} to {df.index[-1].date()}, dpbar = {dpbar:.6f}, kappa = {kappa:.6f}")
    print(tab.to_string(index=False, float_format=lambda v: f"{v:.4f}"))
    tab.assign(kappa=kappa, dpbar=dpbar).to_csv(OUT / "q1b_coefficients.csv", index=False, float_format="%.6f")
    write_tex(tab, OUT / "q1b_table.tex")
    for ext in ("pdf", "png"):
        plot(tab, OUT / f"q1b_decomposition.{ext}")


if __name__ == "__main__":
    main()
