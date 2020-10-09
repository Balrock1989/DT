import re
import threading
from multiprocessing import Process

import helpers.helper as helper
from database.data_base import actions_exists_in_db


class Holodilnik_process(Process):

    def __init__(self, queue, ignore):
        super().__init__()
        self.queue = queue.queue
        self.ignore = ignore

    def __str__(self):
        return "Холодильник"

    def run(self):
        partner_name = 'Холодильник'
        actions_data = []
        page = helper.get_page_use_request('https://ulyanovsk.holodilnik.ru/action/')
        divs = page.find_all("div", class_='col-4')
        begin_url = 'https://holodilnik.ru'
        self.queue.put(f'set {len(divs)}')
        for div in divs:
            url = begin_url + div.a.get('href').strip()
            name = div.find('span', class_='link').text.strip()
            date = div.find('span', class_='text-data').text.strip()
            date = date.split(' - ')
            if len(date[0]) > 1:
                start = re.search(r'(\d+\.\d+\.\d+)', date[0]).group(1)
            else:
                print(f'{name} нет даты date')
                self.queue.put('progress')
                continue
            if len(date) == 2:
                end = re.search(r'(\d+\.\d+\.\d+)', date[1]).group(1)
            else:
                end = helper.get_date_month_ahead(start)
            desc = name
            code = 'Не требуется'
            short_desc = ''
            action_type = helper.check_action_type(code, name, desc)
            if helper.promotion_is_outdated(end):
                self.queue.put('progress')
                continue
            if not self.ignore:
                if actions_exists_in_db(partner_name, name, start, end):
                    self.queue.put('progress')
                    continue
            action = helper.generate_action(partner_name, name, start, end, desc, code, url, action_type, short_desc)
            actions_data.append(action)
            self.queue.put('progress')
        helper.filling_queue(self.queue, actions_data, partner_name)
