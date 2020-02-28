from datetime import datetime
import re
import threading
import requests
from bs4 import BeautifulSoup
from threading import Thread
from multiprocessing import Process
import helpers.helper as helper
from selenium import webdriver


class Kolesadarom_process(Process):

    def __init__(self, queue):
        super().__init__()
        self.queue = queue

    def __str__(self):
        return "Колеса Даром"

    def run(self):
        partner_name = 'Колеса Даром'
        actions_data = []
        lock = threading.Lock()
        main_url = 'https://www.kolesa-darom.ru/actions/'
        driver = webdriver.Chrome()
        driver.get(main_url)
        page = BeautifulSoup(driver.page_source, 'lxml')
        driver.quit()
        divs = page.find_all("div", class_='tiles__item-inner')
        for div in divs:
            begin_url = 'https://www.kolesa-darom.ru'
            name = div.find('a', class_='tiles__link').text.strip()
            url = begin_url + div.find('a', class_='tiles__link').get('href')

            start = helper.DATA_NOW
            try:
                pediod = div.find('div', class_='tiles__period-title').text.strip()
                end = helper.get_one_date(pediod)
            except Exception:
                end = helper.get_date_half_year_ahead(start)
            print(name)
            print(url)
            print(end)
        # threads = [Kolesadarom_thread(actions_data, div, lock, self.queue) for div in divs]
        # for thread in threads:
        #     thread.start()
        # for thread in threads:
        #     thread.join()
        # self.queue.put((partner_name,))
        # self.queue.put(helper.write_csv(actions_data))
        # self.queue.put(actions_data)
        # self.queue.put('progress')


class Kolesadarom_thread(Thread):

    def __init__(self, actions_data, div, lock, print_queue):
        super().__init__()
        self.actions_data = actions_data
        self.div = div
        self.lock = lock
        self.queue = print_queue

    def run(self):
        persent = self.div.find("span", class_='banner-sale-list-item-discount-percent').text.strip()
        end = self.div.find("strong", class_='date').text.strip()
        incoming_date = re.search(r'до\s(.*)\s?', end.lower()).group(1)
        end = helper.get_one_date(incoming_date)
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
        action_type = 'скидка'
        code = 'Не требуется'
        short_desc = ''
        name = f'Скидки {persent} на {name}'
        try:
            desc = descs.find_all('p')[0].text.strip()
            desc = re.sub(r'\n', '', desc)
            desc = re.sub(r'\r', '', desc)
        except Exception:
            pass
        action = helper.generate_action(partner, name, start, end, desc, code, url, action_type, short_desc)
        with self.lock:
            self.actions_data.append(action)
