from django.db import transaction
from django_q.tasks import schedule, Schedule

from corporations.models import Corporation
from residences.models import Residence
from woningzoeker.logging import logger

from .scrapers import scrapers

# TODO: add scrape_reactions task


def initialize_tasks():
    if not Schedule.objects.filter(name='scrape_residences').first():
        schedule('corporations.tasks.scrape_residences', name='scrape_residences', schedule_type=Schedule.CRON, cron='00 */2 * * *')


def scrape_residences():
    # Loop over all scrapers
    for scraper in scrapers:
        try:
            with transaction.atomic():
                # Find corporation
                corporation = Corporation.objects.filter(handle=scraper.get_handle()).first()
                if not corporation:
                    raise Exception(f'Unknown corporation "{scraper.get_handle()}"')

                # Scrape residences
                scraper.start_session()
                residences = scraper.get_residences()
                scraper.end_session()

                # Loop over all scraped residences
                for residence in residences:
                    # Check if the residence already exists
                    if Residence.objects.filter(external_id=residence.external_id, corporation=corporation).count() > 0:
                        continue

                    # Create the residence
                    residence.corporation = corporation
                    residence.save()

            # TODO: check if any users should be notified of new residences
        except Exception as err:
            logger.error(f'Failed to scrape using scraper "{type(scraper).__name__}":')
            logger.exception(err)
