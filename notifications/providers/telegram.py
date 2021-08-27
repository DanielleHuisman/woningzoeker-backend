from django.contrib.auth.models import User

from residences.models import Residence, Reaction

from ..models import NotificationProvider
from .base import Provider


class ProviderTelegram(Provider):

    def get_type(self):
        return NotificationProvider.Type.TELEGRAM

    def send_residences_notification(self, user: User, residences: list[Residence]):
        pass

    def send_reactions_notification(self, user: User, reactions: list[Reaction]):
        pass
