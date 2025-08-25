Webscraping example

This small project demonstrates scraping product names, prices and images from a search results page and writing them into a CSV and PNG files.

Usage

1. Install dependencies (recommended via Poetry):

	poetry install

2. Run the example scraper:

	python scripts/run_scraper.py "https://www.megatronicashop.com/it/ricerca?controller=search&orderby=position&orderway=desc&search_category=all&s=iphone+16+pro&submit_search=" --out output

3. Results:

	- CSV: output/products.csv (columns: name, price, image_filename)
	- Images: output/images/*.png

Notes

- The scraper uses Requests + BeautifulSoup to parse HTML and Pillow to convert/save images as PNG.
- The parsing selectors are forgiving but may need tweaks if the site structure changes.
