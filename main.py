import tkinter.messagebox
import requests
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from bs4 import BeautifulSoup as bs
import csv

class Link:
    def __init__(self, name, link, type, ammount):
        self.name = name
        self.link = link
        self.type = type
        self.ammount = ammount

def recountIndex():
    delitingList = t.get_children()
    for ditem in delitingList:
        t.delete(ditem)
    for i in range(len(Links)):
        insertion = (i + 1, Links[i].type, Links[i].name, Links[i].link, Links[i].ammount)
        t.insert('', 'end', values=insertion)
    blockLinks()

def blockLinks():
    blockinglist = t.get_children()
    with open("blacklist.txt", 'r', newline='') as f:
        blackList = f.readlines()
    for i in blockinglist:
        if len(getDomen(t.item(i).get('values')[3])) >= 2:
            if getDomen(t.item(i).get('values')[3])[2] + '\n' in blackList:
                t.set(i, 3, "[запрещенная ссылка]")

def deleteSimilar():
    for i in range(len(Links)):
        k = 1
        for j in range(i + 1, len(Links)):
            if Links[i].link == Links[j].link:
                k += 1
                Links[j].link = "Removal"
        Links[i].ammount = k

def deleteRemoval():
    selectedItems = t.get_children()
    n = 1
    for itm in selectedItems:
        if t.item(itm).get("values")[3] == "Removal":
            Links.pop(t.item(itm).get("values")[0] - n)
            t.delete(itm)
            n += 1
    recountIndex()

def deleteSelected(event):
    selectedItems = t.selection()
    n = 1
    for itm in selectedItems:
        Links.pop(t.item(itm).get("values")[0] - n)
        t.delete(itm)
        n += 1
    recountIndex()

def getDomen(s):
    return s.split('/')

def getHTML(event):
    Links.clear()
    delitingList = t.get_children()
    for ditem in delitingList:
        t.delete(ditem)
    try:
        r = filedialog.askopenfilename()
        fopen = open(r, "r", encoding='utf-8')
    except:
        tkinter.messagebox.showerror("Ошибка", "Невозможно открыть файл")
        return None
    html = bs(fopen, "html.parser")
    allLinks = html.findAll('a')  # Парсинг всех ссылок
    allIMGS = html.findAll('img')  # Парсинг всех изображений
    for l in allLinks:
        Links.append(Link(l.text.strip(), l.get("href"), "Гиперссылка", "1"))
    for i in allIMGS:
        Links.append(Link(i.get('alt'), i.get('src'), "Изображение", "1"))
    deleteSimilar()
    for i in range(len(Links)):
        insertion = (i + 1, Links[i].type, Links[i].name, Links[i].link, Links[i].ammount)
        t.insert('', 'end', values=insertion)
    deleteRemoval()
    fopen.close()

def addToBlackList(event):
    try:
        focusitems = t.focus()
        with open("blacklist.txt", 'a', newline='') as f:
            f.write(getDomen(t.item(focusitems).get("values")[3])[2] + '\n')
        recountIndex()
    except:
        tkinter.messagebox.showerror("Ошибка", "Невозможно добавить домен в черный список")

def getURL(event):
    with open("blacklist.txt", 'r', newline='') as f:
        blackList = f.readlines()
    Links.clear()
    delitingList = t.get_children()
    for ditem in delitingList:
        t.delete(ditem)
    url = urlValue.get()
    dom = getDomen(url)
    try:
        r = requests.get(url, timeout=1)
    except:
        tkinter.messagebox.showerror("Ошибка", "Невозможно отправить запрос")
        return None
    if dom[2] in blackList:
        tkinter.messagebox.showerror("Ошибка", "Домен присутствует в чёрном списке")
        return None
    html = bs(r.content, "html.parser")
    allLinks = html.findAll('a')  # Парсинг всех ссылок
    allIMGS = html.findAll('img')  # Парсинг всех изображений
    for l in allLinks:
        if l.get("href") is not None:
            Links.append(Link(l.text.strip(), l.get("href"), "Гиперссылка", 1))
    for i in allIMGS:
        if l.get('src') is not None:
            Links.append(Link(i.get('alt'), i.get('src'), "Изображение", 1))
    for lnk in Links:
        if len(lnk.link) > 0:
            if "http" not in str(lnk.link) and dom[2] not in str(lnk.link):
                if str(lnk.link)[0] != "/":
                    lnk.link = dom[0] + "//" + dom[2] + "/" + str(lnk.link)
                else:
                    lnk.link = dom[0] + "//" + dom[2] + str(lnk.link)
    deleteSimilar()
    for i in range(len(Links)):
        insertion = (i + 1, Links[i].type, Links[i].name, Links[i].link, Links[i].ammount)
        t.insert('', 'end', values=insertion)
    deleteRemoval()
    recountIndex()

