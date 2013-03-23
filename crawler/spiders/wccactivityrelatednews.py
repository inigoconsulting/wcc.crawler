from scrapy.item import Item, Field
from scrapy.contrib.spiders.crawl import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from pyquery import PyQuery
import urllib
from base64 import b64encode
import dateutil.parser
import os
import urlparse
import urllib
from scrapy.http import Request
import json

def _get_clean_node_html(node):
    node.find("*[class]").each(
        lambda x: PyQuery(this).attr('class','') if (
        PyQuery(this).attr('class')) else None)

    result = []
    def _extract_value(x):
        value = PyQuery(this).html().replace(u'<p>\xa0</p>',u'')
        result.append(value)

    node.each(_extract_value)
    return ''.join(result)


def clean_url(url):
    parsed = urlparse.urlparse(url)
    qs = parsed.query
    if not qs:
        return url
    qs = urlparse.parse_qs(qs)
    for v in ['print']:
        if qs.has_key(v):
            del qs[v]
    qs = sorted(qs.items(), key=lambda x: x[0])
    qs = [(k,v[0]) for k,v in qs]
    qs = urllib.urlencode(qs)
    data = list(parsed)
    data[4] = qs
    result = urlparse.urlunparse(data)
    for i in range(0,100):
        s = '/browse/%s/' % i 
        if s in result:
            result = result.replace(s, '/')
            break

    return result


class Item(Item):
    orig_url = Field()
    id_url = Field()
    category_ids = Field()

class ItemExtractorMixin(object):

    def parse_item(self, response):
        if response.body is None:
            return

        print response.url
        q = PyQuery(response.body)
        item = Item()
        item['orig_url'] = response.url
        qs = urlparse.parse_qs(
            urlparse.urlparse(response.url).query
        )

        item['category_ids'] = qs['tx_ttnews[cat]'][0].split(
                ',') if (
                qs.has_key('tx_ttnews[cat]') ) else None

        def _extract_id_url(x):
            url = PyQuery(this).attr('href')
            if 'id=' in url:
                item['id_url'] = url

        q('#footer a').each(_extract_id_url)

        return item

class ENSpider(CrawlSpider, ItemExtractorMixin):

    name = 'wccactivityrelatednews-en'
    allowed_domains = ['www.oikoumene.org']
    
    def __init__(self, *args, **kwargs):
        dirname = os.path.dirname(__file__)
        data = json.loads(open(
            os.path.join(dirname, '..', '..', 'wccactivity-en.json')).read())

        self.start_urls = [
            'http://www.oikoumene.org/%s' % i['news_category_url'] for i in data
        ]

        print '\n'.join(self.start_urls)

        super(ENSpider, self).__init__(*args, **kwargs)


    rules = (
        Rule(SgmlLinkExtractor(allow=('^.*/browse/.*\.html',))),
        Rule(SgmlLinkExtractor(allow=(
            '^.*?/news-management/.*\.html',
        ), process_value=clean_url), callback='parse_item', follow=False),
    )
