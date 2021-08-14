import re
from multiprocessing import Process

from database.data_base import actions_exists_in_db_new
from helpers.Utils import Utils
from models.action import Action


class HolodilnikProcess(Process):

    def __init__(self, queue, ignore):
        super().__init__()
        self.queue = queue.queue
        self.ignore = ignore
        self.utils = Utils(self.queue)

    def __str__(self):
        return "Холодильник"

    def run(self):
        actions_data = []
        page = self.utils.ACTIONS_UTIL.get_page_use_request('https://ulyanovsk.holodilnik.ru/action/')
        divs = page.find_all("div", class_='col-4')
        begin_url = 'https://holodilnik.ru'
        self.queue.put(f'set {len(divs)}')
        for div in divs:
            action = Action(str(self))
            action.url = begin_url + div.a.get('href').strip()
            action.name = div.find('span', class_='link').text.strip()
            date = div.find('span', class_='text-data').text.strip()
            date = date.split(' - ')
            if len(date[0]) > 1:
                action.start = re.search(r'(\d+\.\d+\.\d+)', date[0]).group(1)
            else:
                self.queue.put('progress')
                continue
            if len(date) == 2:
                action.end = re.search(r'(\d+\.\d+\.\d+)', date[1]).group(1)
            else:
                action.end = self.utils.DATE_UTIL.get_date_month_ahead(action.start)
            action.desc = action.name
            action.code = 'Не требуется'
            action.short_desc = ''
            action.action_type = self.utils.ACTIONS_UTIL.check_action_type(action)
            if self.utils.DATE_UTIL.promotion_is_outdated(action.end):
                self.queue.put('progress')
                continue
            if not self.ignore:
                if actions_exists_in_db_new(action):
                    self.queue.put('progress')
                    continue
            actions_data.append(self.utils.ACTIONS_UTIL.generate_action(action))
            self.queue.put('progress')
        self.utils.CSV_UTIL.filling_queue(self.queue, actions_data, str(self))
