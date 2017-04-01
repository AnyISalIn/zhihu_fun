import requests
import shutil
from ..toollib.basic import _get_headers, _get_cookies


def my_session() -> requests.Session:
    session = requests.Session()
    session.get('https://www.zhihu.com', cookies=_get_cookies(), headers=_get_headers())
    return session


def _get_image(url: str, path: str):
    res = requests.get(url, stream=True)
    with open(path, 'wb') as f:
        shutil.copyfileobj(res.raw, f)
