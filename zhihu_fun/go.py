from bs4 import BeautifulSoup
from collections import deque
from multiprocessing import Queue
from random import randint
from time import time
from threading import Thread
from .config import config
from .netlib.requests import my_session
from .netlib.selenium import _get_driver, _open_question_description, _open_load_more, _open_question_load_more
from .toollib.basic import _get_headers
from .toollib.bs import _to_bs
from .toollib.logger import Logger
from .toollib.question import _get_questions, _get_question_url, _filter_question, _get_question_title
from .toollib.dec import time_dec
from .toollib.answer import _parse_answers, _get_answers

session = my_session()
session.headers = _get_headers()
ROOTURL = config.get('root_url')


class UrlGenerator(object):
    def __init__(self, q: Queue, keyword_number: int = 1):
        self.driver = _get_driver()
        self._start_url = config.get('start_url') or ROOTURL
        self._first_page = _to_bs(self._get_page(self._start_url))
        self._urls = set()
        self.urls = deque()
        self.info = []
        self.keyword_number = keyword_number
        self.macthed_keys = {}
        self.q = q

    @time_dec
    def _get_page(self, url):
        self.driver.get(url)
        _open_load_more(self.driver)
        if 'question' in self.driver.current_url:
            _open_question_description(self.driver)
        return self.driver.page_source

    @time_dec
    def _generate_url(self, bs_obj: BeautifulSoup):
        for item in _get_questions(bs_obj):
            url = _get_question_url(item)
            title = _get_question_title(item)
            attrs = {'url': url, 'title': title}
            if url not in self._urls:
                matched_keys = _filter_question(item, self.keyword_number)
                if not matched_keys:
                    continue
                for key in matched_keys:
                    if key not in self.macthed_keys:
                        self.macthed_keys[key] = 0
                    self.macthed_keys[key] += 1
                Logger.info('New Page {url} Title {title}'.format(**attrs))
                self._urls.add(url)
                self.info.append(attrs)
                self.urls.append(url)
                if 'question' in url:
                    self.q.put(attrs)
            else:
                Logger.debug('Page {url} Title {title} is Filterd'.format(**attrs))

    def _run(self, first=True, second=None):
        start_time = time()
        if first:
            if config.get('custom_urls'):
                self.urls.extend(config.get('custom_urls'))
                Logger.info('Extend Custom URLs')
            else:
                Logger.info('No Custom URLs')
            Logger.info('First Page, Start URL {}'.format(self._start_url))
            self._generate_url(self._first_page)
            Logger.info('First Page Finished')
        while True:
            total_second = time() - start_time
            if second is not None:
                if total_second > second:
                    Logger.info('Total Second {}, Stopping app...'.format(total_second))
                    break
            try:
                index = randint(0, len(self.urls) - 1)  # generate deque random index
                url = self.urls[index]
                Logger.info('Access URL {}'.format(url))
            except IndexError:
                Logger.info('Finished, No More Resource')
                break
            else:
                bs_obj = _to_bs(self._get_page(url))
                self._generate_url(bs_obj)

    def run(self, second=None):
        self._run(second=second)


class QuestionParser(object):
    def __init__(self, q: Queue):
        self.driver = _get_driver()
        self.q = q

    def _get_page(self, url: str):
        self.driver.get(url)
        _open_question_load_more(self.driver)
        return self.driver.page_source

    def _run(self):
        while True:
            item = self.q.get()
            url, title = item.get('url'), item.get('title')
            bs_obj = _to_bs(self._get_page(url))
            Thread(target=_parse_answers, args=(_get_answers(bs_obj), title)).start()
        Logger.info('Finished, No More Resource')
