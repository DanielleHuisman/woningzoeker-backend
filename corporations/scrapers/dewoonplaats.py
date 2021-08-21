import json
import re
from typing import Optional, Union

from .base import Scraper
from .util import parse_dutch_date, parse_timestamp

# TODO: move session/user state management out of the scraper implementations to prevent duplication

RANK_NUMBER_REGEX = re.compile(r'uitslag: (\d+)')


class ScraperDeWoonplaats(Scraper):

    def base_url(self):
        return 'https://www.dewoonplaats.nl'

    def get_residence(self, external_id: str):
        return self.get_residence_by_url(f'${self.base_url()}/woningaanbod/detail/{external_id}')

    def get_residence_by_url(self, url: str):
        soup = self.fetch_html_page(url)


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
                'size': 9,
                'advertisementType': 'rent',
                'rentalLimit': 'below'
            })

            page_count = len(soup.find('nav', class_='paging').find_all('li'))

            articles = soup.find(id='housingWrapper').find_all('article')

            for article in articles:


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

        data = self.json_request('POST', f'{self.base_url()}/wh_services/wrd/auth', data={
            'id': 1,
            'method': 'Login',
            'params': [
                f'{self.base_url()}/mijn-woonplaats/',
                identifier,
                credentials,
                False,
                {
                    'challenge': '',
                    'returnto': '',
                    'samlidpreq': ''
                }
            ]
        })

        result = data.get('result', {})
        if not result.get('success', False):
            code = result.get('code')
            raise Exception(f'Failed to login ({code})')

        self.is_logged_in = True

    def logout(self):
        if not self.has_session():
            raise Exception('Already logged out')

        self.fetch(f'{self.base_url()}/.wrd/auth/logout.shtml', params={
            'b': 'mijn-woonplaats/'
        })

        self.is_logged_in = False

        if self.has_session():
            self.end_session()

    def get_user(self):
        if not self.is_logged_in:
            raise Exception('Not logged in')

        soup = self.fetch_html_page(f'{self.base_url()}/mijn-woonplaats/!/mijn-gegevens')

        form = soup.find('form', attrs={'data-formname': 'personaldata'})

        initials = form.find('input', attrs={'name': 'wrd_initials'}).attrs['value']
        last_name = form.find('input', attrs={'name': 'wrd_lastname'}).attrs['value']
        phone_number = form.find('input', attrs={'name': 'wrd_contact_phone'}).attrs['value']
        email = form.find('input', attrs={'name': 'wrd_contact_email'}).attrs['value']

        return {
            'name': f'{initials} {last_name}',
            'email': email,
            'phone_number': phone_number
        }

    def get_reactions(self):
        if not self.is_logged_in:
            raise Exception('Not logged in')

        reactions = []

        soup = self.fetch_html_page(f'{self.base_url()}/mijn-woonplaats/!/mijn-woonvinder')
        ids = soup.find(id='woninglist-replies').attrs['data-woningids'].split(',')

        data = self.json_request('POST', f'{self.base_url()}/wh_services/woonplaats_digitaal/woonvinder', data={
            'id': 1,
            'method': 'ZoekWoningen',
            'params': [
                {
                    'ids': ids,
                    'met_verleden': True
                },
                '',
                True
            ]
        })
        results = data.get('result', {}).get('woningen', [])

        for result in results:
            reactions.append({
                'external_id': result['id'],
                'created_at': parse_dutch_date(result['gereageerd_op']),
                'ended_at': parse_timestamp(result['lotingsdatum']),
                'rank_number': result['volgnummer'] if 'volgnummer' in result and result['volgnummer'] > 0 else None
            })

        return reactions

    def json_request(self, method: str, url: str, data: Optional[Union[list, object]], **kwargs):
        response = self.request(method, url, **kwargs, headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            **(kwargs['headers'] if 'headers' in kwargs else {})
        }, data=json.dumps(data) if data else None)

        response_data = response.json()
        if 'error' in response_data and response_data['error']:
            raise Exception(response_data['error'])

        return response_data
