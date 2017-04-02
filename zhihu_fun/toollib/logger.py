import logging
from ..config import config

log_level = config.get('log_level')


def get_logger(level):
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s [%(processName)s] [%(threadName)s] - %(message)s')
    Logger = logging.getLogger()

    if log_level == 'debug':
        level = logging.DEBUG
    elif log_level == 'info':
        level = logging.INFO
    else:
        level = logging.WARNING
    Logger.setLevel(level)
    return Logger


Logger = get_logger(log_level)
