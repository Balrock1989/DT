import threading
from multiprocessing import Process

from database.DataBase import actions_exists_in_db_new
from helpers.Utils import Utils
from models.Action import Action


class SantehnikaTutProcess(Process):
    def __init__(self, queue, ignore):
        super().__init__()
        self.queue = queue.queue
        self.ignore = ignore
        self.count_page = 2
        self.utils = Utils(self.queue)

    def __str__(self):
        return 'СантехникаТут'

    def run(self):
        actions_data = []
        lock = threading.Lock()
        self.queue.put(f'set 2{self.count_page}')
        for i in range(1, self.count_page + 1):
            main_url = f'https://santehnika-tut.ru/actions/page-{i}.html'
            page = self.utils.ACTIONS_UTIL.get_page_use_request(main_url)
            divs = page.find_all('div', class_='col-xs-12 col-sm-6 col-md-3')
            for div in divs:
                action = Action(str(self))
                try:
                    action.name = div.find('span', class_='title').text.strip()
                except AttributeError as exc:
                    self.queue.put(f'{exc}')
                    continue
                action.url = 'https://santehnika-tut.ru' + div.find('a').get('href')
                try:
                    action.start, action.end = self.utils.DATE_UTIL.search_end_data_in_text(
                        div.find('span', class_='date').text.strip())
                except AttributeError:
                    action.start = self.utils.DATE_UTIL.DATA_NOW
                    action.end = self.utils.DATE_UTIL.get_date_end_month()
                action.desc = action.name
                action.code = 'Не требуется'
                if self.utils.DATE_UTIL.promotion_is_outdated(action.end):
                    continue
                action.short_desc = ''
                action.action_type = self.utils.ACTIONS_UTIL.check_action_type(action)
                if not self.ignore:
                    with lock:
                        if actions_exists_in_db_new(action):
                            continue
                action = self.utils.ACTIONS_UTIL.generate_action(action)
                actions_data.append(action)
            self.queue.put('progress')
        self.utils.CSV_UTIL.filling_queue(self.queue, actions_data, str(self))
