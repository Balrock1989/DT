from multiprocessing import Process

from database.data_base import actions_exists_in_db_new
from helpers.Utils import Utils
from models.action import Action


class DomovoyProcess(Process):

    def __init__(self, queue, ignore):
        super().__init__()
        self.queue = queue.queue
        self.ignore = ignore
        self.count_page = 3
        self.utils = Utils(self.queue)

    def __str__(self):
        return "Домовой"

    def run(self):
        actions_data = []
        base_url = 'https://tddomovoy.ru'
        self.queue.put(f'set {self.count_page}')
        for i in range(1, self.count_page + 1):
            main_url = f'https://tddomovoy.ru/actions/?PAGEN_1={i}'
            page = self.utils.ACTIONS_UTIL.get_page_use_request(main_url)
            divs = page.select('a.stock-panel')
            for div in divs:
                action = Action(str(self))
                action.url = base_url + div.get('href')
                action.name = div.find('img').get('title').strip()
                try:
                    date = div.find('div', class_='date').text.strip()
                    action.start, action.end = self.utils.DATE_UTIL.convert_list_to_date(
                        self.utils.DATE_UTIL.get_range_date(date))
                except (AttributeError, ValueError):
                    action.start, action.end = self.utils.DATE_UTIL.get_date_now_to_end_month()
                action.code = "Не требуется"
                try:
                    action.desc = div.find('div', class_='text').text.strip()
                except (AttributeError, ValueError):
                    action.desc = action.name
                action.short_desc = ''
                action.action_type = self.utils.ACTIONS_UTIL.check_action_type(action)
                if self.utils.DATE_UTIL.promotion_is_outdated(action.end):
                    continue
                if not self.ignore:
                    if actions_exists_in_db_new(action):
                        continue
                actions_data.append(self.utils.ACTIONS_UTIL.generate_action(action))
            self.queue.put('progress')
        self.utils.CSV_UTIL.filling_queue(self.queue, actions_data, str(self))
