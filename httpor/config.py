import os
import json

from httpor.logger import getLogger

logger = getLogger(__name__)

statuses = {
    'OK': 0,
    'ERR_TIMED_OUT': 1,
    'ERR_STRING_NOT_FOUND': 2,
    'ERR_STATUS_CODE': 3,
    'ERR_OTHER': 4,
    'ERR_STRING_CODE': 5,
}

def get_param(config, param, default=None):
    try:
        config_param = config[param]
    except Exception:
        config_param = default if default else None
    finally:
        logger.debug(f"{param}: {config_param}")
        return config_param

class Config:

    conf_file = None
    proxy = None
    timeout = None
    frequency = None
    services = None
    resources = None

    def __init__(self):
        Config.load()

    @staticmethod
    def load():
        Config.conf_file = os.environ.get('CONFIG_FILE', 'config.json')
        try:
            with open(Config.conf_file, 'r') as stream:
                config = json.load(stream)
        except Exception as e:
            logger.error(f"Unable to read config from file: {Config.conf_file} {e}")
            config = dict()

        Config.proxy = get_param(config, 'proxy')
        Config.timeout = get_param(config, 'timeout', 10)
        Config.frequency = get_param(config, 'frequency', 15)
        Config.services = get_param(config, 'services')
        Config.resources = get_param(config, 'resources')

config = Config()
