BASE_URL = "https://www.eli.ru"
DB_PATH = "data/eli.db"
COUNT = 9000

INDEX_URL = f"{BASE_URL}/catalog/elochnye-ukrasheniya/elochnye-igrushki/?show={COUNT}"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    ),
}