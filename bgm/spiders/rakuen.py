# -*- coding: utf-8 -*-
import scrapy
from bgm.items import TopicItem, ReplyItem
from bgm.myTypes import TypeResponse
import dateutil.parser


class RakuenSpider(scrapy.Spider):
    name = 'rakuen'
    allowed_domains = ['bgm.tv', 'mirror.bgm.rin.cat']
    start_urls = [
        # 'https://bgm.tv/rakuen/topiclist',
        'https://mirror.bgm.rin.cat/rakuen/topiclist?type=group',
        # 'https://bgm.tv/rakuen/topiclist?type=subject',
        # 'https://bgm.tv/rakuen/topiclist?type=ep',
        # 'https://bgm.tv/rakuen/topiclist?type=mono'
    ]

    def parse(self, response: TypeResponse):
        yield scrapy.Request('https://bgm.tv/rakuen/topic/subject/892', callback=self.parse_page)
        # for item in response.xpath('//*[contains(@class, "item_list")]')[:]:
        #     l = item.xpath('./a/@href').extract_first()
        #     yield scrapy.Request(response.urljoin(l), callback=self.parse_page)
        # print(response.text)

    def parse_page(self, response: TypeResponse):
        with open('./a.html','w',encoding='utf8') as f:
            f.write(response.text)
        topic = TopicItem()
        topic['last_reply'] = max([parse_datetime(x.xpath('./text()').extract_first())
                                   for x in response.xpath('//*[contains(@class,"re_info")]/small')])

        e = response.xpath('//*[contains(@class, "topic_content")]')
        post_topic = response.xpath('//*[contains(@class, "postTopic")]')
        topic['id'] = response.url.split('/')[-1]
        topic['content'] = e.extract_first()
        print(response.xpath('//*[@id="pageHeader"]'))
        print(response.xpath('//*[@id="pageHeader"]/h1/span/a[1]/@class'))
        topic['group'] = response.xpath('//*[@id="pageHeader"]/h1/span/a[1]/@href').extract_first().split('/')[-1]
        topic['title'] = response.xpath('//*[@id="pageHeader"]/h1/text()').extract_first()
        topic['deleted'] = False
        topic['author'] = post_topic.xpath('./div[contains(@class, "inner")]//a/@href').extract_first()
        if not topic['author']:
            raise KeyError('no author')
        else:
            topic['author'] = topic['author'].split('/')[-1]
        create_time = post_topic.xpath('./div[contains(@class, "re_info")]/small/text()').extract_first()
        topic['create_time'] = parse_datetime(create_time)
        print(topic['group'])

        comments = response.xpath('//*[@id="comment_list"]')
        last_reply = topic['create_time']
        for row in comments.xpath('./div[contains(@class, "row_reply")]'):
            for item in parse_row_reply(response, row):
                if item['create_time'] > last_reply:
                    last_reply = item['create_time']
                yield item
            # print(m_r)
        topic['last_reply'] = last_reply
        yield topic


def parse_row_reply(response: TypeResponse, row):
    main_reply = ReplyItem()
    main_reply['nested_reply'] = False
    main_reply['id'] = row.xpath('./@id').extract_first().split('_')[-1]
    main_reply['author'] = row.xpath('./a[contains(@class, "avatar")]/@href').extract_first().split('/')[-1]
    main_reply['create_time'] = parse_datetime(row.xpath('./div[@class="re_info"]/small/text()').extract_first())
    main_reply['content'] = row.xpath('.//div[contains(@class, "message")]').extract_first()
    main_reply['topic'] = response.url.split('/')[-1]
    yield main_reply
    yield from parse_sub_reply(response, row, main_reply['id'])


def parse_sub_reply(response: TypeResponse, row, reply_to):
    for sub_reply_row in row.xpath('.//div[contains(@class, "sub_reply_bg")]'):
        sub_reply = ReplyItem(nested_reply=True)
        sub_reply['reply_to'] = reply_to
        sub_reply['id'] = sub_reply_row.xpath('./@id').extract_first().split('_')[-1]
        sub_reply['topic'] = response.url.split('/')[-1]
        sub_reply['author'] = sub_reply_row.xpath('./a[contains(@class, "avatar")]/@href').extract_first().split('/')[
            -1]
        sub_reply['create_time'] = parse_datetime(sub_reply_row.xpath(
            './div[@class="re_info"]/small/text()'
        ).extract_first())
        sub_reply['content'] = sub_reply_row.xpath('.//div[contains(@class, "cmt_sub_content")]').extract_first()
        yield sub_reply


def parse_datetime(time_string):
    if not time_string:
        return ''
    time_string = time_string.split('-', 1)[-1].strip()
    return dateutil.parser.parse(time_string)


def parse_content(node):
    r = node.xpath('//div')[0]
    print(r)
