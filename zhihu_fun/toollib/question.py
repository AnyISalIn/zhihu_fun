import re
from ..config import config
from .logger import Logger

ROOTURL = config.get('root_url')


def _get_questions(bs_obj):
    return bs_obj.find_all('a', href=re.compile('.*/question/[0-9]+'))


def _get_question_url(bs_obj):
    return ROOTURL + re.compile('.*(/question/[0-9]+).*$').match(bs_obj.get('href')).groups()[0]


def _get_question_title(bs_obj):
    if bs_obj.get('href'):
        ret = bs_obj.text.replace('\n', '')
        if [s for s in ret.split('- ', -1) if '的回答' in s]:
            return ret.split('- ')[0].replace('?', '？')  # replace ? to ？
        return ret.replace('?', '？')
    return bs_obj.find('h1', {'class': 'QuestionHeader-title'}).text.replace('?', '？')


def _filter_question(bs_obj, keyword_number=1):
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
