from queue import Queue
from random import randint
from time import time
from threading import Thread
from .config import config
from .netlib.requests import my_session, _get_image
from .netlib.selenium import _get_driver, _open_question_description, _open_load_more, _open_question_load_more
from .toollib.basic import _get_headers
from .toollib.bs import _to_bs
from .toollib.logger import Logger
from .toollib.question import _get_questions, _get_question_url, _filter_question, _get_question_title
from .toollib.dec import time_dec
from .toollib.answer import _filter_answer, _get_answers, _get_attr
import json
import os

session = my_session()
session.headers = _get_headers()
ROOTURL = config.get('root_url')
basedir = os.path.abspath(os.path.dirname(__name__))


class UrlGenerator(object):
    def __init__(self, q, keyword_number=1):
        self.driver = _get_driver()
        self._start_url = config.get('start_url') or ROOTURL
        self._first_page = _to_bs(self._get_page(self._start_url))
        self._urls = set()
        self.urls = []
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
    def _generate_url(self, bs_obj):
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
                Logger.warning('No Custom URLs')
            Logger.info('First Page, Start URL {}'.format(self._start_url))
            self._generate_url(self._first_page)
            Logger.info('First Page Finished')
        while True:
            total_second = time() - start_time
            if second is not None:
                if total_second > second:
                    Logger.info('Total Second {}, Stopping app...'.format(total_second))
                    break
            if not self.urls:
                Logger.info('Finished, No More Resource')
                break
            index = randint(0, len(self.urls) - 1)  # generate url from random index
            url = self.urls[index]
            self.urls.pop(index)
            Logger.info('Access URL {}'.format(url))
            bs_obj = _to_bs(self._get_page(url))
            self._generate_url(bs_obj)

    def run(self, second=None):
        self._run(second=second)


class QuestionParser(object):
    def __init__(self, q):
        self.driver = _get_driver()  # init selenium webdriver
        self.q = q  # get process queue
        self.answer_queue = Queue()  # init answer queue

    def _get_page(self, url):
        self.driver.get(url)
        _open_question_load_more(self.driver)
        return self.driver.page_source

    def _write_image_meta(self):
        result = []
        meta_file = os.path.join(basedir, 'image_meta.json')
        while True:
            item = self.answer_queue.get()  # get image item from answer queue
            result.append(item)
            if len(result) == 10:
                if not os.path.isfile(meta_file):
                    with open(meta_file, 'w') as json_file:
                        json.dump(result, json_file, indent=4, ensure_ascii=False)
                else:
                    with open(meta_file, 'r') as json_file:
                        try:
                            entrys = json.load(json_file)  # append to json file, if Exception, return []
                        except ValueError:
                            entrys = []
                    with open(meta_file, 'w') as json_file:
                        entrys.extend(result)
                        entrys.sort(key=lambda x: x['vote'], reverse=True)
                        json.dump(entrys, json_file, indent=4, ensure_ascii=False)
                result = []
                Logger.info('Dump URL Resource to {}'.format(meta_file))

    def _parse_answers(self, answers, title):
        for answer in answers:
            images = _filter_answer(answer)
            author_name, author_url, vote = _get_attr(answer)
            if images:
                for image in images:
                    src, width, height = image  # unpack image tuple
                    answer_path = os.path.join('data', title, author_name + '_赞同_{}'.format(vote))
                    path = os.path.join(basedir, answer_path)
                    if not os.path.isdir(path):
                        os.makedirs(path)
                        Logger.info('{} Not Exists, Created'.format(path))
                    image_path = src.split('/')[-1]
                    abs_path = os.path.join(path, image_path)
                    _get_image(src, abs_path)
                    attrs = {'author_name': author_name, 'author_url': author_url, 'vote': vote,
                             'src': os.path.join('/', answer_path, image_path), 'width': width, 'height': height}
                    self.answer_queue.put(attrs)  # put answer attr to thread queue
                    Logger.info('Download Image to {}'.format(image_path))

    def _run(self):
        while True:
            item = self.q.get()  # block, get url from url generator
            url, title = item.get('url'), item.get('title')
            bs_obj = _to_bs(self._get_page(url))  # page source to bs4 object
            Thread(target=self._parse_answers, args=(_get_answers(bs_obj), title)).start()  # start thread handle answer
        Logger.info('Finished, No More Resource')

    def run(self):
        Thread(target=self._write_image_meta, name='write-image').start()  # listen image download with app start
        self._run()
