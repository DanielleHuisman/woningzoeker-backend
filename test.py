from corporations.scrapers.base import Scraper


def test(scraper_name: str):
    scraper: Scraper

    if scraper_name == 'domijn':
        # scraper = ScraperDomijn()
        pass
    elif scraper_name == 'dewoonplaats':
        # scraper = ScraperDeWoonplaats()
        pass
    else:
        raise Exception(f'Unknown scraper "{scraper_name}"')

    scraper.scrape()


test('domijn')
