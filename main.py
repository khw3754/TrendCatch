import tkinter as tk
import crawler
import webbrowser
import smtplib
from email.mime.text import MIMEText


articles = {}
keywords = {}
global_selected_keyword = ''

def crawl_and_analyze():
    global articles
    global keywords
    articles, keywords, count = crawler.start_crawl(root)

    # 분석 완료 기사 개수 표시
    article_count_label = tk.Label(root, text=f"기사 {count}개 분석 완료")
    article_count_label.place(x=700, y=650)

    keywords = dict(sorted(keywords.items(), key=lambda x: len(x[1]), reverse=True))

    i = 1
    for keyword in keywords.keys():
        keyword_listBox.insert(tk.END, str(i) + ".  " + keyword)
        i += 1
    root.update()


def showList(event = None):
    global keywords
    global articles
    global global_selected_keyword

    selected_index = keyword_listBox.curselection()
    if selected_index:
        selected_keyword = keyword_listBox.get(selected_index)

        selected_keyword = selected_keyword.split()[1]
        global_selected_keyword = selected_keyword

        article_listBox.delete(0, tk.END)
        for id in keywords[selected_keyword]:
            title, link, company, date = articles[id]
            article_listBox.insert(tk.END, title)
        root.update()

def search(event = None):
    global global_selected_keyword
    article_listBox.delete(0, tk.END)

    target = search_entry.get()
    # 검색 기록 추가
    all_history = search_history.get(0, tk.END)
    if target != '' and target not in all_history:
        search_history.insert(tk.END, target)

    search_result = keywords.get(target, -1)
    if search_result != -1:
        for id in search_result:
            title, link, company, date = articles[id]
            article_listBox.insert(tk.END, title)
        global_selected_keyword = target
    else:
        article_listBox.insert(tk.END, "관련 기사 없음")
        global_selected_keyword = ''

# 검색 기록에 있는 단어 재검색
def history_research(event = None):
    history_idx = search_history.curselection()
    if history_idx:
        search_entry.delete(0, tk.END)
        search_entry.insert(0, search_history.get(history_idx[0]))
        search()



# 모든 text 블록의 텍스트를 지우는 함수
def all_delete():
    link_text.config(state='normal')
    company_text.config(state='normal')
    title_text.config(state='normal')
    date_text.config(state='normal')

    company_text.delete('1.0', tk.END)
    title_text.delete('1.0', tk.END)
    date_text.delete('1.0', tk.END)
    link_text.delete('1.0', tk.END)

# 모든 text 블록을 disabled 상태로 만드는 함수
# - 사용자가 입력할 수 없도록 함
def all_disabled():
    link_text.config(state='disabled')
    company_text.config(state='disabled')
    title_text.config(state='disabled')
    date_text.config(state='disabled')

def show_article_info(event = None):
    all_delete()

    index = article_listBox.curselection()

    if global_selected_keyword and index:
        article_id = keywords[global_selected_keyword][index[0]]
        title, link, company, date = articles[article_id]
        company_text.insert(tk.END, company)
        title_text.insert(tk.END, title)
        link_text.insert(tk.END, link)

        date = '20' + date
        date = date[:4] + '년 ' + date[4:6] + '월 ' + date[6:8] + '일    ' + date[8:10] + '시 ' + date[10:12] + '분'
        date_text.insert(tk.END, date)
        root.update()

    all_disabled()


def open_browser():
    link = link_text.get('1.0', tk.END)
    if link:
        webbrowser.open_new_tab(link[:-1])

'''
email로 상위 10개 키워드 기사 5개씩 전송해주는 함수
'''
def send_email():
    sendAddress = "trendcatch1@naver.com"
    recvAddress = mail_address.get('1.0', tk.END)

    pw = "trendcatch123!"

    smtpName = "smtp.naver.com"
    smtpPort = 587

    # 메일 구성
    mail_text = 'Trend Catch\n오늘의 Top 10 키워드를 보내드립니다.\n\n'
    if keywords:
        for i, key in enumerate(list(keywords.keys())[:10]):
            ids = keywords[key]
            mail_text += f'Top {i+1} : {key}\n'
            for id in ids[:5]:
                title, link, company, date = articles[id]
                mail_text += f'     {title}   - {company}       링크: {link}\n'

            mail_text += '\n'
    else:
        mail_state_label.config(text="기사 수집/분석을 완료하여 주세요.")
        mail_state_label.place(x=mail_address.winfo_x(), y=mail_address.winfo_y() + 25)
        return


    # 메일 전송
    try:
        msg = MIMEText(mail_text)
        msg['Subject'] = "Trend Catch 오늘의 기사 전송"
        msg['From'] = sendAddress
        msg['To'] = recvAddress

        s = smtplib.SMTP(smtpName, smtpPort)    # 메일 서버 연결
        s.starttls()    # TLS 보안처리
        s.login(sendAddress, pw)    # 로그인
        s.sendmail(sendAddress, recvAddress, msg.as_string())
        s.close()

        state = '메일 전송에 성공하였습니다.'
    except:
        state = '메일 전송에 실패하였습니다.'

    mail_state_label.config(text=state)
    mail_state_label.place(x=mail_address.winfo_x(), y=mail_address.winfo_y() + 25)




