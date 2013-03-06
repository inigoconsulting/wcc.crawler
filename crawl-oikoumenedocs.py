import urllib2
import json
from datetime import datetime
from pyquery import PyQuery
from pprint import pprint


def _get_clean_node_html(node):
    node.find("*[class]").each(
        lambda x: PyQuery(this).attr('class','') if (
        PyQuery(this).attr('class')) else None)
    return node.html().replace(u'<p>\xa0</p>',u'')

def _find_raw_node_html(node):
    result = {'data': None}
    def func(x):
        if 'Raw HTML content' in PyQuery(this).html():
            result['data'] = PyQuery(this)
    node.each(func)
    return result['data']

class Scraper(object):

    postdata = {
        "action":"model_document",
        "method":"get",
        "data":[{
            "start":0,
            "limit":5000,
            "groupBy":"",
            "groupDir":"ASC",
            "grouping":"0",
            "field":"date",
            "direction":"DESC",
            "selNodes":"",
            "sort":"date",
            "dir":"DESC"
            }],
        "type":"rpc","tid":6
    }
    
    url = 'http://www.oikoumene.org/index.php?id=646&L=0&ext=32152&eID=docdb&router=1'

    def scrape(self):
        req = urllib2.Request(self.url, json.dumps(self.postdata),
                {'Content-Type':'application/json'})
        out = urllib2.urlopen(req).read()
        result = json.loads(out)
        self.result = result['result']['rows']

    def process(self):
        items = []
        skipped = []
        for row in self.result:
            if not (row['docPageURL'] or row['docPageURL'].strip()):
                skipped.append(row)
                continue
            print "Processing %s : %s" % (row['title'], row['docPageURL'])
            try: 
                item = self.parse(row)
            except urllib2.HTTPError:
                skipped.append(row)
                continue
            items.append(item) if item else None
        self.skipped = skipped
        return items

    def parse(self, data):
        entry = {}

        entry['title'] = data['title'].encode('utf-8')
        entry['related_descriptors'] = [
            d['title'].encode('utf-8') for d in data['dscr']
        ]
        entry['description'] = data['dAbs'].encode('utf-8')
        entry['owner'] = data['owner'].encode('utf-8')
        entry['document_type'] = data['type'].encode('utf-8')
        entrydate = datetime.fromtimestamp(int(data['date']))
        entry['date'] = entrydate.strftime('%Y-%m-%d %T')
        entry['orig_url'] = data['docPageURL']
        entry['status'] = data['status']
        related_links = []
        for page in data['pages']:
            related_links.append({
                'url': page['url'],
                'description': page['urltitle'].encode('utf-8'),
                'title': page['title'].encode('utf-8')
            })
        entry['related_links'] = related_links
        entry['is_container'] = False
        # extract body

        q = PyQuery(urllib2.urlopen(entry['orig_url']).read())
        bodytext = q('.csc-text')
        if q('.csc-sitemap').html():
            entry['is_container'] = True
        if bodytext.html():
            entry['bodytext'] = _get_clean_node_html(bodytext)
        if not bodytext.html() and not entry['is_container']:
            default = _find_raw_node_html(q('.csc-default'))
            if default:
                entry['bodytext'] = _get_clean_node_html(default)
        return entry

if __name__=='__main__':
    scraper = Scraper()
    scraper.scrape()
    result = scraper.process()
    jsonout = json.dumps(result)
    open('docs-en.json','w').write(jsonout)
    open('docs-en-skipped.json','w').write(scraper.skipped)
