import csv
import re
import threading
from calendar import monthrange
from datetime import datetime, timedelta
import win32

import requests
from bs4 import BeautifulSoup

headers = ['Имя партнера', 'Название акции', 'Дата начала', 'Дата окончания',
           'Условия акции', 'Купон', 'URL', 'Тип купона']


class Parsers:
    def __init__(self):
        self.month_name = {"01": "янв", "02": "фев", "03": "мар", "04": "апр",
                           "05": "мая", "06": "июн", "07": "июл", "08": "авг",
                           "09": "сен", "10": "окт", "11": "ноя", "12": "дек", }

        self.generate_csv()
        self.actions_data = []

    def generate_csv(self):
        with open("actions.csv", "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file, delimiter=";")
            writer.writerow(headers)

    def print_result(self, gui, partner_name):
        for n, a in enumerate(self.actions_data, 1):
            gui.chat_print_signal.emit(f'---№{n}\n')
            action = ''
            for key, value in a.items():
                action = action + "".join('{:_<20}: {}\n'.format(key, value))
            gui.chat_print_signal.emit(action)
        gui.chat_print_signal.emit('*' * 60)
        gui.chat_print_signal.emit(f'Имя партнера: {partner_name}, загружено акций: {len(self.actions_data)}')
        gui.chat_print_signal.emit('*' * 60)
        gui.set_partner_name_signal.emit(partner_name)
        self.actions_data.clear()

    @win32.show_window
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

        def run(link):
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
                    return
                code = "Не требуется"
                action_type = 'подарок'
                action_name = div.h1.text
                paragraphs = div.findAll('p')
                url = 'https://sephora.ru/news/'
                partner_name = 'Sephora'
                descriptions = []
                for p in paragraphs:
                    text = p.text.strip()
                    if 'При' in text:
                        descriptions.append(text)
                for desc in descriptions:
                    action = {'Имя партнера': partner_name, 'Название акции': action_name, 'Дата начала': date_start,
                              'Дата окончания': date_end, 'Условия акции': desc,
                              'Купон': code, 'URL': url, 'Тип купона': action_type}
                    self.actions_data.append(action)
                    with open("actions.csv", "a", newline="", encoding="utf-8") as csv_file:
                        writer = csv.DictWriter(csv_file, fieldnames=headers, delimiter=";")
                        writer.writerow(action)
                self.print_result(gui, partner_name)

        s = requests.Session()
        s.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'})
        main_url = 'https://sephora.ru/news/'
        request = s.get(main_url)
        page = BeautifulSoup(request.text, 'lxml')
        links = page.find_all("a", class_='b-news-thumb__title')

        for link in links:
            threading.Thread(target=run, args=(link,), daemon=True).start()

    @win32.show_window
    def parser_ildebote(self, gui):
        s = requests.Session()
        s.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'})
        url = 'https://iledebeaute.ru/company/actions/'
        request = s.get(url)
        page = BeautifulSoup(request.text, 'lxml')
        divs = page.find_all("div", class_='news_block')
        partner_name = ''
        for div in divs:
            date = div.find("p", class_='date')
            if 'сегодня' not in date.text.strip().lower():
                continue
            partner_name = date.text.split('|')[1].strip()
            action_name = div.h2.text
            date_start = datetime.now().strftime('%d.%m.%Y')
            date_end = (datetime.now() + timedelta(days=3)).strftime('%d.%m.%Y')
            desc = div.find("p", class_='desc').text.strip()
            action_type = 'скидка'
            code = 'Не требуется'
            action = {'Имя партнера': partner_name, 'Название акции': action_name, 'Дата начала': date_start,
                      'Дата окончания': date_end, 'Условия акции': desc,
                      'Купон': code, 'URL': url, 'Тип купона': action_type}
            self.actions_data.append(action)
            with open("actions.csv", "a", newline="", encoding="utf-8") as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=headers, delimiter=";")
                writer.writerow(action)
        self.print_result(gui, partner_name)

