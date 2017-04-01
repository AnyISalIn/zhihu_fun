from ..config import config
from http.cookies import SimpleCookie


def _get_user_agent() -> str:
    return config.get('user-agent')


def _get_headers() -> dict:
    return {'User-Agent': _get_user_agent()}


def _get_cookies() -> dict:
    cookie = SimpleCookie()
    cookie.load(config.get('cookie'))
    return {key: morsel.value for key, morsel in cookie.items()}
