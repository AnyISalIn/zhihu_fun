from functools import wraps
from .logger import Logger
from time import time


def time_dec(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        start_time = time()
        ret = fn(*args, **kwargs)
        Logger.debug('Function {}, Total Seconds {}'.format(fn.__qualname__, time() - start_time))
        return ret

    return wrapper
