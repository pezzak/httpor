import os
import logging
from logging import getLogger


loglevel = os.environ.get('LOGLEVEL', 'INFO')

logformat = '[{asctime}] [{name}.{funcName}:{lineno}] {levelname:7} {message}'

logging.basicConfig(level=loglevel,
                    format=logformat,
                    style='{')

__all__ = ['getLogger']
