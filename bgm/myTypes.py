from typing import Iterator, Callable, Iterable, List, Generic, Union

import scrapy.http
from scrapy import Selector
from parsel import SelectorList


def _xpath(self, query, namespaces=None, **kwargs) -> 'TypeSelectorList':
    pass


def _extract_first(self) -> str:
    pass


class MySelector(Selector):
    xpath = _xpath
    extract_first = _extract_first


class TypeSelectorList(SelectorList, List[MySelector]):
    extract_first = _extract_first


class TypeResponse(scrapy.http.TextResponse):
    xpath = _xpath
