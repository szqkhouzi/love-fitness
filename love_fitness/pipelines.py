# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import codecs
import logging
import re

logger = logging.getLogger(__name__)

class LoveFitnessPipeline(object):
    def __init__(self):
        self.file = codecs.open('fitness.json','w',encoding='utf-8')

    def process_item(self, item, spider):
        item['content'] = self.process_content(item['content'])
        # # 测试
        print(item)

        line = json.dumps(dict(item),ensure_ascii=False)+'\n'
        self.file.write(line)
        return item

    def process_content(self,content):
        content = [re.sub(r'\xa0|\s','',i) for i in content]
        content = [i for i in content if len(i)>0]  # 去除列表中的空字符串
        return content

    def spider_close(self):
        self.file.close()
