import scrapy
from scrapechain.spiders import BaseSpider
from scrapy.http.request import Request
from ..items import ScrapechainItem
import datetime


class SolscanSpider(BaseSpider):
    name = 'solscan'
    allowed_domains = ['solscan.io']
    start_urls = ['https://api.solscan.io/transaction/last?q=200']
    transaction_api = 'https://api.solscan.io/transaction?tx='
    home_page = 'https://solscan.io/txs'
    custom_settings = {
        'FEED_FORMAT' : 'csv',
        'FEED_URI': '/home/atakantuncer/Desktop/certik/scrapechain/csv/{0}_{1}.csv'.format(name, datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')),
        'ITEM_PIPELINES': {
            'scrapechain.pipelines.ElasticsearchPipeline':20
        }
    }
    type_name = 'tx'
    unique_key = 'txHash'



    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url,callback=self.parse)

    def parse(self, response):
        data = self.converter(response.text,'json')
        if not data:
            print("response not available. Exiting")
            return

        for d in data:
            tx_url = self.transaction_api + d.get('txHash')
            yield Request(tx_url,callback=self.parse_tx)


    def parse_tx(self,response):
        data = self.converter(response.text,'json')
        item = ScrapechainItem()
        if not data:
            self.log("response not available. Exiting")
            return

        item['txHash'] = item["unique_key"] = data.get('txHash')
        item['fee'] = data.get('fee')
        item['status'] = data.get('status')
        item['blockTime'] = data.get('blockTime')
        item['slot'] = data.get('slot')
        item['logMessage'] = data.get('logMessage')
        inputAccs = data.get('inputAccount')
        item['inputAccount'] = []
        for acc in inputAccs:
            acc_dict = {}
            acc_dict['account'] = acc.get('account')
            acc_dict['signer'] = acc.get('signer')
            acc_dict['writable'] = acc.get('writable')
            acc_dict['preBalance'] = acc.get('preBalance')
            acc_dict['postBalance'] = acc.get('postBalance')

            item['inputAccount'].append(acc_dict)

        parsedInstructions = data.get('parsedInstruction')
        item["parsedInstruction"] = []
        for parsed in parsedInstructions:
            parsed_dict = {}
            parsed_dict['programId'] = parsed.get('programId')
            parsed_dict['type'] = parsed.get('type')
            parsed_dict['data'] = parsed.get('data')
            parsed_dict['dataEncode'] = parsed.get('dataEncode')
            parsed_dict['name'] = parsed.get('name')
            parsed_dict['params'] = parsed.get('params')
            item["parsedInstruction"].append(parsed_dict)

        item["txStatus"] = item.get('txStatus')
        yield item
