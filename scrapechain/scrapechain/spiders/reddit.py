import scrapy
from scrapechain.spiders import BaseSpider
from ..items import ScrapechainItem
from scrapy.http.request import Request



class RedditSpider(BaseSpider):
    name = 'reddit'
    allowed_domains = ['reddit.com']
    start_urls = ['http://reddit.com/']
    channel_api = 'https://gateway.reddit.com/desktopapi/v1/subreddits/%s?rtj=only&redditWebClient=web2x&app=web2x-client-production&allow_over18=&include=prefsSubreddit&after=&dist=8&forceGeopopular=false&layout=card&sort=new'
    channels = ['Binance','Bitcoin','cryptexlock','CryptoCurrency','CryptoCurrencyClassic']
    custom_settings = {
        'ITEM_PIPELINES': {
            'scrapechain.pipelines.ElasticsearchPipeline':20
        }
    }

    type_name = 'channels'
    unique_key = 'post_id'

    def __init__(self):
        self.type_name = "channels"

    def start_requests(self):
        for channel in self.channels:
            url = self.channel_api%channel
            print("request to %s"%url)
            yield Request(url,callback=self.parse,meta={'channel':channel})

    def parse(self, response):
        data = self.converter(response.text,'json')
        posts = data.get('posts')
        if not posts:
            print("response not available. Exiting")
            return

        for key,post in posts.items():
            item = ScrapechainItem()
            item["channel"] = response.meta.get('channel')
            item['post_id'] = post.get('id')
            item['created'] = post.get('created')
            item['title'] = post.get('title')
            item['authorId'] = post.get('authorId')
            item['author'] = post.get('author')
            item['upvoteRatio'] = item.get('upvoteRatio')
            item["permalink"] = item.get('permalink')
            medias = item.get('media')
            item['richtext'] = []
            item['content'] = ""
            if medias:
                richtexts = medias.get('richtextContent').get('document')
                if richtexts:
                    richtext_list = []
                    for richtext in richtexts:
                        subtexts = richtext.get('c')
                        subtext_list = []
                        for subtext in subtexts:
                            subtext_dict = {}
                            key = subtext.get('e')
                            subtext_dict[key] = subtext.get('t')
                            subtext_list.append(subtext_dict)
                        richtext_list += subtext_list
                    item['richtext'] = richtext_list

                item['content'] = medias.get('content')

            yield item
