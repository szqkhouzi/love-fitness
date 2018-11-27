# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
from pymongo import MongoClient
from scrapy.conf import settings
import codecs
import logging
import re

logger = logging.getLogger(__name__)

class LoveFitnessPipeline(object):
    def __init__(self):
        self.file = codecs.open('fitness.json','w',encoding='utf-8')

        # 获取setting主机名、端口号和数据库名
        host = settings['MONGODB_HOST']
        port = settings['MONGODB_PORT']
        dbname = settings['MONGODB_DBNAME']

        # pymongo.MongoClient(host, port) 创建MongoDB链接
        client = MongoClient(host=host,port=port)

        # 指向指定的数据库
        mdb = client[dbname]
        # 获取数据库里存放数据的表名
        self.post = mdb[settings['MONGODB_DOCNAME']]

    def process_item(self, item, spider):
        item['content'] = self.process_content(item['content'])
        # 测试
        # print(item)

        data = dict(item)
        line = json.dumps(data,ensure_ascii=False)+'\n'
        self.file.write(line)

        # 向指定的表里添加数据
        self.post.insert(data)
        return item

    def process_content(self,content):
        content = [re.sub(r'\xa0|\s','',i) for i in content]
        content = [i for i in content if len(i)>0]  # 去除列表中的空字符串
        return content

    def spider_close(self):
        self.file.close()
