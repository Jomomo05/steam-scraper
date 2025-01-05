import aiohttp
import asyncio
import sqlite3
import os

STEAM_PRODUCTS_LIST="https://api.steampowered.com/ISteamApps/GetAppList/v2/"
STEAM_APP_DETAIL="https://store.steampowered.com/api/appdetails"

# Define the folder where the database will be stored
DATA_DIR = "/app/data"
os.makedirs(DATA_DIR, exist_ok=True)  # Ensure the directory exists

DB_FILE = os.path.join(DATA_DIR, "steam_games.db")

# API rate limits: 200 requests per 5 minutes (one every 1.5s)
RATE_LIMIT_SEMAPHORE = asyncio.Semaphore(5)  # Allow 5 requests at a time

# --- Database Setup ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS games (
            appid INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            release_date TEXT,
            price INTEGER,
            is_free BOOLEAN
        );

        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS genres (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS game_categories (
            game_id INTEGER,
            category_id INTEGER,
            FOREIGN KEY (game_id) REFERENCES games (appid),
            FOREIGN KEY (category_id) REFERENCES categories (id),
            PRIMARY KEY (game_id, category_id)
        );

        CREATE TABLE IF NOT EXISTS game_genres (
            game_id INTEGER,
            genre_id INTEGER,
            FOREIGN KEY (game_id) REFERENCES games (appid),
            FOREIGN KEY (genre_id) REFERENCES genres (id),
            PRIMARY KEY (game_id, genre_id)
        );

        -- Indexes for faster queries
        CREATE INDEX IF NOT EXISTS idx_games_name ON games (name);
        CREATE INDEX IF NOT EXISTS idx_genres_name ON genres (name);
        CREATE INDEX IF NOT EXISTS idx_categories_name ON categories (name);
        CREATE INDEX IF NOT EXISTS idx_game_categories_game ON game_categories (game_id);
        CREATE INDEX IF NOT EXISTS idx_game_genres_game ON game_genres (game_id);
    """)
    conn.commit()
    conn.close()

async def get_product_list():
    async with aiohttp.ClientSession() as session:
        async with session.get(STEAM_PRODUCTS_LIST) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get("applist", {}).get("apps", [])[:100] # Limit to 50 for demo purposes

async def fetch_game_details(app_id):
    async with RATE_LIMIT_SEMAPHORE:  # Throttle API calls
        params = {"appids": app_id}
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(STEAM_APP_DETAIL, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        game_data = data.get(str(app_id), {})
                        if game_data.get("success") and "data" in game_data:
                            return game_data["data"]
            except Exception as e:
                print(f"[ERROR] Failed to fetch app {app_id}: {e}")
        return None

# --- Process and Save Game Data ---
async def process_games():
    print("Fetching game list...")
    games = await get_product_list()

    print("Filtering game IDs...")
    valid_game_ids = [
        game["appid"] for game in games
        if game.get("name") and "demo" not in game["name"].lower() and "bundle" not in game["name"].lower()
    ]

    print(f"Valid Game IDs found: {len(valid_game_ids)}")

    tasks = [fetch_game_details(app_id) for app_id in valid_game_ids]
    game_details = await asyncio.gather(*tasks)

    # Filter out None results
    game_details = [game for game in game_details if game]

    print(f"Fetched {len(game_details)} valid game details.")

    # Save to database
    save_to_database(game_details)

def save_to_database(games):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    for game in games:
        appid = game.get("steam_appid")
        name = game.get("name", "Unknown")
        description = game.get("short_description", "")
        release_date = game.get("release_date", {}).get("date", "Unknown")
        is_free = game.get("is_free", False)
        price = game.get("price_overview", {}).get("final", 0)  # Price in cents

        # Insert game if not exists
        cursor.execute("""
            INSERT OR IGNORE INTO games (appid, name, description, release_date, price, is_free)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (appid, name, description, release_date, price, is_free))

        # Insert categories
        for category in game.get("categories", []):
            category_name = category["description"]
            cursor.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (category_name,))
            cursor.execute("""
                INSERT OR IGNORE INTO game_categories (game_id, category_id)
                VALUES (?, (SELECT id FROM categories WHERE name = ?))
            """, (appid, category_name))

        # Insert genres
        for genre in game.get("genres", []):
            genre_name = genre["description"]
            cursor.execute("INSERT OR IGNORE INTO genres (name) VALUES (?)", (genre_name,))
            cursor.execute("""
                INSERT OR IGNORE INTO game_genres (game_id, genre_id)
                VALUES (?, (SELECT id FROM genres WHERE name = ?))
            """, (appid, genre_name))

    conn.commit()
    conn.close()

# --- Main Execution ---
if __name__ == "__main__":
    init_db()  # Ensure the database is initialized
    asyncio.run(process_games())
