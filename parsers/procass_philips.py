import re
from multiprocessing import Process

import helpers.helper as helper
from database.data_base import actions_exists_in_db


class Philips_process(Process):

    def __init__(self, queue, ignore):
        super().__init__()
        self.queue = queue.queue
        self.ignore = ignore

    def __str__(self):
        return "Philips"

    def run(self):
        partner_name = 'Philips'
        actions_data = []
        page = helper.get_page_use_request('https://www.shop.philips.ru/hot_offers')
        divs = page.find_all("div", class_='col-md-4')
        self.queue.put(f'set {len(divs)}')
        for div in divs:
            url = div.a.get('href').strip()
            name = div.find('div', class_='title').text.strip()
            try:
                date = div.find('span', class_='date-format').text.strip()
                date = re.search(r'(\d+)\/(\d+)\/(\d+)', date)
                start = helper.DATA_NOW
                end = f'{date.group(3)}.{date.group(2)}.{date.group(1)}'
            except AttributeError:
                start = helper.get_first_day_month()
                end = helper.get_date_end_month()
            desc = name
            code = 'Не требуется'
            short_desc = ''
            action_type = div.find('div', class_='caption').text.strip()
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
