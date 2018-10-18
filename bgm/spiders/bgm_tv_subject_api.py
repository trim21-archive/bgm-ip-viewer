# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
import scrapy.http
import json
from bgm.items import SubjectJsonItem


class BgmTvSubjectApiSpider(scrapy.Spider):
    name = 'bgm_tv_subject_api'
    allowed_domains = ['mirror.api.bgm.rin.cat']
    start_urls = ['https://mirror.api.bgm.rin.cat' \
                  '/subject/{}?responseGroup=large'.format(i)
                  for i in range(1, 270000)]

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url)

    def parse(self, response: scrapy.http.Response):
        response_json = json.loads(response.text)
        if 'code' in response_json:
            return
        yield SubjectJsonItem(**response_json,
                              _id=response_json['id'])
