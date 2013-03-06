BUILDOUTROOT=`pwd`
SCRAPY=$BUILDOUTROOT/bin/scrapy
CRAWLERS="ewnnews-en ewnnews-de ewnnews-fr ewnnews-es"

for CRAWLER in $CRAWLERS;do
    cd $BUILDOUTROOT;
    rm -f $CRAWLER.json;
    echo "Crawling $CRAWLER"
    $SCRAPY crawl $CRAWLER -o $CRAWLER.json -t json
done
