from multiprocessing import Process

from database.DataBase import actions_exists_in_db_new
from helpers.Utils import Utils
from models.Action import Action


class MagnitAptekaProcess(Process):

    def __init__(self, queue, ignore):
        super().__init__()
        self.queue = queue.queue
        self.ignore = ignore
        self.utils = Utils(self.queue)

    def __str__(self):
        return "Магнит-аптека"

    def run(self):
        actions_data = []
        actions = []
        base_url = 'https://apteka.magnit.ru'
        main_url = f'https://apteka.magnit.ru/actions/'
        page = self.utils.ACTIONS_UTIL.get_page_use_request(main_url)
        divs = page.select('.action-item')
        self.queue.put(f'set {len(divs)}')
        for div in divs:
            action = Action(str(self))
            if div.select_one('a') is None:
                continue
            action.url = base_url + div.select_one('a').get('href')
            actions.append(action)
        self.queue.put(f'set {len(actions)}')
        for action in actions:
            page = self.utils.ACTIONS_UTIL.get_page_use_request(action.url)
            action.name = page.select_one('.promo-page__title').text.strip()
            action.code = "Не требуется"
            action.desc = page.select_one('.promo-page__main-text').text.strip()
            action.short_desc = ''
            action.action_type = self.utils.ACTIONS_UTIL.check_action_type(action)
            date = page.select_one('.promo-page__date').text.strip()
            action.start, action.end = self.utils.DATE_UTIL.convert_list_to_date(
                self.utils.DATE_UTIL.get_range_date(date))
            if self.utils.DATE_UTIL.promotion_is_outdated(action.end):
                self.queue.put('progress')
                return
            if not self.ignore:
                if actions_exists_in_db_new(action):
                    self.queue.put('progress')
                    continue
            actions_data.append(self.utils.ACTIONS_UTIL.generate_action(action))
            self.queue.put('progress')
        self.utils.CSV_UTIL.filling_queue(self.queue, actions_data, str(self))
