from datetime import datetime
import re
import threading
import requests
from bs4 import BeautifulSoup
from threading import Thread
from multiprocessing import Process
import helpers.helper as helper
from database.data_base import actions_exists_in_db


class Akusherstvo_process(Process):

    def __init__(self, queue, ignore):
        super().__init__()
        self.queue = queue.queue
        self.ignore = ignore

    def __str__(self):
        return "Акушерство"

    def run(self):
        partner_name = 'Акушерство'
        actions_data = []
        lock = threading.Lock()
        page = helper.get_page_use_webdriver('https://www.akusherstvo.ru/sale.php', hidden=True)
        divs = page.find_all("li", class_='banner-sale-list-item js-banner-sale-list-item')
        divs_2 = page.find_all('li', class_='banner-sale-list-item js-banner-sale-list-item middle')
        divs_3 = page.find_all("li", class_='banner-sale-list-item fire js-banner-sale-list-item')
        divs_4 = page.find_all("li", class_='banner-sale-list-item fire js-banner-sale-list-item middle')
        divs = divs + divs_2 + divs_3 + divs_4

        threads = [Akusherstvo_thread(actions_data, div, lock, self.queue, self.ignore) for div in divs]
        helper.start_join_threads(threads)
        self.queue.put(f'set {len(threads)}')
        helper.filling_queue(self.queue, actions_data, partner_name)
        self.queue.put('clear')

class Akusherstvo_thread(Thread):

    def __init__(self, actions_data, div, lock, print_queue, ignore):
        super().__init__()
        self.actions_data = actions_data
        self.div = div
        self.lock = lock
        self.queue = print_queue
        self.ignore = ignore

    def run(self):
        persent = self.div.find("span", class_='banner-sale-list-item-discount-percent').text.strip()
        end = self.div.find("strong", class_='date').text.strip()
        end = helper.get_one_date(end)
        start = datetime.now().strftime('%d.%m.%Y')
        link = self.div.find('a').get('href')
        request = requests.get(link)
        partner_name = 'Акушерство'
        url = 'https://www.akusherstvo.ru/sale.php'
        action_page = BeautifulSoup(request.text, 'lxml')
        name = action_page.h1.text.strip()
        descs = action_page.find('table', class_='centre_header')
        desc = ''
        code = 'Не требуется'
        name = f'Скидки {persent} на {name}'
        try:
            desc = descs.find_all('p')[0].text.strip()
            desc = re.sub(r'\n', '', desc)
            desc = re.sub(r'\r', '', desc)
        except Exception:
            pass
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
            self.queue.put('progress')
            self.actions_data.append(action)
