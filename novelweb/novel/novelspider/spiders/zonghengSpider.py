import json,requests
from lxml import etree
from .defaultSpider import DefaultSpider

class ZonghengSpider(DefaultSpider):
    baseUrl = 'http://www.zongheng.com/'
    def getSourceCode(self,url):
        headers = self.headers
        response = requests.get(url, headers=headers, verify=False).content
        return response

    def getRecommend(self):
        response = self.getSourceCode(self.baseUrl)
        recommends = list()
        for i in etree.HTML(response).xpath('/html/body/div[2]/div[3]/div[2]/div[2]/ul/li'):
            recommend = dict()
            recommend['url'] = i.xpath('./a/@href')[0]
            recommend['imag_url'] = i.xpath('./a/img/@src')[0]
            recommend['name'] = i.xpath('./a/img/@alt')[0]
            try:
                recommend['short_intr'] = i.xpath('./a/div/text()')[0]
            except IndexError:
                recommend['short_intr'] = ''
            recommends.append(recommend)
        return recommends

zongheng = ZonghengSpider()