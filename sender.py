import json
import asyncio
from helper import config, logger

class Sender():
    def __init__(self, data):
        self.data = data


    def _make_lld_data(self):
        res = []
        for i in self.data:
            res.append({'{#URL}':i})
        return res


    async def _sender(self, key, item):
        zbx_config = config['options']['services']['zabbix']
        if 'sender' not in zbx_config:
            zbx_config['sender'] = '/usr/bin/zabbix_sender'
        cmd = [zbx_config['sender'],
               "-z", zbx_config['server'],
               "-s", zbx_config['host'],
               "-k", key,
               "-o", item]
        logger.debug("[Zabbix sender] key: {} value: {}".format(key, item))
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE)
        stdout, stderr = await process.communicate()
        logger.debug("Zabbix sender: {}".format(stdout))
        if stderr:
            logger.error("Zabbix sender: {}".format(stderr))


    async def zabbix(self, url):
        key = 'urlresponsetime[{}]'.format(url)
        await self._sender(key, str(self.data['time']))

        key = 'urlstatus[{}]'.format(url)
        await self._sender(key, str(self.data['status']))


    async def zabbix_lld(self):
        lld_json = json.dumps({ 'data': self._make_lld_data() })
        await self._sender('httpor_discover', lld_json)


    async def zabbix_alive(self):
        await self._sender('httpor_alive', '1')
