"""Q3c: decile portfolios on the Chen-Zimmermann signals BM_CZ, MOM_CZ and GP_CZ, five
portfolio types, average excess returns by decile and HML (decile 10 - decile 1) averages.

Implements spec/q3c.md with the common rules of spec/q3_common.md (src/q3_common.py).
Run from the repo root:  uv run python src/q3c.py
Deciles are formed at the end of tau (monthly) or of June t (annual, held July t to June t+1)
among the firms in the universe at the formation date with a valid signal. The return of month
tau+1 uses the members with a return in tau+1; value weights are ME at the end of tau.
HML t-statistics use the same linearmodels call as method (v) of src/q2b.py (Bartlett kernel,
Newey-West 1994 bandwidth).
"""
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from linearmodels import OLS as LM_OLS

from q3_common import (FIRST_RETURN, LAST_RETURN, crsp_panel, in_signal_window, load_cz, load_rf,
                       month_number, to_yyyymm)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"

SIGNALS = {"BM": "BMdec", "MOM": "Mom12m", "GP": "GP"}          # name: CZ column
POSITIVE_ONLY = {"BM"}                                           # BMdec <= 0 is excluded
COLORS = {"BM": "blue", "MOM": "red", "GP": "green"}
LABELS = {"BM": r"$BM^{CZ}$", "MOM": r"$MOM^{CZ}$", "GP": r"$GP^{CZ}$"}
TYPES = {                                                        # weights, rebalancing, breakpoints
    "i": ("VW", "annual", "NYSE"),
    "ii": ("EW", "annual", "NYSE"),
    "iii": ("VW", "monthly", "NYSE"),
    "iv": ("VW", "annual", "general"),
    "v": ("EW", "monthly", "general"),
}
PERCENTILES = np.arange(10, 100, 10)
FORMATION_MONTH = 6                                              # annual portfolios: June


def formation_table(panel: pd.DataFrame) -> pd.DataFrame:
    """Firms in the universe at tau (signal window) with the CZ signals dated tau."""
    u = panel.loc[panel["universe"] & in_signal_window(panel["yyyymm"]),
                  ["permno", "yyyymm", "month", "PrimaryExch"]]
    cz = load_cz(list(SIGNALS.values())).rename(columns={v: k for k, v in SIGNALS.items()})
    return u.merge(cz, on=["permno", "yyyymm"], how="left", validate="one_to_one")


def assign_deciles(form: pd.DataFrame, signal: str, breakpoints: str) -> pd.DataFrame:
    """Decile of every firm in the sort, for each formation month in the table.
    Decile d: cut_{d-1} < signal <= cut_d, cuts = 10th, ..., 90th percentiles."""
    x = form[signal]
    valid = x.notna() & np.isfinite(x)
    if signal in POSITIVE_ONLY:
        valid &= x > 0
    sort = form.loc[valid, ["permno", "month", "PrimaryExch", signal]]
    pieces = []
    for _, g in sort.groupby("month"):
        base = g.loc[g["PrimaryExch"] == "N", signal] if breakpoints == "NYSE" else g[signal]
        cuts = np.percentile(base.to_numpy(), PERCENTILES)
        decile = np.searchsorted(cuts, g[signal].to_numpy(), side="left") + 1
        pieces.append(g[["permno", "month"]].assign(decile=decile))
    return pd.concat(pieces, ignore_index=True)


