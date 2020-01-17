import re
from calendar import monthrange
from datetime import datetime
import requests
from bs4 import BeautifulSoup


class Parsers:
    def __init__(self):
        self.month_name = {"01": "янв", "02": "фев", "03": "мар", "04": "апр",
                           "05": "мая", "06": "июн", "07": "июл", "08": "авг",
                           "09": "сен", "10": "окт", "11": "ноя", "12": "дек", }

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
                    print(f'Заголовок: {action_name}')
                    print(f'Начало акции: {date_start}')
                    print(f'Окончание акции: {date_end}')
                    print(f'Полное описание: {desc}')
                    print(f'Короткое описание: {action_name}')
                    print(f'Купон: {code}')
                    print(f'URL: https://sephora.ru')
                    print(f'Тип акции: {action_type}')
        gui.chat_print('\nДанные об акциях успешно загружены')
        # TODO подготовить вывод результатов для запись в таблицу csv