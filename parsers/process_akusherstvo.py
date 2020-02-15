import multiprocessing
import os
import signal
from datetime import datetime
import re
import threading
from pprint import pprint

import requests
from bs4 import BeautifulSoup
from threading import Thread
from multiprocessing import Process
import helpers.helper as helper
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class Akusherstvo_process(Process):

    def __init__(self, queue):
        super().__init__()
        self.queue = queue

    def __str__(self):
        return "Акушерство"

    def run(self):
        partner_name = 'Акушерство'
        actions_data = []
        lock = threading.Lock()
        s = requests.Session()
        s.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'})
        main_url = 'https://www.akusherstvo.ru/sale.php'
        options = Options()
        options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(options=options)
        driver.get(main_url)
        page = BeautifulSoup(driver.page_source, 'lxml')
        driver.quit()
        divs = page.find_all("li", class_='banner-sale-list-item js-banner-sale-list-item')
        divs_2 = page.find_all('li', class_='banner-sale-list-item js-banner-sale-list-item middle')
        divs = divs + divs_2
        threads = [Akusherstvo_thread(actions_data, div, lock, self.queue) for div in divs]

        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.queue.put((partner_name,))
        self.queue.put(helper.write_csv(actions_data))
        self.queue.put(actions_data)
        self.queue.put('progress')


class Akusherstvo_thread(Thread):

    def __init__(self, actions_data, div, lock, print_queue):
        super().__init__()
        self.actions_data = actions_data
        self.div = div
        self.lock = lock
        self.queue = print_queue

    def run(self):
        persent = self.div.find("span", class_='banner-sale-list-item-discount-percent').text.strip()
        date_end = self.div.find("strong", class_='date').text.strip()
        incoming_date = re.search(r'до\s(.*)\s?', date_end.lower()).group(1)
        date_end = helper.get_one_date(incoming_date)
        date_start = datetime.now().strftime('%d.%m.%Y')
        link = self.div.find('a').get('href')
        request = requests.get(link)
        partner_name = 'Акушерство'
        main_url = 'https://www.akusherstvo.ru/sale.php'
        action_page = BeautifulSoup(request.text, 'lxml')
        action_name = action_page.h1.text.strip()
        descs = action_page.find('table', class_='centre_header')
        desc = ''
        action_type = 'скидка'
        code = 'Не требуется'
        action_name = f'Скидки {persent} на {action_name}'
        try:
            desc = descs.find_all('p')[0].text.strip()
            desc = re.sub(r'\n', '', desc)
            desc = re.sub(r'\r', '', desc)
        except Exception:
            pass
        action = {'Имя партнера': partner_name, 'Название акции': action_name, 'Дата начала': date_start,
                  'Дата окончания': date_end, 'Условия акции': desc,
                  'Купон': code, 'URL': main_url, 'Тип купона': action_type}
        with self.lock:
            self.actions_data.append(action)
