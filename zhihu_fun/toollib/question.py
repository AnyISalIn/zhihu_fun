import re
from bs4 import BeautifulSoup
from ..config import config
from .logger import Logger

ROOTURL = config.get('root_url')


def _get_questions(bs_obj: BeautifulSoup) -> list:
    return bs_obj.find_all('a', href=re.compile('.*/question/[0-9]+'))


def _get_question_url(bs_obj: BeautifulSoup) -> str:
    return ROOTURL + re.compile('.*(/question/[0-9]+).*$').match(bs_obj.get('href')).groups()[0]


def _get_question_title(bs_obj: BeautifulSoup) -> str:
    if bs_obj.get('href'):
        return bs_obj.text.replace('\n', '')
    return bs_obj.find('h1', {'class': 'QuestionHeader-title'}).text


def _filter_question(bs_obj: BeautifulSoup, keyword_number: int = 1) -> list:
    title = _get_question_title(bs_obj)
    count = 0
    for key in config.get('blacklist'):
        if key in title:
            Logger.debug('Title {} Ignore, Match BlackList {}'.format(title, key))
            return False
    for key in config.get('keyword'):
        if key in title:
            count += 1
            keys = []
            if count == keyword_number:
                Logger.debug('Title {} Macthed, Key {}'.format(title, key))
                keys.append(key)
                return keys
            keys.append(key)
            Logger.debug('Title {} Macthed, Key {}, But Count not end'.format(title, key))
    return []
