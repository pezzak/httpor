import json
import asyncio
import aiohttp
from ..logger import appLogger

logger = appLogger(__name__)

class Alarm_Service():

    config = None

    def __init__(self, config):
        self.config = config

    async def send(self, *args):
        raise NotImplementedError('Not implemented')

class Zabbix_Service(Alarm_Service):
    async def send(self, *args):
        zbx_config = self.config.services['zabbix']
        if 'sender' not in zbx_config:
            zbx_config['sender'] = '/usr/bin/zabbix_sender'
        key, item = args
        cmd = [zbx_config['sender'],
               "-z", zbx_config['server'],
               "-s", zbx_config['host'],
               "-k", key,
               "-o", item]
        logger.debug(f"Zabbix_Service: got key [{key}] value [{item}]")
        #https://docs.python.org/3/library/asyncio-dev.html#detect-exceptions-never-consumed
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE)
            stdout = await process.communicate()
            logger.debug("Zabbix_Service: {}".format(stdout))
        except Exception as e:
            logger.error(f"Zabbix_Service: {e}")

    async def send_item_data(self, item, time, status):
        key = f"urlresponsetime[{item}]"
        await self.send(key, str(time))

        key = f"urlstatus[{item}]"
        await self.send(key, str(status))

    async def send_lld(self, data):
        lld = list()
        [lld.append({'{#URL}':i}) for i in data]
        lld_json = json.dumps({ 'data': lld })
        await self.send('httpor_discover', lld_json)

    async def send_alive(self):
        await self.send('httpor_alive', '1')


class Telegram_Service(Alarm_Service):
    async def send(self, *args):
        msg, msgtype = args
        token = self.config.services['telegram']['token']
        chat_id = self.config.services['telegram']['chat_id']
        url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={msg}"

        logger.debug("Telegram_Service: sending message")
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                await resp.text()


class Slack_Service(Alarm_Service):
    async def send(self, *args):
        msg, msgtype = args
        hook = self.config.services['slack']['hook']
        emoji = ':smile:' if msgtype == 'recover' else ':frowning:'
        data = {'text': msg, 'icon_emoji': emoji}

        logger.debug("Slack_Service: sending message")
        async with aiohttp.ClientSession() as session:
            async with session.post(hook, data=json.dumps(data)) as resp:
                await resp.text()


class ServiceFactory():
    @staticmethod
    def factory(type, config):
        if type == "telegram":
            return Telegram_Service(config)
        if type == "slack":
            return Slack_Service(config)

