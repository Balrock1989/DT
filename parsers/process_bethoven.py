import re
from datetime import datetime
from multiprocessing import Process
import helpers.helper as helper
from database.data_base import actions_exists_in_db


class Bethoven_process(Process):

    def __init__(self, queue, ignore):
        super().__init__()
        self.queue = queue.queue
        self.ignore = ignore

    def __str__(self):
        return "Бетховен"

    def run(self):
        partner_name = 'Бетховен'
        actions_data = []
        base_url = 'https://www.bethowen.ru'
        main_url = 'https://www.bethowen.ru/sale'
        page = helper.get_page_use_request(main_url)
        divs = page.find_all('a', class_='no-decor')
        for div in divs:
            try:
                url = str(div.get('href'))
                url = div.get('href') if 'www' in url else base_url + div.get('href')
            except TypeError:
                print("Отсутствуют данные по акции")
                continue
            name = div.find('img').get('title')
            name = re.sub('_.*$', '', name).strip()
            date = div.find('div', class_='text-period').text.strip()
            start, end = helper.convert_list_to_date(helper.get_range_date(date))
            code = "Не требуется"
            desc = name
            short_desc = ''
            action_type = helper.check_action_type(code, name, desc)
            if helper.promotion_is_outdated(end):
                continue
            if not self.ignore:
                if actions_exists_in_db(partner_name, name, start, end):
                    continue
            action = helper.generate_action(partner_name, name, start, end, desc, code, url, action_type, short_desc)
            actions_data.append(action)
        helper.filling_queue(self.queue, actions_data, partner_name)
