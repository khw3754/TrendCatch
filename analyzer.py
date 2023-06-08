"""
기사의 키워드를 추출하는 모듈.
"""
import sys
import re
import time
import math
import datetime

KEYWORD = dict()
ARTICLES = dict()   # {id: Article}
TOKENS = []
KEYWORD_MAP = []    # [keyword, freq, [article id 리스트]]
TITLE = ''

def init_golbal_vals():
    global KEYWORD
    global ARTICLES
    global TOKENS
    global KEYWORD_MAP
    global TITLE

    KEYWORD = dict()
    ARTICLES = dict()  # {id: Article}
    TOKENS = []  # {id: [tokens]}
    KEYWORD_MAP = []
    TITLE = ''

last_analyze = 0


def refine(content):
    '''
    의미 없는 기호(탈출문자, 구두점 등)를 제거한다.
    '''
    # 줄바꿈, 괄호 공백으로 변환
    content = re.sub('[\t\n()=.<>◇\[\]"“‘”’·■○▲△▷▶\-,\']', ' ', content)
    # 대괄호, 큰따옴표, 작은따옴표 제거
    # content = re.sub('[\[\]"“‘”’·○▲△▷,\']', '', content)
    return content


def get_n_grams(content, n):
    '''
    전달받은 문자열의 n-gram을 배열 형태로 반환한다.
    '''
    content = refine(content)
    content = content.split(' ')
    output = []
    for i in range(len(content)-n+1):
        output.append(content[i:i+n])
    return output


def tokenize(content):
    '''
    기사의 본문(content)를 토큰화하여 반환한다.
    '''
    postposition = set(['에', '을', '를', '은', '는', '이', '가', '게', '의', '와', '에서', '이라고'])
    tokens = refine(content)
    result = []
    for word in tokens.split(' '):
        if len(word) > 0:
            # 명사에 붙는 조사 제거
            if len(word) > 1 and word[-1] in postposition:
                result.append(word[:-1].lower())
            else:
                result.append(word.lower())
    return result


def get_n_tokens(tokens, n):
    '''
    길이가 n인 토큰들로 이루어진 리스트를 반환한다.
    '''
    result = [token for token in tokens if len(token) == n]
    return result


def get_filtered_tf(n_min, n_max):
    '''
    TOKENS에 저장된 토큰들 중 길이가 n_mix 이상, n_max 미만인 것만 남긴다.
    n_min - 토큰 길이 최솟값
    n_max - 토큰 길이의 상한값 (excluded)
    '''
    global TOKENS
    global ARTICLES
    invalid_ids = []
    # for tokens in TOKENS:
    #     # fij 계산
    #     # {token: 빈도수}
    #     freq = dict()
    #     for token in tokens:
    #         if n_min <= len(token) < n_max:
    #             if token not in freq:
    #                 freq[token] = 1
    #             else:
    #                 freq[token] += 1
    #     # if len(freq) == 0:
    #         # n_min, n_max 사이 크기의 토큰이 없는 경우
    #         # invalid_ids.append(art_id)
    #         # print(f'discard \033[31m{art_id}\033[0m')
    #     TOKENS = freq

    freq = dict()
    for token in TOKENS:
        if n_min <= len(token) < n_max:
            if token not in freq:
                freq[token] = 1
            else:
                freq[token] += 1
    TOKENS = freq

# n_min 미만, n_max 이상인 토큰으로만 구성된 기사 제거
    for i in invalid_ids:
        del ARTICLES[i]
        del TOKENS[i]


def is_reducable(term1, term2):
    '''
    두 단어가 적당히 비슷한지 판단한다.
    '''
    s_term = term1 if len(term1) < len(term2) else term2
    l_term = term2 if len(term1) < len(term2) else term1
    common_part_length = 0
    i = 0
    while i < len(s_term) and s_term[i] == l_term[i]:
        common_part_length += 1
        i+=1
    if common_part_length > 1 and common_part_length >= len(s_term)/3:
        return True
    else:
        return False


