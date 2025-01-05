# steamapicollection

A simple Proof-of-Concept Script to Scrape information using the Public Steam APIs.
The data will be saved on a SQLiteDB.

Considerations: The script and data are pretty lightweight, so a container is provided to run on a small vpc like EC2 if needed.

Features TO-DO:
-[x] Uses Steam non-Official APIs for pulling info.
-[x] Includes a Scrapping tool for Steam store data.
-[x] Saves into a SqliteDB.
-[ ] Schema is optimized for querying.

Run with:
```
docker run -d --name steam_scraper_app -v "$(pwd)/data:/app/data" steam_scraper
```

For API usage information see: the public steam API documentation at https://github.com/Revadike/InternalSteamWebAPI by @Revadike.
The current APIs used are do not require any steam key since they are public.

It will automatically get the data on a new data directory.