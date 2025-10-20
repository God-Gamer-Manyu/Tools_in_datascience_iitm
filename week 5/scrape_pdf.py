"""Extract student marks from a file and compute total Economics marks for a cohort.

This script expects a global variable FILE_PATH to point to the input file (PDF/CSV/XLSX).
It will try to parse the file using the best available parser in this order:
 - If file is CSV/XLSX: use pandas directly.
 - If file is PDF: try camelot (recommended) then tabula-py as fallback.

It prints a single integer/float: the sum of the 'Economics' column for students
who have English >= 24 and Group between 22 and 51 (inclusive).

Usage:
    Edit FILE_PATH below to point to your file, then run:
        python scrape_pdf.py

Dependencies:
    pandas, camelot, tabula-py (optional), openpyxl (for xlsx), java runtime (for tabula)
"""
from __future__ import annotations

import os
import sys
from typing import Optional

import pandas as pd

# Set this to the path of the PDF/CSV/XLSX file containing the table
FILE_PATH = "week 5/q-extract-tables-from-pdf.pdf"


def try_read_tabular(file_path: str) -> Optional[pd.DataFrame]:
    """Attempt to read CSV/XLSX directly, or fall back to PDF table extractors.
    Returns a DataFrame or None on failure."""
    root, ext = os.path.splitext(file_path.lower())
    # CSV
    if ext == ".csv":
        return pd.read_csv(file_path)
    # Excel
    if ext in (".xls", ".xlsx"):
        return pd.read_excel(file_path)

    # PDF: groups correspond to PDF pages. Read pages 22..51 inclusive and
    # aggregate tables. Prefer tabula-py (requires Java); fall back to camelot.
    all_tables = []
    tabula_available = False
    try:
        # try to import tabula-py robustly
        try:
            from tabula import read_pdf as _tabula_read
            tabula_read = _tabula_read
        except Exception:
            import tabula as _tabmod  # type: ignore

            tabula_read = getattr(_tabmod, "read_pdf", None)

        if tabula_read:
            tabula_available = True
    except Exception:
        tabula_read = None

    for page in range(22, 52):
        page_str = str(page)
        page_tables = []
        if tabula_available and tabula_read:
            try:
                dfs = tabula_read(file_path, pages=page_str, multiple_tables=True)
                if dfs:
                    for df in dfs:
                        if df is None or df.shape[0] == 0:
                            continue
                        # promote header if first row looks like header
                        first_row = df.iloc[0].astype(str).str.strip()
                        non_numeric = first_row.str.match(r"^[^0-9\-\.]+$")
                        if non_numeric.sum() >= max(1, int(len(first_row) / 2)):
                            df.columns = df.iloc[0]
                            df = df[1:].reset_index(drop=True)
                        df["Group"] = page
                        page_tables.append(df)
            except Exception:
                # continue to try camelot for this page
                pass

        if not page_tables:
            # try camelot for this page
            try:
                import camelot

                tables = camelot.read_pdf(file_path, pages=page_str)
                for t in tables:
                    df = t.df
                    if df is None or df.shape[0] == 0:
                        continue
                    df.columns = df.iloc[0]
                    df = df[1:].reset_index(drop=True)
                    df["Group"] = page
                    page_tables.append(df)
            except Exception:
                pass

        all_tables.extend(page_tables)

    if all_tables:
        try:
            combined = pd.concat(all_tables, ignore_index=True, sort=False)
            return combined
        except Exception:
            # as a fallback, return the largest table found
            try:
                return max(all_tables, key=lambda d: d.shape[0] * d.shape[1])
            except Exception:
                return all_tables[0]

    return None


def coerce_columns(df: pd.DataFrame) -> pd.DataFrame:
    # Normalize column names
    cols = {c: str(c).strip() for c in df.columns}
    df = df.rename(columns=cols)

    # Common column name guesses
    col_map = {}
    for c in df.columns:
        lc = c.lower()
        if "english" in lc:
            col_map[c] = "English"
        elif "economics" in lc or "eco" == lc:
            col_map[c] = "Economics"
        elif "group" in lc:
            col_map[c] = "Group"

    df = df.rename(columns=col_map)

    # Try to coerce numeric columns
    for c in ("English", "Economics", "Group"):
        if c in df.columns:
            df[c] = pd.to_numeric(df[c].astype(str).str.replace(r"[^0-9.-]", "", regex=True), errors="coerce")

    return df


def compute_total_economics(df: pd.DataFrame) -> float:
    # Ensure required columns exist
    if not all(k in df.columns for k in ("English", "Economics", "Group")):
        raise ValueError("Required columns not found after parsing. Found: %s" % list(df.columns))

    mask = (df["English"] >= 24) & (df["Group"] >= 22) & (df["Group"] <= 51)
    total = df.loc[mask, "Economics"].sum()
    return float(total)


def main() -> int:
    file_path = FILE_PATH
    if not os.path.exists(file_path):
        print(f"Input file not found: {file_path}", file=sys.stderr)
        return 2

    df = try_read_tabular(file_path)
    if df is None:
        print("Failed to parse tabular data from the input file.", file=sys.stderr)
        return 3

    df = coerce_columns(df)
    try:
        total = compute_total_economics(df)
    except Exception as e:
        print(f"Error computing total: {e}", file=sys.stderr)
        return 4

    # Print the result (as integer if whole, otherwise float)
    if total.is_integer():
        print(int(total))
    else:
        print(total)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
