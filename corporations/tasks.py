from django.db import transaction
from django_q.tasks import schedule, Schedule
from sentry_sdk import capture_exception

from corporations.models import Corporation, Registration
from residences.models import Residence, Reaction
from woningzoeker.logging import logger

from .scrapers import scrapers, scrapers_by_name


def add_schedule(name: str, func, **kwargs):
    if not Schedule.objects.filter(name=name).first():
        schedule(func, name=name, **kwargs)


def initialize_tasks():
    add_schedule('scrape_residence', 'corporations.tasks.scrape_residences',
                 schedule_type=Schedule.CRON, cron='00 */2 * * *')

    add_schedule('scrape_reactions', 'corporations.tasks.scrape_reactions',
                 schedule_type=Schedule.CRON, cron='00 */6 * * *')


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
            capture_exception(err)


def scrape_reactions():
    # Fetch registrations
    registrations = Registration.objects.all()

    # Loop over all registrations
    for registration in registrations:
        # Lookup the scraper
        scraper = scrapers_by_name[registration.corporation.handle]
        if not scraper:
            raise Exception(f'Unknown scraper "{registration.corporation.handle}"')

        try:
            with transaction.atomic():
                # Log the user in
                scraper.start_session()
                scraper.login(registration.identifier, registration.credentials)

                # Scrape reactions
                scraped_reactions = scraper.get_reactions()

                # Loop over all reactions
                for scraped_reaction in scraped_reactions:
                    # Find the residence
                    residence = Residence.objects.filter(
                        external_id=scraped_reaction['external_id'],
                        corporation=registration.corporation
                    ).first()

                    if not residence:
                        try:
                            # Attempt to scrape the residence
                            residence = scraper.get_residence(scraped_reaction['external_id'])
                            if residence:
                                # Create the residence
                                residence.corporation = registration.corporation
                                residence.save()
                            else:
                                continue
                        except Exception as err:
                            logger.error(f'Failed to scrape using scraper "{type(scraper).__name__}":')
                            logger.exception(err)
                            capture_exception(err)
                            continue

                    # Check if the reaction already exists
                    reaction = Reaction.objects.filter(residence=residence, registration=registration).first()
                    if not reaction:
                        # Create the reaction
                        reaction = Reaction(
                            created_at=scraped_reaction['created_at'],
                            rank_number=reaction['rank_number'],
                            registration=registration,
                            residence=residence
                        )
                        reaction.save()

                    # Update the reactions end timestamp if necessary
                    if scraped_reaction['ended_at'] and not residence.reactions_ended_at:
                        residence.reactions_ended_at = scraped_reaction['ended_at']
                        residence.save()

                # Log the user out
                scraper.logout()
                scraper.end_session()
        except Exception as err:
            logger.error(f'Failed to scrape using scraper "{type(scraper).__name__}":')
            logger.exception(err)
            capture_exception(err)
