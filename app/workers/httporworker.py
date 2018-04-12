import asyncio
from collections import deque
from ..logger import appLogger
from ..services.alarm_service import Zabbix_Service
from ..services.check_service import Check_Service

logger = appLogger(__name__)

class HttporWorker():
    def __init__(self, app):
        self.app = app
        self.loop = app.loop
        self.settings = app['settings']
        self.init_alarm()

    async def run(self):
        queue = asyncio.Queue(loop=self.app.loop)
        producer_coro = self.produce(queue)
        consumer_coro = self.consume(queue)
        self.app['hw_producer'] = self.app.loop.create_task(producer_coro)
        self.app['hw_consumer'] = self.app.loop.create_task(consumer_coro)

    async def produce(self, queue):
        while True:
            logger.debug('Producing queue...')
            await queue.put(self.settings.resources)
            await asyncio.sleep(self.settings.frequency)

    async def consume(self, queue):
        while True:
            resources = await queue.get()
            if 'zabbix' in self.settings.enabled_services:
                zs = Zabbix_Service(self.settings)
                asyncio.ensure_future(zs.send_alive())
            if resources:
                for item, params in resources.items():
                    logger.debug(f"Got item: {item}")
                    host = Check_Service(self.app, item)
                    asyncio.ensure_future(host.check())

    def init_alarm(self):
        self.app['items'] = {}
        for item in self.settings.enabled_resources:
            self.app['items'][item] = {}
            self.app['items'][item]['error'] = False
            #keep last n events
            self.app['items'][item]['history'] = deque(maxlen=1000)
            self.app['items'][item]['fail_sent'] = None
            self.app['items'][item]['recover_sent'] = None
            self.app['items'][item]['statuses'] = list()