root = tk.Tk()
root.geometry("970x680")
root.title("Trend Catch")

crawl_button = tk.Button(root, text="기사 수집/분석", command=crawl_and_analyze)
crawl_button.place(x=1, y=1)
root.update()

show_list_button = tk.Button(root, text="관련 기사 보기", command=showList)
show_list_button.place(x=crawl_button.winfo_width() + 30, y=1)
show_list_button.update()

show_article_info_button = tk.Button(root, text="기사 정보 보기", command=show_article_info)
show_article_info_button.place(x=show_list_button.winfo_x() + show_list_button.winfo_width(), y=1)

# keyword 라벨
keywords_label = tk.Label(root, text="keyword 순위")
keywords_label.place(x=5, y=30)
root.update()

keyword_listBox = tk.Listbox(root, height=35, width=15)
keyword_listBox.bind("<Double-Button-1>", showList)
keyword_listBox.place(x=5, y=keywords_label.winfo_y() + keywords_label.winfo_height())
root.update()


article_listBox = tk.Listbox(root, height=35, width=45)
article_listBox.place(x=keyword_listBox.winfo_width()+10, y=keyword_listBox.winfo_y())
article_listBox.bind("<Double-Button-1>", show_article_info)
root.update()

article_label = tk.Label(root, text="기사 리스트")
article_label.place(x=article_listBox.winfo_x(), y=keywords_label.winfo_y())

# 검색 창, 버튼
search_entry = tk.Entry(root, width=10)
search_entry.place(x=show_article_info_button.winfo_x() + show_article_info_button.winfo_width() + 30, y=3)
search_entry.bind("<Return>", search)
search_entry.update()

search_button = tk.Button(root, text="검색", command=search)
search_button.place(x=search_entry.winfo_x() + search_entry.winfo_width() + 5, y=1)



'''
오른쪽 구간
'''

# 검색 기록
search_history_label = tk.Label(root, text="검색 기록")
search_history_label.place(x=article_listBox.winfo_x() + article_listBox.winfo_width() + 30, y=article_listBox.winfo_y())
search_history_label.update()

search_history = tk.Listbox(root, width=25, height=10)
search_history.bind("<Double-Button-1>", history_research)
search_history.place(x=search_history_label.winfo_x() + search_history_label.winfo_width() + 5, y=search_history_label.winfo_y())
search_history.update()


# 언론사 표시
company_label = tk.Label(root, text="언론사    : ")
company_label.place(x=search_history_label.winfo_x(), y=search_history.winfo_y() + search_history.winfo_height() + 50)
company_label.update()

company_text = tk.Text(root, width=20, height=1, state='disabled')
company_text.insert(tk.END, "")
company_text.place(x=company_label.winfo_x() + company_label.winfo_width() + 5, y=company_label.winfo_y() + 2)
company_text.update()

# 제목 표시
title_label = tk.Label(root, text="제목       : ")
title_label.place(x=company_label.winfo_x(), y=company_label.winfo_y() + 30)
title_label.update()

title_text = tk.Text(root, width=40, height=2, state='disabled')
title_text.insert(tk.END, "")
title_text.place(x=company_text.winfo_x(), y=company_text.winfo_y() + 30)
title_text.update()

# 날짜 표시
date_label = tk.Label(root, text="날짜       : ")
date_label.place(x=title_label.winfo_x(), y=title_label.winfo_y() + 40)
date_label.update()

date_text = tk.Text(root, width=40, height=1, state='disabled')
date_text.insert(tk.END, "")
date_text.place(x=title_text.winfo_x(), y=title_text.winfo_y() + 40)
date_text.update()

# 링크 표시
link_label = tk.Label(root, text="링크       : ")
link_label.place(x=date_label.winfo_x(), y=date_label.winfo_y() + 30)
link_label.update()

link_text = tk.Text(root, width=40, height=5, state='disabled')
link_text.insert(tk.END, "")
link_text.place(x=date_text.winfo_x(), y=date_text.winfo_y() + 30)
link_text.update()


# 브라우저 연결 버튼
open_button = tk.Button(root, text="기사 열기", command=open_browser, width=10, height=3)
open_button.place(x=link_text.winfo_x(), y=link_text.winfo_y() + 100)
open_button.update()

# 메일 보내기 기능
mail_button = tk.Button(root, text="주요 기사\n Email로 받기", command=send_email, width=10, height=3)
mail_button.place(x=open_button.winfo_x() + open_button.winfo_width() + 10, y=open_button.winfo_y())

mail_address = tk.Text(root, width=40, height=1, state='normal')
mail_address.place(x=open_button.winfo_x(), y=open_button.winfo_y() + open_button.winfo_height() + 10)
mail_address.update()

mail_label = tk.Label(root, text="Email 주소 :")
mail_label.place(x=link_label.winfo_x() - 10, y=mail_address.winfo_y()-2)

mail_state_label = tk.Label(root, text="")


root.mainloop()

