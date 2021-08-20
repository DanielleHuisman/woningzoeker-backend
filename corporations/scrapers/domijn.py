import re

from ..util import soup_find_string
from .base import Scraper


class ScraperDomijn(Scraper):

    def base_url(self):
        return 'https://www.domijn.nl'

    def scrape_residences(self):
        residences = []

        page = 1
        page_count = 1

        while page <= page_count:
            soup = self.fetch_html_page(f'{self.base_url()}/woningaanbod', params={
                'page': page - 1,
                'size': 9
            })

            page_count = len(soup.find('nav', class_='paging').find_all('li'))

            articles = soup.find(id='housingWrapper').find_all('article')

            for article in articles:
                url = article.find('a', class_='js-clickable-link').attrs['href']
                split = url.split('/')
                street = split[3]
                number = split[4]
                postal_code = split[5].replace(' ', '')

                url = self.base_url() + url
                image_url = self.base_url() + article.find('img').attrs['src']

                wrapper_info = article.find(class_='info')
                # address = soup_find_string(wrapper_info.find(class_='title'))
                city = soup_find_string(wrapper_info.find('p'))

                wrapper_price = article.find(class_='price')
                price = int(re.sub(r'\D', '', soup_find_string(wrapper_price.find(class_='price-text'))))

                residences.append({
                    'street': street,
                    'number': number,
                    'postal_code': postal_code,
                    'city': city,
                    'price': price,
                    'url': url,
                    'image_url': image_url
                })

            page += 1

        print(len(residences))
        print(residences)

        # TODO: loop over residences, check if it is in the database, if not scrape the residence page
