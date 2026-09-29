"""Q3b: book-to-market signal BM from CRSP and Compustat and its validation against the
Chen-Zimmermann BMdec.

Implements spec/q3b.md with the common rules of spec/q3_common.md (src/q3_common.py).
Run from the repo root:  uv run python src/q3b.py
BM of year t = 1000 * BE / ME, with BE from the accounting record with datadate in calendar
year t-1 and ME of the linked PERMNO in December of t-1; it is assigned to the months June t
to May t+1. For each signal month tau, BM_CZ = BMdec (the ratio in levels) is regressed on a
constant and BM across the firms in the universe at tau.
"""
from pathlib import Path

import numpy as np
import pandas as pd

from q3_common import DATA, crsp_panel, in_signal_window, load_cz
from q3a import SERIES, cross_section_ols, plot_series

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"
CCM = DATA / "ccm_funda.csv.gz"

FIRST_YEAR, LAST_YEAR = 1963, 2024     # t: BM_t applies from June t
MIN_EARLIER_RECORDS = 2


def load_ccm() -> pd.DataFrame:
    cols = ["GVKEY", "LPERMNO", "LINKTYPE", "LINKPRIM", "LINKDT", "LINKENDDT", "datadate", "curcd",
            "seq", "ceq", "pstk", "at", "lt", "txditc", "pstkrv", "pstkl"]
    text = {c: "string" for c in ["GVKEY", "LINKTYPE", "LINKPRIM", "LINKDT", "LINKENDDT", "datadate", "curcd"]}
    ccm = pd.read_csv(CCM, usecols=cols, dtype=text).rename(columns={"GVKEY": "gvkey", "LPERMNO": "permno"})
    ccm["datadate"] = pd.to_datetime(ccm["datadate"])
    ccm["link_start"] = pd.to_datetime(ccm["LINKDT"])
    ccm["link_end"] = pd.to_datetime(ccm["LINKENDDT"].where(ccm["LINKENDDT"] != "E"))   # E: still active
    return ccm


def earlier_records(ccm: pd.DataFrame) -> pd.DataFrame:
    """Number of distinct earlier datadates of the same gvkey in the file as delivered."""
    h = ccm[["gvkey", "datadate"]].drop_duplicates().sort_values(["gvkey", "datadate"])
    h["n_earlier"] = h.groupby("gvkey").cumcount()
    return h


def select_records(ccm: pd.DataFrame) -> pd.DataFrame:
    """One accounting record per PERMNO and calendar year of datadate."""
    in_link = (ccm["datadate"] >= ccm["link_start"]) & (ccm["link_end"].isna() | (ccm["datadate"] <= ccm["link_end"]))
    keep = (ccm["LINKTYPE"].isin(["LC", "LU"]) & ccm["LINKPRIM"].isin(["P", "C"]) & in_link
            & (ccm["curcd"] == "USD").fillna(False))
    rec = ccm[keep].merge(earlier_records(ccm), on=["gvkey", "datadate"], validate="many_to_one")
    rec["year"] = rec["datadate"].dt.year
    rec["primary"] = rec["LINKPRIM"] == "P"
    rec = rec.sort_values(["permno", "year", "primary", "datadate"], ascending=[True, True, False, False])
    assert not rec.duplicated(["permno", "year", "primary", "datadate"]).any(), "tie among records"
    return rec.drop_duplicates(["permno", "year"])


def book_equity(rec: pd.DataFrame) -> pd.Series:
    """BE = SE + TXDITC - BVPS in $ millions; missing when SE is unavailable."""
    se = rec["seq"].fillna(rec["ceq"] + rec["pstk"]).fillna(rec["at"] - rec["lt"])
    bvps = rec["pstkrv"].fillna(rec["pstkl"]).fillna(rec["pstk"]).fillna(0)
    return se + rec["txditc"].fillna(0) - bvps


def book_to_market(rec: pd.DataFrame, panel: pd.DataFrame) -> pd.DataFrame:
    """BM_t for every PERMNO and year t, with the December t-1 market equity of the PERMNO."""
    december = panel.loc[panel["yyyymm"] % 100 == 12, ["permno", "yyyymm", "me"]]
    december = december.assign(year=december["yyyymm"] // 100).rename(columns={"me": "me_dec"})
    bm = rec.merge(december[["permno", "year", "me_dec"]], on=["permno", "year"], how="left")
    bm["be"] = book_equity(bm)
    bm["t"] = bm["year"] + 1
    usable = (bm["be"] > 0) & (bm["n_earlier"] >= MIN_EARLIER_RECORDS)
    bm["bm"] = (1000 * bm["be"] / bm["me_dec"]).where(usable)      # BE $ millions, ME $ thousands
    return bm[bm["t"].between(FIRST_YEAR, LAST_YEAR)]


def main() -> None:
    OUT.mkdir(exist_ok=True)
    panel = crsp_panel()
    bm = book_to_market(select_records(load_ccm()), panel)
    print(f"records for t = {FIRST_YEAR}..{LAST_YEAR}: {len(bm)}, SE unavailable: {bm['be'].isna().sum()}, "
          f"BE <= 0: {(bm['be'] <= 0).sum()}, fewer than {MIN_EARLIER_RECORDS} earlier records: "
          f"{(bm['n_earlier'] < MIN_EARLIER_RECORDS).sum()}, no December ME: {bm['me_dec'].isna().sum()}, "
          f"with BM: {bm['bm'].notna().sum()}")

    universe = panel.loc[panel["universe"] & in_signal_window(panel["yyyymm"]), ["permno", "yyyymm"]]
    year, month = universe["yyyymm"] // 100, universe["yyyymm"] % 100
    universe = universe.assign(t=np.where(month >= 6, year, year - 1))       # June t .. May t+1
    df = universe.merge(bm[["permno", "t", "bm"]], on=["permno", "t"], how="left", validate="many_to_one")
    df = df.merge(load_cz(["BMdec"]), on=["permno", "yyyymm"], how="left")
    print(f"universe firm-months: {len(df)}, with BM: {df['bm'].notna().sum()}, "
          f"with BMdec: {df['BMdec'].notna().sum()}, with both: {df[['bm', 'BMdec']].notna().all(axis=1).sum()}")

    both = df.dropna(subset=["bm", "BMdec"]).rename(columns={"bm": "x", "BMdec": "y"})
    assert np.isfinite(both[["x", "y"]]).all().all(), "infinite signal"
    reg = cross_section_ols(both)
    assert len(reg) == universe["yyyymm"].nunique(), "a signal month has no regression"
    gap = (both["y"] - both["x"]).abs()
    print(f"|BMdec - BM|: median = {gap.median():.2e}, share above 1e-3 = {(gap > 1e-3).mean():.4f}")

    print(f"signal months: {reg.index[0]} to {reg.index[-1]} ({len(reg)} regressions)")
    print(reg.agg(["mean", "median", "min", "max"]).T.to_string(float_format=lambda v: f"{v:.4f}"))
    for key in SERIES:
        print(f"{key}: min in {reg[key].idxmin()}, max in {reg[key].idxmax()}")

    reg.to_csv(OUT / "q3b_regressions.csv", float_format="%.8f")
    dates = pd.to_datetime(reg.index.astype(str), format="%Y%m") + pd.offsets.MonthEnd(0)
    for key, label in SERIES.items():
        s = pd.Series(reg[key].to_numpy(), index=dates)
        for ext in ("pdf", "png"):
            plot_series(s, label, 0.0 if key == "intercept" else 1.0, OUT / f"q3b_{key}.{ext}")


if __name__ == "__main__":
    main()
