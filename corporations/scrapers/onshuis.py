import re

from django.utils import timezone

from residences.models import Residence
from residences.util import lookup_city, lookup_residence_type, is_existing_residence

from ..models import Corporation
from .base import Scraper, ScrapedReaction
from .util import soup_find_string, parse_price, parse_date, parse_datetime, parse_dutch_address

URL_ID_REGEX = re.compile(r'/(\d+)/')


class ScraperOnsHuis(Scraper):

    def get_handle(self):
        return 'onshuis'

    def base_url(self):
        return 'https://mijn.onshuis.com'

    def get_residence(self, external_id: str):
        return self.get_residence_by_url(f'{self.base_url()}/woningaanbod/huur-aanbod/{external_id}/index.html')

    def get_residence_by_url(self, url: str):
        external_id = URL_ID_REGEX.search(url).group(1)

        soup = self.fetch_html_page(url)

        container = soup.find('div', class_='content-box')
        details = container.find('div', class_='details-woningaabod')
        city = details.attrs['data-plaats'].strip().title()
        address = details.attrs['data-select-address']
        address = address.replace(city, '').strip()
        street, number = parse_dutch_address(address)
        reactions_ended_at = parse_datetime(details.attrs['data-reactiedatum'], '%Y%m%d%H%M%S')

        photo_url = self.base_url() + container.find('div', class_='carousel-inner').find('img').attrs['src']

        wrapper_info = container.find(id='main-info-page')
        neighbourhood = soup_find_string(wrapper_info.find('h3', string='Wijk').find_next_sibling(class_='infor-wrapper'))
        residence_type = soup_find_string(wrapper_info.find('h3', string='Woningtype').find_next_sibling(class_='infor-wrapper')).lower()
        has_elevator = 'met lift' in residence_type

        wrapper_area = container.find(id='oppervlaktes-page')
        area = round(float(soup_find_string(wrapper_area.find('h3', string='Woonoppervlakte').find_next_sibling(class_='infor-wrapper'))
                           .replace('m', '').replace(',', '.')))

        wrapper_price = container.find(id='financieel-page')
        price_base = parse_price(soup_find_string(wrapper_price.find('h3', string='Kale huur').find_next_sibling(class_='infor-wrapper')))
        price_service = parse_price(soup_find_string(wrapper_price.find(lambda tag: tag.name == 'h3' and 'Servicekosten ' in tag.strings)
                                                     .find_next_sibling(class_='infor-wrapper')))
        price_total = parse_price(soup_find_string(wrapper_price.find('h3', string='Totale huurprijs').find_next_sibling(class_='infor-wrapper')))
        price_benefit = parse_price(soup_find_string(wrapper_price.find(lambda tag: tag.name == 'h3' and 'Subsidiabele huurprijs ' in tag.strings)
                                                     .find_next_sibling(class_='infor-wrapper')))

        wrapper_price = container.find(id='Woning-page')
        available_at = soup_find_string(wrapper_price.find('h3', string='Beschikbaar per').find_next_sibling(class_='infor-wrapper'))
        available_at = timezone.now().date() if available_at.lower() == 'direct' else parse_date(available_at.strip())
        year = int(soup_find_string(wrapper_price.find('h3', string='Bouwjaar').find_next_sibling(class_='infor-wrapper')))
        bedrooms = int(soup_find_string(wrapper_price.find('h3', string='Aantal slaapkamers').find_next_sibling(class_='infor-wrapper')))
        energy_label = soup_find_string(wrapper_price.find('h3', string='Energielabel').find_next_sibling(class_='infor-wrapper').find('strong')).upper()

        wrapper_downloads = container.find(id='downloads-page')
        floor_plan_url = self.base_url() + wrapper_downloads.find('a').attrs['href'] if wrapper_downloads else None

        return Residence(
            corporation=Corporation.objects.get(handle=self.get_handle()),
            external_id=external_id,
            street=street,
            number=number,
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
            area=area,
            rooms=None,
            bedrooms=bedrooms,
            floor=None,
            available_at=available_at,
            reactions_ended_at=reactions_ended_at,
            has_elevator=has_elevator,
            url=url,
            photo_url=photo_url,
            floor_plan_url=floor_plan_url
            # TODO: age, residents, children
        )

    def get_residences(self):
        residences = []

        soup = self.fetch_html_page(f'{self.base_url()}/woningaanbod', params={
            'filter': '/huur-aanbod'
        })

        container = soup.find('div', class_='aanbodListItems').find_all('div', class_='item')
        for item in container:
            details = item.find('ul', class_='details')
            url = self.base_url() + details.find('a').attrs['href']

            if is_existing_residence(url=url):
                continue

            residences.append(self.get_residence_by_url(url))

        return residences

    def login(self, identifier: str, credentials: any):
        # TODO

        self.is_logged_in = True

    def logout(self):
        if not self.has_session():
            raise Exception('Already logged out')

        # TODO

        self.is_logged_in = False

    def get_user(self):
        if not self.is_logged_in:
            raise Exception('Not logged in')

        # TODO

        return None

    def get_reactions(self):
        if not self.is_logged_in:
            raise Exception('Not logged in')

        reactions: list[ScrapedReaction] = []

        # TODO

        return reactions
