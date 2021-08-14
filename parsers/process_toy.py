from multiprocessing import Process

from database.data_base import actions_exists_in_db_new
from helpers.Utils import Utils
from models.action import Action


class ToyProcess(Process):

    def __init__(self, queue, ignore):
        super().__init__()
        self.queue = queue.queue
        self.ignore = ignore
        self.utils = Utils(self.queue)

    def __str__(self):
        return "Toy"

    def run(self):
        actions_data = []
        base_url = 'https://www.toy.ru'
        self.queue.put(f'set 10')
        for i in range(1, 11):
            main_url = f'https://www.toy.ru/company/akcii/?PAGEN_5={i}'
            page = self.utils.ACTIONS_UTIL.get_page_use_request(main_url)
            divs = page.find_all('div', class_='my-2')
            for div in divs:
                if div.find('img') is None:
                    continue
                if 'monohrome' in div.find('img', class_='img-fluid').get('class'):
                    print('Устаревшая акция')
                    continue
                action = Action(str(self))
                action.url = base_url + div.find('a').get('href')
                action.name = div.find('img', class_='img-fluid').get('title').strip()
                action.start, action.end = self.utils.DATE_UTIL.get_date_now_to_end_month()
                action.code = "Не требуется"
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
