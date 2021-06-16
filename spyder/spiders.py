import scrapy 
from scrapy.crawler import CrawlerProcess
import scrapydo
import time
import logging
import sys
from urllib.parse import urljoin


scrapydo.setup()

class DealSpider(scrapy.Spider):
    name = "deal_spyder"
    search_result = {}
    info = {}

    def __init__(self, user_input=None, mode=None, optional_url=None):

        self.user_input = user_input
        self.base = f"https://pricespy.co.uk/"
        self.search = f'search?search={self.user_input}'
        self.optional_url = optional_url
        self.mode = mode

    def start_requests(self):
        if self.mode == 'initial':
            url = urljoin(self.base, self.search)
            yield scrapy.Request(url=url, callback=self.get_options)
        
        
        if self.mode == 'price_scrape':
            url = urljoin(self.base, self.optional_url)
            yield scrapy.Request(url=url, callback=self.scrape_info)

    def scrape_info(self, response):

 
        for i in range(len(response.css(".ProductName-sc-1e897he-2::text").getall())):
            self.info[i] = {
                            'company' : response.css('.StoreInfoTitle-zagdae-6::text')[i].get(),
                            'name' : response.css(".ProductName-sc-1e897he-2::text")[i].get(),
                            'price': response.css(".PriceLabel-sc-1sn64xr-3::text")[i].get(),
                            'stock': response.css(".IconAndText-sc-1vuvpij-1 svg::attr(class)")[i].get()
                            }
       
     
        for i in self.info:
            stock = self.info[i]['stock']
            name = self.info[i]['name']
            price = self.info[i]['price']

            stock_status = ['in', 'out', 'unknown']
            if stock_status[0] in stock:
                self.info[i]['stock'] = True

            if stock_status[1] in stock:
                self.info[i]['stock'] = False
            
            if stock_status[2] in stock:
                self.info[i]['stock'] = True

    def get_options(self, response):
        self.search_result.clear()
        for i, n in enumerate(range(3), start=1):
            self.search_result[i] = {'name' : response.css(".ProductName-bvh34t-4::text")[n].get(),
                                    'link' : response.css(".ProductLink-bvh34t-0::attr(href)")[n].get()}
          
    def run(self):
        scrapydo.run_spider(DealSpider, user_input=self.user_input, mode=self.mode, optional_url=self.optional_url)
    



if __name__=='__main__':
    logging.getLogger('scrapy').propagate = False
    DealSpider()