import re
from multiprocessing import Process
import helpers.helper as helper


class Utkonos_process(Process):
    def __init__(self, queue):
        super().__init__()
        self.queue = queue

    def __str__(self):
        return "Утконос"

    def run(self):
        partner_name = 'Утконос'
        actions_data = []
        page = helper.prepair_parser_data_use_request('https://www.utkonos.ru/action')
        divs = page.find_all("div", class_='action_wrapper')
        for div in divs:
            name = div.a.text.strip()
            code = 'Не требуется'
            desc = ''
            url = 'https://www.utkonos.ru' + div.a.get('href')
            incoming_date = div.find('div', class_='text').text.strip()
            incoming_date = re.search(r'с\s(\d+\s[а-яА-Я]+).*по\s(\d+\s[а-яА-Я]+)', incoming_date.lower())
            start, end = helper.get_double_date(incoming_date.group(1), incoming_date.group(2))
            if helper.promotion_is_outdated(end):
                continue
            short_desc = ''
            action_type = helper.check_action_type(code, name, desc)
            action = helper.generate_action(partner_name, name, start, end, desc, code, url, action_type, short_desc)
            actions_data.append(action)
        helper.filling_queue(self.queue, actions_data, partner_name)
