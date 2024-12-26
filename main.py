import aiohttp
import asyncio

STEAM_PRODUCTS_LIST="https://api.steampowered.com/ISteamApps/GetAppList/v2/"
STEAM_APP_DETAIL="https://store.steampowered.com/api/appdetails"

async def get_product_list():
    async with aiohttp.ClientSession() as session:
        async with session.get(STEAM_PRODUCTS_LIST) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get("applist", {}).get("apps", [])[:50] # Limit to 50 for demo purposes

async def fetch_game_details(app_id):
    params = {"appids": app_id}
    async with aiohttp.ClientSession() as session:
        async with session.get(STEAM_APP_DETAIL, params=params) as response:
            if response.status == 200:
                return await response.json()

async def process_games():
    print("Fetching game list...")
    games = await get_product_list()

    print("Filtering game IDs...")
    valid_game_ids = [
        game["appid"] for game in games
        if game.get("name") and "demo" not in game["name"].lower() and "bundle" not in game["name"].lower()
    ]

    print(valid_game_ids)

test = asyncio.run(process_games())
