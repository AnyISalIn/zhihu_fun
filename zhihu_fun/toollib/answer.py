from ..toollib.bs import _to_bs
from ..config import config
import os

vote_up = config.get('vote_up')


def _get_author_info(bs_obj):
    ret = bs_obj.find('div', {'class': 'AuthorInfo'}).find_all('a')
    if ret:
        return ret[-1]
    return '匿名用户'


def _get_author_name(bs_obj):
    ret = _get_author_info(bs_obj)
    if ret == '匿名用户':
        return '匿名用户'
    return ret.text


def _get_author_url(bs_obj):
    ret = _get_author_info(bs_obj)
    if ret == '匿名用户':
        return ''
    return ret.get('href')


def _get_attr(bs_obj):
    return _get_author_name(bs_obj), _get_author_url(bs_obj), _get_vote(bs_obj)


def _get_vote(bs_obj):
    return int(bs_obj.find('button', {'class': 'VoteButton--up'}).text)


def _get_images(answer):
    noscripts = answer.find_all('noscript')
    if noscripts:
        images = []
        for item in noscripts:
            bs_obj = _to_bs('<' + item.text.strip('&gt;').strip('lt;') + '/>')  # convert noscripts element to img
            src, width, height = bs_obj.img.attrs.get('src').replace('_b', ''), bs_obj.img.attrs.get(
                'data-rawwidth'), bs_obj.img.attrs.get('data-rawheight')
            images.append((src, width, height))
        return images
    return noscripts


def _get_answers(bs_obj):
    ret = []
    for item in bs_obj.find_all('div', {'class': 'List-item'}):
        if len(item.attrs.get('class')) == 1:
            ret.append(item)
    return ret


def _filter_answer(bs_obj):
    if _get_vote(bs_obj) < vote_up:
        return
    images = _get_images(bs_obj)
    if not images:
        return
    return images