def return_table(panel: pd.DataFrame) -> pd.DataFrame:
    """Firm-months with a return in tau+1, with ME at the end of tau and the formation keys."""
    r = panel.loc[(panel["yyyymm"] >= FIRST_RETURN) & (panel["yyyymm"] <= LAST_RETURN) & panel["ret"].notna(),
                  ["permno", "yyyymm", "month", "ret"]]
    lag = panel[["permno", "month", "me"]].assign(month=panel["month"] + 1).rename(columns={"me": "me_lag"})
    r = r.merge(lag, on=["permno", "month"], how="left", validate="one_to_one")
    r["tau"] = r["month"] - 1                                    # monthly formation date
    tau = to_yyyymm(r["tau"])
    year = np.where(tau % 100 >= FORMATION_MONTH, tau // 100, tau // 100 - 1)
    r["june"] = month_number(year * 100 + FORMATION_MONTH)       # annual formation date
    return r


def portfolio_returns(ret: pd.DataFrame, deciles: pd.DataFrame, weights: str, rebalancing: str) -> pd.DataFrame:
    """Return and number of members of each decile in each return month."""
    key = "tau" if rebalancing == "monthly" else "june"
    d = deciles if rebalancing == "monthly" else deciles[to_yyyymm(deciles["month"]) % 100 == FORMATION_MONTH]
    m = ret.merge(d.rename(columns={"month": key}), on=["permno", key], how="inner", validate="many_to_one")
    if weights == "VW":
        m = m[m["me_lag"].notna()]
        m = m.assign(wr=m["me_lag"] * m["ret"])
        g = m.groupby(["yyyymm", "decile"])
        out = pd.DataFrame({"ret": g["wr"].sum() / g["me_lag"].sum(), "n": g.size()})
    else:
        g = m.groupby(["yyyymm", "decile"])
        out = pd.DataFrame({"ret": g["ret"].mean(), "n": g.size()})
    return out.reset_index()


def newey_west_mean(y: pd.Series) -> dict:
    """Mean of y and its t-statistic from a regression on a constant, Newey-West (1994) lags."""
    res = LM_OLS(y, pd.Series(1.0, index=y.index, name="const")).fit(
        cov_type="kernel", kernel="bartlett", bandwidth=None)
    return {"mean": res.params["const"], "t_NW": res.tstats["const"],
            "lags": int(res.cov_config["bandwidth"]), "N": int(res.nobs)}


def plot_type(avg: pd.DataFrame, title: str, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(6.5, 4))
    for signal in SIGNALS:
        ax.scatter(avg.index, avg[signal], color=COLORS[signal], label=LABELS[signal], s=36, zorder=2)
    ax.set_xticks(range(1, 11))
    ax.set_xlabel("Decile")
    ax.set_ylabel("Average excess return (% per month)")
    ax.set_title(title, fontsize=10)
    ax.grid(True, color="0.92", linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def write_tex(hml: pd.DataFrame, path: Path) -> None:
    """Table body: one block per type (mean in percent per month, [t-stat]), one column per signal."""
    lines = [r"\begin{tabular}{llccc}", r"\toprule",
             " & ".join(["Type", "Portfolios"] + [LABELS[s] for s in SIGNALS]) + r" \\", r"\midrule"]
    for name, (weights, rebalancing, breakpoints) in TYPES.items():
        rows = hml[hml["type"] == name].set_index("signal")
        desc = f"{weights}, {rebalancing}, {breakpoints} breakpoints"
        lines.append(" & ".join([f"({name})", desc] + [f"{rows.loc[s, 'mean']:.3f}" for s in SIGNALS]) + r" \\")
        lines.append(" & ".join(["", ""] + [f"[{rows.loc[s, 't_NW']:.2f}]" for s in SIGNALS]) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT.mkdir(exist_ok=True)
    panel = crsp_panel()
    form, ret, rf = formation_table(panel), return_table(panel), load_rf()
    months = ret["yyyymm"].drop_duplicates().sort_values()

    deciles = {(s, b): assign_deciles(form, s, b) for s in SIGNALS for b in ("NYSE", "general")}
    parts = []
    for name, (weights, rebalancing, breakpoints) in TYPES.items():
        for signal in SIGNALS:
            p = portfolio_returns(ret, deciles[signal, breakpoints], weights, rebalancing)
            assert len(p) == 10 * len(months), f"type {name}, {signal}: a decile is empty in some month"
            parts.append(p.assign(type=name, signal=signal))
    port = pd.concat(parts, ignore_index=True)
    port["xret"] = 100 * (port["ret"] - port["yyyymm"].map(rf))      # percent per month
    assert port["xret"].notna().all()
    print(f"return months: {months.iloc[0]} to {months.iloc[-1]} ({len(months)}); "
          f"members per decile-month: min = {port['n'].min()}, median = {port['n'].median():.0f}")

    avg = port.groupby(["type", "signal", "decile"])["xret"].mean().unstack("signal")[list(SIGNALS)]
    wide = port.pivot(index=["type", "signal", "yyyymm"], columns="decile", values="xret")
    hml_series = (wide[10] - wide[1]).rename("hml")
    hml = pd.DataFrame([{"type": t, "signal": s, **newey_west_mean(hml_series.loc[t, s])}
                        for t in TYPES for s in SIGNALS])

    for name, (weights, rebalancing, breakpoints) in TYPES.items():
        print(f"\ntype ({name}): {weights}, {rebalancing}, {breakpoints} breakpoints; "
              f"average excess return by decile, percent per month")
        print(avg.loc[name].T.to_string(float_format=lambda v: f"{v:.3f}"))
        for ext in ("pdf", "png"):
            plot_type(avg.loc[name], f"({name}) {weights}, {rebalancing} rebalancing, {breakpoints} breakpoints",
                      OUT / f"q3c_deciles_{name}.{ext}")
    print("\nHML = decile 10 - decile 1, percent per month")
    print(hml.to_string(index=False, float_format=lambda v: f"{v:.4f}"))

    port[["type", "signal", "yyyymm", "decile", "n", "xret"]].to_csv(
        OUT / "q3c_portfolios.csv", index=False, float_format="%.6f")
    avg.to_csv(OUT / "q3c_decile_averages.csv", float_format="%.6f")
    hml_series.reset_index().to_csv(OUT / "q3c_hml_series.csv", index=False, float_format="%.6f")
    hml.to_csv(OUT / "q3c_hml.csv", index=False, float_format="%.6f")
    write_tex(hml, OUT / "q3c_hml_table.tex")


if __name__ == "__main__":
    main()
