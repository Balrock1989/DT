# import csv
# import os
# import re
# import threading
# import time
# from calendar import monthrange
# from datetime import datetime, timedelta
# from random import randint
# from time import sleep
#
# import requests
# from bs4 import BeautifulSoup
# from selenium import webdriver
# from selenium.common.exceptions import NoSuchElementException
# from selenium.webdriver.chrome.options import Options
#
# from helpers import Win32
#
# ## TODO создать классы для различных хелперов. даты /веб В вебе сделать драйвер и юзать его для функций
# """Даты для преобразования 02 февраля в 02.02 и тд."""
# MONTH_NAME = {"01": "янв", "02": "фев", "03": "мар", "04": "апр",
#               "05": "мая", "06": "июн", "07": "июл", "08": "авг",
#               "09": "сен", "10": "окт", "11": "ноя", "12": "дек", }
#
# """Заголовки для CSV"""
# HEADERS = ['Тип купона', 'Название акции', 'Сумма скидки', 'Дата начала', 'Дата окончания',
#            'Минимальная сумма', 'Условия акции', 'Купон', 'URL', 'Имя партнера', 'Короткое описание']
#
#
# def time_track(func):
#     def surrogate(*args, **kwargs):
#         started_at = time.time()
#
#         result = func(*args, **kwargs)
#
#         ended_at = time.time()
#         elapsed = round(ended_at - started_at, 4)
#         print(f'Функция работала {elapsed} секунд(ы)')
#         return result
#
#     return surrogate
#
#
# def exception_hook(exctype, value, tb):
#     """Переопределяем вывод ошибок"""
#     print("*******ERROR********")
#     print('My Error Information')
#     print('Type:', exctype)
#     print('Value:', value)
#     print('Traceback:', tb)
#     print("*******ERROR********")
#
#
# home_path = os.getenv('HOMEPATH')
# actions_csv_path = os.path.join('C:\\', home_path, 'Desktop', "actions.csv")
# actions_csv_path = os.path.normpath(actions_csv_path)
# result_path = os.path.join('C:\\', home_path, 'Desktop', 'result')
# database_path = os.path.join('C:\\', home_path, 'Documents', "Actions.db")
# result_path = os.path.normpath(result_path)
# DATA_NOW = datetime.now().strftime('%d.%m.%Y')
#
#
# def check_action_type(code, name, desc):
#     if 'требуется' not in code:
#         action_type = 'купон'
#     elif 'подарок' in name.lower() or 'подарок' in desc.lower():
#         action_type = 'подарок'
#     elif 'доставка' in desc.lower() or 'доставка' in desc.lower():
#         action_type = 'доставка'
#     else:
#         action_type = 'скидка'
#     return action_type
#
#
# def get_page_use_webdriver(url, scroll=False, quit=True, hidden=False):
#     """Делает запрос на URL и возвращает BS объект страницы используя webdriver, с возможностью скролить страницу"""
#     if hidden:
#         chrome_options = Options()
#         chrome_options.add_argument("--disable-extensions")
#         chrome_options.add_argument("--disable-gpu")
#         chrome_options.add_argument("--headless")
#         # #TODO Добавить логгер на вывод в интерфейс, и сообщать о том что нужно обновить драйвер и при открытии
#         #  браузера тоже
#         driver = webdriver.Chrome(chrome_options=chrome_options)
#     else:
#         driver = webdriver.Chrome()
#     Win32.hide_all_chromedriver()
#     driver.get(url)
#     if scroll:
#         scroll_script = \
#             "window.scrollTo(0, document.body.scrollHeight);var len_of_page=document.body.scrollHeight;return " \
#             "len_of_page; "
#         len_of_page = driver.execute_script(scroll_script)
#         while True:
#             last_count = len_of_page
#             sleep(1)
#             len_of_page = driver.execute_script(scroll_script)
#             if last_count == len_of_page:
#                 break
#     page = BeautifulSoup(driver.page_source, 'lxml')
#     if quit:
#         driver.quit()
#         return page
#     else:
#         return page, driver
#
#
# def get_page_use_request(url):
#     """Делает запрос на URL и возвращает BS объект страницы используя библиотеку request"""
#     s = requests.Session()
#     s.headers.update({
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0', })
#     request = s.get(url)
#     return BeautifulSoup(request.text, 'lxml')
#
#
# def generate_csv():
#     """Создает пустой CSV на рабочем столе при запуске программы, для хранения акций"""
#     with open(actions_csv_path, "w", newline="", encoding="utf-8") as csv_file:
#         writer = csv.writer(csv_file, delimiter=";")
#         writer.writerow(HEADERS)
#
#
# def generate_temp_csv():
#     """Создает временный CSV, используется для удаления добавленных акций"""
#     with open("actions_temp.csv", "w", newline="", encoding="utf-8") as csv_file:
#         writer = csv.writer(csv_file, delimiter=";")
#         writer.writerow(HEADERS)
#
#
# def write_csv(actions):
#     """Принимает список из акций, и записывает их в CSV"""
#     for action in actions:
#         with open(actions_csv_path, "a", newline="", encoding="utf-8") as csv_file:
#             writer = csv.DictWriter(csv_file, fieldnames=HEADERS, delimiter=";")
#             writer.writerow(action)
#
#
# def get_count_suitable_actions(gui):
#     """Возвращает количество акций из списка CSV имя которых выбрано в селекте"""
#     with open(actions_csv_path, 'r', encoding='utf-8', newline='') as csv_file:
#         csv_data = csv.DictReader(csv_file, delimiter=';')
#         suitable_actions = [action for action in csv_data if action['Имя партнера'] == gui.partner_name.currentText()]
#     return len(suitable_actions)
#
#
# def filling_queue(queue, actions_data, partner_name):
#     queue.put('progress')
#     if len(actions_data) == 0:
#         queue.put(f'Акции по {partner_name} не найдены ')
#         return
#     queue.put(actions_data)
#     queue.put(write_csv(actions_data))
#     queue.put((partner_name,))
#
#
# def start_join_threads(threads):
#     for thread in threads:
#         thread.start()
#     for thread in threads:
#         thread.join()
#
#
# def one_date_return_two(incoming_date):
#     """ принимает дату в формате 1 февраля 2019, возвращает 2 даты в формате 01.02.2019 и до конца месяца """
#     day, month, year = incoming_date.split(" ")
#     for num, name in MONTH_NAME.items():
#         if name in month.lower():
#             month = num
#     date_start = datetime(day=int(day), month=int(month), year=int(year)).strftime('%d.%m.%Y')
#     day_on_month = monthrange(year=int(year), month=int(month))
#     end_data = datetime(day=day_on_month[1], month=int(month), year=int(year)).strftime('%d.%m.%Y')
#     return date_start, end_data
#
#
# def convert_text_date(incoming_date):
#     """ принимает текст с датами в формате '01.12.21 по 31.03.21' Возвращает 2 даты начала и окончания"""
#     date = re.findall(r'\d+\.\d+\.*\d*', incoming_date)
#     start = get_one_date(date[0])
#     end = get_one_date(date[1])
#     return start, end
#
#
# def get_double_date(first, second):
#     """ принимает 2 даты в формате 1 февраля 2019, возвращает 2 даты в формате 01.02.2019 03.02.2019 """
#     try:
#         first = get_one_date(first)
#     except AttributeError:
#         first = DATA_NOW
#     try:
#         second = get_one_date(second)
#     except AttributeError:
#         second = datetime.strptime(first, '%d.%m.%Y')
#         day_on_month = monthrange(year=int(second.year), month=int(second.month))
#         second = datetime(day=day_on_month[1], month=second.month, year=second.year).strftime('%d.%m.%Y')
#     return first, second
#
#
# def get_one_date(text):
#     """ принимает 1 дату в формате 1 февраля 2019 или 1 февраля, возвращает 1 дату в формате 01.02.2019"""
#     flag = False
#     try:
#         text = re.search(r'(\d+\s\w+\s?\d*)', text).group(1)
#     except AttributeError:
#         text = re.search(r'(\d+.\w+.\d*)', text).group(1)
#         text = text.replace('.', ' ')
#     text = re.sub(r'\xa0', ' ', text).strip()
#     try:
#         day, month, year = text.split(' ')
#     except ValueError:
#         day, month = text.split(" ")
#         year = datetime.now().year
#         flag = True
#     for num, name in MONTH_NAME.items():
#         if name in month.lower():
#             month = num
#     date = datetime(day=int(day), month=int(month), year=int(year))
#     if flag:
#         if (date - datetime.now()).days > 200:
#             if datetime.now().month > 6:
#                 date = datetime(day=int(day), month=int(month), year=int(year) + 1)
#             else:
#                 date = datetime(day=int(day), month=int(month), year=int(year) - 1)
#     return date.strftime('%d.%m.%Y')
#
#
# def get_date_plus_days(count):
#     """ Прибавляет к текущей дате count дней"""
#     date_now = datetime.strptime(DATA_NOW, '%d.%m.%Y')
#     date = date_now + timedelta(days=count)
#     return date.strftime('%d.%m.%Y')
#
#
# def get_date_now_to_end_month():
#     """Возвращает start с текущего дня и end  конец текущего месяца"""
#     date_start = DATA_NOW
#     date_end = datetime.strptime(date_start, '%d.%m.%Y')
#     day_on_month = monthrange(year=int(date_end.year), month=int(date_end.month))
#     date_end = datetime(day=day_on_month[1], month=date_end.month, year=date_end.year).strftime('%d.%m.%Y')
#     return date_start, date_end
#
#
# def get_date_end_month():
#     """Возвращает дату на конец текущего месяца"""
#     date_end = datetime.strptime(DATA_NOW, '%d.%m.%Y')
#     day_on_month = monthrange(year=int(date_end.year), month=int(date_end.month))
#     date_end = datetime(day=day_on_month[1], month=date_end.month, year=date_end.year).strftime('%d.%m.%Y')
#     return date_end
#
#
# def get_first_day_month():
#     """Возвращает первый день текущего месяца"""
#     date_start = datetime.strptime(DATA_NOW, '%d.%m.%Y')
#     date_start = datetime(day=1, month=date_start.month, year=date_start.year).strftime('%d.%m.%Y')
#     return date_start
#
#
# def get_date_month_ahead(start):
#     """Возвращает дату через 30 дней после даты начала"""
#     date_end = datetime.strptime(start, '%d.%m.%Y') + timedelta(days=30)
#     return date_end.strftime('%d.%m.%Y')
#
#
# def get_date_half_year_ahead(start):
#     """Возвращает дату через полгода после даты начала"""
#     date_end = datetime.strptime(start, '%d.%m.%Y') + timedelta(days=179)
#     return date_end.strftime('%d.%m.%Y')
#
#
# def promotion_is_outdated(end):
#     """Проверяет кончилась ли акция"""
#     date_end = datetime.strptime(end, '%d.%m.%Y')
#     date_now = datetime.strptime(DATA_NOW, '%d.%m.%Y')
#     return False if date_end >= date_now else True
#
#
# def get_range_date(text):
#     """ возвращает список [начало акции, конец акции] ищет текст в формате 1 по 20 февраля 2019 или 1 по 20 февраля"""
#     try:
#         text = re.search(r'(\d+\sпо\s\d+\s\w+\s\d*)', text).group(1).strip()
#         data = text.split('по')
#     except AttributeError:
#         try:
#             text = re.search(r'(\d+\sи\s\d+\s\w+\s\d*)', text).group(1).strip()
#             data = text.split('и')
#         except AttributeError:
#             try:
#                 text = re.search(r'(\d+\s\w+\s\d*.*по\s\d+\s\w+\s\d*)', text).group(1).strip()
#                 data = text.split('по')
#             except AttributeError:
#                 text = re.search(r'(\d+-\d+\s\w+\s\d*)', text).group(1).strip()
#                 data = text.split('-')
#     return data
#
#
# def get_do_period(text):
#     """ Принимает текст в формате 'До 1 декабря', возвращает дату начала - сегодня, дату окончания 01.12.2020"""
#     start = datetime.now()
#     result = re.search(r'(\d+)\s([а-яА-Я]+)\s?(\d{4})?', text)
#     day = result.group(1).strip()
#     month = result.group(2).strip().lower()
#     for num, name in MONTH_NAME.items():
#         if name in month:
#             month = int(num)
#             break
#     year = result.group(3).strip() if result.lastindex > 2 else start.year
#     if start.month > 6 and month <= 6:
#         year = year + 1
#     end = datetime(day=int(day), month=month, year=int(year)).strftime('%d.%m.%Y')
#     return start.strftime('%d.%m.%Y'), end
#
#
# def convert_list_to_date(my_list):
#     """принимает не отформатированный список [дата начала, дата окончания] [1, 20 февраля] [1 марта, 20 марта 2020]"""
#     end = get_one_date(my_list[1])
#     start = my_list[0].strip().split(' ')
#     if len(start) == 1:
#         start_temp = datetime.strptime(end, '%d.%m.%Y')
#         start = datetime(day=int(start[0]), month=start_temp.month, year=start_temp.year).strftime('%d.%m.%Y')
#     else:
#         start = ' '.join(start)
#         start = get_one_date(start)
#     return start, end
#
#
# def get_start_date_in_date(text, flag):
#     """ Принимает текст, ищет даты в формате 20 февраля 2019 или 20 февраля, возвращает дату начала и конец месяца"""
#     start = re.search(r'(\d+\s\w+(\s\d{4})?)', text).group(1).strip()
#     start = get_one_date(start)
#     end = get_date_end_month()
#     if flag:
#         return start, end
#     else:
#         return start
#
#
# def search_data_in_text(text):
#     """ Принимает текст, ищет 2 даты в формате 20.12.2020 или в формате 20 декабря 2020 по 25 декабря 2020 и
#     вовзращает их как старт и конец """
#     try:
#         income_data = re.findall(r'(\d+.\d+.\d+)', text)
#         start = income_data[0]
#         end = income_data[1]
#     except:
#         income_data = re.findall(r'(\d+.\d+)', text)
#         start = get_one_date(income_data[0])
#         end = get_one_date(income_data[1])
#     return start, end
#
#
# def search_end_data_in_text(text):
#     """ Принимает текст, ищет 2 даты в формате 20.12.2020 или в формате 20 декабря 2020 по 25 декабря 2020 и
#     вовзращает их как старт и конец """
#     start = DATA_NOW
#     try:
#         income_data = re.findall(r'(\d+.\d+.\d+)', text)
#         end = income_data[0]
#     except:
#         income_data = re.findall(r'(\d+.\d+)', text)
#         end = get_one_date(income_data[0])
#     return start, end
#
#
# def search_data_in_text_without_year(text):
#     """ Принимает текст, ищет 2 даты в формате 20.12 или в формате 20 декабря по 25 декабря, добавляет текущий год
#     и вовзращает их как старт и конец """
#     income_data = re.findall(r'(\d+.\d+)', text)
#     start = income_data[0] + '.' + str(datetime.now().year)
#     end = income_data[1] + '.' + str(datetime.now().year)
#     return start, end
#
#
# def banner_downloader(links, queue):
#     """Загрузка баннеров с сайта"""
#     if links:
#         if not os.path.exists(result_path):
#             os.mkdir(result_path)
#         queue.put(f'Всего будет скачано {len(links)} баннеров')
#         queue.put(f'Результаты здесь: {os.path.abspath(result_path)}')
#
#         threads = [threading.Thread(target=downloader_run, args=(link, queue), daemon=True) for link in links]
#         for thread in threads:
#             thread.start()
#         for thread in threads:
#             thread.join()
#         queue.put('Загрузка завершена')
#     else:
#         queue.put('Баннеры не найдены на этой странице')
#
#
# def downloader_run(link, queue):
#     """Принимает ссылку на баннер http"//......jpg и скачивает ее, запускается из banner_downloader в потоках"""
#     name = randint(1000000, 9999999)
#     file_format = re.search(r'(\w+)$', link).group(1)
#     name = str(name) + "." + file_format
#     path = os.path.join(result_path, name)
#     try:
#         p = requests.get(link, timeout=5)
#         out = open(path, 'wb')
#         out.write(p.content)
#         out.close()
#         queue.put(f'{name} успешно скачан')
#     except Exception as exc:
#         queue.put(f'Не удалось скачать баннер: {link}')
#         print(exc)
#
#
# def generate_action(partner_name, action_name, date_start, date_end, description, code, url, action_type, short_desc):
#     """Сборка акции для дальнейшей записи в CSV"""
#     return {'Имя партнера': partner_name, 'Название акции': action_name, 'Дата начала': date_start,
#             'Дата окончания': date_end, 'Условия акции': description,
#             'Купон': code, 'URL': url, 'Тип купона': action_type, 'Короткое описание': short_desc}
#
#
# def generate_action_new(action):
#     """Сборка акции для дальнейшей записи в CSV"""
#     return {'Имя партнера': action.partner_name,
#             'Название акции': action.name,
#             'Дата начала': action.start,
#             'Дата окончания': action.end,
#             'Условия акции': action.desc,
#             'Купон': action.code,
#             'URL': action.url,
#             'Тип купона': action.action_type,
#             'Короткое описание': action.short_desc}
#
#
# def check_digit(text):
#     """Принимает текст, ищет в нем все цифры и по одному слову слева и справа. Возвращает цифру по шаблону"""
#     """ Возможные комбинации Скидка 1000 ₽, Скидка 1000₽, Скидка 1 000 руб, Скидка 1000 руб, Скидка 1000руб"""
#     lists = re.findall(r'\w+\s\d+\s?\d+\s?\w+', text)
#     lists2 = re.findall(r'\w+\s\d+\s?\d+\s?\W', text)
#     lists = lists + lists2
#     for string in lists:
#         digit = re.sub(r'\D', '', string)
#         if len(string.split()) == 4:
#             digit = string.split()
#             digit = digit[1] + " " + digit[2]
#         if f'от {digit} руб' in string:
#             continue
#         if f'{digit} руб' in string or f'{digit}руб' in string:
#             return digit.replace(' ', '')
#         elif f'{digit} ₽' in string or f'{digit}₽' in string:
#             return digit.replace(' ', '')
#         else:
#             continue
#     return '0'
#
#
# def find_promo_code(text):
#     """Принимает текст, по слову промокод ищет код стоящий после слова"""
#     promo = re.findall(r'\bпромокод[а-я]*?\b\s\"?\«?\'?(\w+)', text)
#     return promo[0] if promo else 'Не требуется'
#
#
# def check_exists_by_css(driver, css):
#     try:
#         elem = driver.find_element_by_css_selector(css)
#     except NoSuchElementException:
#         return False
#     return elem
