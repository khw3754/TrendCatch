import tkinter as tk
import crawler


articles = {}
keywords = {}

def button_clicked():
    global articles
    global keywords
    articles, keywords = crawler.start_crawl()

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


def showList():
    global keywords
    global articles

    selected_index = keyword_listBox.curselection()
    selected_keyword = keyword_listBox.get(selected_index)

    selected_keyword = selected_keyword.split()[1]

    article_listBox.delete(0, tk.END)
    for id in keywords[selected_keyword]:
        title, link = articles[id]
        article_listBox.insert(tk.END, title)
    root.update()




root = tk.Tk()
root.geometry("1000x700")
root.title("Trend Catch")

crawl_button = tk.Button(root, text="기사 수집/분석", command=button_clicked)
crawl_button.place(x=1, y=1)
root.update()

show_list_button = tk.Button(root, text="관련 기사 보기", command=showList)
show_list_button.place(x=crawl_button.winfo_width() , y=1)

# keyword 라벨
keywords_label = tk.Label(root, text="keyword 순위")
keywords_label.place(x=5, y=30)
root.update()

keyword_listBox = tk.Listbox(root, height=35, width=15)
keyword_listBox.place(x=5, y=keywords_label.winfo_y() + keywords_label.winfo_height())
root.update()


article_listBox = tk.Listbox(root, height=35, width=45)
article_listBox.place(x=keyword_listBox.winfo_width()+10, y=keyword_listBox.winfo_y())
root.update()

article_label = tk.Label(root, text="기사 리스트")
article_label.place(x=article_listBox.winfo_x(), y=keywords_label.winfo_y())

root.mainloop()

