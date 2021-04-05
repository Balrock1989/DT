import threading
from multiprocessing import Process

import helpers.helper as helper
from database.data_base import actions_exists_in_db


class Book_process(Process):

    def __init__(self, queue, ignore):
        super().__init__()
        self.queue = queue.queue
        self.ignore = ignore

    def __str__(self):
        return "Book24"

    def run(self):
        partner_name = 'Book24'
        actions_data = []
        lock = threading.Lock()
        page = helper.get_page_use_webdriver('https://book24.ru/sales/', scroll=True, hidden=True)
        begin_url = 'https://book24.ru'
        divs = page.find_all('div', class_='stock-list-item__container')
        self.queue.put(f'set {len(divs)}')
        for div in divs:
            if not div.find('div', class_='stock-list-item__countdown'):
                self.queue.put('progress')
                continue
            name = div.find('p', class_='stock-list-item__title').text.strip()
            date = div.find('span', class_='info-list__text').text.strip() \
                if len(div.findAll('div', class_='info-list__item')) < 2 \
                else div.findAll('span', class_='info-list__text')[1].text.strip()
            start, end = helper.get_do_period(date)
            desc = div.find('div', class_='stock-list-item__desc').text.strip() \
                if div.find('div', class_='stock-list-item__desc') else name
            url = begin_url + div.find("div", class_='stock-list-item__more').a.get('href')
            code = 'Не требуется'
            if helper.promotion_is_outdated(end):
                self.queue.put('progress')
                continue
            short_desc = ''
            action_type = helper.check_action_type(code, name, desc)
            if not self.ignore:
                with lock:
                    if actions_exists_in_db(partner_name, name, start, end):
                        self.queue.put('progress')
                        continue
            action = helper.generate_action(partner_name, name, start, end, desc, code, url, action_type, short_desc)
            actions_data.append(action)
            self.queue.put('progress')
        helper.filling_queue(self.queue, actions_data, partner_name)
