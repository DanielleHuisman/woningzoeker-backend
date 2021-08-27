import telebot
from django.conf import settings

bot = telebot.TeleBot(settings.TELEGRAM_BOT_TOKEN)


@bot.message_handler(commands=['start'])
def handle_start_command(message):
    print(message)


bot.polling()
