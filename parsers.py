import csv
import re
from calendar import monthrange
from datetime import datetime
from time import sleep

import requests
from bs4 import BeautifulSoup


class Parsers:
    def __init__(self):
        self.month_name = {"01": "янв", "02": "фев", "03": "мар", "04": "апр",
                           "05": "мая", "06": "июн", "07": "июл", "08": "авг",
                           "09": "сен", "10": "окт", "11": "ноя", "12": "дек", }
        self.headers = ['Имя партнера', 'Название акции', 'Дата начала', 'Дата окончания',
                        'Полное описание', 'Короткое описание', 'Купон', 'URL', 'Тип акции']
        self.generate_csv()

    def generate_csv(self):
        with open("actions.csv", "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file, delimiter=";")
            writer.writerow(self.headers)

    def parser_sephora(self, gui):
        """Сбор и форамтирование информации об акциях"""

        def get_date(self, div):
            incoming_date = re.search(r'Срок проведения Акции: с (\d.*\d+)', div.text)[1]
            day, month, year = incoming_date.split(" ")
            for num, name in self.month_name.items():
                if name in month.lower():
                    month = num
            date_start = datetime(day=int(day), month=int(month), year=int(year)).strftime('%d.%m.%Y')
            day_on_month = monthrange(year=int(year), month=int(month))
            end_data = datetime(day=day_on_month[1], month=int(month), year=int(year)).strftime('%d.%m.%Y')
            return date_start, end_data

        s = requests.Session()
        s.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'})
        main_url = 'https://sephora.ru/news/'
        request = s.get(main_url)
        page = BeautifulSoup(request.text, 'lxml')
        links = page.find_all("a", class_='b-news-thumb__title')
        with open("actions.csv", "a", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.headers, delimiter=";")
            #TODO Добавить потоки на обработку каждой ссылки
            for link in links:
                link = main_url[:-5] + link['href'][1:]
                gui.log.info(f'{link}')
                request = s.get(link)
                page = BeautifulSoup(request.text, 'lxml')
                div = page.find('div', class_='b-news-detailed')
                if div:
                    try:
                        date_start, date_end = get_date(self, div)
                    except TypeError:
                        gui.log.info('Не найдена дата проведения акции')
                        continue
                    code = "Не требуется"
                    action_type = 'подарок'
                    action_name = div.h1.text
                    paragraphs = div.findAll('p')
                    descriptions = []
                    for p in paragraphs:
                        text = p.text.strip()
                        if 'При' in text:
                            descriptions.append(text)
                    for desc in descriptions:
                        action = {'Имя партнера': 'Sephora', 'Название акции': action_name, 'Дата начала': date_start,
                                  'Дата окончания': date_end, 'Полное описание': desc, 'Короткое описание': action_name,
                                  'Купон': code, 'URL': 'https://sephora.ru', 'Тип акции': action_type}
                        writer.writerow(action)
                    gui.chat_print(f'\nИмя партнера: Sephora, загружено акций: {len(descriptions)}')
