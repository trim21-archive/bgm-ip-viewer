# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field


class SubjectItem(scrapy.Item):
    # define the fields for your item here like:
    id = Field()
    name = Field()
    image = Field()
    subject_type = Field()
    name_cn = Field()
    tags = Field()
    info = Field()

    score = Field()

    score_details = Field()

    wishes = Field()
    done = Field()
    doings = Field()
    on_hold = Field()
    dropped = Field()


class SubjectJsonItem(scrapy.Item):
    # define the fields for your item here like:
    _id = Field()
    id = Field()
    url = Field()
    eps = Field()
    eps_count = Field()
    vols_count = Field()
    type = Field()
    name = Field()
    name_cn = Field()
    summary = Field()
    air_date = Field()
    air_weekday = Field()
    rating = Field()
    rank = Field()
    images = Field()
    collection = Field()
    crt = Field()
    staff = Field()
    topic = Field()
    blog = Field()


class RelationItem(scrapy.Item):
    # define the fields for your item here like:
    _id = Field()
    source = Field()
    target = Field()
    relation = Field()


class TopicItem(scrapy.Item):
    id = Field()
    author = Field()
    content = Field()
    create_time = Field()
    last_modify_time = Field()
    deleted = Field()
    title = Field()
    group = Field()
    last_reply = Field()


class ReplyItem(scrapy.Item):
    id = Field()
    author = Field()
    content = Field()
    create_time = Field()
    last_modify_time = Field()
    deleted = Field()
    nested_reply = Field()
    reply_to = Field()
    topic = Field()