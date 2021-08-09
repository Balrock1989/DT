import threading
from datetime import datetime, timedelta
from multiprocessing import Process
import helpers.helper as helper
from database.data_base import actions_exists_in_db


class IldeboteProcess(Process):
    def __init__(self, queue, ignore):
        super().__init__()
        self.queue = queue.queue
        self.ignore = ignore

    def __str__(self):
        return "ИльДэБотэ"

    def run(self):
        partner_name = 'ИльДэБотэ'
        actions_data = []
        lock = threading.Lock()
        url = 'https://iledebeaute.ru/company/actions'
        page = helper.get_page_use_request(url)
        divs = page.find_all("div", class_='news_block')
        self.queue.put(f'set {len(divs)}')
        for div in divs:
            name = div.h2.text
            try:
                start = helper.get_start_date_in_date(div.find("p", class_='date').text.strip(), False)
            except Exception:
                start = helper.DATA_NOW
            end = (datetime.now() + timedelta(days=3)).strftime('%d.%m.%Y')
            desc = div.find("p", class_='desc').text.strip()
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
