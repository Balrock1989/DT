import re
import threading
from multiprocessing import Process
import helpers.helper as helper
from database.data_base import actions_exists_in_db


class VseinstrumentiProcess(Process):
    def __init__(self, queue, ignore):
        super().__init__()
        self.queue = queue.queue
        self.ignore = ignore

    def __str__(self):
        return "ВсеИнструменты"

    def run(self):
        partner_name = 'Все инструменты'
        actions_data = []
        page = helper.get_page_use_webdriver('https://www.vseinstrumenti.ru/our_actions/aktsii')
        divs = page.find_all("div", class_='action_main')
        lock = threading.Lock()
        self.queue.put(f'set {len(divs)}')
        for div in divs:
            name = div.find('div', class_='action_header').a.text.strip()
            code = 'Не требуется'
            url = 'https://www.vseinstrumenti.ru/our_actions/aktsii'
            try:
                desc = div.find('div', class_='act_descr').find_all('p')[3].text.strip()
            except:
                try:
                    desc = div.find('div', class_='act_descr').text.strip()
                    desc = re.search(r'.*\n.*\n.*\n(.*)', desc).group(1).strip()
                except:
                    desc = div.find('div', class_='act_descr').find('p').text.strip()
            try:
                incoming_date = div.find('div', class_='act_descr').find_all('p')[0].text.strip()
            except:
                incoming_date = div.find('div', class_='act_descr').find_all('div')[0].text.strip()
            incoming_date = re.search(r'(\d.*)\–\s(.*)', incoming_date.lower())
            try:
                start, end = helper.get_double_date(incoming_date.group(1), incoming_date.group(2))
            except:
                start, end = helper.get_date_now_to_end_month()
            if helper.promotion_is_outdated(end):
                self.queue.put('progress')
                continue
            short_desc = ''
            action_type = helper.check_action_type(code, name, desc)
            if not self.ignore:
                with lock:
                    if actions_exists_in_db(partner_name, name, start, end):
                        self.queue.put('progress')
                        continue
            action = helper.generate_action(partner_name, name, start, end, desc, code, url, action_type, short_desc)
            actions_data.append(action)
            self.queue.put('progress')
        helper.filling_queue(self.queue, actions_data, partner_name)
