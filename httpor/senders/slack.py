import aiohttp
import json

from httpor.config import config
from httpor.logger import getLogger

logger = getLogger(__name__)

class SlackSender():
    @staticmethod
    async def send(msg, msgtype):
        hook = config.services['slack']['hook']
        emoji = ':smile:' if msgtype == 'recover' else ':frowning:'
        data = {'text': msg, 'icon_emoji': emoji}

        logger.debug('Sendind message with slack')
        async with aiohttp.ClientSession() as session:
            async with session.post(hook, data=json.dumps(data)) as resp:
                await resp.text()
