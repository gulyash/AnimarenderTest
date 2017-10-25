import concurrent.futures

import tornado.platform.asyncio

# The global instance of ThreadPoolExecutor which can be used anywhere in the
# application.
EXECUTOR = concurrent.futures.ThreadPoolExecutor()


def run_async(func, *args, **kwargs):
    """
    Runs a ``function`` with positional and keyword arguments on the
    ``concurrent.futures.ThreadPoolExecutor`` and returns
    ``tornado.concurrent.Future`` with results.

    :param func: The function.
    :param args: Function arguments.
    :param kwargs: Function keyword arguments.
    :return tornado.concurrent.Future: Future wrapper for the result.
    """
    future = EXECUTOR.submit(func, *args, **kwargs)
    return tornado.platform.asyncio.to_tornado_future(future)
