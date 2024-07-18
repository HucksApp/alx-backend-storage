#!/usr/bin/env python3
'''A module with tools for request caching and tracking.
'''
import redis
import requests
from datetime import timedelta
from functools import wraps


def cache_and_track(func):
    '''Decorator to cache the result of a function
        and track the number of calls to a URL.
    '''
    @wraps(func)
    def wrapper(url: str):
        if url is None or len(url.strip()) == 0:
            return ''

        redis_store = redis.Redis()
        res_key = 'result:{}'.format(url)
        req_key = 'count:{}'.format(url)

        result = redis_store.get(res_key)
        if result is not None:
            redis_store.incr(req_key)
            return result.decode('utf-8')

        result = func(url)
        redis_store.setex(res_key, timedelta(seconds=10), result)
        redis_store.incr(req_key)
        return result
    return wrapper


@cache_and_track
def get_page(url: str) -> str:
    '''Returns the content of a URL after caching the request's response,
    and tracking the request.

    Args:
        url (str): The URL to retrieve the HTML content from.

    Returns:
        str: The HTML content of the URL.
    '''
    return requests.get(url).content.decode('utf-8')


if __name__ == "__main__":
    # Test the function with a slow response simulation
    test_url = ('http://slowwly.robertomurray.co.uk/\
        delay/5000/url/http://www.google.com')
    print(get_page(test_url))
