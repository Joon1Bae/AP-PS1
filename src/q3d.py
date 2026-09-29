"""Q3d: Fama-MacBeth regressions of excess returns on the cross-firm quantiles of BM_CZ, GP_CZ
and Dur, specifications (i)-(vii), by OLS and by WLS with market-equity weights.

Implements spec/q3d.md with the common rules of spec/q3_common.md (src/q3_common.py).
Run from the repo root:  uv run python src/q3d.py
For each signal month tau, xR_{j,tau+1} (percent per month) is regressed on a constant and the
quantiles Q^X_{j,tau} across the firms in the universe at tau. The Fama-MacBeth estimate is the
time-series mean of the monthly coefficients; t-statistics use the same linearmodels call as
method (v) of src/q2b.py (Bartlett kernel, Newey-West 1994 bandwidth), through src/q3c.py.
"""
from pathlib import Path

import numpy as np
import pandas as pd

from q3_common import crsp_panel, formation_year, in_signal_window, load_cz, load_dur, load_rf
from q3c import newey_west_mean

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"

SIGNALS = ["BM", "GP", "Dur"]                   # column order of the table
FIRST_DUR_SIGNAL = 197306
SPECS = {                                       # regressors, first signal month
    "i": (["BM"], 196306),
    "ii": (["GP"], 196306),
    "iii": (["Dur"], FIRST_DUR_SIGNAL),
    "iv": (["BM", "GP"], 196306),
    "v": (["Dur", "BM"], FIRST_DUR_SIGNAL),
    "vi": (["Dur", "GP"], FIRST_DUR_SIGNAL),
    "vii": (["Dur", "GP", "BM"], FIRST_DUR_SIGNAL),
}
METHODS = ["OLS", "WLS"]


def build_sample(panel: pd.DataFrame) -> pd.DataFrame:
    """Universe firm-months at tau with the quantiles of the signals, ME at tau and xR in tau+1."""
    u = panel.loc[panel["universe"] & in_signal_window(panel["yyyymm"]), ["permno", "yyyymm", "month", "me"]]
    u = u.merge(load_cz(["BMdec", "GP"]).rename(columns={"BMdec": "BM"}),
                on=["permno", "yyyymm"], how="left", validate="one_to_one")
    u = u.assign(t=formation_year(u["yyyymm"])).merge(load_dur(), on=["permno", "t"], how="left",
                                                        validate="many_to_one")
    for s in SIGNALS:
        valid = u[s].notna() & np.isfinite(u[s])
        if s == "BM":
            valid &= u[s] > 0
        x = u[s].where(valid)
        by_month = x.groupby(u["yyyymm"])
        u[f"Q_{s}"] = by_month.rank(method="average") / by_month.transform("count")

    nxt = panel[["permno", "month", "yyyymm", "ret"]].assign(month=panel["month"] - 1)
    nxt = nxt.rename(columns={"yyyymm": "ret_month", "ret": "ret_next"})
    u = u.merge(nxt, on=["permno", "month"], how="left", validate="one_to_one")
    u["xr"] = 100 * (u["ret_next"] - u["ret_month"].map(load_rf()))      # percent per month
    return u


def cross_sections(df: pd.DataFrame, regressors: list[str], weighted: bool) -> pd.DataFrame:
    """Coefficients and N of the regression of xr on a constant and the quantiles, month by month."""
    cols = [f"Q_{s}" for s in regressors]
    rows = []
    for yyyymm, g in df.groupby("yyyymm"):
        X = np.column_stack([np.ones(len(g))] + [g[c].to_numpy() for c in cols])
        y = g["xr"].to_numpy()
        if weighted:
            root = np.sqrt(g["me"].to_numpy())
            X, y = X * root[:, None], y * root
        coef = np.linalg.lstsq(X, y, rcond=None)[0]
        rows.append({"yyyymm": yyyymm, "a": coef[0], **dict(zip([f"b_{s}" for s in regressors], coef[1:])),
                     "N": len(g)})
    return pd.DataFrame(rows)


def fama_macbeth(monthly: pd.DataFrame, regressors: list[str]) -> dict:
    out = {"months": len(monthly), "avg_N": monthly["N"].mean(),
           "first": int(monthly["yyyymm"].iloc[0]), "last": int(monthly["yyyymm"].iloc[-1])}
    for c in ["a"] + [f"b_{s}" for s in regressors]:
        nw = newey_west_mean(monthly[c])
        out[c], out[f"t_{c}"], out[f"lags_{c}"] = nw["mean"], nw["t_NW"], nw["lags"]
    return out


def write_tex(tab: pd.DataFrame, path: Path) -> None:
    """Table body: one block per specification and method (coefficient, [t-stat] below);
    columns a, b_BM, b_GP, b_Dur, average N, number of months."""
    coefs = ["a"] + [f"b_{s}" for s in SIGNALS]
    head = ["", "", "$a$"] + [rf"$b_{{\mathit{{{s}}}}}$" for s in SIGNALS] + ["Avg.\\ $N$", "Months"]
    lines = [r"\begin{tabular}{llcccccc}", r"\toprule", " & ".join(head) + r" \\", r"\midrule"]
    for k, (_, r) in enumerate(tab.iterrows()):
        if k and r["method"] == METHODS[0]:
            lines.append(r"\addlinespace")
        label = f"({r['spec']})" if r["method"] == METHODS[0] else ""
        est = [f"{r[c]:.3f}" if pd.notna(r[c]) else "" for c in coefs]
        tst = [f"[{r[f't_{c}']:.2f}]" if pd.notna(r[c]) else "" for c in coefs]
        lines.append(" & ".join([label, r["method"]] + est + [f"{r['avg_N']:,.0f}", f"{r['months']:d}"]) + r" \\")
        lines.append(" & ".join(["", ""] + tst + ["", ""]) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT.mkdir(exist_ok=True)
    sample = build_sample(crsp_panel())
    assert sample["me"].notna().all()                   # universe at tau requires ME at tau
    monthly, rows = [], []
    for spec, (regressors, first) in SPECS.items():
        need = [f"Q_{s}" for s in regressors] + ["xr"]
        df = sample[(sample["yyyymm"] >= first) & sample[need].notna().all(axis=1)]
        for method in METHODS:
            m = cross_sections(df, regressors, weighted=(method == "WLS"))
            monthly.append(m.assign(spec=spec, method=method))
            rows.append({"spec": spec, "method": method, **fama_macbeth(m, regressors)})
    tab = pd.DataFrame(rows)
    monthly = pd.concat(monthly, ignore_index=True)

    show = ["spec", "method", "a", "t_a"] + [c for s in SIGNALS for c in (f"b_{s}", f"t_b_{s}")]
    print(tab[show + ["avg_N", "months", "first", "last"]].to_string(
        index=False, float_format=lambda v: f"{v:.3f}", na_rep=""))
    lag_cols = [c for c in tab.columns if c.startswith("lags_")]
    print(f"Newey-West (1994) lags: min = {int(tab[lag_cols].min().min())}, max = {int(tab[lag_cols].max().max())}")

    order = ["spec", "method", "yyyymm", "a"] + [f"b_{s}" for s in SIGNALS] + ["N"]
    monthly[order].to_csv(OUT / "q3d_monthly_coefficients.csv", index=False, float_format="%.6f")
    tab.to_csv(OUT / "q3d_fama_macbeth.csv", index=False, float_format="%.6f")
    write_tex(tab, OUT / "q3d_table.tex")


if __name__ == "__main__":
    main()
