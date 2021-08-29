from residences.models import Residence, Reaction

from ..bots.telegram import bot
from ..models import NotificationProvider
from .base import Provider


def format_header(title: str):
    return '<b>{:=^32}</b>'.format(f' {title} ')


class ProviderTelegram(Provider):

    def get_type(self):
        return NotificationProvider.Type.TELEGRAM

    def send_residences_notification(self, notification_provider: NotificationProvider, residences: list[Residence]):
        lines = [('', format_header('New residences'))]

        for residence in residences:
            line = '- <a href="{}">{} - {} {}, {}</a>\n  {} - €{:.2f}'.format(residence.url, residence.corporation.name, residence.street, residence.number,
                                                                               residence.city, residence.pretty_type, residence.price_total / 100)

            if residence.energy_label is not None:
                line += f' - Label {residence.energy_label}'

            if residence.area is not None:
                line += f' - {residence.area} m²'

            lines.append((residence.corporation.name + residence.pretty_address, line))

        lines.sort(key=lambda l: l[0])
        text = '\n'.join([line[1] for line in lines])

        bot.send_message(notification_provider.identifier, text, parse_mode='HTML', disable_web_page_preview=True)

    def send_reactions_notification(self, notification_provider: NotificationProvider, reactions: list[Reaction]):
        lines = [('', format_header('New reaction positions'))]

        for reaction in reactions:
            residence = reaction.residence

            line = '- {} - {} {}, {}\n  Position {}'.format(residence.corporation.name, residence.street, residence.number, residence.city,
                                                            reaction.rank_number)

            lines.append((residence.corporation.name + residence.pretty_address, line))

        lines.sort(key=lambda l: l[0])
        text = '\n'.join([line[1] for line in lines])

        bot.send_message(notification_provider.identifier, text, parse_mode='HTML', disable_web_page_preview=True)
