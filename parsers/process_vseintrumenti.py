import re
from multiprocessing import Process
import helpers.helper as helper


class Vseinstrumenti_process(Process):
    def __init__(self, queue):
        super().__init__()
        self.queue = queue

    def __str__(self):
        return "ВсеИнструменты"

    def run(self):
        partner_name = 'Все инструменты'
        actions_data = []
        page = helper.prepare_parser_data_use_webdriver('https://www.vseinstrumenti.ru/our_actions/aktsii')
        divs = page.find_all("div", class_='action_main')
        for div in divs:
            name = div.find('div', class_='action_header').a.text.strip()
            code = 'Не требуется'
            url = 'https://www.vseinstrumenti.ru/our_actions/aktsii'
            desc = div.find('div', class_='act_descr').find_all('p')[3].text.strip()
            incoming_date = div.find('div', class_='act_descr').find_all('p')[0].text.strip()
            incoming_date = re.search(r'(\d.*)\–\s(.*)', incoming_date.lower())
            try:
                start, end = helper.get_double_date(incoming_date.group(1), incoming_date.group(2))
            except Exception:
                start, end = helper.get_date_now_to_end_month()
            if helper.promotion_is_outdated(end):
                continue
            short_desc = ''
            action_type = helper.check_action_type(code, name, desc)
            action = helper.generate_action(partner_name, name, start, end, desc, code, url, action_type, short_desc)
            actions_data.append(action)
        helper.filling_queue(self.queue, actions_data, partner_name)
