from random import randint
import contextlib
import logging
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

logger = logging.getLogger(__name__)
TIMEOUT = 120


@contextlib.contextmanager
def wait_for_page_load(driver, element=None, timeout=TIMEOUT):
    # if no element is provided, use tag html
    if element is None:
        element = driver.find_element_by_tag_name('html')
    yield
    # wait until the staleness of element
    WebDriverWait(driver, timeout).until(EC.staleness_of(element))
    # wait until the ready of new page
    WebDriverWait(driver, timeout).\
        until(lambda _:
              driver.execute_script(
                  'return document.readyState') == 'complete')


def login(driver, url, username, password):
    driver.get(url)
    e_username = driver.find_element_by_id('username')
    e_password = driver.find_element_by_id('password')
    e_username.clear()
    e_username.send_keys(username)
    e_password.clear()
    e_password.send_keys(password)
    with wait_for_page_load(driver, timeout=TIMEOUT):
        e_password.submit()


def collect_links(driver):
    e_list = driver.find_element_by_id('user_homepage_message_list')
    e_archors = e_list.find_elements_by_css_selector(
        'li.messageInformationContents a')
    news_links = [e.get_property('href') for e in e_archors]
    return news_links


def praise(driver):
    e_praise_span = driver.find_element_by_css_selector(
        'span[id^="praise_count_"]')
    try:
        e_praise_btn = e_praise_span\
            .find_element_by_css_selector('a[title="点赞"]')
        e_praise_btn.click()
        time.sleep(10)
        return True
    except NoSuchElementException:
        e_praise_btn = e_praise_span\
            .find_element_by_css_selector('a[title="取消点赞"]')
        logger.info('Already be praised: %r!', driver.current_url)
        return False


def comment(driver, words):
    # random comment word
    word = words[randint(0, len(words) - 1)]
    # find comment input
    e_iframe = WebDriverWait(driver, TIMEOUT).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR,
                                          'iframe[class="ke-edit-iframe"]')))
    # e_iframe = driver.find_element_by_css_selector(
    #     'iframe[class="ke-edit-iframe"]')
    # input comment
    driver.execute_script(
        "arguments[0].contentDocument.body.innerHTML=\"{}\";".format(word),
        e_iframe)
    # submit comment
    with wait_for_page_load(driver, element=e_iframe, timeout=TIMEOUT):
        e_iframe.submit()
    # # wait until comment is submitted
    # logger.info('Waiting until staleness of e_iframe ...')
    # WebDriverWait(driver, TIMEOUT).until(EC.staleness_of(e_iframe))
    # # wait until the ready of new page
    # logger.info('Waring until the ready of document ...')
    # WebDriverWait(driver, TIMEOUT).\
    #     until(lambda _:
    #           driver.execute_script(
    #               'return document.readyState') == 'complete')


def filter(driver):
    if '彪哥' in driver.page_source or '毛建彪' in driver.page_source:
        return False
    else:
        return True


def auto(conf, stop_if_praised=False, force_comment=True, start_page=1):
    url = conf['trustie']['url']
    username = conf['trustie']['username']
    password = conf['trustie']['password']
    page = start_page
    words = ['赞赞！', '加油！', '辛苦!', '学习！', '收藏！']
    driver = webdriver.Firefox()
    logger.info('Try login ...')
    login(driver, url, username, password)
    logger.info('Login done!')
    url_pattern = \
        'https://www.trustie.net/users/14ShaoCC/user_activities?page={}'
    while True:
        logger.info('Collecting links for page number %r', page)
        links = collect_links(driver)
        logger.info('Collected links are: %s', links)
        if len(links) == 0:
            logger.warning('Empty links in the page %r', driver.current_url)
        logger.info('Commenting each link ...')
        for link in links:
            logger.debug('Processing link %r ...', link)
            with wait_for_page_load(driver, timeout=TIMEOUT):
                driver.get(link)
            if filter(driver) is False:
                continue
            try:
                logger.info('Praising %r ...', link)
                is_praised_before = praise(driver)
                if is_praised_before is True and stop_if_praised is True:
                    break
                if is_praised_before is True and force_comment is False:
                    continue
                logger.info('Commenting %r ...', link)
                comment(driver, words)
            except NoSuchElementException as e:
                logger.error(e)
                logger.warning('Skip this page: %r', driver.current_url)
                continue
        page += 1
        url = url_pattern.format(page)
        try:
            driver.get(url)
        except WebDriverException as e:
            logger.error(e)
            break
        logger.info('Current page=%s', page)
        break
