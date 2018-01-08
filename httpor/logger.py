import os
import logging
from logging import getLogger


loglevel = os.environ.get('LOGLEVEL', 'INFO')

# if loglevel == 'DEBUG':
#     logformat = '[{asctime}] [{name}.{funcName}:{lineno}] {levelname:7} {message}'
# else:
#     logformat = '[{asctime}] {levelname:7} {message}'
logformat = '[{asctime}] [{name}.{funcName}:{lineno}] {levelname:7} {message}'

#logger
logging.basicConfig(level=loglevel,
                    format=logformat,
                    style='{')
#logger = logging.getLogger()

__all__ = ['getLogger']
