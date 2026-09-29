"""Q3e: pooled regressions of decile-portfolio excess returns on the portfolios' average firm
deciles in BM_CZ, GP_CZ and Dur, specifications (i)-(vii), for value-weighted and
equal-weighted portfolios, with Driscoll-Kraay (1998) standard errors.

Implements spec/q3e.md with the common rules of spec/q3_common.md (src/q3_common.py).
Run from the repo root:  uv run python src/q3e.py
Portfolios are the annual NYSE-breakpoint deciles of spec/q3c.md (types (i) and (ii)), built
with the functions of src/q3c.py, plus Dur deciles built with the same rules. The bandwidth
of the Bartlett kernel is selected by the routine behind method (v) of src/q2b.py
(linearmodels, Newey-West 1994), applied to the moments summed across portfolios by month.
"""
from pathlib import Path

import numpy as np
import pandas as pd
from linearmodels.iv.covariance import kernel_optimal_bandwidth
from linearmodels.panel import PooledOLS

from q3_common import crsp_panel, formation_year, load_dur, load_rf, to_yyyymm
from q3c import FORMATION_MONTH, assign_deciles, formation_table, return_table

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"

SIGNALS = ["BM", "GP", "Dur"]                   # column order of the table
FIRST_DUR_RETURN = 197307
SPECS = {                                       # regressors, first return month
    "i": (["BM"], 196307),
    "ii": (["GP"], 196307),
    "iii": (["Dur"], FIRST_DUR_RETURN),
    "iv": (["BM", "GP"], 196307),
    "v": (["Dur", "BM"], FIRST_DUR_RETURN),
    "vi": (["Dur", "GP"], FIRST_DUR_RETURN),
    "vii": (["Dur", "GP", "BM"], FIRST_DUR_RETURN),
}
WEIGHTS = {"VW": "Value-weighted portfolios", "EW": "Equal-weighted portfolios"}
Q3C_TYPE = {"VW": "i", "EW": "ii"}              # the same portfolios in output/q3c_portfolios.csv


def firm_deciles(panel: pd.DataFrame) -> pd.DataFrame:
    """Decile of each firm in each signal from the annual NYSE sort at June t (one row per
    permno and June), missing where the firm is not in the sort of that signal."""
    form = formation_table(panel)
    form = form[form["yyyymm"] % 100 == FORMATION_MONTH]
    form = form.assign(t=formation_year(form["yyyymm"])).merge(load_dur(), on=["permno", "t"], how="left",
                                                                validate="one_to_one")
    out = form[["permno", "month"]]
    for s in SIGNALS:
        d = assign_deciles(form, s, "NYSE").rename(columns={"decile": f"d_{s}"})
        out = out.merge(d, on=["permno", "month"], how="left", validate="one_to_one")
    return out.rename(columns={"month": "june"})


def portfolios(members: pd.DataFrame, sort: str, weights: str) -> pd.DataFrame:
    """Return, number of members and average firm deciles of the decile portfolios sorted on
    `sort`, by return month. Averages use the weights of the portfolio return, renormalized
    over the members that have a decile in the signal."""
    m = members[members[f"d_{sort}"].notna()]
    if weights == "VW":
        m = m[m["me_lag"].notna()]
    w = m["me_lag"] if weights == "VW" else pd.Series(1.0, index=m.index)
    cols = {"w": w, "wr": w * m["ret"]}
    for s in SIGNALS:
        cols[f"w_{s}"] = w.where(m[f"d_{s}"].notna(), 0.0)
        cols[f"wd_{s}"] = (w * m[f"d_{s}"]).fillna(0.0)
    sums = pd.DataFrame(cols).groupby([m["yyyymm"], m[f"d_{sort}"].astype(int).rename("decile")]).sum()
    out = pd.DataFrame({"ret": sums["wr"] / sums["w"], "n": m.groupby(["yyyymm", f"d_{sort}"]).size().to_numpy()},
                       index=sums.index)
    for s in SIGNALS:
        out[f"Dec_{s}"] = sums[f"wd_{s}"] / sums[f"w_{s}"].where(sums[f"w_{s}"] > 0)
    assert np.allclose(out[f"Dec_{sort}"], out.index.get_level_values("decile"))
    return out.reset_index().assign(sort=sort, weights=weights)


def check_against_q3c(port: pd.DataFrame) -> None:
    """The BM and GP portfolios are those of Q3c types (i) and (ii)."""
    q3c = pd.read_csv(OUT / "q3c_portfolios.csv")
    for weights, kind in Q3C_TYPE.items():
        for s in ("BM", "GP"):
            a = port[(port["sort"] == s) & (port["weights"] == weights)].set_index(["yyyymm", "decile"])["xret"]
            b = q3c[(q3c["type"] == kind) & (q3c["signal"] == s)].set_index(["yyyymm", "decile"])["xret"]
            assert a.index.equals(b.index) and np.allclose(a, b, atol=1e-5), f"{s} {weights} differs from Q3c"


