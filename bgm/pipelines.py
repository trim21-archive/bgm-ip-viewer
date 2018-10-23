# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from bgm.items import SubjectItem, RelationItem
from typing import Union
from bgm.models import Subject, Relation
from twisted.enterprise import adbapi
import bgm.settings
from data_cleaner.main import add_new_subject, pre_remove_relation, pre_remove
import datetime
from bgm.spiders.bgm_tv_wiki import BgmTvWikiSpider

add_subject = set()

import os
from os import path
from pathlib import Path

file_lock = Path('/tmp/scrapy_lock')


class MysqlPipeline(object):
    def open_spider(self, spider):
        if isinstance(spider, BgmTvWikiSpider):
            self.wiki = True
            if file_lock.exists():
                exit()
            else:
                with open(file_lock, 'w', encoding='utf8') as f:
                    f.write(str(datetime.datetime.now()))
        else:
            self.wiki = False
        self.dbpool = adbapi.ConnectionPool(
            "MySQLdb",
            db=bgm.settings.MYSQL_DBNAME,
            host=bgm.settings.MYSQL_HOST,
            user=bgm.settings.MYSQL_USER,
            password=bgm.settings.MYSQL_PASSWORD,
            charset='utf8mb4',
        )

    # @inlineCallbacks
    def process_item(self,
                     item: Union[SubjectItem, RelationItem],
                     spider):
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
            insert_sql = Subject.insert(
                **item
            ).on_conflict(
                preserve=(Subject.name_cn, Subject.name,

                          Subject.image, Subject.tags, Subject.locked,

                          Subject.info, Subject.score_details,

                          Subject.score, Subject.wishes, Subject.done,
                          Subject.doings, Subject.on_hold, Subject.dropped,
                          ),
            ).sql()
            if self.wiki:
                add_subject.add(int(item['id']))
        elif isinstance(item, RelationItem):
            insert_sql = Relation.insert(
                id=f'{item["source"]}-{item["target"]}',
                **item
            ).on_conflict(
                preserve=(Relation.relation,),
            ).sql()
        else:
            return
        cursor.execute(*insert_sql)

    def close_spider(self, spider):
        if self.wiki:
            if file_lock.exists():
                try:
                    os.remove(file_lock)
                except OSError:
                    pass
            print(datetime.datetime.now())
            print('finish crawling, start building map')
            pre_remove()
            print(add_subject)
            for id in add_subject:
                add_new_subject(id)
            print('finish build map')
            print(datetime.datetime.now())
