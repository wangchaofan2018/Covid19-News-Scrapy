import scrapy
import re
from scrapy import Spider
from scrapy import Request
from scrapy import Selector
from covid_19.items import BaseDataItem

class Shan_xiSpider(Spider):
    def __init__(self):
        super(Shan_xiSpider, self).__init__()
        self.num = 1
    name = "shanxi3"
    original_url = "http://www.scio.gov.cn/xwfbh/gssxwfbh/xwfbh/shan_xi/"
    def start_requests(self):
        url = "http://www.scio.gov.cn/xwfbh/gssxwfbh/xwfbh/shan_xi/index.htm"
        yield scrapy.Request(url=url,callback=self.parse,dont_filter=True)
    def parse(self,response):
        sel = Selector(response)
        detail_page_info = sel.xpath('//table[@id="PagerOutline1"]//li')
        for info in detail_page_info:
            detail_url_href = info.xpath('./div/a/@href').extract_first()
            detail_url = self.original_url + detail_url_href
            publish_time_all = info.xpath('./span[@class="ftime fr"]/text()').extract_first()
            publish_time = publish_time_all[1:-1]
            # title = info.xpath('./div/a/text()').extract_first()
            yield scrapy.Request(url = detail_url,meta={"detail_url":detail_url,"publish_time":publish_time},callback=self.detail_parse,dont_filter=True)

        if self.num < 4:
            next_page_url = "http://www.scio.gov.cn/xwfbh/gssxwfbh/xwfbh/shan_xi/index_%s.htm"%str(self.num)
            self.num += 1
            yield scrapy.Request(url=next_page_url,callback=self.parse,dont_filter=True)

    def detail_parse(self,response):
        item = BaseDataItem()
        sel = Selector(response)
        item["detail_url"] = response.meta["detail_url"]
        item["publish_time"] = response.meta["publish_time"]
        title = ""
        title_text = sel.xpath('//div[@id="content"]//p[1]/text()').extract()
        for tit in title_text:
            title = title + tit.strip() +"\n"
        item["title"] = title
        summary = ""
        summary_text = sel.xpath('//div[@id="content"]//p[2]//text()').extract()
        for row in summary_text:
            summary = summary + row.strip() +"\n"
        item["summary"] = summary
        item["province"] = "陕西"
        item["location"] = ""
        attend_persons = ""
        attend_persons_text = sel.xpath('//div[@id="content"]//p/span[@style="color: #0033ff"]//text()').extract()
        for per in attend_persons_text:
            attend_persons = attend_persons + per.strip() +"\n"
        item["attend_persons"] = attend_persons
        item["time_stamp"] = ""
        content = ""
        content_text = sel.xpath('//div[@id="content"]//p//text()').extract()
        for col in content_text[1:]:
            content = content + col.strip() +"\n"
        item["content"] = content
        print(item)
        # yield item