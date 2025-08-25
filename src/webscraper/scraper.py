from __future__ import annotations

import csv
import os
from dataclasses import dataclass
from io import BytesIO
from typing import Iterable, List

import requests
from bs4 import BeautifulSoup
from PIL import Image


@dataclass
class Product:
    name: str
    price: str
    image_url: str


def fetch_html(url: str, *, timeout: int = 10) -> str:
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    return resp.text


def parse_products(html: str) -> List[Product]:
    soup = BeautifulSoup(html, "lxml")
    products: List[Product] = []

    # The site lists products inside containers with class 'product-container' or 'product-miniature'
    # we'll attempt a forgiving selector to catch product items.
    items = soup.select(".product-miniature, .product-container, .product-listing-item, li.product")
    if not items:
        # fallback: look for articles with product information
        items = soup.select("article, .product")

    for it in items:
        # name
        name_tag = it.select_one(".product-name, a.product-name, h2, h3, .name, .product-title")
        if not name_tag:
            # try anchor text
            name_tag = it.find("a")
        name = name_tag.get_text(strip=True) if name_tag else ""

        # price
        price_tag = it.select_one(".price, .product-price, .product-price-and-shipping, .current-price")
        price = price_tag.get_text(strip=True) if price_tag else ""

        # image
        img_tag = it.select_one("img")
        image_url = img_tag.get("data-src") or img_tag.get("src") if img_tag else ""

        if name and (price or image_url):
            products.append(Product(name=name, price=price, image_url=image_url))

    # Deduplicate by name keeping first occurrence
    seen = set()
    unique: List[Product] = []
    for p in products:
        if p.name in seen:
            continue
        seen.add(p.name)
        unique.append(p)

    return unique


def download_image(url: str, dest_path: str, *, timeout: int = 20) -> None:
    if not url:
        return
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    # Convert to PNG using Pillow to ensure consistent format
    img = Image.open(BytesIO(resp.content)).convert("RGBA")
    img.save(dest_path, format="PNG")


def write_csv(products: Iterable[Product], csv_path: str, images_dir: str) -> None:
    os.makedirs(os.path.dirname(csv_path) or ".", exist_ok=True)
    os.makedirs(images_dir, exist_ok=True)

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "price", "image_filename"])
        for i, p in enumerate(products, start=1):
            # sanitize filename
            safe_name = "_".join(p.name.split())[:100]
            image_filename = f"product_{i}_{safe_name}.png" if p.image_url else ""
            writer.writerow([p.name, p.price, image_filename])
            if p.image_url:
                image_path = os.path.join(images_dir, image_filename)
                try:
                    download_image(p.image_url, image_path)
                except Exception:
                    # skip failing images; keep CSV mapping but leave file absent
                    continue


def scrape_to_csv(url: str, csv_path: str = "products.csv", images_dir: str = "images") -> None:
    html = fetch_html(url)
    products = parse_products(html)
    write_csv(products, csv_path, images_dir)


__all__ = ["Product", "scrape_to_csv", "parse_products", "fetch_html"]
