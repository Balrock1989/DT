import re
import threading
from multiprocessing import Process
import helpers.helper as helper
from database.data_base import *


class Utkonos_process(Process):
    def __init__(self, queue, ignore):
        super().__init__()
        self.queue = queue.queue
        self.ignore = ignore

    def __str__(self):
        return "Утконос"

    def run(self):
        partner_name = 'Утконос'
        actions_data = []
        lock = threading.Lock()
        page = helper.get_page_use_request('https://www.utkonos.ru/action')
        divs = page.find_all("utk-action-list-item")
        self.queue.put(f'set {len(divs)}')
        for div in divs:
            try:
                name = div.find('div', class_='template__content-text').text.strip()
            except AttributeError as exc:
                self.queue.put(f'{exc}')
                print('')
                continue
            code = 'Не требуется'
            desc = ''
            url = 'https://www.utkonos.ru' + div.a.get('href')
            try:
                incoming_date = div.find('div', class_='template__content-status').text.strip()
            except:
                incoming_date = ''
            if incoming_date != '':
                if "остал" in incoming_date.lower():
                    days = re.search(r'(\d+)', incoming_date.lower()).group(1)
                    start = helper.DATA_NOW
                    end = helper.get_date_plus_days(int(days))
                else:
                    start, end = helper.get_do_period(incoming_date)
            else:
                start, end = helper.get_date_now_to_end_month()
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
