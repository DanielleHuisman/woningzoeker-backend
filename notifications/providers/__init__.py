from typing import Type

from ..models import NotificationProvider
from .base import Provider
from .telegram import ProviderTelegram

providers: list[Type[Provider]] = [
    ProviderTelegram
]

providers_by_type: dict[NotificationProvider.Type, Type[Provider]] = {}
for provider in providers:
    providers_by_type[provider().get_type()] = provider
