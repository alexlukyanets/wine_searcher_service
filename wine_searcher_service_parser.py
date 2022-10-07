import json
from dataclasses import dataclass
from json import JSONDecodeError
from typing import Optional, List, Union
from urllib.parse import unquote


@dataclass
class WineItem:
    name: Optional[str] = None
    year: Optional[str] = None
    bottle_size: Optional[str] = None
    location: Optional[str] = None
    price: Optional[str] = None
    tax_inf: Optional[str] = None
    shop_url: Optional[str] = None


class WineSearcherServiceParser:
    @staticmethod
    def domain_url() -> str:
        return 'https://www.wine-searcher.com/'

    @classmethod
    def build_items_url(cls, search_string: str) -> str:
        return f'{cls.domain_url()}find/{search_string}/europe?Xcurrencycode=EUR&Xsavecurrency=Y'

    @classmethod
    def build_tips_url(cls, search_string: str) -> str:
        return f'{cls.domain_url()}ajax/ng/csearch/search?q=1&p=1&c=wine&k={search_string}&v='

    @staticmethod
    def is_ok_status_code(status_code: int) -> bool:
        if status_code != 200:
            return False
        return True

    @staticmethod
    def extract_xpath(div_tag, xpath) -> Optional[str]:
        text = div_tag.xpath(xpath).get()
        if not text:
            return
        return text.strip()

    @classmethod
    def parse_items(cls, response) -> List:
        pared_items = []
        div_tags = response.xpath('//div[@class="js-offers-container"]/div')
        for div_tag in div_tags:
            wine_item = WineItem()
            wine_item.shop_url = unquote(cls.extract_xpath(div_tag, 'div/a/@href'))
            wine_item.name = cls.extract_xpath(div_tag, 'div/div/a/text()')
            wine_item.year = cls.extract_xpath(div_tag, 'div/div/div/span/text()')
            wine_item.location = cls.extract_xpath(div_tag, 'div/div[@class="col3"]/div[2]/text()')
            wine_item.bottle_size = cls.extract_xpath(div_tag, 'div/div[@class="col3"]/div[2]/text()')
            wine_item.price = div_tag.xpath('div/a/div/div/div[contains(@class, "detail price")]/span/text()').getall()
            wine_item.price = ' '.join(wine_item.price)
            wine_item.tax_inf = cls.extract_xpath(div_tag, 'div/a/div/div/div[contains(@class, "price__tax")]/text()')
            pared_items.append(wine_item.__dict__)
        return pared_items

    @staticmethod
    def parse_tips(response) -> Union[List, str]:
        try:
            return json.loads(response.text)
        except JSONDecodeError:
            return 'Not found'
