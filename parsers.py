import csv
import os
import re
import threading
from calendar import monthrange
from datetime import datetime, timedelta
import win32
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
from bs4 import BeautifulSoup

headers = ['Имя партнера', 'Название акции', 'Дата начала', 'Дата окончания',
           'Условия акции', 'Купон', 'URL', 'Тип купона']
home_path = os.getenv('HOMEPATH')
actions_csv = os.path.join('C:\\', home_path, 'Desktop', "actions.csv")
actions_csv = os.path.normpath(actions_csv)


class Parsers:
    def __init__(self, gui):
        self.month_name = {"01": "янв", "02": "фев", "03": "мар", "04": "апр",
                           "05": "мая", "06": "июн", "07": "июл", "08": "авг",
                           "09": "сен", "10": "окт", "11": "ноя", "12": "дек", }

        self.generate_csv()
        self.actions_data = []
        self.gui = gui

    def generate_csv(self):

        with open(actions_csv, "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file, delimiter=";")
            writer.writerow(headers)

    def print_result(self, partner_name):
        for n, a in enumerate(self.actions_data, 1):
            self.gui.chat_print_signal.emit(f'---№{n}\n')
            action = ''
            for key, value in a.items():
                action = action + "".join('{:_<20}: {}\n'.format(key, value))
            self.gui.chat_print_signal.emit(action)
        self.gui.chat_print_signal.emit('*' * 60)
        self.gui.chat_print_signal.emit(f'Имя партнера: {partner_name}, загружено акций: {len(self.actions_data)}')
        self.gui.chat_print_signal.emit('*' * 60)
        self.gui.set_partner_name_signal.emit(partner_name)
        self.actions_data.clear()

    def get_one_date(self, text):
        try:
            text = re.sub(r'\xa0', ' ', text).strip()
            day, month, year = text.split(' ')
        except Exception:
            day, month = text.split(" ")
            year = datetime.now().year
        for num, name in self.month_name.items():
            if name in month.lower():
                month = num
        date = datetime(day=int(day), month=int(month), year=int(year)).strftime('%d.%m.%Y')
        return date

    def get_double_date(self, first, second):
        try:
            first = self.get_one_date(first)
        except Exception:
            first = datetime.now().strftime('%d.%m.%Y')
        try:
            second = self.get_one_date(second)
        except Exception:
            second = datetime.strptime(first, '%d.%m.%Y')
            day_on_month = monthrange(year=int(second.year), month=int(second.month))
            second = datetime(day=day_on_month[1], month=second.month, year=second.year).strftime('%d.%m.%Y')
        return first, second

    @win32.show_window
    def parser_sephora(self):
        """Сбор и форамтирование информации об акциях"""
        partner_name = 'Sephora'
        self.gui.chat_print_signal.emit(f'Загрузка {partner_name}')

        def get_date_with_year(self, div):
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
            self.gui.log.info(f'{link}')
            request = s.get(link)
            page = BeautifulSoup(request.text, 'lxml')
            div = page.find('div', class_='b-news-detailed')
            if div:
                try:
                    date_start, date_end = get_date_with_year(self, div)
                except TypeError:
                    self.gui.log.info('Не найдена дата проведения акции')
                    return
                code = "Не требуется"
                action_name = div.h1.text
                action_type = 'подарок' if 'подар' in action_name.lower() else 'скидка'
                paragraphs = div.findAll('p')
                url = 'https://sephora.ru/news/'

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
                    with open(actions_csv, "a", newline="", encoding="utf-8") as csv_file:
                        writer = csv.DictWriter(csv_file, fieldnames=headers, delimiter=";")
                        writer.writerow(action)
                self.print_result(partner_name)

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
    def parser_ildebote(self):
        self.gui.chat_print_signal.emit('Загрузка Иль Дэ Ботэ')
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
            action_type = 'подарок' if 'подарок' in action_name.lower() else 'скидка'
            code = 'Не требуется'
            action = {'Имя партнера': partner_name, 'Название акции': action_name, 'Дата начала': date_start,
                      'Дата окончания': date_end, 'Условия акции': desc,
                      'Купон': code, 'URL': url, 'Тип купона': action_type}
            self.actions_data.append(action)
            with open(actions_csv, "a", newline="", encoding="utf-8") as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=headers, delimiter=";")
                writer.writerow(action)
        self.print_result(partner_name)

    def parser_kupivip(self):

        partner_name = 'KupiVip'
        self.gui.chat_print_signal.emit(f'Загрузка {partner_name}')
        s = requests.Session()
        s.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'})
        main_url = 'https://www.kupivip.ru/campaigns?showIn=FEMALE&filter=ALL'
        request = s.get(main_url)
        page = BeautifulSoup(request.text, 'lxml')
        divs = page.find_all("div", attrs={'data-banner': 'campaign'})

        for div in divs:
            persent = ''
            desc = ''
            action_name = div.find("div", class_='brands').text.strip()
            try:
                persent = div.find("div", class_='percent').text.strip()
            except Exception:
                pass
            try:
                desc = div.find("div", class_='name').text.strip()
            except Exception:
                pass
            if persent:
                action_name += f'. Скидки до {persent}%'
            date_start = datetime.now().strftime('%d.%m.%Y')
            action_type = 'скидка'
            code = 'Не требуется'
            if 'промокод' in action_name.lower():
                code = re.search(r'код\s(.*)\s?', action_name).group(1)
                action_type = 'купон'
            url = 'https://www.kupivip.ru/'
            action = {'Имя партнера': partner_name, 'Название акции': action_name, 'Дата начала': date_start,
                      'Дата окончания': date_start, 'Условия акции': desc,
                      'Купон': code, 'URL': url, 'Тип купона': action_type}
            self.actions_data.append(action)
            with open(actions_csv, "a", newline="", encoding="utf-8") as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=headers, delimiter=";")
                writer.writerow(action)
        self.print_result(partner_name)

    def parser_akusherstvo(self):
        partner_name = 'Акушерство'
        self.gui.chat_print_signal.emit(f'Загрузка {partner_name}')
        self.gui.create_progress_bar(30)

        def run(div):
            persent = div.find("span", class_='banner-sale-list-item-discount-percent').text.strip()
            date_end = div.find("strong", class_='date').text.strip()
            incoming_date = re.search(r'до\s(.*)\s?', date_end.lower()).group(1)
            date_end = self.get_one_date(incoming_date)
            link = div.find('a').get('href')
            request = s.get(link)
            action_page = BeautifulSoup(request.text, 'lxml')
            action_name = action_page.h1.text.strip()
            descs = action_page.find('table', class_='centre_header')
            desc = ''
            action_type = 'скидка'
            code = 'Не требуется'
            action_name = f'Скидки {persent} на {action_name}'
            try:
                desc = descs.find_all('p')[0].text.strip()
                desc = re.sub(r'\n', '', desc)
                desc = re.sub(r'\r', '', desc)
            except Exception:
                self.gui.chat_print_signal.emit(f"Не удалось обработать описание для {action_name}")
            action = {'Имя партнера': partner_name, 'Название акции': action_name, 'Дата начала': date_start,
                      'Дата окончания': date_end, 'Условия акции': desc,
                      'Купон': code, 'URL': main_url, 'Тип купона': action_type}
            self.actions_data.append(action)
            with open(actions_csv, "a", newline="", encoding="utf-8") as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=headers, delimiter=";")
                writer.writerow(action)

        s = requests.Session()
        options = Options()
        options.add_argument('--disable-gpu')
        main_url = 'https://www.akusherstvo.ru/sale.php'
        driver = webdriver.Chrome(options=options)
        driver.get(main_url)
        page = BeautifulSoup(driver.page_source, 'lxml')
        driver.quit()
        divs = page.find_all("li", class_='banner-sale-list-item js-banner-sale-list-item')
        divs_2 = page.find_all('li', class_='banner-sale-list-item js-banner-sale-list-item middle')
        divs = divs + divs_2
        date_start = datetime.now().strftime('%d.%m.%Y')
        threads = [threading.Thread(target=run, args=(div,), daemon=True) for div in divs]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.print_result(partner_name)

    def parser_utkonos(self):
        partner_name = 'Утконос'
        self.gui.chat_print_signal.emit(f'Загрузка {partner_name}')
        s = requests.Session()
        s.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'})
        main_url = 'https://www.utkonos.ru/action'
        request = s.get(main_url)
        page = BeautifulSoup(request.text, 'lxml')
        divs = page.find_all("div", class_='action_wrapper')
        for div in divs:
            action_name = div.a.text.strip()
            code = 'Не требуется'
            action_type = 'скидка'
            url = 'https://www.utkonos.ru' + div.a.get('href')
            incoming_date = div.find('div', class_='text').text.strip()
            incoming_date = re.search(r'с\s(\d+\s[а-яА-Я]+).*по\s(\d+\s[а-яА-Я]+)', incoming_date.lower())
            date_start, date_end = self.get_double_date(incoming_date.group(1), incoming_date.group(2))
            action = {'Имя партнера': partner_name, 'Название акции': action_name, 'Дата начала': date_start,
                      'Дата окончания': date_end, 'Условия акции': '',
                      'Купон': code, 'URL': url, 'Тип купона': action_type}
            self.actions_data.append(action)
            with open(actions_csv, "a", newline="", encoding="utf-8") as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=headers, delimiter=";")
                writer.writerow(action)
        self.print_result(partner_name)

    # def parser_sportmaster(self):
    # https: // www.sportmaster.ru / news / 1781660 /?icid = home!w!button

    def parser_vseinstrumenti(self):
        partner_name = 'Все инструменты'
        self.gui.chat_print_signal.emit(f'Загрузка {partner_name}')
        options = Options()
        options.add_argument('--disable-gpu')
        main_url = 'https://www.vseinstrumenti.ru/our_actions/aktsii'
        driver = webdriver.Chrome(options=options)
        driver.get(main_url)
        page = BeautifulSoup(driver.page_source, 'lxml')
        driver.quit()
        divs = page.find_all("div", class_='action_main')
        for div in divs:
            action_name = div.find('div', class_='action_header').a.text.strip()
            code = 'Не требуется'
            action_type = 'скидка'
            url = 'https://www.vseinstrumenti.ru/our_actions/aktsii'
            desc = div.find('div', class_='act_descr').find_all('p')[3].text.strip()
            incoming_date = div.find('div', class_='act_descr').find_all('p')[0].text.strip()
            incoming_date = re.search(r'(\d.*)\–\s(.*)', incoming_date.lower())
            date_start, date_end = self.get_double_date(incoming_date.group(1), incoming_date.group(2))
            action = {'Имя партнера': partner_name, 'Название акции': action_name, 'Дата начала': date_start,
                      'Дата окончания': date_end, 'Условия акции': desc,
                      'Купон': code, 'URL': url, 'Тип купона': action_type}
            self.actions_data.append(action)
            with open(actions_csv, "a", newline="", encoding="utf-8") as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=headers, delimiter=";")
                writer.writerow(action)
        self.print_result(partner_name)
