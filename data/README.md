# Data

Both CSV files are provided by the course and are committed to this repository so that the
results can be reproduced from the repository alone.

| File | Original name | Contents |
|---|---|---|
| `eq.csv` | EQ Dataset.csv | Monthly observations (1927:12 to 2021:12) of annual variables: `dp` (log dividend-price ratio), `dg` (log annual dividend growth), `rf` (log annual deflated risk-free return), `re` (log annual deflated equity market return). Excess returns are constructed in the code as e^re - e^rf. See `ps1.pdf` for the definitions. |
| `bond.csv` | Bond Dataset.csv | CRSP Treasury series; the Fama-Bliss discount bond yields (1- to 5-year, `TTERMTYPE` 5001 to 5005, 1952:06 to 2024:12) are the ones used in Question 4. |

## External data for Question 3 (downloaded 2026-09-28)

| File | Source | Contents |
|---|---|---|
| `cz_signals.csv.gz` | Chen and Zimmermann (2022), https://www.openassetpricing.com/, data release 2025.10 (v2.00), obtained with the `openassetpricing` Python package (`OpenAP().dl_signal(..., ['Mom12m','BMdec','GP'], signed=False)`, i.e. the individual predictor files, raw signals; Sign = +1 for all three so signed and raw coincide) | Firm-month panel, columns `permno`, `yyyymm`, `Mom12m`, `BMdec`, `GP`; 4,245,647 rows, 30,551 permnos, 1926:11 to 2026:10, no duplicate `(permno, yyyymm)`. `Mom12m` and `BMdec` end in 2024:12 (CRSP cut-off of the release); `GP` runs to 2026:10 because Compustat annual values are carried forward monthly. `GP` has 24 infinite values (zero total assets). **`BMdec` in this release is the raw BE/ME ratio, not its log** (CZ source `Signals/pyCode/Predictors/BMdec.py`: `BMdec = tempBE / DecME`; 2.7% of values are negative). |
| `raw/CZ_SignalDoc.csv` | same release | Chen-Zimmermann signal documentation (sign, sample, definitions). |
| `dur_firmlevel_2020.csv` | Goncalves (2021b), https://andreigoncalves.com/published-papers/, "Dur Portfolios + Dur Estimates" (zip, 2020-07-24) | Firm-year equity duration: `PERMNO`, `FF.YEAR`, `Dur`; 117,472 rows, FF.YEAR 1973 to 2018. `Dur` is capped near 500 (ranks preserved). |
| `dur_firmlevel_updated2025.csv` | same page, "Dur Portfolios + Dur Estimates (updated to 2025)" (7z, 2026-04-15) | Same layout; 141,498 rows, FF.YEAR 1973 to 2025. Values differ slightly from the 2020 file for overlapping firm-years because of a CRSP data revision (see the author's notes in `raw/`). |
| `raw/Dur_Background_Details_*.txt` | shipped with the two Dur archives | Author's notes (timing: FF.YEAR = t means Dur is available at the end of June of year t). |
| `raw/F-F_Research_Data_Factors.csv` | Ken French data library, "Fama/French 3 Factors" (CSV zip), built from the 2026-08 CRSP database | Original file (monthly block followed by an annual block). |
| `ff3_monthly.csv` | parsed from the file above | Monthly block only: `yyyymm`, `Mkt-RF`, `SMB`, `HML`, `RF`; 1,202 rows, 1926:07 to 2026:08. Values are in percent as in the original (divide by 100 for decimal returns). |

## WRDS data for Question 3 (downloaded by the student on 2026-09-28)

| File | Source (WRDS) | Contents |
|---|---|---|
| `crsp_msf.csv.gz` | CRSP Monthly Stock File, CIZ format (`stkMthSecurityData`; original download name `mvverjsqorilzkp0.csv.gz`) | 4,947,859 rows, 40,039 PERMNOs, `YYYYMM` 1960:01 to 2025:12, 87 columns: security header (`PrimaryExch`, `ShareType`, `SecurityType`, `USIncFlg`, `SICCD`, `NAICS`, ...), monthly data (`MthCalDt`, `MthPrc`, `MthRet`, `MthRetx`, `MthCap`, `MthVol`, `ShrOut`, ...), distribution events (`Dis*` columns) and index returns (`vwretd`, `vwretx`, `ewretd`, `ewretx`, `sprtrn`). **`(PERMNO, YYYYMM)` is not unique**: 56,933 duplicate rows arise when a security has several distribution events in a month (rows differ only in the `Dis*` columns), so drop the `Dis*` columns and de-duplicate before use. CIZ codes replace the legacy ones: `PrimaryExch` N/A/Q (legacy `exchcd` 1/2/3) and `ShareType` NS with `SecurityType` EQTY and `USIncFlg` Y (legacy `shrcd` 10/11). |
| `ccm_funda.csv.gz` | CRSP/Compustat Merged, Fundamentals Annual with link history (original download name `l8xnjkq0saodhazh.csv.gz`) | 341,267 rows, 27,897 GVKEYs, 28,502 LPERMNOs, `datadate` 1955-06-30 to 2026-08-31 (`fyear` 1955 to 2026). Link columns `LINKTYPE` (LU, LC), `LINKPRIM` (P, C, J, N), `LINKDT`, `LINKENDDT` (`E` = still active); Compustat columns `at`, `ceq`, `lt`, `pstk`, `pstkl`, `pstkrv`, `seq`, `txditc`, `sich`, `fyr`, `curcd`, `costat`. All rows are INDL/C/D/STD. `(LPERMNO, datadate)` is unique; `(GVKEY, datadate)` has 2,933 duplicates from multiple links per GVKEY. |
