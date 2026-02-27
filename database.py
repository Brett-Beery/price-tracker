import sqlite3
import datetime
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "price_tracker.db")

def init_db():
    """Initialize database and create tables."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            url TEXT UNIQUE NOT NULL,
            category TEXT,
            date_added TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            price REAL NOT NULL,
            url TEXT NOT NULL,
            date_scraped TEXT NOT NULL,
            UNIQUE(title, date_scraped)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS watchlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE NOT NULL,
            target_price REAL,
            date_added TEXT DEFAULT CURRENT_TIMESTAMP,
            notes TEXT
        )
    ''')

    conn.commit()
    conn.close()
    print("Database initialized.")


def save_price(title, price, url, date_scraped):
    """Save a price record."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Upsert product
    c.execute('''
        INSERT OR IGNORE INTO products (title, url)
        VALUES (?, ?)
    ''', (title, url))

    # Save price history
    c.execute('''
        INSERT OR REPLACE INTO price_history (title, price, url, date_scraped)
        VALUES (?, ?, ?, ?)
    ''', (title, price, url, date_scraped))

    conn.commit()
    conn.close()


def get_price_history(title):
    """Get full price history for a product."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT title, price, date_scraped
        FROM price_history
        WHERE title = ?
        ORDER BY date_scraped ASC
    ''', (title,))
    rows = c.fetchall()
    conn.close()
    return rows


def get_all_latest_prices():
    """Get the most recent price for every tracked product."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT title, price, date_scraped
        FROM price_history
        WHERE (title, date_scraped) IN (
            SELECT title, MAX(date_scraped)
            FROM price_history
            GROUP BY title
        )
        ORDER BY title
    ''')
    rows = c.fetchall()
    conn.close()
    return rows


def get_price_drops(threshold_pct=5.0):
    """Find products where price dropped by more than threshold %."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT title, MIN(price) as low, MAX(price) as high,
               MAX(price) - MIN(price) as drop_amount,
               ROUND((MAX(price) - MIN(price)) / MAX(price) * 100, 2) as drop_pct
        FROM price_history
        GROUP BY title
        HAVING drop_pct >= ?
        ORDER BY drop_pct DESC
    ''', (threshold_pct,))
    rows = c.fetchall()
    conn.close()
    return rows


def add_to_watchlist(title, target_price=None, notes=None):
    """Add a product to the watchlist."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO watchlist (title, target_price, notes)
            VALUES (?, ?, ?)
        ''', (title, target_price, notes))
        conn.commit()
        print(f"Added to watchlist: {title}")
    except sqlite3.IntegrityError:
        print(f"Already on watchlist: {title}")
    conn.close()


if __name__ == "__main__":
    init_db()
    print("Database ready.")