# import re
# import threading
# import requests
# from bs4 import BeautifulSoup
# from threading import Thread
# from multiprocessing import Process
# import helpers.helper as helper
#
#
# class Sephora_process(Process):
#
#     def __init__(self, queue):
#         super().__init__()
#         self.queue = queue
#
#     def __str__(self):
#         return "Сефора"
#
#     def run(self):
#         partner_name = 'Sephora'
#         actions_data = []
#         lock = threading.Lock()
#         s = requests.Session()
#         s.headers.update({
#             'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'})
#         main_url = 'https://sephora.ru/news/'
#         request = s.get(main_url)
#         page = BeautifulSoup(request.text, 'lxml')
#         links = page.find_all("a", class_='b-news-thumb__title')
#         threads = [Sephora_thread(actions_data, main_url, link, lock, self.queue) for link in links]
#         for thread in threads:
#             thread.start()
#         for thread in threads:
#             thread.join()
#         if len(actions_data) == 0:
#             self.queue.put(f'Акции по {partner_name} не найдены ')
#             return
#         self.queue.put(actions_data)
#         self.queue.put((partner_name,))
#         self.queue.put(helper.write_csv(actions_data))
#         self.queue.put('progress')
#
#
# class Sephora_thread(Thread):
#
#     def __init__(self, actions_data, main_url, link, lock, print_queue):
#         super().__init__()
#         self.actions_data = actions_data
#         self.main_url = main_url
#         self.link = link
#         self.lock = lock
#         self.queue = print_queue
#
#     def run(self):
#         link = self.main_url[:-5] + self.link['href'][1:]
#         request = requests.get(link)
#         page = BeautifulSoup(request.text, 'lxml')
#         div = page.find('div', class_='b-news-detailed')
#         if div:
#             try:
#                 incoming_date = re.search(r'Срок проведения Акции: с (\d.*\d+)', div.text)[1]
#                 start, end = helper.one_date_return_two(incoming_date)
#             except TypeError:
#                 return
#             code = "Не требуется"
#             name = div.h1.text
#             partner = 'Sephora'
#             short_desc = ''
#             action_type = 'подарок' if 'подар' in name.lower() else 'скидка'
#             paragraphs = div.findAll('p')
#             url = 'https://sephora.ru/news/'
#             descriptions = []
#             for p in paragraphs:
#                 text = p.text.strip()
#                 if 'При' in text:
#                     descriptions.append(text)
#             for desc in descriptions:
#                 action = helper.generate_action(partner, name, start, end, desc, code, url, action_type, short_desc)
#                 with self.lock:
#                     self.actions_data.append(action)





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
        if len(actions_data) == 0:
            self.queue.put(f'Акции по {partner_name} не найдены ')
            return
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
            all_p = page.find_all('p')
            desc = ''
            for p in all_p:
                desc += p.text
            if len(desc) < 1500:
                try:
                    range = helper.get_range_date(desc)
                    start, end = helper.convern_list_to_date(range)
                except Exception:
                    try:
                        start, end = helper.get_start_date_in_date(desc)
                    except Exception:
                        return
                url = link
                name = page.h1.text
                desc = re.sub(r'\s{2,}', '', desc).strip()
                desc = re.sub(r'\xa0', ' ', desc).strip()
                desc = desc.replace("На этот номер телефона будет отправлено sms с кодом восстановления:Войди или"
                                    " зарегистрируйся, чтобы получить все преимущества постоянного покупателя", '')
                partner = 'Sephora'
                code = "Не требуется"
                short_desc = ''
                action_type = 'скидка'
                action = helper.generate_action(partner, name, start, end, desc, code, url, action_type, short_desc)
                with self.lock:
                    self.actions_data.append(action)
