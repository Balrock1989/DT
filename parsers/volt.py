import re
from multiprocessing import Process
import helpers.helper as helper


class Volt_process(Process):
    def __init__(self, queue):
        super().__init__()
        self.queue = queue

    def __str__(self):
        return "220Volt"

    def run(self):
        partner_name = '220Volt'
        actions_data = []
        main_url = 'https://ulyanovsk.220-volt.ru/share/0/'
        page = helper.prepare_parser_data_use_webdriver(main_url)
        divs = page.find_all('div', class_='actionContainer rel')
        for div in divs:
            date = div.find('div', class_='actionPeriod').text.strip()
            start, end = helper.convert_text_date(date)
            name = div.find('div', class_='actionText').h4.text.strip()
            desc = div.find('div', class_='text').text.strip()
            desc = re.sub(r'\s{2,}', ' ', desc).strip()
            url = 'https://220-volt.ru' + div.find('a', class_='activeButton').get('href')
            code = 'Не требуется'
            if helper.promotion_is_outdated(end):
                continue
            short_desc = ''
            action_type = helper.check_action_type(code, name, desc)
            action = helper.generate_action(partner_name, name, start, end, desc, code, url, action_type, short_desc)
            actions_data.append(action)
        helper.filling_queue(self.queue, actions_data, partner_name)
