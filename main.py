import tkinter as tk

def button_clicked():
    print("버튼이 클릭되었습니다.")

root = tk.Tk()

button = tk.Button(root, text="버튼", command=button_clicked)
button.pack()

root.mainloop()
