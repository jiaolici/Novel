# -*- coding: utf-8 -*-
import scrapy
from .. import items


class XbiqugeSpider(scrapy.Spider):
    name = 'xbiquge'
    allowed_domains = ['xbiquge.la']
    url='http://www.xbiquge.la/'
    type={1:['xuanhuanxiaoshuo','玄幻'],2:['xiuzhenxiaoshuo','修真'],3:['dushixiaoshuo','都市'],
          4:['chuanyuexiaoshuo','穿越'],5:['wangyouxiaoshuo','网游'],6:['kehuanxiaoshuo','科幻']}
    offset=1
    start_urls = [url+type[offset][0]+'/']

    def parse(self, response):
        novel_list=response.xpath('/html/body/div[1]/div[3]/div/div[1]/div/div')
        for novel in novel_list:
            item = items.NovelscrapyItem()
            item['name'] = novel.xpath('./dl/dt/a/text()').extract_first(default='')
            item['author'] = novel.xpath('./dl/dt/span/text()').extract_first(default='')
            item['cover'] = novel.xpath('./div[1]/a/img/@src').extract_first(default='')
            item['novel_type'] = self.type[self.offset][1]
            item['status'] = 0#是否完结，0表示未完结
            item['source'] = '新笔趣阁'
            item['novel_url'] = novel.xpath('./div[1]/a/@href').extract_first(default='')
            novel_url = novel.xpath('./dl/dt/a/@href').extract_first(default='')
            yield scrapy.Request(url=novel_url,meta={'item':item},callback=self.parse_detail)

        if self.offset<6:
            self.offset+=1
            yield scrapy.Request(url=self.url+self.type[self.offset][0]+'/',callback=self.parse)

    def parse_detail(self,response):
        item = response.meta['item']
        item['intr'] = response.xpath('/html/body/div/div[3]/div[2]/div[2]/p[2]/text()').extract_first(default='')
        item['last_update_chapter'] = response.xpath('/html/body/div/div[3]/div[2]/div[1]/p[4]/a/text()').extract_first(default='')
        item['last_update_time'] = response.xpath('/html/body/div/div[3]/div[2]/div[1]/p[3]/text()').extract_first(default='').split('：')[1]
        yield item
