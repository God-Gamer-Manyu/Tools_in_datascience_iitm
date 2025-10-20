"""HNRSSS_api.py

Query HNRSS for latest Hacker News posts mentioning 'AWS' with a minimum of 84 points.
Extract the first <item> and print its <link> URL only.

Usage:
	python HNRSSS_api.py
"""
from __future__ import annotations

import sys
import requests
import xml.etree.ElementTree as ET


def main() -> int:
	# Query HNRSS search endpoint for 'AWS'. We'll filter by points after receiving
	# results because adding unknown parameters can lead to 404 on the service.
	url = "https://hnrss.org/newest"
	params = {"q": "AWS", "points" : 84}
	headers = {"User-Agent": "hnrss-client-example/1.0"}

	try:
		resp = requests.get(url, params=params, headers=headers, timeout=15)
		resp.raise_for_status()
	except Exception as e:
		print(f"Failed to fetch HNRSS: {e}", file=sys.stderr)
		return 2

	# Parse RSS XML
	try:
		root = ET.fromstring(resp.content)
	except ET.ParseError as e:
		print(f"Failed to parse RSS XML: {e}", file=sys.stderr)
		return 3

	# RSS -> channel -> item
	channel = root.find("channel")
	if channel is None:
		print("No channel found in RSS", file=sys.stderr)
		return 4

	# Iterate items (they are ordered newest first) and select the first
	# whose points >= 84. HNRSS includes a namespaced tag for points, e.g. <hn:points>.
	items = channel.findall('item')
	print("Printing latest to oldest")
	for idx, item in enumerate(items, 1):
		print(f"Item {idx} link: {item.findtext('link')}")
	
	print("---------------------")
	print(f"Total items found: {items[0].findtext('link')}")	
	# No matching item found
	print("", end="")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())

