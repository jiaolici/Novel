import json,requests
from lxml import etree
from .defaultSpider import DefaultSpider

class XbiqugeSpider(DefaultSpider):
    def getSourceCode(self,url):
        headers = self.headers
        response = requests.get(url, headers=headers, verify=False).content
        return response

    def getChapters(self, url):
        sourceCode = self.getSourceCode(url)
        selector = etree.HTML(sourceCode)
        novelName = selector.xpath('/html/body/div/div[3]/div[2]/div[1]/h1/text()')[0]
        chapters = []
        for i,each in enumerate(selector.xpath('/html/body/div/div[5]/div/dl/dd')):
            chapterId = i+1
            chapterUrl = 'http://www.xbiquge.la'+each.xpath('./a/@href')[0]
            title = each.xpath('./a/text()')[0]
            content = {'novelName':novelName,'chapterId':chapterId,'chapterUrl':chapterUrl,'title':title}
            chapters.append(content)
        return chapters

    def getChapterContent(self,url):
        sourceCode = self.getSourceCode(url)
        sourceCode = sourceCode.decode()
        selector = etree.HTML(sourceCode)
        contents = selector.xpath('//*[@id="content"]/text()')
        content = ''
        for i in contents:
            i = i.replace('\r','<br>')
            i = i.replace('\xa0', '&ensp;')
            content+=i
        return content

    def getSearch(self,keyword):
        sourceCode = self.getSourceCode('http://www.xbiquge.la/xiaoshuodaquan/')
        selector = etree.HTML(sourceCode)
        urls = selector.xpath("//a[contains(text(),'"+keyword+"')]/@href")
        novels = []
        for url in urls:
            detail_sourceCode = self.getSourceCode(url)
            detail_sourceCode = detail_sourceCode.decode()
            detail_selector = etree.HTML(detail_sourceCode)
            novel = {}
            novel['name'] = detail_selector.xpath('/html/body/div/div[3]/div[2]/div[1]/h1/text()')[0]
            novel['author'] = detail_selector.xpath('/html/body/div/div[3]/div[2]/div[1]/p[1]/text()')[0].split('：')[-1]
            novel['intr'] = detail_selector.xpath('/html/body/div/div[3]/div[2]/div[2]/p[2]/text()')[0]
            novel['cover'] = detail_selector.xpath('/html/body/div/div[3]/div[3]/div/img/@src')[0]
            novel['novel_type'] = detail_selector.xpath('/html/body/div/div[3]/div[1]/a[2]/text()')[0].rstrip('小说')
            novel['last_update_chapter'] = detail_selector.xpath('/html/body/div/div[3]/div[2]/div[1]/p[4]/a/text()')[0]
            novel['last_update_time'] = detail_selector.xpath('/html/body/div/div[3]/div[2]/div[1]/p[3]/text()')[0].split('：')[1]
            novel['status'] = 0
            novel['source'] = '新笔趣阁'
            novel['novel_url'] = url
            novels.append(novel)
        return novels

xbiquge = XbiqugeSpider()