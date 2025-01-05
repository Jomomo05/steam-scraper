# steamapicollection

A simple **Proof-of-Concept (PoC)** script that scrapes **public Steam API** data and stores it in a **SQLite database**.

This project is designed to demonstrate efficient data extraction, organization, and querying using Steam's **non-official public APIs**. The lightweight script can be containerized and deployed on **small cloud instances (e.g., AWS EC2)** for automation.

---

## **Features**
✅ Uses **Steam’s Public APIs** – No authentication required.  
✅ Scrapes **Steam store data** efficiently.  
✅ Saves structured data into an **optimized SQLite database**.  
✅ Uses **Docker for easy deployment** on small cloud instances.  
✅ Supports **indexing and optimized querying** for performance.

---

## **How It Works**
1. The script **fetches** a list of Steam apps using the **public API**.
2. It **scrapes additional details** for each game (name, price, categories, genres, etc.).
3. The data is stored in a **SQLite database (`steam_games.db`)** inside the `/data` directory.
4. The database schema is **optimized** for better query performance using **indexes and relational tables**.

---


## **Running the Project (Docker)**
Run the following command to start the scraper **inside a Docker container**:
```sh
docker run -d --name steam_scraper_app -v "$(pwd)/data:/app/data" steam_scraper
```
- This bind-mounts the /data directory in your repository to persist the database outside the container.
- The script runs automatically and saves results in data/steam_games.db.
- Logs and output can be checked using
```sh
docker logs -f steam_scraper_app
```

## **Querying the Database**
Once the Scraper is complete, query the data with SQLite:

```sh
sqlite3 data/steam_games.db
```

Query example:

```sql
SELECT
    g.appid,
    g.name,
    g.description,
    g.release_date,
    g.price,
    g.is_free,
    GROUP_CONCAT(DISTINCT c.name) AS categories,
    GROUP_CONCAT(DISTINCT ge.name) AS genres
FROM games g
         LEFT JOIN game_categories gc ON g.appid = gc.game_id
         LEFT JOIN categories c ON gc.category_id = c.id
         LEFT JOIN game_genres gg ON g.appid = gg.game_id
         LEFT JOIN genres ge ON gg.genre_id = ge.id
GROUP BY g.appid
ORDER BY g.name;
```
## **Development Setup**

If you want to run the script locally (without Docker), follow these steps:

1. Install Dependencies
Ensure you have Python 3.12+ installed, then run:
```sh
pip install -r requirements.txt
```
2. Run the Script
```sh
python main.py
```
This will create the steam_games.db file inside the data/ directory.


## **Notes**
This project uses Steam's public, unofficial APIs, which do not require an API key.
For more details, visit the Steam Web API Documentation from @Revadike https://github.com/Revadike/InternalSteamWebAPI

## **Contributing**
- This is a proof-of-concept project, but PRs are welcome!
- As such, some features are not complete such as:
- [ ] Add support for incremental updates to avoid redundant API calls.
- [ ] Implement better error handling and logging.
- [ ] Create a Terraform Script for deploy on AWS.

## **Final Thoughts**
- Feedback is appreciated, feel free to use the code as you wish.