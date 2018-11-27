# -*- coding: utf-8 -*-
import scrapy
from love_fitness.items import LoveFitnessItem
from copy import deepcopy
import re
import logging

logger = logging.getLogger(__name__)

class LovefitnessSpider(scrapy.Spider):
    name = 'loveFitness'
    allowed_domains = ['www.love-fitness.com.cn']
    start_urls = ['http://www.love-fitness.com.cn']

    def parse(self, response):
        # 1.大分类分组
        li_list = response.xpath('//ul[@id="main-menu"]/li')[:3]
        for li in li_list:
            item = LoveFitnessItem()
            item['b_cate'] = li.xpath('./a/text()').extract_first()
            # 2.小分类分组
            a_list = li.xpath('.//ul/li/a')
            for a in a_list:
                item['s_href'] = a.xpath('./@href').extract_first()
                item['s_cate'] = a.xpath('./text()').extract_first()
                if item['s_href'] is not None:
                    yield scrapy.Request(
                        item['s_href'],
                        callback=self.parse_fitness,
                        meta={'item': deepcopy(item)}  # deepcopy,防止覆盖
                    )

        # 其他分类的分组
        li_list = response.xpath('//ul[@id="main-menu"]/li')[3:]
        for li in li_list:
            item = {}
            item['s_cate'] = li.xpath('./a/text()').extract_first()
            item['s_href'] = li.xpath('./a/@href').extract_first()
            if item['s_href'] is not None:
                yield scrapy.Request(
                    item['s_href'],
                    callback=self.parse_fitness,
                    meta={'item': item}
                )

    def  parse_fitness(self,response):  # 处理列表页
        # 重难点：scrapy 是 twictid(单词可能拼的不对) 异步框架
        # 这里要注意的是 第一次for循环 和 第二次for循环 用的是一个item
        # 所以，后面的for遍历，会把前面的覆盖。 会出现很多重复的数据
        # 后面的item 用的是前面的 item ,他们会相互影响

        # a = {"a":100,"b":20}
        # b = a
        # b["a"] = 10
        # 这时a 和 b是一样的

        # from copy import deepcopy
        # c = deepcopy(a)   #这样就不是指向一个引用了， 而是另开辟了一块空间

        # 这个item接收的是deepcopy之后item，这样就不会相互影响了，是传递一个真正的值
        item = deepcopy(response.meta['item'])
        #列表页分组 - posts
        posts_list = response.xpath('//div[@class="posts-loop"]/article')
        for posts in posts_list:
            item['title'] = posts.xpath('.//header[@class="entry-header"]/h2/a/text()').extract_first()
            item['img'] = posts.xpath('.//img/@src').extract_first()
            item['date'] = posts.xpath('.//span[@class="posted-on"]/a/time[1]/text()').extract_first()
            item['category'] = posts.xpath('.//span[@class="category"]/a/text()').extract()
            item['href'] = posts.xpath('.//header[@class="entry-header"]/h2/a/@href').extract_first()
            yield scrapy.Request(
                item['href'],
                callback=self.parse_detail,
                meta = {'item':deepcopy(item)}
            )

        # 翻页
        next_url = response.xpath('//a[text()="→"]/@href').extract_first()
        if next_url is not None:
            yield scrapy.Request(
                next_url,
                callback=self.parse_fitness,
                meta = {'item':response.meta['item']}
                # 翻页 也是去列表页，meta 传的是 parse中 大分类，小分类，小分类href的数据
                # 所以在parse_fitness 中设置 item = deepcopy(response.meta['item']) 接收item数据 ,
                # 去接收一个没有经过任何修改的item，只是传过去 大分类，小分类，小分类href
                # 只传 deepcopy(item)的话，也是可以的，但是会覆盖这个解析里的一部分 item
            )

    def parse_detail(self,response): # 处理详情页
        item = response.meta['item']
        item['author'] = response.xpath('//span[@class="author vcard"]/a/text()').extract_first()
        item['content'] = response.xpath('//div[@class="entry-content"]//text()').extract()
        content_img = response.xpath('//div[@class="entry-content"]//img/@src').extract()
        # 详情页中 有的图片有url 前缀， 有的没有 ，需要做数据清洗
        if content_img != []:
            http = 'http://www.love-fitness.com.cn'
            x = 0
            while True:
                if content_img[x][0:30:] == http:
                    pass
                else:
                    content_img[x] = http + content_img[x]
                if x == len(content_img) - 1:
                    break
                x += 1
        item['content_img'] = content_img
        item['video'] = response.xpath('//div[@class="player"]/iframe/@src').extract()
        item['content_html'] = re.findall('<main id="main"[\s\S]*?(<article[\s\S]*?)<!-- .entry-content -->',response.body.decode())
        item['content_html'] = item['content_html'][0] if len(item['content_html'])>0 else None
        yield item