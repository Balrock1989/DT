import threading
from multiprocessing import Process
from threading import Thread

from bs4 import BeautifulSoup

from database.data_base import actions_exists_in_db_new
from helpers.Utils import Utils
from models.action import Action


class MieleProcess(Process):

    def __init__(self, queue, ignore):
        super().__init__()
        self.queue = queue.queue
        self.ignore = ignore
        self.count_page = 2
        self.link_selector = '.SpecialOfferPreview-media a'
        self.utils = Utils(self.queue)

    def __str__(self):
        return "Miele-shop"

    def run(self):
        actions_data = []
        threads = []
        lock = threading.Lock()
        base_url = 'https://www.miele-shop.ru'
        self.queue.put(f'set {self.count_page}')
        driver = self.utils.ACTIONS_UTIL.get_webdriver(hidden=False)
        for i in range(1, self.count_page + 1):
            main_url = f'https://www.miele-shop.ru/news/special/?PAGEN_1={i}'
            driver.get(main_url)
            page = BeautifulSoup(driver.page_source, 'lxml')
            divs = page.select('.preview-full__container')
            for div in divs:
                action = Action(str(self))
                action.url = base_url + div.select_one('a.preview-full__wrap').get('href')
                action.name = div.select_one('.preview-full__title').text.strip()
                action.code = "Не требуется"
                action.desc = div.select_one('.preview-full__text').text.strip()
                action.short_desc = ''
                action.action_type = self.utils.ACTIONS_UTIL.check_action_type(action.code, action.name, action.desc)
                threads.append(MieleThread(actions_data, lock, self.queue, action, self.ignore, self.utils, driver))
        self.queue.put(f'set {len(threads)}')
        self.utils.ACTIONS_UTIL.start_join_threads(threads)
        driver.quit()
        self.utils.CSV_UTIL.filling_queue(self.queue, actions_data, str(self))


class MieleThread(Thread):

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
        self.driver.get(self.action.url)
        page = BeautifulSoup(self.driver.page_source, 'lxml')
        try:
            self.action.start, self.action.end = self.utils.DATE_UTIL.convert_list_to_date(
                self.utils.DATE_UTIL.get_range_date(page.select_one('.content').text.strip()))
        except AttributeError:
            self.queue.put(f'Не удалось загрузить данные для "{self.action.name}" из за проблем с датой')
            return
        if self.utils.DATE_UTIL.promotion_is_outdated(self.action.end):
            self.queue.put('progress')
            return
        if not self.ignore:
            with self.lock:
                if actions_exists_in_db_new(self.action):
                    self.queue.put('progress')
                    return
        with self.lock:
            self.actions_data.append(self.utils.ACTIONS_UTIL.generate_action_new(self.action))
            self.queue.put('progress')
