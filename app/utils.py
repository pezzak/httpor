import time
from functools import wraps
from itertools import islice

def time_req(fn):
    @wraps(fn)
    async def wrapped(*args):
        t = time.monotonic()
        d, s = await fn(*args)
        #msec
        time_delta = int(round(time.monotonic() - t, 3) * 1000)
        return d, s, time_delta
    return wrapped


def get_last_from_deque(deque, num):
    deque_len = len(deque)
    return list(islice(deque, deque_len-num, deque_len))
