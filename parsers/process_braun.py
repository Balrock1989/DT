import re
from multiprocessing import Process

from database.data_base import actions_exists_in_db
from helpers.Utils import Utils
from models.action import Action


class BraunProcess(Process):

    def __init__(self, queue, ignore):
        super().__init__()
        self.queue = queue.queue
        self.ignore = ignore
        self.link_selector = '.imageBlock a'
        self.utils = Utils(self.queue)

    def __str__(self):
        return "Braun"

    def run(self):
        partner_name = 'Braun'
        actions_data = []
        base_url = 'https://braun-russia.ru'
        page = self.utils.ACTIONS_UTIL.get_page_use_request('https://braun-russia.ru/actions')
        divs = page.select('.bm2-cat-item')
        self.queue.put(f'set {len(divs)}')
        for div in divs:
            if div.select_one(self.link_selector) is None:
                continue
            action = Action(partner_name)
            action.url = div.select_one(self.link_selector).get('href').strip()
            if 'http' not in action.url:
                action.url = base_url + action.url
            action.name = div.select_one(self.link_selector).get('title').strip()
            try:
                date = div.select_one('.daysleft').text.strip()
                date_end_action = re.search(r'(\d+)', date)
                action.start = self.utils.DATE_UTIL.DATA_NOW
                action.end = self.utils.DATE_UTIL.get_date_plus_days(int(date_end_action.group(1)))
            except AttributeError:
                action.start, action.end = self.utils.DATE_UTIL.get_date_now_to_end_month()
            action.desc = div.select_one('.teaser').text.strip()
            if 'промокод' in action.name.lower():
                try:
                    action.code = re.search(r'([A-Z0-9]+)', action.name).group(1)
                except AttributeError:
                    action.code = 'Не требуется'
            else:
                action.code = 'Не требуется'
            action.short_desc = ''
            action.action_type = self.utils.ACTIONS_UTIL.check_action_type_new(action)
            if self.utils.DATE_UTIL.promotion_is_outdated(action.end):
                self.queue.put('progress')
                continue
            if not self.ignore:
                if actions_exists_in_db(action):
                    self.queue.put('progress')
                    continue
            action = self.utils.ACTIONS_UTIL.generate_action_new(action)
            actions_data.append(action)
            self.queue.put('progress')
        self.utils.CSV_UTIL.filling_queue(self.queue, actions_data, partner_name)
