import urllib2
import json
from datetime import datetime
from pyquery import PyQuery
from pprint import pprint
import logging
import os
from base64 import b64encode

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

def _find_raw_node_html(node):
    result = {'data': None}
    def func(x):
        if 'Raw HTML content' in PyQuery(this).html():
            result['data'] = PyQuery(this)
    node.each(func)
    return result['data']

def _write(data):
    if not isinstance(data, str):
        result = json.dumps(data)
        if not os.path.exists('docs-en.json'):
            result = '[\n' + result
        else:
            result = ',\n' + result
    else:
        result = data
    open('docs-en.json','a').write(result)

def _download_file(url):
    name = os.path.basename(url)
    downurl = 'http://www.oikoumene.org/' + url
    print "Downloading file %s" % downurl
    data = urllib2.urlopen(downurl).read()
    return name, b64encode(data)

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
        print "Loading Data"
        out = urllib2.urlopen(req).read()
        result = json.loads(out)
        self.result = result['result']['rows']

    def process(self):
        items = []
        skipped = []
        for row in self.result:

            skipthis = False
            for p in ['en/resources/documents', 
                      'de/dokumentation/documents',
                      'fr/documentation/documents',
                      'es/documentacion/documents']:
                if p in row['docPageURL']:
                    break

                skipthis = True

            if skipthis:
                continue

            if not (row['docPageURL'] or row['docPageURL'].strip()):
                skipped.append(row)
                continue
            print "Processing %s : %s" % (row['title'], row['docPageURL'])
            try: 
                item = self.parse(row)
            except urllib2.HTTPError, urllib2.URLError:
                skipped.append(row)
                continue
#            items.append(item) if item else None
            _write(item)
        _write('\n]')
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
        entry['effectiveDate'] = entrydate.isoformat()
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

        q = None
        retrycount = 0

        if 'oikoumene.org' not in entry['orig_url']:
            # skip stuff not in oikoumene.org
            return None

        while not q and retrycount < 10:
            try:
                print "Fetching %s" % entry['orig_url']
                q = PyQuery(urllib2.urlopen(entry['orig_url']).read())
            except Exception, e:
                retrycount += 1
                if retrycount >= 10:
                    raise e
                print "Failed to load %s, retrying" % entry['orig_url']



        bodytext = q('.csc-text')

        entry['bodytext'] = ''
        if q('.csc-sitemap').html():
            entry['is_container'] = True
        if bodytext.html():
            entry['bodytext'] = _get_clean_node_html(bodytext)
        if not bodytext.html() and not entry['is_container']:
            default = _find_raw_node_html(q('.csc-default'))
            if default:
                entry['bodytext'] = _get_clean_node_html(default)

        entry['lang_urls'] = {}

        def _extract_langurl(x):
            ql = PyQuery(this)
            lang = ql.attr('lang')
            entry['lang_urls'][lang] = 'http://www.oikoumene.org/%s' % ql.attr('href')

        q('#languages a.lang').each(_extract_langurl)


        def _extract_id_url(x):
            url = PyQuery(this).attr('href')
            if 'id=' in url:
                entry['id_url'] = url

        q('#footer a').each(_extract_id_url)

        files = []

        def _extract_document(x):
            url = PyQuery(this).attr('href')
            if not url:
                return
            if '.pdf' in url:
                files.append(url)

        q('.csc-text a').each(_extract_document)

        if len(files) == 1:
            name, data = _download_file(files[0])
            entry['file'] = {
                'data': data,
                'name': name
            }
        else:
            entry['file'] = None
        return entry

if __name__=='__main__':
    if os.path.exists('docs-en.json'):
        os.unlink('docs-en.json')

    scraper = Scraper()
    scraper.scrape()
    result = scraper.process()
#    jsonout = json.dumps(result)
    open('docs-en-skipped.json','w').write(json.dumps(scraper.skipped))
