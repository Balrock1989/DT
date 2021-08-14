import threading
from multiprocessing import Process
from threading import Thread

from database.data_base import actions_exists_in_db_new
from helpers.Utils import Utils
from models.action import Action


class MtsProcess(Process):

    def __init__(self, queue, ignore):
        super().__init__()
        self.queue = queue.queue
        self.ignore = ignore
        self.utils = Utils(self.queue)

    def __str__(self):
        return "МТС"

    def run(self):
        lock = threading.Lock()
        actions_data = []
        base_url = 'https://shop.mts.ru'
        threads = []
        driver = self.utils.ACTIONS_UTIL.get_webdriver(hidden=False)
        for i in range(1, 3):
            main_url = f'https://shop.mts.ru/actions/{i}/'
            page = self.utils.ACTIONS_UTIL.get_page_with_driver(driver, main_url)
            divs = page.find_all('div', class_='news-block')
            for div in divs:
                threads.append(MtsThread(actions_data, lock, self.queue, base_url + div.find('a').get('href'),
                                         self.ignore, self.utils, driver))
        self.queue.put(f'set {len(threads)}')
        self.utils.ACTIONS_UTIL.start_join_threads(threads)
        driver.quit()
        self.utils.CSV_UTIL.filling_queue(self.queue, actions_data, str(self))


class MtsThread(Thread):

    def __str__(self):
        return "МТС"

    def __init__(self, actions_data, lock, queue, url, ignore, utils, driver):
        super().__init__()
        self.actions_data = actions_data
        self.lock = lock
        self.queue = queue
        self.url = url
        self.ignore = ignore
        self.utils = utils
        self.driver = driver

    def run(self):
        page = self.utils.ACTIONS_UTIL.get_page_with_driver(self.driver, self.url)
        action = Action(str(self))
        action.name = page.h1.text.strip()
        try:
            data_text = page.find_all('div', class_='wrapper')[0].find('p').text.strip()
            action.start, action.end = self.utils.DATE_UTIL.search_data_in_text(data_text)
        except (AttributeError, ValueError, IndexError):
            action.start, action.end = self.utils.DATE_UTIL.get_date_now_to_end_month()
        action.desc = action.name
        action.code = 'Не требуется'
        action.short_desc = ''
        action.action_type = self.utils.ACTIONS_UTIL.check_action_type(action)
        if self.utils.DATE_UTIL.promotion_is_outdated(action.end):
            self.queue.put('progress')
            return
        if not self.ignore:
            if actions_exists_in_db_new(action):
                self.queue.put('progress')
                return
        with self.lock:
            self.actions_data.append(self.utils.ACTIONS_UTIL.generate_action(action))
            self.queue.put('progress')
