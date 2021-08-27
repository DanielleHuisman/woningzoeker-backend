import telebot
from django.conf import settings

from profiles.models import Profile
from profiles.util import generate_token
from woningzoeker.logging import logger

from ..models import NotificationProvider
from .base import Bot

bot = telebot.TeleBot(settings.TELEGRAM_BOT_TOKEN)

# TODO: add end command


@bot.message_handler(commands=['start'])
def handle_start_command(message):
    print(message)

    if message.chat.type != 'private':
        bot.send_message(message.chat.id, 'This bot only works in private chats.')
        return

    provider = NotificationProvider.objects.filter(identifier=str(message.chat.id)).first()
    if provider:
        bot.send_message(message.chat.id, 'You are already registered to receive notifications.')
        return
    else:
        token = message.text[len('/start '):]
        if len(token) == 0:
            # TODO: send registration message
            return

        profile = Profile.objects.filter(token).first()
        if not profile:
            bot.send_message(message.chat.id, 'Unknown registration token, please check if you entered it correctly.')
            return

        # Create notification provider
        provider = NotificationProvider(type=NotificationProvider.Type.TELEGRAM, identifier=str(message.chat.id), credentials=None, user=profile.user)
        provider.save()

        # Generate new profile token
        generate_token(profile)

        bot.send_message(message.chat.id, 'You are successfully registered to receive notifications.')


class BotTelegram(Bot):

    def run(self):
        logger.info('Starting Telegram bot')
        bot.polling()
