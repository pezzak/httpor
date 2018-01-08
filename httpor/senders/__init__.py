from .zabbix import ZabbixSender
from .telegram import TelegramSender
from .slack import SlackSender
from ..utils import get_enabled_services

async def send_all_services(msg, msgtype):
    services = get_enabled_services()
    try:
        services.remove('zabbix')
    except ValueError:
        pass
    for service in services:
        serviceCls = service.capitalize() + 'Sender'
        await eval(serviceCls).send(msg, msgtype)
