import re
import threading
import requests
from bs4 import BeautifulSoup
from threading import Thread
from multiprocessing import Process
import helpers.helper as helper
from database.data_base import actions_exists_in_db


class Sephora_process(Process):

    def __init__(self, queue, ignore):
        super().__init__()
        self.queue = queue.queue
        self.ignore = ignore

    def __str__(self):
        return "Сефора"

    def run(self):
        partner_name = 'Sephora'
        actions_data = []
        lock = threading.Lock()
        main_url = 'https://sephora.ru/news/'
        page = helper.get_page_use_request(main_url)
        links = page.find_all("a", class_='b-news-thumb__title')
        threads = [Sephora_thread(actions_data, main_url, link, lock, self.queue, self.ignore) for link in links]
        self.queue.put(f'set {len(threads)}')
        helper.start_join_threads(threads)
        helper.filling_queue(self.queue, actions_data, partner_name)


class Sephora_thread(Thread):

    def __init__(self, actions_data, main_url, link, lock, print_queue, ignore):
        super().__init__()
        self.actions_data = actions_data
        self.main_url = main_url
        self.link = link
        self.lock = lock
        self.queue = print_queue
        self.ignore = ignore

    def run(self):
        link = self.main_url[:-5] + self.link['href'][1:]
        request = requests.get(link)
        page = BeautifulSoup(request.text, 'lxml')
        div = page.find('div', class_='b-news-detailed')
        if div:
            all_p = page.find_all('p')
            desc = ''
            for p in all_p:
                desc += p.text
            desc = re.sub(r'\s{2,}', '\n', desc).strip()
            desc = re.sub(r'\xa0', '\n', desc).strip()
            if len(desc) < 2500:
                try:
                    range = helper.get_range_date(desc)
                    start, end = helper.convert_list_to_date(range)
                except Exception:
                    try:
                        start, end = helper.get_start_date_in_date(desc)
                    except Exception:
                        self.queue.put('progress')
                        return
                url = link
                name = page.h1.text
                desc = desc.replace("На этот номер телефона будет отправлено sms с кодом восстановления:Войди или"
                                    " зарегистрируйся, чтобы получить все преимущества постоянного покупателя!", '').strip()
                partner_name = 'Sephora'
                code = "Не требуется"
                if helper.promotion_is_outdated(end):
                    self.queue.put('progress')
                    return
                short_desc = ''
                action_type = helper.check_action_type(code, name, desc)
                if not self.ignore:
                    with self.lock:
                        if actions_exists_in_db(partner_name, name, start, end):
                            self.queue.put('progress')
                            return
                action = helper.generate_action(partner_name, name, start, end, desc, code, url, action_type, short_desc)
                with self.lock:
                    self.actions_data.append(action)
                    self.queue.put('progress')
            else:
                self.queue.put('progress')
        else:
            self.queue.put('progress')