import re
from multiprocessing import Process
import helpers.helper as helper
from database.data_base import actions_exists_in_db


class Pharmacosmetica_process(Process):

    def __init__(self, queue, ignore):
        super().__init__()
        self.queue = queue.queue
        self.ignore = ignore

    def __str__(self):
        return "ФармКосметика"

    def run(self):
        partner_name = 'ФармКосметика'
        actions_data = []
        base_url = 'https://www.pharmacosmetica.ru'
        for i in range(3):
            main_url = f'https://www.pharmacosmetica.ru/podarki-dlya-vas/?page={i}'
            try:
                page = helper.get_page_use_request(main_url)
            except:
                continue
            divs = page.find_all('a', class_='podarok')
            self.queue.put(f'set {len(divs)}')
            for div in divs:
                url = base_url + div.get('href')
                name = div.find('div', class_='textpod').text.strip()
                name = re.sub(r'\n', ' ', name).strip()
                start, end = helper.get_date_now_to_end_month()
                code = "Не требуется"
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
