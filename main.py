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
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS games (
            appid INTEGER PRIMARY KEY,
            name TEXT,
            categories TEXT,
            genres TEXT
        )
    ''')
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
        categories = ", ".join([c["description"] for c in game.get("categories", [])])
        genres = ", ".join([g["description"] for g in game.get("genres", [])])

        # Check if game already exists in DB
        cursor.execute("SELECT COUNT(*) FROM games WHERE appid = ?", (appid,))
        if cursor.fetchone()[0] == 0:  # If game is not in DB, insert it
            cursor.execute(
                "INSERT INTO games (appid, name, categories, genres) VALUES (?, ?, ?, ?)",
                (appid, name, categories, genres)
            )
            print(f"Added: {name} (ID: {appid})")

    conn.commit()
    conn.close()

# --- Main Execution ---
if __name__ == "__main__":
    init_db()  # Ensure the database is initialized
    asyncio.run(process_games())
