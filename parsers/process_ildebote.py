from datetime import datetime, timedelta
from multiprocessing import Process

import requests
from bs4 import BeautifulSoup
import helpers.helper as helper


class Ildebote_process(Process):
    def __init__(self, queue):
        super().__init__()
        self.queue = queue

    def __str__(self):
        return "ИльДэБотэ"

    def run(self):
        partner_name = 'ИльДэБотэ'
        actions_data = []
        s = requests.Session()
        s.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'})
        url = 'https://iledebeaute.ru/company/actions/'
        request = s.get(url)
        page = BeautifulSoup(request.text, 'lxml')
        divs = page.find_all("div", class_='news_block')
        for div in divs:
            date = div.find("p", class_='date')
            if 'сегодня' not in date.text.strip().lower() and 'вчера' not in date.text.strip().lower():
                continue
            action_name = div.h2.text
            date_start = datetime.now().strftime('%d.%m.%Y')
            date_end = (datetime.now() + timedelta(days=3)).strftime('%d.%m.%Y')
            desc = div.find("p", class_='desc').text.strip()
            action_type = 'подарок' if 'подарок' in action_name.lower() else 'скидка'
            code = 'Не требуется'
            action = {'Имя партнера': partner_name, 'Название акции': action_name, 'Дата начала': date_start,
                      'Дата окончания': date_end, 'Условия акции': desc,
                      'Купон': code, 'URL': url, 'Тип купона': action_type}
            actions_data.append(action)
            self.queue.put(helper.write_csv(action))
        self.queue.put(actions_data)
        self.queue.put((partner_name,))
        self.queue.put('progress')
