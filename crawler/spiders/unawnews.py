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
        dd, tt = datestr.strip().split(' ')
        d,m,y = dd.split('.')
        return dateutil.parser.parse('20%s.%s.%s %s' % (y,m,d,tt))

    def parse_newsitem(self, response):
        q = PyQuery(response.body)
        item = NewsItem()
        item['title'] = q('#news h1').text()
        if not item['title']:
            item['title'] = q('title').text()
        item['effectiveDate'] = self._parse_date(
            q('.news-single-timedata').text()
        ).isoformat()
        image_loader_url = q('.news-single-img a').attr('href')
        if image_loader_url:
            qi = PyQuery(urllib.urlopen(
                'http://www.oikoumene.org/%s' % image_loader_url).read())
            image_url = qi('img').attr('src')
            item['image'] = b64encode(urllib.urlopen(
                'http://www.oikoumene.org/%s' % image_url).read())
            item['imageCaption'] = q('.news-single-imgcaption').text()
        bodytext = q('.news-single-item')
        bodytext.remove('h2:first')
        bodytext.remove('.news-single-backlink')
        bodytext.remove('.news_footer')
        bodytext.remove('.more_link')
        bodytext.remove('.news-single-timedata')

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

class EnglishNewsSpider(CrawlSpider, NewsItemExtractorMixin):

    name = 'unawnews-en'
    allowed_domains = ['www.oikoumene.org']
    start_urls = [
        'http://www.oikoumene.org/en/events-sections/unaw/news.html'
    ]
    rules = (
            Rule(SgmlLinkExtractor(allow='^.*?/events-sections/unaw/news/browse/.*')),
        Rule(SgmlLinkExtractor(allow=(
            '^.*?/events-sections/unaw/news/.*/article/.*\.html',
        )), callback='parse_newsitem', follow=False),
    )

