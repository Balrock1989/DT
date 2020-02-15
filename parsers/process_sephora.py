import re
import threading
import requests
from bs4 import BeautifulSoup
from threading import Thread
from multiprocessing import Process
import helpers.helper as helper


class Sephora_process(Process):

    def __init__(self, queue):
        super().__init__()
        self.queue = queue

    def __str__(self):
        return "Сефора"

    def run(self):
        partner_name = 'Sephora'
        actions_data = []
        lock = threading.Lock()
        s = requests.Session()
        s.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'})
        main_url = 'https://sephora.ru/news/'
        request = s.get(main_url)
        page = BeautifulSoup(request.text, 'lxml')
        links = page.find_all("a", class_='b-news-thumb__title')
        threads = [Sephora_thread(actions_data, main_url, link, lock, self.queue) for link in links]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.queue.put(actions_data)
        self.queue.put((partner_name,))
        self.queue.put(helper.write_csv(actions_data))
        self.queue.put('progress')


class Sephora_thread(Thread):

    def __init__(self, actions_data, main_url, link, lock, print_queue):
        super().__init__()
        self.actions_data = actions_data
        self.main_url = main_url
        self.link = link
        self.lock = lock
        self.queue = print_queue

    def run(self):
        link = self.main_url[:-5] + self.link['href'][1:]
        request = requests.get(link)
        page = BeautifulSoup(request.text, 'lxml')
        div = page.find('div', class_='b-news-detailed')
        if div:
            try:
                incoming_date = re.search(r'Срок проведения Акции: с (\d.*\d+)', div.text)[1]
                date_start, date_end = helper.one_date_return_two(incoming_date)
            except TypeError:
                return
            code = "Не требуется"
            action_name = div.h1.text
            partner_name = 'Sephora'
            action_type = 'подарок' if 'подар' in action_name.lower() else 'скидка'
            paragraphs = div.findAll('p')
            url = 'https://sephora.ru/news/'
            descriptions = []
            for p in paragraphs:
                text = p.text.strip()
                if 'При' in text:
                    descriptions.append(text)
            for desc in descriptions:
                action = {'Имя партнера': partner_name, 'Название акции': action_name, 'Дата начала': date_start,
                          'Дата окончания': date_end, 'Условия акции': desc,
                          'Купон': code, 'URL': url, 'Тип купона': action_type}
                with self.lock:
                    self.actions_data.append(action)
