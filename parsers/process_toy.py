from multiprocessing import Process

import helpers.helper as helper
from database.data_base import actions_exists_in_db


class Toy_process(Process):

    def __init__(self, queue, ignore):
        super().__init__()
        self.queue = queue.queue
        self.ignore = ignore

    def __str__(self):
        return "Toy"

    def run(self):
        partner_name = 'Toy'
        actions_data = []
        base_url = 'https://www.toy.ru'
        for i in range(1, 11):
            main_url = f'https://www.toy.ru/company/akcii/?PAGEN_5={i}'
            page = helper.get_page_use_request(main_url)
            divs = page.find_all('div', class_='my-2')
            for div in divs:
                if div.find('img') is None:
                    continue
                if 'monohrome' in div.find('img', class_='img-fluid').get('class'):
                    print('Устаревшая акция')
                    continue
                url = base_url + div.find('a').get('href')
                name = div.find('img', class_='img-fluid').get('title').strip()
                start,end = helper.get_date_now_to_end_month()
                code = "Не требуется"
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
        helper.filling_queue(self.queue, actions_data, partner_name)
