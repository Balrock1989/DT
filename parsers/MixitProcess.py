import re
from multiprocessing import Process

from database.DataBase import actions_exists_in_db_new
from helpers.Utils import Utils
from models.Action import Action


class MixitProcess(Process):

    def __init__(self, queue, ignore):
        super().__init__()
        self.queue = queue.queue
        self.ignore = ignore
        self.link_selector = '.SpecialOfferPreview-media a'
        self.utils = Utils(self.queue)

    def __str__(self):
        return "Mixit"

    def run(self):
        actions_data = []
        url_base = 'https://mixit.ru'
        page = self.utils.ACTIONS_UTIL.get_page_use_webdriver('https://mixit.ru/special-offers', hidden=True)
        divs = page.select('.SpecialOfferList-item')
        self.queue.put(f'set {len(divs)}')
        for div in divs:
            if div.select_one(self.link_selector) is None:
                continue
            action = Action(str(self))
            action.url = url_base + div.select_one(self.link_selector).get('href').strip()
            action.name = div.select_one('.Media-picture').get('alt').strip()
            action.start, action.end = self.utils.DATE_UTIL.get_date_now_to_end_month()
            try:
                date = div.select_one('.SpecialOfferPreview-expireCaption').text.strip()
                if 'дне' in date:
                    day_end_action = re.search(r'(\d+)', date)
                    action.end = self.utils.DATE_UTIL.get_date_plus_days(int(day_end_action.group(1)))
                elif 'месяц' in date:
                    month_end_action = re.search(r'(\d+)', date)
                    action.end = self.utils.DATE_UTIL.get_date_plus_days(int(month_end_action.group(1)) * 30)
            except AttributeError:
                self.queue.put('log error when processing dates')
            action.desc = div.select_one('.SpecialOfferPreview-description').text.strip()
            if 'промокод' in action.name.lower():
                try:
                    action.code = re.search(r'([A-Z0-9]+)', action.name).group(1)
                except AttributeError:
                    action.code = 'Не требуется'
            else:
                action.code = 'Не требуется'
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
