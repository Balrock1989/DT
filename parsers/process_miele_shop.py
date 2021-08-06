import threading
from multiprocessing import Process
from threading import Thread

import requests
from bs4 import BeautifulSoup

import helpers.helper as helper
from database.data_base import actions_exists_in_db
from models.action import Action


class MieleProcess(Process):

    def __init__(self, queue, ignore):
        super().__init__()
        self.queue = queue.queue
        self.ignore = ignore
        self.count_page = 2
        self.link_selector = '.SpecialOfferPreview-media a'

    def __str__(self):
        return "Miele-shop"

    def run(self):
        partner_name = 'Miele-shop'
        actions_data = []
        threads = []
        lock = threading.Lock()
        base_url = 'https://www.miele-shop.ru'
        self.queue.put(f'set {self.count_page}')
        for i in range(1, self.count_page + 1):
            main_url = f'https://www.miele-shop.ru/news/special/?PAGEN_1={i}'
            page = helper.get_page_use_request(main_url)
            divs = page.select('.preview-full__container')
            for div in divs:
                action = Action(partner_name)
                action.url = base_url + div.select_one('a.preview-full__wrap').get('href')
                action.name = div.select_one('.preview-full__title').text.strip()
                action.code = "Не требуется"
                action.desc = div.select_one('.preview-full__text').text.strip()
                action.short_desc = ''
                action.action_type = helper.check_action_type(action.code, action.name, action.desc)
                threads.append(MieleThread(actions_data, lock, self.queue, action, self.ignore))
            self.queue.put(f'set {len(threads)}')
            helper.start_join_threads(threads)
            helper.filling_queue(self.queue, actions_data, partner_name)


class MieleThread(Thread):

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
        self.action.start, self.action.end = helper.convert_list_to_date(
            helper.get_range_date(page.select_one('.content').text.strip()))
        if helper.promotion_is_outdated(self.action.end):
            self.queue.put('progress')
            return
        if not self.ignore:
            with self.lock:
                if actions_exists_in_db(self.action.partner_name, self.action.name, self.action.start,
                                        self.action.end):
                    self.queue.put('progress')
                    return
        action = helper.generate_action_new(self.action)
        with self.lock:
            self.actions_data.append(action)
            self.queue.put('progress')
