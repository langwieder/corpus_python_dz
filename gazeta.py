import urllib.request
import re
import os
from lxml.html import parse
from lxml.html.clean import clean_html
import hashlib

# Базовый URL сайта для парсинга
BASE_URL = 'http://www.marpravda.ru'

# Словарь в котором хранятся уже загруженные ссылки
links_dic = {}


# Загрузка страницы из интернета, попытаться загрузить по url, в случае ошибки возвращается none
def load_page(url):
    try:
        con = urllib.request.urlopen(url)
    except:
        return None
    page = con.read()
    page = page.decode()
    return page


# Функция для извлечения ссылок со страницы
def extract_news_links(page):
    links = []
    ahrefs = re.findall("<a.*href=\"(.+?)\"", page)
    for ahref in ahrefs:
        if ahref[0:6] == '/news/' and ahref[0:10] != '/news/tag/' and ahref.find("#") == -1 and ahref.find("?") == -1:
            link = BASE_URL + ahref
            links.append(link)

    return links


# Функция для обработки страницы (загрузки, сохранения, извлечения ссылок)

def execute_url(url):
    # проверяем, не обрабатывали ли ранее эту ссылку
    if url in links_dic.keys():
        return
    links_dic[url] = 1

    print(url)

    parse_url_and_save(url)

    page = load_page(url)
    if page is None:
        return

    links = extract_news_links(page)
    for link in links:
        execute_url(link)


def parse_url_and_save(url):
    try:
        html_document = parse(url).getroot()
    except:
        print("не удалось загрузить url или распарсить документ")
        return

    page_contents = html_document.find_class("page_content")
    if len(page_contents) == 0:
        return
    page_content = page_contents[0]

    news_contents = page_content.find_class("content_c")
    if len(news_contents) == 0:
        return
    news_content = news_contents[0]

    news_details = page_content.find_class("news_detail")
    if len(news_details) == 0:
        return
    news_detail = news_details[0]

    # Автор статьи
    authors = news_content.find_class("autor_name")
    if len(authors) == 0:
        return
    author = authors[0].find('a')
    author = clean_html(author).text_content()

    # Заголовок статьи
    header = news_content.find("h1")
    header = clean_html(header).text_content()
    header = header.strip(' \t\n\r')
    if len(header) == 0:
        return

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
    text = text.strip(' \t\n\r')

    # Сохраняем извлеченную инфу в файл, добавляем в csv
    path = save_text_to_file(author, header, created, topic, source, text)
    add_to_csv(path, author, header, topic, created, source, publ_year)


def add_to_csv(path, author, header, topic, created, source, publ_year):
    string = path + "|" + author + "|||" + header + "|" + created + "|публицистика|||" + topic + "||нейтральный|н-возраст|н-уровень|республиканская|" + source + "|Марийская правда||" + publ_year + " |газета|Россия|Марий Эл|ru\n"
    f = open('marpravda.csv', 'a+', encoding='utf-8')
    f.write(string)


words_count = 0


# Функция, которая сохранит текст и файл
def save_text_to_file(author, header, created, topic, source, text):
    # Чтобы записать значение в переменную за пределами функции
    global words_count

    # Считаем количество слов
    words = re.findall(r'\w+', text)
    words_count += len(words)
    print("Количество слов: " + str(words_count))

    year = created[6:]
    month = created[3:5]
    # Путь, куда сохраняем файлы 3 видов: текстовый, xml-mystem и text-mystem
    directory = './' + year + '/' + month + '/'
    text_dir = directory + 'text/'
    xml_mystem_dir = directory + 'mystem_xml/'
    text_mystem_dir = directory + 'mystem_text/'
    # Создаем папки для файлов
    if not os.path.exists(text_dir):
        os.makedirs(text_dir)
    if not os.path.exists(xml_mystem_dir):
        os.makedirs(xml_mystem_dir)
    if not os.path.exists(text_mystem_dir):
        os.makedirs(text_mystem_dir)
    # Генерируем имя файла
    filename = hashlib.md5(source.encode()).hexdigest()
    # Полные пути к файлам
    text_path = text_dir + filename + ".txt"
    xml_mystem_path = xml_mystem_dir + filename + ".xml"
    text_mystem_path = text_mystem_dir + filename + ".txt"
    # Добавление информации в шапку текста
    file_header = '@au ' + author + '\n'
    file_header = file_header + '@ti ' + header + '\n'
    file_header = file_header + '@da ' + created + '\n'
    file_header = file_header + '@topic ' + topic + '\n'
    file_header = file_header + '@url ' + source + '\n'
    file_text = file_header + text
    f = open(text_path, 'w', encoding='utf-8')
    f.write(file_text)
    f.close()

    # Путь к текущей директории для mystem
    current_dir = os.getcwd() + "/"

    # Выполняем mystem
    os.system(current_dir + "mystem -d -l -i " + current_dir + text_path + " " + current_dir + text_mystem_path)
    os.system(current_dir + "mystem -d -l -i --format xml " + current_dir + text_path + " " + current_dir + xml_mystem_path)

    return text_path

execute_url(BASE_URL)
