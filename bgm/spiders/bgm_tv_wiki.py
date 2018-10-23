# -*- coding: utf-8 -*-
import scrapy

from bgm.myTypes import TypeResponse
from bgm.spiders import bgm_tv
from scrapy import Request


class BgmTvWikiSpider(scrapy.Spider):
    name = 'bgm_tv_wiki'
    allowed_domains = ['mirror.bgm.rin.cat']
    start_urls = ['https://mirror.bgm.rin.cat/wiki']

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, meta={'dont_cache': True})

    def parse(self, response: TypeResponse):
        links = response.xpath('//*[@id="wiki_wiki-subject-relation"]/li/a/@href')
        for link in links.extract():
            yield Request(response.urljoin(link),
                          callback=self.parse_page,
                          meta={'dont_cache': True})
        for link in response.xpath('//*[@id="latest_all"]/li/a/@href').extract():
            yield Request(response.urljoin(link),
                          callback=self.parse_page,
                          meta={'dont_cache': True})

    parse_page = bgm_tv.BgmTvSpider.parse
