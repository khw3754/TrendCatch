import tkinter as tk
import crawler
import webbrowser


articles = {}
keywords = {}
global_selected_keyword = ''

def crawl_and_analyze():
    global articles
    global keywords
    articles, keywords = crawler.start_crawl(root)

    # for id in articles.keys():
    #     title, link = articles[id]
    #     listBox.insert(tk.END, title)
    print(keywords)
    print(articles)
    sorted_keywords = dict(sorted(keywords.items(), key=lambda x: len(x[1]), reverse=True))

    i = 1
    for keyword in sorted_keywords.keys():
        keyword_listBox.insert(tk.END, str(i) + ".   " + keyword)
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
    search_result = keywords.get(target, -1)
    if search_result != -1:
        for id in search_result:
            title, link, company, date = articles[id]
            article_listBox.insert(tk.END, title)
        global_selected_keyword = target
    else:
        article_listBox.insert(tk.END, "관련 기사 없음")
        global_selected_keyword = ''


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




root = tk.Tk()
root.geometry("1000x680")
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


# 언론사, 기사 제목, 간략한 내용 몇 줄... , 날짜---- 있으면 좋을 듯?
# 웹에서 보기 버튼
# article에 제목, 링크는 있고 언론사, 날짜 추가하면 될 듯

# 언론사 표시
company_label = tk.Label(root, text="언론사    : ")
company_label.place(x=article_listBox.winfo_x() + article_listBox.winfo_width() + 30, y=article_listBox.winfo_y())
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


root.mainloop()

