from scrapy.item import Item, Field
from scrapy.contrib.spiders.crawl import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from pyquery import PyQuery
import urllib
from base64 import b64encode
import dateutil.parser

class NewsItem(Item):
    name = Field()
    title = Field()
    description = Field()
    bodytext = Field()
    image = Field()
    imageCaption = Field()
    effectiveDate = Field()
    orig_url = Field()
    id_url = Field()
    lang_urls = Field()

class NewsItemExtractorMixin(object):

    def _parse_date(self, datestr):
        d,m,y = datestr.split('.')
        return dateutil.parser.parse('20%s-%s-%s' % (y,m,d))

    def parse_newsitem(self, response):
        q = PyQuery(response.body)
        item = NewsItem()
        item['title'] = q('#news h1').text()
        edate = q('#news .date').text()
        effectiveDate = self._parse_date(edate)
        item['effectiveDate'] = effectiveDate.isoformat()
        image_loader_url = q('#news .img a').attr('href')
        if image_loader_url:
            qi = PyQuery(urllib.urlopen(
                'http://www.oikoumene.org/%s' % image_loader_url).read())
            image_url = qi('img').attr('src')
            item['image'] = b64encode(urllib.urlopen(
                'http://www.oikoumene.org/%s' % image_url).read())
            item['imageCaption'] = q('#news .img .caption').text()
        bodytext = q('#news .news-content')
        bodytext.remove('.news_footer')
        bodytext.remove('.more_link')

        # cleanup html and set bodytext
        bodytext.find("*[class]").each(lambda x: PyQuery(this).attr('class',''))
        item['bodytext'] = bodytext.html().replace(u'<p>\xa0</p>',u'')
#        item['description'] = bodytext.find('b:first').text()
        item['description'] = ''
        
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

class EnglishNewsSpider(CrawlSpider, NewsItemExtractorMixin):

    name = 'wccnews-en'
    allowed_domains = ['www.oikoumene.org']
    start_urls = [
            'http://www.oikoumene.org/en/news.html'
    ]
    rules = (
            Rule(SgmlLinkExtractor(allow='^.*?/news/browse/.*\.html')),
        Rule(SgmlLinkExtractor(allow=(
            '^.*?/news/news-management/.*/article/.*\.html',
        )), callback='parse_newsitem', follow=False),
    )

class DeutschNewsSpider(CrawlSpider, NewsItemExtractorMixin):

    name = 'wccnews-de'
    allowed_domains = ['www.oikoumene.org']
    start_urls = [
            'http://www.oikoumene.org/de/nachrichten.html'
    ]
    rules = (
            Rule(SgmlLinkExtractor(allow='^.*?/nachrichten/browse/.*\.html')),
        Rule(SgmlLinkExtractor(allow=(
            '^.*?/nachrichten/news-management/.*/article/.*\.html',
        )), callback='parse_newsitem', follow=False),
    )

class FrancaisNewsSpider(CrawlSpider, NewsItemExtractorMixin):

    name = 'wccnews-fr'
    allowed_domains = ['www.oikoumene.org']
    start_urls = [
            'http://www.oikoumene.org/fr/nouvelles.html'
    ]
    rules = (
            Rule(SgmlLinkExtractor(allow='^.*?/nouvelles/browse/.*\.html')),
        Rule(SgmlLinkExtractor(allow=(
            '^.*?/nouvelles/news-management/.*/article/.*\.html',
        )), callback='parse_newsitem', follow=False),
    )

class EspanolNewsSpider(CrawlSpider, NewsItemExtractorMixin):

    name = 'wccnews-es'
    allowed_domains = ['www.oikoumene.org']
    start_urls = [
            'http://www.oikoumene.org/es/novedades.html'
    ]
    rules = (
            Rule(SgmlLinkExtractor(allow='^.*?/novedades/browse/.*\.html')),
        Rule(SgmlLinkExtractor(allow=(
            '^.*?/novedades/news-management/.*/article/.*\.html',
        )), callback='parse_newsitem', follow=False),
    )

class PortugueseNewsSpider(CrawlSpider, NewsItemExtractorMixin):

    name = 'wccnews-pt'
    allowed_domains = ['www.oikoumene.org']
    start_urls = [
            'http://www.oikoumene.org/po/novidades.html'
    ]
    rules = (
            Rule(SgmlLinkExtractor(allow='^.*?/novidades/browse/.*\.html')),
        Rule(SgmlLinkExtractor(allow=(
            '^.*?/novidades/news-management/.*/article/.*\.html',
        )), callback='parse_newsitem', follow=False),
    )

