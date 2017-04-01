from bs4 import BeautifulSoup


def _to_bs(page):
    return BeautifulSoup(page, 'lxml')



