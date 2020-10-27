import threading
from multiprocessing import Process
from threading import Thread

import helpers.helper as helper
from database.data_base import actions_exists_in_db


class Mts_process(Process):

    def __init__(self, queue, ignore):
        super().__init__()
        self.queue = queue.queue
        self.ignore = ignore

    def __str__(self):
        return "МТС"

    def run(self):
        partner_name = 'МТС'
        lock = threading.Lock()
        actions_data = []
        base_url = 'https://shop.mts.ru'
        threads = []
        for i in range(1, 4):
            main_url = f'https://shop.mts.ru/actions/{i}/'
            try:
                page = helper.get_page_use_request(main_url)
            except:
                continue
            divs = page.find_all('div', class_='news-block')
            for div in divs:
                threads.append(Holodilnik_thread(actions_data, lock, self.queue, base_url + div.find('a').get('href'),
                                                 self.ignore))
        self.queue.put(f'set {len(threads)}')
        helper.start_join_threads(threads)
        helper.filling_queue(self.queue, actions_data, partner_name)


class Holodilnik_thread(Thread):

    def __init__(self, actions_data, lock, queue, url, ignore):
        super().__init__()
        self.actions_data = actions_data
        self.lock = lock
        self.queue = queue
        self.url = url
        self.ignore = ignore

    def run(self):
        partner_name = 'МТС'
        page = helper.get_page_use_request(self.url)
        name = page.h1.text.strip()
        try:
            data_text = page.find_all('div', class_='wrapper')[0].find('p').text.strip()
            start, end = helper.search_data_in_text(data_text)
        except:
            start, end = helper.get_date_now_to_end_month()
        desc = name
        code = 'Не требуется'
        short_desc = ''
        action_type = helper.check_action_type(code, name, desc)
        if helper.promotion_is_outdated(end):
            self.queue.put('progress')
            return
        if not self.ignore:
            if actions_exists_in_db(partner_name, name, start, end):
                self.queue.put('progress')
                return
        action = helper.generate_action(partner_name, name, start, end, desc, code, self.url, action_type,short_desc)
        with self.lock:
            self.actions_data.append(action)
            self.queue.put('progress')
