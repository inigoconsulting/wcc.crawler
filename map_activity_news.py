import json
import urlparse

class Processor(object):

    def __init__(self, activities, activitynews):
        self._raw_activities = activities
        self._raw_activitynews = activitynews
        self._by_category = {}
        for a in activities:
            qs = urlparse.parse_qs(
                urlparse.urlparse(a['news_category_url']).query
            )
            cat = qs['tx_ttnews[cat]'][0].split(
                ',')[0] if (
                qs.has_key('tx_ttnews[cat]') ) else None

            self._by_category[cat] = {
                'id_url': a['id_url'],
                'related_news': set(),
                'category_id': cat
            }

    def run_mapper(self):
        result = {}
        for news in self._raw_activitynews:
            default = {
                'id_url': news['id_url'],
                'categories': []
            }

            result.setdefault(news['id_url'], default)
            entry = result[news['id_url']]
            for c in news['category_ids'] or []:
                if not self._by_category.has_key(c):
                    continue
                if self._by_category[c]['id_url'] in entry['categories']:
                    continue
                entry['categories'].append(self._by_category[c]['id_url'])
        return result
proc = Processor(
    json.loads(open('wccactivity-en.json').read()), 
    json.loads(open('wccactivityrelatednews-en.json').read())
)

result = proc.run_mapper().values()
print json.dumps(result)
