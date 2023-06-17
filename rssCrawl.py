from bs4 import BeautifulSoup
import requests
import analyzer




'''
문자열 date를 받아서 DB에 저장할 문자열 형식으로 바꿔주는 함수
ex) “2023.04.05 오후 1시2분3초”  →  230405130203
각 언론사 별로 처리
'''
def date_format(date, company):
    mon = {'Jan':'01', 'Feb':'02', 'Mar':'03', 'Apr':'04', 'May':'05', 'Jun':'06', 'Jul':'07', 'Aug':'08',\
           'Sep':'09', 'Oct':'10', 'Nov':'11', 'Dec':'12'}
    if company == 'jtbc':
        date = list(date.split())[1:]
        yymmdd = ''.join(date[0].split('-'))[2:]
        clock = ''.join(date[1].split(':')) + '00'
        return yymmdd + clock

    elif company == "kukmin":
        date = list(date.split())
        yymmdd = ''.join(date[-2].split('-'))[2:]
        clock = ''.join(date[-1].split(':')) + '00'
        return yymmdd + clock

    elif company == 'kyunghyang':
        date = list(date.split())[2:]
        yymmdd = ''.join(date[0].split('.'))[2:]
        clock = ''.join(date[1].split(':')) + '00'
        return yymmdd + clock

    elif company == 'moneytoday':
        return date[2:14]

    '''
    나머지 언론사들 공통화 시킴
    '''
    if company == 'financial':
        date = date[4:]

    date = list(date.split())
    if not (company == 'kukmin' or company == 'financial'):
        date = date[1:]

    day = date[0] if len(date[0]) == 2 else '0' + date[0]
    month = mon.get(date[1])
    year = date[2][2:4]
    clock = ''.join(date[3].split(':'))

    return year + month + day + clock


'''
기사들을 각각 크롤링하는 함수
'''
def print_articles(entries, company, get_encoding):
    # [기사 제목, 링크, 날짜, [키워드]] 가 들어감
    result = []
    count = 0

    # 기사 엔트리 = 기사 리스트
    entries = entries[::-1]
    for entry in entries:
        title = entry["title"]
        link = entry["link"]
        try:
            date = entry["published"]
            date = date_format(date, company)
        except:
            date = "date없음"

        # 헤더를 변경해야 본문을 보내주는 언론사 있음
        request_headers = {
            'User-Agent': ('Mozilla/5.0 (Windows NT 10.0;Win64; x64)\
                    AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98\
                    Safari/537.36'), }
        try:
            article_res = requests.get(link, headers=request_headers)
        except:
            continue

        article_res.encoding = get_encoding
        soup = BeautifulSoup(article_res.text, "html.parser")

        # 혹시 모를 예외처리
        try:
            #### jtbc 본문 ####
            if company == "jtbc" :
                '''
                날짜를 받아옴 (수정있을 시 수정날짜로 받아옴)
                '''
                date = soup.find("span", attrs={"class": "artical_date"})
                date = date.findAll("span")[-1]
                date = date_format(date.text, company)

                content = soup.find("div", attrs={"class": "article_content"})

            #### 국민일보, 매일경제, 머니투데이, 헤럴드경제, 이데일리, mbn, 동아일보 본문 ####
            elif company in ["kukmin", "maeil", "moneytoday", "herald", "edaily", "mbn", "donga"] :
                content = soup.find("div", attrs={"itemprop": "articleBody"})

                if company == "kukmin":
                    date = soup.findAll("div", attrs={"class":"date"})[-1]
                    date = date_format(date.text, company)

                if company == "donga":
                    # 동아일보 본문만 남기고 좋아요 구독 같은 거 없애줌
                    content.find(attrs={"class": "article_footer"}).decompose()

            #### 한국경제, 경향신문 본문 ####
            elif company == "hankyung" or company == "kyunghyang":
                '''날짜 처리'''
                if company == "kyunghyang":
                    date = soup.find("div", attrs={"class": "byline"})
                    date = date.findAll("em")[-1]
                    date = date_format(date.text, company)

                content = soup.find("div", attrs={"itemprop": "articleBody"})

            #### sbs 본문 ####
            elif company == "sbs":
                content = soup.find("div", attrs={"class": "article_cont_area"})

            #### 한겨래 본문 ####
            elif company == "hankyoreh":
                content = soup.find("div", attrs={"class": "text"})

            #### 파이낸셜 본문 ####
            elif company == "financial":
                content = soup.find("div", attrs={"id": "article_content"})
                if content == None:
                    content = soup.find("div", attrs={"itemprop": "articleBody"})
        except:
            continue

        # 본문은 analyzer에서 분석
        try:
            tokens = analyzer.extract_keyword(title, content.text)
            count += 1
        except:
            print(title + "     분석 오류 남     " + link)
            continue

        # [제목, 링크, 날짜, [키워드]] 형태로 리스트에 넣음
        result.append([title, link, date, tokens])

    # result와 기사 개수 반환
    return result, count