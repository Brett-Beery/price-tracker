import requests
from bs4 import BeautifulSoup
import pandas as pd
from database import save_price, get_price_history, init_db
import datetime

BASE_URL = "https://books.toscrape.com/catalogue/"
INDEX_URL = "https://books.toscrape.com/catalogue/page-{}.html"

RATING_MAP = {
    "One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5
}

def get_page(url):
    """Fetch a page and return BeautifulSoup object."""
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, "lxml")
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


def scrape_book_detail(detail_url):
    """Scrape detailed info from a book's individual page."""
    soup = get_page(detail_url)
    if not soup:
        return {}

    product_info = {}
    table = soup.find("table", class_="table-striped")
    if table:
        for row in table.find_all("tr"):
            header = row.find("th").text.strip()
            value = row.find("td").text.strip()
            product_info[header] = value

    description = soup.find("meta", {"name": "description"})
    product_info["description"] = description["content"].strip() if description else ""

    return product_info


def scrape_catalog(pages=1, category=None):
    """
    Scrape books from the catalog.
    pages: number of pages to scrape (20 books per page)
    category: optional category URL to filter by
    """
    books = []
    today = datetime.date.today().strftime("%Y-%m-%d")

    for page_num in range(1, pages + 1):
        if category:
            url = category
        else:
            url = INDEX_URL.format(page_num)

        print(f"Scraping page {page_num}: {url}")
        soup = get_page(url)
        if not soup:
            break

        articles = soup.find_all("article", class_="product_pod")
        print(f"  Found {len(articles)} books")

        for article in articles:
            # Title
            title_tag = article.find("h3").find("a")
            title = title_tag["title"]
            relative_url = title_tag["href"].replace("../", "")
            detail_url = BASE_URL + relative_url

            # Price
            price_str = article.find("p", class_="price_color").text.strip()
            price = float(price_str.replace("£", "").replace("Â", "").strip())

            # Rating
            rating_tag = article.find("p", class_="star-rating")
            rating_word = rating_tag["class"][1]
            rating = RATING_MAP.get(rating_word, 0)

            # Availability
            availability = article.find("p", class_="instock").text.strip()

            book = {
                "title": title,
                "price": price,
                "rating": rating,
                "availability": availability,
                "url": detail_url,
                "date_scraped": today
            }

            books.append(book)
            save_price(title, price, detail_url, today)
            print(f"    {title[:50]:<50} £{price:.2f}  {'★' * rating}")

        # Handle pagination for multi-page scrapes
        if not category:
            next_btn = soup.find("li", class_="next")
            if not next_btn:
                print("No more pages.")
                break

    print(f"\nTotal books scraped: {len(books)}")
    return books


def get_categories():
    """Get all available categories from the site."""
    soup = get_page("https://books.toscrape.com")
    if not soup:
        return []

    categories = []
    nav = soup.find("ul", class_="nav-list")
    if nav:
        for link in nav.find_all("a")[1:]:  # Skip "Books" parent
            name = link.text.strip()
            url = "https://books.toscrape.com/" + link["href"]
            categories.append({"name": name, "url": url})

    return categories


if __name__ == "__main__":
    init_db()
    print("=== BOOKS PRICE SCRAPER ===\n")
    
    # Show available categories
    print("Fetching categories...")
    categories = get_categories()
    print(f"Found {len(categories)} categories\n")
    
    # Scrape first 2 pages as a demo
    books = scrape_catalog(pages=2)