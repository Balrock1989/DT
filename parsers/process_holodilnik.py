import re
import threading
import requests
from bs4 import BeautifulSoup
from threading import Thread
from multiprocessing import Process
import helpers.helper as helper
from database.data_base import actions_exists_in_db


class Holodilnik_process(Process):

    def __init__(self, queue, ignore):
        super().__init__()
        self.queue = queue.queue
        self.ignore = ignore

    def __str__(self):
        return "Холодильник"

    def run(self):
        partner_name = 'Холодильник'
        actions_data = []
        lock = threading.Lock()
        page = helper.get_page_use_request('https://ulyanovsk.holodilnik.ru/action/')
        divs = page.find_all("div", class_='col-4')
        begin_url = 'holodilnik.ru'
        threads = []
        for div in divs:
            url = begin_url + div.a.get('href').strip()
            name = div.find('span', class_='link').text.strip()
            date = div.find('span', class_='text-data').text.strip()
            date = date.split(' - ')
            threads.append(Holodilnik_thread(actions_data, lock, self.queue, name, url, date, self.ignore))
        helper.start_join_threads(threads)
        helper.filling_queue(self.queue, actions_data, partner_name)


class Holodilnik_thread(Thread):

    def __init__(self, actions_data, lock, queue, name, url, date, ignore):
        super().__init__()
        self.actions_data = actions_data
        self.lock = lock
        self.queue = queue
        self.name = name
        self.url = url
        self.date = date
        self.ignore = ignore

    def run(self):
        if len(self.date[0]) > 1:
            start = re.search(r'(\d+\.\d+\.\d+)', self.date[0]).group(1)
        else:
            return
        if len(self.date) == 2:
            end = re.search(r'(\d+\.\d+\.\d+)', self.date[1]).group(1)
        else:
            end = helper.get_date_month_ahead(start)
        id = 'tblact_' + self.url[21:-1]
        self.url = 'http://www.' + self.url
        s = requests.Session()
        s.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0'}
        request = s.get(self.url)
        page = BeautifulSoup(request.text, 'lxml')
        try:
            main_div = page.find('div', id=id).find('span', class_='item-txt')
            divs = main_div.find_all('div')
        except Exception:
            return
        partner_name = 'Холодильник'
        try:
            desc = re.sub(r'\s{2,}', ' ', main_div.text.strip()).strip()
        except:
            desc = re.sub(r'\s{2,}', ' ', divs[1].text.strip()).strip()
        desc = re.sub(r'\xa0', '\n', desc).strip()
        if len(desc) > 1500:
            desc = desc[:1499]
        code = helper.find_promo_code(desc)
        if helper.promotion_is_outdated(end):
            return
        short_desc = ''
        action_type = helper.check_action_type(code, self.name, desc)
        if not self.ignore:
            with self.lock:
                if actions_exists_in_db(partner_name, self.name, start, end):
                    return
        action = helper.generate_action(partner_name, self.name, start, end, desc, code, self.url, action_type, short_desc)
        with self.lock:
            self.actions_data.append(action)
