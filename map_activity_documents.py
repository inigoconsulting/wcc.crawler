import json
import urlparse
import urllib

def clean_url(url):
    parsed = urlparse.urlparse(url)
    qs = parsed.query
    if not qs:
        return url
    qs = urlparse.parse_qs(qs)
    for v in ['print', 'tx_ttnews[cat]']:
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


class Processor(object):

    def __init__(self, activities):
        self._raw_activities = activities

    def run_mapper(self):
        result = {}
        for a in self._raw_activities:
            urls = a['related_document_urls']
            if a.get('document_folder_url', None):
                urls.append(a['document_folder_url'])

            for url in urls:
                url = 'http://www.oikoumene.org/' + url
                url = clean_url(url)
                if '#' in url:
                    url = url[:url.find('#')]
                result.setdefault(url, [])
                result[url].append(a['id_url'])

        return [{
            'orig_url': k,
            'related_activities': v
        } for k,v in result.items()]

proc = Processor(
    json.loads(open('wccactivity-de.json').read())
)

result = proc.run_mapper()
print json.dumps(result)
