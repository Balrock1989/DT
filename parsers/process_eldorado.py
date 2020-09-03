from datetime import datetime
from multiprocessing import Process
import helpers.helper as helper
from database.data_base import actions_exists_in_db


class Eldorado_process(Process):

    def __init__(self, queue, ignore):
        super().__init__()
        self.queue = queue.queue
        self.ignore = ignore

    def __str__(self):
        return "Эльдорадо"

    def run(self):
        partner_name = 'Эльдорадо'
        actions_data = []
        base_url = 'https://www.eldorado.ru'
        main_url = 'https://www.eldorado.ru/actions.php?type=online'
        page = helper.get_page_use_request(main_url)
        divs = page.find_all('a', class_='promotion__promotion')
        for div in divs:
            try:
                url = str(div.get('href'))
                url = div.get('href') if 'www' in url else base_url + div.get('href')
            except TypeError:
                print("Отсутствуют данные по акции")
                continue
            name = div.find('div', class_='promotion__promotion-title').text.strip()
            start = helper.DATA_NOW
            try:
                end = div.find('div', class_='promotion__promotion-date').get('data-date')
                end = datetime.strptime(end, '%Y-%m-%d').strftime('%d.%m.%Y')
            except ValueError:
                print("Отсутствует дата окончания акции")
                continue
            code = "Не требуется"
            desc = name
            short_desc = ''
            action_type = helper.check_action_type(code, name, desc)
            if helper.promotion_is_outdated(end):
                continue
            if not self.ignore:
                if actions_exists_in_db(partner_name, name, start, end):
                    continue
            action = helper.generate_action(partner_name, name, start, end, desc, code, url, action_type,short_desc)
            actions_data.append(action)
        helper.filling_queue(self.queue, actions_data, partner_name)
