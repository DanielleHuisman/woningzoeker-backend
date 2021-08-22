import json
import re
from typing import Optional, Union

from residences.models import Residence
from residences.util import lookup_city, lookup_residence_type

from .base import Scraper
from .util import parse_price, parse_dutch_date, parse_dutch_datetime

# TODO: move session/user state management out of the scraper implementations to prevent duplication

URL_ID_REGEX = re.compile(r'/w(\d+)/')
RANK_NUMBER_REGEX = re.compile(r'uitslag: (\d+)')


class ScraperDeWoonplaats(Scraper):

    def get_handle(self):
        return 'dewoonplaats'

    def base_url(self):
        return 'https://www.dewoonplaats.nl'

    def convert_residence(self, result: dict):
        external_id = result['id']

        # TODO: parse additional photos

        return Residence(
            external_id=external_id,
            street=result['straat'],
            number=result['huisnummer'] + result['huisnummertoevoeging'],
            postal_code=result['postcode'].replace(' ', ''),
            city=lookup_city(result['plaats']),
            type=lookup_residence_type(result['soort'][0].lower(), result['woningtype'].lower()),
            neighbourhood=result['wijk'].split('-')[-1].strip(),
            price_base=int(result['relevante_huurprijs'] * 100),
            price_service=parse_price(result['servicekosten']),
            price_benefit=parse_price(result['toeslagprijs']),
            price_total=parse_price(result['brutoprijs']),
            energy_label=result['energielabel'][0:1],
            year=result['bouwjaar'],
            area=round(float(result['woonoppervlak'].replace(',', '.'))) if len(result['woonoppervlak']) > 0 else None,
            rooms=None,
            bedrooms=result['slaapkamers'],
            floor=int(result['etage']) if len(result['etage']) > 0 and 'begane' not in result['etage'].lower() else 0,
            has_elevator=result['lift'],
            available_at=parse_dutch_date(result['aanvaardingsdatum']),
            reactions_ended_at=parse_dutch_datetime(result['reactiedatum']),
            url=f'{self.base_url()}/ik-zoek-woonruimte/!/woning/{external_id}',
            photo_url=self.base_url() + result['overview'],
            floor_plan_url=None
            # TODO: also include result['criteria'] (e.g. 55+)
            # is_senior='senior' in result['woningtype'].lower()
        )

    def get_residence(self, external_id: str):
        data = self.json_request('POST', f'{self.base_url()}/wh_services/woonplaats_digitaal/woonvinder', data={
            'id': 1,
            'method': 'ZoekWoningen',
            'params': [
                {
                    'ids': [external_id],
                    'met_verleden': True
                },
                '',
                True
            ]
        })

        result = data.get('result', {}).get('woningen', [])[0]
        return self.convert_residence(result)

    def get_residence_by_url(self, url: str):
        external_id = URL_ID_REGEX.search(url).group(1)
        return self.get_residence(external_id)

    def get_residences(self):
        data = self.json_request('POST', f'{self.base_url()}/wh_services/woonplaats_digitaal/woonvinder', data={
            'id': 1,
            'method': 'ZoekWoningen',
            'params': [
                {
                    'tehuur': True,
                    'prijstot': 752.33
                },
                '',
                True
            ]
        })

        results = data.get('result', {}).get('woningen', [])
        residences = [self.convert_residence(result) for result in results if result['soort'][0].lower() != 'parkeren']

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
                'ended_at': parse_dutch_datetime(result['reactiedatum']),
                'rank_number': result['volgnummer'] if 'volgnummer' in result and result['volgnummer'] > 0 else None
            })

        return reactions

    def json_request(self, method: str, url: str, data: Optional[Union[list, dict]], **kwargs):
        response = self.request(method, url, **kwargs, headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            **(kwargs['headers'] if 'headers' in kwargs else {})
        }, data=json.dumps(data) if data else None)

        # The API always returns status 200, so check the response data for errors
        response_data = response.json()
        if 'error' in response_data and response_data['error']:
            raise Exception(response_data['error'])

        return response_data
