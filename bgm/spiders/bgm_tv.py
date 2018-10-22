# -*- coding: utf-8 -*-
from typing import List
from collections import defaultdict

from scrapy import Request

from bgm.items import SubjectItem, RelationItem

import scrapy.downloadermiddlewares.defaultheaders

from bgm.myTypes import TypeResponse, TypeSelectorList


def url_from_id(_id):
    return 'https://mirror.bgm.rin.cat/subject/{}'.format(_id)


blank_list = {'角色出演', '角色出演', '片头曲', '片尾曲', '其他'}
regexpNS = 'http://exslt.org/regular-expressions'

collector = {
    'wishes' : 'wishes',
    'done'   : 'collections',
    'doings' : 'doings',
    'on_hold': 'on_hole',
    'dropped': 'dropped'
}

from ..models import Subject


class BgmTvSpider(scrapy.Spider):
    name = 'bgm_tv'
    allowed_domains = ['mirror.bgm.rin.cat']
    start_urls = []

    def start_requests(self):
        CHUNK = 5000
        for i in range(3000, 270000, CHUNK):
            for x in Subject.select(Subject.id).where((Subject.id >= i) & (Subject.id < i + CHUNK)):
                yield Request(url_from_id(x.id))

    def parse(self, response: TypeResponse):
        if '出错了' not in response.text:
            subject_item = SubjectItem()
            if '已锁定' in response.text:
                subject_item['id'] = int(response.url.split('/')[-1])
                subject_item['locked'] = True

            subject_type = response.xpath(
                '//*[@id="panelInterestWrapper"]//div[contains(@class, "global_score")]'
                '/div/small[contains(@class, "grey")]/text()'
            ).extract_first()

            subject_item['subject_type'] = subject_type.split()[1]

            # if subject_item['subject_type'] == 'Music':
            #     return

            subject_item['id'] = int(response.url.split('/')[-1])

            subject_item['info'] = get_info(response)
            subject_item['tags'] = get_teg_from_response(response)
            subject_item['image'] = get_image(response)
            subject_item['score'] = get_score(response)
            subject_item['score_details'] = get_score_details(response)

            title = response.xpath('//*[@id="headerSubject"]/h1/a')[0]

            subject_item['name_cn'] = title.attrib['title']
            subject_item['name'] = title.xpath('text()').extract_first()

            # this will set 'wishes', 'done', 'doings', 'on_hold', 'dropped'
            subject_item.update(get_collector_count(response))

            for edge in get_relation(response, source=subject_item['id']):
                relation_item = RelationItem(**edge, )
                yield relation_item
                # yield Request(url_from_id(relation_item['target']))
            yield subject_item
        # else:
        #     self.logger.error('can\'t parse {}'.format(response.url))


def get_score_details(response: TypeResponse):
    detail = {
        'total': response.xpath('//*[@id="ChartWarpper"]/div/small/span/text()').extract_first()
    }
    for li in response.xpath('//*[@id="ChartWarpper"]/ul[@class="horizontalChart"]/li'):
        detail[
            li.xpath('.//span[@class="label"]/text()').extract_first()
        ] = li.xpath('.//span[@class="count"]/text()').extract_first()[1:-1]
    return detail


def get_info(response: TypeResponse):
    info = defaultdict(list)

    for info_el in response.xpath('//*[@id="infobox"]/li', namespaces={'re': regexpNS}):
        info[info_el.xpath('span/text()').extract_first().replace(':', '').strip()].append(
            info_el.xpath('text()').extract_first() or info_el.xpath('a/text()').extract_first()
        )
    return dict(info)


def get_teg_from_response(response: TypeResponse):
    tags = []
    for a in response.xpath('//*[@id="subject_detail"]//div[@class="subject_tag_section"]/div[@class="inner"]/a'):
        tags.append({
            'name' : a.xpath('span/text()').extract_first(),
            'count': int(a.xpath('small/text()').extract_first())
        })
    return tags


def get_image(response: TypeResponse):
    not_nsfw_cover = response.xpath('//*[@id="bangumiInfo"]/div/div/a/img/@src')
    if not_nsfw_cover:
        return not_nsfw_cover.extract_first().replace('//lain.bgm.tv/pic/cover/c/', 'lain.bgm.tv/pic/cover/g/')
    else:
        return 'lain.bgm.tv/img/no_icon_subject.png'


def get_score(response: TypeResponse):
    return response.xpath(
        '//*[@id="panelInterestWrapper"]//div[@class="global_score"]/span[1]/text()'
    ).extract_first()


def get_collector_count(response: TypeResponse):
    item = {}
    for key, value in collector.items():
        item[key] = response.xpath(
            '//*[@id="subjectPanelCollect"]/span[@class="tip_i"]/a[re:test(@href, "{}$")]/text()'.format(value),
            namespaces={'re': regexpNS}
        ).extract_first()

    for key in collector:
        if item[key]:
            item[key] = int(item[key].split('人')[0])
        else:
            item[key] = 0
    return item


def get_relation(response: TypeResponse, source):
    section = response.xpath(
        '//div[@class="subject_section"][//h2[@class="subtitle" and contains(text(), "关联条目")]]'
        '/div[@class="content_inner"]/ul/li'
    )
    relation = []
    chunk_list = []  # type:List[TypeSelectorList]

    for li in section:
        if 'sep' in li.attrib.get('class', ''):
            chunk_list.append([li, ])
        else:
            chunk_list[-1].append(li)
    for li_list in chunk_list:
        rel = li_list[0].xpath('span/text()').extract_first()
        for li in li_list:
            target = li.xpath('a/@href').extract_first()
            relation.append({
                'source'  : source,
                'target'  : int(target.split('/')[-1]),
                'relation': rel,
            })
    return relation
