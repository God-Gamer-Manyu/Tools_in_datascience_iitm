"""scrape_mut_links.py

Given a global list `LINKS` of URLs, visit each URL, extract all HTML tables,
sum all numbers (integers and decimals) present in any table cell on those pages,
and print the grand total.

The script tries to use requests + BeautifulSoup. If you prefer, pass a file
containing one URL per line with the --file option.

Usage:
	python scrape_mut_links.py
	python scrape_mut_links.py --file links.txt

"""

from __future__ import annotations

import argparse
import re
import sys
from typing import List

try:
	import requests
	from bs4 import BeautifulSoup
except Exception:
	print("Please install required packages: pip install requests beautifulsoup4")
	raise

# Try to import Playwright sync API for JS-rendered pages
try:
	from playwright.sync_api import sync_playwright
	PLAYWRIGHT_AVAILABLE = True
except Exception:
	sync_playwright = None
	PLAYWRIGHT_AVAILABLE = False

# ====== Global LINKS (replace or set externally) ======
LINKS: List[str] = [
	"https://sanand0.github.io/tdsdata/js_table/?seed=71",
	"https://sanand0.github.io/tdsdata/js_table/?seed=72",
	"https://sanand0.github.io/tdsdata/js_table/?seed=73",
    "https://sanand0.github.io/tdsdata/js_table/?seed=74",
    "https://sanand0.github.io/tdsdata/js_table/?seed=75",
    "https://sanand0.github.io/tdsdata/js_table/?seed=76",
    "https://sanand0.github.io/tdsdata/js_table/?seed=77",
    "https://sanand0.github.io/tdsdata/js_table/?seed=78",
    "https://sanand0.github.io/tdsdata/js_table/?seed=79",
    "https://sanand0.github.io/tdsdata/js_table/?seed=80",
]


number_re = re.compile(r"[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?")


def extract_numbers_from_table(table_tag) -> List[float]:
	nums: List[float] = []
	# find all td and th text
	cells = table_tag.find_all(["td", "th"])
	for c in cells:
		txt = c.get_text(" ", strip=True)
		for m in number_re.finditer(txt):
			try:
				val = float(m.group(0))
				nums.append(val)
			except Exception:
				continue
	return nums


def fetch_html_with_requests(url: str) -> str:
	try:
		r = requests.get(url, timeout=15)
		r.raise_for_status()
		return r.text
	except Exception as e:
		print(f"Failed to fetch {url} with requests: {e}")
		return ""


class PlaywrightRenderer:
	def __init__(self):
		self._pw = None
		self._browser = None

	def start(self):
		if not PLAYWRIGHT_AVAILABLE:
			return
		try:
			# sync_playwright().start() returns a Playwright instance with .chromium/.firefox/.webkit
			self._pw = sync_playwright().start()
			self._browser = self._pw.chromium.launch(headless=True)
		except Exception as e:
			print(f"Playwright start failed: {e}")
			self._pw = None
			self._browser = None

	def render(self, url: str) -> str:
		if not self._browser:
			return ""
		try:
			page = self._browser.new_page()
			page.goto(url, timeout=30000)
			# wait for network to be idle or a short sleep
			page.wait_for_load_state("networkidle", timeout=30000)
			content = page.content()
			page.close()
			return content
		except Exception as e:
			print(f"Playwright render failed for {url}: {e}")
			return ""

	def stop(self):
		try:
			if self._browser:
				self._browser.close()
			if self._pw:
				# self._pw is the Playwright instance returned by start()
				try:
					self._pw.stop()
				except Exception:
					pass
		except Exception:
			pass


def sum_numbers_in_url(url: str, renderer: PlaywrightRenderer | None = None) -> float:
	html = ""
	# Prefer Playwright renderer when available (handles JS-rendered tables)
	if renderer is not None:
		html = renderer.render(url)
		if not html:
			# fallback to requests
			html = fetch_html_with_requests(url)
	else:
		html = fetch_html_with_requests(url)

	if not html:
		return 0.0

	soup = BeautifulSoup(html, "html.parser")
	total = 0.0

	# First, look for real <table> elements
	tables = soup.find_all("table")
	if not tables:
		# fallback: detect plain numeric blocks (JS tables often render as divs/pre)
		# reuse previous heuristic: largest block of numeric lines
		body_text = soup.get_text("\n", strip=True)
		blocks = []
		cur = []
		for ln in body_text.splitlines():
			if number_re.search(ln):
				cur.append(ln)
			else:
				if cur:
					blocks.append("\n".join(cur))
					cur = []
		if cur:
			blocks.append("\n".join(cur))
		if blocks:
			longest = max(blocks, key=lambda b: len(b))
			# sum numbers in longest block by splitting lines and tokens
			for line in longest.splitlines():
				for m in number_re.finditer(line):
					try:
						total += float(m.group(0))
					except Exception:
						pass
			if total:
				print(f"{url} : plain-block sum = {total}")
				return total

	for table in tables:
		nums = extract_numbers_from_table(table)
		if nums:
			s = sum(nums)
			print(f"{url} : table sum = {s}")
			total += s
	return total


def main(argv: List[str] | None = None) -> int:
	p = argparse.ArgumentParser()
	p.add_argument("--file", "-f", help="Path to file with one URL per line")
	args = p.parse_args(argv)

	urls: List[str] = []
	if args.file:
		try:
			with open(args.file, "r", encoding="utf-8") as fh:
				for line in fh:
					u = line.strip()
					if u:
						urls.append(u)
		except Exception as e:
			print(f"Failed to read links file: {e}")
			return 2
	else:
		urls = LINKS

	if not urls:
		print("No URLs provided. Set LINKS in the script or pass --file links.txt")
		return 1

	grand_total = 0.0

	renderer = None
	if PLAYWRIGHT_AVAILABLE:
		renderer = PlaywrightRenderer()
		renderer.start()

	for u in urls:
		print(f"Processing URL: {u}")
		s = sum_numbers_in_url(u, renderer)
		grand_total += s

	if renderer:
		renderer.stop()

	# Print the grand total as integer if it's a whole number, else float
	if abs(grand_total - round(grand_total)) < 1e-9:
		print(int(round(grand_total)))
	else:
		print(grand_total)

	return 0


if __name__ == "__main__":
	sys.exit(main())

