import re
import threading
from multiprocessing import Process

from database.DataBase import *
from helpers.Utils import Utils
from models.Action import Action


class UtkonosProcess(Process):
    def __init__(self, queue, ignore):
        super().__init__()
        self.queue = queue.queue
        self.ignore = ignore
        self.utils = Utils(self.queue)

    def __str__(self):
        return "Утконос"

    def run(self):
        actions_data = []
        lock = threading.Lock()
        divs = self.utils.ACTIONS_UTIL.get_page_use_webdriver_with_scroll_into_elem('https://www.utkonos.ru/action',                                                                        'utk-action-list-item')
        self.queue.put(f'set {len(divs)}')
        for div in divs:
            action = Action(str(self))
            try:
                action.name = div.find('div', class_='template__content-text').text.strip()
            except AttributeError as exc:
                self.queue.put(f'{exc}')
                continue
            action.code = 'Не требуется'
            action.desc = ''
            action.url = 'https://www.utkonos.ru' + div.a.get('href')
            try:
                incoming_date = div.find('div', class_='template__content-status').text.strip()
            except (AttributeError, ValueError):
                incoming_date = ''
            if incoming_date != '':
                if 'остал' in incoming_date.lower():
                    days = re.search(r'(\d+)', incoming_date.lower()).group(1)
                    action.start = self.utils.DATE_UTIL.DATA_NOW
                    action.end = self.utils.DATE_UTIL.get_date_plus_days(int(days))
                elif 'Акция' == incoming_date:
                    action.start, action.end = self.utils.DATE_UTIL.get_date_now_to_end_month()
                else:
                    action.start, action.end = self.utils.DATE_UTIL.get_do_period(incoming_date)
            else:
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
