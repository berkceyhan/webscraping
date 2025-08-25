#!/usr/bin/env python3
"""Simple runner for the webscraping.scraper module."""
from __future__ import annotations

import argparse
from pathlib import Path

from webscraper.scraper import scrape_to_csv


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="Search page URL to scrape")
    parser.add_argument("--out", default="output", help="Output directory for CSV and images")
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "products.csv"
    images_dir = out_dir / "images"

    scrape_to_csv(args.url, str(csv_path), str(images_dir))


if __name__ == "__main__":
    main()
