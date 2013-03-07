from scrapy.item import Item, Field
from scrapy.contrib.spiders.crawl import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from pyquery import PyQuery
import urllib
from base64 import b64encode
import urlparse

class PageItem(Item):
    name = Field()
    title = Field()
    description = Field()
    bodytext = Field()
    image = Field()
    imageCaption = Field()
    effectiveDate = Field()
    orig_url = Field()
    lang_urls = Field()
    is_container = Field()

class PageItemExtractorMixin(object):

    def parse_page(self, response):
        if 'water.oikoumene.org' in response.url:
            return None
        if 'user-login.html' in response.url:
            return None
        if 'type=224' in response.url:
            return None

        q = PyQuery(response.body)
        if q('.yt_player').html():
            item = self._parse_page_lazyraw(response)
        elif q('.csc-header').text():
            item = self._parse_page_method1(response)
        elif q('.csc-textpic-text .csc-text').html():
            item = self._parse_page_method2(response)
        elif q('.csc-text .contenttable').html():
            item = self._parse_page_method3(response)
        else:
            item = self._parse_page_lazyraw(response)
#            raise Exception("No idea how to parse")

        item['orig_url'] = response.url
        item['lang_urls'] = {}

        def _extract_langurl(x):
            ql = PyQuery(this)
            lang = ql.attr('lang')
            item['lang_urls'][lang] = 'http://www.oikoumene.org/%s' % ql.attr('href')

        q('#languages a.lang').each(_extract_langurl)
        return item

    def _parse_page_lazyraw(self, response):
        q = PyQuery(response.body)
        item = PageItem()
        bodytext = q('#main-content')
        item['bodytext'] = bodytext.html()
        item['title'] = bodytext.find('h1').text()
        item['title'].strip() if item['title'] else None
        if not item['title']:
            item['title'] = bodytext.find('h2').text()
        return item


    def _parse_page_method1(self, response):
        q = PyQuery(response.body)
        item = PageItem()
        bodytext = q('.csc-text:first')
        item['title'] = q('.csc-header').text()
        image_url = bodytext.find('img:first').attr('src')
        if image_url:
            item['image'] = b64encode(urllib.urlopen(
                'http://www.oikoumene.org/%s' % image_url).read())
        bodytext.remove('img:first')
        bodytext.find("*[class]").each(lambda x: PyQuery(this).attr('class',''))
        try:
            item['bodytext'] = bodytext.html().replace(u'<p>\xa0</p>',u'')
        except:
            import pdb;pdb.set_trace()
        return item

    def _parse_page_method2(self, response):
        q = PyQuery(response.body)
        item = PageItem()

        bodytext = q('.csc-textpic-text .csc-text')
        headerblock = q('.csc-text:first')
        item['title'] = headerblock.find('h1').text()
        if not item['title']:
            item['title'] = headerblock.find('h2').text()

        image_url = q('.csc-textpic-image img').attr('src')
        if image_url:
            item['image'] = b64encode(urllib.urlopen(
                'http://www.oikoumene.org/%s' % image_url).read())
            item['imageCaption'] = q('.csc-textpic-caption').text()

        # cleanup html and set bodytext
        bodytext.find("*[class]").each(lambda x: PyQuery(this).attr('class',''))

        item['bodytext'] = bodytext.html().replace(u'<p>\xa0</p>',u'')

        subheader = headerblock.find('h3').text()

        if subheader:
            item['bodytext'] = subheader + item['bodytext']

        return item

    def _parse_page_method3(self, response):
        q = PyQuery(response.body)
        item = PageItem()

        bodytext = q('.csc-text')
        item['title'] = bodytext.find('h2.align-left').text()
        bodytext.remove('h2.align-left')
        bodytext.find("*[class]").each(lambda x: PyQuery(this).attr('class',''))
        try:
            item['bodytext'] = bodytext.html().replace(u'<p>\xa0</p>',u'')
        except:
            import pdb;pdb.set_trace()
        return item

class EWNEnglishPageSpider(CrawlSpider, PageItemExtractorMixin):

    name = 'ewnsevenweekwater-en'
    allowed_domains = ['www.oikoumene.org']
    start_urls = [
            'http://www.oikoumene.org/en/activities/ewn-home/resources-and-links/seven-weeks-for-water/about-this-campaign/previous-years.html'
    ]
    rules = (
        Rule(SgmlLinkExtractor(allow=(
            '^.*?/activities/ewn-home/resources-and-links/seven-weeks-for-water/about-this-campaign/previous-years/.*\.html',
        )), callback='parse_page', follow=True),
    )

class EWNDeutschPageSpider(CrawlSpider, PageItemExtractorMixin):

    name = 'ewnsevenweekwater-de'
    allowed_domains = ['www.oikoumene.org']

    start_urls = [
        'http://www.oikoumene.org/de/activities/oekumenisches-wassernetzwerk-oewn/ressourcen-und-links/sieben-wochen-fuer-wasser/ueber-die-kampagne/archiv.html'
    ]

    rules = (
        Rule(SgmlLinkExtractor(
            allow='^.*?/activities/oekumenisches-wassernetzwerk-oewn/ressourcen-und-links/sieben-wochen-fuer-wasser/ueber-die-kampagne/archiv/.*\.html'),
            callback='parse_page', follow=True),
    )

class EWNFrancaisPageSpider(CrawlSpider, PageItemExtractorMixin):
    name = 'ewnsevenweekwater-fr'
    allowed_domains = ['www.oikoumene.org']
    start_urls = [
        'http://www.oikoumene.org/fr/activities/roe/ressources-et-liens/sept-semaines-pour-leau/a-propos/archive.html'
    ]

    rules = (
        Rule(SgmlLinkExtractor(
            allow='^.*?/activities/roe/ressources-et-liens/sept-semaines-pour-leau/a-propos/archive/.*?\.html'),
            callback='parse_page', follow=True),
    )

class EWNEspanolPageSpider(CrawlSpider, PageItemExtractorMixin):
    name = 'ewnsevenweekwater-es'
    start_urls = [
        'http://www.oikoumene.org/es/activities/la-reda/recursos-y-enlaces/siete-semanas-para-el-agua/acerca-de-la-campana/archivo.html'
    ]

    rules = (
        Rule(SgmlLinkExtractor(
            allow='^.*?/activities/la-reda/recursos-y-enlaces/siete-semanas-para-el-agua/acerca-de-la-campana/archivo/.*\.html'),
            callback='parse_page', follow=True),
    )
