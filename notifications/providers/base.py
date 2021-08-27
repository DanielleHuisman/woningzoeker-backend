from django.contrib.auth.models import User

from residences.models import Residence, Reaction

from ..models import NotificationProvider


class Provider:

    def get_type(self) -> NotificationProvider.Type:
        raise NotImplementedError()

    def send_residences_notification(self, user: User, residences: list[Residence]) -> None:
        raise NotImplementedError()

    def send_reactions_notification(self, user: User, reactions: list[Reaction]) -> None:
        raise NotImplementedError()
