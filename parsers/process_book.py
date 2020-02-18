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
        s = requests.Session()
        s.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'})
        main_url = 'https://book24.ru/sales/'
        request = s.get(main_url)
        page = BeautifulSoup(request.text, 'lxml')
        begin_url = 'https://book24.ru'
        # TODO Загрузить через вебдрайвер, проскролить сраницу в самый низ, и спарсить
        divs = page.find_all('div', class_='stock-list-item__actions')
        links = []
        for div in divs:
            if div.find('div', class_='stock-list-item__countdown'):
                links.append(begin_url + div.find("div", class_='stock-list-item__more').a.get('href'))
            else:
                print('НЕТ')
        print(links)


        # divs = page.find_all("div", class_='stock-list-item__more')
        # links = [begin_url + div.a.get('href') for div in divs]
        # threads = [Book_thread(actions_data, link, lock, self.queue) for link in links]
        # for thread in threads:
        #     thread.start()
        # for thread in threads:
        #     thread.join()
        # self.queue.put(actions_data)
        # self.queue.put((partner_name,))
        # self.queue.put(helper.write_csv(actions_data))
        # self.queue.put('progress')


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
        desc = page.find_all('div', class_='text-block-d')[1].text.strip()
        desc = re.sub(r'\s{2,}', '', desc).strip()
        desc = re.sub(r'\r', '', desc).strip()
        partner = 'Book24'
        action = helper.generate_action(partner, name, start, end, desc, code, self.link, action_type, short_desc)
        with self.lock:
            self.actions_data.append(action)
