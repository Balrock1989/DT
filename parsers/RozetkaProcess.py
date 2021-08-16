import re
from multiprocessing import Process

import requests
from bs4 import BeautifulSoup

from database.DataBase import actions_exists_in_db_new
from helpers.Utils import Utils
from models.Action import Action


class RozetkaProcess(Process):

    def __init__(self, queue, ignore):
        super().__init__()
        self.queue = queue.queue
        self.ignore = ignore
        self.count_page = 20
        self.utils = Utils(self.queue)

    def __str__(self):
        return "Розетка"

    def run(self):
        actions_data = []
        self.queue.put(f'set {self.count_page}')
        s = requests.Session()
        cookie = s.get('https://rozetka.com.ua/news-articles-promotions/promotions/').request.headers.get(
            'cookie')
        # .replace('slang=ua', 'slang=ru')
        s.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
            'Cookie': cookie
        })
        s.cookies.set('slang', 'ru')
        for i in range(1, self.count_page + 1):
            main_url = f'https://rozetka.com.ua/news-articles-promotions/promotions/page={i}/'
            request = s.get(main_url)
            page = BeautifulSoup(request.text, 'lxml')
            divs = page.find_all('li', class_='promo-grid__cell')
            for div in divs:
                if div.get('name') == 'more_promotions':
                    continue
                action = Action(str(self))
                action.url = div.find('a').get('href')
                action.name = div.find('img', class_='promo-tile__picture').get('title').strip()
                try:
                    date = div.find('time', class_='promo-tile__period').text.strip()
                    date = re.sub(r'\xa0', ' ', date).strip()
                    date = date.split('—')
                    action.start = self.utils.DATE_UTIL.get_one_date(date[0])
                    action.end = self.utils.DATE_UTIL.get_one_date(date[1])
                except:
                    action.start, action.end = self.utils.DATE_UTIL.get_date_now_to_end_month()
                action.code = "Не требуется"
                action.desc = action.name
                action.short_desc = ''
                action.action_type = self.utils.ACTIONS_UTIL.check_action_type(action)
                if self.utils.DATE_UTIL.promotion_is_outdated(action.end):
                    continue
                if not self.ignore:
                    if actions_exists_in_db_new(action):
                        continue
                actions_data.append(self.utils.ACTIONS_UTIL.generate_action(action))
            self.queue.put('progress')
        self.utils.CSV_UTIL.filling_queue(self.queue, actions_data, str(self))
