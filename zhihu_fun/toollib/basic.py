from ..config import config
from http.cookies import SimpleCookie


def _get_user_agent():
    return config.get('user-agent')


def _get_headers():
    return {'User-Agent': _get_user_agent()}


def _get_cookies():
    cookie = SimpleCookie()
    cookie.load(config.get('cookie'))
    return {key: morsel.value for key, morsel in cookie.items()}
