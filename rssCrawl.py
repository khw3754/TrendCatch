from bs4 import BeautifulSoup
import requests
from datetime import datetime
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

def find_img(soup, company, link):
    if company == "hankyung":
        return soup.find("article").find("img")["src"]
    elif company == "financial":
        return soup.find("span", attrs={"class":"art_img"}).find("img")["src"]
    elif company == "jtbc":
        return None
    elif company == "hankyung":
        return soup.find("div", attrs={"class":"figure-img"})
    elif company == "maeil":
        return soup.find("div", attrs={"class":"thumb"}).find("img")["data-src"]
    elif company == "kyunghyang":
        return soup.find("picture").find("img")["src"]
    elif company == "herald":
        return soup.find("div", attrs={"id":"articleText"}).find("img")["src"]
    elif company == "edaily":
        return soup.find("div", attrs={"itemprop":"articleBody"}).find("img")["src"]
    elif company == "mbn":
        return "https:" + soup.find("div", attrs={"itemprop":"articleBody"}).find("img")["data-src"]


def print_articles(entries, company, get_encoding):
    # [기사 제목, 링크, [키워드]] 가 들어감
    result = []

    entries = entries[::-1]
    for entry in entries:
        title = entry["title"]
        link = entry["link"]
        try:
            date = entry["published"]
            date = date_format(date, company)
        except:
            date = "date없음"

        # RSS에 이미지 url 있는 언론사들 (국민, 머니투데이, sbs, 동아)
        try:
            if company == "kukmin" or company == "moneytoday":
                img = entry["description"].split('src="')[1].split('"')[0]
            elif company == "sbs":
                img = entry["links"][1]["href"]
            elif company == "donga":
                img = entry["summary"].split('src="')[1].split('"')[0]
            elif company == "hankyoreh":
                img = entry["description"].split('src="')[1].split('"')[0]
            else:
                img = None
        except:
            img = "이미지 없음"

        print(title)
        print(link)
        print(img)


        request_headers = {
            'User-Agent': ('Mozilla/5.0 (Windows NT 10.0;Win64; x64)\
                    AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98\
                    Safari/537.36'), }
        article_res = requests.get(link, headers=request_headers)
        article_res.encoding = get_encoding
        soup = BeautifulSoup(article_res.text, "html.parser")

        if not img:
            try:
                img = find_img(soup, company, link)
            except:
                img = "이미지 없음"
            print(img)

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

        print(date)
        # tokens = analyzer.extract_keyword(title, content.text)
        try:
            # print(content.getText().strip())
            tokens = analyzer.extract_keyword(title, content.text)
            print(tokens)
        except:
            print(title + "     분석 오류 남     " + link)
            continue

        result.append([title, link, tokens])
        print()

    return result


def save_articles(entries, company, get_encoding):
    # 경로 조정 필요
    file_path = "/Users/hyung/articles/" + company + "/"
    count = 0
    for entry in entries:
        # id 생성
        now = datetime.now()
        id = now.strftime('%Y%m%d%H%M%S')
        id += str(now.microsecond)

        title = entry["title"]
        link = entry["link"]
        try:
            date = entry["published"]
            date = date_format(date, company)
        except:
            date = "date없음"

        # RSS에 이미지 url 있는 언론사들 (국민, 머니투데이, sbs, 동아)
        try:
            if company == "kukmin" or company == "moneytoday":
                img = entry["description"].split('src="')[1].split('"')[0]
            elif company == "sbs":
                img = entry["links"][1]["href"]
            elif company == "donga":
                img = entry["summary"].split('src="')[1].split('"')[0]
            elif company == "hankyoreh":
                img = entry["description"].split('src="')[1].split('"')[0]
            else:
                img = None
        except:
            img = None


        try:
            f = open(file_path+company+'-'+id, 'w', encoding=get_encoding)
        except:
            print(file_path+company+'-'+id + "       제목: " + title + "    file open 오류발생")
            continue

        request_headers = {
            'User-Agent': ('Mozilla/5.0 (Windows NT 10.0;Win64; x64)\
                            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98\
                            Safari/537.36'), }
        try:
            article_res = requests.get(link, headers=request_headers)
            article_res.encoding = get_encoding
            soup = BeautifulSoup(article_res.text, "html.parser")
        except:
            print(title + "      requests.get() 오류발생")
            continue

        if not img:
            try:
                img = find_img(soup, company, link)
            except:
                img = None


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

        try:
            f.write(title + '\n' + content.getText().strip())
            f.close()
            count += 1
        except:
            print(title + "      저장 오류       " + link)

    return count