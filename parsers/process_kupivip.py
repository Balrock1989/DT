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
        partner = 'КупиВип'
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
            name = div.find("div", class_='brands').text.strip()
            try:
                persent = div.find("div", class_='percent').text.strip()
            except Exception:
                pass
            try:
                desc = div.find("div", class_='name').text.strip()
            except Exception:
                pass
            if persent:
                name += f'. Скидки до {persent}%'
            start = datetime.now().strftime('%d.%m.%Y')
            end = datetime.now().strftime('%d.%m.%Y')
            code = 'Не требуется'
            if 'промокод' in name.lower():
                code = re.search(r'код\s(.*)\s?', name).group(1)
            url = 'https://www.kupivip.ru/'
            if helper.promotion_is_outdated(end):
                continue
            short_desc = ''
            action_type = helper.check_action_type(code, name, desc)
            action = helper.generate_action(partner, name, start, end, desc, code, url, action_type, short_desc)
            actions_data.append(action)
        if len(actions_data) == 0:
            self.queue.put(f'Акции по {partner} не найдены ')
            return
        self.queue.put(actions_data)
        self.queue.put(helper.write_csv(actions_data))
        self.queue.put((partner,))
        self.queue.put('progress')
