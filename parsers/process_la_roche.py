import re
from multiprocessing import Process

from database.data_base import actions_exists_in_db_new
from helpers.Utils import Utils
from models.action import Action


class LaRocheProcess(Process):

    def __init__(self, queue, ignore):
        super().__init__()
        self.queue = queue.queue
        self.ignore = ignore
        self.utils = Utils(self.queue)

    def __str__(self):
        return "La Roche posay"

    def run(self):
        actions_data = []
        base_url = 'https://www.laroche-posay.ru'
        main_url = 'https://www.laroche-posay.ru/special-offers/'
        page = self.utils.ACTIONS_UTIL.get_page_use_request(main_url)
        divs1 = page.findAll('div', class_='special-offers-banner')
        divs1 = [div for div in divs1 if div.get('style') is None]
        self.queue.put(f'set {len(divs1)}')
        for div in divs1:
            action = Action(str(self))
            action.url = main_url
            text = div.findAll('div', class_='special-offers-banner__text')
            action.name = re.sub(r'\n', ' ', text[0].text.strip()).strip()
            action.name = re.sub(r'\r', ' ', action.name).strip()
            action.name = re.sub(r'\s{2,}', ' ', action.name)
            try:
                date = text[1].text.strip()
                action.start, action.end = self.utils.DATE_UTIL.convert_list_to_date(
                    self.utils.DATE_UTIL.get_range_date(date))
            except AttributeError:
                action.start, action.end = self.utils.DATE_UTIL.get_date_now_to_end_month()
            try:
                action.code = div.find('div', class_='special-offers-banner__code').text.strip()
            except AttributeError:
                action.code = 'Не требуется'
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

        divs2 = page.findAll('div', class_='special-offers-promo')
        divs2 = [div for div in divs2 if div.get('style') is None]
        self.queue.put(f'set {len(divs2)}')
        for div in divs2:
            action = Action(str(self))
            action.url = base_url + div.find('a').get('href')
            action.name = div.find(class_='special-offers-promo__text').text.strip()
            action.name = re.sub(r'\n', ' ', action.name)
            action.name = re.sub(r'\r', ' ', action.name).strip()
            action.name = re.sub(r'\s{2,}', ' ', action.name)
            action.start = self.utils.DATE_UTIL.DATA_NOW
            action.end = self.utils.DATE_UTIL.get_date_end_month()
            action.code = 'Не требуется'
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
