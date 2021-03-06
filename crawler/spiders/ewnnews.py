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

    def parse_newsitem(self, response):
        q = PyQuery(response.body)
        item = NewsItem()
        item['title'] = q('#news h1').text()
        edate = q('#news .date').text()
        d,m,y = edate.split('.')
        effectiveDate = dateutil.parser.parse('20%s-%s-%s' % (y,m,d))
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
        item['description'] = bodytext.find('b:first').text()
        item['orig_url'] = response.url
        item['lang_urls'] = {}

        def _extract_langurl(x):
            ql = PyQuery(this)
            lang = ql.attr('lang')
            item['lang_urls'][lang] = 'http://www.oikoumene.org/%s' % ql.attr('href')

        q('#languages a.lang').each(_extract_langurl)

        item['id_url'] = q('#footer a[rel="nofollow"]').attr('href')
        return item

class EWNEnglishNewsSpider(CrawlSpider, NewsItemExtractorMixin):

    name = 'ewnnews-en'
    allowed_domains = ['www.oikoumene.org']
    start_urls = [
        'http://www.oikoumene.org/en/activities/ewn-home/resources-and-links/news.html'
    ]
    rules = (
        Rule(SgmlLinkExtractor(allow='^.*?/activities/ewn-home/resources-and-links/news/.*')),
        Rule(SgmlLinkExtractor(allow=(
            '^.*?/activities/ewn-home/ewn-news-and-events-containers/.*?html',
        )), callback='parse_newsitem', follow=False),
    )

class EWNDeutschNewsSpider(CrawlSpider, NewsItemExtractorMixin):

    name = 'ewnnews-de'
    allowed_domains = ['www.oikoumene.org']

    start_urls = [
        'http://www.oikoumene.org/de/activities/oekumenisches-wassernetzwerk-oewn/ressourcen-und-links/nachrichten.html'
    ]

    rules = (
        Rule(SgmlLinkExtractor(
            allow='^.*?/activities/oekumenisches-wassernetzwerk-oewn/ressourcen-und-links/nachrichten/.*')),
        Rule(SgmlLinkExtractor(
            allow='^.*?/oekumenisches-wassernetzwerk-oewn/ewn-news-and-events-containers/.*?html'),
            callback='parse_newsitem', follow=False)
    )

class EWNFrancaisNewsSpider(CrawlSpider, NewsItemExtractorMixin):
    name = 'ewnnews-fr'
    allowed_domains = ['www.oikoumene.org']
    start_urls = [
        'http://www.oikoumene.org/fr/activities/roe/ressources-et-liens/nouvelles.html'
    ]

    rules = (
        Rule(SgmlLinkExtractor(
        allow='^.*?/activities/roe/ressources-et-liens/nouvelles/.*')),
        Rule(SgmlLinkExtractor(
            allow='^.*?/activities/roe/ewn-news-and-events-containers/.*?html'),
            callback='parse_newsitem', follow=False)
    )

class EWNEspanolNewsSpider(CrawlSpider, NewsItemExtractorMixin):
    name = 'ewnnews-es'
    start_urls = [
        'http://www.oikoumene.org/es/activities/la-reda/recursos-y-enlaces/novedades.html'
    ]

    rules = (
        Rule(SgmlLinkExtractor(
            allow='^.*?/activities/la-reda/recursos-y-enlaces/novedades/.*')),
        Rule(SgmlLinkExtractor(
            allow='^.*?/activities/la-reda/ewn-news-and-events-containers/.*html'),
            callback='parse_newsitem', follow=False)
    )
