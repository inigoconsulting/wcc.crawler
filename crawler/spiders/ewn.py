from scrapy.item import Item, Field
from scrapy.contrib.spiders.crawl import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from pyquery import PyQuery

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
        image_url = q('#news .img a').attr('href')
        if image_url:
            item['image'] = 'http://www.oikoumene.org/%s' % image_url
            item['imageCaption'] = q('#news .img .caption').text()
        bodytext = q('#news .news-content')
        bodytext.remove('.news_footer')
        bodytext.remove('.more_link')
        item['bodytext'] = bodytext.html()
        item['orig_url'] = response.url
        return item

class EWNEnglishNewsSpider(CrawlSpider, NewsItemExtractorMixin):

    name = 'ewn-english'
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
