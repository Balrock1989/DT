import threading
from multiprocessing import Process
from threading import Thread

import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException

from database.data_base import actions_exists_in_db_new
from helpers.Utils import Utils
from models.action import Action


class RivegaucheProcess(Process):

    def __init__(self, queue, ignore):
        super().__init__()
        self.queue = queue.queue
        self.ignore = ignore
        self.utils = Utils(self.queue)

    def __str__(self):
        return "Ривгош"

    def run(self):
        actions_data = []
        threads = []
        lock = threading.Lock()
        base_url = 'http://www.rivegauche.ru'
        main_url = f'https://rivegauche.ru/promotionslist'
        page = self.utils.ACTIONS_UTIL.get_page_use_webdriver(main_url, scroll=True, hidden=True)
        divs = page.select('.b-promo-item')
        for div in divs:
            action = Action(str(self))
            action.url = base_url + div.find('a').get('href')
            action.start = self.utils.DATE_UTIL.get_first_day_month()
            action.end = self.utils.DATE_UTIL.get_date_end_month()
            action.code = "Не требуется"
            action.short_desc = ''
            if self.utils.DATE_UTIL.promotion_is_outdated(action.end):
                self.queue.put('progress')
                continue
            threads.append(RivegaucheThread(actions_data, lock, self.queue, action, self.ignore, self.utils))
        self.queue.put(f'set {len(threads)}')
        self.utils.ACTIONS_UTIL.start_join_threads(threads)
        self.utils.CSV_UTIL.filling_queue(self.queue, actions_data, str(self))


class RivegaucheThread(Thread):

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
        try:
            request = s.get(self.action.url, timeout=3)
        except RequestException:
            self.queue.put('progress')
            return
        page = BeautifulSoup(request.text, 'lxml')
        self.action.name = page.select_one(
            '[data-smartedit-component-id="ngVerticalCategoryMenuComponent"] .b-label__title').text.strip()
        self.action.desc = self.action.name
        self.action.action_type = self.utils.ACTIONS_UTIL.check_action_type(self.action)
        if not self.ignore:
            with self.lock:
                if actions_exists_in_db_new(self.action):
                    self.queue.put('progress')
                    return
        with self.lock:
            self.actions_data.append(self.utils.ACTIONS_UTIL.generate_action(self.action))
            self.queue.put('progress')
