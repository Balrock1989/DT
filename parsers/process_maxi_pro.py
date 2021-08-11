import threading
from multiprocessing import Process

from database.data_base import actions_exists_in_db_new
from helpers.Utils import Utils
from models.action import Action


class MaxiProProcess(Process):
    def __init__(self, queue, ignore):
        super().__init__()
        self.queue = queue.queue
        self.ignore = ignore
        self.utils = Utils(self.queue)

    def __str__(self):
        return "МаксиПро"

    def run(self):
        actions_data = []
        lock = threading.Lock()
        main_url = 'https://maxipro.ru/sales/'
        base_url = 'https://maxipro.ru'
        page = self.utils.ACTIONS_UTIL.get_page_use_request(main_url)
        divs = page.find_all("div", class_='sale-card-wrapper')
        self.queue.put(f'set {len(divs)}')
        for div in divs:
            action = Action(str(self))
            action.url = base_url + div.find("a").get('href')
            action.name = div.find("div", class_='sale-card-title').text.strip()
            action.desc = div.find("div", class_='sale-card-text d-none d-md-block').text.strip()
            try:
                date = div.find("div", class_='sale-card-text -grey-').text.strip()
                action.start, action.end = self.utils.DATE_UTIL.search_data_in_text_without_year(date)
            except AttributeError:
                action.start = self.utils.DATE_UTIL.DATA_NOW
                action.end = self.utils.DATE_UTIL.get_date_plus_days(30)
            action.code = 'Не требуется'
            if self.utils.DATE_UTIL.promotion_is_outdated(action.end):
                self.queue.put('progress')
                continue
            action.short_desc = ''
            action.action_type = self.utils.ACTIONS_UTIL.check_action_type_new(action)
            if not self.ignore:
                with lock:
                    if actions_exists_in_db_new(action):
                        self.queue.put('progress')
                        continue
            actions_data.append(self.utils.ACTIONS_UTIL.generate_action_new(action))
            self.queue.put('progress')
        self.utils.CSV_UTIL.filling_queue(self.queue, actions_data, str(self))
