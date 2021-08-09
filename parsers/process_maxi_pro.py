import threading
from datetime import datetime, timedelta
from multiprocessing import Process
import helpers.helper as helper
from database.data_base import actions_exists_in_db


class MaxiProProcess(Process):
    def __init__(self, queue, ignore):
        super().__init__()
        self.queue = queue.queue
        self.ignore = ignore

    def __str__(self):
        return "МаксиПро"

    def run(self):
        partner_name = 'МаксиПро'
        actions_data = []
        lock = threading.Lock()
        main_url = 'https://maxipro.ru/sales/'
        base_url = 'https://maxipro.ru'
        page = helper.get_page_use_request(main_url)
        divs = page.find_all("div", class_='sale-card-wrapper')
        self.queue.put(f'set {len(divs)}')
        for div in divs:
            url = base_url + div.find("a").get('href')
            name = div.find("div", class_='sale-card-title').text.strip()
            desc = div.find("div", class_='sale-card-text d-none d-md-block').text.strip()
            try:
                date = div.find("div", class_='sale-card-text -grey-').text.strip()
                start, end = helper.search_data_in_text_without_year(date)
            except AttributeError:
                start = helper.DATA_NOW
                end = helper.get_date_plus_days(30)
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
