from scrapy.item import Item, Field
from scrapy.contrib.spiders.crawl import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from pyquery import PyQuery
import urllib
from base64 import b64encode

class NewsItem(Item):
    name = Field()
    title = Field()
    description = Field()
    bodytext = Field()
    image = Field()
    imageCaption = Field()
    effectiveDate = Field()
    orig_url = Field()

class NewsItemExtractorMixin(object):

    def parse_newsitem(self, response):
        q = PyQuery(response.body)
        item = NewsItem()
        item['title'] = q('#news h1').text()
        item['effectiveDate'] = q('#news .date').text()
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
