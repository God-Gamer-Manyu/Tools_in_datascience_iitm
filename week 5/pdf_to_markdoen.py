"""pdf_to_markdoen.py

Convert an OCRed PDF to Markdown and save as `q10.md`.

Behavior:
- Read the PDF file path from the global variable `STUDENT_MARKS_FILE` (set it before running or modify the default).
- Try to extract text using pdfplumber (preferred). Fall back to PyPDF2 if pdfplumber is not available.
- Apply simple heuristics to turn page text into Markdown:
  - Lines in ALL CAPS or lines followed by a short uppercase line are treated as headings.
  - Lines starting with bullets or numbered lists converted to Markdown lists.
  - Consecutive lines with | or tab-separated values are converted into Markdown tables (best-effort).
  - Preserve blank lines between paragraphs.
- Write the output to `q10.md` in the same directory as this script (or current working dir).
- Attempt to format `q10.md` with Prettier v3.4.2 via `npx prettier@3.4.2 --parser markdown --write q10.md` if `npx` is available.

This script is best-effort: it tries to preserve structure but complex layouts (multi-column PDFs,
images, and deeply nested tables) might not convert perfectly.

Usage:
	- Edit the STUDENT_MARKS_FILE variable below to point to your PDF, or export it as an env var.
	- Install dependencies for best results: pip install pdfplumber PyPDF2
	- Have node (and npx) available if you want Prettier formatting.

"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from typing import List, Optional

try:
	import pdfplumber
except Exception:
	pdfplumber = None

try:
	from PyPDF2 import PdfReader
except Exception:
	PdfReader = None

# === User-configurable global PDF path ===
# Set this to the path of the OCRed PDF to convert.
# You can also set the environment variable STUDENT_MARKS_FILE to override.
STUDENT_MARKS_FILE = "week 5/q-pdf-to-markdown.pdf"


def extract_text_with_pdfplumber(path: str) -> List[str]:
	pages: List[str] = []
	if pdfplumber is None:
		raise RuntimeError("pdfplumber is not installed")
	with pdfplumber.open(path) as pdf:
		for p in pdf.pages:
			# use .extract_text() which works well for OCRed pdfs
			text = p.extract_text() or ""
			pages.append(text)
	return pages


def extract_text_with_pypdf2(path: str) -> List[str]:
	if PdfReader is None:
		raise RuntimeError("PyPDF2 is not installed")
	reader = PdfReader(path)
	pages: List[str] = []
	for p in reader.pages:
		try:
			txt = p.extract_text() or ""
		except Exception:
			txt = ""
		pages.append(txt)
	return pages


def split_lines_preserve(text: str) -> List[str]:
	# Normalize CRLF and split into lines
	text = text.replace("\r\n", "\n").replace("\r", "\n")
	lines = text.split("\n")
	return lines


def is_heading_candidate(line: str) -> bool:
	# Heuristic: short, non-empty, many uppercase letters and few words
	l = line.strip()
	if not l:
		return False
	if len(l) <= 60 and sum(1 for c in l if c.isupper()) >= max(1, len(l) // 6):
		return True
	# If line ends with ':' and is short
	if l.endswith(":") and len(l.split()) <= 6:
		return True
	return False


def detect_table_block(lines: List[str], i: int) -> Optional[int]:
	# If current line contains '|' or tab or multiple spaces as separators, and next lines too,
	# treat a block of consecutive such lines as a table. Return end index (exclusive) or None.
	n = len(lines)
	if i >= n:
		return None
	pattern = re.compile(r"\|\s*|\t|\s{2,}")
	if not pattern.search(lines[i]):
		return None
	j = i
	# require at least 2 lines that look like a row to consider as table
	count = 0
	while j < n and pattern.search(lines[j]):
		count += 1
		j += 1
	if count >= 2:
		return j
	return None


def lines_to_markdown(lines: List[str]) -> str:
	out_lines: List[str] = []
	i = 0
	n = len(lines)
	while i < n:
		line = lines[i].rstrip()
		if not line.strip():
			out_lines.append("")
			i += 1
			continue

		# Table detection
		table_end = detect_table_block(lines, i)
		if table_end is not None and table_end - i >= 1:
			# Simple table conversion: split rows into cells using | or tabs or multi-space
			rows = [re.split(r"\s*\|\s*|\t|\s{2,}", ln.strip()) for ln in lines[i:table_end]]
			# Trim empty leading/trailing cells
			rows = [[cell.strip() for cell in row if cell.strip() != ""] for row in rows]
			if rows:
				# header guess: first row if all cells look like text
				header = rows[0]
				out_lines.append("| " + " | ".join(header) + " |")
				out_lines.append("| " + " | ".join(["---"] * len(header)) + " |")
				for r in rows[1:]:
					# pad to header length
					cells = r + [""] * (len(header) - len(r))
					out_lines.append("| " + " | ".join(cells) + " |")
			i = table_end
			out_lines.append("")
			continue

		# Lists (normalize bullets and numbered lists)
		m = re.match(r"^\s*([\-\*\u2022]|\d+\.)\s+(.+)", line)
		if m:
			marker = m.group(1)
			content = m.group(2).strip()
			# Normalize common bullet markers to '-'
			if re.match(r"^\d+\.", marker):
				out_lines.append(f"1. {convert_urls_in_line(content)}")
			else:
				out_lines.append(f"- {convert_urls_in_line(content)}")
			i += 1
			continue

		# Headings
		if is_heading_candidate(line):
			# Map to H2 or H3 based on length
			lvl = "##" if len(line) > 20 else "###"
			out_lines.append(f"{lvl} {convert_urls_in_line(line.strip())}")
			i += 1
			continue

		# Normal paragraph: join subsequent short lines that likely belong to same paragraph
		para_lines = [line.strip()]
		j = i + 1
		while j < n:
			nxt = lines[j].strip()
			if not nxt:
				break
			# stop if next line looks like heading or list or table starter
			if is_heading_candidate(nxt) or re.match(r"^\s*([\-\*\u2022]|\d+\.)\s+", nxt) or detect_table_block(lines, j):
				break
			# If previous line ends with a hyphenated word, join without space
			if para_lines[-1].endswith("-"):
				para_lines[-1] = para_lines[-1][:-1] + nxt
			else:
				para_lines.append(nxt)
			j += 1
		out_lines.append(convert_urls_in_line(" ".join(para_lines)))
		out_lines.append("")
		i = j

	return "\n".join(out_lines).strip() + "\n"


def convert_urls_in_line(text: str) -> str:
	# Convert http(s) and www links to Markdown [url](url)
	def repl(m: re.Match) -> str:
		url = m.group(0)
		if url.startswith("www."):
			url = "http://" + url
		# avoid double-wrapping if already markdown
		if re.match(r"\[.*\]\(.*\)", text):
			return url
		return f"[{url}]({url})"

	return re.sub(r"https?://[^\s)]+|www\.[^\s)]+", repl, text)


def convert_pages_to_markdown(pages: List[str]) -> str:
	md_pages: List[str] = []
	for pnum, text in enumerate(pages, start=1):
		header = f"<!-- Page {pnum} -->\n\n"
		lines = split_lines_preserve(text)
		md = lines_to_markdown(lines)
		md_pages.append(header + md)
	return "\n\n".join(md_pages)


def write_markdown(md: str, out_path: str) -> None:
	with open(out_path, "w", encoding="utf-8") as f:
		f.write(md)


def try_format_with_prettier(md_path: str) -> bool:
	# Try to run: npx prettier@3.4.2 --parser markdown --write <file>
	cmd = ["npx", "prettier@3.4.2", "--parser", "markdown", "--write", md_path]
	try:
		subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		return True
	except FileNotFoundError:
		print("npx not found; skipping Prettier formatting.")
		return False
	except subprocess.CalledProcessError as e:
		print("Prettier formatting failed:\n", e.stderr.decode(errors="replace"))
		return False


def main() -> int:
	pdf_path = STUDENT_MARKS_FILE
	if not pdf_path or not os.path.isfile(pdf_path):
		print(f"PDF file not found: {pdf_path}")
		return 2

	pages: List[str] = []
	# Try pdfplumber first
	try:
		if pdfplumber is not None:
			pages = extract_text_with_pdfplumber(pdf_path)
		else:
			raise RuntimeError("pdfplumber not available")
	except Exception as e:
		print(f"pdfplumber extraction failed: {e}")
		# Fallback to PyPDF2
		try:
			pages = extract_text_with_pypdf2(pdf_path)
		except Exception as e2:
			print(f"PyPDF2 extraction failed: {e2}")
			return 3

	md = convert_pages_to_markdown(pages)
	out_file = os.path.abspath("q10.md")
	write_markdown(md, out_file)
	print(f"Wrote Markdown to: {out_file}")

	formatted = try_format_with_prettier(out_file)
	if formatted:
		print("Formatted q10.md with Prettier@3.4.2")
	else:
		print("q10.md was written but not formatted with Prettier.")

	return 0


if __name__ == "__main__":
	sys.exit(main())

