import re
from multiprocessing import Process

import helpers.helper as helper
from database.data_base import actions_exists_in_db


class Thomas_process(Process):

    def __init__(self, queue, ignore):
        super().__init__()
        self.queue = queue.queue
        self.ignore = ignore

    def __str__(self):
        return "Thomas"

    def run(self):
        partner_name = 'Thomas'
        actions_data = []
        base_url = 'https://thomas-muenz.ru'
        self.queue.put(f'set 2')
        for i in range(1, 3):
            main_url = f'https://thomas-muenz.ru/actions/?PAGEN_1={i}'
            page = helper.get_page_use_request(main_url)
            divs = page.select('.promo-list__item')
            for div in divs:
                url = base_url + div.select_one('h2 a.link').get('href')
                name = div.select_one('h2 a.link').text.strip()
                date = div.select_one('.promo-alt-card__footer').text.strip()
                date = re.split(r' по ', date.lower())
                if len(date) > 1:
                    start, end = helper.get_double_date(date[0].strip(), date[1].strip())
                elif len(date) == 1:
                    start, end = helper.get_start_date_in_date(date[0], True)
                else:
                    start, end = helper.get_date_now_to_end_month()
                code = "Не требуется"
                desc = div.select_one('.promo-alt-card__text').text.strip()
                short_desc = ''
                action_type = helper.check_action_type(code, name, desc)
                if helper.promotion_is_outdated(end):
                    continue
                if not self.ignore:
                    if actions_exists_in_db(partner_name, name, start, end):
                        continue
                action = helper.generate_action(partner_name, name, start, end, desc, code, url, action_type,
                                                short_desc)
                actions_data.append(action)
            self.queue.put('progress')
        helper.filling_queue(self.queue, actions_data, partner_name)
