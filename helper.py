import json
import logging

#config
config = json.load(open('config.json'))

#logger
logging.basicConfig(level=config['options']['loglevel'],
                    format='%(asctime)s:%(levelname)s:%(message)s')
logger = logging.getLogger()

#zabbix errors
statuses = {
    'OK': 0,
    'ERR_TIMED_OUT': 1,
    'ERR_STRING_NOT_FOUND': 2,
    'ERR_STATUS_CODE': 3,
    'ERR_OTHER': 4,
    'ERR_STRING_CODE': 5,
}
