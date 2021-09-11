import re
import threading
from multiprocessing import Process
from threading import Thread

from database.DataBase import actions_exists_in_db_new
from helpers.Utils import Utils
from models.Action import Action


class SephoraProcess(Process):

    def __init__(self, queue, ignore):
        super().__init__()
        self.queue = queue.queue
        self.ignore = ignore
        self.utils = Utils(self.queue)

    def __str__(self):
        return "Сефора"

    def run(self):
        actions_data = []
        lock = threading.Lock()
        main_url = 'https://sephora.ru/news/'
        page = self.utils.ACTIONS_UTIL.get_page_use_request(main_url)
        links = page.find_all("a", class_='b-news-thumb__title')
        threads = [SephoraThread(actions_data, main_url, link, lock, self.queue, self.ignore, self.utils) for link in
                   links]
        self.queue.put(f'set {len(threads)}')
        self.utils.ACTIONS_UTIL.start_join_threads(threads)
        self.utils.CSV_UTIL.filling_queue(self.queue, actions_data, str(self))


class SephoraThread(Thread):

    def __str__(self):
        return "Сефора"

    def __init__(self, actions_data, main_url, link, lock, print_queue, ignore, utils):
        super().__init__()
        self.actions_data = actions_data
        self.main_url = main_url
        self.link = link
        self.lock = lock
        self.queue = print_queue
        self.ignore = ignore
        self.utils = utils

    def run(self):
        link = self.main_url[:-5] + self.link['href'][1:]
        page = self.utils.ACTIONS_UTIL.get_page_use_request(link)
        div = page.find('div', class_='b-news-detailed')
        if div:
            action = Action(str(self))
            all_p = page.find_all('p')
            action.desc = ''
            for p in all_p:
                action.desc += p.text
            action.desc = re.sub(r'\s{2,}', '\n', action.desc).strip()
            action.desc = re.sub(r'\xa0', '\n', action.desc).strip()
            if len(action.desc) < 2500:
                try:
                    date_range = self.utils.DATE_UTIL.get_range_date(action.desc)
                    action.start, action.end = self.utils.DATE_UTIL.convert_list_to_date(date_range)
                except (AttributeError, ValueError):
                    try:
                        action.start, action.end = self.utils.DATE_UTIL.get_start_date_in_date(action.desc, True)
                    except (AttributeError, ValueError):
                        self.queue.put('progress')
                        return
                action.url = link
                action.name = page.h1.text
                action.desc = action.desc.replace(
                    "На этот номер телефона будет отправлено sms с кодом восстановления:Войди или"
                    " зарегистрируйся, чтобы получить все преимущества постоянного покупателя!",
                    '').strip()
                action.code = "Не требуется"
                if self.utils.DATE_UTIL.promotion_is_outdated(action.end):
                    self.queue.put('progress')
                    return
                action.short_desc = ''
                action.action_type = self.utils.ACTIONS_UTIL.check_action_type(action)
                if not self.ignore:
                    with self.lock:
                        if actions_exists_in_db_new(action):
                            self.queue.put('progress')
                            return
                with self.lock:
                    self.actions_data.append(self.utils.ACTIONS_UTIL.generate_action(action))
                    self.queue.put('progress')
            else:
                self.queue.put('progress')
        else:
            self.queue.put('progress')
