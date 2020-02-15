import re
from datetime import datetime
from multiprocessing import Process

import requests
from bs4 import BeautifulSoup
import helpers.helper as helper


class Kupivip_process(Process):
    def __init__(self, queue):
        super().__init__()
        self.queue = queue

    def __str__(self):
        return "КупиВип"

    def run(self):
        actions_data = []
        partner_name = 'КупиВип'
        s = requests.Session()
        s.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'})
        main_url = 'https://www.kupivip.ru/campaigns?showIn=FEMALE&filter=ALL'
        request = s.get(main_url)
        page = BeautifulSoup(request.text, 'lxml')
        divs = page.find_all("div", attrs={'data-banner': 'campaign'})

        for div in divs:
            persent = ''
            desc = ''
            action_name = div.find("div", class_='brands').text.strip()
            try:
                persent = div.find("div", class_='percent').text.strip()
            except Exception:
                pass
            try:
                desc = div.find("div", class_='name').text.strip()
            except Exception:
                pass
            if persent:
                action_name += f'. Скидки до {persent}%'
            date_start = datetime.now().strftime('%d.%m.%Y')
            action_type = 'скидка'
            code = 'Не требуется'
            if 'промокод' in action_name.lower():
                code = re.search(r'код\s(.*)\s?', action_name).group(1)
                action_type = 'купон'
            url = 'https://www.kupivip.ru/'
            action = {'Имя партнера': partner_name, 'Название акции': action_name, 'Дата начала': date_start,
                      'Дата окончания': date_start, 'Условия акции': desc,
                      'Купон': code, 'URL': url, 'Тип купона': action_type}
            actions_data.append(action)

        self.queue.put(actions_data)
        self.queue.put(helper.write_csv(actions_data))
        self.queue.put((partner_name,))
        self.queue.put('progress')