def get_common_str(term1, term2):
    '''
    두 단어에서 공통된 부분을 반환한다.
    '''
    s_term = term1 if len(term1) < len(term2) else term2
    l_term = term2 if len(term1) < len(term2) else term1
    common_str = ''
    i = 0
    while i < len(s_term) and s_term[i] == l_term[i]:
        common_str += s_term[i]
        i+=1
    return common_str


def reduce(term_frequencies):
    '''
    하나의 문서에서 적당히 비슷한 토큰을 하나로 합친다.
    term_frequencies - 하나의 문서에 대한 term_frequencies 딕셔너리(stage2의 결과)
    {term: f, term: f, ...} 형태
    '''
    result = {}
    reduced_keys = set()
    terms = list(term_frequencies.keys())
    for i, term in enumerate(terms):
        if term not in reduced_keys:
            for other in terms[i+1:]:
                if is_reducable(term, other):
                    new_key = get_common_str(term, other)
                    if new_key in result:
                        result[new_key] += 1
                    else:
                        result[new_key] = term_frequencies[term] + term_frequencies[other]
                    reduced_keys.add(term)
                    reduced_keys.add(other)
    # 합쳐지지 않은 토큰들을 보존한다.
    for term in terms:
        if term not in reduced_keys:
            result[term] = term_frequencies[term]
    return result


def normalize_frequency(tokens):
    '''
    토큰의 빈도를 최대값으로 나눈다.
    tokens - {term: freq} 딕셔너리(기사 한 개)
    '''
    max_freq = max(tokens.values())
    for t, f in tokens.items():
        # 제목에 등장한 키워드 가중치
        if t in TITLE:
            tokens[t] = round(f/max_freq*(1.2), 2)
        else:
            tokens[t] = round(f/max_freq, 2)



def get_df(documents):
    '''
    모든 토큰의 DF값을 구하여 반환한다.
    핫 키워드를 찾는데 사용한다.
    '''
    result = []
    N = len(documents)  # 문서 개수
    for document in documents:
        df = dict()
        for term in document.keys():
            n = 0
            for doc in documents:
                if term in doc:
                    n += 1
            df[term] = 1/math.log2(N/n)
        result.append(df)
    return result


def tf_idf_score(tf, idf):
    '''
    각 토큰의 TF.IDF 점수를 반환한다.
    '''
    result = list()
    if len(tf) != len(idf):
        print('[ERROR] tf_idf_score')
        exit()
    for i in range(len(tf)):
        scores = dict()
        for term in tf[i].keys():
            scores[term] = tf[i][term] * idf[i][term]
        result.append(scores)
    return result


def print_stage_info(stage):
    stage_name = 'unnamed'
    if stage == 1:
        stage_name = 'tokenize&map'
    elif stage == 2:
        stage_name = 'filter'
    elif stage == 3:
        stage_name = 'reduce'
    elif stage == 4:
        stage_name = 'normalization'
    elif stage == 5:
        stage_name = 'IDF'
    elif stage == 6:
        stage_name = 'prunning'
    print('[stage%d] %15s is done.' % (stage, stage_name))


