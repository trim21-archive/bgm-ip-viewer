# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo

from bgm.items import SubjectItem, RelationItem
from typing import Union
from bgm.models import Subject, Relation
from twisted.enterprise import adbapi
import bgm.settings


class MysqlPipeline(object):
    def open_spider(self, spider):
        self.dbpool = adbapi.ConnectionPool("MySQLdb",
                                            host=bgm.settings.MYSQL_HOST,
                                            db=bgm.settings.MYSQL_DBNAME,
                                            user=bgm.settings.MYSQL_USER,
                                            password=bgm.settings.MYSQL_PASSWORD)

    # @inlineCallbacks
    def process_item(self, item: Union[SubjectItem, RelationItem], spider):
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
            insert_sql = Subject.insert(
                **item
            ).on_conflict_replace().sql()
            # Subject.create(**dict(item))
            # Subject.insert(Subject(**dict(item))).on_conflict_replace()
            pass
        elif isinstance(item, RelationItem):
            insert_sql = Relation.insert(
                **item
            ).on_conflict_replace().sql()
            # Relation.create(**dict(item))
            # Relation.insert(Relation(**dict(item))).on_conflict_replace()
        else:
            return
        cursor.execute(*insert_sql)
    # 拿传进的cursor进行执行，并且自动完成commit操作
