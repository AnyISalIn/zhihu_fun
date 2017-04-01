from bs4 import BeautifulSoup


def _to_bs(page) -> BeautifulSoup:
    return BeautifulSoup(page, 'lxml')



