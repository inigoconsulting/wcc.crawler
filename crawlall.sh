BUILDOUTROOT=`pwd`
SCRAPY=$BUILDOUTROOT/bin/scrapy
#MODULES="ewnnewsletter ewnsevenweekwater ewngallery ewnnews"
#MODULES='piefnewsletter piefalerts'
#MODULES="wccfeaturenews"
LANGS="en de fr es"
MODULES="wccactivity"
CRAWLERS=""
for MOD in $MODULES;do
    for LANG in $LANGS;do
        CRAWLERS="$CRAWLERS $MOD-$LANG"
    done;
done;


for CRAWLER in $CRAWLERS;do
    cd $BUILDOUTROOT;
    rm -f $CRAWLER.json;
    echo "Crawling $CRAWLER"
    $SCRAPY crawl $CRAWLER -o $CRAWLER.json -t json $@
done
