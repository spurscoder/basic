from tkinter import *
import tkinter.font as tkFont

filename = '/home/spurs/data/50m_xiaohuangji.txt'
dialog = []
with open(filename, 'r', encoding='utf-8') as f:
    line = f.readline()
    while line != "":
        if not line.startswith('E') and line != '\n':
            dialog.append(line[:-1])
        line = f.readline()
print(dialog[:10])

class WidgetsDemo:
    def __init__(self):
        window = Tk()
        window.title("标记")
#        window.geometry("900x300")
        #添加一个多选按钮和单选按钮到frame1
        frame1 = Frame(window, bg='#333745')
        frame1.pack(fill=X, side=TOP)  #看下面的解释（包管理器）
        ft = tkFont.Font(family='', size=14)

        self.num = 1

        self.label1 = Label(frame1, text = "第 1 句话：",width=10, font=ft, bg='#999999', fg = 'white')
        self.label2 = Label(frame1, text = "%s" % dialog[self.num], width=50, font=ft, bg='#333745', fg= 'white')
        self.label1.grid(row=0, pady=50 )
        self.label2.grid(row=0, column=1)

        frame2 = Frame(window, bg='#333745')
        frame2.pack(fill=X)

        self.mainclass = IntVar(value=1)
        class1 = Label(frame2, text = "大类", width=10, font=ft, bg="#999999", fg="white")
        rb1 = Radiobutton(frame2, indicatoron=0, text = "Telling", font=ft,bg='#66CDAA', width=8, variable=self.mainclass, value = 1)
        rb2 = Radiobutton(frame2, indicatoron=0, text = "Asking", font=ft, bg='#66CDAA', width=8,variable=self.mainclass, value = 2)
        rb3 = Radiobutton(frame2, indicatoron=0, text = "Ordering", font=ft, bg='#66CDAA',width=8, variable=self.mainclass, value = 3)
        rb4 = Radiobutton(frame2, indicatoron=0, text = "Judging", font=ft, bg='#66CDAA', width=8,variable=self.mainclass, value = 4)
        rb5 = Radiobutton(frame2, indicatoron=0, text = "Emotion", font=ft, bg='#66CDAA', width=8,variable=self.mainclass, value = 5)
        class1.grid(row=2, column=0, pady=10)
        rb1.grid(row=2, column=1, padx=8)
        rb2.grid(row=2, column=2, padx=8)
        rb3.grid(row=2, column=3, padx=8)
        rb4.grid(row=2, column=4, padx=8)
        rb5.grid(row=2, column=5, padx=8)

        self.subclass = IntVar(value=1)
        class2 = Label(frame2, text = "小类", width=10, font=ft, bg="#999999", fg="white")
        sub_rb1 = Radiobutton(frame2, indicatoron=0, text = "喜", font=ft,bg='#DAA520', width=7, variable=self.subclass, value = 1)
        sub_rb2 = Radiobutton(frame2, indicatoron=0, text = "怒", font=ft,bg='#DAA520', width=7, variable=self.subclass, value = 2)
        sub_rb3 = Radiobutton(frame2, indicatoron=0, text = "哀", font=ft,bg='#DAA520', width=7, variable=self.subclass, value = 3)
        sub_rb4 = Radiobutton(frame2, indicatoron=0, text = "乐", font=ft,bg='#DAA520', width=7, variable=self.subclass, value = 4)
        sub_rb5 = Radiobutton(frame2, indicatoron=0, text = "忧", font=ft,bg='#DAA520', width=7, variable=self.subclass, value = 5)
        class2.grid(row=3, column=0, pady=10)
        sub_rb1.grid(row=3, column=1)
        sub_rb2.grid(row=3, column=2)
        sub_rb3.grid(row=3, column=3)
        sub_rb4.grid(row=3, column=4)
        sub_rb5.grid(row=3, column=5)

        frame3 = Frame(window, bg='#333745')
        frame3.pack(fill=X)

        left_button = Button(frame3, text="上一句", font=ft, width = 12, bg='#CCCC66', fg='white', command = self.on_left)
        right_buttion = Button(frame3, text="下一句", font=ft, width = 12, bg='#339966', fg='white', command = self.on_right)
        left_button.grid(row = 4, column = 0, padx=90, pady=10)
        right_buttion.grid(row = 4, column = 1)


        window.mainloop()

    def on_left(self):
        if self.num > 0:
            print(dialog[self.num],"\t大类标记为：",self.mainclass.get(),"\t小类标记为：",self.subclass.get())

        if self.num > 0:
            self.num -= 1
            self.label1.config(text = "第 %d 句话：" % self.num)
            self.label2.config(text = dialog[self.num])
            self.mainclass.set(1)
            self.subclass.set(1)



    def on_right(self):
        print(dialog[self.num],"\t大类标记为：",self.mainclass.get(),"\t小类标记为：",self.subclass.get())

        self.num += 1
        self.label1.config(text = "第 %d 句话：" % self.num)
        self.label2.config(text = dialog[self.num])
        self.mainclass.set(1)
        self.subclass.set(1)

WidgetsDemo()

