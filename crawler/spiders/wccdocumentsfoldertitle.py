from scrapy.item import Item, Field
from scrapy.contrib.spiders.crawl import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from pyquery import PyQuery
import urllib
from base64 import b64encode
import dateutil.parser
import urlparse 
import urllib

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
    orig_url = Field()
    id_url = Field()
    lang_urls = Field()

class ItemExtractorMixin(object):

    def _parse_date(self, datestr):
        d,m,y = datestr.split('.')
        return dateutil.parser.parse('20%s-%s-%s' % (y,m,d))

    def parse_item(self, response):
        q = PyQuery(response.body)
        item = Item()
        item['title'] = q('title').text()
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

class Spider(CrawlSpider, ItemExtractorMixin):

    name = 'wccdocumentsfoldertitle-en'
    allowed_domains = ['www.oikoumene.org']
    start_urls = [
            'http://www.oikoumene.org/en/resources/documents.html',
#            'http://www.oikoumene.org/de/dokumentation/documents.html',
#            'http://www.oikoumene.org/fr/documentation/documents.html',
#            'http://www.oikoumene.org/es/documentacion/documents.html',
    ]
    rules = (
        Rule(SgmlLinkExtractor(allow=(
            '^.*?/resources/documents/.*\.html',
#            '^.*?/dokumentation/documents/.*\.html',
#            '^.*?/documentation/documents/.*\.html',
#            '^.*?/documentacion/documents/.*\.html',
        ), deny=(
            '^.*?/documents/search-wcc-documents/.*',
#            '^.*?/documents/suche-in-oerk-dokumenten/.*',
#            '^.*?/documents/chercher-documents/.*',
#            '^.*?/documents/buscar-documentos-cmi/.*',
        ), process_value=clean_url), callback='parse_item', follow=True),
    )

