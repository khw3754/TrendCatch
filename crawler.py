import feedparser
import requests
import time
import datetime


import rssCrawl

'''
배포 url
'''
# companies = {"https://fs.jtbc.co.kr/RSS/newsflash.xml": "jtbc", "https://fs.jtbc.co.kr/RSS/politics.xml": "jtbc",
#              "https://fs.jtbc.co.kr/RSS/economy.xml": "jtbc", "https://fs.jtbc.co.kr/RSS/society.xml": "jtbc",
#              "https://fs.jtbc.co.kr/RSS/international.xml": "jtbc", "https://fs.jtbc.co.kr/RSS/culture.xml": "jtbc",
#              "https://fs.jtbc.co.kr/RSS/entertainment.xml": "jtbc", "https://fs.jtbc.co.kr/RSS/sports.xml" : "jtbc",
#              "http://rss.kmib.co.kr/data/kmibRssAll.xml": "kukmin",
#              "https://rss.hankyung.com/feed/economy.xml": "hankyung", "https://rss.hankyung.com/feed/it.xml": "hankyung",
#              "https://rss.hankyung.com/feed/international.xml": "hankyung", "https://rss.hankyung.com/feed/life.xml": "hankyung",
#              "https://rss.hankyung.com/feed/sports.xml": "hankyung", "https://rss.hankyung.com/feed/stock.xml": "hankyung",
#              "https://rss.hankyung.com/feed/land.xml": "hankyung", "https://rss.hankyung.com/feed/politics.xml": "hankyung",
#              "https://rss.hankyung.com/feed/society.xml": "hankyung", "https://rss.hankyung.com/feed/hei.xml": "hankyung",
#              "https://www.mk.co.kr/rss/40300001/": "maeil",
#              "https://news.sbs.co.kr/news/SectionRssFeed.do?sectionId=01&plink=RSSREADER": "sbs", "https://news.sbs.co.kr/news/SectionRssFeed.do?sectionId=02&plink=RSSREADER": "sbs",
#              "https://news.sbs.co.kr/news/SectionRssFeed.do?sectionId=03&plink=RSSREADER": "sbs", "https://news.sbs.co.kr/news/SectionRssFeed.do?sectionId=07&plink=RSSREADER": "sbs",
#              "https://news.sbs.co.kr/news/SectionRssFeed.do?sectionId=08&plink=RSSREADER": "sbs", "https://news.sbs.co.kr/news/SectionRssFeed.do?sectionId=14&plink=RSSREADER": "sbs",
#              "https://news.sbs.co.kr/news/SectionRssFeed.do?sectionId=09&plink=RSSREADER": "sbs",
#              "https://www.hani.co.kr/rss/": "hankyoreh",
#              "https://www.khan.co.kr/rss/rssdata/total_news.xml": "kyunghyang",
#              "https://rss.donga.com/total.xml": "donga",
#              "https://rss.mt.co.kr/mt_news.xml": "moneytoday",
#              "http://biz.heraldcorp.com/common/rss_xml.php?ct=0": "herald",
#              "http://rss.edaily.co.kr/edaily_news.xml": "edaily",
#              "https://www.fnnews.com/rss/r20/fn_realnews_all.xml": "financial",
#              "https://www.mbn.co.kr/rss/": "mbn"}
'''
테스트 url
'''
companies = {"https://www.mk.co.kr/rss/40300001/": "maeil"}

def start_crawl():
    start = time.time()
    count = 0

    articles = {}
    keywords = {}
    id = 0

    for url, company in companies.items() :
        #먼저 받아옴
        for i in range(4):
            try:
                res = requests.get(url)
                res.raise_for_status()
            except:
                print(f"RSS 연결 실패. 재시도 중...{i+1}")
                time.sleep(3)
            else:
                # 연결 성공
                break
        else:
            print("RSS 연결 실패. 다음 언론사로 넘어감...")
            continue

        html = res.text

        #인코딩 방식 추출
        try:
            dd = html.index("encoding=")
            get_encoding = html[dd + 10:dd + 16]
            res.encoding = get_encoding             #인코딩 방식 지정 -- 안하면 깨지는 제목들 있음
        except:
            pass
        html = res.text

        d = feedparser.parse(html)

        entries = d.entries
        entry_count = len(entries)

        print(entry_count, company, res.encoding)


        ###### 출력 테스트 ######
        get_articles = rssCrawl.print_articles(entries, company, res.encoding)
        for title, link in get_articles:
            articles[id] = [title, link]
            id += 1


        ###### 저장 테스트 #####
        # count += rssCrawl.save_articles(entries, company, res.encoding)

        print("-----------------------------------------------------------")


    print(count, "개 저장 완료")

    end = time.time()
    sec = end - start
    print(datetime.timedelta(seconds=sec))

    now = time
    last = now.strftime('%Y%m%d%H%M%S')[2:]

    # return count, str(datetime.timedelta(seconds=sec)), last
    return articles