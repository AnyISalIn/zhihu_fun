from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from ..netlib.requests import my_session
from ..toollib.basic import _get_user_agent
from ..toollib.bs import _to_bs
from ..toollib.logger import Logger
from ..toollib.answer import _get_answers


def _get_driver():
    driver = webdriver.PhantomJS(desired_capabilities=_set_driver_ua())
    Logger.info('Initialize PhantomJS Webdriver')
    _set_cookies(driver, my_session().cookies)
    Logger.info('Initialize Webdriver Cookies')
    _set_driver_window_size(driver)
    Logger.info('Initialize Webdriver Finished')
    return driver


def _set_driver_ua():
    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = (_get_user_agent())
    return dcap


def _set_cookies(driver, cookies):
    for c in cookies:
        driver.add_cookie({'name': c.name, 'value': c.value, 'path': c.path, 'expiry': c.expires, 'domain': c.domain})


def _set_driver_window_size(driver):
    driver.set_window_position(0, 0)
    driver.set_window_size(1920, 1080)


def _open_question_description(driver):
    els = driver.find_elements_by_xpath(
        '//button[@type="button"][@class="Button QuestionRichText-more Button--plain"]')
    # if element not exist, find_elements is fast than find_element
    if len(els) > 0:
        Logger.info('{} Question Description Read More Button Found'.format(driver.current_url))
        els[0].click()
        Logger.info('Click Load More, Wait...')


def _open_load_more(driver, recur_depth=0, max_depth=3):
    recur_depth = recur_depth
    if recur_depth > max_depth:
        return
    els = driver.find_elements_by_class_name('zu-button-more')
    if len(els) > 0:
        Logger.info('URL {} Found Load More Button'.format(driver.current_url))
        els[0].click()
        Logger.info('Click Load More, Wait...')
        sleep(1)
        return _open_load_more(driver, recur_depth + 1)


def _get_question_h4_answer_count(driver):
    return int(driver.find_element_by_class_name('List-headerText').text.split(' ')[0])


def _open_question_load_more(driver, recur_depth=1, max_depth=10):
    answer_count = len(_get_answers(_to_bs(driver.page_source)))
    recur_depth = recur_depth
    if recur_depth > max_depth:
        return
    try:
        title_count = _get_question_h4_answer_count(driver)
        if title_count > 20 and answer_count < title_count:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, '//button[@class="Button QuestionMainAction"]')))
    except TimeoutException:
        Logger.error('Question {} Load More Timeout'.format(driver.current_url))
    els = driver.find_elements_by_xpath('//button[@class="Button QuestionMainAction"]')
    if len(els) > 0:
        Logger.info('Question {} Found Load More Button'.format(driver.current_url))
        els[0].click()
        Logger.info('Click Load More, Wait...')
        sleep(1)
        return _open_question_load_more(driver, recur_depth + 1)
    answer_count = len(_get_answers(_to_bs(driver.page_source)))
    Logger.info('Summary: Question {} Answer Count {}'.format(driver.current_url, answer_count))
