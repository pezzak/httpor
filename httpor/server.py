import asyncio
import signal

from httpor.checker import Checker
from httpor.helper import config
from httpor.sender import Sender
from httpor.utils import get_enabled_services
from httpor.logger import getLogger

signal.signal(signal.SIGINT, signal.SIG_DFL)
logger = getLogger(name=__name__)

class Server():
    def __init__(self):
        self._server()

    async def produce(self, queue):
        while True:
            logger.debug('producing queue')
            await queue.put(config['resources'])
            await asyncio.sleep(config['options']['frequency'])

    async def consume(self, queue):
        while True:
            items = await queue.get()
            if 'zabbix' in get_enabled_services():
                sender = Sender(items.keys())
                asyncio.ensure_future(sender.zabbix_lld())
                asyncio.ensure_future(sender.zabbix_alive())
            for item in items:
                logger.debug('got item: {}'.format(item))
                host = Checker(item, items[item])
                asyncio.ensure_future(host.check())


    def _server(self):
        loop = asyncio.get_event_loop()
        queue = asyncio.Queue(loop=loop)
        producer_coro = self.produce(queue)
        consumer_coro = self.consume(queue)
        logger.info('Starting loop...')
        loop.run_until_complete(asyncio.gather(producer_coro, consumer_coro))
        loop.close()

server = Server()
