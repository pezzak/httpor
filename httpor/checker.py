import time
import aiohttp
import asyncio
import json

from httpor.config import config, statuses
from httpor.utils import get_enabled_services
from httpor.logger import getLogger

from httpor.senders import ZabbixSender

logger = getLogger(__name__)


class Checker():
    def __init__(self, item, req_params):
        self.item = item
        self.type = req_params['type']
        self.url = req_params['url']
        self.expected_text = req_params['expected_text']
        self.expected_code = req_params['expected_code']
        if self.type == 'POST':
            self.data = req_params['data']
        self.timeout = config.timeout
        self.proxy = config.proxy
        self.encoding = req_params['encoding'] if 'encoding' in req_params else 'utf-8'


    async def _request(self):
        res = dict()
        t = time.monotonic()
        try:
            async with aiohttp.ClientSession() as session:
                if self.type == 'GET':
                    async with session.get(self.url,
                                           proxy=self.proxy,
                                           timeout=self.timeout) as resp:
                        res['resp_data'] = await resp.text(encoding=self.encoding)
                if self.type == 'POST':
                    async with session.post(self.url,
                                            data=json.loads(self.data),
                                            proxy=self.proxy,
                                            timeout=self.timeout,
                                            encoding=self.encoding) as resp:
                        res['resp_data'] = await resp.text()
                logger.debug(f"{self.url} status: {resp.status}")
                res['resp_status'] = resp.status
                res['resp_time'] = round(time.monotonic() - t, 3)
                logger.debug(f"{self.url} resp time: {res['resp_time']} sec")
        except asyncio.TimeoutError:
            res['resp_error'] = statuses['ERR_TIMED_OUT']
        except Exception as e:
            res['resp_error'] = statuses['ERR_OTHER']
            logger.error(f"{self.url}: {e}")
        return res


    def _filter(self, response):
        res = {}
        res['status'] = statuses['OK']
        if 'resp_error' in response:
            res['status'] = response['resp_error']
            res['time'] = '-1'
        else:
            res['time'] = response['resp_time']
            e_code = config.resources[self.item]['expected_code']
            if e_code != response['resp_status']:
                res['status'] += statuses['ERR_STATUS_CODE']
                logger.info(f"{self.url} status: {response['resp_status']}")
            e_string = config.resources[self.item]['expected_text']
            if e_string not in response['resp_data']:
                res['status'] += statuses['ERR_STRING_NOT_FOUND']
                logger.info(f"{self.url} expected string not found")
        return res


    async def check(self):
        response = await self._request()
        data = self._filter(response)
        if 'zabbix' in get_enabled_services():
            await ZabbixSender.send_item_data(self.item, data['time'], data['status'])
