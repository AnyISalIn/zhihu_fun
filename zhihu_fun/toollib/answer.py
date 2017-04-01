from bs4 import BeautifulSoup
from .logger import Logger
from ..netlib.requests import _get_image
from ..config import config
import os

basedir = os.path.abspath(os.path.dirname(__name__))
vote_up = config.get('vote_up')


def _get_author_info(bs_obj: BeautifulSoup) -> BeautifulSoup:
    ret = bs_obj.find('div', {'class': 'AuthorInfo'}).find_all('a')
    if ret:
        return ret[-1]
    return '匿名用户'


def _get_author_name(bs_obj: BeautifulSoup) -> str:
    ret = _get_author_info(bs_obj)
    if ret == '匿名用户':
        return '匿名用户'
    return ret.text


def _get_author_url(bs_obj: BeautifulSoup) -> str:
    ret = _get_author_info(bs_obj)
    if ret == '匿名用户':
        return ''
    return ret.get('href')


def _get_attr(bs_obj: BeautifulSoup) -> tuple:
    return _get_author_name(bs_obj), _get_author_url(bs_obj), _get_vote(bs_obj)


def _get_vote(bs_obj: BeautifulSoup) -> int:
    return int(bs_obj.find('button', {'class': 'VoteButton--up'}).text)


def _get_images(answer: BeautifulSoup) -> list:
    noscripts = answer.find_all('noscript')
    if noscripts:
        images = [text.strip('src=').strip('"') for item in noscripts for text in item.text.split(' ') if 'src' in text]
        return images
    return noscripts


def _get_answers(bs_obj: BeautifulSoup) -> list:
    ret = []
    for item in bs_obj.find_all('div', {'class': 'List-item'}):
        if len(item.attrs.get('class')) == 1:
            ret.append(item)
    return ret


def _filter_answer(bs_obj: BeautifulSoup) -> str:
    if _get_vote(bs_obj) < vote_up:
        return
    images = _get_images(bs_obj)
    if not images:
        return
    return images


def _parse_answers(answers: list, title: str):
    for answer in answers:
        images = _filter_answer(answer)
        author_name, author_url, vote = _get_attr(answer)
        if images:
            for image in images:
                path = os.path.join(basedir, 'data', title, author_name + '_赞同_{}'.format(vote))
                path.replace(' ', '')
                if not os.path.isdir(path):
                    os.makedirs(path)
                    Logger.info('{} Not Exists, Created'.format(path))
                image_path = os.path.join(path, image.split('/')[-1])
                _get_image(image, image_path)
                Logger.info('Download Image to {}'.format(image_path))
