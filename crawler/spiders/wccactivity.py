from scrapy.item import Item, Field
from scrapy.contrib.spiders.crawl import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from pyquery import PyQuery
import urllib
from base64 import b64encode
import dateutil.parser

import urlparse
import urllib
import re


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
    return urlparse.urlunparse(data)


class Item(Item):
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
    news_category_url = Field()
    category_id = Field()
    document_folder_url = Field()

class ItemExtractorMixin(object):


    def _parse_date(self, datestr):
        d,m,y = datestr.split('.')
        return dateutil.parser.parse('20%s-%s-%s' % (y,m,d))

    def parse_item(self, response):
        if response.body is None:
            return

        q = PyQuery(response.body)

        if q('#activity_description').length == 0:
            return 

        item = Item()
        item['title'] = q('title').text()
        item['bodytext'] = _get_clean_node_html(q('#activity_description'))
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

        item['news_category_url'] = None

        def _extract_newscategory_url(x):
            url = PyQuery(this).attr('href')
            if self._category_url.match(url):
                item['news_category_url'] = url

        q('#activity_news a').each(_extract_newscategory_url)

        qs = urlparse.parse_qs(
            urlparse.urlparse(response.url).query
        )

        item['category_id'] = qs['tx_ttnews[cat]'][0].split(
                ',')[0] if (
                qs.has_key('tx_ttnews[cat]') ) else None

        def _extract_document__folder_url(x):
            url = PyQuery(this).attr('href')
            if self._document_folder_url.match(url):
                item['document_folder_url'] = url

        q('.link_more a').each(_extract_document__folder_url)
        return item


class ENSpider(CrawlSpider, ItemExtractorMixin):

    name = 'wccactivity-en'
    allowed_domains = ['www.oikoumene.org']
    start_urls = ['http://www.oikoumene.org/en/programmes/']

    _category_url = re.compile('.*en/news/news-on-selected-category.html.*')
    _document_folder_url = re.compile('.*document.*')

    rules = (
        Rule(SgmlLinkExtractor(allow=(
            '^.*?/en/programmes/.*\.html',
        ), process_value=clean_url), callback='parse_item', follow=True),
    )

class DESpider(CrawlSpider, ItemExtractorMixin):

    name = 'wccactivity-de'
    allowed_domains = ['www.oikoumene.org']
    start_urls = ['http://www.oikoumene.org/de/programme.html']

    _category_url = re.compile('.*de/nachrichten/nachrichten.html.*')
    _document_folder_url = re.compile('.*dokumentation.*')

    rules = (
        Rule(SgmlLinkExtractor(allow=(
            '^.*?/de/programme/.*\.html',
        ), process_value=clean_url), callback='parse_item', follow=True),
    )
