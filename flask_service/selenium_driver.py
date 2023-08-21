import os

from dotenv import load_dotenv
from selenium.webdriver.chrome.service import Service
from seleniumwire import webdriver
from webdriver_manager.chrome import ChromeDriverManager

chrome_options = webdriver.ChromeOptions()

# chrome_options.add_argument("--headless")
# chrome_options.add_argument("--incognito")
chrome_options.add_argument("--disable-popup-blocking")
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--lang=en-EU")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

load_dotenv()

PROXY = os.getenv('PROXY')

options = {
    'proxy': {
        'http': PROXY,
        'https': PROXY,
        'no_proxy': 'localhost,127.0.0.1'}
}

# service = Service("chromedriver_docker")
service = Service(ChromeDriverManager().install())


class SeleniumChromeDriver:
    def __init__(self):
        self.driver = webdriver.Chrome(seleniumwire_options=options,
                                       service=service,
                                       options=chrome_options)
