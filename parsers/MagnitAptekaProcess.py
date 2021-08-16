import threading
from multiprocessing import Process
from threading import Thread

from database.data_base import actions_exists_in_db_new
from helpers.Utils import Utils
from models.action import Action


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
        threads = []
        lock = threading.Lock()
        base_url = 'https://apteka.magnit.ru'

        driver = self.utils.ACTIONS_UTIL.get_webdriver()
        main_url = f'https://apteka.magnit.ru/actions/'
        page = self.utils.ACTIONS_UTIL.get_page_with_driver(driver, main_url)
        divs = page.select('.action-item')
        self.queue.put(f'set {len(divs)}')
        for div in divs:
            action = Action(str(self))
            if div.select_one('a') is None:
                continue
            action.url = base_url + div.select_one('a').get('href')
            threads.append(MagnitAptekaThread(actions_data, lock, self.queue, action, self.ignore, self.utils, driver))
        self.queue.put(f'set {len(threads)}')
        self.utils.ACTIONS_UTIL.start_join_threads(threads)
        driver.quit()
        self.utils.CSV_UTIL.filling_queue(self.queue, actions_data, str(self))


class MagnitAptekaThread(Thread):

    def __init__(self, actions_data, lock, queue, action, ignore, utils, driver):
        super().__init__()
        self.actions_data = actions_data
        self.lock = lock
        self.queue = queue
        self.action = action
        self.ignore = ignore
        self.utils = utils
        self.driver = driver

    def run(self):
        page = self.utils.ACTIONS_UTIL.get_page_with_driver(self.driver, self.action.url)
        self.action.name = page.select_one('.promo-page__title').text.strip()
        self.action.code = "Не требуется"
        self.action.desc = page.select_one('.promo-page__main-text').text.strip()
        self.action.short_desc = ''
        self.action.action_type = self.utils.ACTIONS_UTIL.check_action_type(self.action)
        date = page.select_one('.promo-page__date').text.strip()
        self.action.start, self.action.end = self.utils.DATE_UTIL.convert_list_to_date(
            self.utils.DATE_UTIL.get_range_date(date))
        if self.utils.DATE_UTIL.promotion_is_outdated(self.action.end):
            self.queue.put('progress')
            return
        if not self.ignore:
            with self.lock:
                if actions_exists_in_db_new(self.action):
                    self.queue.put('progress')
                    return
        with self.lock:
            self.actions_data.append(self.utils.ACTIONS_UTIL.generate_action(self.action))
            self.queue.put('progress')
