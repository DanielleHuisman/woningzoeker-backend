from datetime import datetime

from .base import Scraper
from .util import soup_find_string, parse_price


class ScraperDomijn(Scraper):

    def base_url(self):
        return 'https://www.domijn.nl'

    def scrape_residence(self, external_id: str):
        return self.scrape_residence_by_url(f'${self.base_url()}/woningaanbod/detail/{external_id}')

    def scrape_residence_by_url(self, url: str):
        soup = self.fetch_html_page(url)

        content = soup.find(id='content-anchor')

        external_id = content.find('form', attrs={'name': 'reactionform'}).attrs['action'].split('/')[-1]
        title = soup_find_string(content.find(class_='title')).split('-')
        # TODO: split address into street and number/suffix
        address = title[0].strip()
        city = title[1].strip()

        wrapper_prices = content.find(class_='price').parent.parent.find_all('p')
        price_total = parse_price(soup_find_string(wrapper_prices[0].span))
        price_benefit = parse_price(soup_find_string(wrapper_prices[1]))
        price_base = parse_price(soup_find_string(wrapper_prices[2]))

        table = content.find('dl').find_all('dd')
        available_at = datetime.strptime(soup_find_string(table[1]).strip(), '%d-%m-%Y').date()
        ended_at = datetime.strptime(soup_find_string(table[2]).strip(), '%d-%m-%Y %H:%M')

        # TODO: parse additional info and floor plan

        return {
            'external_id': external_id,
            # TODO: split address
            'street': None,
            'number': None,
            'city': city,
            'price_base': price_base,
            # TODO: consider calculating the service costs
            'price_service': None,
            'price_benefit': price_benefit,
            'price_total': price_total,
            'available_at': available_at,
            'ended_at': ended_at
        }

    def scrape_residences(self):
        self.start_session()

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
                price = parse_price(soup_find_string(wrapper_price.find(class_='price-text')))

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

        for residence in residences:
            # TODO: check if this residence already exists in the database

            result = self.scrape_residence_by_url(residence['url'])
            print(result)

            break

        self.end_session()
