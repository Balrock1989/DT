from multiprocessing import Process

import helpers.helper as helper
from database.data_base import actions_exists_in_db


class KotofotoProcess(Process):

    def __init__(self, queue, ignore):
        super().__init__()
        self.queue = queue.queue
        self.ignore = ignore

    def __str__(self):
        return "Котофото"

    def run(self):
        partner_name = 'Котофото'
        actions_data = []
        base_url = 'https://kotofoto.ru'
        main_url = 'https://kotofoto.ru/promotion/'
        page = helper.get_page_use_request(main_url)
        divs = page.select('.media-object')
        self.queue.put(f'set {len(divs)}')
        for div in divs:
            url = base_url + div.find('h4').find('a').get('href')
            name = div.find('h4').text.strip()
            try:
                date = div.find('span').text.strip()
                start, end = helper.convert_text_date(date)
            except:
                start, end = helper.get_date_now_to_end_month()
            code = "Не требуется"
            try:
                desc = div.find('p').text.strip()
            except:
                desc = name
            short_desc = ''
            action_type = helper.check_action_type(code, name, desc)
            if helper.promotion_is_outdated(end):
                self.queue.put('progress')
                continue
            if not self.ignore:
                if actions_exists_in_db(partner_name, name, start, end):
                    self.queue.put('progress')
                    continue
            action = helper.generate_action(partner_name, name, start, end, desc, code, url, action_type,short_desc)
            actions_data.append(action)
            self.queue.put('progress')
        helper.filling_queue(self.queue, actions_data, partner_name)
