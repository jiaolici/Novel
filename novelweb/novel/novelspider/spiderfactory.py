from .spiders import zonghengSpider,xbiqugeSpider

def getSpider(url):
    if 'zongheng.com' in url:
        return zonghengSpider.zongheng
    if 'xbiquge.la' in url:
        return xbiqugeSpider.xbiquge
def getAllSpider():
    return (xbiqugeSpider.xbiquge,)