import re
from multiprocessing import Process

from database.data_base import actions_exists_in_db_new
from helpers.Utils import Utils
from models.action import Action


class PharmacosmeticaProcess(Process):

    def __init__(self, queue, ignore):
        super().__init__()
        self.queue = queue.queue
        self.ignore = ignore
        self.utils = Utils(self.queue)

    def __str__(self):
        return "ФармКосметика"

    def run(self):
        actions_data = []
        base_url = 'https://www.pharmacosmetica.ru'
        for i in range(3):
            main_url = f'https://www.pharmacosmetica.ru/podarki-dlya-vas/?page={i}'
            page = self.utils.ACTIONS_UTIL.get_page_use_request(main_url)
            divs = page.find_all('a', class_='podarok')
            self.queue.put(f'set {len(divs)}')
            for div in divs:
                action = Action(str(self))
                action.url = base_url + div.get('href')
                action.name = div.find('div', class_='textpod').text.strip()
                action.name = re.sub(r'\n', ' ', action.name).strip()
                action.start, action.end = self.utils.DATE_UTIL.get_date_now_to_end_month()
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
                actions_data.append(self.utils.ACTIONS_UTIL.generate_action(action))
                self.queue.put('progress')
        self.utils.CSV_UTIL.filling_queue(self.queue, actions_data, str(self))
