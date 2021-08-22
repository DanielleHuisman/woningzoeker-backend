from .base import Scraper
from .dewoonplaats import ScraperDeWoonplaats
from .domijn import ScraperDomijn

scrapers: list[Scraper] = [
    ScraperDeWoonplaats(),
    ScraperDomijn()
]

scrapers_by_name: dict[str, Scraper] = {}
for scraper in scrapers:
    scrapers_by_name[scraper.get_handle()] = scraper
