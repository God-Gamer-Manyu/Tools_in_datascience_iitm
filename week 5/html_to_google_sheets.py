"""
Fetch the batting stats table from ESPN Cricinfo (page 3) and load into a pandas DataFrame.

Usage:
	python html_to_google_sheets.py

The script will attempt to fetch the page, parse HTML tables with pandas, find the batting table
by looking for a 'Player' column, normalize the header row if needed, clean numeric columns and
save the resulting DataFrame to 'espn_batting_page3.csv' in the script folder.

Notes:
- The remote site may block automated requests; if you get non-200 responses, try running from
  a personal machine or adjust headers/approach (Google Sheets IMPORTHTML is another option).
"""

from __future__ import annotations
import re
import sys
from typing import Optional

import os
import requests
import pandas as pd


DEFAULT_URL = (
	"https://stats.espncricinfo.com/stats/engine/stats/index.html?"
	"class=2;page=3;template=results;type=batting"
)


def fetch_html(url: str, timeout: int = 15) -> str:
	headers = {
		"User-Agent": (
			"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
			"(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
		)
	}
	resp = requests.get(url, headers=headers, timeout=timeout)
	resp.raise_for_status()
	return resp.text


def choose_batting_table(tables: list[pd.DataFrame]) -> Optional[pd.DataFrame]:
	# Pick the table that seems to be the batting stats: look for 'Player' column or 'Mat'/'Runs'
	for df in tables:
		# Reset column names to strings
		cols = list(map(lambda c: str(c).strip(), df.columns.tolist()))
		# Check columns or first row for 'Player'
		first_row = None
		try:
			first_row = df.iloc[0].astype(str).tolist()
		except Exception:
			first_row = []

		searchable = cols + first_row
		combined = "\n".join(searchable)
		if re.search(r"\bPlayer\b", combined, flags=re.IGNORECASE) or (
			re.search(r"\bMat\b", combined, flags=re.IGNORECASE)
			and re.search(r"\bRuns\b", combined, flags=re.IGNORECASE)
		):
			return df.copy()
	return None


def normalize_table(df: pd.DataFrame) -> pd.DataFrame:
	# If first row contains header names (e.g., 'Player'), promote it to header
	first_row = df.iloc[0].astype(str).tolist()
	if any(re.match(r"^Player$", x.strip(), flags=re.IGNORECASE) for x in first_row):
		df = df.copy()
		df.columns = list(map(lambda v: str(v).strip(), first_row))
		df = df.iloc[1:].reset_index(drop=True)
	else:
		# coerce column names to simple strings
		df.columns = list(map(lambda v: str(v).strip(), df.columns.tolist()))

	# Drop repeated header rows that sometimes appear in pages
	if "Player" in df.columns:
		df = df[~df["Player"].astype(str).str.match(r"^Player$", na=False)]

	# Strip whitespace from string/object columns (column-wise to avoid applymap type warnings)
	obj_cols = df.select_dtypes(include=[object, "string"]).columns.tolist()
	for c in obj_cols:
		# convert to string, strip, then restore empty strings to NA
		df[c] = df[c].astype(str).str.strip().replace({"nan": pd.NA, "": pd.NA})

	# Clean numeric columns: remove commas, dashes, and convert to numeric where possible
	def clean_num_col(s: pd.Series) -> pd.Series:
		return pd.to_numeric(
			s.astype(str).str.replace(r"[^0-9.-]", "", regex=True).replace({"": None}),
			errors="coerce",
		)

	# Heuristic numeric columns names often present
	numeric_names = [c for c in df.columns if re.search(r"\b(Mat|Inns|Runs|BF|Ave|SR|100|50|0|HS)\b", c, flags=re.IGNORECASE)]
	for name in numeric_names:
		try:
			df[name] = clean_num_col(df[name])
		except Exception:
			pass

	return df


def main(url: str = DEFAULT_URL) -> int:
	print(f"Fetching: {url}")
	try:
		html = fetch_html(url)
	except requests.HTTPError as e:
		print(f"HTTP error while fetching URL: {e}")
		return 2
	except Exception as e:
		print(f"Error while fetching URL: {e}")
		return 3

	print("Parsing tables with pandas.read_html()...")
	try:
		tables = pd.read_html(html)
	except Exception as e:
		print(f"pandas.read_html failed: {e}")
		return 4

	print(f"Found {len(tables)} tables on the page")
	df = choose_batting_table(tables)
	if df is None:
		print("Could not find a batting table automatically. Available table column samples:")
		for i, t in enumerate(tables[:5]):
			print(f"Table {i} columns: {list(map(str, t.columns.tolist()))[:10]}")
		return 5

	print("Normalizing table and cleaning numeric columns...")
	df_clean = normalize_table(df)

	out_csv = os.path.join(os.path.dirname(__file__), "espn_batting_page3.csv")
	try:
		df_clean.to_csv(out_csv, index=False)
		print(f"Saved cleaned table to: {out_csv}")
	except Exception as e:
		print(f"Failed to save CSV: {e}")

	print("Preview (first 10 rows):")
	with pd.option_context("display.max_columns", None):
		print(df_clean.head(10))

	print(f"Final shape: {df_clean.shape}")
	return 0


if __name__ == "__main__":
	url = DEFAULT_URL
	# allow overriding URL by arg
	if len(sys.argv) > 1:
		url = sys.argv[1]
	exit_code = main(url)
	sys.exit(exit_code)

