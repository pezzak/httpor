import json
#from logging import getLogger

#config
config = json.load(open('httpor/config.json'))

#zabbix errors
statuses = {
    'OK': 0,
    'ERR_TIMED_OUT': 1,
    'ERR_STRING_NOT_FOUND': 2,
    'ERR_STATUS_CODE': 3,
    'ERR_OTHER': 4,
    'ERR_STRING_CODE': 5,
}

#__all__ = ['getLogger']
