import tkinter as tk
import crawler

def button_clicked():
    articles = crawler.start_crawl()

    for id in articles.keys():
        title, link = articles[id]
        listBox.insert(tk.END, title)
    listBox.pack()


root = tk.Tk()

button = tk.Button(root, text="버튼", command=button_clicked)
button.pack()
listBox = tk.Listbox(root, height=40, width=60)
listBox.pack()

root.mainloop()

