from django.contrib.auth.models import User
from sentry_sdk import capture_exception

from residences.models import Residence, Reaction
from woningzoeker.logging import logger

from .providers import providers_by_type


def send_residences_notification(user: User, residences: list[Residence]):
    for notification_provider in user.notification_providers.all():
        try:
            provider = providers_by_type[notification_provider.type]()
            provider.send_residences_notification(user, residences)
        except Exception as err:
            logger.error(f'Failed to send residences notification for user "{user.username}" to provider "{notification_provider.type}"')
            logger.exception(err)
            capture_exception(err)


def send_reactions_notification(user: User, reactions: list[Reaction]):
    for notification_provider in user.notification_providers.all():
        try:
            provider = providers_by_type[notification_provider.type]()
            provider.send_reactions_notification(user, reactions)
        except Exception as err:
            logger.error(f'Failed to send reactions notification for user "{user.username}" to provider "{notification_provider.type}"')
            logger.exception(err)
            capture_exception(err)
