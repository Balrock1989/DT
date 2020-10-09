import re
import threading
from pprint import pprint

import requests
from bs4 import BeautifulSoup
from threading import Thread
from multiprocessing import Process
import helpers.helper as helper
from database.data_base import actions_exists_in_db


class Respublica_process(Process):

    def __init__(self, queue, ignore):
        super().__init__()
        self.queue = queue.queue
        self.ignore = ignore

    def __str__(self):
        return "Республика"

    def run(self):
        partner_name = 'Республика'
        actions_data = []
        lock = threading.Lock()
        main_url = 'https://www.respublica.ru/promotions'
        page = helper.get_page_use_request(main_url)
        divs = page.find_all('div', class_='rd-promo-item')
        divs_work = []
        links = []
        for div in divs:
            if div.find('a', text='Подробнее'):
                divs_work.append(div)
        for div in divs_work:
            links.append('https://www.respublica.ru/' + div.find('a', text='Подробнее').get('href'))
        threads = [Respulica_thread(actions_data, link, lock, self.ignore, self.queue) for link in links]
        self.queue.put(f'set {len(threads)}')
        helper.start_join_threads(threads)
        helper.filling_queue(self.queue, actions_data, partner_name)


class Respulica_thread(Thread):

    def __init__(self, actions_data, link, lock, ignore, queue):
        super().__init__()
        self.actions_data = actions_data
        self.link = link
        self.lock = lock
        self.queue = queue
        self.ignore = ignore

    def run(self):
        partner_name = 'Республика'
        page = helper.get_page_use_request(self.link)
        common_block = page.findAll('div')[14]
        test = re.sub(r'(?s)<script>.*?</script>', '',  str(common_block))
        page2 = BeautifulSoup(test, 'lxml')
        name = page2.find('div', class_='rd-promo-show_col-right').h1.text.strip()
        short_desc = page2.find('div', class_='rd-promo-show_title').text.strip()
        desc = page2.find('div', class_='rd-promo-show_text').text.strip()
        desc = re.sub(r'\s{2,}', ' ', desc).strip()
        code = "Не требуется"
        try:
            start, end = helper.search_data_in_text(short_desc)
        except:
            start = helper.DATA_NOW
            end = helper.get_date_end_month()
        action_type = helper.check_action_type(code, name, desc)
        if helper.promotion_is_outdated(end):
            self.queue.put('progress')
            return
        if not self.ignore:
            with self.lock:
                if actions_exists_in_db(partner_name, name, start, end):
                    self.queue.put('progress')
                    return
        action = helper.generate_action(partner_name, name, start, end, desc, code, self.link, action_type, short_desc)
        with self.lock:
            self.actions_data.append(action)
            self.queue.put('progress')

