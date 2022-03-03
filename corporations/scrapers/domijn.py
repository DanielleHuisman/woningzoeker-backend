from residences.models import Residence

from residences.util import lookup_city, lookup_residence_type, is_existing_residence

from ..models import Corporation
from .base import Scraper, ScrapedReaction
from .util import soup_find_string, parse_price, parse_date, parse_datetime, parse_dutch_datetimes


class ScraperDomijn(Scraper):

    def get_handle(self):
        return 'domijn'

    def base_url(self):
        return 'https://www.domijn.nl'

    def get_residence(self, external_id: str):
        return self.get_residence_by_url(f'{self.base_url()}/woningaanbod/detail/{external_id}')

    def get_residence_by_url(self, url: str):
        soup = self.fetch_html_page(url)

        content = soup.find(id='content-anchor')

        if 'Deze advertentie is niet meer beschikbaar' in str(content):
            return None

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
        available_at = parse_date(soup_find_string(table[1]).strip()) if len(table) >= 2 else None
        ended_at = parse_datetime(soup_find_string(table[2]).strip()) if len(table) >= 3 else None

        wrapper_properties = content.find(class_='properties')
        items = [{
            'icon': prop.i.attrs['class'][-1].split('--')[-1],
            'text': soup_find_string(prop.span.span.span).strip() if prop.span.span.span else prop.span.span.contents[-1].strip()
        } for prop in wrapper_properties.find_all('div', class_='icon-item')]

        properties = {}
        for item in items:
            icon = item['icon']
            while icon in properties:
                icon += '_'
            properties[icon] = item['text']

        energy_label = properties['lamp'] if 'lamp' in properties else None
        residence_type = properties['house'].lower() if 'house' in properties else 'unknown'
        bedrooms = int(properties['bedroom']) if 'bedroom' in properties else None
        year = int(properties['clock']) if 'clock' in properties else None
        rooms = int(properties['door']) if 'door' in properties else None
        floor = (0 if 'begane' in properties['stair'].lower() else int(properties['stair']))\
            if 'stair' in properties else None
        has_elevator = properties['elevator'] == 'ja' if 'elevator' in properties else None
        is_senior = properties['house_'] == 'ja' if 'house_' in properties else None

        link_floor_plan = wrapper_properties.find_next_sibling('a')
        floor_plan_url = self.base_url() + link_floor_plan.attrs['href'] if link_floor_plan is not None else None

        table = content.find(class_='content').find_next_sibling(class_='row').find('dl').find_all('dd')
        price_service = parse_price(soup_find_string(table[1]))

        # TODO: parse additional photos

        return Residence(
            corporation=Corporation.objects.get(handle=self.get_handle()),
            external_id=external_id,
            # TODO: split address
            # 'street': None,
            # 'number': None,
            # 'postal_code': None,
            city=lookup_city(city),
            neighbourhood=neighbourhood,
            type=lookup_residence_type(residence_type),
            # TODO: are other assignment options possible?
            assignment=Residence.Assignment.DRAW,
            price_base=price_base,
            price_service=price_service,
            price_benefit=price_benefit,
            price_total=price_total,
            energy_label=energy_label,
            year=year,
            area=None,
            rooms=rooms,
            bedrooms=bedrooms,
            floor=floor,
            available_at=available_at,
            reactions_ended_at=ended_at,
            has_elevator=has_elevator,
            url=url,
            photo_url=None,
            floor_plan_url=floor_plan_url,
            # TODO: residents, children, possibly improve min/max age
            min_age=65 if is_senior else 0,
            max_age=None
        )

    def get_residences(self):
        residence_stubs = []

        page = 1
        page_count = 1

        while page <= page_count:
            soup = self.fetch_html_page(f'{self.base_url()}/woningaanbod', params={
                'page': page - 1,
                'size': 9,
                'advertisementType': 'rent',
                'rentalLimit': 'below',
                'price-minimum1': 0,
                'price-maximum1': 752
            })

            nav = soup.find('nav', class_='paging')
            if nav:
                page_count = len(nav.find_all('li'))

            articles = soup.find(id='housingWrapper').find_all('article')

            for article in articles:
                url = article.find('a', class_='js-clickable-link').attrs['href']
                split = url.split('/')
                street = split[3]
                number = split[4]
                postal_code = split[5].replace(' ', '')

                url = self.base_url() + url
                photo_url = self.base_url() + article.find('img').attrs['src']

                wrapper_info = article.find(class_='info')
                # address = soup_find_string(wrapper_info.find(class_='title'))
                city = soup_find_string(wrapper_info.find('p'))
                residence_type = soup_find_string(wrapper_info.find(class_='row').div.p)
                residence_type = residence_type.replace('/', '').lower().strip()
                if 'garage' in residence_type:
                    continue

                wrapper_price = article.find(class_='price')
                price = parse_price(soup_find_string(wrapper_price.find(class_='price-text')))

                residence_stubs.append({
                    'street': street,
                    'number': number,
                    'postal_code': postal_code,
                    'city': city,
                    'price_total': price,
                    'url': url,
                    'photo_url': photo_url
                })

            page += 1

        residences = []

        for residence_stub in residence_stubs:
            if is_existing_residence(url=residence_stub['url']):
                continue

            residence = self.get_residence_by_url(residence_stub['url'])

            residence.street = residence_stub['street']
            residence.number = residence_stub['number']
            residence.postal_code = residence_stub['postal_code']
            residence.url = residence_stub['url']
            residence.photo_url = residence_stub['photo_url']
            if not hasattr(residence, 'city'):
                residence.city = lookup_city(residence_stub['city'])

            residences.append(residence)

        return residences

    def login(self, identifier: str, credentials: any):
        soup = self.fetch_html_page(f'{self.base_url()}/mijndomijn/inloggen')
        verification_token = soup.find(id='usernameLogin').find('input', attrs={'name': '__RequestVerificationToken'}).attrs['value']

        self.fetch(f'{self.base_url()}/mijndomijn/inloggen', method='POST', headers={
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

        self.fetch(f'{self.base_url()}/account/logout', params={
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

        reactions: list[ScrapedReaction] = []

        soup = self.fetch_html_page(f'{self.base_url()}/woningzoekende/reageren/overzicht')
        rows = soup.find('table', class_='table-status').tbody.find_all('tr')

        for row in rows:
            columns = row.find_all(['th', 'td'])
            external_id = columns[0].a.attrs['href'].split('/')[-1]
            external_id = external_id[:external_id.index('?')]

            timestamps = parse_dutch_datetimes(''.join(columns[2].text))
            created_at = timestamps[0].date()
            ended_at = timestamps[1]

            rank_number_text = soup_find_string(columns[3].span).strip().lower()
            rank_number = None if rank_number_text == 'volgt' else int(rank_number_text)

            reactions.append({
                'corporation_handle': self.get_handle(),
                'external_id': external_id,
                'created_at': created_at,
                'ended_at': ended_at,
                'rank_number': rank_number,
            })

        return reactions
