import urllib.request
import re
import os
import lxml
from lxml import etree
from io import StringIO
from lxml.html import parse
from lxml.cssselect import CSSSelector

from lxml import html
from lxml.html.clean import clean_html

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
        if ahref[0:6] == '/news/' and ahref[0:10] != '/news/tag/':
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

    parse_url_and_save(url)

    page = load_page(url)
    save_page(page)
    links = extract_news_links(page)
    for link in links:
        execute_url(link)

def parse_url_and_save(url):
    html_document = parse(url).getroot()

    page_contents = html_document.find_class("page_content")
    if len(page_contents) == 0: return
    page_content = page_contents[0]

    news_contents = page_content.find_class("content_c")
    if len(news_contents) == 0: return
    news_content = news_contents[0]

    news_details = page_content.find_class("news_detail")
    if len(news_details) == 0: return
    news_detail = news_details[0]

    # Автор статьи
    authors = news_content.find_class("autor_name")
    if len(authors) == 0: return
    author = authors[0].find('a')
    author = clean_html(author).text_content()

    # Заголовок статьи
    header = news_content.find("h1")
    header = clean_html(header).text_content()
    if len(header) == 0: return

    # Дата статьи
    created = page_content.find_class('date_time')[0].find_class('date')[0]
    created = clean_html(created).text_content()

    # Topic
    topic = news_content.find_class('rubric')[0]
    topic = clean_html(topic).text_content()

    # source
    source = url

    # publ_year
    publ_year = created[6:]

    # Текст статьи
    text = news_detail.find("article")
    text = clean_html(text).text_content()

    add_to_csv('m', author, header, topic, created, text, source, publ_year)

    # print("Coхраняем статью: " + created + "; " + author + "; " + topic)

def add_to_csv (path, author, header, topic, created, text, source, publ_year):
    str = path + "|" + author + "|||" + header + "|" + created + "|публицистика|||"+topic+"||нейтральный|н-возраст|н-уровень|республиканская|"+source+"|Марийская правда||"+ publ_year+" |газета|Россия|Марий Эл|ru\n"
    f = open('test.csv', 'a+',encoding = 'utf-8')
    f.write(str)
execute_url(BASE_URL)






# path -- это путь к файлу со статьёй,
# author -- имя автора, если его можно достать со страницы (и вообще если оно есть),
# sex -- поле оставить пустым,
# birthday -- оставить пустым
# header -- название статьи
# created -- дата в формате 07.01.2012 (день.месяц.год)
# sphere -- слово "публицистика"
# genre_fi -- оставить пустым
# type -- оставить пустым
# topic -- категория, если мы её можем найти на странице со статьёй
# chronotop -- оставить пустым
# style -- слово "нейтральный"
# audience_age -- слово "н-возраст"
# audience_level -- слово "н-уровень"
# audience_size -- "районная", если газета районная, "республиканская", если газета республиканская, "городская" -- если городская.
# source -- URL, откуда статья была скачана
# publication -- название газеты
# publisher -- оставить пустой
# publ_year -- год публикации
# medium -- слово "газета"
# country -- слово "Россия"
# region -- Название региона, откуда ваша газета
# language -- слово "ru"




