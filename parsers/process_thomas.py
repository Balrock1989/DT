import re
from multiprocessing import Process

from database.data_base import actions_exists_in_db_new
from helpers.Utils import Utils
from models.action import Action


class ThomasProcess(Process):

    def __init__(self, queue, ignore):
        super().__init__()
        self.queue = queue.queue
        self.ignore = ignore
        self.utils = Utils(self.queue)

    def __str__(self):
        return "Thomas"

    def run(self):
        partner_name = 'Thomas'
        actions_data = []
        base_url = 'https://thomas-muenz.ru'
        self.queue.put(f'set 2')
        for i in range(1, 3):
            main_url = f'https://thomas-muenz.ru/actions/?PAGEN_1={i}'
            page = self.utils.ACTIONS_UTIL.get_page_use_request(main_url)
            divs = page.select('.promo-list__item')
            for div in divs:
                action = Action(partner_name)
                action.url = base_url + div.select_one('h2 a.link').get('href')
                action.name = div.select_one('h2 a.link').text.strip()
                date = div.select_one('.promo-alt-card__footer').text.strip()
                date = re.split(r' по ', date.lower())
                if len(date) > 1:
                    action.start, action.end = self.utils.DATE_UTIL.get_double_date(date[0].strip(), date[1].strip())
                elif len(date) == 1:
                    action.start, action.end = self.utils.DATE_UTIL.get_start_date_in_date(date[0], True)
                else:
                    action.start, action.end = self.utils.DATE_UTIL.get_date_now_to_end_month()
                action.code = "Не требуется"
                action.desc = div.select_one('.promo-alt-card__text').text.strip()
                action.short_desc = ''
                action.action_type = self.utils.ACTIONS_UTIL.check_action_type_new(action)
                if self.utils.DATE_UTIL.promotion_is_outdated(action.end):
                    continue
                if not self.ignore:
                    if actions_exists_in_db_new(action):
                        continue
                actions_data.append(self.utils.ACTIONS_UTIL.generate_action_new(action))
            self.queue.put('progress')
        self.utils.CSV_UTIL.filling_queue(self.queue, actions_data, partner_name)
