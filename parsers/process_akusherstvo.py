from datetime import datetime
import re
import threading
import requests
from bs4 import BeautifulSoup
from threading import Thread
from multiprocessing import Process
import helpers.helper as helper
from selenium import webdriver


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
        main_url = 'https://www.akusherstvo.ru/sale.php'
        driver = webdriver.Chrome()
        driver.get(main_url)
        page = BeautifulSoup(driver.page_source, 'lxml')
        driver.quit()
        divs = page.find_all("li", class_='banner-sale-list-item js-banner-sale-list-item')
        divs_2 = page.find_all('li', class_='banner-sale-list-item js-banner-sale-list-item middle')
        divs_3 = page.find_all("li", class_='banner-sale-list-item fire js-banner-sale-list-item')
        divs_4 = page.find_all("li", class_='banner-sale-list-item fire js-banner-sale-list-item middle')
        divs = divs + divs_2 + divs_3 + divs_4
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
        end = self.div.find("strong", class_='date').text.strip()
        end = helper.get_one_date(end)
        if helper.promotion_is_outdated(end):
            return
        start = datetime.now().strftime('%d.%m.%Y')
        link = self.div.find('a').get('href')
        request = requests.get(link)
        partner = 'Акушерство'
        url = 'https://www.akusherstvo.ru/sale.php'
        action_page = BeautifulSoup(request.text, 'lxml')
        name = action_page.h1.text.strip()
        descs = action_page.find('table', class_='centre_header')
        desc = ''
        code = 'Не требуется'
        short_desc = ''
        name = f'Скидки {persent} на {name}'
        try:
            desc = descs.find_all('p')[0].text.strip()
            desc = re.sub(r'\n', '', desc)
            desc = re.sub(r'\r', '', desc)
        except Exception:
            pass
        if 'подарок' in self.name.lower() or 'подарок' in desc.lower():
            action_type = 'подарок'
        elif 'доставка' in self.name.lower() or 'доставка' in desc.lower():
            action_type = 'доставка'
        else:
            action_type = 'скидка'
        action = helper.generate_action(partner, name, start, end, desc, code, url, action_type, short_desc)
        with self.lock:
            self.actions_data.append(action)
