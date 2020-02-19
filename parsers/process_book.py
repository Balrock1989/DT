import re
import threading
import time

import requests
from bs4 import BeautifulSoup
from threading import Thread
from multiprocessing import Process
import helpers.helper as helper
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


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
        main_url = 'https://book24.ru/sales/'
        driver = webdriver.PhantomJS()
        driver.get(main_url)
        scroll_script = \
            "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;"
        lenOfPage = driver.execute_script(scroll_script)
        while True:
            lastCount = lenOfPage
            time.sleep(1)
            lenOfPage = driver.execute_script(scroll_script)
            if lastCount == lenOfPage:
                break
        page = BeautifulSoup(driver.page_source, 'lxml')
        driver.quit()
        begin_url = 'https://book24.ru'
        divs = page.find_all('div', class_='stock-list-item__actions')
        links = []
        for div in divs:
            if div.find('div', class_='stock-list-item__countdown'):
                links.append(begin_url + div.find("div", class_='stock-list-item__more').a.get('href'))
            else:
                pass
        threads = [Book_thread(actions_data, link, lock, self.queue) for link in links]
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
            action_type = 'купон'
        except AttributeError:
            code = 'Не требуется'
            action_type = 'скидка'
        info_divs = page.find_all('div', class_='info-list__item')
        short_desc = ''
        full_date = ''
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
        action = helper.generate_action(partner, name, start, end, desc, code, self.link, action_type, short_desc)
        with self.lock:
            self.actions_data.append(action)
