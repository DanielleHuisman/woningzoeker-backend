from corporations.scrapers.base import Scraper
from corporations.scrapers.domijn import ScraperDomijn


def test(scraper_name: str):
    scraper: Scraper

    if scraper_name == 'domijn':
        scraper = ScraperDomijn()
    # elif scraper_name == 'dewoonplaats':
        # scraper = ScraperDeWoonplaats()
        # pass
    else:
        raise Exception(f'Unknown scraper "{scraper_name}"')

    scraper.get_residences()
    # scraper.login('', '')
    # print(scraper.get_user())
    # scraper.logout()


test('domijn')
