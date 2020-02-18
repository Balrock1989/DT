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
        partner = 'ИльДэБотэ'
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
            name = div.h2.text
            start = datetime.now().strftime('%d.%m.%Y')
            end = (datetime.now() + timedelta(days=3)).strftime('%d.%m.%Y')
            desc = div.find("p", class_='desc').text.strip()
            action_type = 'подарок' if 'подарок' in name.lower() else 'скидка'
            code = 'Не требуется'
            short_desc = ''
            action = helper.generate_action(partner, name, start, end, desc, code, url, action_type, short_desc)
            actions_data.append(action)
        self.queue.put(actions_data)
        self.queue.put((partner,))
        self.queue.put(helper.write_csv(actions_data))
        self.queue.put('progress')
