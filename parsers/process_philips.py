import re
from multiprocessing import Process

from database.data_base import actions_exists_in_db_new
from helpers.Utils import Utils
from models.action import Action


class PhilipsProcess(Process):

    def __init__(self, queue, ignore):
        super().__init__()
        self.queue = queue.queue
        self.ignore = ignore
        self.utils = Utils(self.queue)

    def __str__(self):
        return "Philips"

    def run(self):
        actions_data = []
        page = self.utils.ACTIONS_UTIL.get_page_use_request('https://www.shop.philips.ru/hot_offers')
        divs = page.find_all("div", class_='col-md-4')
        self.queue.put(f'set {len(divs)}')
        for div in divs:
            action = Action(str(self))
            action.url = div.a.get('href').strip()
            action.name = div.find('div', class_='title').text.strip()
            try:
                date = div.find('span', class_='date-format').text.strip()
                date = re.search(r'(\d+)\/(\d+)\/(\d+)', date)
                action.start = self.utils.DATE_UTIL.DATA_NOW
                action.end = f'{date.group(3)}.{date.group(2)}.{date.group(1)}'
            except AttributeError:
                action.start = self.utils.DATE_UTIL.get_first_day_month()
                action.end = self.utils.DATE_UTIL.get_date_end_month()
            action.desc = action.name
            action.code = 'Не требуется'
            action.short_desc = ''
            action.action_type = div.find('div', class_='caption').text.strip()
            if self.utils.DATE_UTIL.promotion_is_outdated(action.end):
                self.queue.put('progress')
                continue
            if not self.ignore:
                if actions_exists_in_db_new(action):
                    self.queue.put('progress')
                    continue
            actions_data.append(self.utils.ACTIONS_UTIL.generate_action_new(action))
            self.queue.put('progress')
        self.utils.CSV_UTIL.filling_queue(self.queue, actions_data, str(self))