def exportCSV(event):
    try:
        path = str(
            filedialog.asksaveasfilename(filetypes=[("CSV file", ".csv "), ("TXT file", ".txt")],
                                         defaultextension=".csv"))
        with open(path, 'w', newline='', encoding='cp1251') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(['№', 'Тип', 'Название', 'Ссылка', 'Кол-во повторений'])
            allitems = t.get_children()
            for itm in allitems:
                writer.writerow([str(t.item(itm).get("values")[0]), str(t.item(itm).get("values")[1]),
                                 str(t.item(itm).get("values")[2]), str(t.item(itm).get("values")[3]),
                                 str(t.item(itm).get("values")[4])])
    except:
        tkinter.messagebox.showerror("Ошибка", "Невозможно экспортировать файл")

def editLink(event):
    def edit():
        Links[int(t.item(te).get('values')[0]) - 1].link = churl.get()
        Links[int(t.item(te).get('values')[0]) - 1].name = chname.get()
        Links[int(t.item(te).get('values')[0]) - 1].type = chtype.get()
        recountIndex()
        window.destroy()
    te = t.focus()
    if len(te) == 0:
        return None
    window = Tk()
    window.title("Изменить ссылку")
    window.resizable(width=False, height=False)
    window.geometry("300x110")
    chnm = Label(window, text="Название: ")
    chname = Entry(window, width=30)
    chrl = Label(window, text="Ссылка: ")
    churl = Entry(window, width=30)
    chpe = Label(window, text="Тип: ")
    chtype = ttk.Combobox(window, width=30, values=["Гиперссылка", "Изображение"],state="readonly")
    but = Button(window, text="Изменить", command= lambda: edit())
    but2 = Button(window, text="Отмена", command=lambda: window.destroy())
    chname.grid(row=0, column=1, columnspan=1, pady=2, padx=5)
    churl.grid(row=1, column=1, columnspan=1, pady=2, padx=5)
    chtype.grid(row=2, column=1, columnspan=1, pady=2, padx=5)
    chnm.grid(row=0, column=0, columnspan=1, pady=2, padx=5)
    chrl.grid(row=1, column=0, columnspan=1, pady=2, padx=5)
    chpe.grid(row=2, column=0, columnspan=1, pady=2, padx=5)
    but.grid(row=3, column=0, columnspan=1, pady=2, padx=5)
    but2.grid(row=3, column=1, columnspan=1, pady=2, padx=5)
    window.mainloop()

allLinks = []
allIMGS = []
Links = []
blackList = []

root = Tk()
root.geometry("690x450")
root.title("HTML-парсер")
root.resizable(width=False, height=False)
headings = ['№', 'Тип', 'Название', 'Ссылка', 'Кол-во повторений']
t = ttk.Treeview(root, show="headings", height=17)
t.grid(padx=5)
t['columns'] = headings
for h in headings:
    t.heading(h, text=h, anchor='center')
    t.column(h, anchor='center')
t.column('№', width=50, minwidth=0, stretch=NO)
t.column('Тип', width=100)
t.column('Название', width=200)
t.column('Ссылка', width=200)
t.column('Кол-во повторений', width=130, stretch=NO)
t.grid(row=1, column=0, rowspan=2, columnspan=5)
Label(text="URL-адрес: ") \
    .grid(row=0, column=0, columnspan=1, padx=5)
urlValue = StringVar()
writeURL = Entry(width=57, textvariable=urlValue)
writeURL.grid(row=0, column=1, columnspan=2, padx=5, pady=5)
buttonWriteURL = Button(text="Вставить URL")
buttonDeleteSelected = Button(text="Удалить выбранные")
buttonDeleteSelected.grid(row=3, column=1, pady=10, padx=5)
buttonPasteHTML = Button(text="Импорт")
buttonExportCSV = Button(text="Экспорт")
buttonEditLink = Button(text="Изменить ссылку")
buttonPasteHTML.grid(row=0, column=4, columnspan=1, rowspan=1, pady=5)
buttonWriteURL.grid(row=0, column=3, columnspan=1, rowspan=1, pady=5, padx=5)
buttonExportCSV.grid(row=3, column=0, pady=10)
buttonEditLink.grid(row=3, column=3, columnspan=1, pady=10)
buttonAddToBlackList = Button(text="Добавить домен в чёрный список")
buttonAddToBlackList.grid(row=3, column=2, columnspan=1, pady=10)
buttonWriteURL.bind('<Button-1>', getURL)
buttonPasteHTML.bind('<Button-1>', getHTML)
buttonDeleteSelected.bind('<Button-1>', deleteSelected)
buttonExportCSV.bind('<Button-1>', exportCSV)
buttonAddToBlackList.bind('<Button-1>', addToBlackList)
buttonEditLink.bind('<Button-1>', editLink)
root.mainloop()
