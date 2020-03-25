import re
from datetime import datetime
from multiprocessing import Process
import helpers.helper as helper
# TODO Добавить акции с главной станицы.

class Kupivip_process(Process):
    def __init__(self, queue):
        super().__init__()
        self.queue = queue

    def __str__(self):
        return "КупиВип"

    def run(self):
        actions_data = []
        partner_name = 'КупиВип'
        page = helper.get_page_use_request('https://www.kupivip.ru/campaigns?showIn=FEMALE&filter=ALL')
        divs = page.find_all("div", attrs={'data-banner': 'campaign'})
        for div in divs:
            persent = ''
            desc = ''
            try:
                name = div.find("div", class_='brands').text.strip()
            except:
                self.queue.put("Пропущена одна акция без названия")
                continue
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
            action = helper.generate_action(partner_name, name, start, end, desc, code, url, action_type, short_desc)
            actions_data.append(action)
        helper.filling_queue(self.queue, actions_data, partner_name)
