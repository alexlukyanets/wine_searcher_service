import json
import os
import pickle
from random import choice
from sys import argv
from typing import Optional, List, Union

from dotenv import load_dotenv
from requests import session
from scrapy.http import HtmlResponse

from selenium_driver import SeleniumChromeDriver
from settings import WINE_SEARCHER_PRODUCT_URLS, WINE_SEARCHER_ITEMS_HEADERS, WINE_SEARCHER_TIPS_HEADERS
from wine_searcher_service_parser import WineSearcherServiceParser

load_dotenv()
PROXY = os.getenv('PROXY')
COOKIES_FILE_NAME = os.getenv('COOKIES_FILE_NAME')
CHANGE_IP_URL = os.getenv('CHANGE_IP_URL')


class WineSearcherService:
    def __init__(self, driver):
        try:
            self.search_string = '+'.join(argv[1:]).replace(',', '').lower().strip()
        except (IndexError, TypeError):
            raise RuntimeError('Unable to parse search string')
        self.cookies = {}
        self.cookies_str = None
        self.proxies = {'http': PROXY, 'https': PROXY}
        self.parser = WineSearcherServiceParser
        self.request_session = session()
        self.request_session.proxies.update(self.proxies)

    def change_proxy_ip(self):
        response = self.request_session.get(CHANGE_IP_URL)
        if self.parser.is_ok_status_code(response.status_code):
            return
        raise RuntimeError(f'Unable to change ip status code is {response.status_code}')

    def restart_search(self):
        self.change_proxy_ip()
        self.write_cookies()
        self.print_items_and_tips()

    def search_items(self) -> Optional[List]:
        search_items_url = self.parser.build_items_url(self.search_string)
        WINE_SEARCHER_ITEMS_HEADERS.update(cookie=self.cookies_str)
        response = self.request_session.get(search_items_url, headers=WINE_SEARCHER_ITEMS_HEADERS)
        if not self.parser.is_ok_status_code(response.status_code):
            self.restart_search()
            return
        response_items = HtmlResponse(search_items_url, body=response.content)
        return self.parser.parse_items(response_items)

    def search_tips(self) -> Optional[Union[List, str]]:
        WINE_SEARCHER_TIPS_HEADERS.update(cookie=self.cookies_str)
        tips_url = self.parser.build_tips_url(self.search_string)
        response_tips = self.request_session.get(tips_url, headers=WINE_SEARCHER_TIPS_HEADERS)
        if not self.parser.is_ok_status_code(response_tips.status_code):
            self.restart_search()
            return
        return self.parser.parse_tips(response_tips)

    def print_items_and_tips(self):
        self.set_cookies_str()
        parsed_items = self.search_items()
        parsed_tips = self.search_tips()
        print(json.dumps({'parsed_items': parsed_items, 'parsed_tips': parsed_tips}))

    def update_cookies(self):
        try:
            cookies = pickle.load(open(COOKIES_FILE_NAME, "rb"))
        except FileNotFoundError:
            return
        [self.cookies.update({cookie['name']: cookie['value']}) for cookie in cookies]

    def set_cookies_str(self):
        self.update_cookies()
        if not self.cookies:
            self.write_cookies()
            self.update_cookies()
        self.cookies_str = f"cookie_enabled=true; find_tab={self.cookies.get('find_tab')}; ID={self.cookies.get('ID')}; " \
                           f"IDPWD={self.cookies.get('IDPWD')}; COOKIE_ID={self.cookies.get('COOKIE_ID')}; " \
                           f"visit={self.cookies.get('visit')}; user_status={self.cookies.get('user_status')}; " \
                           f"_csrf={self.cookies.get('_csrf')}; cookie_consent={self.cookies.get('cookie_consent')}; " \
                           f"pxcts={self.cookies.get('pxcts')}; _hjSessionUser_453016={self.cookies.get('_hjSessionUser_453016')}; " \
                           f"_hjFirstSeen={self.cookies.get('_hjFirstSeen')}; " \
                           f"_hjSession_453016={self.cookies.get('_hjSession_453016')}; " \
                           f"_hjAbsoluteSessionInProgress={self.cookies.get('_hjAbsoluteSessionInProgress')};  " \
                           f"search={self.cookies.get('search')}; _ga_M0W3BEYMXL={self.cookies.get('_ga_M0W3BEYMXL')}; " \
                           f"_ga={self.cookies.get('_ga')}; _pxde={self.cookies.get('_pxde')}; " \
                           f"_pxhd={self.cookies.get('_pxhd')}; X-WS-Find-Mode=TW"

    @staticmethod
    def write_cookies():
        driver = SeleniumChromeDriver().driver
        driver.get(choice(WINE_SEARCHER_PRODUCT_URLS))
        pickle.dump(driver.get_cookies(), open(COOKIES_FILE_NAME, "wb"))
        driver.close()


if __name__ == '__main__':
    wine_service = WineSearcherService(SeleniumChromeDriver)
    wine_service.print_items_and_tips()