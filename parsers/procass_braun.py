import re
from multiprocessing import Process

import helpers.helper as helper
from database.data_base import actions_exists_in_db


class Braun_process(Process):

    def __init__(self, queue, ignore):
        super().__init__()
        self.queue = queue.queue
        self.ignore = ignore
        self.link_selector = '.imageBlock a'

    def __str__(self):
        return "Braun"

    def run(self):
        partner_name = 'Braun'
        actions_data = []
        base_url = 'https://braun-russia.ru'
        page = helper.get_page_use_request('https://braun-russia.ru/actions')
        divs = page.select('.bm2-cat-item')
        self.queue.put(f'set {len(divs)}')
        for div in divs:
            if div.select_one(self.link_selector) is None:
                continue
            url = div.select_one(self.link_selector).get('href').strip()
            if 'http' not in url:
                url = base_url + url
            name = div.select_one(self.link_selector).get('title').strip()
            try:
                date = div.select_one('.daysleft').text.strip()
                date_end_action = re.search(r'(\d+)', date)
                start = helper.DATA_NOW
                end = helper.get_date_plus_days(int(date_end_action.group(1)))
            except AttributeError:
                start, end = helper.get_date_now_to_end_month()
            desc = div.select_one('.teaser').text.strip()
            if 'промокод' in name.lower():
                try:
                    code = re.search(r'([A-Z0-9]+)', name).group(1)
                except AttributeError:
                    code = 'Не требуется'
            else:
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
