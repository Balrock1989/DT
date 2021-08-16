import re
from multiprocessing import Process

from database.DataBase import actions_exists_in_db_new
from helpers.Utils import Utils
from models.Action import Action


class BethovenProcess(Process):

    def __init__(self, queue, ignore):
        super().__init__()
        self.queue = queue.queue
        self.ignore = ignore
        self.utils = Utils(self.queue)

    def __str__(self):
        return "Бетховен"

    def run(self):
        actions_data = []
        base_url = 'https://www.bethowen.ru'
        main_url = 'https://www.bethowen.ru/sale'
        page = self.utils.ACTIONS_UTIL.get_page_use_request(main_url)
        divs = page.find_all('a', class_='no-decor')
        self.queue.put(f'set {len(divs)}')
        for div in divs:
            action = Action(str(self))
            try:
                action.url = str(div.get('href'))
                action.url = div.get('href') if 'www' in action.url else base_url + div.get('href')
            except TypeError:
                self.queue.put('progress')
                continue
            action.name = div.find('img').get('title')
            action.name = re.sub('_.*$', '', action.name).strip()
            date = div.find('div', class_='text-period').text.strip()
            if "остал" in date.lower():
                days = re.search(r'(\d+)', date.lower()).group(1)
                action.start = self.utils.DATE_UTIL.DATA_NOW
                action.end = self.utils.DATE_UTIL.get_date_plus_days(int(days))
            else:
                action.start, action.end = self.utils.DATE_UTIL.convert_list_to_date(
                    self.utils.DATE_UTIL.get_range_date(date))
            action.code = "Не требуется"
            action.desc = action.name
            action.short_desc = ''
            action.action_type = self.utils.ACTIONS_UTIL.check_action_type(action)
            if self.utils.DATE_UTIL.promotion_is_outdated(action.end):
                self.queue.put('progress')
                continue
            if not self.ignore:
                if actions_exists_in_db_new(action):
                    self.queue.put('progress')
                    continue
            action = self.utils.ACTIONS_UTIL.generate_action(action)
            actions_data.append(action)
            self.queue.put('progress')
        self.utils.CSV_UTIL.filling_queue(self.queue, actions_data, str(self))
