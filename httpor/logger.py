import logging
from logging import getLogger

from httpor.helper import config

loglevel = config['options']['loglevel']

#logger
logging.basicConfig(level=config['options']['loglevel'],
                    format='[{asctime}] [{name}.{funcName}:{lineno}] {levelname:7} {message}',
                    style='{')
#logger = logging.getLogger()

__all__ = ['getLogger']
