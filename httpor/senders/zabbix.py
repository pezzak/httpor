import json
import asyncio

from httpor.config import config
from httpor.logger import getLogger

logger = getLogger(__name__)

class ZabbixSender():

    @staticmethod
    async def send(key, item):
        zbx_config = config.services['zabbix']
        if 'sender' not in zbx_config:
            zbx_config['sender'] = '/usr/bin/zabbix_sender'
        cmd = [zbx_config['sender'],
               "-z", zbx_config['server'],
               "-s", zbx_config['host'],
               "-k", key,
               "-o", item]
        logger.debug("Zabbix sender: key: {} value: {}".format(key, item))
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE)
        stdout, stderr = await process.communicate()
        logger.debug("Zabbix sender: {}".format(stdout))
        if stderr:
            logger.error("Zabbix sender: {}".format(stderr))

    @staticmethod
    async def send_item_data(item, time, status):
        key = 'urlresponsetime[{}]'.format(item)
        await ZabbixSender.send(key, str(time))

        key = 'urlstatus[{}]'.format(item)
        await ZabbixSender.send(key, str(status))

    @staticmethod
    async def send_lld(data):
        lld = list()
        [lld.append({'{#URL}':i}) for i in data]
        lld_json = json.dumps({ 'data': lld })
        await ZabbixSender.send('httpor_discover', lld_json)

    @staticmethod
    async def send_alive():
        await ZabbixSender.send('httpor_alive', '1')
