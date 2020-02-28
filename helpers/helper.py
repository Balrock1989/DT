import csv
import os
import re
import threading
from calendar import monthrange
from random import randint
from datetime import datetime, timedelta

import requests

"""Даты для преобразования 02 февраля в 02.02 и тд."""
MONTH_NAME = {"01": "янв", "02": "фев", "03": "мар", "04": "апр",
              "05": "мая", "06": "июн", "07": "июл", "08": "авг",
              "09": "сен", "10": "окт", "11": "ноя", "12": "дек", }

"""Заголовки для CSV"""
HEADERS = ['Имя партнера', 'Название акции', 'Дата начала', 'Дата окончания',
           'Условия акции', 'Купон', 'URL', 'Тип купона', 'Короткое описание']


def exception_hook(exctype, value, tb):
    """Переопределяем вывод ошибок"""
    print("*******ERROR********")
    print('My Error Information')
    print('Type:', exctype)
    print('Value:', value)
    print('Traceback:', tb)
    print("*******ERROR********")


home_path = os.getenv('HOMEPATH')
actions_csv_path = os.path.join('C:\\', home_path, 'Desktop', "actions.csv")
actions_csv_path = os.path.normpath(actions_csv_path)
result_path = os.path.join('C:\\', home_path, 'Desktop', 'result')
result_path = os.path.normpath(result_path)
DATA_NOW = datetime.now().strftime('%d.%m.%Y')


def check_action_type(code, name, desc):
    if 'требуется' not in code:
        action_type = 'купон'
    elif 'подарок' in name.lower() or 'подарок' in name.lower():
        action_type = 'подарок'
    elif 'доставка' in desc.lower() or 'доставка' in desc.lower():
        action_type = 'доставка'
    else:
        action_type = 'скидка'
    return action_type

def generate_csv():
    """Создает пустой CSV на рабочем столе при запуске программы, для хранения акций"""
    with open(actions_csv_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file, delimiter=";")
        writer.writerow(HEADERS)


