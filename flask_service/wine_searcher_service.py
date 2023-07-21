import json
import os
import pickle

from random import choice
from typing import Optional, List, Union

from dotenv import load_dotenv
from requests import session
from flask import Flask

from selenium_driver import SeleniumChromeDriver
from settings import WINE_SEARCHER_PRODUCT_URLS, WINE_SEARCHER_ITEMS_HEADERS, WINE_SEARCHER_TIPS_HEADERS
from wine_searcher_service_parser import WineSearcherServiceParser

load_dotenv()
PROXY = os.getenv('PROXY')
COOKIES_FILE_NAME = os.getenv('COOKIES_FILE_NAME')
CHANGE_IP_URL = os.getenv('CHANGE_IP_URL')
SERVICE_PORT = os.getenv('SERVICE_PORT', 5000)

app = Flask(__name__)


class WineSearcherService:
    def __init__(self):
        self.cookies = {}
        self.cookies_str = None
        self.search_string = None
        self.proxies = {'http': PROXY, 'https': PROXY}
        self.parser = WineSearcherServiceParser
        self.request_session = self.create_request_session()
        self.app = Flask(__name__)
        self.register_routes()

    def register_routes(self):
        self.app.add_url_rule('/get_items_and_tips/<params>', 'get_items_and_tips', self.get_items_and_tips)
        self.app.add_url_rule('/', 'show_running', self.show_running)

    def show_running(self):
        return json.dumps({'response': 'Service is running'})

    def create_request_session(self):
        request_session = session()
        request_session.proxies.update(self.proxies)
        return request_session

    def change_proxy_ip(self):
        response = self.request_session.get(CHANGE_IP_URL)
        if self.parser.is_ok_status_code(response.status_code):
            return
        raise RuntimeError(f'Unable to change ip status code is {response.status_code}')

    def restart_search(self):
        self.request_session = self.create_request_session()
        self.change_proxy_ip()
        self.write_cookies()
        self.get_items_and_tips()

    def search_items(self) -> Optional[List]:
        search_items_url = self.parser.build_items_url(self.search_string)
        WINE_SEARCHER_ITEMS_HEADERS.update(cookie=self.cookies_str)
        response = self.request_session.get(search_items_url, headers=WINE_SEARCHER_ITEMS_HEADERS)
        self.app.logger.info(f'Request to {search_items_url}, response status code is {response.status_code}')
        if not self.parser.is_ok_status_code(response.status_code):
            self.restart_search()
            return
        return self.parser.parse_items(response, search_items_url)

    def search_tips(self) -> Optional[Union[List, str]]:
        WINE_SEARCHER_TIPS_HEADERS.update(cookie=self.cookies_str)
        tips_url = self.parser.build_tips_url(self.search_string)
        response_tips = self.request_session.get(tips_url, headers=WINE_SEARCHER_TIPS_HEADERS)
        self.app.logger.info(f'Request to {tips_url}, response status code is {response_tips.status_code}')
        if not self.parser.is_ok_status_code(response_tips.status_code):
            self.restart_search()
            return
        return self.parser.parse_tips(response_tips)

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
        # self.cookies_str = f"cookie_enabled=true; find_tab={self.cookies.get('find_tab')}; ID={self.cookies.get('ID')}; " \
        #                    f"IDPWD={self.cookies.get('IDPWD')}; COOKIE_ID={self.cookies.get('COOKIE_ID')}; " \
        #                    f"visit={self.cookies.get('visit')}; user_status={self.cookies.get('user_status')}; " \
        #                    f"_csrf={self.cookies.get('_csrf')}; cookie_consent={self.cookies.get('cookie_consent')}; " \
        #                    f"pxcts={self.cookies.get('pxcts')}; _hjSessionUser_453016={self.cookies.get('_hjSessionUser_453016')}; " \
        #                    f"_hjFirstSeen={self.cookies.get('_hjFirstSeen')}; " \
        #                    f"_hjSession_453016={self.cookies.get('_hjSession_453016')}; " \
        #                    f"_hjAbsoluteSessionInProgress={self.cookies.get('_hjAbsoluteSessionInProgress')};  " \
        #                    f"search={self.cookies.get('search')}; _ga_M0W3BEYMXL={self.cookies.get('_ga_M0W3BEYMXL')}; " \
        #                    f"_ga={self.cookies.get('_ga')}; _pxde={self.cookies.get('_pxde')}; " \
        #                    f"_pxhd={self.cookies.get('_pxhd')}; X-WS-Find-Mode=TW"

        self.cookies_str = f"_pxhd={self.cookies.get('_pxhd')}; pxcts={self.cookies.get('pxcts')};  " \
                           f"_px3={self.cookies.get('_px3')}; _px2={self.cookies.get('_px2')}; " \
                           f"_pxde={self.cookies.get('_pxde')};"

    def write_cookies(self) -> None:
        driver = SeleniumChromeDriver().driver
        driver.get(choice(WINE_SEARCHER_PRODUCT_URLS))
        pickle.dump(driver.get_cookies(), open(COOKIES_FILE_NAME, "wb"))
        self.app.logger.info('Cookies was written')
        driver.close()

    def get_items_and_tips(self, params=None):
        if not params or not params.strip():
            return json.dumps({'error': 'Search string is empty'})
        if not self.search_string:
            self.search_string = '+'.join(params.split()).replace(',', '').lower().strip()
        self.set_cookies_str()
        parsed_items = self.search_items()
        parsed_tips = self.search_tips()
        return json.dumps({'parsed_items': parsed_items, 'parsed_tips': parsed_tips})

    def run(self):
        self.app.run(host='0.0.0.0', port=SERVICE_PORT, debug=True)


if __name__ == '__main__':
    wine_service = WineSearcherService()
    wine_service.write_cookies()
    wine_service.run()
