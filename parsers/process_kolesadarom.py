import re
import threading
import requests
from bs4 import BeautifulSoup
from threading import Thread
from multiprocessing import Process
import helpers.helper as helper
from database.data_base import actions_exists_in_db


class Kolesadarom_process(Process):

    def __init__(self, queue, ignore):
        super().__init__()
        self.queue = queue.queue
        self.ignore = ignore

    def __str__(self):
        return "Колеса Даром"

    def run(self):
        partner_name = 'Колеса Даром'
        actions_data = []
        lock = threading.Lock()
        page = helper.get_page_use_webdriver('https://www.kolesa-darom.ru/actions/', hidden=True)
        divs = page.find_all("div", class_='tiles__item-inner')
        threads = []
        for div in divs:
            begin_url = 'https://www.kolesa-darom.ru'
            name = div.find('a', class_='tiles__link').text.strip()
            url = begin_url + div.find('a', class_='tiles__link').get('href')
            try:
                period = div.find('div', class_='tiles__period-date').text.strip()
                end = helper.get_one_date(period)
            except Exception:
                end = helper.get_date_half_year_ahead(helper.DATA_NOW)
            threads.append(Kolesadarom_thread(actions_data, lock, self.queue, name, url, end, self.ignore))
        self.queue.put(f'set {len(threads)}')
        helper.start_join_threads(threads)
        helper.filling_queue(self.queue, actions_data, partner_name)

class Kolesadarom_thread(Thread):

    def __init__(self, actions_data, lock, queue, name, url, date_end, ignore):
        super().__init__()
        self.actions_data = actions_data
        self.lock = lock
        self.queue = queue
        self.name = name
        self.url = url
        self.end = date_end
        self.ignore = ignore

    def run(self):
        s = requests.Session()
        s.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0'}
        request = s.get(self.url)
        page = BeautifulSoup(request.text, 'lxml')
        main_div = page.find('div', class_='article-tiles')
        partner_name = 'Колеса Даром'
        try:
            desc = main_div.find('div', class_=False).find_all('p')
            desc = desc[0].text.strip() + desc[1].text.strip()
        except IndexError:
            desc = main_div.find('div', class_=False).find_all('p')
            if desc:
                desc = desc[0].text.strip()[:300]
            else:
                desc = main_div.find('div', class_=False).text.strip()[:300]
        desc = re.sub(r'\s{2,}', ' ', desc).strip()
        desc = re.sub(r'\xa0', '\n', desc).strip()
        desc = re.sub(r'&nbsp;', ' ', desc).strip()
        start = helper.DATA_NOW
        code = 'Не требуется'
        if helper.promotion_is_outdated(self.end):
            self.queue.put('progress')
            return
        short_desc = ''
        action_type = helper.check_action_type(code, self.name, desc)
        if not self.ignore:
            with self.lock:
                if actions_exists_in_db(partner_name, self.name, start, self.end):
                    self.queue.put('progress')
                    return
        action = helper.generate_action(partner_name, self.name, start, self.end, desc, code, self.url, action_type,
                                        short_desc)
        with self.lock:
            self.actions_data.append(action)
            self.queue.put('progress')
