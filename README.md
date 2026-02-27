# Price Tracker

A Python web scraping tool that monitors product prices over time, detects 
price drops, and generates formatted Excel reports with analytics. Built as 
a demonstration of real-world scraping, data persistence, and automated 
reporting workflows.

---

## The Problem This Solves

Manually checking prices across products is time-consuming and easy to forget.
This tool automates the entire workflow — scrape, store, compare, and report —
so price changes are caught automatically and delivered in a clean, 
client-ready Excel format.

---

## Features

- **Web scraping** via requests and BeautifulSoup
- **Price history database** — every scrape session is stored in SQLite,
  building a historical dataset over time
- **Price drop detection** — automatically flags products where price has
  dropped 5% or more across sessions
- **Three-sheet Excel report** generated on demand:
  - **Price Snapshot** — current prices for all tracked products with
    alternating row formatting
  - **Price Drop Alerts** — products with significant price reductions
    highlighted in red
  - **Analytics** — price distribution table and bar chart
- **Category filtering** — scrape the full catalog or target specific
  categories
- **Configurable depth** — control how many pages to scrape per session

---

## Tech Stack

- Python 3.x
- requests
- BeautifulSoup4
- pandas
- openpyxl
- sqlite3 (built-in)

---

## Setup
```bash
# Clone the repository
git clone https://github.com/Brett-Beery/price-tracker.git
cd price-tracker

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install requests beautifulsoup4 pandas openpyxl lxml
```

---

## Usage
```bash
# Run the scraper (scrapes 2 pages by default)
python scraper.py

# Generate Excel report from stored data
python report.py
```

---

## How It Works

1. `scraper.py` fetches product listings from the target site, parses titles,
   prices, ratings, and availability, then saves everything to a local SQLite
   database with a timestamp
2. `database.py` handles all data persistence — products, price history, and
   watchlist management
3. `report.py` reads the database and generates a formatted Excel workbook
   with summary statistics, price drop alerts, and distribution analytics

Running the scraper daily builds a price history that makes the drop
detection and trend analysis increasingly valuable over time.

---

## Adapting to Other Sites

This project uses [Books to Scrape](https://books.toscrape.com) as a 
demonstration target — a site built specifically for scraping practice.
The architecture is designed to be adapted to any retail or e-commerce 
site by modifying the parsing logic in `scraper.py` to match the target 
site's HTML structure.

---

## Roadmap

- GUI interface for managing watchlists and triggering scrapes
- Email/SMS alerts when watched products hit target prices
- Scheduled scraping via cron or Windows Task Scheduler
- Multi-site support with site-specific scraper modules
- Price trend charts embedded directly in the Excel report

---

## Author

Brett Beery — Python developer specializing in automation and data
manipulation.
[GitHub](https://github.com/Brett-Beery) |
[LinkedIn](https://www.linkedin.com/in/brett-beery/)