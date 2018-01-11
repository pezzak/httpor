import time
import aiohttp
import asyncio
import json

from httpor.config import config, statuses
from httpor.utils import get_enabled_services, alarm_status, get_status_name
from httpor.logger import getLogger

from httpor.senders import ZabbixSender, send_all_services

logger = getLogger(__name__)


class Checker():
    """


    Args
    -------
    item (str): Item key from resources.
    req_params (dict): Request params.
    """
    def __init__(self, item, req_params):
        self.item = item
        self.type = req_params['type']
        self.url = req_params['url']
        self.expected_text = req_params['expected_text']
        self.expected_code = req_params['expected_code']
        if self.type == 'POST':
            self.data = req_params['data']
        self.timeout = config.timeout
        self.proxy = config.proxy if req_params['use_proxy'] else None
        self.encoding = req_params['encoding'] if 'encoding' in req_params else 'utf-8'
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
            res['resp_error'] = statuses['ERR_TIMED_OUT']
            logger.warn(f"{self.item} ERR_TIMED_OUT")
        except Exception as e:
            res['resp_error'] = statuses['ERR_OTHER']
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
        res['status'] = statuses['OK']
        if 'resp_error' in response:
            res['status'] = response['resp_error']
            res['time'] = '-1'
        else:
            res['time'] = response['resp_time']
            e_code = config.resources[self.item]['expected_code']
            if e_code != response['resp_status']:
                res['status'] += statuses['ERR_STATUS_CODE']
                logger.warn(f"{self.item} status: {response['resp_status']}")
            e_string = config.resources[self.item]['expected_text']
            if e_string not in response['resp_data']:
                res['status'] += statuses['ERR_STRING_NOT_FOUND']
                logger.warn(f"{self.item} expected string not found")
        return res


    async def send_alarm(self, status, recover=False):
        """
        Sends fail/recover alarm to all enabled services

        Args
        -------
        status (int): Status code
        recover (bool): Fail or recover alarm
        """
        i = alarm_status[self.item]
        detail = f"{get_status_name(status)}"
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
        await send_all_services(msg, msg_type)
        logger.info(f"Alarm sent: {msg}")


    async def check(self):
        """
        Makes check and send alert to alert services if check failed
        Send check result to zabbix if zabbix service enabled
        """
        self.response = await self._request()
        data = self._filter(self.response)
        #check if alarm services enabled
        services = get_enabled_services()
        if 'zabbix' in services:
            services.remove('zabbix')
        if len(services) > 0:
            #analyze filtered data
            i = alarm_status[self.item]
            i['statuses'].append(data['status'])
            logger.debug(f"{self.item}: {i}")
            if data['status'] != 0:
                if i['statuses'].count(data['status']) >= config.trigger_threshold:
                    if  (
                         not i['fail_sent'] or
                         time.time() - i['fail_sent'] > config.alarm_repeat
                        ):
                        await self.send_alarm(data['status'])
            else:
                if i['statuses'][-3:].count(0) >= config.recover_threshold:
                    i['statuses'] = []
                    if i['fail_sent']:
                        await self.send_alarm(data['status'], True)
                        i['fail_sent'] = None

        if 'zabbix' in get_enabled_services():
            await ZabbixSender.send_item_data(self.item, data['time'], data['status'])
