import threading
from datetime import datetime, timedelta
from multiprocessing import Process
import helpers.helper as helper
from database.data_base import actions_exists_in_db


class Santehnika_tut_process(Process):
    def __init__(self, queue, ignore):
        super().__init__()
        self.queue = queue.queue
        self.ignore = ignore

    def __str__(self):
        return 'СантехникаТут'

    def run(self):
        partner_name = 'СантехникаТут'
        actions_data = []
        lock = threading.Lock()
        self.queue.put(f'set 2')
        for i in range(1, 3):
            main_url = f'https://santehnika-tut.ru/actions/page-{i}.html'
            page = helper.get_page_use_request(main_url)
            divs = page.find_all('div', class_='col-xs-12 col-sm-6 col-md-3')
            self.queue.put(f'set {len(divs)}')
            for div in divs:
                try:
                    name = div.find('span', class_='title').text.strip()
                except Exception:
                    continue
                url = 'https://santehnika-tut.ru' + div.find('a').get('href')
                try:
                    start, end = helper.get_do_period(div.find('span', class_='date').text.strip())
                except Exception:
                    start = helper.DATA_NOW
                    end = helper.get_date_end_month()
                desc = name
                code = 'Не требуется'
                if helper.promotion_is_outdated(end):
                    continue
                short_desc = ''
                action_type = helper.check_action_type(code, name, desc)
                if not self.ignore:
                    with lock:
                        if actions_exists_in_db(partner_name, name, start, end):
                            continue
                action = helper.generate_action(partner_name, name, start, end, desc, code, url, action_type, short_desc)
                actions_data.append(action)
            self.queue.put('progress')
        helper.filling_queue(self.queue, actions_data, partner_name)
