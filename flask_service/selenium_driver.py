import os

from dotenv import load_dotenv
from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

chrome_options = webdriver.ChromeOptions()

chrome_options.add_argument("--headless")
chrome_options.add_argument("--start-maximized")
# chrome_options.add_argument("--incognito")
chrome_options.add_argument("--disable-popup-blocking")
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--lang=en-EU")

load_dotenv()

PROXY = os.getenv('PROXY')

options = {
    'proxy': {
        'http': PROXY,
        'https': PROXY,
        'no_proxy': 'localhost,127.0.0.1'
    }
}


class SeleniumChromeDriver:
    def __init__(self):
        self.driver = webdriver.Chrome(seleniumwire_options=options, service=Service(ChromeDriverManager().install()),
                                       options=chrome_options)
