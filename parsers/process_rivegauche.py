import threading
from multiprocessing import Process
from threading import Thread

import requests
from bs4 import BeautifulSoup

import helpers.helper as helper
from database.data_base import actions_exists_in_db
from models.action import Action


class RivegaucheProcess(Process):

    def __init__(self, queue, ignore):
        super().__init__()
        self.queue = queue.queue
        self.ignore = ignore

    def __str__(self):
        return "Ривгош"

    def run(self):
        partner_name = 'Ривгош'
        actions_data = []
        threads = []
        lock = threading.Lock()
        base_url = 'http://www.rivegauche.ru'
        main_url = f'https://rivegauche.ru/promotionslist'
        page = helper.get_page_use_webdriver(main_url, scroll=True, hidden=True)
        divs = page.select('.b-promo-item')
        for div in divs:
            action = Action(partner_name)
            action.url = base_url + div.find('a').get('href')
            action.start = helper.get_first_day_month()
            action.end = helper.get_date_end_month()
            action.code = "Не требуется"
            action.short_desc = ''
            if helper.promotion_is_outdated(action.end):
                self.queue.put('progress')
                continue
            threads.append(RivegaucheThread(actions_data, lock, self.queue, action, self.ignore))
        self.queue.put(f'set {len(threads)}')
        helper.start_join_threads(threads)
        helper.filling_queue(self.queue, actions_data, partner_name)


class RivegaucheThread(Thread):

    def __init__(self, actions_data, lock, queue, action, ignore):
        super().__init__()
        self.actions_data = actions_data
        self.lock = lock
        self.queue = queue
        self.action = action
        self.ignore = ignore

    def run(self):
        s = requests.Session()
        s.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0'}
        try:
            request = s.get(self.action.url, timeout=3)
        except Exception:
            self.queue.put('progress')
            return
        page = BeautifulSoup(request.text, 'lxml')
        self.action.name = page.select_one(
            '[data-smartedit-component-id="ngVerticalCategoryMenuComponent"] .b-label__title').text.strip()
        self.action.desc = self.action.name
        self.action.action_type = helper.check_action_type(self.action.code, self.action.name, self.action.desc)
        if not self.ignore:
            with self.lock:
                if actions_exists_in_db(self.action.partner_name, self.action.name, self.action.start, self.action.end):
                    self.queue.put('progress')
                    return
        action = helper.generate_action_new(self.action)
        with self.lock:
            self.actions_data.append(action)
            self.queue.put('progress')
