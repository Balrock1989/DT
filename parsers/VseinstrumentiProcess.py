import re
import threading
from multiprocessing import Process

from database.DataBase import actions_exists_in_db_new
from helpers.Utils import Utils
from models.Action import Action


class VseinstrumentiProcess(Process):
    def __init__(self, queue, ignore):
        super().__init__()
        self.queue = queue.queue
        self.ignore = ignore
        self.utils = Utils(self.queue)

    def __str__(self):
        return "ВсеИнструменты"

    def run(self):
        actions_data = []
        page = self.utils.ACTIONS_UTIL.get_page_use_webdriver('https://www.vseinstrumenti.ru/our_actions/aktsii')
        divs = page.find_all("div", class_='action_main')
        lock = threading.Lock()
        self.queue.put(f'set {len(divs)}')
        for div in divs:
            action = Action(str(self))
            action.name = div.find('div', class_='action_header').a.text.strip()
            action.code = 'Не требуется'
            action.url = 'https://www.vseinstrumenti.ru/our_actions/aktsii'
            try:
                action.desc = div.find('div', class_='act_descr').find_all('p')[3].text.strip()
            except AttributeError:
                try:
                    action.desc = div.find('div', class_='act_descr').text.strip()
                    action.desc = re.search(r'.*\n.*\n.*\n(.*)', action.desc).group(1).strip()
                except AttributeError:
                    action.desc = div.find('div', class_='act_descr').find('p').text.strip()
            try:
                incoming_date = div.find('div', class_='act_descr').find_all('p')[0].text.strip()
            except AttributeError:
                incoming_date = div.find('div', class_='act_descr').find_all('div')[0].text.strip()
            incoming_date = re.search(r'(\d.*)\–\s(.*)', incoming_date.lower())
            try:
                action.start, action.end = self.utils.DATE_UTIL.get_double_date(incoming_date.group(1),
                                                                                incoming_date.group(2))
            except (AttributeError, ValueError):
                action.start, action.end = self.utils.DATE_UTIL.get_date_now_to_end_month()
            if self.utils.DATE_UTIL.promotion_is_outdated(action.end):
                self.queue.put('progress')
                continue
            action.short_desc = ''
            action.action_type = self.utils.ACTIONS_UTIL.check_action_type(action)
            if not self.ignore:
                with lock:
                    if actions_exists_in_db_new(action):
                        self.queue.put('progress')
                        continue
            actions_data.append(self.utils.ACTIONS_UTIL.generate_action(action))
            self.queue.put('progress')
        self.utils.CSV_UTIL.filling_queue(self.queue, actions_data, str(self))
