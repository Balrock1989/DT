from multiprocessing import Process

import helpers.helper as helper
from database.data_base import actions_exists_in_db


class LabirintProcess(Process):

    def __init__(self, queue, ignore):
        super().__init__()
        self.queue = queue.queue
        self.ignore = ignore

    def __str__(self):
        return "Labirint"

    def run(self):
        partner_name = 'Labirint'
        actions_data = []
        base_url = 'https://www.labirint.ru'
        self.queue.put(f'set 2')
        for i in range(1, 3):
            main_url = f'https://www.labirint.ru/actions/?page={i}'
            page = helper.get_page_use_request(main_url)
            divs = page.find_all('div', class_='need-watch')
            for div in divs:
                url = base_url + div.find('a').get('href')
                name = div.find('a').get('title').strip()
                date = div.find('div', class_='news-item__dates').text.strip()
                start, end = helper.search_data_in_text(date)
                code = "Не требуется"
                desc = div.find('div', class_='news-item__anons').text.strip()
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
