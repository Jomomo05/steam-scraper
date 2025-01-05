# steamapicollection

A simple Proof-of-Concept Script to Scrape information using the Public Steam APIs.

Features TO-DO:
-[ ] Uses Steam non-Official APIs for pulling info.
-[ ] Includes a Scrapping tool for Steam store data.
-[ ] Saves into a SqliteDB.
-[ ] Schema is optimized for querying.

Run with:
```
docker run -d --name steam_scraper_app -v "$(pwd)/data:/app/data" steam_scraper
```
It will automatically get the data on a new data directory.