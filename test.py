from datetime import datetime

from django.contrib.auth.models import User
from django.utils import timezone

from corporations.scrapers.base import Scraper
from corporations.scrapers.dewoonplaats import ScraperDeWoonplaats
from corporations.scrapers.domijn import ScraperDomijn
from corporations.scrapers.onshuis import ScraperOnsHuis
from notifications.util import send_residences_notification, send_reactions_notification
from residences.models import Residence, Reaction


def test_scraper(scraper_name: str):
    scraper: Scraper

    if scraper_name == 'dewoonplaats':
        scraper = ScraperDeWoonplaats()
    elif scraper_name == 'domijn':
        scraper = ScraperDomijn()
    elif scraper_name == 'onshuis':
        scraper = ScraperOnsHuis()
    else:
        raise Exception(f'Unknown scraper "{scraper_name}"')

    print([vars(residence) for residence in scraper.get_residences()])
    # scraper.login('', '')
    # print(scraper.get_user())
    # print(scraper.get_reactions())
    # scraper.logout()


def test_notifications():
    user = User.objects.first()
    timestamp = timezone.make_aware(datetime(2021, 8, 25))

    residences = Residence.objects.filter(city__name='Enschede', reactions_ended_at__gte=timestamp).all()
    send_residences_notification(user, residences)

    reactions = Reaction.objects.filter(rank_number__isnull=False, residence__reactions_ended_at__gte=timestamp).all()
    send_reactions_notification(user, reactions)


test_scraper('onshuis')
# test_notifications()
