import asyncio
import signal

from httpor.checker import Checker
from httpor.config import config
from httpor.senders.zabbix import ZabbixSender
from httpor.utils import get_enabled_services
from httpor.logger import getLogger

signal.signal(signal.SIGINT, signal.SIG_DFL)
logger = getLogger(name=__name__)

class Server():
    def __init__(self):
        self._server()

    async def produce(self, queue):
        while True:
            logger.debug('Producing queue...')
            await queue.put(config.resources)
            await asyncio.sleep(config.frequency)

    async def consume(self, queue):
        while True:
            items = await queue.get()
            if 'zabbix' in get_enabled_services():
                asyncio.ensure_future(ZabbixSender.send_alive())
            if items:
                for item in items:
                    logger.debug(f"Got item: {item}")
                    host = Checker(item, items[item])
                    asyncio.ensure_future(host.check())


    def _server(self):
        loop = asyncio.get_event_loop()
        queue = asyncio.Queue(loop=loop)
        producer_coro = self.produce(queue)
        consumer_coro = self.consume(queue)
        logger.info('Starting loop...')
        if 'zabbix' in get_enabled_services():
            loop.run_until_complete(asyncio.ensure_future(ZabbixSender.send_lld(config.resources.keys())))
        loop.run_until_complete(asyncio.gather(producer_coro, consumer_coro))
        loop.close()

server = Server()
