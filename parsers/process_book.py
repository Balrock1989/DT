import re
import threading
import requests
from bs4 import BeautifulSoup
from threading import Thread
from multiprocessing import Process
import helpers.helper as helper


class Book_process(Process):

    def __init__(self, queue):
        super().__init__()
        self.queue = queue

    def __str__(self):
        return "Book24"

    def run(self):
        partner_name = 'Book24'
        actions_data = []
        lock = threading.Lock()
        page = helper.get_page_use_webdriver('https://book24.ru/sales/', scroll=True)
        begin_url = 'https://book24.ru'
        divs = page.find_all('div', class_='stock-list-item__actions')
        links = []
        for div in divs:
            if div.find('div', class_='stock-list-item__countdown'):
                links.append(begin_url + div.find("div", class_='stock-list-item__more').a.get('href'))
            else:
                pass
        threads = [Book_thread(actions_data, link, lock, self.queue) for link in links]
        helper.start_join_threads(threads)
        helper.filling_queue(self.queue, actions_data, partner_name)


class Book_thread(Thread):

    def __init__(self, actions_data, link, lock, print_queue):
        super().__init__()
        self.actions_data = actions_data
        self.link = link
        self.lock = lock
        self.queue = print_queue

    def run(self):
        request = requests.get(self.link)
        page = BeautifulSoup(request.text, 'lxml')
        name = page.h1.text
        start = helper.DATA_NOW
        try:
            code = page.find('input', class_='copy-promocode__code').get('value').strip()
        except AttributeError:
            code = 'Не требуется'
        info_divs = page.find_all('div', class_='info-list__item')
        full_date = ''
        short_desc = ''
        if len(info_divs) == 3:
            short_desc = info_divs[0].find('span', class_='info-list__text').text.strip()
            full_date = info_divs[2].find('span', class_='info-list__text').text.strip()
        if len(info_divs) == 2:
            short_desc = info_divs[0].find('span', class_='info-list__text').text.strip()
            full_date = info_divs[1].find('span', class_='info-list__text').text.strip()
        if len(info_divs) == 1:
            full_date = info_divs[0].find('span', class_='info-list__text').text.strip()
        try:
            end = re.search(r'(\d.*\d{4})', full_date).group(1).strip()
            end = helper.get_one_date(end)
        except Exception:
            end = helper.get_date_end_month()
        try:
            desc = page.find_all('div', class_='text-block-d')[1].text.strip()
            desc = re.sub(r'\s{2,}', '', desc).strip()
        except Exception:
            try:
                desc = page.find_all('div', class_='text-block-d')[0].text.strip()
                desc = re.sub(r'\s{2,}', '', desc).strip()
            except Exception:
                return
        partner = 'Book24'
        if helper.promotion_is_outdated(end):
            return
        action_type = helper.check_action_type(code, name, desc)
        action = helper.generate_action(partner, name, start, end, desc, code, self.link, action_type, short_desc)
        with self.lock:
            self.actions_data.append(action)
