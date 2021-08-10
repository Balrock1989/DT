from multiprocessing import Process

from database.data_base import actions_exists_in_db_new
from helpers.Utils import Utils
from models.action import Action


class KotofotoProcess(Process):

    def __init__(self, queue, ignore):
        super().__init__()
        self.queue = queue.queue
        self.ignore = ignore
        self.utils = Utils(self.queue)

    def __str__(self):
        return "Котофото"

    def run(self):
        actions_data = []
        base_url = 'https://kotofoto.ru'
        main_url = 'https://kotofoto.ru/promotion/'
        page = self.utils.ACTIONS_UTIL.get_page_use_request(main_url)
        divs = page.select('.media-object')
        self.queue.put(f'set {len(divs)}')
        for div in divs:
            action = Action(str(self))
            action.url = base_url + div.find('h4').find('a').get('href')
            action.name = div.find('h4').text.strip()
            try:
                date = div.find('span').text.strip()
                action.start, action.end = self.utils.DATE_UTIL.convert_text_date(date)
            except:
                action.start, action.end = self.utils.DATE_UTIL.get_date_now_to_end_month()
            action.code = "Не требуется"
            try:
                action.desc = div.find('p').text.strip()
            except:
                action.desc = action.name
            action.short_desc = ''
            action.action_type = self.utils.ACTIONS_UTIL.check_action_type_new(action)
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
