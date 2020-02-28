import re
import threading
from pprint import pprint

import requests
from bs4 import BeautifulSoup
from threading import Thread
from multiprocessing import Process
import helpers.helper as helper


class Holodilnik_process(Process):

    def __init__(self, queue):
        super().__init__()
        self.queue = queue

    def __str__(self):
        return "Холодильник"

    def run(self):
        partner_name = 'Холодильник'
        actions_data = []
        lock = threading.Lock()
        s = requests.Session()
        s.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Host': 'ulyanovsk.holodilnik.ru',
            'Upgrade-Insecure-Requests': '1',
        })
        main_url = 'https://ulyanovsk.holodilnik.ru/action/'
        request = s.get(main_url)
        page = BeautifulSoup(request.text, 'lxml')
        divs = page.find_all("div", class_='col-4')
        begin_url = 'holodilnik.ru'
        threads = []
        for div in divs:
            url = begin_url + div.a.get('href').strip()
            name = div.find('span', class_='link').text.strip()
            date = div.find('span', class_='text-data').text.strip()
            date = date.split(' - ')
            threads.append(Holodilnik_thread(actions_data, lock, self.queue, name, url, date))
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        if len(actions_data) == 0:
            self.queue.put(f'Акции по {partner_name} не найдены ')
            return
        self.queue.put(actions_data)
        self.queue.put((partner_name,))
        self.queue.put(helper.write_csv(actions_data))
        self.queue.put('progress')


class Holodilnik_thread(Thread):

    def __init__(self, actions_data, lock, queue, name, url, date):
        super().__init__()
        self.actions_data = actions_data
        self.lock = lock
        self.queue = queue
        self.name = name
        self.url = url
        self.date = date

    def run(self):
        if len(self.date[0]) > 1:
            start = re.search(r'(\d+\.\d+\.\d+)', self.date[0]).group(1)
        else:
            return
        if len(self.date) == 2:
            end = re.search(r'(\d+\.\d+\.\d+)', self.date[1]).group(1)
        else:
            end = helper.get_date_month_ahead(start)
        if helper.promotion_is_outdated(end):
            return
        id = 'tblact_' + self.url[21:-1]
        link = 'http://www.' + self.url
        s = requests.Session()
        s.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0'}
        request = s.get(link)
        page = BeautifulSoup(request.text, 'lxml')
        main_div = page.find('div', id=id)
        try:
            div = main_div.find_all('div')
        except Exception:
            return
        partner = 'Холодильник'
        desc = re.sub(r'\s{2,}', ' ', div[1].text.strip()).strip()
        desc = re.sub(r'\xa0', '\n', desc).strip()
        if len(desc) > 1500:
            desc = desc[:1499]
        code = helper.find_promo_code(desc)
        action_type = 'купон' if 'требуется' not in code else 'скидка'
        short_desc = ''
        action = helper.generate_action(partner, self.name, start, end, desc, code, self.url, action_type, short_desc)
        with self.lock:
            self.actions_data.append(action)
