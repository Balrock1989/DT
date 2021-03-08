import re
from multiprocessing import Process

import requests
from bs4 import BeautifulSoup

import helpers.helper as helper
from database.data_base import actions_exists_in_db


class Rozetka_process(Process):

    def __init__(self, queue, ignore):
        super().__init__()
        self.queue = queue.queue
        self.ignore = ignore

    def __str__(self):
        return "Розетка"

    def run(self):
        partner_name = 'Розетка'
        actions_data = []
        self.queue.put(f'set 20')
        s = requests.Session()
        cookie = s.get('https://rozetka.com.ua/news-articles-promotions/promotions/').request.headers.get(
            'cookie').replace('slang=ua', 'slang=ru')
        s.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
            'Cookie': cookie
        })
        s.cookies.set('slang', 'ru')
        for i in range(1, 21):
            main_url = f'https://rozetka.com.ua/news-articles-promotions/promotions/page={i}/'
            request = s.get(main_url)
            page = BeautifulSoup(request.text, 'lxml')
            divs = page.find_all('li', class_='promo-grid__cell')
            for div in divs:
                if div.get('name') == 'more_promotions':
                    continue
                url = div.find('a').get('href')
                name = div.find('img', class_='promo-tile__picture').get('title').strip()
                try:
                    date = div.find('time', class_='promo-tile__period').text.strip()
                    date = re.sub(r'\xa0', ' ', date).strip()
                    date = date.split('—')
                    start =helper.get_one_date(date[0])
                    end = helper.get_one_date(date[1])
                except:
                    start, end = helper.get_date_now_to_end_month()
                code = "Не требуется"
                desc = name
                short_desc = ''
                action_type = helper.check_action_type(code, name, desc)
                if helper.promotion_is_outdated(end):
                    continue
                if not self.ignore:
                    if actions_exists_in_db(partner_name, name, start, end):
                        continue
                action = helper.generate_action(partner_name, name, start, end, desc, code, url, action_type, short_desc)
                actions_data.append(action)
            self.queue.put('progress')
        helper.filling_queue(self.queue, actions_data, partner_name)
