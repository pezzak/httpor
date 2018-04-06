import os
import logging

loglevel = os.environ.get('LOGLEVEL', 'INFO')

class AppStreamHandler(logging.StreamHandler):


    def __init__(self):
        logging.StreamHandler.__init__(self)
        fmt = '[{asctime}] [{name}.{funcName}:{lineno}] {levelname:7} {message}'
        formatter = logging.Formatter(fmt, style='{')
        self.setFormatter(formatter)


def appLogger(name):
    logger = logging.getLogger(name)
    logger.setLevel(loglevel)
    logger.addHandler(AppStreamHandler())
    return logger


__all__ = ['appLogger']