def generate_temp_csv():
    """Создает временный CSV, используется для удаления добавленных акций"""
    with open("actions_temp.csv", "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file, delimiter=";")
        writer.writerow(HEADERS)


def write_csv(actions):
    """Принимает список из акций, и записывает их в CSV"""
    for action in actions:
        with open(actions_csv_path, "a", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=HEADERS, delimiter=";")
            writer.writerow(action)


def one_date_return_two(incoming_date):
    """ принимает дату в формате 1 февраля 2019, возвращает 2 даты в формате 01.02.2019 и до конца месяца """
    day, month, year = incoming_date.split(" ")
    for num, name in MONTH_NAME.items():
        if name in month.lower():
            month = num
    date_start = datetime(day=int(day), month=int(month), year=int(year)).strftime('%d.%m.%Y')
    day_on_month = monthrange(year=int(year), month=int(month))
    end_data = datetime(day=day_on_month[1], month=int(month), year=int(year)).strftime('%d.%m.%Y')
    return date_start, end_data


def get_double_date(first, second):
    """ принимает 2 даты в формате 1 февраля 2019, возвращает 2 даты в формате 01.02.2019 03.02.2019 """
    try:
        first = get_one_date(first)
    except Exception:
        first = DATA_NOW
    try:
        second = get_one_date(second)
    except Exception:
        second = datetime.strptime(first, '%d.%m.%Y')
        day_on_month = monthrange(year=int(second.year), month=int(second.month))
        second = datetime(day=day_on_month[1], month=second.month, year=second.year).strftime('%d.%m.%Y')
    return first, second


def get_one_date(text):
    """ принимает 1 дату в формате 1 февраля 2019 или 1 февраля, возвращает 1 дату в формате 01.02.2019"""
    try:
        text = re.search(r'(\d+\s\w+\s?\d*)', text).group(1)
    except Exception:
        text = re.search(r'(\d+.\w+.\d*)', text).group(1)
        text = text.replace('.', ' ')
    text = re.sub(r'\xa0', ' ', text).strip()
    try:
        day, month, year = text.split(' ')
    except Exception:
        day, month = text.split(" ")
        year = datetime.now().year
    for num, name in MONTH_NAME.items():
        if name in month.lower():
            month = num
    date = datetime(day=int(day), month=int(month), year=int(year)).strftime('%d.%m.%Y')
    return date


def get_date_now_to_end_month():
    """Возвращает start с текущего дня и end  конец текущего месяца"""
    date_start = DATA_NOW
    date_end = datetime.strptime(date_start, '%d.%m.%Y')
    day_on_month = monthrange(year=int(date_end.year), month=int(date_end.month))
    date_end = datetime(day=day_on_month[1], month=date_end.month, year=date_end.year).strftime('%d.%m.%Y')
    return date_start, date_end


def get_date_end_month():
    """Возвращает дату на конец текущего месяца"""
    date_end = datetime.strptime(DATA_NOW, '%d.%m.%Y')
    day_on_month = monthrange(year=int(date_end.year), month=int(date_end.month))
    date_end = datetime(day=day_on_month[1], month=date_end.month, year=date_end.year).strftime('%d.%m.%Y')
    return date_end

def get_date_month_ahead(start):
    """Возвращает дату через 30 дней после даты начала"""
    date_end = datetime.strptime(start, '%d.%m.%Y') + timedelta(days=30)
    return date_end.strftime('%d.%m.%Y')

def get_date_half_year_ahead(start):
    """Возвращает дату через полгода после даты начала"""
    date_end = datetime.strptime(start, '%d.%m.%Y') + timedelta(days=179)
    return date_end.strftime('%d.%m.%Y')

def promotion_is_outdated(end):
    """Проверяет кончилась ли акция"""
    date_end = datetime.strptime(end, '%d.%m.%Y')
    date_now = datetime.strptime(DATA_NOW, '%d.%m.%Y')
    return False if date_end >= date_now else True


def get_range_date(text):
    """ возвращает список [начало акции, конец акции] ищет текст в формате 1 по 20 февраля 2019 или 1 по 20февраля"""
    try:
        text = re.search(r'(\d+\sпо\s\d+\s\w+\s\d*)', text).group(1).strip()
        data = text.split('по')
    except Exception:
        try:
            text = re.search(r'(\d+\sи\s\d+\s\w+\s\d*)', text).group(1).strip()
            data = text.split('и')
        except Exception:
            try:
                text = re.search(r'(\d+\s\w+\sпо\s\d+\s\w+\s\d*)', text).group(1).strip()
                data = text.split('по')
            except Exception:
                text = re.search(r'(\d+-\d+\s\w+\s\d*)', text).group(1).strip()
                data = text.split('-')
    return data


def convert_list_to_date(my_list):
    """принимает не отформатированный список [дата начала, дата окончания] [1, 20 февраля] [1 марта, 20 марта 2020]"""
    end = get_one_date(my_list[1])
    start = my_list[0].strip().split(' ')
    if len(start) == 1:
        start_temp = datetime.strptime(end, '%d.%m.%Y')
        start = datetime(day=int(start[0]), month=start_temp.month, year=start_temp.year).strftime('%d.%m.%Y')
    else:
        start = ' '.join(start)
        start = get_one_date(start)
    return start, end


def get_start_date_in_date(text):
    """ Принимает текст, ищет даты в формате 20 февраля 2019 или 20 февраля, возвращает дату начала и конец месяца"""
    start = re.search(r'(\d+\s\w+\s\d*)', text).group(1).strip()
    start = get_one_date(start)
    end = get_date_end_month()
    return start, end


def banner_downloader(links, queue):
    """Загрузка баннеров с сайта"""
    if links:
        if not os.path.exists(result_path):
            os.mkdir(result_path)
        queue.put(f'Всего будет скачано {len(links)} баннеров')
        queue.put(f'Результаты здесь: {os.path.abspath(result_path)}')

        threads = [threading.Thread(target=downloader_run, args=(link, queue), daemon=True) for link in links]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        queue.put('Загрузка завершена')
    else:
        queue.put('Баннеры не найдены на этой странице')


def downloader_run(link, queue):
    """Принимает ссылку на баннер http"//......jpg и скачивает ее, запускается из banner_downloader в потоках"""
    name = randint(1000000, 9999999)
    format = re.search(r'(\w+)$', link).group(1)
    name = str(name) + "." + format
    path = os.path.join(result_path, name)
    p = requests.get(link)
    out = open(path, 'wb')
    out.write(p.content)
    out.close()
    queue.put(f'{name} успешно скачан')


def generate_action(partner_name, action_name, date_start, date_end, description, code, url, action_type, short_desc):
    """Сборка акции для дальнейшей записи в CSV"""
    return {'Имя партнера': partner_name, 'Название акции': action_name, 'Дата начала': date_start,
            'Дата окончания': date_end, 'Условия акции': description,
            'Купон': code, 'URL': url, 'Тип купона': action_type, 'Короткое описание': short_desc}

def check_digit(text):
    """Принимает текст, ищет в нем все цифры и по одному слову слева и справа. Возвращает цифру по шаблону"""
    lists = re.findall(r'[а-я]+\s\d+\s?\d+\s[а-я]+', text)
    for string in lists:
        if len(string.split()) == 3:
            digit = string.split()[1]
        elif len(string.split()) == 4:
            digit = string.split()
            digit = digit[1] + " " + digit[2]
        if f'от {digit} руб' in string:
            print(list(string))
            continue
        if f'{digit} руб' in string:
            return digit.replace(' ', '')
        else:
            continue
    return '0'

def find_promo_code(text):
    """Принимает текст, по слову промокод ищет код стоящий после слова"""
    try:
        list = re.findall(r'\bпромокод[а-я]*?\b\s\"?\«?\'?(\w+)', text)
    except Exception:
        return 'Не требуется'
    return list[0] if list else 'Не требуется'

