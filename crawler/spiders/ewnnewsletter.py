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
        item['name'] = os.path.basename(response.url).replace('.html','')
        item['title'] = q('title').text()
        item['raw_html'] = response.body
        item['orig_url'] = response.url
        item['type_tag'] = 'newsletter'
        item['lang_urls'] = {}
        return item

class NewsletterSpider(CrawlSpider, NewsletterItemExtractorMixin):

    name = 'ewnnewsletter-en'
    allowed_domains = ['www.oikoumene.org']
    start_urls = [
        'http://www.oikoumene.org/en/activities/ewn-home/resources-and-links/ewn-newsletter.html'
    ]
    rules = (
        Rule(SgmlLinkExtractor(allow=(
            '^.*?/activities/ewn-home/ewn-direct-mail/.*\.html',
        )), callback='parse_newsletter', follow=False),
    )

class EWNDeutschPageSpider(CrawlSpider, NewsletterItemExtractorMixin):

    name = 'ewnnewsletter-de'
    allowed_domains = ['www.oikoumene.org']

    start_urls = [
            'http://www.oikoumene.org/de/activities/oekumenisches-wassernetzwerk-oewn/ressourcen-und-links/ewn-newsletter.html'
    ]

    rules = (
        Rule(SgmlLinkExtractor(
            allow='^.*?/activities/oekumenisches-wassernetzwerk-oewn/ewn-direct-mail/.*\.html'),
            callback='parse_newsletter', follow=False),
    )

class EWNFrancaisPageSpider(CrawlSpider, NewsletterItemExtractorMixin):
    name = 'ewnnewsletter-fr'
    allowed_domains = ['www.oikoumene.org']
    start_urls = [
            'http://www.oikoumene.org/fr/activities/roe/ressources-et-liens/le-bulletin-du-reseau-oecumenique-de-leau.html'
    ]

    rules = (
        Rule(SgmlLinkExtractor(
            allow='^.*?/activities/roe/ewn-direct-mail/.*\.html'),
            callback='parse_newsletter', follow=True),
    )

class EWNEspanolPageSpider(CrawlSpider, NewsletterItemExtractorMixin):
    name = 'ewnnewsletter-es'
    start_urls = [
            'http://www.oikoumene.org/es/activities/la-reda/recursos-y-enlaces/boletin-de-noticias-de-la-reda.html'
    ]

    rules = (
        Rule(SgmlLinkExtractor(
            allow='^.*?/activities/la-reda/ewn-direct-mail/.*\.html'),
            callback='parse_newsletter', follow=True),
    )
