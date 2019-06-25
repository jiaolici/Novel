# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
from scrapy.conf import settings
import datetime

class NovelscrapyPipeline(object):
    def __init__(self):
        host = settings["MYSQL_HOST"]
        port = settings["MYSQL_PORT"]
        dbname = settings["MYSQL_DBNAME"]
        user = settings["MYSQL_USER"]
        passwd = settings["MYSQL_PASSWD"]
        print(host, port, dbname, user, passwd)
        self.db = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=dbname, charset='utf8')
        self.cur = self.db.cursor()

    def process_item(self, item, spider):
        sql = '''
INSERT INTO novel (author,name,intr,cover,novel_type,last_update_chapter,last_update_time,status,source,novel_url) 
VALUES ('%(author)s','%(name)s','%(intr)s','%(cover)s','%(novel_type)s','%(last_update_chapter)s','%(last_update_time)s',%(status)d,'%(source)s','%(novel_url)s') 
ON DUPLICATE KEY UPDATE author='%(author)s',name='%(name)s',intr='%(intr)s',cover='%(cover)s',novel_type='%(novel_type)s',last_update_chapter='%(last_update_chapter)s',last_update_time='%(last_update_time)s',status=%(status)d,source='%(source)s',novel_url=0'%(novel_url)s'
'''
        sql = sql % dict(item)
        try:
            self.cur.execute(sql)
            self.db.commit()
            return item
        except:
            print('mysql insert exception:'+sql)
            self.db.rollback()

    def close_spider(self,spider):
        self.db.close()