def extract_keyword(title, content):
    """
    메모리에 로드된 기사들에서 키워드를 추출한다.
    """
    init_golbal_vals()

    global TOKENS
    global TITLE
    print(f'[{datetime.datetime.now()}]')
    # count_article = 0
    start_time = time.time()        # [dev]
    ''' 
    stage 1 - 모든 기사를 토큰화한다.
    documents_tokens - 각 원소가 토큰화된 기사인 리스트 
    (리스트의 크기가 기사의 개수와 일치)
    TOKENS = [token]
    '''
    if len(content) == 0:
        return []
    TOKENS = tokenize(content)
    TITLE = title
    '''
    stage 2 - filter
    크기가 3~10인 토큰만 남긴다. 
    기사의 모든 토큰이 3보다 작은 경우가 있음에 주의.
    '''

    get_filtered_tf(3, 11)
    # print_stage_info(2)
    '''
    stage 3 - reduce
    적당히 비슷한 토큰을 합친다.
    TOKENS = {token: 빈도수}
    '''
    TOKENS = reduce(reduce(TOKENS))
    # print_stage_info(3)
    '''
    stage 4 - normalize
    모든 토큰의 TF값 계산
    '''
    normalize_frequency(TOKENS)
    # print_stage_info(4)
    '''
    stage 5 - 점수가 높은 토큰만 남긴다.
    TOKENS = {token: score}
    '''

    # 점수가 기준 이상인 토큰
    useful = []
    for t, f in TOKENS.items():
        if f > 0.3:
            useful.append(t)
    TOKENS = useful
    end_time = time.time()          # [dev]
    '''
    for i, tokens in TOKENS.items():
        print(f'{ARTICLES[i].title}')
        for t, f in tokens.items():
            print(f'{t}: {f}')
    '''

    print("elapsed time: %0.2f" % (end_time - start_time))
    print('---------------------------------------------')
    sys.stdout.flush()

    return TOKENS


# def collect_keyword(db, Keywords):
#     """
#     분석된 모든 기사를 키워드로 묶는다.
#     KEYWORD_MAP = [키워드, freq, [Article 리스트]]
#     TOKENS = {id: {token: score}}
#     total_tokens = {token: [count, [art_id]]}
#     """
#     global last_analyze
#     print(f'before collect_keyword(): last_analyze = {last_analyze}')
#     C, IDs = 0, 1
#     last_analyze_id = 0
#     start = time.time()
#     total_tokens = dict()
#     for art_id, tokens in TOKENS.items():
#         for t, score in tokens.items():
#             if t in total_tokens:
#                 total_tokens[t][C] += 1
#                 total_tokens[t][IDs].append(str(art_id))
#             else:
#                 total_tokens[t] = [1, [str(art_id)]]
#         if art_id > last_analyze_id:
#             last_analyze_id = art_id
#     # 결과 저장
#     data = [Keywords(k, info[C], ' '.join(info[IDs])) for k, info in total_tokens.items()]
#     try:
#         from kk_editor import app
#         with app.app_context():
#             for d in data:
#                 saved_keyword = Keywords.query.filter(Keywords.keyword == d.keyword).first()
#                 if saved_keyword:
#                     # 중복 제거
#                     saved_keyword.articles += ' ' + d.articles
#                     article_list = list(saved_keyword.articles.split(' '))
#                     article_set = set(article_list)
#                     saved_keyword.rank += len(article_list) - len(article_set)
#                     saved_keyword.articles = ' '.join(list(article_set))
#                     db.session.commit()
#                 else:
#                     db.session.add(d)
#                     db.session.commit()
#     except Exception as e:
#         print(f'[EROR] [collect_keyword]: {e}')
#     end = time.time()
#     print(f'[collect_keyword] elapsed time: {round(end-start, 3)}s')
#
#     # 분석 완료한 마지막 기사 id 저장
#     last_analyze = last_analyze_id
#     print(f'after collect_keyword(): last_analyze = {last_analyze}')


def recommend_by_keyword(keyword, Keywords, Article):
    data = Keywords.query.filter(Keywords.keyword==keyword).one()
    print(f'[{datetime.datetime.now()}][API 호출]recommend for {keyword}')
    print(f'rank: {data.rank} article_id: {data.articles}')
    art_ids = list(map(int, data.articles.split(' ')))
    # fetch articles from DB
    articles = []
    for i in art_ids:
        articles.append(Article.query.filter(Article.id==i).one())
    # 클라이언트에게 반환할 객체 생성
    result = []
    for article in articles:
        tmp = {'title': article.title, 'link': article.link, 'image': article.image, 'press': article.company, 'content': article.content}
        result.append(tmp)
    sys.stdout.flush()
    return result
