from typing import Type

from .base import Scraper
from .dewoonplaats import ScraperDeWoonplaats
from .domijn import ScraperDomijn
from .onshuis import ScraperOnsHuis

scrapers: list[Type[Scraper]] = [
    ScraperDeWoonplaats,
    ScraperDomijn,
    ScraperOnsHuis
]

scrapers_by_name: dict[str, Type[Scraper]] = {}
for scraper in scrapers:
    scrapers_by_name[scraper().get_handle()] = scraper
