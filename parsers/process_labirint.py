from multiprocessing import Process

from database.data_base import actions_exists_in_db_new
from helpers.Utils import Utils
from models.action import Action


class LabirintProcess(Process):

    def __init__(self, queue, ignore):
        super().__init__()
        self.queue = queue.queue
        self.ignore = ignore
        self.utils = Utils(self.queue)

    def __str__(self):
        return "Labirint"

    def run(self):
        actions_data = []
        base_url = 'https://www.labirint.ru'
        self.queue.put(f'set 2')
        for i in range(1, 3):
            main_url = f'https://www.labirint.ru/actions/?page={i}'
            page = self.utils.ACTIONS_UTIL.get_page_use_request(main_url)
            divs = page.find_all('div', class_='need-watch')
            for div in divs:
                action = Action(str(self))
                action.url = base_url + div.find('a').get('href')
                action.name = div.find('a').get('title').strip()
                date = div.find('div', class_='news-item__dates').text.strip()
                action.start, action.end = self.utils.DATE_UTIL.search_data_in_text(date)
                action.code = "Не требуется"
                action.desc = div.find('div', class_='news-item__anons').text.strip()
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
