import re
from multiprocessing import Process

import requests
from bs4 import BeautifulSoup
import helpers.helper as helper


class Utkonos_process(Process):
    def __init__(self, queue):
        super().__init__()
        self.queue = queue

    def __str__(self):
        return "Утконос"

    def run(self):
        partner = 'Утконос'
        actions_data = []
        s = requests.Session()
        s.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'})
        main_url = 'https://www.utkonos.ru/action'
        request = s.get(main_url)
        page = BeautifulSoup(request.text, 'lxml')
        divs = page.find_all("div", class_='action_wrapper')
        for div in divs:
            name = div.a.text.strip()
            code = 'Не требуется'
            action_type = 'скидка'
            short_desc = ''
            desc = ''
            url = 'https://www.utkonos.ru' + div.a.get('href')
            incoming_date = div.find('div', class_='text').text.strip()
            incoming_date = re.search(r'с\s(\d+\s[а-яА-Я]+).*по\s(\d+\s[а-яА-Я]+)', incoming_date.lower())
            start, end = helper.get_double_date(incoming_date.group(1), incoming_date.group(2))
            if helper.promotion_is_outdated(end):
                continue
            action = helper.generate_action(partner, name, start, end, desc, code, url, action_type, short_desc)
            actions_data.append(action)
        self.queue.put(actions_data)
        self.queue.put(helper.write_csv(actions_data))
        self.queue.put((partner,))
        self.queue.put('progress')
