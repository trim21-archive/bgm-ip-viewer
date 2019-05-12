# -*- coding: utf-8 -*-

import json
from typing import Union

from twisted.enterprise import adbapi

import bgm.settings
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from bgm.items import (
    SubjectItem,
    RelationItem,
    SubjectJsonItem,
    TopicItem,
    ReplyItem,
    TagItem,
)
from bgm.models import Subject, Relation, SubjectJson, Tag


class MysqlPipeline(object):
    def open_spider(self, spider):
        self.dbpool = adbapi.ConnectionPool(
            "MySQLdb",
            db=bgm.settings.MYSQL_DBNAME,
            host=bgm.settings.MYSQL_HOST,
            user=bgm.settings.MYSQL_USER,
            password=bgm.settings.MYSQL_PASSWORD,
            charset='utf8mb4',
        )

    # @inlineCallbacks
    def process_item(
        self,
        item: Union[SubjectItem, RelationItem, SubjectJsonItem, TagItem],
        spider,
    ):
        query = self.dbpool.runInteraction(self.do_insert, item)
        # 处理异常
        query.addErrback(self.handle_error, item, spider)
        return item

    def handle_error(self, failure, item, spider):
        # 处理异步插入的异常
        print(failure)

    def do_insert(self, cursor, item):
        # 会从dbpool取出cursor
        # 执行具体的插入
        if isinstance(item, SubjectItem):
            if not item['name']:
                item['name'] = item['name_cn']
            # if not item['name_cn']:
            #     item['name_cn'] = item['name']
            insert_sql = Subject.insert(**item).on_conflict(
                preserve=(
                    Subject.name_cn,
                    Subject.name,
                    Subject.image,
                    Subject.tags,
                    Subject.locked,
                    Subject.info,
                    Subject.score_details,
                    Subject.score,
                    Subject.wishes,
                    Subject.done,
                    Subject.doings,
                    Subject.on_hold,
                    Subject.dropped,
                ),
            ).sql()
        elif isinstance(item, RelationItem):
            insert_sql = Relation.insert(
                id=f'{item["source"]}-{item["target"]}', **item
            ).on_conflict(preserve=(Relation.relation, ), ).sql()
        elif isinstance(item, SubjectJsonItem):
            insert_sql = SubjectJson.insert(
                id=item['id'], info=json.dumps(dict(item))
            ).on_conflict(preserve=(SubjectJson.info), ).sql()
        elif isinstance(item, TagItem):
            insert_sql = Tag.insert(
                **item
            ).on_conflict(preserve=(Tag.count, ), ).sql()
        else:
            return
        cursor.execute(*insert_sql)


class TopicMysqlPipeline(object):
    def open_spider(self, spider):
        self.dbpool = adbapi.ConnectionPool(
            "MySQLdb",
            db=bgm.settings.MYSQL_DBNAME,
            host=bgm.settings.MYSQL_HOST,
            user=bgm.settings.MYSQL_USER,
            password=bgm.settings.MYSQL_PASSWORD,
            charset='utf8mb4',
        )

    # @inlineCallbacks
    def process_item(
        self, item: Union[TopicItem, ReplyItem, ReplyItem], spider
    ):
        query = self.dbpool.runInteraction(self.do_insert, item)
        # 处理异常
        query.addErrback(self.handle_error, item, spider)
        return item

    def handle_error(self, failure, item, spider):
        # 处理异步插入的异常
        print(failure)

    def do_insert(self, cursor, item):
        # 会从dbpool取出cursor
        # 执行具体的插入
        if isinstance(item, SubjectItem):
            if not item['name']:
                item['name'] = item['name_cn']
            # if not item['name_cn']:
            #     item['name_cn'] = item['name']
            insert_sql = Subject.insert(**item).on_conflict(
                preserve=(
                    Subject.name_cn,
                    Subject.name,
                    Subject.image,
                    Subject.tags,
                    Subject.locked,
                    Subject.info,
                    Subject.score_details,
                    Subject.score,
                    Subject.wishes,
                    Subject.done,
                    Subject.doings,
                    Subject.on_hold,
                    Subject.dropped,
                ),
            ).sql()
        elif isinstance(item, RelationItem):
            insert_sql = Relation.insert(
                id=f'{item["source"]}-{item["target"]}', **item
            ).on_conflict(preserve=(Relation.relation, ), ).sql()
        elif isinstance(item, SubjectJsonItem):
            insert_sql = SubjectJson.insert(
                id=item['id'], info=json.dumps(dict(item))
            ).on_conflict(preserve=(SubjectJson.info), ).sql()
        else:
            return
        cursor.execute(*insert_sql)
