# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class LoveFitnessItem(scrapy.Item):
    # define the fields for your item here like:
    b_cate = scrapy.Field()  # 大分类前3个分类
    s_href = scrapy.Field()  # 分类href
    s_cate = scrapy.Field()  # 分类名称
    title = scrapy.Field()  # 标题
    img = scrapy.Field()  # 列表页每个文章图片
    href = scrapy.Field()  # 每篇文章href
    date = scrapy.Field()  # 上传日期
    category = scrapy.Field()  # 分类名称
    author = scrapy.Field()  # 作者
    content = scrapy.Field()  # 详情页内容
    content_img = scrapy.Field()  # 详情页图片
    video = scrapy.Field()  # 详情页视频
    content_html = scrapy.Field()  # 详情页article源码

