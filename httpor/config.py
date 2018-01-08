import os
import json

from httpor.logger import getLogger

logger = getLogger(__name__)

def get_param(self, config, param, default=None, mandatory=True):
    try:
        config = param
        return config
    except Exception as e:
        if mandatory:
            logger.error(f"Unable to get param: {param}")
        else:
            pass

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
        Config.conf_file = os.environ.get('CONFIG_FILE', '../config.json')
        try:
            with open(Config.conf_file, 'r') as stream:
                config = json.load(stream)
        except Exception as e:
            logger.error(f"Unable to read config from file: {Config.conf_file} {e}")

        get_param(Config.proxy, config['proxy'], mandatory=False)
        get_param(Config.timeout, config['timeout'], default=10)
        get_param(Config.frequency, config['frequency'], default=15)

