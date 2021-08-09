from multiprocessing import Process

import helpers.helper as helper
from database.data_base import actions_exists_in_db


class DomovoyProcess(Process):

    def __init__(self, queue, ignore):
        super().__init__()
        self.queue = queue.queue
        self.ignore = ignore

    def __str__(self):
        return "Домовой"

    def run(self):
        partner_name = 'Домовой'
        actions_data = []
        base_url = 'https://tddomovoy.ru/actions'
        self.queue.put(f'set 3')
        for i in range(1, 4):
            main_url = f'https://tddomovoy.ru/actions/?PAGEN_1={i}'
            page = helper.get_page_use_request(main_url)
            divs = page.select('.bx_news li')
            for div in divs:
                url = base_url + div.find('a').get('href')
                name = div.find('img').get('title').strip()
                try:
                    date = div.find('div', class_='date').text.strip()
                    start, end = helper.convert_list_to_date(helper.get_range_date(date))
                except:
                    start, end = helper.get_date_now_to_end_month()
                code = "Не требуется"
                try:
                    desc = div.find('div', class_='text').text.strip()
                except:
                    desc = name
                short_desc = ''
                action_type = helper.check_action_type(code, name, desc)
                if helper.promotion_is_outdated(end):
                    continue
                if not self.ignore:
                    if actions_exists_in_db(partner_name, name, start, end):
                        continue
                action = helper.generate_action(partner_name, name, start, end, desc, code, url, action_type,short_desc)
                actions_data.append(action)
            self.queue.put('progress')
        helper.filling_queue(self.queue, actions_data, partner_name)
