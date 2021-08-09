import threading
from multiprocessing import Process

from database.data_base import actions_exists_in_db_new
from helpers.Utils import Utils
from models.action import Action


class BookProcess(Process):

    def __init__(self, queue, ignore):
        super().__init__()
        self.queue = queue.queue
        self.ignore = ignore
        self.utils = Utils(self.queue)

    def __str__(self):
        return "Book24"

    def run(self):
        actions_data = []
        lock = threading.Lock()
        page = self.utils.ACTIONS_UTIL.get_page_use_webdriver('https://book24.ru/sales/', scroll=True, hidden=True)
        begin_url = 'https://book24.ru'
        divs = page.find_all('div', class_='stock-list-item__container')
        self.queue.put(f'set {len(divs)}')
        for div in divs:
            if not div.find('div', class_='stock-list-item__countdown'):
                self.queue.put('progress')
                continue
            action = Action(str(self))
            action.name = div.find('p', class_='stock-list-item__title').text.strip()
            date = div.find('span', class_='info-list__text').text.strip() \
                if len(div.findAll('div', class_='info-list__item')) < 2 \
                else div.findAll('span', class_='info-list__text')[1].text.strip()
            action.start, action.end = self.utils.DATE_UTIL.get_do_period(date)
            action.desc = div.find('div', class_='stock-list-item__desc').text.strip() \
                if div.find('div', class_='stock-list-item__desc') else action.name
            action.url = begin_url + div.find("div", class_='stock-list-item__more').a.get('href')
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
