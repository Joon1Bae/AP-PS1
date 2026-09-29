"""Q3 common: CRSP firm-month panel, universe, market equity, and loaders for the other
Question 3 data files.

Implements spec/q3_common.md; imported by the Q3 scripts (src/q3a.py, ...).
The CRSP file is in CIZ format with several rows per PERMNO-month. The panel has one row per
PERMNO-month: return and price data from the PERMNO-month, security info (universe fields and
SICCD) from the row with SecInfoStartDt <= MthCalDt <= SecInfoEndDt. The parsed panel is cached
in data/cache/ (git-ignored) and rebuilt when the CRSP file or this module changes.
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CACHE = DATA / "cache"
CRSP = DATA / "crsp_msf.csv.gz"
CZ = DATA / "cz_signals.csv.gz"
FF3 = DATA / "ff3_monthly.csv"

FIRST_SIGNAL, LAST_SIGNAL = 196306, 202412     # signal months tau
FIRST_RETURN, LAST_RETURN = 196307, 202501     # return months tau + 1

INFO_COLS = ["SecInfoStartDt", "SecInfoEndDt", "PrimaryExch", "ConditionalType", "TradingStatusFlg",
             "ShareType", "SecurityType", "SecuritySubType", "USIncFlg", "IssuerType"]
DATA_COLS = ["MthRet", "MthRetFlg", "MthPrc", "ShrOut"]
SIC_EXCLUDED = [(4900, 4949), (6000, 6999)]    # utilities, financials


def month_number(yyyymm):
    """Consecutive month count, so that tau + 1 and tau - k are plain integer arithmetic."""
    return (yyyymm // 100) * 12 + yyyymm % 100 - 1


def to_yyyymm(month):
    return (month // 12) * 100 + month % 12 + 1


def read_crsp() -> pd.DataFrame:
    """Rows of crsp_msf without the Dis* columns and without exact duplicates."""
    cols = ["PERMNO", "YYYYMM", "MthCalDt", "SICCD"] + INFO_COLS + DATA_COLS
    flags = {c: "string" for c in INFO_COLS + ["MthCalDt", "MthRetFlg"]}
    df = pd.read_csv(CRSP, usecols=cols, dtype=flags).drop_duplicates()
    cal = pd.to_datetime(df["MthCalDt"])
    assert (cal.dt.year * 100 + cal.dt.month == df["YYYYMM"]).all(), "YYYYMM is not the month of MthCalDt"
    df["valid_info"] = ((pd.to_datetime(df["SecInfoStartDt"]) <= cal)
                        & (cal <= pd.to_datetime(df["SecInfoEndDt"])))
    return df


def build_panel(df: pd.DataFrame) -> pd.DataFrame:
    """One row per PERMNO-month: ret, prc, shrout, me, security info, filled SIC, universe flag."""
    key = ["PERMNO", "YYYYMM"]
    g = df.groupby(key)
    assert (g["valid_info"].sum() <= 1).all(), "more than one row with valid security info"
    for c in DATA_COLS:
        assert (g[c].nunique(dropna=False) == 1).all(), f"{c} differs within a PERMNO-month"

    base = df.drop_duplicates(key)[key + DATA_COLS]
    info = df.loc[df["valid_info"], key + ["SICCD"] + INFO_COLS[2:]]
    panel = base.merge(info, on=key, how="left", indicator="has_info", validate="one_to_one")
    panel["has_info"] = panel["has_info"] == "both"
    panel = panel.sort_values(key, ignore_index=True)

    # SIC: SICCD at tau; 0 is missing; filled with the PERMNO's most recent earlier non-zero
    # code, else its next later one, searching every month with valid security info in the file
    code = panel["SICCD"].where(panel["has_info"] & (panel["SICCD"] != 0))
    by_permno = code.groupby(panel["PERMNO"])
    panel["sic"] = code.fillna(by_permno.ffill()).fillna(by_permno.bfill())
    panel["sic_source"] = np.select(
        [~panel["has_info"], code.notna(), by_permno.ffill().notna(), panel["sic"].notna()],
        ["no info", "own", "earlier", "later"], default="never")
    excluded = np.zeros(len(panel), dtype=bool)
    for lo, hi in SIC_EXCLUDED:
        excluded |= (panel["sic"] >= lo) & (panel["sic"] <= hi)      # missing SIC is not excluded
    panel["sic_excluded"] = excluded

    panel["me"] = panel["MthPrc"].abs() * panel["ShrOut"]            # $ thousands
    panel["screen"] = (panel["has_info"]
                       & (panel["ShareType"] == "NS") & (panel["SecurityType"] == "EQTY")
                       & (panel["SecuritySubType"] == "COM") & (panel["USIncFlg"] == "Y")
                       & panel["IssuerType"].isin(["ACOR", "CORP"])
                       & panel["PrimaryExch"].isin(["N", "A", "Q"])
                       & (panel["ConditionalType"] == "RW") & (panel["TradingStatusFlg"] == "A")).fillna(False)
    panel["universe"] = panel["screen"] & ~panel["sic_excluded"] & panel["me"].notna()

    panel = panel.rename(columns={"PERMNO": "permno", "YYYYMM": "yyyymm", "MthRet": "ret",
                                  "MthRetFlg": "ret_flag", "MthPrc": "prc", "ShrOut": "shrout"})
    panel["month"] = month_number(panel["yyyymm"])
    keep = ["permno", "yyyymm", "month", "ret", "ret_flag", "prc", "shrout", "me", "PrimaryExch",
            "has_info", "screen", "sic", "sic_source", "sic_excluded", "universe"]
    return panel[keep]


def crsp_panel(refresh: bool = False) -> pd.DataFrame:
    """The firm-month panel (1960:01 to 2025:12), from the cache when it is up to date."""
    path = CACHE / "q3_crsp_panel.pkl"
    newest_input = max(CRSP.stat().st_mtime, Path(__file__).stat().st_mtime)
    if not refresh and path.exists() and path.stat().st_mtime > newest_input:
        return pd.read_pickle(path)
    panel = build_panel(read_crsp())
    CACHE.mkdir(exist_ok=True)
    panel.to_pickle(path)
    return panel


def in_signal_window(yyyymm, first: int = FIRST_SIGNAL, last: int = LAST_SIGNAL):
    return (yyyymm >= first) & (yyyymm <= last)


def load_cz(columns: list[str]) -> pd.DataFrame:
    """Chen-Zimmermann signals dated tau (observed at the end of tau), keyed (permno, yyyymm)."""
    cz = pd.read_csv(CZ, usecols=["permno", "yyyymm"] + columns)
    assert not cz.duplicated(["permno", "yyyymm"]).any()
    return cz


def load_rf() -> pd.Series:
    """Monthly risk-free return in decimals, indexed by yyyymm."""
    ff = pd.read_csv(FF3, usecols=["yyyymm", "RF"])
    return (ff.set_index("yyyymm")["RF"] / 100).rename("rf")


def describe(panel: pd.DataFrame) -> pd.Series:
    """Counts of the universe steps over the signal window."""
    w = panel[in_signal_window(panel["yyyymm"])]
    s = w[w["screen"]]
    return pd.Series({
        "PERMNO-months in window": len(w),
        "without valid security info": int((~w["has_info"]).sum()),
        "pass security screen": len(s),
        "SICCD zero, filled from earlier month": int((s["sic_source"] == "earlier").sum()),
        "SICCD zero, filled from later month": int((s["sic_source"] == "later").sum()),
        "SICCD never non-zero (kept)": int((s["sic_source"] == "never").sum()),
        "removed by SIC ranges": int(s["sic_excluded"].sum()),
        "removed by missing ME": int((~s["sic_excluded"] & s["me"].isna()).sum()),
        "universe": int(w["universe"].sum()),
        "PERMNOs in universe": int(w.loc[w["universe"], "permno"].nunique()),
    })


if __name__ == "__main__":
    print(describe(crsp_panel(refresh=True)).to_string())
