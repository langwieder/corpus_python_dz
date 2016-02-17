import urllib.request
import re
import os

# Базовый URL сайта для парсинга
BASE_URL = 'http://www.marpravda.ru'

# Словарь в котором хранятся уже загруженные ссылки
links_dic = {}

# Загрузка страницы из интернета
def load_page(url):
    con = urllib.request.urlopen(url)
    page = con.read()
    page = page.decode()
    return page


# Функция для извлечения ссылок со страницы
def extract_news_links(page):
    links = []
    ahrefs = re.findall("<a.*href\=\"(.+?)\"", page)
    for ahref in ahrefs:
        if ahref[0:6] == '/news/':
            link = BASE_URL + ahref
            links.append(link)

    return links

dir_num = 0
file_num = 0

# Функция для сохранения страницы
def save_page(page):
    global dir_num
    global file_num

    # Создать папку, если ее нет
    dir_path = './pages/' + str(dir_num)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    file = open(dir_path + '/' + str(file_num) + '.html','w',encoding = 'utf-8')
    file.write(page)

    file_num += 1
    if file_num > 49:
        dir_num += 1
        file_num = 0


# Функция для обработки страницы (загрузки, сохранения, извлечения ссылок)
def execute_url(url):
    if url in links_dic.keys():
        return

    links_dic[url] = 1

    print(url)

    page = load_page(url)
    save_page(page)
    links = extract_news_links(page)
    for link in links:
        execute_url(link)


execute_url(BASE_URL)