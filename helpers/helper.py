import csv
import os
import re
import threading
from calendar import monthrange
from datetime import datetime
from random import randint

import requests

MONTH_NAME = {"01": "янв", "02": "фев", "03": "мар", "04": "апр",
              "05": "мая", "06": "июн", "07": "июл", "08": "авг",
              "09": "сен", "10": "окт", "11": "ноя", "12": "дек", }

HEADERS = ['Имя партнера', 'Название акции', 'Дата начала', 'Дата окончания',
           'Условия акции', 'Купон', 'URL', 'Тип купона']


def exception_hook(exctype, value, tb):
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


def generate_csv():
    with open(actions_csv_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file, delimiter=";")
        writer.writerow(HEADERS)


def generate_temp_csv():
    with open("actions_temp.csv", "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file, delimiter=";")
        writer.writerow(HEADERS)


def write_csv(actions):
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
    date_start = DATA_NOW
    date_end = datetime.strptime(date_start, '%d.%m.%Y')
    day_on_month = monthrange(year=int(date_end.year), month=int(date_end.month))
    date_end = datetime(day=day_on_month[1], month=date_end.month, year=date_end.year).strftime('%d.%m.%Y')
    return date_start, date_end


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
    name = randint(1000000, 9999999)
    format = re.search(r'(\w+)$', link).group(1)
    name = str(name) + "." + format
    path = os.path.join(result_path, name)
    p = requests.get(link)
    out = open(path, 'wb')
    out.write(p.content)
    out.close()
    queue.put(f'{name} успешно скачан')


def generate_action(partner_name, action_name, date_start, date_end, description, code, url, action_type):
    return {'Имя партнера': partner_name, 'Название акции': action_name, 'Дата начала': date_start,
            'Дата окончания': date_end, 'Условия акции': description,
            'Купон': code, 'URL': url, 'Тип купона': action_type}
