import time
from functools import wraps

def time_req(fn):
    @wraps(fn)
    async def wrapped(*args):
        t = time.monotonic()
        d, s = await fn(*args)
        #msec
        time_delta = int(round(time.monotonic() - t, 3) * 1000)
        return d, s, time_delta
    return wrapped
