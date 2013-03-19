from scrapy.item import Item, Field
from scrapy.contrib.spiders.crawl import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from pyquery import PyQuery
import urllib
from base64 import b64encode
import dateutil.parser

class FeatureNewsItem(Item):
    orig_url = Field()
    id_url = Field()
    lang_urls = Field()

class FeatureNewsItemExtractorMixin(object):

    def parse_newsitem(self, response):
        q = PyQuery(response.body)
        item = FeatureNewsItem() 
        item['orig_url'] = response.url
        item['lang_urls'] = {}

        def _extract_langurl(x):
            ql = PyQuery(this)
            lang = ql.attr('lang')
            item['lang_urls'][lang] = 'http://www.oikoumene.org/%s' % ql.attr('href')

        q('#languages a.lang').each(_extract_langurl)

        def _extract_id_url(x):
            url = PyQuery(this).attr('href')
            if 'id=' in url:
                item['id_url'] = url


        q('#footer a').each(_extract_id_url)
        return item

class EnglishNewsSpider(CrawlSpider, FeatureNewsItemExtractorMixin):

    name = 'wccfeaturenews-en'
    allowed_domains = ['www.oikoumene.org']
    start_urls = [
            'http://www.oikoumene.org/en/news/feature-stories.html'
    ]
    rules = (
            Rule(SgmlLinkExtractor(allow='^.*?/news/feature-stories/browse/.*\.html')),
        Rule(SgmlLinkExtractor(allow=(
            '^.*?/news/news-management/.*/article/.*\.html',
        )), callback='parse_newsitem', follow=False),
    )

class DeutschNewsSpider(CrawlSpider, FeatureNewsItemExtractorMixin):

    name = 'wccfeaturenews-de'
    allowed_domains = ['www.oikoumene.org']
    start_urls = [
            'http://www.oikoumene.org/de/nachrichten/feature.html'
    ]
    rules = (
            Rule(SgmlLinkExtractor(allow='^.*?/nachrichten/feature/browse/.*\.html')),
        Rule(SgmlLinkExtractor(allow=(
            '^.*?/nachrichten/news-management/.*/article/.*\.html',
        )), callback='parse_newsitem', follow=False),
    )

class FrancaisNewsSpider(CrawlSpider, FeatureNewsItemExtractorMixin):

    name = 'wccfeaturenews-fr'
    allowed_domains = ['www.oikoumene.org']
    start_urls = [
            'http://www.oikoumene.org/fr/nouvelles/articles.html'
    ]
    rules = (
            Rule(SgmlLinkExtractor(allow='^.*?/nouvelles/articles/browse/.*\.html')),
        Rule(SgmlLinkExtractor(allow=(
            '^.*?/nouvelles/news-management/.*/article/.*\.html',
        )), callback='parse_newsitem', follow=False),
    )

class EspanolNewsSpider(CrawlSpider, FeatureNewsItemExtractorMixin):

    name = 'wccfeaturenews-es'
    allowed_domains = ['www.oikoumene.org']
    start_urls = [
            'http://www.oikoumene.org/es/novedades/cronicas.html'
    ]
    rules = (
            Rule(SgmlLinkExtractor(allow='^.*?/novedades/cronicas/browse/.*\.html')),
        Rule(SgmlLinkExtractor(allow=(
            '^.*?/novedades/news-management/.*/article/.*\.html',
        )), callback='parse_newsitem', follow=False),
    )

class PortugueseNewsSpider(CrawlSpider, FeatureNewsItemExtractorMixin):

    name = 'wccfeaturenews-pt'
    allowed_domains = ['www.oikoumene.org']
    start_urls = [
            'http://www.oikoumene.org/po/novidades/feature-stories.html'
    ]
    rules = (
            Rule(SgmlLinkExtractor(allow='^.*?/novidades/feature-stories/browse/.*\.html')),
        Rule(SgmlLinkExtractor(allow=(
            '^.*?/novidades/news-management/.*/article/.*\.html',
        )), callback='parse_newsitem', follow=False),
    )

