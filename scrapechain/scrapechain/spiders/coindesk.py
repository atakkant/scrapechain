import scrapy
from scrapechain.spiders import BaseSpider
from ..items import ScrapechainItem
from scrapy.http.request import Request


class CoindeskSpider(BaseSpider):
    name = 'coindesk'
    allowed_domains = ['coindesk.com']
    start_urls = ['https://www.coindesk.com/search?s=breach&df=720']
    custom_settings = {
        'ITEM_PIPELINES': {
            'scrapechain.pipelines.ElasticsearchPipeline':20
        },
        'DOWNLOADER_MIDDLEWARES': {
            'scrapechain.middlewares.SeleniumMiddleware': 20,
        },
    }

    type_name = 'news'
    unique_key = 'unique_key'

    def __init__(self):
        self.wait_at_open = 3

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url,callback=self.parse)

    def parse(self,response):
        number_of_results = response.xpath('//div[contains(@class,"searchstyles__ResultsData")]/div[1]//h6/text()').get('').replace("Showing","").replace("results for","").strip()
        print("number of results: %s"%number_of_results)

        news = response.xpath('//div[contains(@class,"searchstyles__ResultsData")]/div/div/div/a/@href').getall()
        if not news:
            print("news not acquired. Exiting")
            return

        for new in news:
            yield Request(response.urljoin(new),callback=self.parse_news)

    def parse_news(self,response):
        item = ScrapechainItem()
        item['category'] = response.xpath('//div[@class="at-category"]/a/span/text()').get('')
        if not item['category']:
            item['category'] = response.xpath('//div[contains(@class,"headline1")]/h1/text()').get('')
        item["title"] = response.xpath('//div[@class="at-headline"]/h1/text()').get('')
        if not item["title"]:
            item["title"] = response.xpath('//div[contains(@class,"headline2")]/h1/text()').get('')
        item["subtitle"] = response.xpath('//div[@class="at-subheadline"]/h2/text()').get('')
        if not item["subtitle"]:
            item["subtitle"] = response.xpath('//div[contains(@class,"headline3")]//text()').get('')
        item["author"] = response.xpath('//div[@class="at-authors"]/span/a/text()').get('')
        item["created"] = response.xpath('//div[contains(@class,"at-created")]/div/span/text()').get('')
        if not item['created']:
            item["created"] = response.xpath('//div[contains(@class,"at-created")]//span/text()').get('')
        item["updated"] = "".join(response.xpath('//div[@class="at-updated"]/span/text()').getall()).replace("Updated ","")
        item["text"] = ". ".join(response.xpath('//div[@class="main-body-grid"]//div[contains(@class,"contentstyle")]//text()').getall())
        item["url"] = response.url
        item["unique_key"] = self.create_unique_id(item["url"])

        yield item
        print(item)