def driscoll_kraay(df: pd.DataFrame, regressors: list[str]) -> dict:
    """Pooled OLS of xret on a constant and the average deciles, Driscoll-Kraay standard
    errors with the Bartlett kernel and the Newey-West (1994) bandwidth."""
    names = [f"Dec_{s}" for s in regressors]
    data = df.assign(const=1.0, date=pd.to_datetime(df["yyyymm"].astype(str), format="%Y%m"),
                     portfolio=df["sort"] + df["decile"].astype(str)).set_index(["portfolio", "date"])
    y, X = data["xret"], data[["const"] + names]
    assert y.notna().all() and X.notna().all().all(), "missing value in the panel"
    months, n_port = df["yyyymm"].nunique(), data.index.get_level_values("portfolio").nunique()
    assert len(data) == months * n_port, "unbalanced panel"

    beta = np.linalg.lstsq(X.to_numpy(), y.to_numpy(), rcond=None)[0]
    moments = X.mul(y - X.to_numpy() @ beta, axis=0).groupby(level="date").sum().sort_index()
    scores = moments[names].sum(axis=1).to_numpy()[:, None]        # as in q2b(v): constant left out
    lags = kernel_optimal_bandwidth(scores, "bartlett")

    # debiased=False: no degrees-of-freedom factor, as in the linearmodels OLS call of q2b(v)
    res = PooledOLS(y, X).fit(cov_type="kernel", kernel="bartlett", bandwidth=lags, debiased=False)
    assert np.allclose(res.params.to_numpy(), beta)
    out = {"portfolios": n_port, "months": months, "N": int(res.nobs), "lags": int(lags),
           "first": int(df["yyyymm"].min()), "last": int(df["yyyymm"].max()),
           "a": res.params["const"], "t_a": res.tstats["const"]}
    for s, name in zip(regressors, names):
        out[f"b_{s}"], out[f"t_b_{s}"] = res.params[name], res.tstats[name]
    return out


def write_tex(tab: pd.DataFrame, path: Path) -> None:
    """Table body: one panel per weighting, one block per specification (coefficient,
    [t-stat] below); columns a, b_BM, b_GP, b_Dur, number of portfolios and of months."""
    coefs = ["a"] + [f"b_{s}" for s in SIGNALS]
    head = ["", "$a$"] + [rf"$b_{{\mathit{{{s}}}}}$" for s in SIGNALS] + ["Portfolios", "Months"]
    lines = [r"\begin{tabular}{lcccccc}", r"\toprule", " & ".join(head) + r" \\"]
    for weights, title in WEIGHTS.items():
        lines += [r"\midrule", rf"\multicolumn{{7}}{{l}}{{{title}}} \\", r"\addlinespace"]
        for _, r in tab[tab["weights"] == weights].iterrows():
            est = [f"{r[c]:.3f}" if pd.notna(r[c]) else "" for c in coefs]
            tst = [f"[{r[f't_{c}']:.2f}]" if pd.notna(r[c]) else "" for c in coefs]
            lines.append(" & ".join([f"({r['spec']})"] + est + [f"{r['portfolios']:d}", f"{r['months']:d}"]) + r" \\")
            lines.append(" & ".join([""] + tst + ["", ""]) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT.mkdir(exist_ok=True)
    panel = crsp_panel()
    members = return_table(panel).merge(firm_deciles(panel), on=["permno", "june"], how="inner",
                                        validate="many_to_one")
    port = pd.concat([portfolios(members, s, w) for w in WEIGHTS for s in SIGNALS], ignore_index=True)
    port["xret"] = 100 * (port["ret"] - port["yyyymm"].map(load_rf()))       # percent per month
    check_against_q3c(port)
    size = port.groupby(["weights", "sort"]).agg(first=("yyyymm", "min"), last=("yyyymm", "max"),
                                                 rows=("xret", "size"), min_members=("n", "min"))
    print(size.to_string())

    rows = []
    for weights in WEIGHTS:
        for spec, (regressors, first) in SPECS.items():
            df = port[(port["weights"] == weights) & port["sort"].isin(regressors) & (port["yyyymm"] >= first)]
            rows.append({"weights": weights, "spec": spec, **driscoll_kraay(df, regressors)})
    tab = pd.DataFrame(rows)
    show = ["weights", "spec", "a", "t_a"] + [c for s in SIGNALS for c in (f"b_{s}", f"t_b_{s}")]
    print(tab[show + ["portfolios", "months", "lags", "first", "last"]].to_string(
        index=False, float_format=lambda v: f"{v:.3f}", na_rep=""))

    order = ["weights", "sort", "yyyymm", "decile", "n", "xret"] + [f"Dec_{s}" for s in SIGNALS]
    port[order].to_csv(OUT / "q3e_portfolios.csv", index=False, float_format="%.6f")
    tab.to_csv(OUT / "q3e_regressions.csv", index=False, float_format="%.6f")
    write_tex(tab, OUT / "q3e_table.tex")


if __name__ == "__main__":
    main()
