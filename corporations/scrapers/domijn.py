import re
from datetime import datetime

from .base import Scraper
from .util import soup_find_string, parse_price, parse_date, parse_datetime, DUTCH_MONTHS

REACTION_DATE_TIME_REGEX = re.compile(r'(\d{1,2})\s+([a-z]+)\s+(\d{4})\s+om\s+(\d{1,2}):(\d{1,2})')

# TODO: move session/user state management out of the scraper implementations to prevent duplication


class ScraperDomijn(Scraper):

    def base_url(self):
        return 'https://www.domijn.nl'

    def get_residence(self, external_id: str):
        return self.get_residence_by_url(f'${self.base_url()}/woningaanbod/detail/{external_id}')

    def get_residence_by_url(self, url: str):
        soup = self.fetch_html_page(url)

        content = soup.find(id='content-anchor')

        external_id = content.find('form', attrs={'name': 'reactionform'}).attrs['action'].split('/')[-1]
        title = soup_find_string(content.find(class_='title')).split('-')
        # TODO: split address into street and number/suffix
        address = title[0].strip()
        city = title[1].strip()
        neighbourhood = soup_find_string(content.p)

        wrapper_prices = content.find(class_='price').parent.parent.find_all('p')
        price_total = parse_price(soup_find_string(wrapper_prices[0].span))
        price_benefit = parse_price(soup_find_string(wrapper_prices[1]))
        price_base = parse_price(soup_find_string(wrapper_prices[2]))

        table = content.find('dl').find_all('dd')
        available_at = parse_date(soup_find_string(table[1]).strip())
        ended_at = parse_datetime(soup_find_string(table[2]).strip())

        wrapper_properties = content.find(class_='properties')
        properties = [soup_find_string(prop.span.span.span).strip() if prop.span.span.span else prop.span.span.contents[-1].strip()
                      for prop in wrapper_properties.find_all('div', class_='icon-item')]
        energy_label = properties[0]
        # TODO: lookup residence type
        residence_type = properties[1].lower()
        bedrooms = int(properties[2])
        year = int(properties[6])
        rooms = int(properties[7])
        floor = int(properties[9])
        has_elevator = properties[10] == 'ja'
        is_senior = properties[11] == 'ja'

        floor_plan_url = self.base_url() + wrapper_properties.find_next_sibling('a').attrs['href']

        table = content.find(class_='content').find_next_sibling(class_='row').find('dl').find_all('dd')
        price_service = parse_price(soup_find_string(table[1]))

        return {
            'external_id': external_id,
            'type': residence_type,
            # TODO: split address
            # 'street': None,
            # 'number': None,
            # 'city': city,
            'neighbourhood': neighbourhood,
            'price_base': price_base,
            'price_service': price_service,
            'price_benefit': price_benefit,
            'price_total': price_total,
            'available_at': available_at,
            'ended_at': ended_at,
            'year': year,
            'energy_label': energy_label,
            'rooms': rooms,
            'bedrooms': bedrooms,
            'floor': floor,
            'has_elevator': has_elevator,
            'is_senior': is_senior,
            'floor_plan_url': floor_plan_url
        }

    def get_residences(self):
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
                    'price_total': price,
                    'url': url,
                    'image_url': image_url
                })

            page += 1

        for residence in residences:
            # TODO: check if this residence already exists in the database

            result = self.get_residence_by_url(residence['url'])
            residence.update(result)

            break

        self.end_session()

        return residences

    def login(self, identifier: str, credentials: any):
        if not self.has_session():
            self.start_session()

        soup = self.fetch_html_page(f'{self.base_url()}/mijndomijn/inloggen')
        verification_token = soup.find(id='usernameLogin').find('input', attrs={'name': '__RequestVerificationToken'}).attrs['value']

        self.fetch_html_page(f'{self.base_url()}/mijndomijn/inloggen', method='POST', headers={
            'Content-Type': 'application/x-www-form-urlencoded'
        }, data={
            'Email': identifier,
            'Password': credentials,
            'RememberMe': 'False',
            'ReturnUrl': '',
            '__RequestVerificationToken': verification_token
        })

        self.is_logged_in = True

    def logout(self):
        if not self.has_session():
            raise Exception('Already logged out')

        self.fetch_html_page(f'{self.base_url()}/account/logout', params={
            'returnUrl': '/'
        })

        self.is_logged_in = False

    def get_user(self):
        if not self.is_logged_in:
            raise Exception('Not logged in')

        soup = self.fetch_html_page(f'{self.base_url()}/mijndomijn/persoonlijke-gegevens')

        values = soup.find('table', class_='summary-table').tbody.find_all('td')
        name = soup_find_string(values[0])
        phone_number = soup_find_string(values[4])
        email = soup_find_string(values[5])

        return {
            'name': name,
            'email': email,
            'phone_number': phone_number,
        }

    def get_reactions(self):
        if not self.is_logged_in:
            raise Exception('Not logged in')

        reactions = []

        soup = self.fetch_html_page(f'{self.base_url()}/woningzoekende/reageren/overzicht')

        rows = soup.find('table', class_='table-status').tbody.find_all('tr')

        for row in rows:
            columns = row.find_all(['th', 'td'])
            external_id = columns[0].a.attrs['href'].split('/')[-1]
            external_id = external_id[:external_id.index('?')]

            timestamps = REACTION_DATE_TIME_REGEX.findall(''.join(columns[2].text))
            created_at = parse_datetime('{0}-{1}-{2} {3}:{4}'.format(timestamps[0][0], DUTCH_MONTHS[timestamps[0][1]], *timestamps[0][2:5]))
            ended_at = parse_datetime('{0}-{1}-{2} {3}:{4}'.format(timestamps[1][0], DUTCH_MONTHS[timestamps[1][1]], *timestamps[1][2:5]))

            rank_number_text = soup_find_string(columns[3].span).strip().lower()
            rank_number = None if rank_number_text == 'volgt' else int(rank_number_text)

            reactions.append({
                'external_id': external_id,
                'created_at': created_at,
                'ended_at': ended_at,
                'rank_number': rank_number
            })

        return reactions
