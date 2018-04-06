import time
import aiohttp
import asyncio
import json

from .alarm_service import Zabbix_Service, ServiceFactory
from ..logger import appLogger

# from httpor.config import config, statuses
# from httpor.utils import get_enabled_services, alarm_status, get_status_name
# from httpor.logger import getLogger

# from httpor.senders import ZabbixSender, send_all_services

logger = appLogger(__name__)


class Check_Service():
    """
    Args
    -------
    item (str): Item key from resources.
    req_params (dict): Request params.
    """
    def __init__(self, app, item):
        self.app = app
        self.item = item
        self.settings = app['settings']
        self.statuses = self.settings.statuses
        self.type = self.settings.resources[item]['type']
        self.url = self.settings.resources[item]['url']
        self.expected_text = self.settings.resources[item]['expected_text']
        self.expected_code = self.settings.resources[item]['expected_code']
        if self.type == 'POST':
            self.data = self.settings.resources[item]['data']
        self.timeout = self.settings.timeout
        self.proxy = None
        if 'use_proxy' in self.settings.resources[item]:
            self.proxy = self.settings.resources[item]['use_proxy']
        self.encoding = 'utf-8'
        if 'encoding' in self.settings.resources[item]:
            self.encoding = self.settings.resources[item]['encoding']
        self.response = None

    async def _request(self):
        """
        Makes async GET/POST request

        Returns
        -------
        dict
          if error:
            resp_error -- timed out, or other error
            resp_error_desc -- other error description
          if no error:
            resp_data -- response page data
            resp_status -- response status
            resp_time -- response time
        """
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
                logger.debug(f"{self.item} status: {resp.status}")
                res['resp_status'] = resp.status
                res['resp_time'] = round(time.monotonic() - t, 3)
                logger.debug(f"{self.item} resp time: {res['resp_time']} sec")
        except asyncio.TimeoutError:
            res['resp_error'] = self.statuses['ERR_TIMED_OUT']
            logger.warn(f"{self.item} ERR_TIMED_OUT")
        except Exception as e:
            res['resp_error'] = self.statuses['ERR_OTHER']
            res['resp_error_desc'] = e
            logger.warn(f"{self.item}: {e}")
        return res


    def _filter(self, response):
        """
        Filter response data

        Returns
        -------
        dict
          status. The return code::
            0 -- OK
            1 -- ERR_TIMED_OUT
            2 -- ERR_STRING_NOT_FOUND
            3 -- ERR_STATUS_CODE
            4 -- ERR_OTHER
            5 -- ERR_STRING_CODE
          time -- the response time (-1 if status == 1 or 4)
        """
        res = dict()
        res['status'] = self.statuses['OK']
        if 'resp_error' in response:
            res['status'] = response['resp_error']
            res['time'] = '-1'
        else:
            res['time'] = response['resp_time']
            if self.expected_code != response['resp_status']:
                res['status'] += self.statuses['ERR_STATUS_CODE']
                logger.warn(f"{self.item} status: {response['resp_status']}")
            if self.expected_text not in response['resp_data']:
                res['status'] += self.statuses['ERR_STRING_NOT_FOUND']
                logger.warn(f"{self.item} expected string not found")
        return res


    async def send_alarm(self, services, status, recover=False):
        """
        Sends fail/recover alarm to all enabled services

        Args
        -------
        status (int): Status code
        recover (bool): Fail or recover alarm
        """
        i = self.app['alarm_status'][self.item]
        detail = f"{self.settings.get_status_name(status)}"
        if status == 4:
            detail = detail + f" ({self.response['resp_error_desc']})"
        if not recover:
            if not i['fail_sent']:
                msg = f"Failed: {self.item} | {detail}"
            else:
                msg = f"Still failing: {self.item} | {detail}"
            i['fail_sent'] = time.time()
            msg_type = 'fail'
        else:
            msg = f"Recover: {self.item}"
            msg_type = 'recover'
            i['recover_sent'] = time.time()
        for service in services:
            service_obj = ServiceFactory.factory(service, self.settings)
            await service_obj.send(msg, msg_type)
        logger.info(f"Alarm sent: {msg}")

    async def check1(self):
        print(123)

    async def check(self):
        """
        Makes check and send alert to alert services if check failed
        Send check result to zabbix if zabbix service enabled
        """
        cfg = self.settings
        self.response = await self._request()
        data = self._filter(self.response)
        #check if alarm services enabled
        services = self.settings.enabled_services
        if 'zabbix' in services:
            zs = Zabbix_Service(self.settings)
            await zs.send_item_data(self.item, data['time'], data['status'])
            services.remove('zabbix')
        if len(services) > 0:
            #analyze filtered data
            i = self.app['alarm_status'][self.item]
            i['statuses'].append(data['status'])
            logger.debug(f"{self.item}: {i}")
            if data['status'] != 0:
                if i['statuses'].count(data['status']) >= cfg.trigger_threshold:
                    if  (
                         not i['fail_sent'] or
                         time.time() - i['fail_sent'] > cfg.alarm_repeat
                        ):
                        await self.send_alarm(services, data['status'])
            else:
                if i['statuses'][-3:].count(0) >= cfg.recover_threshold:
                    i['statuses'] = []
                    if i['fail_sent']:
                        await self.send_alarm(services, data['status'], True)
                        i['fail_sent'] = None
