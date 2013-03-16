from scrapy.item import Item, Field
from scrapy.contrib.spiders.crawl import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from pyquery import PyQuery
import urllib
from base64 import b64encode
import urlparse
import re
import os

class NewsletterItem(Item):
    name = Field()
    title = Field()
    raw_html = Field()
    orig_url = Field()
    lang_urls = Field()
    type_tag = Field()

class NewsletterItemExtractorMixin(object):

    def parse_newsletter(self, response):
        q = PyQuery(response.body)

        item = NewsletterItem()

        path = urlparse.urlparse(response.url).path
        item['name'] = os.path.basename(path).replace('.html','')
        item['title'] = q('title').text()
        item['raw_html'] = response.body
        item['orig_url'] = response.url
        item['type_tag'] = 'newsletter'
        item['lang_urls'] = {}
        return item

class NewsletterSpider(CrawlSpider, NewsletterItemExtractorMixin):

    name = 'piefalerts-en'
    allowed_domains = ['www.oikoumene.org']
    start_urls = [
            'http://www.oikoumene.org/en/programmes/public-witness-addressing-power-affirming-peace/churches-in-the-middle-east/pief/news-events/pief-alerts.html'
    ]
    rules = (
        Rule(SgmlLinkExtractor(allow=(
            '^.*?/en/programmes/public-witness-addressing-power-affirming-peace/churches-in-the-middle-east/pief/news-events/alerts/.*\.html',
        )), callback='parse_newsletter', follow=False),
    )
