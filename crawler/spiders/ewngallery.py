from scrapy.item import Item, Field
from scrapy.contrib.spiders.crawl import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from pyquery import PyQuery
import urllib
from base64 import b64encode

class GalleryItem(Item):
    title = Field()
    description = Field()
    bodytext = Field()
    images = Field()

class ImageItem(Item):
    caption = Field()
    image = Field()

class GalleryExtractorMixin(object):

    def parse_gallery(self, response):
        q = PyQuery(response.body)
        item = GalleryItem()
        item['title'] = q('.csc-header.csc-header-n1 b').text()
        item['bodytext'] = q('.csc-text').html()
        images = []
        q('.myGallery .imageElement').each(
            lambda x: self.parse_image(this, images)
        )

        q('.csc-textpic-image').each(
            lambda x: self.parse_textpic_image(this, images)
        )

        item['images'] = images
        return item

    def parse_image(self, imagenode, results):
        item = ImageItem()
        q = PyQuery(imagenode)
        item['caption'] = q('h3').text()
        image_url = q('img').attr('src')
        image_url = 'http://www.oikoumene.org/%s' % image_url
        item['image'] = b64encode(urllib.urlopen(image_url).read())
        results.append(item)

    def parse_textpic_image(self, imagenode, results):
        item = ImageItem()
        q = PyQuery(imagenode)
        item['caption'] = q('.csc-textpic-caption').text()
        image_wrapper_url = q('dt a').attr('href')
        qi = PyQuery(urllib.urlopen(
                'http://www.oikoumene.org/%s' % image_wrapper_url
        ).read())
        image_url = qi('img').attr('src')
        item['image'] = b64encode(urllib.urlopen(
            'http://www.oikoumene.org/%s' % image_url
        ).read())
        results.append(item)


class EWNEnglishGallerySpider(CrawlSpider, GalleryExtractorMixin):

    name = 'ewngallery-english'
    allowed_domains = ['www.oikoumene.org']
    start_urls = [
            'http://www.oikoumene.org/en/activities/ewn-home/resources-and-links/ewn-picture-gallery.html'
    ]
    rules = (
            Rule(SgmlLinkExtractor(allow='^.*?/activities/ewn-home/resources-and-links/ewn-picture-gallery/.*\.html'),
                callback='parse_gallery', follow=False),
    )
