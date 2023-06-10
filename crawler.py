import feedparser
import requests
import time
import datetime
import tkinter as tk

import rssCrawl

'''
배포 url
'''
companies = {"https://fs.jtbc.co.kr/RSS/newsflash.xml": "jtbc", "https://fs.jtbc.co.kr/RSS/politics.xml": "jtbc",
             "https://fs.jtbc.co.kr/RSS/economy.xml": "jtbc", "https://fs.jtbc.co.kr/RSS/society.xml": "jtbc",
             "https://fs.jtbc.co.kr/RSS/international.xml": "jtbc", "https://fs.jtbc.co.kr/RSS/culture.xml": "jtbc",
             "https://fs.jtbc.co.kr/RSS/entertainment.xml": "jtbc", "https://fs.jtbc.co.kr/RSS/sports.xml" : "jtbc",
             "http://rss.kmib.co.kr/data/kmibRssAll.xml": "kukmin",
             "https://rss.hankyung.com/feed/economy.xml": "hankyung", "https://rss.hankyung.com/feed/it.xml": "hankyung",
             "https://rss.hankyung.com/feed/international.xml": "hankyung", "https://rss.hankyung.com/feed/life.xml": "hankyung",
             "https://rss.hankyung.com/feed/sports.xml": "hankyung", "https://rss.hankyung.com/feed/stock.xml": "hankyung",
             "https://rss.hankyung.com/feed/land.xml": "hankyung", "https://rss.hankyung.com/feed/politics.xml": "hankyung",
             "https://rss.hankyung.com/feed/society.xml": "hankyung", "https://rss.hankyung.com/feed/hei.xml": "hankyung",
             "https://www.mk.co.kr/rss/40300001/": "maeil",
             "https://news.sbs.co.kr/news/SectionRssFeed.do?sectionId=01&plink=RSSREADER": "sbs", "https://news.sbs.co.kr/news/SectionRssFeed.do?sectionId=02&plink=RSSREADER": "sbs",
             "https://news.sbs.co.kr/news/SectionRssFeed.do?sectionId=03&plink=RSSREADER": "sbs", "https://news.sbs.co.kr/news/SectionRssFeed.do?sectionId=07&plink=RSSREADER": "sbs",
             "https://news.sbs.co.kr/news/SectionRssFeed.do?sectionId=08&plink=RSSREADER": "sbs", "https://news.sbs.co.kr/news/SectionRssFeed.do?sectionId=14&plink=RSSREADER": "sbs",
             "https://news.sbs.co.kr/news/SectionRssFeed.do?sectionId=09&plink=RSSREADER": "sbs",
             "https://www.hani.co.kr/rss/": "hankyoreh",
             "https://www.khan.co.kr/rss/rssdata/total_news.xml": "kyunghyang",
             "https://rss.donga.com/total.xml": "donga",
             "https://rss.mt.co.kr/mt_news.xml": "moneytoday",
             "http://biz.heraldcorp.com/common/rss_xml.php?ct=0": "herald",
             "http://rss.edaily.co.kr/edaily_news.xml": "edaily",
             "https://www.fnnews.com/rss/r20/fn_realnews_all.xml": "financial",
             "https://www.mbn.co.kr/rss/": "mbn"}
'''
테스트 url
'''
# companies = {"https://rss.donga.com/total.xml": "donga"}

def start_crawl(root):
    start = time.time()
    count = 0

    articles = {}
    keywords = {}
    id = 0

    show_percent = "수집, 분석중  |"
    percent1 = tk.Label(root, text=show_percent)
    percent1.place(x=5, y=650)

    done_count = 0
    done_percent = '| ' + str(done_count / len(companies) * 100) + '%'
    percent2 = tk.Label(root, text=done_percent)
    percent2.place(x=570, y=650)
    percent2.update()

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

        # response 에서 인코딩 방식 추출
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
        get_articles, nums = rssCrawl.print_articles(entries, company, res.encoding)
        count += nums
        for title, link, date, tokens in get_articles:
            articles[id] = [title, link, company, date]

            for token in tokens:
                if keywords.get(token, -1) == -1:
                    keywords[token] = [id]
                else:
                    keywords[token].append(id)

            id += 1

        # 퍼센트 위젯 추가
        done_count += 1
        r_show = show_percent + '#' * round((done_count / len(companies)) * 60)
        percent1.config(text=r_show)
        percent1.update()

        done_percent = '| ' + str(round(done_count / len(companies) * 100, 1)) + '%'
        percent2.config(text=done_percent)
        percent2.update()
        print("-----------------------------------------------------------")


    print(count, "개 저장 완료")

    end = time.time()
    sec = end - start
    print('걸린 시간:   ', end='')
    print(datetime.timedelta(seconds=sec))

    return articles, keywords, count