import re
import threading
from multiprocessing import Process
from threading import Thread

import requests
from bs4 import BeautifulSoup

from database.data_base import actions_exists_in_db_new
from helpers.Utils import Utils
from models.action import Action


class KolesadaromProcess(Process):

    def __init__(self, queue, ignore):
        super().__init__()
        self.queue = queue.queue
        self.ignore = ignore
        self.utils = Utils(self.queue)

    def __str__(self):
        return "Колеса Даром"

    def run(self):
        actions_data = []
        lock = threading.Lock()
        page = self.utils.ACTIONS_UTIL.get_page_use_webdriver('https://www.kolesa-darom.ru/actions/', hidden=True)
        divs = page.find_all("div", class_='tiles__item-inner')
        threads = []
        for div in divs:
            action = Action(str(self))
            begin_url = 'https://www.kolesa-darom.ru'
            action.name = div.find('a', class_='tiles__link').text.strip()
            action.url = begin_url + div.find('a', class_='tiles__link').get('href')
            try:
                period = div.find('div', class_='tiles__period-date').text.strip()
                action.end = self.utils.DATE_UTIL.get_one_date(period)
            except AttributeError:
                action.end = self.utils.DATE_UTIL.get_date_half_year_ahead(self.utils.DATE_UTIL.DATA_NOW)
            threads.append(KolesadaromThread(actions_data, lock, self.queue, action, self.ignore, self.utils))
        self.queue.put(f'set {len(threads)}')
        self.utils.ACTIONS_UTIL.start_join_threads(threads)
        self.utils.CSV_UTIL.filling_queue(self.queue, actions_data, str(self))


class KolesadaromThread(Thread):

    def __init__(self, actions_data, lock, queue, action, ignore, utils):
        super().__init__()
        self.actions_data = actions_data
        self.lock = lock
        self.queue = queue
        self.action = action
        self.ignore = ignore
        self.utils = utils

    def run(self):
        s = requests.Session()
        s.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0'}
        request = s.get(self.action.url)
        page = BeautifulSoup(request.text, 'lxml')
        main_div = page.find('div', class_='article-tiles')
        try:
            self.action.desc = main_div.find('div', class_=False).find_all('p')
            self.action.desc = self.action.desc[0].text.strip() + self.action.desc[1].text.strip()
        except IndexError:
            self.action.desc = main_div.find('div', class_=False).find_all('p')
            if self.action.desc:
                self.action.desc = self.action.desc[0].text.strip()[:300]
            else:
                self.action.desc = main_div.find('div', class_=False).text.strip()[:300]
        self.action.desc = re.sub(r'\s{2,}', ' ', self.action.desc).strip()
        self.action.desc = re.sub(r'\xa0', '\n', self.action.desc).strip()
        self.action.desc = re.sub(r'&nbsp;', ' ', self.action.desc).strip()
        self.action.start = self.utils.DATE_UTIL.DATA_NOW
        self.action.code = 'Не требуется'
        if self.utils.DATE_UTIL.promotion_is_outdated(self.action.end):
            self.queue.put('progress')
            return
        self.action.short_desc = ''
        self.action.action_type = self.utils.ACTIONS_UTIL.check_action_type(self.action)
        if not self.ignore:
            with self.lock:
                if actions_exists_in_db_new(self.action):
                    self.queue.put('progress')
                    return
        with self.lock:
            self.actions_data.append(self.utils.ACTIONS_UTIL.generate_action(self.action))
            self.queue.put('progress')
