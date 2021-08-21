from corporations.scrapers.base import Scraper
from corporations.scrapers.dewoonplaats import ScraperDeWoonplaats
from corporations.scrapers.domijn import ScraperDomijn


def test(scraper_name: str):
    scraper: Scraper

    if scraper_name == 'dewoonplaats':
        scraper = ScraperDeWoonplaats()
    elif scraper_name == 'domijn':
        scraper = ScraperDomijn()
    else:
        raise Exception(f'Unknown scraper "{scraper_name}"')

    # print(scraper.get_residences())
    scraper.login('', '')
    # print(scraper.get_user())
    print(scraper.get_reactions())
    scraper.logout()


test('dewoonplaats')
