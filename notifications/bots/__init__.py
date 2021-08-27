from woningzoeker.logging import logger

from .base import Bot
from .telegram import BotTelegram

bots: list[Bot] = [
    BotTelegram()
]

logger.info('Starting all bots...')

for bot in bots:
    bot.start()

logger.info('Finished starting all bots.')

for bot in bots:
    bot.join()
