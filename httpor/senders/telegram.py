import aiohttp

from httpor.config import config
from httpor.logger import getLogger

logger = getLogger(__name__)

class TelegramSender():
    @staticmethod
    async def send(msg, msgtype):
        token = config.services['telegram']['token']
        chat_id = config.services['telegram']['chat_id']
        url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={msg}"

        logger.debug('Sendind message with telegram')
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                await resp.text()
